# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Write a Honeybee Model to a Radiance Model Folder.
_
This Radiance Model Folder is what is used to run various types of Radiance
studies off of a consistent set of geometry and modifiers.

-

    Args:
        _model: A honeybee model object possessing all geometry, radiance modifiers
            and simulation assets like Sensor Grids and Views.
        _folder_: An optional folder to into which the Model Radiance Folder
            will be written. NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE
            ANY SPACES OR UNDERSCORES IN THE FILE PATH.
        _write: Set to True to write the Model to a Radiance folder.

    Returns:
        report: Reports, errors, warnings, etc.
        folder: Path to the folder in which all of the files have been written.
"""

ghenv.Component.Name = 'HB Model to Rad Folder'
ghenv.Component.NickName = 'ModelToRad'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os

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
    _folder_ = folders.default_simulation_folder if _folder_ is None else _folder_
    folder = os.path.join(_folder_, _model.identifier, 'Radiance')
    if os.path.isdir(folder):
        nukedir(folder, rmdir=True)  # delete the folder if it already exists
    else:
        preparedir(folder)  # create the directory if it's not there

    # write the model folder
    _model.to.rad_folder(_model, folder)
