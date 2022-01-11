# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a point-in-time view-based study for a Honeybee model.
_
Point-in-time view-based recipes require a sky and can output High Dynamic Range
(HDR) images of illuminance, irradiance, luminance or radiance.
_
The `view_count_` input can be used to split each view for parallel processing,
producing multiple images that are recombined into a single .HDR for the view at
the end of the recipe. The recombination process automatically includes an
anti-aliasing pass that smooths and improves the quality of the image. The recipe
also performs an overture calculation prior to splitting each view, which results
in an image with better interpolation between neighboring pixels.

-
    Args:
        _model: A Honeybee Model for which a point-in-time view-based study will be run.
            Note that this model should have views assigned to it in order
            to produce meaningfule results.
        _sky: A Radiance sky from any of the sky components under the "Light Sources" tab.
            Skies can be either CIE, ClimateBased/Custom, or for a specific
            Illuminance/Irradiance. This input can also just be a text definition
            of a sky's paramters. Examples include:
                * cie 21 Mar 9:00 -lat 41.78 -lon -87.75 -tz 5 -type 0
                * climate-based 21 Jun 12:00 -lat 41.78 -lon -87.75 -tz 5 -dni 800 -dhi 120
                * irradiance 0
        _metric_: Either an integer or the full name of a point-in-time metric to be
            computed by the recipe. (Default: luminance). Choose from the following:
                * 0 = illuminance
                * 1 = irradiance
                * 2 = luminance
                * 3 = radiance
        _resolution_: An integer for the maximum dimension of each image in pixels
            (either width or height depending on the input view angle and
            type). (Default: 800).
        view_filter_: Text for a view identifer or a pattern to filter the views of the
            model that are simulated. For instance, `first_floor_*` will simulate
            only the views that have an identifier that starts with `first_floor_`.
            By default, all views in the model will be simulated.
        skip_overture_: A boolean to note whether an ambient file (.amb) should be
            generated for an overture calculation before the view is split
            into smaller views. With an overture calculation, the ambient file
            (aka ambient cache) is first populated with values. Thereby ensuring
            that - when reused to create an image - Radiance uses interpolation
            between already calculated values rather than less reliable
            extrapolation. The overture calculation has comparatively small
            computation time to full rendering but is single-core can become
            time consuming in situations with a high view_count_ and workers.
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -aa 0.25 -ad 512 -ar 16).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results. This input can also be
            the integer "2" to run the recipe silently.

    Returns:
        report: Reports, errors, warnings, etc.
        results: High Dynamic Range (HDR) images for each View in the model. These can be
            plugged into the Ladybug "Image Viewer" component to preview the image. 
            They can also be plugged into the "HB False Color" component to convert 
            the image into a false color version. Lastly, it can be connected to 
            the "HB HDR to GIF" component to get a GIF image that is more portable 
            and easily previewed by different software. Pixel values are in the
            standard SI units of the requested input metric.
                * illuminance = lux (aka. lm/m2)
                * irradiance = W/m2
                * luminance = cd/m2 (aka. lm/m2-sr)
                * radiance = W/m2-sr
"""

ghenv.Component.Name = 'HB Point-In-Time View-Based'
ghenv.Component.NickName = 'PITView'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os

try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from lbt_recipes.recipe import Recipe
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, recipe_result, \
        recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # create the recipe and set the input arguments
    recipe = Recipe('point-in-time-view')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('sky', _sky)
    recipe.input_value_by_name('metric', _metric_)
    recipe.input_value_by_name('resolution', _resolution_)
    recipe.input_value_by_name('view-filter', view_filter_)
    recipe.input_value_by_name('skip-overture', skip_overture_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(run_settings_, radiance_check=True, silent=silent)

    # load the results
    try:
        results = recipe_result(recipe.output_value_by_name('results', project_folder))
        if hasattr(results, 'BranchCount') and results.BranchCount == 0:
            raise ValueError()
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
