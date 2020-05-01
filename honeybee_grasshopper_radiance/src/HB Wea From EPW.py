# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Wea object from an EPW file.
-

    Args:
        _epw_file = Full path to epw weather file.
        timestep_: An integer representing the timestep with which to make the 
            WEA object.  Default is set to 1 for 1 step per hour of the year.
    
    Returns:
        wea: A wea object from epw file.
"""

ghenv.Component.Name = 'HB Wea From EPW'
ghenv.Component.NickName = 'Wea'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.wea import Wea
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    timestep_ = 1 if timestep_ is None else timestep_
    wea = Wea.from_epw_file(_epw_file, timestep_)
