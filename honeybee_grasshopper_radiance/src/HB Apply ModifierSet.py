# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply ModifierSet to Honeybee Rooms.
-

    Args:
        _rooms: Honeybee Rooms to which the input _mod_set should be assigned.
        _mod_set: A Honeybee ModifierSet to be applied to the input _room.
            This can also be text for a modifier set to be looked up in the
            modifier set library.
    
    Returns:
        rooms: The input Rooms with their modifier sets edited.
"""

ghenv.Component.Name = 'HB Apply ModifierSet'
ghenv.Component.NickName = 'ApplyModSet'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '6'


try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [obj.duplicate() for obj in _rooms]

    # process the input modifier set if it's a string
    if isinstance(_mod_set, str):
        _mod_set = modifier_set_by_identifier(_mod_set)

    # assign the modifier set
    for rm in rooms:
        rm.properties.radiance.modifier_set = _mod_set
