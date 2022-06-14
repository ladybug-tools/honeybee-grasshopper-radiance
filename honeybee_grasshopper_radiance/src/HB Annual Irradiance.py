# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run an annual irradiance study for a Honeybee model to compute hourly solar
irradiance for each sensor in a model's sensor grids.
_
The fundamental calculation of this recipe is the same as that of "HB Annual
Daylight" in that an enhaced 2-phase method is used to accurately account for
direct sun at each simulation step. However, this recipe computes broadband
solar irradiance in W/m2 instead of visible illuminance in lux.
_
Consequently, the average irradiance and cumulative radiation values produced from
this recipe are more accurate than those produced by the "HB Cumulative Radiation"
recipe. Furthermore, because the hourly irriadiance values are accurate, this
recipe can be used to evaluate `peak_irradiance` and determine the worst-case
solar loads over clear sky Weas that represent cooling design days.

-
    Args:
        _model: A Honeybee Model for which Annual Irradiance will be simulated.
            Note that this model must have grids assigned to it.
        _wea: A Wea object produced from the Wea components that are under the Light
            Sources tab. This can also be the path to a .wea or a .epw file.
        _timestep_: An integer for the timestep of the inpput _wea. This value is used
            to compute average irradiance and cumulative radiation. (Default: 1)
        visible_: Boolean to indicate the type of irradiance output, which can be solar (False)
            or visible (True). Note that the output values will still be
            irradiance (W/m2) when "visible" is selected but these irradiance
            values will be just for the visible portion of the electromagnetic
            spectrum. The visible irradiance values can be converted into
            illuminance by multiplying them by the Radiance luminous efficacy
            factor of 179. (Default: False).
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
        results: Raw result files (.ill) that contain matrices of irradiance in W/m2
            for each time step of the wea.
        res_direct: Raw result files (.ill) that contain irradiance matrices for just the
            direct sun at each hour of the simulation. These can be postprocessed
            using various components under the 4::Results sub-tab.
        avg_irr: The average irradiance in W/m2 for each sensor over the Wea time period.
        peak_irr: The highest irradiance value in W/m2 during the Wea time period. This
            is suitable for assessing the worst-case solar load of clear skies on
            cooling design days. It can also be used to determine the highest
            radiant temperatures that occupants might experience in over the
            time period of the Wea.
        radiation: The cumulative radiation in kWh/m2 over the Wea time period.
"""

ghenv.Component.Name = 'HB Annual Irradiance'
ghenv.Component.NickName = 'AnnualIrradiance'
ghenv.Component.Message = '1.5.0'
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
    recipe = Recipe('annual-irradiance')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('timestep', _timestep_)
    recipe.input_value_by_name('output-type', visible_)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name('results', project_folder))
        res_direct = recipe_result(recipe.output_value_by_name('results-direct', project_folder))
        avg_irr = recipe_result(recipe.output_value_by_name('average-irradiance', project_folder))
        peak_irr = recipe_result(recipe.output_value_by_name('peak-irradiance', project_folder))
        radiation = recipe_result(recipe.output_value_by_name('cumulative-radiation', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
