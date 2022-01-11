# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run a quick view-based Radiance simulation to visualize the properties of Honeybee
objects within Radiance.
_
Note that this simulation is always run on a single processor and will only show
static Radiance properties (no dynamic Aperture or Shade properties). Accordingly, this
component is only intended for quick checks of properties. For full customization
of view-based simulations, the "HB Point-in-time View-based" recipe should be used.

-
    Args:
        _hb_objs: An array of honeybee Rooms, Faces, Apertures, Doors or Shades to be
            visualized in Radiance. This can also be an entire Model to be
            visualized.
        _view_: An optional Honeybee-Radiance view to specify the view to render. If
            unspecified, the currently active Rhino viewport will be rendered.
        _sky_: An optional Radiance sky from any of the sky components under the "Light
            Sources" tab. If unspecified, a uniform sky with 10000 lux will be used.
        adj_expos_: Boolean to note whether the exposure of the image should be adjusted to
            mimic the human visual response in the output. The goal of this process
            is to output an image that correlates more strongly with a person’s
            subjective impression of a scene rather than the absolute birghtness
            of the scene. (Default: True).
        _metric_: Either an integer or the full name of a point-in-time metric to be
            computed by the recipe. (Default: luminance). Choose from the following:
                * 0 = illuminance
                * 1 = irradiance
                * 2 = luminance
                * 3 = radiance
        _resolution_: An integer for the maximum dimension of each image in pixels
            (either width or height depending on the input view angle and
            type). (Default: 800).
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -aa 0.25 -ad 512 -ar 16).
        _run: Set to "True" to run Radiance and get an image of the scene.

    Returns:
        report: Reports, errors, warnings, etc.
        hdr: A High Dynamic Range (HDR) image of the scene. This can be plugged into
            the Ladybug "Image Viewer" component to preview the image. It 
            can also be plugged into the "HB False Color" component to convert 
            the image into a false color version. Lastly, it can be connected to 
            the "HB HDR to GIF" component to get a GIF image that is more portable 
            and easily previewed by different software. Pixel values are in the
            standard SI units of the requested input metric.
                * illuminance = lux (aka. lm/m2)
                * irradiance = W/m2
                * luminance = cd/m2 (aka. lm/m2-sr)
                * radiance = W/m2-sr
"""

ghenv.Component.Name = 'HB Check Scene'
ghenv.Component.NickName = 'CheckScene'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

import os

try:  # import honeybee_radiance dependencies
    from ladybug.futil import write_to_file_by_name
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import honeybee dependencies
    from honeybee.config import folders
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.oconv import Oconv
    from honeybee_radiance_command.rpict import Rpict
    from honeybee_radiance_command.rtrace import Rtrace
    from honeybee_radiance_command.rcalc import Rcalc
    from honeybee_radiance_command.pcond import Pcond
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance_command:\n\t{}'.format(e))

try:  # import honeybee_radiance dependencies
    from honeybee_radiance.config import folders as rad_folders
    from honeybee_radiance.view import View
    from honeybee_radiance.lightsource.sky.strutil import string_to_sky
    from honeybee_radiance.lightsource.sky import CertainIrradiance, ClimateBased
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.viewport import viewport_by_name, viewport_properties
    from ladybug_rhino.config import tolerance, angle_tolerance, units_system
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# check the Radiance date of the installed radiance
try:  # import lbt_recipes dependencies
    from lbt_recipes.version import check_radiance_date
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))
check_radiance_date()

# dictionary of supported metrics
metric_dict = {
    '0': 'illuminance',
    '1': 'irradiance',
    '2': 'luminance',
    '3': 'radiance',
    'illuminance': 'illuminance',
    'irradiance': 'irradiance',
    'luminance': 'luminance',
    'radiance': 'radiance'
}


if all_required_inputs(ghenv.Component) and _run:
    # set defaults for resolution, metric and view
    _resolution_ = 800 if _resolution_ is None else _resolution_
    try:
        _metric_ = metric_dict[_metric_.lower()] if _metric_ is not None else 'luminance'
    except KeyError:
        raise ValueError('Metric "{}" is not supported.'.format(_metric_))
    if _view_ is None:
        viewp = viewport_by_name(None)
        v_props = viewport_properties(viewp, 0)
        VIEW_TYPES = ('v', 'h', 'l', 'c', 'a')
        _view_ = View(
            'current_viewport', v_props['position'], v_props['direction'],
            v_props['up_vector'], VIEW_TYPES[v_props['view_type']],
            v_props['h_angle'], v_props['v_angle'])
    else:
        assert isinstance(_view_, View), 'Expected Radiance View. Got {}.'.format(type(_view_))

    # process the sky input
    if _sky_ is None:
        _sky_ = CertainIrradiance.from_illuminance(10000)
    elif isinstance(_sky_, str):  # convert the sky string into a sky object
        _sky_ = string_to_sky(_sky_)
    to_rad_int = 1 if _metric_ in ('irradiance', 'radiance') else 0
    sky_content = _sky_.to_radiance(1) if isinstance(_sky_, ClimateBased) else _sky_.to_radiance()

    # process the _hb_objs into a Model and then a Radiance string
    models = [obj for obj in _hb_objs if isinstance(obj, Model)]
    other_objs = [obj for obj in _hb_objs if not isinstance(obj, Model)]
    model = Model.from_objects('scene', other_objs, units_system(), tolerance, angle_tolerance)
    for m in models:
        model.add_model(m)
    model_content, modifier_content = model.to.rad(model, minimal=True)

    # set up the paths for the various files used in translation
    scene_dir = os.path.join(folders.default_simulation_folder, 'scene_visualiztion')
    sky_file, scene_file, mat_file, view_file = \
        'weather.sky', 'scene.rad', 'scene.mat', 'view.vf'
    write_to_file_by_name(scene_dir, sky_file, sky_content, mkdir=True)
    write_to_file_by_name(scene_dir, scene_file, model_content)
    write_to_file_by_name(scene_dir, mat_file, modifier_content)
    _view_.to_file(scene_dir, view_file)
    scene_oct, final_hdr = 'scene_visual.oct', 'scene.HDR'
    hdr = os.path.join(scene_dir, final_hdr)
    if os.path.isfile(hdr):
        os.remove(hdr)

    # build up the commands to render the image of the sky
    oconv = Oconv(inputs=[sky_file, mat_file, scene_file], output=scene_oct)
    oconv.options.f = True

    rpict = Rpict(octree=scene_oct, output=final_hdr, view=view_file)
    rpict.options.ab = 2
    rpict.options.aa = 0.25
    rpict.options.ad = 512
    rpict.options.ar = 16
    if radiance_par_:
        rpict.options.update_from_string(radiance_par_.strip())
    if _metric_ in ('illuminance', 'irradiance'):
        rpict.options.i = True
    else:
        rpict.options.i = False
    rpict.options.x = _resolution_
    rpict.options.y = _resolution_

    commands = [oconv, rpict]
    if adj_expos_ or adj_expos_ is None:
        adj_image = final_hdr.lower().replace('.hdr', '_h.HDR')
        pcond = Pcond(input=final_hdr, output=adj_image)
        pcond.options.h = True
        commands.append(pcond)
        hdr = os.path.join(scene_dir, adj_image)
        if os.path.isfile(hdr):
            os.remove(hdr)

    # run the commands in series and load the global horizontal irradiance
    env = None
    if rad_folders.env != {}:
        env = rad_folders.env
    env = dict(os.environ, **env) if env else None
    for r_cmd in commands:
        r_cmd.run(env, cwd=scene_dir)
