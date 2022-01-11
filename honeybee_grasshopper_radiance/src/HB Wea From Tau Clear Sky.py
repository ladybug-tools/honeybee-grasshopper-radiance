# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a WEA object for an ASHRAE Revised Clear Sky (Tau Model) using a STAT file.
-

    Args:
        _stat_file: Full path to .stat file that will be used to make the clear
            sky Wea. Note that an error will be raised if no atmospheric
            optical data is found in the file. In this case, the "HB Wea from
            Clear Sky" component can be used.
        hoys_: An optional list of hours of the year (numbers from 0 to 8759) for
            which the Wea will be filtered. HOYs can be generated from the
            "LB Analysis Period" component or they can be obtained through
            other means like analysis of the values in an occupancy schedule.
            By default, the Wea will be generated for the whole year.
        timestep_: An integer representing the timestep with which to make the 
            WEA object.  Default is set to 1 for 1 step per hour of the year.

    Returns:
        wea: A wea object from stat file. This wea object represents an ASHRAE Revised 
            Clear Sky ("Tau Model"), which is intended to determine peak solar load 
            and sizing parmeters for HVAC systems. The "Tau Model" uses monthly 
            optical depths found within a .stat file.
"""

ghenv.Component.Name = 'HB Wea From Tau Clear Sky'
ghenv.Component.NickName = 'TauClearSky'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

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
    if len(hoys_) != 0:
        wea = wea.filter_by_hoys(hoys_)