# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run an annual daylight study for a Honeybee model.

-
    Args:
        _model: A Honeybee Model for which Annual Daylight will be simulated.
            Note that this model should have grids assigned to it in order
            to produce meaningfule results.
        _wea: A Wea object produced from the Wea components that are under the Light
            Sources tab. This can also be the path to a .wea or a .epw file.
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. This can
            also be Vector for the direction to North. (Default: 0).
        _thresholds_: A string to change the threshold for daylight autonomy and useful
            daylight illuminance. Valid keys are -t for daylight autonomy threshold,
            -lt for the lower threshold for useful daylight illuminance and
            -ut for the upper threshold. The order of the keys is not important
            and you can include one or all of them. For instance if you only want
            to change the upper threshold to 2000 lux you should use -ut 2000
            as the input. (Default: -t 300 -lt 100 -ut 3000).
        _schedule_: An annual occupancy schedule, either as a Ladybug Hourly Continuous
            Data Collection or a HB-Energy schedule object. This can also be the
            path to a CSV file with 8760 rows or the identifier of a schedule in
            the honeybee-energy schedule library. Any value in this schedule
            that is 0.1 or above will be considered occupied.
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
        results: Folder with raw result files (.ill) that contain illuminance matrices.
        DA: Daylight autonomy results.
        cDA: Continuous daylight autonomy results.
        UDI: Useful daylight illuminance results.
        UDI_low: Results for the percent of time that is below the lower threshold
            of useful daylight illuminance.
        UDI_up: Results for the percent of time that is above the upper threshold
            of useful daylight illuminance.
"""

ghenv.Component.Name = 'HB Annual Daylight'
ghenv.Component.NickName = 'AnnualDaylight'
ghenv.Component.Message = '1.2.2'
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
    recipe = Recipe('annual-daylight')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('thresholds', _thresholds_)
    recipe.input_value_by_name('schedule', _schedule_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('sensor-count', sensor_count_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    project_folder = recipe.run(run_settings_, radiance_check=True)

    # load the results
    results = recipe_result(recipe.output_value_by_name('results', project_folder))
    DA = recipe_result(recipe.output_value_by_name('da', project_folder))
    cDA = recipe_result(recipe.output_value_by_name('cda', project_folder))
    UDI = recipe_result(recipe.output_value_by_name('udi', project_folder))
    UDI_low = recipe_result(recipe.output_value_by_name('udi-lower', project_folder))
    UDI_up = recipe_result(recipe.output_value_by_name('udi-upper', project_folder))
