# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate Annual Daylight Metrics from a result (.ill) files.

-
    Args:
        _results: An list of annual Radiance result files from the "HB Annual Daylight"
            component (containing the .ill files and the sun-up-hours.txt).
            This can also be just the path to the folder containing these
            result files.
        dyn_sch_: Optional dynamic Aperture Group Schedules from the "HB Aperture Group
            Schedule" component, which will be used to customize the behavior
            of any dyanmic aperture geometry in the output metrics. If unsupplied,
            all dynamic aperture groups will be in their default state in for
            the output metrics.
        _occ_sch_: An annual occupancy schedule as a Ladybug Data Collection or a HB-Energy
            schedule object. This can also be the identifier of a schedule in
            your HB-Energy schedule library. Any value in this schedule that is
            0.1 or above will be considered occupied. If None, a schedule from
            8AM to 6PM on all days will be used.
        _threshold_: Threshhold for daylight autonomy (DA) in lux (default: 300).
        _min_max_: A list for min, max illuminacne thresholds for useful daylight illuminance
            in lux. (Default: (100, 3000)).
        grid_filter_: The name of a grid or a pattern to filter the grids. For instance,
            first_floor_* will simulate only the sensor grids that have an
            identifier that starts with first_floor_. By default all the grids
            will be processed.

    Returns:
        report: Reports, errors, warnings, etc.
        DA: Daylight autonomy results in percent. DA is the percentage of occupied hours
            that each sensor recieves equal or more than the illuminance threshold.
            Each value is for a different sensor of the grid. These can be plugged
            into the "LB Spatial Heatmap" component along with meshes of the sensor
            grids to visualize results. These can also be connected to the "HB
            Spatial Daylight Autonomy" component to compute spatial daylight
            autonomy for each grid.
        cDA: Continuous daylight autonomy results in percent. cDA is similar to DA except
            that values below the illuminance threshold can still count partially
            towards the final percentage. Each value is for a different
            sensor of the grid. These can be plugged into the "LB Spatial Heatmap"
            component along with meshes of the sensor grids to visualize results.
        UDI: Useful daylight illuminance results in percent. UDI is the percentage of time
            that illuminace falls between minimum and maximum thresholds. Each value
            is for a different sensor of the grid. These can be plugged into the
            "LB Spatial Heatmap" component along with meshes of the sensor grids
            to visualize results.
        UDI_low: Results for the percent of time that is below the lower threshold
            of useful daylight illuminance in percent. Each value is for a different
            sensor of the grid. These can be plugged into the "LB Spatial Heatmap"
            component along with meshes of the sensor grids to visualize results.
        UDI_up: Results for the percent of time that is above the upper threshold
            of useful daylight illuminance in percent. Each value is for a different
            sensor of the grid. These can be plugged into the "LB Spatial Heatmap"
            component along with meshes of the sensor grids to visualize results.
