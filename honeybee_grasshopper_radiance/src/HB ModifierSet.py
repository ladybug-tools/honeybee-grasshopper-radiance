# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a ModifierSet object containing all radiance modifiers needed to create
an radiance model. ModifierSets can be assigned to Honeybee Rooms to specify
all default modifiers on the Room.
-

    Args:
        _name_: Text to set the name for the ModifierSet and to be incorporated
            into a unique ModifierSet identifier. If None, a random one will
            be genrated.
        base_mod_set_: An optional ModifierSet object that will be used
            as the starting point for the new ModifierSet output from this
            component. This can also be text for the name of a ModifierSet
            within the library such as that output from the "HB Search Modifier
            Sets" component. If None, the Honeybee "Generic Default Modifier
            Set" will be used as the base.
        _exterior_subset_: A modifier subset list from the "HB Exterior Modifier
            Subset" component. Note that None values in this list correspond to
            no change to the given modifier in the base_mod_set_.
        _interior_subset_: A modifier subset list from the "HB Interior Modifier
            Subset" component. Note that None values in this list correspond to
            no change to the given modifier in the base_mod_set_.
        _subface_subset_: A modifier subset list from the "HB Subface Subset"
            component. Note that None values in this list correspond to no
            change to the given modifier in the base_mod_set_.
        _shade_subset_: A modifier subset list from the "HB Shade Modifier
            Subset" component. Note that None values in this list correspond to
            no change to the given modifier in the base_mod_set_.

    Returns:
        mod_set: A ModifierSet object that can be assigned to Honeybee
            Rooms in order to specify all default modifiers on the Room.
"""

ghenv.Component.Name = 'HB ModifierSet'
ghenv.Component.NickName = 'ModifierSet'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

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
    # get the base modifier set
    name = clean_and_id_rad_string('ModifierSet') if _name_ is None else \
        clean_rad_string(_name_)
    if base_mod_set_ is None:
        mod_set = ModifierSet(name)
    else:
        if isinstance(base_mod_set_, str):
            base_mod_set_ = modifier_set_by_identifier(base_mod_set_)
        mod_set = base_mod_set_.duplicate()
        mod_set.identifier = name
        if _name_ is not None:
            mod_set.display_name = _name_

    # go through each input modifier subset and assign it to the set
    if len(_exterior_subset_) != 0:
        assert len(_exterior_subset_) == 3, 'Input _exterior_subset_ is not valid.'
        if _exterior_subset_[0] is not None:
            mod_set.wall_set.exterior_modifier = _exterior_subset_[0]
        if _exterior_subset_[1] is not None:
            mod_set.roof_ceiling_set.exterior_modifier = _exterior_subset_[1]
        if _exterior_subset_[2] is not None:
            mod_set.floor_set.exterior_modifier = _exterior_subset_[2]

    if len(_interior_subset_) != 0:
        assert len(_interior_subset_) == 6, 'Input _interior_subset_ is not valid.'
        if _interior_subset_[0] is not None:
            mod_set.wall_set.interior_modifier = _interior_subset_[0]
        if _interior_subset_[1] is not None:
            mod_set.roof_ceiling_set.interior_modifier = _interior_subset_[1]
        if _interior_subset_[2] is not None:
            mod_set.floor_set.interior_modifier = _interior_subset_[2]
        if _interior_subset_[3] is not None:
            mod_set.aperture_set.interior_modifier = _interior_subset_[3]
        if _interior_subset_[4] is not None:
            mod_set.door_set.interior_modifier = _interior_subset_[4]
        if _interior_subset_[5] is not None:
            mod_set.door_set.interior_glass_modifier = _interior_subset_[5]

    if len(_subface_subset_) != 0:
        assert len(_subface_subset_) == 6, 'Input _subface_subset_ is not valid.'
        if _subface_subset_[0] is not None:
            mod_set.aperture_set.window_modifier = _subface_subset_[0]
        if _subface_subset_[1] is not None:
            mod_set.aperture_set.skylight_modifier = _subface_subset_[1]
        if _subface_subset_[2] is not None:
            mod_set.aperture_set.operable_modifier = _subface_subset_[2]
        if _subface_subset_[3] is not None:
            mod_set.door_set.exterior_modifier = _subface_subset_[3]
        if _subface_subset_[4] is not None:
            mod_set.door_set.overhead_modifier = _subface_subset_[4]
        if _subface_subset_[5] is not None:
            mod_set.door_set.exterior_glass_modifier = _subface_subset_[5]

    if len(_shade_subset_) != 0:
        assert len(_shade_subset_) == 2, 'Input _shade_subset_ is not valid.'
        if _shade_subset_[0] is not None:
            mod_set.shade_set.exterior_modifier = _shade_subset_[0]
        if _shade_subset_[1] is not None:
            mod_set.shade_set.interior_modifier = _shade_subset_[1]
