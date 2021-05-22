# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct a Wea object into data collections of direct, diffuse, and golbal
irradiance at each timestep of the file.

-
    Args:
        _wea: A Honeybee WEA object.

    Returns:
        readMe!: Reports, errors, warnings, etc.
        dir: A data collection of direct normal irradiance values at each timestep
            of the Wea.
        diff: A data collection of diffuse sky solar irradiance values at each
            timestep of the Wea.
        glob: A data collection of global horizontal irradiance values at each
            timestep of the Wea.
"""

ghenv.Component.Name = 'HB Deconstruct Wea'
ghenv.Component.NickName = 'DecnstrWea'
ghenv.Component.Message = '1.2.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    dir = _wea.direct_normal_irradiance
    diff = _wea.diffuse_horizontal_irradiance
    glob = _wea.global_horizontal_irradiance