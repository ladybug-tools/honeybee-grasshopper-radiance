# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a LEED v4.1 Daylight Option 2 point-in-time study for a Honeybee model.
_
This recipe calculates illuminance for two specific times on a clear sky day 
near the equinox: 9:00 AM and 3:00 PM. It determines compliance based on whether 
sensor points fall within the target luxury range.
_
GLARE CONTROL LOGIC:
* If '_glr_ctrl_' is set to True, the space is assumed to possess view-preserving
    automatic glare-control devices. Consequently, sensor points only need to
    achieve an illuminance level above 300 lux to pass.
* If '_glr_ctrl_' is set to False, sensor points must fall strictly between 300
    lux and 3,000 lux to be considered compliant.

-
    Args:
        _model: A Honeybee model in HBJSON file format (.json or .hbjson). 
            Note that this model must have sensor grids assigned to it.
        _wea: A Typical Meteorological Year (TMY) .wea or .epw file. The file must 
            be annual with a timestep of 1 for a non-leap year.
        north_: A number between 0 and 360 for rotation from North in degrees. 
            (Default: 0).
        grid_filter_: Text for a grid identifier or a pattern to filter the sensor grids of
            the model that are simulated. For instance, first_floor_* will simulate
            only the sensor grids that have an identifier that starts with
            first_floor_. By default, all grids in the model will be simulated.
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 5 -aa 0.1 -ad 2048 -ar 64).
        _glr_ctrl_: Set to True to specify that the model has view-preserving automatic 
            (with manual override) glare-control devices. (Default: True).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results. This input can also be
            the integer "2" to run the recipe silently.

    Returns:
        report: Reports, errors, warnings, etc.
        credit_summary: A summary containing the number of LEED credits achieved and 
            a summary of the percentage of the sensor grid area that meets the criteria.
        space_summary: A room-by-room breakdown containing the percentage of the sensor
            grid area in each space that meets the compliance criteria.
        combined_compliance: A folder containing pass/fail results for the combined 
            simulation as binary (1/0) values. Points must pass at BOTH 9 AM and 3 PM.
        illuminance_9am: A folder containing the raw illuminance results for the 9:00 AM 
            simulation in lux.
        illuminance_3pm: A folder containing the raw illuminance results for the 3:00 PM 
            simulation in lux.
        compliance_9am: A folder containing binary (1/0) pass/fail evaluation results 
            for the 9:00 AM simulation state.
        compliance_3pm: A folder containing binary (1/0) pass/fail evaluation results 
            for the 3:00 PM simulation state.
"""

ghenv.Component.Name = 'HB LEED Option II'
ghenv.Component.NickName = 'LEEDOptII'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from lbt_recipes.recipe import Recipe
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, recipe_result
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    glare_control = 'glare-control' if _glr_ctrl_ is True else 'no-glare-control'
    
    # create the recipe and set the input arguments
    recipe = Recipe('leed-daylight-option-two')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)
    recipe.input_value_by_name('glare-control-devices', glare_control)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        credit_summary = recipe_result(recipe.output_value_by_name('credit-summary', project_folder))
        space_summary = recipe_result(recipe.output_value_by_name('space-summary', project_folder))
        combined_compliance = recipe_result(recipe.output_value_by_name('pass-fail-combined', project_folder))
        illuminance_9am = recipe_result(recipe.output_value_by_name('illuminance-9am', project_folder))
        illuminance_3pm = recipe_result(recipe.output_value_by_name('illuminance-3pm', project_folder))
        compliance_9am = recipe_result(recipe.output_value_by_name('pass-fail-9am', project_folder))
        compliance_3pm = recipe_result(recipe.output_value_by_name('pass-fail-3pm', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))