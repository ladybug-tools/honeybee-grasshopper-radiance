# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Deconstruct a modifier into a radiance string.
-

    Args:
        _mod: A modifier to be deconstructed or text for a modifier to be looked
            up in the modifier library.

    Returns:
        rad_str: A Radiance string that includes all of the attributes that
            define the modifier.
"""

ghenv.Component.Name = 'HB Deconstruct Modifier'
ghenv.Component.NickName = 'DecnstrMod'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '0'


try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the input
    if isinstance(_mod, str):
        _mod = modifier_by_identifier(_mod)
    rad_str = _mod.to_radiance()
