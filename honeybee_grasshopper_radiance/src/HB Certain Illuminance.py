# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a uniform sky that yields a certain illuminance.

-
    Args:
        _value_: Desired value for sky horizontal illuminance in lux. (Default: 10000).

    Returns:
        sky: A honeybee sky that can be used to create a point-in-time recipe.
"""

ghenv.Component.Name = 'HB Certain Illuminance'
ghenv.Component.NickName = 'CertainIllum'
ghenv.Component.Message = '1.2.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from honeybee_radiance.lightsource.sky import CertainIrradiance
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))


_value_ = 10000 if _value_ is None else _value_
sky = CertainIrradiance.from_illuminance(_value_)
