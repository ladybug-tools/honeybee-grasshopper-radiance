# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate Annual Sunlight Exposure from a results folder.
_
Note: This component will only output a LEED compliant ASE if you've run the
simulation with all operable shading devices retracted. If you are using
results with operable shading devices, then this output is NOT LEED compliant.

-
    Args:
        _results: An annual results folder containing direct illuminance results.
            This can be the output of the "HB Annual Daylight" component. This can
            also be just the path to the results folder.
        _occ_sch_: An annual occupancy schedule as a Ladybug Data Collection or a HB-Energy
            schedule object. This can also be the identifier of a schedule in
            your HB-Energy schedule library. Any value in this schedule that is
            0.1 or above will be considered occupied. If None, a schedule from
            9AM to 5PM on weekdays will be used.
        _threshold_: The threshold (lux) that determines if a sensor is
            overlit (default: 1000).
        _target_hrs_: The number of occupied hours that cannot receive higher
            illuminance than the direct threshold (default: 250).
        grid_filter_: The name of a grid or a pattern to filter the grids. For instance,
            first_floor_* will simulate only the sensor grids that have an
            identifier that starts with first_floor_. By default all the grids
            will be processed.

    Returns:
        report: Reports, errors, warnings, etc.
        ASE: Annual sunlight exposure as a percentage for each sensor grid.
        hrs_above_thresh: The number of hours above the threshold for each sensor point.
            These can be plugged into the "LB Spatial Heatmap" component along with
            meshes of the sensor grids to visualize results.
"""

ghenv.Component.Name = "HB Annual Sunlight Exposure"
ghenv.Component.NickName = 'ASE'
ghenv.Component.Message = '1.6.0'
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
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:  # honeybee schedule library is not available
    schedule_by_identifier = None

try:
    from pollination_handlers.outputs.daylight import read_ase_from_folder, \
        read_hours_from_folder
except ImportError as e:
    raise ImportError('\nFailed to import pollination_handlers:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values for the thresholds and the grid filter
    grid_filter_ = '*' if grid_filter_ is None else grid_filter_
    _direct_threshold_ = _threshold_ if _threshold_ else 1000
    _occ_hours_ = _target_hrs_ if _target_hrs_ else 250

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
    if os.path.isfile(os.path.join(res_folder, 'grid_states.json')):
        cmds = [
            folders.python_exe_path, '-m', 'honeybee_radiance_postprocess',
            'post-process', 'annual-sunlight-exposure', res_folder, '-sf', 'metrics',
            '-dt', str(_direct_threshold_), '-oh', str(_occ_hours_)
        ]
        if grid_filter_ != '*':
            cmds.extend(['--grids-filter', grid_filter_])
        if schedule is not None:
            sch_str = '\n'.join(str(h) for h in schedule)
            sch_file = os.path.join(res_folder, 'schedule.txt')
            write_to_file(sch_file, sch_str)
            cmds.extend(['--schedule', sch_file])
        use_shell = True if os.name == 'nt' else False
        process = subprocess.Popen(
            cmds, cwd=res_folder, shell=use_shell,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = process.communicate()  # wait for the process to finish
        if stdout[-1] != '':
            print(stdout[-1])
            raise ValueError('Failed to compute annual sunlight exposure.')
        metric_dir = os.path.join(res_folder, 'metrics')
        ASE = read_ase_from_folder(os.path.join(metric_dir, 'ase'))
        hrs_above_thresh = list_to_data_tree(read_hours_from_folder(os.path.join(metric_dir, 'hours_above')))
    else:
        raise ValueError('Invalid results folder!')
