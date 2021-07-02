# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Honeybee.
#
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Compute annual irradiance metrics from detailed result matrices (.ill files).

-
    Args:
        _results: An list of annual Radiance result files from the "HB Annual Irradiance"
            component.  This should include both the .ill files and the
            sun-up-hours.txt
        hoys_: An optional integer or list of integers (each greater than or equal to 0)
            to select the hours of the year (HOYs) for which radiation results
            will be displayed. These HOYs can be obtained from the "LB Calculate
            HOY" or the "LB Analysis Period" components. If None, all hours of
            the results will be used.
        timestep_: The timesteps per hour of the Wea that was used for the radiation analysis.
            This will be used to ensure radiation values are in the correct
            units. (Default: 1).

    Returns:
        report: Reports, errors, warnings, etc.
        irradiance: Average irradiance valules for each sensor in W/m2.
        radiation: Cumulative radiation valules for each sensor in Wh/m2.
"""

ghenv.Component.Name = "HB Annual Irradiance Result"
ghenv.Component.NickName = 'IrradianceResult'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def parse_sun_up_hours(result_files, hoys, timestep):
    """Parse the sun-up hours from the result file .txt file.

    Args:
        result_files: A list of result files that contains the .txt file.
        hoys: A list of 8760 * timestep values for the hoys to select. If an empty
            list is passed, None will be returned.
    """
    for i, r_file in enumerate(result_files):
        if r_file.endswith('.txt'):
            result_files.pop(i)  # remove it from the list
            if len(hoys) != 0:
                schedule = [False] * (8760 * timestep)
                for hr in hoys:
                    schedule[int(hr * timestep)] = True
                with open(r_file) as soh_f:
                    occ_pattern = [schedule[int(float(h) * timestep)] for h in soh_f]
                return occ_pattern


def cumulative_radiation(ill_file, occ_pattern, timestep):
    """Compute cumulative radiation for a given result file."""
    irradiance, radiation = [], []
    with open(ill_file) as results:
        if occ_pattern is None:  # no HOY filter on results
            for pt_res in results:
                values = [float(r) for r in pt_res.split()]
                total_val = sum(values)
                irradiance.append(total_val / len(values))
                radiation.append(total_val / timestep)
        else: 
            for pt_res in results:
                values = [float(r) for r, is_hoy in zip(pt_res.split(), occ_pattern) if is_hoy]
                total_val = sum(values)
                irradiance.append(total_val / len(values))
                radiation.append(total_val / timestep)
    return irradiance, radiation


if all_required_inputs(ghenv.Component):
    # process the sun-up hours and parse timestep
    timestep_ = 1 if timestep_ is None else timestep_
    occ_pattern = parse_sun_up_hours(_results, hoys_, timestep_)

    # compute the annual metrics
    irradiance, radiation = [], []
    for ill_file in _results:
        irr, rad = cumulative_radiation(ill_file, occ_pattern, timestep_)
        irradiance.append(irr)
        radiation.append(rad)
    irradiance = list_to_data_tree(irradiance)
    radiation = list_to_data_tree(radiation)
