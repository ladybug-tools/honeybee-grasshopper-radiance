# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Generate SensorGrid objects from exterior Faces (Walls, Roofs, and Floors).
_
These SensorGrids can be used in any grid-based recipe and are particularly useful
for radiation studies of roofs for photovoltaic potential or solar gain studies
of walls.
-

    Args:
        _hb_objs: A list of honeybee Faces or Rooms for which sensor grids will be
            generated. This can also be an entire Honeybee Model.
        _grid_size: Number for the size of the grid cells.
        _offset_: Number for the distance to move points from the base geometry.
            The default is 0.1 meters.
        _face_type_: Text or an integer to specify the type of face that will be used to
            generate grids. Note that only Faces with Outdoors boundary conditions
            will be used, meaning that most Floors will typically be
            excluded unless they represent the underside of a cantilever.
            Choose from the following. (Default: Wall).
                * 1 - Wall
                * 2 - Roof
                * 3 - Floor
                * 4 - All
        punched_: Boolean to note whether the punched_geometry of the faces
            should be used (True) with the areas of sub-faces removed from the grid
            or the full geometry should be used (False). (Default:False).
        quad_only_: Boolean to note whether meshing should be done using Rhino's
            defaults (False), which fills the entire face geometry to the edges
            with both quad and tringulated faces, or a mesh with only quad
            faces should be generated. (Default: False).

    Returns:
        grid: A SensorGrid object that can be used in a grid-based recipe.
        points: The points that are at the center of each grid cell.
        mesh: Analysis mesh that can be passed to the 'Spatial Heatmap' component.
"""

ghenv.Component.Name = 'HB Sensor Grid from Faces'
ghenv.Component.NickName = 'GridFaces'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.boundarycondition import Outdoors
    from honeybee.facetype import Floor, Wall, RoofCeiling
    from honeybee.typing import clean_rad_string, clean_and_id_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


FACE_TYPES = {
    '1': Wall,
    '2': RoofCeiling,
    '3': Floor,
    '4': (Wall, RoofCeiling, Floor),
    'Wall': Wall,
    'Roof': RoofCeiling,
    'RoofCeiling': RoofCeiling,
    'Floor': Floor,
    'All': (Wall, RoofCeiling, Floor)
}


if all_required_inputs(ghenv.Component):
    # set defaults for any blank inputs
    _offset_ = 0.1 / conversion_to_meters() if _offset_ is None else _offset_
    ft = FACE_TYPES[_face_type_.title()] if _face_type_ is not None else Wall

    # collect all of the relevant faces
    faces = []
    for obj in _hb_objs:
        if isinstance(obj, (Model, Room)):
            for face in obj.faces:
                if isinstance(face.boundary_condition, Outdoors) and isinstance(face.type, ft):
                    faces.append(face)
        elif isinstance(obj, Face):
            if isinstance(obj.boundary_condition, Outdoors) and isinstance(obj.type, ft):
                faces.append(obj)
        else:
            raise TypeError('Expected Honeybee Face, Room or Model. Got {}.'.format(type(obj)))

    # greneate the meshes and grids from the faces
    if len(faces) != 0:
        # create the gridded ladybug Mesh3D
        f_geos = [face.punched_geometry for face in faces] if punched_ else \
            [face.geometry for face in faces]
        if quad_only_:  # use Ladybug's built-in meshing methods
            lb_meshes = []
            for geo in f_geos:
                try:
                    lb_meshes.append(geo.mesh_grid(_grid_size, offset=_offset_))
                except AssertionError:
                    continue
            if len(lb_meshes) == 0:
                lb_mesh = None
            else:
                lb_mesh = lb_meshes[0] if len(lb_meshes) == 1 else \
                    Mesh3D.join_meshes(lb_meshes)
        else:  # use Rhino's default meshing
            rh_faces = [from_face3d(face) for face in f_geos]
            lb_mesh = to_joined_gridded_mesh3d(rh_faces, _grid_size, _offset_)

        if lb_mesh is not None:
            # extract positions and directions from the mesh
            mesh = from_mesh3d(lb_mesh)
            points = [from_point3d(pt) for pt in lb_mesh.face_centroids]
            base_poss = [(pt.x, pt.y, pt.z) for pt in lb_mesh.face_centroids]
            base_dirs = [(vec.x, vec.y, vec.z) for vec in lb_mesh.face_normals]

            # create the sensor grid
            f_nm = 'Faces' if isinstance(ft, tuple) else ft.__name__
            g_name = clean_rad_string('{}_Exterior{}'.format(_hb_objs[0].display_name, f_nm)) \
                if len(_hb_objs) == 1 else clean_and_id_rad_string('Exterior{}'.format(f_nm))
            grid = SensorGrid.from_position_and_direction(g_name, base_poss, base_dirs)
            grid.mesh = lb_mesh
