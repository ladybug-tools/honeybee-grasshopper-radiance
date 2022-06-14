# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an opaque radiance modifier from red, green, and blue reflectances.
-

    Args:
        _name_: Text to set the name for the modifier and to be incorporated into
            a unique modifier identifier.
        _r_ref: A number between 0 and 1 for the red reflectance.
        _g_ref: A number between 0 and 1 for the green reflectance.
        _b_ref: A number between 0 and 1 for the blue reflectance.
        _spec_: A number between 0 and 1 for the fraction of specularity. Specularity
            fractions greater than 0.1 are not common in non-metallic
            materials. (Default: 0).
        _rough_: Roughness is specified as the rms slope of surface facets. A value
            of 0 corresponds to a perfectly smooth surface, and a value of 1 would be
            a very rough surface. Roughness values greater than 0.2 are not very
            realistic. (Default: 0).

    Returns:
        modifier: An opaque modifier that can be assigned to a Honeybee geometry
            or Modifier Sets.
"""

ghenv.Component.Name = 'HB Opaque Modifier 3'
ghenv.Component.NickName = 'OpaqueMod3'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.modifier.material import Plastic
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default modifier properties
    _spec_ = 0.0 if _spec_ is None else _spec_
    _rough_ = 0.0 if _rough_ is None else _rough_
    name = clean_and_id_rad_string('OpaqueMaterial') if _name_ is None else \
        clean_rad_string(_name_)

    # create the modifier
    modifier = Plastic(name, _r_ref, _g_ref, _b_ref, _spec_, _rough_)
    if _name_ is not None:
        modifier.display_name = _name_
