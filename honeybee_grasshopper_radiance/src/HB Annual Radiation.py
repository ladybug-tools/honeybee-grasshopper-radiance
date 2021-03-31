# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run an annual radiation study for a Honeybee model.
_
The annual radiation values will be for each timestep of the input wea file.
_
Total radiation is calculated by summing together the direct irradiance from
sun disks and the contribution from indirect sky radiation.

-
    Args:
        _model: A Honeybee Model for which Annual Radiation will be simulated.
            Note that this model should have grids assigned to it in order
            to produce meaningfule results.
        _wea: A Wea object produced from the Wea components that are under the Light
            Sources tab. This can also be the path to a .wea or a .epw file.
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
        total: Folder with raw result files (.ill) that contain irradiance matrices
            for the total radiation at each sensor and timestep.
        direct: Folder with raw result files (.ill) that contain irradiance matrices
            for the direct radiation at each sensor and timestep.
"""

ghenv.Component.Name = 'HB Annual Radiation'
ghenv.Component.NickName = 'AnnualRadiation'
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
    recipe = Recipe('annual-radiation')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('wea', _wea)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('sensor-count', sensor_count_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    project_folder = recipe.run(run_settings_, radiance_check=True)

    # load the results
    total = recipe_result(recipe.output_value_by_name('total-radiation', project_folder))
    direct = recipe_result(recipe.output_value_by_name('direct-radiation', project_folder))
