# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Interpolate or extrapolate a High Dynamic Range (HDR) image file from another
HDR image file.
_
Recommended use is to extract 180 FOV (-vh 180 -vv 180) angular or hemispherical
HDR images from a 360 FOV (-vh 360 -vv 360) angular HDR image. Alternatively,
conversions between 180 FOV angular and hemispherical HDR images can be made.
-

    Args:
        _view: A view to interpolate or extrapolate into a new HDR. The "HB View" 
            component can be used to create an input view and it must
            have the same position as that use to make the _hdr.
        _hdr: Path to a High Dynamic Range (HDR) image file from which to
            interpolate or extrapolate.
        _resolution_: An integer for the dimension of the output image in pixels.
            If extracting a 180 FOV angular or hemispherical HDR image from a
            360 FOV HDR image, the default resolution is 1/3 of the resolution of
            _hdr. If converting between 180 FOV angular or hemispherical HDR 
            images, the default resolution is that of _hdr.

    Returns:
        hdr: Path to the resulting HDR image file.
"""

ghenv.Component.Name = 'HB Extract HDR'
ghenv.Component.NickName = 'ExtractHDR'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import subprocess

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.pinterp import Pinterp
    from honeybee_radiance_command.ra_xyze import Ra_xyze
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance_command:\n\t{}'.format(e))

try:  # import honeybee_radiance dependencies
    from honeybee_radiance.config import folders as rad_folders
    from honeybee_radiance.view import View
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# check the Radiance date of the installed radiance
try:  # import lbt_recipes dependencies
    from lbt_recipes.version import check_radiance_date
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))
check_radiance_date()


def check_view_hdr(hdr_path):
    """Check if the header of the HDR image contains a view (VIEW=).
    
    A ValueError is raised if the image does not contain a valid view.
    A ValueError is raised if the view type is not -vta or -vth.
    
    Args:
        hdr_path: The path to an HDR image file.
    """
    # set hdr_view to None
    hdr_view = None
    
    # read hdr image and search for a valid view
    with open(hdr_path, 'r') as hdr_file:
        for lineCount, line in enumerate(hdr_file):
            if lineCount < 200:
                low_line = line.lower()
                if not low_line.startswith('\t'):
                    if low_line.startswith('view='):
                        hdr_view = View.from_string('hdr_view', line)
            else:  # no need to check the rest of the document
                break
    if not hdr_view:
        raise ValueError(
            'Connected _hdr image does not contain a valid view in the header.\n'
            'Note that indented views in the header will be ignored by pinterp.')
    if not hdr_view.type in ('a', 'h'):
        msg = 'Expected view type -vta or -vth in _hdr. Got view type -vt{}.'
        raise ValueError(msg.format(hdr_view.type))
    return hdr_view


def check_view_points(view, hdr_view):
    """Check if view points of output view and input HDR are matching.
    
    A ValueError is raised if the view points are not matching.
    
    Args:
        view: A Honeybee Radiance View to extract.
        hdr_view: A Honeybee Radiance View from the input HDR.
    """
    if not view.position == hdr_view.position:
        msg = 'View points of _view and _hdr are not matching.\n' \
        'Got _view = {} and _hdr = {}.'
        raise ValueError(msg.format(view.position, hdr_view.position))


def check_resolution(hdr_path, resolution, view, hdr_view):
    """Check the resolution of the output HDR as well as the input HDR.
    
    A warning is raised if the HDR image dimensions are not square. A warning is
    raised if the resolution is larger than one third of the HDR image
    resolution if converting a 360 FOV HDR to 180 FOV HDR. A warning is raised 
    if the output resolution is larger than the input resolution.
    
    Args:
        hdr_path: The path to an HDR image file.
        resolution: The resolution of the extracted view from hdr_path.
        view: A Honeybee Radiance View to extract.
        hdr_view: A Honeybee Radiance View from the input HDR.
    """
    # get the path the the getinfo command
    getinfo_exe = os.path.join(rad_folders.radbin_path, 'getinfo.exe') if \
        os.name == 'nt' else os.path.join(rad_folders.radbin_path, 'getinfo')
    
    # run the getinfo command in a manner that lets us obtain the result
    cmds = [getinfo_exe, '-d', hdr_path]
    use_shell = True if os.name == 'nt' else False
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
    stdout = process.communicate()
    img_dim = stdout[0]
    
    # check the X and Y dimensions of the image
    hdr_x = int(img_dim.split(' ')[-1].strip())
    hdr_y = int(img_dim.split(' ')[-3].strip())
    if hdr_x == hdr_y: 
        hdr_resolution = hdr_x = hdr_y
    else:
        msg = 'It is recommended that image dimensions of _hdr are square.\n' \
            'Got {} x {}.'
        give_warning(ghenv.Component, msg.format(hdr_x, hdr_y))
    
    # check resolution ratio of output image / input image
    if hdr_view.h_size == 360 and hdr_view.v_size == 360:
        if resolution is None: 
            resolution = hdr_resolution / 3
        if resolution > hdr_resolution / 3:
            msg = 'Recommended _resolution_ is one third or less of the _hdr resolution. \n' \
                'Got {} for _resolution_ and {} for _hdr. Recommended _resolution_ \n' \
                'is {} or lower.'
            give_warning(ghenv.Component, msg.format(resolution, hdr_resolution, 
                         int(hdr_resolution / 3)))
    else:
        if resolution is None: 
            resolution = hdr_resolution
        if resolution > hdr_resolution:
            msg = 'Output image resolution ({}) is larger than input image \n' \
                'resolution ({}). It is recommended that _resolution_ is equal \n' \
                'to or less than input image resolution.'
            give_warning(ghenv.Component, msg.format(resolution, hdr_resolution))
    return resolution


if all_required_inputs(ghenv.Component):
    # check if _view is Honeybee Radiance View
    assert isinstance(_view, View), \
        'Expected Honeybee Radiance View in _view. Got {}.'.format(type(_view))
    
    # check if header contains a view
    hdr_view = check_view_hdr(_hdr)
    
    # check view points
    check_view_points(_view, hdr_view)
    
    # check resolution
    resolution = check_resolution(_hdr, _resolution_, _view, hdr_view)
    
    # set up the paths for the various files used in translation
    img_dir = os.path.dirname(_hdr)
    input_image = os.path.basename(_hdr)
    commands = []
    
    # add the command to include exposure in the pixels
    expos_image = input_image.lower().replace('.hdr', '_e.hdr')
    ra_xyze = Ra_xyze(input=input_image, output=expos_image)
    ra_xyze.options.r = True
    ra_xyze.options.o = True
    commands.append(ra_xyze)
    
    # add the command to extract a view (HDR)
    view_identifier = _view.identifier
    view = os.path.basename(_view.to_file(img_dir))
    pinterp_image = input_image.lower().replace('.hdr', '_{}.hdr'.format(view_identifier))
    pinterp = Pinterp(output=pinterp_image, view=view, image=expos_image,
                      zspec=1)
    pinterp.options.x = resolution
    pinterp.options.y = resolution
    commands.append(pinterp)
    hdr = os.path.join(img_dir, pinterp_image)
    
    # run the commands in series
    env = None
    if rad_folders.env != {}:
        env = rad_folders.env
    env = dict(os.environ, **env) if env else None
    for r_cmd in commands:
        r_cmd.run(env, cwd=img_dir)
