# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a list of exterior subface (apertures + doors) modifiers that can be
used to edit or create a ModifierSet object.
-

    Args:
        _window_: A modifier object for apertures with an Outdoors boundary
            condition and a Wall face type for their parent face. This can also
            be text for the identifier of the modifier within the library.
        _skylight_: A modifier object for apertures with an Outdoors boundary
            condition and a RoofCeiling or Floor face type for their parent face.
            This can also be text for the identifier of the modifier within
            the library.
        _operable_: A modifier object for apertures with an Outdoors boundary
            condition and True is_operable property. This can also be text for
            the identifier of the modifier within the library.
        _exterior_door_: A modifier object for opaque doors with an Outdoors
            boundary condition and a Wall face type for their parent face. This
            can also be text for the identifier of the modifier within
            the library.
        _overhead_door_: A modifier object for opaque doors with an Outdoors
            boundary condition and a RoofCeiling or Floor face type for their
            parent face. This can also be text for the identifier of the modifier
            within the library.
        _glass_door_: A modifier object for all glass doors with an Outdoors
            boundary condition. This can also be text for the identifier of the
            modifier within the library.
    
    Returns:
        subface_set: A list of exterior subface modifiers that can be used
            to edit or create a ModifierSet object.
"""

ghenv.Component.Name = 'HB Subface Modifier Subset'
ghenv.Component.NickName = 'SubfaceSubset'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import honeybee_radiance dependencies
    from honeybee_radiance.modifier import Modifier
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))


def check_mod(mod, input_name):
    """Get an Modifier from the library if it's a string."""
    if isinstance(mod, str):
        return modifier_by_identifier(mod)
    else:
        assert isinstance(mod, Modifier), \
            'Expected Modifier for {}. Got {}'.format(input_name, type(mod))
    return mod


# go through each input construction
if _window_ is not None:
    _window_ = check_mod(_window_, '_window_')
if _skylight_ is not None:
    _skylight_ = check_mod(_skylight_, '_skylight_')
if _operable_ is not None:
    _operable_ = check_mod(_operable_, '_operable_')
if _exterior_door_ is not None:
    _exterior_door_ = check_mod(_exterior_door_, '_exterior_door_')
if _overhead_door_ is not None:
    _overhead_door_ = check_mod(_overhead_door_, '_overhead_door_')
if _glass_door_ is not None:
    _glass_door_ = check_mod(_glass_door_, '_glass_door_')


# return the final list from the component
subface_set = [_window_, _skylight_, _operable_, _exterior_door_,
               _overhead_door_, _glass_door_]
