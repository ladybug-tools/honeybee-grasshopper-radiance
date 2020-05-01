# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a WEA object for an ASHRAE Revised Clear Sky (Tau Model) using a STAT file.
-

    Args:
        _stat_file = Full path to .stat file (typically next to the epw file).
        timestep_: An integer representing the timestep with which to make the 
            WEA object.  Default is set to 1 for 1 step per hour of the year.
    
    Returns:
        wea: A wea object from stat file. This wea object represents an ASHRAE Revised 
            Clear Sky ("Tau Model"), which is intended to determine peak solar load 
            and sizing parmeters for HVAC systems. The "Tau Model" uses monthly 
            optical depths found within a .stat file.
"""

ghenv.Component.Name = 'HB Tau Clear Sky from STAT'
ghenv.Component.NickName = 'TauClearSky'
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
    wea = Wea.from_stat_file(_stat_file, timestep_)