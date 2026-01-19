# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Honeybee LuminaireZone of LuminaireInstances.
_
It is recommended to apply the rotation in the following order: spin, tilt, rotation.
If an aiming point is added it will override any spin, tilt, and rotation values.
-
    Args:
        _points: A point or list of points that will be used to position the luminaires.
        _spin_: Rotation about the local vertical axis (degrees), This axis is
            also called the G0 axis. Default: 0.
        _tilt_: Tilt angle around the Y axis (degrees). Default: 0.
        _rotation_: Rotation angle around the Z axis (degrees). Default: 0.
        aiming_point: A point representing the location at which the photometric
            axis of the luminaires should be aimed. This can also be a list of
            points that matches the length of _points.

    Returns:
        report: Reports, errors, warnings, etc.
        luminaire_zone: A LuminaireZone that can be plugged into a Luminaire.
"""

ghenv.Component.Name = 'HB Luminaire Zone'
ghenv.Component.NickName = 'LuminaireZone'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from honeybee_radiance.luminaire import LuminaireZone, LuminaireInstance
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults
    points = [to_point3d(pt) for pt in _points]
    _spin = [0]*len(points) if not _spin_ else _spin_
    _tilt = [0]*len(points) if not _tilt_ else _tilt_
    _rotation = [0]*len(points) if not _rotation_ else _rotation_
    _aiming_point = aiming_point_ or None

    if _aiming_point:
        if len(_aiming_point) == 1:  # all instances point to same aiming point
            _aiming_point = _aiming_point * len(points)

    lum_instances = []
    for idx, point in enumerate(points):
        spin = _spin[idx]
        tilt = _tilt[idx]
        rotation = _rotation[idx]
    
        if _aiming_point:
            aiming_point = _aiming_point[idx]
            lum_instance = LuminaireInstance.from_aiming_point(point, aiming_point, spin=spin, tilt=tilt, rotation=rotation)
        else:
            lum_instance = LuminaireInstance(point, spin, tilt, rotation)
    
        lum_instances.append(lum_instance)
    
    luminaire_zone = LuminaireZone(lum_instances)
