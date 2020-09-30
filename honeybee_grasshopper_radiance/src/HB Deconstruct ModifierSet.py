# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Deconstruct a modifier set into its constituient exterior modifiers.
-

    Args:
        _mod_set: A modifier set to be deconstructed. This can also be
            text for a modifier set to be looked up in the modifier
            set library.

    Returns:
        exterior_wall: A modifier object for the set's exterior walls.
        exterior_roof: A modifier object for the set's exterior roofs.
        exposed_floor: A modifier object for the set's exposed floors.
        ground_wall: A modifier object for the set's underground walls.
        ground_roof: A modifier object for the set's underground roofs.
        ground_floor: A modifier object for the set's ground-contact floors.
        window: A modifier object for apertures with an Outdoors boundary
            condition and a Wall face type for their parent face.
        skylight: A modifier object for apertures with an Outdoors boundary
            condition and a RoofCeiling or Floor face type for their parent face.
        operable: A modifier object for apertures with an Outdoors boundary
            condition and True is_operable property.
        exterior_door: A modifier object for opaque doors with an Outdoors
            boundary condition and a Wall face type for their parent face.
        overhead_door: A modifier object for opaque doors with an Outdoors
            boundary condition and a RoofCeiling or Floor face type for their
            parent face.
        glass_door: A modifier object for all glass doors with an Outdoors
            boundary condition.
        exterior_shade: A modifier object for all exterior shades.
"""

ghenv.Component.Name = 'HB Deconstruct ModifierSet'
ghenv.Component.NickName = 'DecnstrModSet'
ghenv.Component.Message = '1.0.0'
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

    exterior_wall = _mod_set.wall_set.exterior_modifier
    exterior_roof = _mod_set.roof_ceiling_set.exterior_modifier
    exposed_floor = _mod_set.floor_set.exterior_modifier
    window = _mod_set.aperture_set.window_modifier
    skylight = _mod_set.aperture_set.skylight_modifier
    operable = _mod_set.aperture_set.operable_modifier
    exterior_door = _mod_set.door_set.exterior_modifier
    overhead_door = _mod_set.door_set.overhead_modifier
    glass_door = _mod_set.door_set.exterior_glass_modifier
    exterior_shade = _mod_set.shade_set.exterior_modifier
