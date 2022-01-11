# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a list of modifiers that can be used to edit or create a ModifierSet object.
-

    Args:
        _exterior_shade_: A modifier object for exterior shades (or text for
            the identifier of the modifier within the library).
        _interior_shade_: A modifier object for interior shades (or text for
            the identifier of the modifier within the library).
    
    Returns:
        shade_set: A list of shade modifiers that can be used to edit or create
            a ModifierSet object.
"""

ghenv.Component.Name = 'HB Shade Modifier Subset'
ghenv.Component.NickName = 'ShadeSubset'
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
if _exterior_shade_ is not None:
    _exterior_shade_ = check_mod(_exterior_shade_, '_exterior_shade_')
if _interior_shade_ is not None:
    _interior_shade_ = check_mod(_interior_shade_, '_interior_shade_')

# return the final list from the component
shade_set = [_exterior_shade_, _interior_shade_]
