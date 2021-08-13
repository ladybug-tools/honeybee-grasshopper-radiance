# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Honeybee.
#
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Get the average illuminance or irradiance value from an annual daylight or irradiance
simulation.
_
This can also be used to obtain cumulative radiation values in the case of an annual
irradiance simulation.
_
The _hoys_ input can be used to filter the data for a particular time period or
hour/timestep of the simulation.

-
    Args:
        _results: An list of annual Radiance result files from either the "HB Annual Daylight"
            or the "HB Annual Irradiance" component (containing the .ill files and
            the sun-up-hours.txt). This can also be just the path to the folder
            containing these result files.
        _hoys_: An optional numbers or list of numbers to select the hours of the year (HOYs)
            for which results will be computed. These HOYs can be obtained from the
            "LB Calculate HOY" or the "LB Analysis Period" components. If None, all
            hours of the results will be used.
        timestep_: The timesteps per hour of the Wea that was used for the analysis.
            This will be used to ensure cumulative values are in the correct
            units (with hours as the unit). (Default: 1).
        grid_filter_: The name of a grid or a pattern to filter the grids. For instance,
            first_floor_* will simulate only the sensor grids that have an
            identifier that starts with first_floor_. By default all the grids
            will be processed.

    Returns:
        report: Reports, errors, warnings, etc.
        avg_vals: Average illuminance or irradiance valules for each sensor in lux or W/m2.
            Each value is for a different sensor of the grid. These can be plugged
            into the "LB Spatial Heatmap" component along with meshes of the sensor
            grids to visualize results.
        cumul_vals: In the case of an annual irradaince simulation, this is the cumulative
            radiation valules for each sensor in Wh/m2. For annual daylight,
            it is cumulative illuminance. These can be plugged into the "LB
            Spatial Heatmap" component along with meshes of the sensor
            grids to visualize results.
"""

ghenv.Component.Name = 'HB Annual Result Values'
ghenv.Component.NickName = 'AnnualValues'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os

try:
    from honeybee_radiance.postprocess.annualdaylight import _process_input_folder
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def parse_sun_up_hours(sun_up_hours, hoys, timestep):
    """Parse the sun-up hours from the result file .txt file.

    Args:
        sun_up_hours: A list of integers for the sun-up hours.
        hoys: A list of 8760 * timestep values for the hoys to select. If an empty
            list is passed, None will be returned.
        timestep: Integer for the timestep of the analysis.
    """
    if len(hoys) != 0:
        schedule = [False] * (8760 * timestep)
        for hr in hoys:
            schedule[int(hr * timestep)] = True
        su_pattern = [schedule[int(h * timestep)] for h in sun_up_hours]
        return su_pattern


def average_values(ill_file, su_pattern, timestep):
    """Compute average/cumulative values for a given result file."""
    avg_vals, cumul_vals = [], []
    with open(ill_file) as results:
        if su_pattern is None:  # no HOY filter on results
            for pt_res in results:
                values = [float(r) for r in pt_res.split()]
                total_val = sum(values)
                avg_vals.append(total_val / len(values))
                cumul_vals.append(total_val / timestep)
        else: 
            for pt_res in results:
                values = [float(r) for r, is_hoy in zip(pt_res.split(), su_pattern) if is_hoy]
                total_val = sum(values)
                try:
                    avg_vals.append(total_val / len(values))
                    cumul_vals.append(total_val / timestep)
                except ZeroDivisionError:
                    avg_vals.append(0)
                    cumul_vals.append(0)
    return avg_vals, cumul_vals


if all_required_inputs(ghenv.Component):
    # set default values
    grid_filter_ = '*' if grid_filter_ is None else grid_filter_
    timestep_ = 1 if timestep_ is None else timestep_

    # get the relevant .ill files
    res_folder = os.path.dirname(_results[0]) if os.path.isfile(_results[0]) \
        else _results[0]
    grids, sun_up_hours = _process_input_folder(res_folder, grid_filter_)
    su_pattern = parse_sun_up_hours(sun_up_hours, _hoys_, timestep_)

    # compute the annual metrics
    avg_vals, cumul_vals = [], []
    for grid_info in grids:
        ill_file = os.path.join(res_folder, '%s.ill' % grid_info['full_id'])
        irr, rad = average_values(ill_file, su_pattern, timestep_)
        avg_vals.append(irr)
        cumul_vals.append(rad)
    avg_vals = list_to_data_tree(avg_vals)
    cumul_vals = list_to_data_tree(cumul_vals)
