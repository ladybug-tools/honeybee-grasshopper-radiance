# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Generate SensorGrids of radial directions around positions from the floors of rooms.
_
This type of sensor grid is particularly helpful for studies of multiple view
directions, such as imageless glare studies.
_
The names of the grids will be the same as the rooms that they came from.
-

    Args:
        _rooms: A list of honeybee Rooms for which sensor grids will be generated.
            This can also be an entire Honeybee Model from which Rooms will
            be extracted.
        _grid_size: Number for the size of the grid cells.
        _dist_floor_: Number for the distance to move points from the floors of
            the input rooms. (Default: 1.2 meters).
        _dir_count_: A positive integer for the number of radial directions to be
            generated around each position. (Default: 8).
        _start_vec_: A Vector3D to set the start direction of the generated directions.
            This can be used to orient the resulting sensors to specific parts
            of the scene. It can also change the elevation of the resulting
            directions since this start vector will always be rotated in the
            XY plane to generate the resulting directions. (Default: (0, -1, 0)).
        wall_offset_: A number for the distance at which sensors close to walls
            should be removed.
        by_zone_: Set to "True" to have the component generate one sensor grid per zone
            across the input rooms rather than one sensor grid per room. This
            option is useful for getting a more consolidated set of Radiance
            results by zone. (Default: False).

    Returns:
        grid: A SensorGrid object that can be used in a grid-based recipe.
        points: The points that are at the center of each circle. These align with
            the vecs output below and can be visualized with the native
            Grasshopper vector display component.
        vecs: The vectors for the directions of each sensor. These align with
            the points output above and can be visualized with the native
            Grasshopper vector display component.
        mesh: Analysis mesh that can be passed to the 'Spatial Heatmap' component.
"""

ghenv.Component.Name = 'HB Radial Grid from Rooms'
ghenv.Component.NickName = 'RadialGridRooms'
ghenv.Component.Message = '1.9.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

from collections import OrderedDict

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d import Vector3D, Point3D, Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.typing import clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_vector3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults for any blank inputs and process the quad_only_
    _dist_floor_ = 1.2 / conversion_to_meters() if _dist_floor_ is None else _dist_floor_
    wall_offset = 0 if wall_offset_ is None else wall_offset_
    dir_count = 8 if _dir_count_ is None else _dir_count_
    try:
        st_vec = to_vector3d(_start_vec_)
    except AttributeError:
        st_vec = Vector3D(0, -1, 0)

    # gather all of the rooms
    rooms = []
    for obj in _rooms:
        if isinstance(obj, Model):
            rooms.extend(obj.rooms)
        elif isinstance(obj, Room):
            rooms.append(obj)
        else:
            raise TypeError('Expected Honeybee Room or Model. Got {}.'.format(type(obj)))

    # group the rooms by zone if requested
    if by_zone_:
        room_groups = OrderedDict()
        for room in rooms:
            try:
                room_groups[room.zone].append(room)
            except KeyError:  # first room to be found in the zone
                room_groups[room.zone] = [room]
    else:
        room_groups = OrderedDict([(room.identifier, [room]) for room in rooms])

    # create lists to be filled with content
    grid, points, vecs, mesh = [], [], [], []

    # loop through the rooms and create the grids
    for zone_id, room_group in room_groups.items():
        # get the base meshs
        floor_meshes = []
        for room in room_group:
            floor_mesh = room.properties.radiance._base_sensor_mesh(
                _grid_size, _grid_size, offset=_dist_floor_, remove_out=True,
                wall_offset=wall_offset)
            if floor_mesh is not None:
                floor_meshes.append(floor_mesh)
        if len(floor_meshes) == 0:
            continue
        floor_grid = Mesh3D.join_meshes(floor_meshes) \
            if len(floor_meshes) != 1 else floor_meshes[0]

        # create the sensor grid from the mesh
        mesh_radius = _grid_size * 0.45
        sg_name = room.display_name if not by_zone_ else zone_id
        grid_name = '{}_Radial'.format(clean_rad_string(sg_name))
        s_grid = SensorGrid.from_mesh3d_radial(
            grid_name, floor_grid, dir_count=dir_count, start_vector=st_vec,
            mesh_radius=mesh_radius)
        s_grid.room_identifier = room_group[0].identifier
        s_grid.display_name = sg_name

        # add the relevant items to the outputs
        grid.append(s_grid)
        sensors = s_grid.sensors
        base_points = [from_point3d(Point3D(*sen.pos)) for sen in sensors]
        base_vecs = [from_vector3d(Vector3D(*sen.dir)) for sen in sensors]
        points.append(base_points)
        vecs.append(base_vecs)
        lb_mesh = s_grid.mesh
        if lb_mesh is not None:
            mesh.append(from_mesh3d(lb_mesh))
        else:
            mesh.append(None)

    # convert the lists of points to data trees
    points = list_to_data_tree(points)
    vecs = list_to_data_tree(vecs)
