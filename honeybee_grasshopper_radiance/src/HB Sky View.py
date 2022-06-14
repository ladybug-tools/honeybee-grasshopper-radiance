# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a Sky View (SV) study for a Honeybee model.
_
Sky View is defined as the percent of the sky dome seen by a surface. These can
be computed either using a uniform (default) sky or a cloudy sky.
_
Note that computing cloudy Sky View for a vertically-oriented geometry (horizontal
sensor direction) will yield Vertical Sky Component (VSC) as described by the UK
Building Research Establishment (BRE). VSC is defined as the ratio of cloudy sky
illuminance falling on a vertical wall to the simultaneous horizontal illuminance
under an unobstructed sky [Littlefair, 1991].
_
Also note that this recipe still respects the transparency of objects, reducing
the percentage of the sky visible through a certain geometry by the transmittance
of that geometry.

-
    Args:
        _model: A Honeybee Model for which Sky View or Wky Exposure will be simulated.
            Note that this model should have grids assigned to it in order
            to produce meaningful results.
        cloudy_sky_: A boolean to note whether a uniform sky should be used  (False) or
            a cloudy overcast sky (True). (Default: False).
        grid_filter_: Text for a grid identifer or a pattern to filter the sensor grids of
            the model that are simulated. For instance, `first_floor_*` will simulate
            only the sensor grids that have an identifier that starts with
            `first_floor_`. By default, all grids in the model will be simulated.
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -aa 0.1 -ad 2048 -ar 64).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results.

    Returns:
        report: Reports, errors, warnings, etc.
        results: Numbers for the sky view or sky exposure at each sensor. These can be plugged
            into the "LB Spatial Heatmap" component along with meshes of the
            sensor grids to visualize results. Values are in percent (between 0
            and 100).
"""

ghenv.Component.Name = 'HB Sky View'
ghenv.Component.NickName = 'SkyView'
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
    recipe = Recipe('sky-view')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('cloudy-sky', cloudy_sky_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    project_folder = recipe.run(run_settings_, radiance_check=True)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name('results', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
