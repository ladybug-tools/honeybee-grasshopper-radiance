# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate typical statistics (Average, median, minimum, maximum, sum) for an
annual daylight or irradiance simulation.

Statistics can either be computed per sensor or per timestep.

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
        _hoys_: An optional numbers or list of numbers to select the hours of the year (HOYs)
            for which results will be computed. These HOYs can be obtained from the
            "LB Calculate HOY" or the "LB Analysis Period" components. If None, all
            hours of the results will be used.
        grid_filter_: The name of a grid or a pattern to filter the grids. For instance,
            first_floor_* will simulate only the sensor grids that have an
            identifier that starts with first_floor_. By default all the grids
            will be processed.
        per_timestep_: Set to True to calculate statistics per-timestep instead of per-sensor.
            (Default: False)

    Returns:
        report: Reports, errors, warnings, etc.
        average: Average illuminance or irradiance values for each sensor or timestep
            in lux or W/m2. This is either a list of values or a list of data collections
            if per_timestep_ is True.
        median: Median illuminance or irradiance values for each sensor or timestep
            in lux or W/m2. This is either a list of values or a list of data collections
            if per_timestep_ is True.
        minimum: Minimum illuminance or irradiance values for each sensor or timestep
            in lux or W/m2. This is either a list of values or a list of data collections
            if per_timestep_ is True.
        maximum: Maximum illuminance or irradiance values for each sensor or timestep
            in lux or W/m2. This is either a list of values or a list of data collections
            if per_timestep_ is True.
        cumulative: Cumulative illuminance or irradiance values for each sensor or timestep
            in lux or W/m2. This is either a list of values or a list of data collections
            if per_timestep_ is True.
"""

ghenv.Component.Name = "HB Annual Statistics"
ghenv.Component.NickName = 'AnnualStatistics'
ghenv.Component.Message = '1.9.2'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import json
import subprocess

try:
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.futil import write_to_file
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance_postprocess.dynamic import DynamicSchedule
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from pollination_handlers.outputs.helper import read_sensor_grid_result
except ImportError as e:
    raise ImportError('\nFailed to import pollination_handlers:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree,   \
        give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # compute the annual summary
    grid_filter_ = '*' if grid_filter_ is None else grid_filter_
    res_folder = _results
    per_timestep = False if per_timestep_ is None else per_timestep_
    
    # check to see if results use the newer numpy arrays
    if os.path.isdir(os.path.join(res_folder, '__static_apertures__')) or \
        os.path.isfile(os.path.join(res_folder, 'grid_states.json')):
        cmds = [folders.python_exe_path, '-m', 'honeybee_radiance_postprocess',
                'post-process', 'annual-statistics', res_folder, '-sf',
                'statistics']
        if len(_hoys_) != 0:
            hoys_str = '\n'.join(str(h) for h in _hoys_)
            hoys_file = os.path.join(res_folder, 'hoys.txt')
            write_to_file(hoys_file, hoys_str)
            cmds.extend(['--hoys-file', hoys_file])
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
        
        if per_timestep:
            cmds.extend(['--timestep'])
        
        use_shell = True if os.name == 'nt' else False
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        process = subprocess.Popen(
            cmds, cwd=res_folder, shell=use_shell, env=custom_env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()  # wait for the process to finish
        print(stderr)
        if process.returncode != 0:
            raise ValueError('Failed to compute annual statistics values.')
        
        res_dir = os.path.join(res_folder, 'statistics')
        average_values_dir = os.path.join(res_dir, 'average_values')
        median_values_dir = os.path.join(res_dir, 'median_values')
        minimum_values_dir = os.path.join(res_dir, 'minimum_values')
        maximum_values_dir = os.path.join(res_dir, 'maximum_values')
        cumulative_values_dir = os.path.join(res_dir, 'cumulative_values')
        
        if per_timestep is False:
            average = list_to_data_tree(read_sensor_grid_result(average_values_dir, 'average', 'full_id', False))
            median = list_to_data_tree(read_sensor_grid_result(median_values_dir, 'median', 'full_id', False))
            minimum = list_to_data_tree(read_sensor_grid_result(minimum_values_dir, 'minimum', 'full_id', False))
            maximum = list_to_data_tree(read_sensor_grid_result(maximum_values_dir, 'maximum', 'full_id', False))
            cumulative = list_to_data_tree(read_sensor_grid_result(cumulative_values_dir, 'cumulative', 'full_id', False))
        else:
            with open(os.path.join(average_values_dir, 'grids_info.json')) as json_file:
                grids_info = json.load(json_file)
            average = []
            median = []
            minimum = []
            maximum = []
            cumulative = []
            for grid_info in grids_info:
                with open(os.path.join(average_values_dir, '{}_average.json'.format(grid_info['full_id']))) as json_file:
                    data_dict = json.load(json_file)
                average.append(HourlyContinuousCollection.from_dict(data_dict))
                with open(os.path.join(median_values_dir, '{}_median.json'.format(grid_info['full_id']))) as json_file:
                    data_dict = json.load(json_file)
                median.append(HourlyContinuousCollection.from_dict(data_dict))
                with open(os.path.join(minimum_values_dir, '{}_minimum.json'.format(grid_info['full_id']))) as json_file:
                    data_dict = json.load(json_file)
                minimum.append(HourlyContinuousCollection.from_dict(data_dict))
                with open(os.path.join(maximum_values_dir, '{}_maximum.json'.format(grid_info['full_id']))) as json_file:
                    data_dict = json.load(json_file)
                maximum.append(HourlyContinuousCollection.from_dict(data_dict))
                with open(os.path.join(cumulative_values_dir, '{}_cumulative.json'.format(grid_info['full_id']))) as json_file:
                    data_dict = json.load(json_file)
                cumulative.append(HourlyContinuousCollection.from_dict(data_dict))
            average = list_to_data_tree(average)
            median = list_to_data_tree(median)
            minimum = list_to_data_tree(minimum)
            maximum = list_to_data_tree(maximum)
            cumulative = list_to_data_tree(cumulative)
    else:
        msg = 'Annual Statistics is only supported for Annual Daylight and Annual Irradiance ' \
            'simulations with NumPy arrays.'
        print(msg)
        give_warning(ghenv.Component, msg)