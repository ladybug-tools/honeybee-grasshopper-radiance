# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a list of exterior modifiers that can be used to edit or create a
ModifierSet object.
-

    Args:
        _exterior_wall_: A modifier object for exterior walls (or text for
            the identifier of the modifier within the library).
        _exterior_roof_: A modifier object for exterior roofs (or text for
            the identifier of the modifier within the library).
        _exposed_floor_: A modifier object for exposed floors (or text for
            the identifier of the modifier within the library).
    
    Returns:
        exterior_set: A list of exterior modifiers that can be used to edit
            or create a ModifierSet object.
"""

ghenv.Component.Name = 'HB Exterior Modifier Subset'
ghenv.Component.NickName = 'ExteriorSubset'
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
if _exterior_wall_ is not None:
    _exterior_wall_ = check_mod(_exterior_wall_, '_exterior_wall_')
if _exterior_roof_ is not None:
    _exterior_roof_ = check_mod(_exterior_roof_, '_exterior_roof_')
if _exposed_floor_ is not None:
    _exposed_floor_ = check_mod(_exposed_floor_, '_exposed_floor_')


# return the final list from the component
exterior_set = [_exterior_wall_, _exterior_roof_, _exposed_floor_]
