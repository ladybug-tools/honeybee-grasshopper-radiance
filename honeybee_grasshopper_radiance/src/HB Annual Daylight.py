# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run an annual daylight study for a Honeybee model to compute hourly illuminance
for each sensor in a model's sensor grids.
_
This recipe uses an enhanced 2-phase method for daylight simulation which accurately
models direct sun by tracing rays from each sensor to the solar position at each
hour of the calculation.
_
The resulting illuminance is used to compute the following metrics:
_
* Daylight Autonomy (DA) - The percentage of occupied hours that each sensor
        recieves more than the illuminance threshold.
* Continuous Daylight Autonomy (cDA) - Similar to DA except that values below the
        illuminance threshold can still count partially towards the final percentage.
* Useful Daylight Illuminance (UDI) - The percentage of occupied hours that
        illuminace falls between minimum and maximum thresholds

-
    Args:
        _model: A Honeybee Model for which Annual Daylight will be simulated.
            Note that this model must have grids assigned to it.
        _wea: A Wea object produced from the Wea components that are under the Light
            Sources tab. This can also be the path to a .wea or a .epw file.
            Note that the Wea must have a timestep of 1 to be used with this
            recipe.
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
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -ad 5000 -lw 2e-05).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results. This input can also be
            the integer "2" to run the recipe silently.

    Returns:
        report: Reports, errors, warnings, etc.
        results: Raw result files (.ill) that contain illuminance matrices for each sensor
            at each hour of the simulation. These can be postprocessed using
            various components under the 4::Results sub-tab.
        DA: Daylight autonomy results in percent. DA is the percentage of occupied hours
            that each sensor recieves equal or more than the illuminance threshold.
            Each value is for a different sensor of the grid. These can be plugged
            into the "LB Spatial Heatmap" component along with meshes of the sensor
            grids to visualize results. These can also be connected to the "HB
            Spatial Daylight Autonomy" component to compute spatial daylight
            autonomy for each grid. Note that the resulting sDA is only compliant
            with LEED if dynamic blinds have been simulated using the methods
            in IES-LM-83-12.
        cDA: Continuous daylight autonomy results in percent. cDA is similar to DA except
            that values below the illuminance threshold can still count partially
            towards the final percentage. Each value is for a different
            sensor of the grid. These can be plugged into the "LB Spatial Heatmap"
            component along with meshes of the sensor grids to visualize results.
        UDI: Useful daylight illuminance results in percent. UDI is the percentage of
            occupied hours that illuminace falls between minimum and maximum
            thresholds. Each value is for a different sensor of the grid. These
            can be plugged into the "LB Spatial Heatmap" component along with
            meshes of the sensor grids to visualize results.
        UDI_low: Results for the percent of time that is below the lower threshold
            of useful daylight illuminance in percent. Each value is for a different
            sensor of the grid. These can be plugged into the "LB Spatial Heatmap"
            component along with meshes of the sensor grids to visualize results.
        UDI_up: Results for the percent of time that is above the upper threshold
            of useful daylight illuminance in percent. Each value is for a different
            sensor of the grid. These can be plugged into the "LB Spatial Heatmap"
            component along with meshes of the sensor grids to visualize results.
"""

ghenv.Component.Name = 'HB Annual Daylight'
ghenv.Component.NickName = 'AnnualDaylight'
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
    recipe = Recipe('annual-daylight')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('thresholds', _thresholds_)
    recipe.input_value_by_name('schedule', _schedule_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name('results', project_folder))
        DA = recipe_result(recipe.output_value_by_name('da', project_folder))
        cDA = recipe_result(recipe.output_value_by_name('cda', project_folder))
        UDI = recipe_result(recipe.output_value_by_name('udi', project_folder))
        UDI_low = recipe_result(recipe.output_value_by_name('udi-lower', project_folder))
        UDI_up = recipe_result(recipe.output_value_by_name('udi-upper', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
