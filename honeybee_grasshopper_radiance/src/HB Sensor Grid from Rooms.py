# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Generate SensorGrid objects from the floors of honeybee Rooms.
These SensorGrids can be used in a grid-based recipe.
-
The names of the grids will be the same as the rooms that they came from.
-

    Args:
        _rooms: A list of honeybee Rooms for which sensor grids will be generated.
            This can also be an entire Honeybee Model from which Rooms will
            be extracted.
        _grid_size: Number for the size of the grid cells.
        _dist_floor_: Number for the distance to move points from the floors of
            the input rooms. The default is 0.8 meters.
        quad_only_: Boolean to note whether meshing should be done using Rhino's
            defaults (False), which fills the entire _geometry to the edges
            with both quad and tringulated faces, or a mesh with only quad
            faces should be generated.
            _
            FOR ADVANCED USERS: This input can also be a vector object that will
            be used to set the orientation of the quad-only grid. Note that,
            if a vector is input here that is not aligned with the plane of
            the room's floors, an error will be raised.
        remove_out_: Boolean to note whether an extra check should be run to remove
            sensor points that lie outside the Room volume. Note that this can
            add significantly to the component's run time and this check is
            usually not necessary in the case that all walls are vertical
            and all floors are horizontal (Default: False).
        wall_offset_: A number for the distance at which sensors close to walls
            should be removed.

    Returns:
        grid: A SensorGrid object that can be used in a grid-based recipe.
        points: The points that are at the center of each grid cell.
        mesh: Analysis mesh that can be passed to the 'Spatial Heatmap' component.
"""

ghenv.Component.Name = 'HB Sensor Grid from Rooms'
ghenv.Component.NickName = 'GridRooms'
ghenv.Component.Message = '1.4.4'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.facetype import Floor, Wall
    from honeybee.typing import clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.config import conversion_to_meters, tolerance
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d, to_vector3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_face3d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults for any blank inputs and process the quad_only_
    _dist_floor_ = 0.8 / conversion_to_meters() if _dist_floor_ is None else _dist_floor_
    try:
        x_axis = to_vector3d(quad_only_)
    except AttributeError:
        x_axis = None

    # create lists to be filled with content
    grid = []
    points = []
    mesh = []
    rooms = []
    for obj in _rooms:
        if isinstance(obj, Model):
            rooms.extend(obj.rooms)
        elif isinstance(obj, Room):
            rooms.append(obj)
        else:
            raise TypeError('Expected Honeybee Room or Model. Got {}.'.format(type(obj)))

    for room in rooms:
        # get all of the floor faces of the room as Breps
        lb_floors = [face.geometry.flip() for face in room.faces if isinstance(face.type, Floor)]

        if len(lb_floors) != 0:
            # create the gridded ladybug Mesh3D
            if quad_only_:  # use Ladybug's built-in meshing methods
                if x_axis:
                    lb_floors = [Face3D(f.boundary, Plane(f.normal, f[0], x_axis), f.holes)
                                 for f in lb_floors]
                lb_meshes = []
                for geo in lb_floors:
                    try:
                        lb_meshes.append(geo.mesh_grid(_grid_size, offset=_dist_floor_))
                    except AssertionError:
                        continue
                if len(lb_meshes) == 0:
                    lb_mesh = None
                else:
                    lb_mesh = lb_meshes[0] if len(lb_meshes) == 1 else \
                        Mesh3D.join_meshes(lb_meshes)
            else:  # use Rhino's default meshing
                floor_faces = [from_face3d(face) for face in lb_floors]
                lb_mesh = to_joined_gridded_mesh3d(floor_faces, _grid_size, _dist_floor_)

            # remove points outside of the room volume if requested
            if remove_out_ and lb_mesh is not None:
                pattern = [room.geometry.is_point_inside(pt)
                           for pt in lb_mesh.face_centroids]
                try:
                    lb_mesh, vertex_pattern = lb_mesh.remove_faces(pattern)
                except AssertionError:  # the grid lies completely outside of the room
                    lb_mesh = None

            # remove any sensors within a certain distance of the walls, if requested
            if wall_offset_ is not None and lb_mesh is not None:
                wall_geos = [f.geometry for f in room.faces if isinstance(f.type, Wall)]
                pattern = []
                for pt in lb_mesh.face_centroids:
                    for wg in wall_geos:
                        if wg.plane.distance_to_point(pt) <= wall_offset_:
                            pattern.append(False)
                            break
                    else:
                        pattern.append(True)
                try:
                    lb_mesh, vertex_pattern = lb_mesh.remove_faces(pattern)
                except AssertionError:  # the grid lies completely outside of the room
                    lb_mesh = None

            if lb_mesh is not None:
                # extract positions and directions from the mesh
                base_points = [from_point3d(pt) for pt in lb_mesh.face_centroids]
                base_poss = [(pt.x, pt.y, pt.z) for pt in lb_mesh.face_centroids]
                base_dirs = [(vec.x, vec.y, vec.z) for vec in lb_mesh.face_normals]

                # create the sensor grid
                s_grid = SensorGrid.from_position_and_direction(
                    clean_rad_string(room.display_name), base_poss, base_dirs)
                s_grid.display_name = room.display_name
                s_grid.room_identifier = room.identifier
                s_grid.mesh = lb_mesh
                s_grid.base_geometry = \
                    tuple(f.move(f.normal * _dist_floor_) for f in lb_floors)

                # append everything to the lists
                grid.append(s_grid)
                points.append(base_points)
                mesh.append(from_mesh3d(lb_mesh))

    # convert the lists of points to data trees
    points = list_to_data_tree(points)
