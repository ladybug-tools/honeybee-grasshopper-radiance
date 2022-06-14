# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Perform glare post-processing on a hemisphical fisheye HDR image file.
_
Glare post-processing includes calcuating Daylight Glare Probability (DGP) as
well as other glare indexes (DGI, UGR, VCP, CGI, UDP).
_
This component is using the `evalglare` function for glare calculations., which
is developed by J. Wienold at Fraunhofer ISE. More information on evalglare
can be found here:
https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/evalglare.pdf/view
_
For more information about the metrics used to evaluate glare, see here:
http://web.mit.edu/tito_/www/Projects/Glare/GlareRecommendationsForPractice.html

-
    Args:
        _hdr: Path to a hemisphical fisheye High Dynamic Range (HDR) image file. This can be
            obtained from the "HB Point-In-Time View-Based" recipe component. Due
            to runtime reasons of the evalglare code, the input HDR image should
            be smaller than 1500 x 1500 pixels. The recommended size is 1000 x 1000
            pixels, the minimum recommended size is 800 x 800 pixels.
        task_pos_: An optional task position as a 2D point or string formatted as "X, Y".
            The X and Y coordinates of this point must be numbers between 0 and 1
            and correspond to fraction of the image width and height where the
            task position lies. If no task position is provided, the glare will
            be valuated for the entire scene of the image.
        task_angle_: An number between 0 and 180 for the task position opening angle
            in degrees. This angle indicates how widely the peripheral vision
            is engaged for the task. (Default: 30).
        hide_task_: Boolean to note whether the task area should be hidden in the
            output check_hdr.

    Returns:
        DGP: Daylight Glare Probability (DGP) as a number between 0 and 1. The DGP
            describes the fraction of persons disturbed by glare, where 0 is no
            one disturbed and 1 is everyone. Values lower than 0.2 are out of the
            range of the user assessment tests, where the program is based on and
            should be interpreted carefully.
        category: Text for the category of glare discomfort. It will be one of the
            following.
                * Imperceptible Glare [0.35 > DGP]
                * Perceptible Glare [0.4 > DGP >= 0.35]
                * Disturbing Glare [0.45 > DGP >= 0.4]
                * Intolerable Glare [DGP >= 0.45] 
        glare_indices: A list of various glare indices ordered as follows.
                * Daylight Glare Index (DGI)
                * Unified Glare Rating (UGR)
                * Visual Comfort Probability (VCP)
                * CIE Glare Index (CGI)
                * Veiling Luminance (Lveil)
        check_hdr: Path to a HDR image produced from the glare study. The image will
            use randomly-assigned colors to indicate different sources of glare
            in the image. It will also show a circular region for the task area
            unless hide_task_ has been set to True.