"""

ghenv.Component.Name = "HB Annual Daylight Metrics"
ghenv.Component.NickName = 'DaylightMetrics'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess

try:
    from ladybug.datacollection import BaseCollection
    from ladybug.futil import write_to_file
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.postprocess.annualdaylight import metrics_from_folder
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from honeybee_radiance_postprocess.dynamic import DynamicSchedule
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:  # honeybee schedule library is not available
    schedule_by_identifier = None

try:
    from pollination_handlers.outputs.daylight import read_da_from_folder, \
        read_cda_from_folder, read_udi_from_folder
except ImportError as e:
    raise ImportError('\nFailed to import pollination_handlers:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree,   \
        give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values for the thresholds and the grid filter
    grid_filter_ = '*' if grid_filter_ is None else grid_filter_
    _threshold_ = _threshold_ if _threshold_ else 300
    if len(_min_max_) != 0:
        assert len(_min_max_), 'Expected two values for _min_max_.'
        min_t = _min_max_[0]
        max_t = _min_max_[1]
    else:
        min_t = 100
        max_t = 3000

    # process the schedule
    if _occ_sch_ is None:
        schedule = None
    elif isinstance(_occ_sch_, BaseCollection):
        schedule = _occ_sch_.values
    elif isinstance(_occ_sch_, str):
        if schedule_by_identifier is not None:
            try:
                schedule = schedule_by_identifier(_occ_sch_).values()
            except TypeError:  # it's probably a ScheduleFixedInterval
                schedule = schedule_by_identifier(_occ_sch_).values
        else:
            raise ValueError('honeybee-energy must be installed to reference '
                             'occupancy schedules by identifier.')
    else:  # assume that it is a honeybee schedule object
        try:
            schedule = _occ_sch_.values()
        except TypeError:  # it's probably a ScheduleFixedInterval
            schedule = _occ_sch_.values
    if schedule is not None:
        bin_schedule = []
        for val in schedule:
            bin_val = 1 if val >= 0.1 else 0
            bin_schedule.append(bin_val)
        schedule = bin_schedule

    # compute the annual metrics
    res_folder = os.path.dirname(_results[0]) if os.path.isfile(_results[0]) \
        else _results[0]
    if os.path.isdir(os.path.join(res_folder, '__static_apertures__')) or \
            os.path.isfile(os.path.join(res_folder, 'grid_states.json')):
        cmds = [
            folders.python_exe_path, '-m', 'honeybee_radiance_postprocess',
            'post-process', 'annual-daylight', res_folder, '-sf', 'metrics',
            '-t', str(_threshold_), '-lt', str(min_t), '-ut', str(max_t)
        ]
        if grid_filter_ != '*':
            cmds.extend(['--grids-filter', grid_filter_])
        if len(dyn_sch_) != 0:
            if os.path.isfile(os.path.join(res_folder, 'grid_states.json')):
                dyn_sch = dyn_sch_[0] if isinstance(dyn_sch_[0], DynamicSchedule) else \
                    DynamicSchedule.from_group_schedules(dyn_sch_)
                dyn_sch_file = dyn_sch.to_json(folder=res_folder)
                cmds.extend(['--states', dyn_sch_file])
            else:
                msg = 'No dynamic aperture groups were found in the Model.\n' \
                    'The input dynamic schedules will be ignored.'
                print(msg)
                give_warning(ghenv.Component, msg)
        if schedule is not None:
            sch_str = '\n'.join(str(h) for h in schedule)
            sch_file = os.path.join(res_folder, 'schedule.txt')
            write_to_file(sch_file, sch_str)
            cmds.extend(['--schedule', sch_file])
        use_shell = True if os.name == 'nt' else False
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        process = subprocess.Popen(
            cmds, cwd=res_folder, shell=use_shell, env=custom_env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = process.communicate()  # wait for the process to finish
        if stdout[-1] != '':
            print(stdout[-1])
            raise ValueError('Failed to compute annual daylight metrics.')
        metric_dir = os.path.join(res_folder, 'metrics')
        DA = list_to_data_tree(read_da_from_folder(os.path.join(metric_dir, 'da')))
        cDA = list_to_data_tree(read_cda_from_folder(os.path.join(metric_dir, 'cda')))
        UDI = list_to_data_tree(read_udi_from_folder(os.path.join(metric_dir, 'udi')))
        UDI_low = list_to_data_tree(read_udi_from_folder(os.path.join(metric_dir, 'udi_lower')))
        UDI_up = list_to_data_tree(read_udi_from_folder(os.path.join(metric_dir, 'udi_upper')))
    else:
        if len(dyn_sch_) != 0:
            msg = 'Dynamic Schedules are currently only supported for Annual Daylight ' \
                'simulations.\nThe input schedules will be ignored.'
            print(msg)
            give_warning(ghenv.Component, msg)
        DA, cDA, UDI_low, UDI, UDI_up = metrics_from_folder(
            res_folder, schedule, _threshold_, min_t, max_t, grid_filter_)
        DA = list_to_data_tree(DA)
        cDA = list_to_data_tree(cDA)
        UDI = list_to_data_tree(UDI)
        UDI_low = list_to_data_tree(UDI_low)
        UDI_up = list_to_data_tree(UDI_up)
