# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Adjust and format a High Dynamic Range (HDR) image file.
_
Possible adjustments include chaging the exposure of the image to mimic what would
be seen by a human eye and adding an optional text label to the image.
-

    Args:
        _hdr: Path to a High Dynamic Range (HDR) image file.
        adj_expos_: Boolean to note whether the exposure of the image should be adjusted to
            mimic the human visual response in the output. The goal of this process
            is to output an image that correlates more strongly with a person’s
            subjective impression of a scene rather than the absolute birghtness
            of the scene. (Default: False).
        label_: Optional text label to be appended to the bottom of the image. This
            is useful when one has several images and would like to easily
            identify them while scrolling through them.
        label_hgt_: An integer for the height of the label text in pixels. (Default: 32).

    Returns:
        hdr: Path to the resulting adjusted HDR image file.
"""

ghenv.Component.Name = 'HB Adjust HDR'
ghenv.Component.NickName = 'AdjustHDR'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.pcond import Pcond
    from honeybee_radiance_command.psign import Psign
    from honeybee_radiance_command.pcompos import Pcompos
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


if all_required_inputs(ghenv.Component):
    # set up the paths for the various files used in translation
    img_dir = os.path.dirname(_hdr)
    input_image = os.path.basename(_hdr)
    hdr = _hdr
    commands = []

    # add the command to adjust the exposure to reflect human vision (if requested)
    if adj_expos_:
        adj_image = input_image.lower().replace('.hdr', '_h.HDR')
        pcond = Pcond(input=input_image, output=adj_image)
        pcond.options.h = True
        commands.append(pcond)
        hdr = os.path.join(img_dir, adj_image)
        input_image = adj_image

    # add the command to for a text label (if requested)
    if label_:
        label_images = []
        for i, l_tex in enumerate(reversed(label_.split('\n'))):
            label_image = 'label{}.HDR'.format(i)
            psign = Psign(text=l_tex, output=label_image)
            psign.options.cb = (0, 0, 0)
            psign.options.cf = (1, 1, 1)
            psign.options.h = label_hgt_ if label_hgt_ is not None else 32
            commands.append(psign)
            label_images.append(label_image)

        lbl_image = input_image.lower().replace('.hdr', '_label.HDR')
        pcompos = Pcompos(input=label_images + [input_image], output=lbl_image)
        pcompos.options.a = 1
        commands.append(pcompos)
        hdr = os.path.join(img_dir, lbl_image)
        input_image = lbl_image

    # run the commands in series and load the global horizontal irradiance
    env = None
    if rad_folders.env != {}:
        env = rad_folders.env
    env = dict(os.environ, **env) if env else None
    for r_cmd in commands:
        r_cmd.run(env, cwd=img_dir)
