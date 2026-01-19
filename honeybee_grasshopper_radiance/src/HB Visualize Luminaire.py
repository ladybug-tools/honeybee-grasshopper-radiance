# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize a Luminaire.
_
This is useful to check if the the spin, tilt, and rotation is applied correctly.

-
    Args:
        _luminaire: A Honeybee Luminaire.
        _scale_: A scalar value to scale the geometry.

    Returns:
        report: Reports, errors, warnings, etc.
        lum_poly: Geometric representation of the luminous opening.
        lum_web: Geometric representation of the candela distribution of the luminaire.
        lum_axes: Line representation of the C0-G0 axes of the luminaire.
"""

ghenv.Component.Name = 'HB Visualize Luminaire'
ghenv.Component.NickName = 'VizLuminaire'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import Rhino as rc
import math
from Rhino.Geometry import Point3d, PolyCurve, Brep, Line
import scriptcontext as sc
import copy
from ladybug_geometry.geometry3d.pointvector import Vector3D, Point3D
from ladybug_geometry.geometry3d.polyline import Polyline3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_rhino.fromgeometry import from_face3d

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree,   \
        give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def luminaire_web_to_rhino_breps(luminaire, normalize=True):
    """Generate geometric representation of the candela distribution of a luminaire.
    
    Args:
        luminaire: A Honeybee Luminaire.
        normalize: Set to True to Normalize candela values.
    
    Returns:
        List[Rhino.Geometry.Brep]
    """

    # Ensure photometry is parsed
    luminaire.parse_photometric_data()

    # Expand symmetry
    horz_deg, candelas = luminaire._expand_horizontal_angles(
        luminaire.horizontal_angles,
        luminaire.candela_values
    )

    vert_deg = luminaire.vertical_angles

    # Convert to radians
    horz = [math.radians(h) for h in horz_deg]
    vert = [math.radians(v) for v in vert_deg]

    # Normalize candela
    if normalize:
        max_cd = luminaire.max_candela or 1.0
        candelas = [
            [v / max_cd for v in row]
            for row in candelas
        ]

    # Scale = max luminous dimension
    mul3d = max(abs(luminaire.width_m), abs(luminaire.length_m))

    # Create vertical-angle curves
    curves = []

    for h_idx, h_ang in enumerate(horz):
        pts = []

        for v_idx, v_ang in enumerate(vert):
            cd = mul3d * candelas[h_idx][v_idx]

            x = cd * math.sin(v_ang) * math.cos(h_ang)
            y = cd * math.sin(v_ang) * math.sin(h_ang)
            z = -cd * math.cos(v_ang)

            pts.append(Point3d(x, y, z))

        curves.append(PolyCurve.CreateControlPointCurve(pts))

    # Create edge surfaces between curves
    breps = []

    for i in range(len(curves) - 1):
        b = Brep.CreateEdgeSurface([curves[i], curves[i + 1]])
        if b:
            breps.append(b)

    return breps


def luminaire_web_to_ladybug_faces(luminaire, normalize=True):
    """Generate a Ladybug-geometry photometric web.
    
    Args:
        luminaire: A Honeybee Luminaire.
        normalize: Set to True to Normalize candela values.
    
    Returns:
        List[Face3D]
    """

    luminaire.parse_photometric_data()

    horz_deg, candelas = luminaire._expand_horizontal_angles(
        luminaire.horizontal_angles,
        luminaire.candela_values
    )

    vert_deg = luminaire.vertical_angles

    horz = [math.radians(h) for h in horz_deg]
    vert = [math.radians(v) for v in vert_deg]

    if normalize:
        max_cd = luminaire.max_candela or 1.0
        candelas = [[v / max_cd for v in row] for row in candelas]

    scale = max(abs(luminaire.width_m), abs(luminaire.length_m))

    # Build vertical-angle polylines
    curves = []

    for h_idx, h_ang in enumerate(horz):
        pts = []
        for v_idx, v_ang in enumerate(vert):
            cd = scale * candelas[h_idx][v_idx]

            x = cd * math.sin(v_ang) * math.cos(h_ang)
            y = cd * math.sin(v_ang) * math.sin(h_ang)
            z = -cd * math.cos(v_ang)

            pts.append(Point3D(x, y, z))

        curves.append(Polyline3D(pts))

    # Create quad faces between adjacent curves
    faces = []

    for i in range(len(curves) - 1):
        c0 = curves[i].vertices
        c1 = curves[i + 1].vertices

        for j in range(len(c0) - 1):
            face = Face3D((c0[j], c0[j + 1], c1[j + 1], c1[j]))
            faces.append(face)

    return faces


def transform_geometry(geometry, spin=0, tilt=0, rotation=0, translation=(0,0,0), scale=1.0):
    """Transform a geometry or list of geometries based on spin, tilt, rotation,
    translation, scale.
    
    Args:
        geometry: """
    if not isinstance(geometry, list):
        geometry = [geometry]
    geometry = [copy.deepcopy(g) for g in geometry]

    norm_vec = rc.Geometry.Vector3d(0, 0, 1)
    plane = rc.Geometry.Plane(rc.Geometry.Point3d(0, 0, 0), norm_vec)
    origin = rc.Geometry.Point3d(0, 0, 0)

    # Scale
    if scale != 1.0:
        s = rc.Geometry.Transform.Scale(plane, scale, scale, scale)
        for g in geometry: g.Transform(s)

    # Spin (Z-axis)
    if spin != 0:
        t = rc.Geometry.Transform.Rotation(math.radians(spin), rc.Geometry.Vector3d.ZAxis, origin)
        for g in geometry: g.Transform(t)

    # Tilt (Y-axis)
    if tilt != 0:
        t = rc.Geometry.Transform.Rotation(math.radians(tilt), rc.Geometry.Vector3d.YAxis, origin)
        for g in geometry: g.Transform(t)

    # Rotate (Z-axis)
    if rotation != 0:
        t = rc.Geometry.Transform.Rotation(math.radians(rotation), rc.Geometry.Vector3d.ZAxis, origin)
        for g in geometry: g.Transform(t)

    # Translate
    x, y, z = translation
    t = rc.Geometry.Transform.Translation(x, y, z)
    for g in geometry: g.Transform(t)

    return geometry if len(geometry) > 1 else geometry[0]


def place_luminaire_from_object(luminaire, luminaire_web, scale):
    """Take a Luminaire object, place its geometry at all points in its LuminaireZone,
    applying spin, tilt, and rotation.
    
    Args:
        luminaire: A Honeybee Luminaire.
        luminaire_web: Geometric representation of the candela distribution of
            of the luminaire.
        scale: Scalar value to scale the geometry.
    
    Returns:
        List[Rhino.Geometry.Brep]
    """
    if luminaire.luminaire_zone is None:
        return [luminaire_web]

    luminaire_zone = luminaire.luminaire_zone
    geometry = []

    for instance in luminaire_zone.instances:
        geo = transform_geometry(
            luminaire_web,
            spin=instance.spin,
            tilt=instance.tilt,
            rotation=instance.rotation,
            translation=instance.point,
            scale=scale
        )
        geometry.append(geo)

    return geometry


def create_luminaire_brep(luminaire):
    """Create geometric representation of the luminous opening of a Luminaire.
    
    Args:
        luminaire: A Honeybee Luminaire.
    
    Returns:
        List[Rhino.Geometry.Brep]
    """
    w = luminaire.width_m
    l = luminaire.length_m
    h = luminaire.height_m

    plane = rc.Geometry.Plane.WorldXY
    origin = rc.Geometry.Point3d.Origin
    breps = []

    # Implies that the luminous opening is a point
    if round(w, 2) == 0 and round(l, 2) == 0 and round(h, 2) == 0:
        return []
    # Implies that luminous opening is rectangular
    elif w > 0 and l > 0 and round(h, 2) == 0:
        corner_a = rc.Geometry.Point3d(-l/2, -w/2, 0)
        corner_b = rc.Geometry.Point3d(l/2, w/2, 0)
        lum_rect = rc.Geometry.Rectangle3d(plane, corner_a, corner_b).ToNurbsCurve()
        lum_poly = rc.Geometry.Brep.CreatePlanarBreps([lum_rect])[0]
    # Implies that luminous opening is rectangular with luminous sides
    elif w > 0 and l > 0 and h> 0:
        x_interval = rc.Geometry.Interval(-l/2, l/2)
        y_interval = rc.Geometry.Interval(-w/2, w/2)
        z_interval = rc.Geometry.Interval(-h/2, h/2)
        lum_poly = rc.Geometry.Box(plane, x_interval, y_interval, z_interval)
    # Implies that the luminous opening is a circle  
    elif w < 0 and l < 0 and round(l, 2) == round(w, 2) and round(h, 2) == 0:
        lum_circ = rc.Geometry.Circle(plane ,origin, abs(-w/2)).ToNurbsCurve()
        lum_poly = rc.Geometry.Brep.CreatePlanarBreps([lum_circ])[0]
    elif w < 0 and round(l, 2) == 0 and round(h, 2) == 0:
        lum_circ = rc.Geometry.Circle(plane, origin, abs(-w/2)).ToNurbsCurve()
        lum_poly = rc.Geometry.Brep.CreatePlanarBreps([lum_circ])[0]
    # Implies that the luminous opening is an ellipse
    elif w < 0 and l < 0 and round(l, 2) != round(w, 2) and round(h, 2) == 0:
        lum_ellip = rc.Geometry.Ellipse(plane, abs(-w/2), abs(-l/2)).ToNurbsCurve()
        lum_poly = rc.Geometry.Brep.CreatePlanarBreps([lum_ellip])[0]
    # Implies the luminous opening is a vertical cylinder
    elif w < 0 and l < 0 and h > 0 and round(l, 2) == round(w, 2):
        lum_circ = rc.Geometry.Circle(plane, origin, abs(-w/2))
        lum_poly = rc.Geometry.Cylinder(lum_circ, h).ToBrep(True, True)
    # Implies the luminous opening is a vertical elliptcal cylinder
    elif w < 0 and l < 0 and h > 0 and round(l, 2) != round(w, 2):
        lum_circ = rc.Geometry.Circle(plane, origin, 1)
        lum_poly = rc.Geometry.Cylinder(lum_circ, 1).ToNurbsSurface()
        transf = rc.Geometry.Transform.Scale(plane, abs(w/2), abs(l/2), abs(h))
        lum_poly.Transform(transf)
        lum_poly = lum_poly.ToBrep().CapPlanarHoles(sc.doc.ModelAbsoluteTolerance)
    elif w < 0 and l < 0 and h < 0 and round(l, 2) == round(w, 2) and round(w, 2) == round(h, 2):
        lum_poly = rc.Geometry.Sphere(rc.Geometry.Point3d(0, 0, abs(w/2)), abs(w/2))
    # Implies the luminous opening is an ellipsoid
    elif w < 0 and l < 0 and h < 0:
        lum_poly = rc.Geometry.Sphere(rc.Geometry.Point3d(0, 0, abs(w/2)), 1).ToNurbsSurface()
        transf = rc.Geometry.Transform.Scale(rc.Geometry.Plane(rc.Geometry.Point3d(0, 0, abs(w/2)), rc.Geometry.Vector3d.ZAxis), abs(w/2), abs(l/2), abs(h/2))
        lum_poly.Transform(transf)
    # Implies the luminous opening is a horizontal cylinder
    elif w < 0 and l > 0 and h < 0 and round(w, 2) == round(h, 2):
        lum_circ = rc.Geometry.Circle(rc.Geometry.Plane.WorldYZ,rc.Geometry.Point3d((-l/2), 0, abs(-w/2)), abs(-w/2))
        lum_poly = rc.Geometry.Cylinder(lum_circ, l).ToBrep(True, True)
    # Implies the luminous opening is a horizontal elliptical cylinder
    elif w < 0 and l > 0 and h < 0 and round(w, 2) != round(h, 2):
        cent_pt = rc.Geometry.Point3d((h/ 2), 0, abs(h/ 2))
        lum_circ = rc.Geometry.Circle(rc.Geometry.Plane.WorldYZ, cent_pt, 1)
        lum_poly = rc.Geometry.Cylinder(lum_circ, 1).ToNurbsSurface()
        transf = rc.Geometry.Transform.Scale(rc.Geometry.Plane(cent_pt,rc.Geometry.Vector3d.ZAxis), abs(l), abs(w/2), abs(h/2))
        lum_poly.Transform(transf)
        lum_poly = lum_poly.ToBrep().CapPlanarHoles(sc.doc.ModelAbsoluteTolerance)
    # Implies the luminous opening is a horizontal cylinder
    elif w > 0 and l < 0 and h < 0 and round(l, 2) == round(h, 2):
        lum_circ = rc.Geometry.Circle(rc.Geometry.Plane.WorldZX, rc.Geometry.Point3d(0, (-w/2), abs(-l/2)), abs(-l/2))
        lum_poly = rc.Geometry.Cylinder(lum_circ, w).ToBrep(True, True)
    # Implies the luminous opening is a horizontal elliptical cylinder
    elif w > 0 and l < 0 and h < 0 and round(l, 2) != round(h, 2):
        cent_pt = rc.Geometry.Point3d(0, (-w/2), abs(h/2))
        lum_circ = rc.Geometry.Circle(rc.Geometry.Plane.WorldZX, cent_pt, 1)
        lum_poly = rc.Geometry.Cylinder(lum_circ, 1).ToNurbsSurface()
        transf = rc.Geometry.Transform.Scale(rc.Geometry.Plane(cent_pt, rc.Geometry.Vector3d.ZAxis), abs(l/2), abs(w), abs(h/2))
        lum_poly.Transform(transf)
        lum_poly = lum_poly.ToBrep().CapPlanarHoles(sc.doc.ModelAbsoluteTolerance)
    # Implies the luminous opening is a vertical circle
    elif w < 0 and round(l) == 0 and h < 0 and round(w, 2) == round(h, 2):
        lum_circ = rc.Geometry.Circle(rc.Geometry.Plane.WorldYZ, origin, abs(w/2)).ToNurbsCurve()
        lum_poly = rc.Geometry.Brep.CreatePlanarBreps([lum_circ])[0]
    # Implies the luminous opening is a vertical ellipse
    elif w < 0 and round(l) == 0 and h < 0 and round(w, 2) != round(h, 2):
        lum_ellip = rc.Geometry.Ellipse(rc.Geometry.Plane.WorldYZ, abs(w/2), abs(h/2)).ToNurbsCurve()
        lum_poly = rc.Geometry.Brep.CreatePlanarBreps([lum_circ])[0]
    
    return lum_poly


def create_luminaire_axes(luminaire):
    """Draw the C0–G0 axes for a Luminaire according to IES LM-63.
    
    Args:
        luminare: A Honeybee Luminaire.
    
    Returns:
        [C0 axis, G0 axis]
    """

    # Ensure photometry is parsed
    luminaire.parse_photometric_data()

    # Dimensions
    width = luminaire.width_m
    length = luminaire.length_m
    height = luminaire.height_m

    # IES rule: circular luminaires
    # width < 0, length == 0: use width magnitude
    if abs(length) < 1e-6 and width < 0:
        length = abs(width)

    # Fallback if dimensions are zero
    if abs(length) < 1e-6:
        length = 0.5  # default

    origin = Point3d(0, 0, 0)

    # C0 axis
    c0_axis = Line(
        origin,
        Point3d(1.2 * length / 2.0, 0, 0)
    )

    # G0 axis
    g0_axis = Line(
        origin,
        Point3d(0, 0, -2.0 * length / 2.0)
    )

    return [c0_axis, g0_axis]


if all_required_inputs(ghenv.Component):
    scale = 1 if _scale_ is None else _scale_
    
    luminaire_web = luminaire_web_to_rhino_breps(_luminaire, normalize=True)
    lum_web = list_to_data_tree(place_luminaire_from_object(_luminaire, luminaire_web, scale))
    
    luminaire_poly = create_luminaire_brep(_luminaire)
    lum_poly = list_to_data_tree(place_luminaire_from_object(_luminaire, luminaire_poly, scale))
    
    luminaire_axes = create_luminaire_axes(_luminaire)
    lum_axes = list_to_data_tree(place_luminaire_from_object(_luminaire, luminaire_axes, scale))
