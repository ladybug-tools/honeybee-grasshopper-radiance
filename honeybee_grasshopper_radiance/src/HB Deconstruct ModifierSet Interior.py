# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Deconstruct a modifier set into its constituient interior modifiers.
-

    Args:
        _mod_set: A modifier set to be deconstructed. This can also be
            text for a modifier set to be looked up in the modifier
            set library.

    Returns:
        interior_wall: A modifier object for the set's interior walls.
        ceiling: A modifier object for the set's interior roofs.
        interior_floor: A modifier object for the set's interior floors.
        interior_window: A modifier object for all apertures with a Surface
            boundary condition.
        interior_door: A modifier object for all opaque doors with a Surface
            boundary condition.
        int_glass_door: A modifier object for all glass doors with a Surface
            boundary condition.
        interior_shade: A modifier object for all interior shades.
"""

ghenv.Component.Name = 'HB Deconstruct ModifierSet Interior'
ghenv.Component.NickName = 'DecnstrConstrSetInt'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '5'


try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.modifierset import ModifierSet
    from honeybee_radiance.lib.modifiersets import modifier_set_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the input
    if isinstance(_mod_set, str):
        _mod_set = modifier_set_by_identifier(_mod_set)
    else:
        assert isinstance(_mod_set, ModifierSet), \
            'Expected ModifierSet. Got {}.'.format(type(_mod_set))

    interior_wall = _mod_set.wall_set.interior_modifier
    ceiling = _mod_set.roof_ceiling_set.interior_modifier
    interior_floor = _mod_set.floor_set.interior_modifier
    interior_window = _mod_set.aperture_set.interior_modifier
    interior_door = _mod_set.door_set.interior_modifier
    int_glass_door = _mod_set.door_set.interior_glass_modifier
    interior_shade = _mod_set.shade_set.interior_modifier
