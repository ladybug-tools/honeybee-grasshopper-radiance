# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = "1 :: Modifiers"
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string
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
    # create the modifier
    modifier = Mirror(
        clean_and_id_rad_string(_name), _r_ref, _g_ref, _b_ref)
    modifier.display_name = _name
