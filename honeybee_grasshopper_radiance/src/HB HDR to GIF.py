# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Convert a High Dynamic Range (HDR) image file into a Graphics Interchange Format
(GIF) image file.
_
GIF files are much smaller than HDRs, they are more portable, and they can be
previewed with many different types of software. However, they do not contain
all of the information that an HDR image has.
-

    Args:
        _hdr: Path to a High Dynamic Range (HDR) image file.

    Returns:
        gif: Path to the resulting GIF file,
"""

ghenv.Component.Name = 'HB HDR to GIF'
ghenv.Component.NickName = 'HDR-GIF'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os

try:  # import honeybee_radiance_command dependencies
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
    ra_gif = Ra_GIF(input=input_image, output=new_image)

    # run the command
    env = None
    if rad_folders.env != {}:
        env = rad_folders.env
    env = dict(os.environ, **env) if env else None
    ra_gif.run(env, cwd=img_dir)
