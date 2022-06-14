# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run an annual glare study for a Honeybee model to compute hourly Daylight Glare
Probability (DGP) for each sensor in a model's sensor grids.
_
This recipe uses the image-less glare method developed by Nathaniel Jones to
estimate glare at each sensor. More information on this method can be found here:
https://github.com/nljones/Accelerad/wiki/The-Imageless-Method-for-Spatial-and-Annual-Glare-Analysis
_
The resulting DGP is used to compute Glare Autonomy (GA), which is the percentage
of occupied time that a view is free of glare.

-
    Args:
        _model: A Honeybee Model for which Annual Daylight Glare Probability (DGP) will
            be simulated. Note that this model must have grids assigned to
            it and, typically, these are radial grids created using the
            "radial grid" components.
        _wea: A Wea object produced from the Wea components that are under the Light
            Sources tab. This can also be the path to a .wea or a .epw file.
            Note that the Wea must have a timestep of 1 to be used with this
            recipe.
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. This can
            also be Vector for the direction to North. (Default: 0).
        _glare_thresh_: A fractional number for the threshold of DGP above which conditions
            are considered to induce glare. This value is used when calculating
            glare autonomy, which is the percent of hours in which the view is
            free of glare. (Default: 0.4 for disturbing or intolerable glare).
        _luminance_fac_: Luminance factor in cd/m2. If the sky patch brightness
            is above this factor it will act as a glare source. (Default: 2000).
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
        results: Raw result files (.dgp) that contain Daylight Glare Probability (DGP)
            matrices for each sensor at each hour of the simulation. These can
            be postprocessed using various components under the 4::Results sub-tab.
        GA: Glare Autonomy (GA) results in percent. GA is the percentage of occupied hours
            that each view is free of glare (with a DGP below the glare threshold).
            These can be plugged into the "LB Spatial Heatmap" component along
            with meshes of the sensor grids to visualize results.
"""

ghenv.Component.Name = 'HB Imageless Annual Glare'
ghenv.Component.NickName = 'AnnualGlare'
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
    recipe = Recipe('imageless-annual-glare')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('glare-threshold', _glare_thresh_)
    recipe.input_value_by_name('luminance-factor', _luminance_fac_)
    recipe.input_value_by_name('schedule', _schedule_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name('results', project_folder))
        GA = recipe_result(recipe.output_value_by_name('ga', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
