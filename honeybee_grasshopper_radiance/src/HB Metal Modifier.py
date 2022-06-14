# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a metal radiance modifier from a single reflectance.
-

    Args:
        _name_: Text to set the name for the modifier and to be incorporated into
            a unique modifier identifier.
        _reflect: A number between 0 and 1 for the metal reflectance.
            This reflectance will be the same for the red, green and blue channels.
        _spec_: A number between 0 and 1 for the fraction of specularity. Specularity
            of metals is usually 0.9 or greater. (Default: 0.9)
        _rough_: Roughness is specified as the rms slope of surface facets. A value
            of 0 corresponds to a perfectly smooth surface, and a value of 1 would be
            a very rough surface. Roughness values greater than 0.2 are not very
            realistic. (Default: 0).

    Returns:
        modifier: A metal modifier that can be assigned to a Honeybee geometry
            or Modifier Sets.
"""

ghenv.Component.Name = 'HB Metal Modifier'
ghenv.Component.NickName = 'MetalMod'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.modifier.material import Metal
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default modifier properties
    _spec_ = 0.9 if _spec_ is None else _spec_
    _rough_ = 0.0 if _rough_ is None else _rough_
    name = clean_and_id_rad_string('MetalMaterial') if _name_ is None else \
        clean_rad_string(_name_)

    # create the modifier
    modifier = Metal.from_single_reflectance(name, _reflect, _spec_, _rough_)
    if _name_ is not None:
        modifier.display_name = _name_
