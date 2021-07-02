# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run an annual solar irradiance study for a Honeybee model.
_
The fundamental calculation of this recipe is the same as that of "HB Annual
Daylight" in that a detailed accounting of direct sun is performed at each
simulation step. However, this recipe computes broadband solar irradiance in
W/m2 instead of visible illuminance in lux.
_
As such, this recipe can not only be used to get a high-accuraccy tally of
cumulative radiation over the Wea time period but the `peak_irradiance` and the
detailed result matrices are suitable for assessing the radiant temperatures
expereinced by occupants and determining the worst-case solar load from clear
sky Weas that represent cooling design days.

-
    Args:
        _model: A Honeybee Model for which Annual Radiation will be simulated.
            Note that this model should have grids assigned to it in order
            to produce meaningfule results.
        _wea: A Wea object produced from the Wea components that are under the Light
            Sources tab. This can also be the path to a .wea or a .epw file.
        _timestep_: An integer for the timestep of the inpput _wea. This value is used
            to compute average irradiance and cumulative radiation. (Default: 1)
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. This can
            also be Vector for the direction to North. (Default: 0).
        grid_filter_: Text for a grid identifer or a pattern to filter the sensor grids of
            the model that are simulated. For instance, first_floor_* will simulate
            only the sensor grids that have an identifier that starts with
            first_floor_. By default, all grids in the model will be simulated.
        sensor_count_: Integer for the maximum number of sensor grid points per
            parallel execution. (Default: 200).
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -ad 5000 -lw 2e-05).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results.

    Returns:
        report: Reports, errors, warnings, etc.
        results: Raw result files (.ill) that contain matrices of irradiance in W/m2
            for each time step of the wea.
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
ghenv.Component.Message = '1.2.0'
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
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('sensor-count', sensor_count_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    project_folder = recipe.run(run_settings_, radiance_check=True)

    # load the results
    results = recipe_result(recipe.output_value_by_name('results', project_folder))
    avg_irr = recipe_result(recipe.output_value_by_name('average-irradiance', project_folder))
    peak_irr = recipe_result(recipe.output_value_by_name('peak-irradiance', project_folder))
    radiation = recipe_result(recipe.output_value_by_name('cumulative-radiation', project_folder))
