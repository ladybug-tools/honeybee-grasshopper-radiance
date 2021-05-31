# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a High Dynamic Range (HDR) image file into a Graphics Interchange Format
(GIF) image file.
_
GIF files are much smaller than HDRs, they are more portable, and they can be
previewed with many different types of software. However, they do not contain
all of the information that an HRD has.
-

    Args:
        _hdr: Path to a High Dynamic Range (HDR) image file.
        adj_expos_: Boolean to note whether the exposure of the image should be adjusted to
            mimic the human visual response in the output. The goal of this process
            is to output an image that correlates more strongly with a person’s
            subjective impression of a scene rather than the absolute birghtness
            of the scene. (Default: True).

    Returns:
        gif: Path to the resulting GIF file,
"""

ghenv.Component.Name = 'HB HDR to GIF'
ghenv.Component.NickName = 'HDR-GIF'
ghenv.Component.Message = '1.2.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.pcond import Pcond
    from honeybee_radiance_command.ra_gif import Ra_GIF
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
    new_image = input_image.lower().replace('.hdr', '.gif')
    gif = os.path.join(img_dir, new_image)

    # create the command to run the conversion to GIF
    if adj_expos_ or adj_expos_ is None:
        adj_image = input_image.lower().replace('.hdr', '_h.HDR')
        pcond = Pcond(input=input_image, output=adj_image)
        pcond.options.h = True
        ra_gif = Ra_GIF(input=adj_image, output=new_image)
        commands = (pcond, ra_gif)
    else:
        ra_gif = Ra_GIF(input=input_image, output=new_image)
        commands = (ra_gif,)

    # run the commands in series and load the global horizontal irradiance
    env = None
    if rad_folders.env != {}:
        env = rad_folders.env
    env = dict(os.environ, **env) if env else None
    for r_cmd in commands:
        r_cmd.run(env, cwd=img_dir)
