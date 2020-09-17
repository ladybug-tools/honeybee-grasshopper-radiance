# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Generate SensorGrid objects from the floors of honeybee Rooms.
These SensorGrids can be used in a grid-based recipe.
-
The names of the grids will be the same as the rooms that they came from.
-

    Args:
        _rooms: A list of honeybee Rooms for which sensor grids will be generated.
        _grid_size: Number for the size of the grid cells.
        _dist_floor_: Number for the distance to move points from the floors of
            the input rooms. The default is 0.8 meters.
        remove_out_: Boolean to note whether an extra check should be run to remove
            sensor points that lie outside the Room volume. Note that this can
            add significantly to the component's run time and this check is
            usually not necessary in the case that all walls are vertical
            and all floors are horizontal (Default: False).

    Returns:
        grid: A SensorGrid object that can be used in a grid-based recipe.
        points: The points that are at the center of each grid cell.
        mesh: Analysis mesh that can be passed to the 'Color Mesh' component.
"""

ghenv.Component.Name = 'HB Sensor Grid from Rooms'
ghenv.Component.NickName = 'GridRooms'
ghenv.Component.Message = '0.3.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.facetype import Floor
    from honeybee.typing import clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.config import conversion_to_meters, tolerance
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_face3d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults for any blank inputs
    if _dist_floor_ is None:
        _dist_floor_ = 0.8 / conversion_to_meters()

    # create lists to be filled with content
    grid = []
    points = []
    mesh = []

    for room in _rooms:
        # get all of the floor faces of the room as Breps
        floor_faces = [from_face3d(face.geometry.flip()) for face in room.faces
                       if isinstance(face.type, Floor)]

        if len(floor_faces) != 0:
            # create the gridded ladybug Mesh3D
            lb_mesh = to_joined_gridded_mesh3d(floor_faces, _grid_size, _dist_floor_)

            # remove points outside of the room volume if requested
            if remove_out_:
                pattern = [room.geometry.is_point_inside(pt)
                           for pt in lb_mesh.face_centroids]
                lb_mesh, vertex_pattern = lb_mesh.remove_faces(pattern)

            # extract positions and directions from the mesh
            base_points = [from_point3d(pt) for pt in lb_mesh.face_centroids]
            base_poss = [(pt.x, pt.y, pt.z) for pt in lb_mesh.face_centroids]
            base_dirs = [(vec.x, vec.y, vec.z) for vec in lb_mesh.face_normals]

            # create the sensor grid
            s_grid = SensorGrid.from_position_and_direction(room.identifier, base_poss, base_dirs)
            s_grid.display_name = clean_rad_string(room.display_name)
            s_grid.room_identifier = room.identifier
            s_grid.mesh = lb_mesh

            # append everything to the lists
            grid.append(s_grid)
            points.append(base_points)
            mesh.append(from_mesh3d(lb_mesh))

    # convert the lists of points to data trees
    points = list_to_data_tree(points)
