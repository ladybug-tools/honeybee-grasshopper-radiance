# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an glass radiance modifier from a red, green, and blue transmittances
-

    Args:
        _name_: Text to set the name for the modifier and to be incorporated into
            a unique modifier identifier.
        _r_trans: A number between 0 and 1 for the transmittance of the red
            channel. (Default: 0).
        _g_trans: A number between 0 and 1 for the transmittance of the green
            channel. (Default: 0).
        _b_trans: A number between 0 and 1 for the transmittance of the blue
            channel. (Default: 0).
        _refract_: Index of refraction. Typical values are 1.52 for float
            glass and 1.4 for ETFE. If None, Radiance will default to using 1.52
            for glass (Default: None).

    Returns:
        modifier: A glass modifier that can be assigned to a Honeybee geometry or
            Modifier Sets.
"""

ghenv.Component.Name = 'HB Glass Modifier 3'
ghenv.Component.NickName = 'GlassMod3'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_rad_string, clean_and_id_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.modifier.material import Glass
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    name = clean_and_id_rad_string('GlassMaterial') if _name_ is None else \
        clean_rad_string(_name_)

    # create the modifier
    modifier = Glass.from_transmittance(name, _r_trans, _g_trans, _b_trans, _refract_)
    if _name_ is not None:
        modifier.display_name = _name_
