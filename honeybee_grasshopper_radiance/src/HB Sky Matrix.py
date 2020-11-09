# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Sky Matrix from Wea.
-

    Args:
        north_: A number between 0 and 360 that represents the degrees off from
            the y-axis to make North. This can also be a vector to set the North.
            Default is 0. The default North direction is the Y-axis (0 degrees).
        _wea: Ladybug Wea object.
        _density_: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
        hoys_: Optional list of numbers for the hours of the year to be included
            in the sky matrix [0-8759].

    Returns:
        readMe!: Reports, errors, warnings, etc.
        skymtx: Sky matrix for multi-phase daylight analysis.
"""

ghenv.Component.Name = 'HB Sky Matrix'
ghenv.Component.NickName = 'SkyMatrix'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from honeybee_radiance.lightsource.sky import SkyMatrix
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

    # set default values and process the hoys if they are input
    _density_ = _density_ or 1
    if len(hoys_) != 0:
        _wea = _wea.filter_by_hoys(hoys_)

    # create the sky object
    skymtx = SkyMatrix(_wea, north_, _density_)