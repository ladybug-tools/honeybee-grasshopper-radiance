# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Write a Honeybee Model to a Radiance Model Folder.
_
This Radiance Model Folder is what is used to run various types of Radiance
studies off of a consistent set of geometry and modifiers.

-

    Args:
        _model: A honeybee model object possessing all geometry, radiance modifiers
            and simulation assets like Sensor Grids and Views.
        minimal_: Boolean to note whether the radiance strings should be written in a minimal
            format (with spaces instead of line breaks). (Default: False).
        _folder_: Path to a folder to into which the Model Radiance Folder will be
            written. If unspecified, it will be written to a sub-folder
            within the default simulation folder.
        _write: Set to True to write the Model to a Radiance folder.

    Returns:
        report: Reports, errors, warnings, etc.
        folder: Path to the folder in which all of the files have been written.
"""

ghenv.Component.Name = 'HB Model to Rad Folder'
ghenv.Component.NickName = 'ModelToRad'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import re

try:
    from ladybug.futil import write_to_file_by_name, nukedir, preparedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance_folder.folder import ModelFolder
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance_folder:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _write:
    # process the simulation folder name and the directory
    clean_name = re.sub(r'[^.A-Za-z0-9_-]', '_', _model.display_name)
    folder = os.path.join(folders.default_simulation_folder, clean_name, 'radiance') \
        if _folder_ is None else _folder_
    if os.path.isdir(folder):
        nukedir(folder, rmdir=True)  # delete the folder if it already exists
    else:
        preparedir(folder)  # create the directory if it's not there

    # write the model folder
    _model.to.rad_folder(_model, folder, minimal=bool(minimal_))
