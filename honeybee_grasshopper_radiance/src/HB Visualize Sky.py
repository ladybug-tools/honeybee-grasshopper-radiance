# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize a sky as a High Dynamic Range (HDR) image file.
-

    Args:
        _sky: A Radiance sky from any of the sky components under the "Light Sources" tab.
            Text string representations of skies are also acceptable.
        _size_: A number for the X and Y dimension of the imgae in pixles. (Default: 500 px)

    Returns:
        hdr: Path to the High Dynamic Range (HDR) image file of the sky. This can be
            plugged into the Ladybug "Image Viewer" component to preview the image.
            It can also be plugged into the "HB False Color" component to convert
            the image into a false color version. Lastly, it can be connected to
            the "HB HDR to GIF" component to get a GIF image that is more portable
            and easily previewed by different software.
        ghi: The global horizontal irradiance (W/m2) for an upstructed test point under
            the sky.
"""

ghenv.Component.Name = 'HB Visualize Sky'
ghenv.Component.NickName = 'VizSky'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os

try:  # import honeybee_radiance dependencies
    from ladybug.futil import write_to_file_by_name
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import honeybee dependencies
    from honeybee.config import folders
    from honeybee.typing import clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.oconv import Oconv
    from honeybee_radiance_command.rpict import Rpict
    from honeybee_radiance_command.rtrace import Rtrace
    from honeybee_radiance_command.rcalc import Rcalc
    from honeybee_radiance_command.pcond import Pcond
    from honeybee_radiance_command.pflip import Pflip
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance_command:\n\t{}'.format(e))

try:  # import honeybee_radiance dependencies
    from honeybee_radiance.config import folders as rad_folders
    from honeybee_radiance.lightsource.sky.strutil import string_to_sky
    from honeybee_radiance.lightsource.sky import ClimateBased
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# check the Radiance date of the installed radiance
try:  # import lbt_recipes dependencies
    from lbt_recipes.version import check_radiance_date
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))
check_radiance_date()


if all_required_inputs(ghenv.Component):
    # set defaults and process the sky input
    _size_ = 500 if _size_ is None else _size_
    if isinstance(_sky, str):  # convert the sky string into a sky object
        _sky = string_to_sky(_sky)
    sky_content = _sky.to_radiance(1) if isinstance(_sky, ClimateBased) else _sky.to_radiance()

    # set up the paths for the various files used in translation
    sky_dir = os.path.join(folders.default_simulation_folder, 'sky_visualiztion')
    sky_file, sky_oct = 'weather.sky', 'sky_visual.oct'
    write_to_file_by_name(sky_dir, sky_file, sky_content, mkdir=True)
    ghi_res, full_ghi_res = 'ghi.res', os.path.join(sky_dir, 'ghi.res')
    init_hdr, final_hdr = 'sky_init.HDR', '{}.HDR'.format(clean_rad_string(str(_sky)))
    hdr = os.path.join(sky_dir, final_hdr)
    if os.path.isfile(hdr):
        os.remove(hdr)

    # build up the commands to render the image of the sky
    oconv = Oconv(inputs=[sky_file], output=sky_oct)
    oconv.options.f = True

    rpict = Rpict(octree=sky_oct, output=init_hdr)
    rpict.options.i = True
    rpict.options.t = 10
    rpict.options.ab = 1
    rpict.options.ad = 1000
    rpict.options.as_ = 20
    rpict.options.ar = 300
    rpict.options.aa = 0.1
    rpict.options.x = _size_
    rpict.options.y = _size_
    rpict.options.vt = 'h'
    rpict.options.vp = (0, 0, 0)
    rpict.options.vd = (0, 0, 1)
    rpict.options.vu = (0, 1, 0)
    rpict.options.vh = 180
    rpict.options.vv = 180

    pflip = Pflip(input=init_hdr, output=final_hdr)
    pflip.options.h = True

    # add the command to get the horizontal irradiance of the sky
    grid = SensorGrid.from_position_and_direction('up_sensor', [(0, 0, 0)], [(0, 0, 1)])
    grid.to_file(sky_dir, 'up_sensor.pts')
    rtrace = Rtrace(octree=sky_oct, sensors='up_sensor.pts')
    rtrace.options.I = True
    rtrace.options.w = True
    rtrace.options.h = True
    rtrace.options.ab = 1
    rcalc = Rcalc(output=ghi_res)
    rcalc.options.e = '$1=(0.265*$1+0.67*$2+0.065*$3)'
    rtrace.pipe_to = rcalc

    # run the commands in series and load the global horizontal irradiance
    env = None
    if rad_folders.env != {}:
        env = rad_folders.env
    env = dict(os.environ, **env) if env else None
    for r_cmd in (oconv, rpict, pflip, rtrace):
        r_cmd.run(env, cwd=sky_dir)
    with open(full_ghi_res, 'r') as inf:
        ghi = inf.readlines()[0].strip()