"""

ghenv.Component.Name = 'HB Glare Postprocess'
ghenv.Component.NickName = 'Glare'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os
import subprocess
import math
import re

try:  # import honeybee_radiance dependencies
    from honeybee_radiance.config import folders as rad_folders
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


def check_hdr_luminance_and_fisheye(hdr_path):
    """Check that a given HDR file is a fisheye image for visible luminance.

    A ValueError is raised if the image is not for luminance or if the image is
    not clearly a hemispheical fisheye.

    Args:
        hdr_path: The path to an HDR image file.
    """
    msg = 'Connected _hdr image must be for luminance. Got "{}".'
    projection = '-vth'
    with open(hdr_path, 'r') as hdr_file:
        for lineCount, line in enumerate(hdr_file):
            if lineCount < 200:
                low_line = line.strip().lower()
                if low_line.startswith('rpict'):
                    if line.find('_irradiance.vf') > -1:
                        raise ValueError(msg.format('irradiance'))
                    if line.find('_radiance.vf') > -1:
                        raise ValueError(msg.format('radiance'))
                    if line.find('-i') > -1 and not line.find('-i-') > -1:
                        raise ValueError(msg.format('illuminance'))
                elif low_line.startswith('view='):
                    if line.find('-vth') > -1:
                        projection = '-vth'
                    elif line.find('-vta') > -1:
                        projection = '-vta'
                    else:
                        raise ValueError(
                            'Connected _hdr image is not a fisheye projection.\n'
                            'Make sure the view type of the image is 1(h) or 4(a).')
                elif 'pcond -h' in low_line:
                    raise ValueError(
                        'Connected _hdr image has had the exposure adjusted on it.\n'
                        'Make sure adj_expos_ has been set to False in previous steps.')
            else:  # no need to check the rest of the document
                break
    return projection

def check_hdr_dimensions(hdr_path):
    """Check that a given HDR file has dimensions suitable for evalglare.

    A warning is raised if the image is not 1000x1000 pixels and a ValueError is
    raised if the image is completely outside the accptable ragne from 800x800
    to 1500x1500 pixels.

    Args:
        hdr_path: The path to an HDR image file.
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

    def get_dimensions(img_dim):
        dimensions = []
        for d in ['+X', '-Y']:
            regex = r'\%s\s+(\d+)' % d
            matches = re.finditer(regex, img_dim, re.MULTILINE)
            dim = next(matches).groups()[0]
            dimensions.append(int(dim))
        return dimensions
    # check the X and Y dimensions of the image
    x, y = get_dimensions(img_dim)

    msg = 'Recommended _hdr image dimensions for glare analysis should be \n' \
        '{} {} x {} pixels. Got {} x {}.'
    if x < 800 or y < 800:
        give_warning(ghenv.Component, msg.format('at least', 800, 800, x, y))
    elif x > 1500 or y > 1500:
        give_warning(ghenv.Component, msg.format('no greater than', 1500, 1500, x, y))
    return x, y


def dgp_comfort_category(dgp):
    """Get text for the glare comfort category given a DGP value."""
    if dgp < 0.35:
        return 'Imperceptible Glare'
    elif dgp < 0.40:
        return 'Perceptible Glare'
    elif dgp < 0.45:
        return 'Disturbing Glare'
    else:
        return 'Intolerable Glare'


if all_required_inputs(ghenv.Component):
    # check the input image to ensure it meets the criteria
    projection = check_hdr_luminance_and_fisheye(_hdr)
    width, height = check_hdr_dimensions(_hdr)

    # get the path the the evalglare command and setup the check image argument
    evalglare_exe = os.path.join(rad_folders.radbin_path, 'evalglare.exe') if \
        os.name == 'nt' else os.path.join(rad_folders.radbin_path, 'evalglare')
    img_dir = os.path.dirname(_hdr)
    input_image = os.path.basename(_hdr)
    new_image = input_image.lower().replace('.hdr', '_check.HDR')
    check_hdr = os.path.join(img_dir, new_image)
    cmds = [evalglare_exe, '-c', check_hdr]

    # since pcomp is used to merge images, the input usually doesn't have view information
    # add default view information for hemispheical fish-eye camera
    cmds.extend([projection, '-vv', '180', '-vh', '180'])

    # process the task position and add the input HDR
    if task_pos_:
        uv_pt = [float(val) for val in task_pos_.split(',')]
        assert 0 <= uv_pt[0] <= 1 and 0 <= uv_pt[1] <= 1, 'Task position X and Y ' \
            'coordinates must be between 0 and 1.'
        angle = math.radians(task_angle_) if task_angle_ is not None else math.radians(30)
        task_opt = '-t' if hide_task_ else '-T'
        cmds.extend(
            [task_opt, str(int(uv_pt[0] * width)), str(int(uv_pt[1] * height)), str(angle)])
    cmds.append(_hdr)

    # run the evalglare command in a manner that lets us obtain the stdout result
    use_shell = True if os.name == 'nt' else False
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
    stdout = process.communicate()

    # process the stdout result into the component outputs
    glare_result = stdout[0].split(':')[-1].strip()
    glare_indices = [float(val) for val in glare_result.split(' ')]
    DGP = glare_indices.pop(0)
    category = dgp_comfort_category(DGP)
