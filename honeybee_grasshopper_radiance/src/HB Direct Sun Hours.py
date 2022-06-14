# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate the number of hours of direct sun received by grids of sensors in a
Honeybee model.
_
The fundamental calculation of this recipe is the same as that of the "LB Direct
Sun Hours" component except that this recipe uses Radiance, which allows the
simulation to scale better for large numbers of sensors.

-
    Args:
        _model: A Honeybee Model for which Direct Sun Hours will be simulated.
            Note that this model should have grids assigned to it in order
            to produce meaningfule results.
        _wea: A Wea object produced from the Wea components that are under the Light
            Sources tab. This can also be the path to a .wea or a .epw file.
        _timestep_: An integer for the timestep of the inpput _wea. This value will
            be used to ensure the units of the results are in hours. (Default: 1)
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. This can
            also be Vector for the direction to North. (Default: 0).
        grid_filter_: Text for a grid identifer or a pattern to filter the sensor grids of
            the model that are simulated. For instance, first_floor_* will simulate
            only the sensor grids that have an identifier that starts with
            first_floor_. By default, all grids in the model will be simulated.
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results. This input can also be
            the integer "2" to run the recipe silently.

    Returns:
        report: Reports, errors, warnings, etc.
        results: Raw result files (.ill) that contain matrices of zero/one values
            indicating whether each sensor is exposed to the sun at a given
            time step of the input Wea.
        hours: The cumulative number of hours that each sensor can see the sun.
            Each value is always in hours provided that the input _timestep_
            is the same as the input Wea.
"""

ghenv.Component.Name = 'HB Direct Sun Hours'
ghenv.Component.NickName = 'DirectSunHours'
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
    recipe = Recipe('direct-sun-hours')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('timestep', _timestep_)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name(
            'direct-sun-hours', project_folder))
        hours = recipe_result(recipe.output_value_by_name(
            'cumulative-sun-hours', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
