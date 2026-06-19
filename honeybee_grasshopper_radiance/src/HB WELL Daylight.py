# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a WELL v2 Daylight compliance study (Features L01 and L06) for a Honeybee model.
_
This recipe executes an annual climate-based simulation using the 2-phase daylight 
coefficient method. It automates the extraction of localized daylight hours directly 
from an EPW file and processes automated aperture group blinds to verify both spatial 
daylight access and dynamic glare control metrics.
_
The component evaluates criteria for two primary features:
* WELL Feature L01: Evaluates annual daylight via the IES LM-83 and EN 17037 methodology.
* WELL Feature L06: Evaluates annual daylight via the IES LM-83 and EN 17037 methodology.
_
SIMULATION REQUIREMENTS:
* ROOMS: The model must consist of Honeybee Rooms.
* APERTURE GROUPS: For dynamic shading to work, you must assign aperture groups 
    to your Honeybee Apertures through "HB Automatic Aperture Group" (room_based must
    be True) or "HB Dynamic Aperture Group" for more control of the grouping.

-
    Args:
        _model: A Honeybee Model for which WELL Daylight 4b will be simulated.
            Note that this model must have grids assigned to it. It is also required
            that the model consists of rooms and that aperture groups be assigned
            to exterior apertures.
        _epw: An EPW or Wea object produced from the Wea components that are under
            the Light Sources tab. This can also be the path to a .wea or a .epw file.
            Note that the EPW and Wea must have a timestep of 1 to be used with this
            recipe. This input is used to create the "daylight hours" schedule; the
            daylight hours schedule is only used for the EN 17037 method. If an EPW
            is used, the schedule is based on global horizontal illuminance; if a
            Wea is used, it is based on global horizontal irradiance.
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. This can
            also be a Vector for the direction to North. (Default: 0).
        grid_filter_: Text for a grid identifier or a pattern to filter the sensor grids of
            the model that are simulated. For instance, first_floor_* will simulate
            only the sensor grids that have an identifier that starts with
            first_floor_. By default, all grids in the model will be simulated.
        radiance_par_: Text specifying the radiance parameters for ray tracing. 
            (Default: -ab 2 -ad 5000 -lw 2e-05 -dr 0).
        _diff_trans_: Diffuse visible transmission of the aperture group blinds when 
            deployed. (Default: 0.05 / 5%).
        _spec_trans_: Specular visible transmission of the aperture group blinds when 
            deployed. (Default: 0.0001 / 0%).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results. This input can also be
            the integer "2" to run the recipe silently.

    Returns:
        report: Reports, errors, warnings, execution logs, etc.
        results: A folder path containing the raw hourly illuminance matrix data tables 
            (`.ill`) generated for every sensor grid.
        l01_compliance: A summary of L01 compliance for both IES LM-83 and EN 17037.
        l06_compliance: A summary of L06 compliance for both IES LM-83 and EN 17037.
        dynamic_schedule: A list of Ladybug Data Collection, where each collection
            represents the dynamic schedule for an aperture group. The schedules
            can be visualized with the 'Hourly Plot' component.
"""

ghenv.Component.Name = 'HB WELL Daylight'
ghenv.Component.NickName = 'WELLDaylight'
ghenv.Component.Message = '1.10.0'
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
    recipe = Recipe('well-daylight')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('epw', _epw)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('grid-filter', grid_filter_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)
    recipe.input_value_by_name('diffuse-transmission', _diff_trans_)
    recipe.input_value_by_name('specular-transmission', _spec_trans_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name('results', project_folder))
        l01_compliance = recipe_result(recipe.output_value_by_name('l01-summary', project_folder))
        l06_compliance = recipe_result(recipe.output_value_by_name('l06-summary', project_folder))
        dynamic_schedule = recipe_result(recipe.output_value_by_name('dynamic-schedule', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))