# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a High Dynamic Range (HDR) image file into a falsecolor version of itself.
-

    Args:
        _hdr: Path to a High Dynamic Range (HDR) image file.
        max_: A number to set the upper boundary of the legend. The default is
            dictated based on the legend_unit_.
        seg_count_: An interger representing the number of steps between the
            high and low boundary of the legend. The default is set to 10
            and any custom values input in here should always be greater
            than or equal to 2.
        legend_height_: An integer for the height of the legend in pixels. Set to 0
            to completely remove the legend from the output. (Default: 200).
        legend_width_: An integer for the width of the legend in pixels. Set to 0
            to completely remove the legend from the output. (Default: 100).
        legend_unit_: Text for the unit of the legend. If unspecified, an attempt will
            be made to sense the metric from the input image file. Typical examples
            include lux, W/m2, cd/m2, w/sr-m2.
        conversion_: Number for the conversion factor (aka. multiplier) for the results.
            The default is either 1 or 179 depending on whether the image is for
            radiance or irradiance to luminance or illuminance, respectively.
        contour_lines_: Set to True ro render the image with colored contour lines.
        extrema_: Set to True to cause extrema points to be printed on the brightest
            and darkest pixels of the input picture.
        mask_: A boolen to note whether pixels with a value of zero should be masked in
            black. (Default: False).
        color_palette_: Optional interger or text to change the color palette.
            Choose from the following.
                * 0 = def - default colors
                * 1 = pm3d -  a variation of the default colors
                * 2 = spec - the old spectral mapping
                * 3 = hot - a thermal scale

    Returns:
        hdr: Path to the resulting falsecolor HDR file. This can be plugged into the
            Ladybug "Image Viewer" component to preview the image. It can also
            be plugged into the "HB HDR to GIF" component to get a GIF image
            that is more portable and easily previewed by different software.
