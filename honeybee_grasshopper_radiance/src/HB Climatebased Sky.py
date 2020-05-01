# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a point-in-time climate-based sky from a WEA.

    Args:
        north_: A number between 0 and 360 that represents the degrees off from
            the y-axis to make North. The default North direction is set to the
            Y-axis (default: 0 degrees).
        _wea: A Ladybug Wea object.
        _month_: An integer between 1 and 12 for the month of the year (default: 6).
        _day_: An integer between 1 and 31 for the day of the month (default: 21).
        _hour_: A number between 0 and 23.999.. for the hour of the day (default: 12).
    
    Returns:
        sky: A Honeybee sky that can be used to create a point-in-time recipe.
"""

ghenv.Component.Name = 'HB Climatebased Sky'
ghenv.Component.NickName = 'ClimateBased'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from honeybee_radiance.lightsource.sky import ClimateBased
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values
    north_ = north_ or 0
    _month_ = _month_ or 6
    _day_ = _day_ or 21
    _hour_ = _hour_ or 12

    # create the sky object
    sky = ClimateBased.from_wea(_wea, _month_, _day_, _hour_, north_)