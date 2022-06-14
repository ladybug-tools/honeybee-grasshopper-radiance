# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a daylight factor study for a Honeybee model.
_
Daylight Factor (DF) is defined as the ratio of the indoor daylight illuminance
to outdoor illuminance under an unobstructed overcast sky. It is expressed as a
percentage between 0 and 100.
_
Because daylight factor is computed using an overcast sky, it does not change
with [North, East, South, West] orientation. As such, it is more suited to
assessing daylight in climates where cloudy conditions are common. The "HB
Annual Daylight" recipe yields a much more accurate assessment of daylight
and is suitable for all climates, though it requires a significantly longer
calculation time than Daylight Factor.

-
    Args:
        _model: A Honeybee Model for which Daylight Factor will be simulated.
            Note that this model should have grids assigned to it in order
            to produce meaningfule results.
        grid_filter_: Text for a grid identifer or a pattern to filter the sensor grids of
            the model that are simulated. For instance, `first_floor_*` will simulate
            only the sensor grids that have an identifier that starts with
            `first_floor_`. By default, all grids in the model will be simulated.
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -aa 0.1 -ad 2048 -ar 64).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results. This input can also be
            the integer "2" to run the recipe silently.

    Returns:
        report: Reports, errors, warnings, etc.
        results: The daylight factor values from the simulation in percent. Each
            value is for a different sensor of the grid. These can be plugged
            into the "LB Spatial Heatmap" component along with meshes of the
            sensor grids to visualize results.
"""

ghenv.Component.Name = 'HB Daylight Factor'
ghenv.Component.NickName = 'DaylightFactor'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

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
    recipe = Recipe('daylight-factor')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name('results', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
