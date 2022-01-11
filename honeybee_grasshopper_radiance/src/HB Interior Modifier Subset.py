# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a list of interior modifiers that can be used to edit or create a
ModifierSet object.
-

    Args:
        _interior_wall_: A modifier object for interior walls (or text for
            the identifier of the modifier within the library).
        _ceiling_: A modifier object for ceilings (or text for the identifier of
            the modifier within the library).
        _interior_floor_: A modifier object for interior floors (or text for
            the identifier of the modifier within the library).
        _interior_window_: A modifier object for all apertures with a Surface
            boundary condition. This can also be text for the identifier of the
            modifier within the library.
        _interior_door_: A modifier object for all opaque doors with a Surface
            boundary condition. This can also be text for the identifier of the
            modifier within the library.
        _int_glass_door_: A modifier object for all glass doors with a Surface
            boundary condition. This can also be text for the identifier of the
            modifier within the library.
    
    Returns:
        interior_set: A list of interior modifiers that can be used to edit
            or create a ModifierSet object.
"""

ghenv.Component.Name = 'HB Interior Modifier Subset'
ghenv.Component.NickName = 'InteriorSubset'
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


# go through each input modifier
if _interior_wall_ is not None:
    _interior_wall_ = check_mod(_interior_wall_, '_interior_wall_')
if _ceiling_ is not None:
    _ceiling_ = check_mod(_ceiling_, '_ceiling_')
if _interior_floor_ is not None:
    _interior_floor_ = check_mod(_interior_floor_, '_interior_floor_')
if _interior_window_ is not None:
    _interior_window_ = check_mod(_interior_window_, '_interior_window_')
if _interior_door_ is not None:
    _interior_door_ = check_mod(_interior_door_, '_interior_door_')
if _int_glass_door_ is not None:
    _int_glass_door_ = check_mod(_int_glass_door_, '_int_glass_door_')

# return the final list from the component
interior_set = [_interior_wall_, _ceiling_, _interior_floor_, _interior_window_,
                _interior_door_, _int_glass_door_]
