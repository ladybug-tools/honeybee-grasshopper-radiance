# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a cumulative radiation study for a Honeybee model.
_
This recipe calculates cumulative radiation (kWh/m2) and average irradiance (W/m2)
over the time period of a specified Wea.
_
The fundamental calculation of this recipe is the same as that of the "LB Incident
Radiation" component except that this recipe uses Radiance and can therefore
account for ambient reflections. Like LB Incident Radiation, the direct sun in this
recipe is diffused between several sky patches and so the precise line between shadow
and sun for each hour is blurred. This approximation is acceptable for studies
where one is only concerned about the average/total conditions over time and the
timestep-by-timestep irradiance values do not need to be exact. For accurate
modeling of direct irradiance on a timestep-by-timestep basis, see the "HB Annual
Irradiance" recipe.

-
    Args:
        _model: A Honeybee Model for which Cumulative Radiation will be simulated.
            Note that this model should have grids assigned to it.
        _wea: A Wea object produced from the Wea components that are under the Light
            Sources tab. This can also be the path to a .wea or a .epw file.
        _timestep_: An integer for the timestep of the inpput _wea. (Default: 1)
        _sky_density_: An integer for the number of times that that the original Tregenza
            sky patches are subdivided. 1 indicates that 145 patches are used
            to describe the sky hemisphere, 2 indicates that 577 patches describe
            the hemisphere, and each successive value will roughly quadruple the
            number of patches used. Setting this to a high value will result in
            a more accurate analysis but will take longer to run. (Default: 1).
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
        report: Reports, errors, warnings, etc.
        avg_irr: The average irradiance in W/m2 for each sensor over the Wea time period.
        radiation: The cumulative radiation in kWh/m2 over the Wea time period.
"""

ghenv.Component.Name = 'HB Cumulative Radiation'
ghenv.Component.NickName = 'CumulativeRadiation'
ghenv.Component.Message = '1.4.0'
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
    recipe = Recipe('cumulative-radiation')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('timestep', _timestep_)
    recipe.input_value_by_name('sky-density', _sky_density_)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        avg_irr = recipe_result(recipe.output_value_by_name('average-irradiance', project_folder))
        radiation = recipe_result(recipe.output_value_by_name('cumulative-radiation', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
