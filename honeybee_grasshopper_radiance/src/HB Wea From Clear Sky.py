# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a WEA object using the original ASHRAE Clear Sky formula.
-

    Args:
        _location: A Ladybug Location object which will set the sun poisition for
            the clear sky Wea. Locations can be obtained from the "LB Import
            EPW" or the "LB Construct Location" component.
        clearness_: A factor to be multiplied by the output of the clear sky model.
            This is to help account for locations where clear, dry skies predominate
            (e.g., at high elevations) or, conversely, where hazy and humid conditions
            are frequent. See Threlkeld and Jordan (1958) for recommended values.
            Typical values range from 0.95 to 1.05 and are usually never more
            than 1.2. (Default: 1.0).
        hoys_: An optional list of hours of the year (numbers from 0 to 8759) for
            which the Wea will be filtered. HOYs can be generated from the
            "LB Analysis Period" component or they can be obtained through
            other means like analysis of the values in an occupancy schedule.
            By default, the Wea will be generated for the whole year.
        timestep_: An integer representing the timestep with which to make the
            WEA object. (Default: 1, for 1 step per hour of the year).

    Returns:
        wea: A wea object from stat file. This wea object represents an original 
            ASHRAE Clear Sky, which is intended to determine peak solar load and
            sizing parmeters for HVAC systems.
"""

ghenv.Component.Name = 'HB Wea From Clear Sky'
ghenv.Component.NickName = 'ClearSky'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug.wea import Wea
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    timestep_ = 1 if timestep_ is None else timestep_
    clearness_ = 1 if clearness_ is None else clearness_
    wea = Wea.from_ashrae_clear_sky(_location, clearness_, timestep_)
    if len(hoys_) != 0:
        wea = wea.filter_by_hoys(hoys_)