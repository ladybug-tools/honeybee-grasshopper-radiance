# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Custom sky from direct and diffuse irradiance.
-

    Args:
        north_: A number between 0 and 360 that represents the degrees off from
            the y-axis to make North. This can also be a vector to set the North.
            Default is 0. The default North direction is the Y-axis (0 degrees).
        _location: A Ladybug location object.
        _dir_rad: Direct normal irradiance (W/m2).
        _diff_rad: Diffuse horizontal irradiance (W/m2).
        _month_: An integer between 1 and 12 for the month of the year (default: 6).
        _day_: An integer between 1 and 31 for the day of the month (default: 21).
        _hour_: A number between 0 and 23.999 for the hour of the day (default: 12).

    Returns:
        sky: Honeybee sky. You can use this sky to create a daylight recipe.
"""

ghenv.Component.Name = 'HB Custom Sky'
ghenv.Component.NickName = 'CustomSky'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from honeybee_radiance.lightsource.sky import ClimateBased
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.togeometry import to_vector2d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import math


if all_required_inputs(ghenv.Component):
    # process the north input
    north_ = north_ or 0
    try:  # it's a vector
        north_ = math.degrees(to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
    except AttributeError:  # north angle instead of vector
        north_ = float(north_)

    # set default values if they are not set
    _month_ = _month_ or 6
    _day_ = _day_ or 21
    _hour_ = _hour_ or 12

    # create the sky object
    sky = ClimateBased.from_location(
        _location, _month_, _day_, _hour_, _dir_rad, _diff_rad, north_)
