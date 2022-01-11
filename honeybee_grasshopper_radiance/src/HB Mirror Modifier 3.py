# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an mirror radiance modifier from a single reflectance.
-

    Args:
        _name: Text to set the name for the modifier and to be incorporated into
            a unique modifier identifier.
        _r_ref: A number between 0 and 1 for the red reflectance.
        _g_ref: A number between 0 and 1 for the green reflectance.
        _b_ref: A number between 0 and 1 for the blue reflectance.
    
    Returns:
        modifier: An mirror modifier that can be assigned to a Honeybee geometry
            or Modifier Sets.
"""

ghenv.Component.Name = 'HB Mirror Modifier 3'
ghenv.Component.NickName = 'MirrorMod3'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = "1 :: Modifiers"
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_rad_string, clean_and_id_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.modifier.material import Mirror
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    name = clean_and_id_rad_string('MirrorMaterial') if _name_ is None else \
        clean_rad_string(_name_)

    # create the modifier
    modifier = Mirror(name, _r_ref, _g_ref, _b_ref)
    if _name_ is not None:
        modifier.display_name = _name_
