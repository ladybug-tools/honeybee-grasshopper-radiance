# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run daylight factor for a single model.

    Args:
        _model: A Honeybee Model for which Daylight Factor will be simulated.
            Note that this model should have grids assigned to it in order
            to produce meaningful results.
        grid_filter_: Text for a grid identifer or a pattern to filter the sensor grids of
            the model that are simulated. For instance, first_floor_* will simulate
            only the sensor grids that have an identifier that starts with
            first_floor_. By default, all grids in the model will be simulated.
        sensor_count_: Integer for the maximum number of sensor grid points per
            parallel execution. (Default: 200).
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -aa 0.1 -ad 2048 -ar 64).

    Returns:
        recipe: A simulation recipe that contains a simulation instructions and
            input arguments. Use the "HB Run Recipe" component to execute the
            recipe and get results.
"""

ghenv.Component.Name = 'HB Daylight Factor'
ghenv.Component.NickName = 'DaylightFactor'
ghenv.Component.Message = '1.1.5'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os

try:
    from honeybee.config import folders as hb_folders
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from lbt_recipes.recipe import Recipe
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # create the recipe and set the input arguments
    recipe = Recipe('daylight_factor')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('sensor-grid', grid_filter_)
    recipe.input_value_by_name('sensor-count', sensor_count_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # set the default project folder based on the model name if available
    if isinstance(_model, Model):
        recipe.default_project_folder = os.path.join(
            hb_folders.default_simulation_folder, _model.identifier, 'Radiance')
