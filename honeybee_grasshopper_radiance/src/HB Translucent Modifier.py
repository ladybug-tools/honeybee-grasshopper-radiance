# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a translucent radiance modifier from a reflectance and transmittance.
_
The sum of the average reflectance and average transmittance must be less than 1
and any energy not transmitted or reflected is assumed to be absorbed.
The resulting material will always be grey with equivalent red, green and
blue channels.
_
More properties are available with the "HB Translucent Modifier 3" component.
-

    Args:
        _name_: Text to set the name for the modifier and to be incorporated into
            a unique modifier identifier.
        _avg_ref: The average reflectance of the material. The value should be
            between 0 and 1.
        _avg_trans: The average transmittance of the material. The value should be
            between 0 and 1.
        _is_spec_: Boolean to note if the reflected component is specular (True) or
            diffuse (False). (Default: False).
        _is_diffusing_: Boolean to note if the tranmitted component is diffused (True)
            instead of specular like glass (False). (Default: True).
        _rough_: Roughness is specified as the rms slope of surface facets. A value
            of 0 corresponds to a perfectly smooth surface, and a value of 1 would be
            a very rough surface. Roughness values greater than 0.2 are not very
            realistic. (Default: 0).

    Returns:
        modifier: A translucent modifier that can be assigned to a Honeybee geometry
            or Modifier Sets.
"""

ghenv.Component.Name = 'HB Translucent Modifier'
ghenv.Component.NickName = 'TransMod'
ghenv.Component.Message = '1.3.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.modifier.material import Trans
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default modifier properties
    _is_spec_ = False if _is_spec_ is None else _is_spec_
    _is_diffusing_ = True if _is_diffusing_ is None else _is_diffusing_
    _rough_ = 0.0 if _rough_ is None else _rough_
    name = clean_and_id_rad_string('TransMaterial') if _name_ is None else \
        clean_rad_string(_name_)

    # create the modifier
    modifier = Trans.from_average_properties(
        name, _avg_ref, _avg_trans, _is_spec_, _is_diffusing_, _rough_)
    if _name_ is not None:
        modifier.display_name = _name_
