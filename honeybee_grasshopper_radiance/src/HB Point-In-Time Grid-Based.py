# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a point-in-time grid-based study for a Honeybee model.
_
Point-in-time recipes require a sky and can output illuminance, irradiance,
luminance or radiance.

-
    Args:
        _model: A Honeybee Model for which a point-in-time grid-based study will be run.
            Note that this model should have grids assigned to it in order
            to produce meaningfule results.
        _sky: A Radiance sky from any of the sky components under the "Light Sources" tab.
            Skies can be either CIE, ClimateBased/Custom, or for a specific
            Illuminance/Irradiance. This input can also just be a text definition
            of a sky's paramters. Examples include:
                * cie 21 Mar 9:00 -lat 41.78 -lon -87.75 -tz 5 -type 0
                * climate-based 21 Jun 12:00 -lat 41.78 -lon -87.75 -tz 5 -dni 800 -dhi 120
                * irradiance 0
        _metric_: Either an integer or the full name of a point-in-time metric to be computed
            by the recipe. (Default: illuminance). Choose from the following:
                * 0 = illuminance
                * 1 = irradiance
                * 2 = luminance
                * 3 = radiance
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
        results: Numbers for the point-in-time value at each sensor. Values are in the
            standard SI units of the requested input metric. These can be plugged
            into the "LB Spatial Heatmap" component along with meshes of the
            sensor grids to visualize results.
                * illuminance = lux (aka. lm/m2)
                * irradiance = W/m2
                * luminance = cd/m2 (aka. lm/m2-sr)
                * radiance = W/m2-sr
"""

ghenv.Component.Name = 'HB Point-In-Time Grid-Based'
ghenv.Component.NickName = 'PITGrid'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

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
    recipe = Recipe('point-in-time-grid')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('sky', _sky)
    recipe.input_value_by_name('metric', _metric_)
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
