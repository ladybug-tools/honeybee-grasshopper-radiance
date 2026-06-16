# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run an annual daylight compliance study according to European Standard EN 17037.
_
This recipe executes a climate-based annual simulation using a 2-phase daylight 
coefficient method. It automatically parses the input EPW file to isolate the evaluation 
to unique, location-specific daylight hours (discarding night intervals). 
_
COMPLIANCE METRICS EVALUATED:
* EN 17037 Metrics: Specifically gauges target illuminance thresholds across a 
    set percentage of the space for at least half of the daylight hours of the year.

-
    Args:
        _model: A Honeybee Model for which Annual Daylight EN17037 will be simulated.
            Note that this model must have grids assigned to it.
        _epw: An EPW weather file containing meteorological data used to compute
            daylight hours for the post-processing schedule.
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. This can
            also be Vector for the direction to North. (Default: 0).
        grid_filter_: Text for a grid identifer or a pattern to filter the sensor grids of
            the model that are simulated. For instance, first_floor_* will simulate
            only the sensor grids that have an identifier that starts with
            first_floor_. By default, all grids in the model will be simulated.
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -ad 5000 -lw 2e-05).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results. This input can also be
            the integer "2" to run the recipe silently.

    Returns:
        report: Reports, errors, warnings, execution logs, etc.
        results: Raw result files (.ill) that contain illuminance matrices for each sensor
            at each hour of the simulation. These can be postprocessed using
            various components under the 4::Results sub-tab.
        summary: A comma-separated summary report profiling compiled scorecards 
            across all analyzed sensor grids.
        daylight_hours: Occupancy schedule used in the post-processing. This schedule
            consists of the half of the year with the largest quantity of daylight.
"""

ghenv.Component.Name = 'HB Annual Daylight EN17037'
ghenv.Component.NickName = 'EN17037Daylight'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from lbt_recipes.recipe import Recipe
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, recipe_result
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    
    # create the recipe and set the input arguments
    recipe = Recipe('annual-daylight-en17037')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('epw', _epw)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name('results', project_folder))
        summary = recipe_result(recipe.output_value_by_name('summary', project_folder))
        daylight_hours = recipe_result(recipe.output_value_by_name('daylight-hours', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))