"""

ghenv.Component.Name = 'HB False Color'
ghenv.Component.NickName = 'FalseColor'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os
import subprocess
import re

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.falsecolor import Falsecolor
    from honeybee_radiance_command.pcomb import Pcomb
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance_command:\n\t{}'.format(e))

try:  # import honeybee_radiance dependencies
    from honeybee_radiance.config import folders as rad_folders
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


def sense_metric_from_hdr(hdr_path):
    """Sense the metric/units of a given HDR file from its properties.

    Args:
        hdr_path: The path to an HDR image file

    Returns:
        Text for the units of the file (either 'lux', 'W/m2', 'cd/m2', 'W/sr-m2')
    """
    with open(hdr_path, 'r') as hdr_file:
        for lineCount, line in enumerate(hdr_file):
            if lineCount < 10:
                low_line = line.strip().lower()
                if low_line.startswith('oconv') and low_line.endswith('.sky'):
                    return 'W/sr-m2'  # this is an image of a sky
                if low_line.startswith('rpict'):
                    if line.find('_irradiance.vf') > -1:
                        return 'W/m2'
                    if line.find('_radiance.vf') > -1:
                        return 'W/sr-m2'
                    if line.find('-i') > -1 and not line.find('-i-') > -1:
                        return 'lux'
            else:  # we have passed the header of the file
                return 'cd/m2'  # luminance


def is_fisheye(hdr_path):
    """Sense whether a given HDR file is a fisheye.

    Args:
        hdr_path: The path to an HDR image file

    Returns:
        Text for the units of the file (either 'lux', 'W/m2', 'cd/m2', 'W/sr-m2')
    """
    with open(hdr_path, 'r') as hdr_file:
        for lineCount, line in enumerate(hdr_file):
            if lineCount < 10:
                if '-vth' in line:
                    return True
            else:
                return False

def get_dimensions(img_dim):
    """Get integers for the dimensions of an image from the pcomb stdout.

    Args:
        img_dim: Text string that is returned from the pcomb function

    Returns:
        Two integers for the dimensions of the HDR image
    """
    dimensions = []
    for d in ['+X', '-Y']:
        regex = r'\%s\s+(\d+)' % d
        matches = re.finditer(regex, img_dim, re.MULTILINE)
        dim = next(matches).groups()[0]
        dimensions.append(int(dim))
    return dimensions


if all_required_inputs(ghenv.Component):
    # set up the paths for the various files used in translation
    img_dir = os.path.dirname(_hdr)
    input_image = os.path.basename(_hdr)
    new_image = input_image.lower().replace('.hdr', '_falsecolor.HDR')
    hdr = os.path.join(img_dir, new_image)

    # set default properties
    seg_count_ = seg_count_ if seg_count_ is not None else 10
    if legend_unit_ is None:
        legend_unit_ = sense_metric_from_hdr(_hdr)
    if conversion_ is None:
        if legend_unit_ in ('W/sr-m2', 'W/m2'):
            conversion_ = 1
        else:
            conversion_ = 179
    if max_ is None:  # get the max value by running pextrem
        pextrem_exe = os.path.join(rad_folders.radbin_path, 'pextrem.exe') if \
            os.name == 'nt' else os.path.join(rad_folders.radbin_path, 'pextrem')
        use_shell = True if os.name == 'nt' else False
        cmds = [pextrem_exe, '-o', _hdr]
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
        stdout = process.communicate()
        max_rgb = stdout[0].split('\n')[1]
        max_ = (sum([float(x) for x in max_rgb.split(' ')[2:]]) / 3) * conversion_
        if legend_unit_ == 'W/sr-m2' and max_ > 200:  # sun pixel overpowering image
            max_ = max_ / 50000
        max_ = str(round(max_, 1)) if max_ >= 0.1 else str(max_)

    # create the command to run falsecolor
    mask = True if mask_ and is_fisheye(_hdr) else False
    out_img = new_image if not mask else input_image.lower().replace('.hdr', '_fc_temp.HDR')
    falsecolor = Falsecolor(input=input_image, output=out_img)
    falsecolor.options.s = max_
    falsecolor.options.n = seg_count_
    falsecolor.options.l = legend_unit_
    falsecolor.options.m = conversion_
    if contour_lines_:
        falsecolor.options.cl = True
        falsecolor.options.p = input_image
    if extrema_:
        falsecolor.options.e = True
    if legend_height_ is not None:
        falsecolor.options.lh = legend_height_
    if legend_width_ is not None:
        falsecolor.options.lw = legend_width_
    if color_palette_:
        PALETTE_DICT = {
            '0': 'def',
            '1': 'pm3d',
            '2': 'spec',
            '3': 'hot',
            'def': 'def',
            'pm3d': 'pm3d',
            'spec': 'spec',
            'hot': 'hot'
        }
        falsecolor.options.pal = PALETTE_DICT[color_palette_]

    # run the falsecolor command
    env = None
    if rad_folders.env != {}:
        env = rad_folders.env
    env = dict(os.environ, **env) if env else None
    falsecolor.run(env, cwd=img_dir)

    # if we should maske, then run an additional pcomb command
    if mask:
        # get the dimensions of the image
        getinfo_exe = os.path.join(rad_folders.radbin_path, 'getinfo.exe') if \
            os.name == 'nt' else os.path.join(rad_folders.radbin_path, 'getinfo')
        cmds = [getinfo_exe, '-d', _hdr]
        use_shell = True if os.name == 'nt' else False
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
        stdout = process.communicate()
        img_dim = stdout[0]
        x, y = get_dimensions(img_dim)

        # mask the image
        xw = legend_width_ if legend_width_ is not None else 100
        lh = int(legend_height_ * 1.17) if legend_height_ is not None else (200 * 1.17)
        yw = lh - y if lh - y > 0 else 0
        expression = 's(x):x*x;' \
            'm=if((xmax-{0})*(ymax-{1})/4-s(x-{0}-(xmax-{0})/2)-s(y-(ymax-{1})/2),1,if({0}-x,1,0));' \
            'ro=m*ri(1);' \
            'go=m*gi(1);' \
            'bo=m*bi(1)'.format(xw, yw)
        pcomb = Pcomb(input=out_img, output=new_image)
        pcomb.options.e = expression
        pcomb.run(env, cwd=img_dir)
