# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Sensor Grid object that can be used in a grid-based recipe.
-

    Args:
        _name_: A name for this sensor grid.
        _positions: A list or a datatree of points with one point for the position
            of each sensor. Each branch of the datatree will be considered as a
            separate sensor grid.
        _directions_: A list or a datatree of vectors with one vector for the
            direction of each sensor. The input here MUST therefor align with
            the input _positions. If no value is provided (0, 0, 1) will be
            assigned for all the sensors.
        mesh_: An optional mesh that aligns with the sensors. This is useful for
            generating visualizations of the sensor grid beyond the sensor
            positions. Note that the number of sensors in the grid must match
            the number of faces or the number vertices within the mesh.
        base_geo_: An optional Brep for the geometry used to make the grid. There are
            no restrictions on how this brep relates to the sensors and it is
            provided only to assist with the display of the grid when the number
            of sensors or the mesh is too large to be practically visualized.

    Returns:
        grid: An SensorGrid object that can be used in a grid-based recipe.
"""

ghenv.Component.Name = 'HB Sensor Grid'
ghenv.Component.NickName = 'SensorGrid'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.togeometry import to_mesh3d, to_face3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default name and process the points to tuples
    name = clean_and_id_rad_string('SensorGrid') if _name_ is None else _name_
    pts = [(pt.X, pt.Y, pt.Z) for pt in _positions]

    # create the sensor grid object
    id  = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
    if len(_directions_) == 0:
        grid = SensorGrid.from_planar_positions(id, pts, (0, 0, 1))
    else:
        vecs = [(vec.X, vec.Y, vec.Z) for vec in _directions_]
        grid = SensorGrid.from_position_and_direction(id, pts, vecs)

    # set the display name
    if _name_ is not None:
        grid.display_name = _name_
    if '/' in name:
        grid.group_identifier = \
            '/'.join(clean_rad_string(key) for key in name.split('/')[1:])
    if mesh_ is not None:
        grid.mesh = to_mesh3d(mesh_)
    if base_geo_ is not None:
        grid.base_geometry = to_face3d(base_geo_)
