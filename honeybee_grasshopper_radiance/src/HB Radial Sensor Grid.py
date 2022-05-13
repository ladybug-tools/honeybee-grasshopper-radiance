# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Sensor Grid object from radial directions around sensor positions.
_
This type of sensor grid is particularly helpful for studies of multiple view
directions, such as imageless glare studies.
-

    Args:
        _name_: A name for this sensor grid.
        _positions: A list or a datatree of points with one point for the position
            of each radial sensor. Each branch of the datatree will be
            considered as a separate sensor grid.
        _dir_count_: A positive integer for the number of radial directions to be
            generated around each position. (Default: 8).
        _start_vec_: A Vector3D to set the start direction of the generated directions.
            This can be used to orient the resulting sensors to specific parts
            of the scene. It can also change the elevation of the resulting
            directions since this start vector will always be rotated in the
            XY plane to generate the resulting directions. (Default: (0, -1, 0)).
        mesh_radius_: An optional number that can be used to generate a mesh that is
            aligned with the resulting sensors and will automatically be
            assigned to the grid. Such meshes will resemble a circle around
            each sensor with the specified radius and will contain triangular
            faces that can be colored with simulation results. If zero, no mesh
            will be generated for the sensor grid. (Default: 0.2 meters).

    Returns:
        grid: An SensorGrid object that can be used in a grid-based recipe.
        mesh: Analysis mesh that can be passed to the 'Spatial Heatmap' component.
"""

ghenv.Component.Name = 'HB Radial Sensor Grid'
ghenv.Component.NickName = 'SensorGrid'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.pointvector import Vector3D, Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.sensorgrid import SensorGrid
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_vector3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default name and process the points to tuples
    name = clean_and_id_rad_string('SensorGrid') if _name_ is None else _name_
    pts = [(pt.X, pt.Y, pt.Z) for pt in _positions]
    dir_count = 8 if _dir_count_ is None else _dir_count_
    mesh_radius = 0.2 / conversion_to_meters() if mesh_radius_ is None else mesh_radius_
    try:
        st_vec = to_vector3d(_start_vec_)
    except AttributeError:
        st_vec = Vector3D(0, -1, 0)

    # create the sensor grid object
    id  = clean_rad_string(name) if '/' not in name else clean_rad_string(name.split('/')[0])
    grid = SensorGrid.from_positions_radial(
        id, pts, dir_count, start_vector=st_vec, mesh_radius=mesh_radius)

    # set the display name and get outputs
    if _name_ is not None:
        grid.display_name = _name_
    if '/' in name:
        grid.group_identifier = \
            '/'.join(clean_rad_string(key) for key in name.split('/')[1:])
    sensors = grid.sensors
    points = [from_point3d(Point3D(*sen.pos)) for sen in sensors]
    vecs = [from_vector3d(Vector3D(*sen.dir)) for sen in sensors]
    lb_mesh = grid.mesh
    if lb_mesh is not None:
        mesh = from_mesh3d(lb_mesh)
