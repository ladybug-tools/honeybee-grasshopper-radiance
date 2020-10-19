# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Honeybee View for an image-based analysis.
-

    Args:
        _name_: Text to set the name for the modifier and to be incorporated into
            a unique modifier identifier.
        _position: An point to set the position of the view in 3D space (-vp).
            This is the focal point of a perspective view or the center of a
            parallel projection.
        _direction: A vector for the direction that the veiw is facing (-vd).
            The length of this vector indicates the focal distance as needed by
            the pixel depth of field (-pd) in rpict.
        _up_vector_: An optional vector to set the vertical direction of the
            view (-vu). Default: (0, 0, 1)
        _view_type_: An integer to set the view type (-vt). Choose from the choices
            below. Default: 0.
                * 0 Perspective (v)
                * 1 Hemispherical fisheye (h)
                * 2 Parallel (l)
                * 3 Cylindrical panorama (c)
                * 4 Angular fisheye (a)
                * 5 Planisphere [stereographic] projection (s)
            For more detailed description about view types check rpict manual
            page (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
        _h_angle_: A number for the view horizontal size (-vh) in degrees. For a
            perspective projection (including fisheye views), val is the horizontal
            field of view. For a parallel projection, val is the view width in
            world coordinates. Default: 60.
        _v_angle_: A number for the view vertical size (-vv) in degrees. For
            a perspective projection (including fisheye views), val is the horizontal
            field of view. For a parallel projection, val is the view width in
            world coordinates. Default: 60.
    
    Returns:
        view: A Honeybee View object that can be used in an image-based recipe.
"""

ghenv.Component.Name = 'HB View'
ghenv.Component.NickName = 'View'
ghenv.Component.Message = '1.0.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.view import View
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

VIEW_TYPES = ('v', 'h', 'l', 'c', 'a')


if all_required_inputs(ghenv.Component):
    # process the points/vectors into tuples
    _pos = (_position.X, _position.Y, _position.Z)
    _dir = (_direction.X, _direction.Y, _direction.Z)

    # set the default values
    name = 'RadianceView' if _name_ is None else _name_
    _up_vec = (_up_vector_.X, _up_vector_.Y, _up_vector_.Z) if _up_vector_ \
        is not None else (0, 0, 1)
    _type_= 'v' if _view_type_ is None else VIEW_TYPES[_view_type_]
    _h_angle_ = 60 if _h_angle_ is None else _h_angle_
    _v_angle_ = 60 if _v_angle_ is None else _v_angle_

    view = View(
        clean_and_id_rad_string(name), _pos, _dir, _up_vec, _type_,
        _h_angle_, _v_angle_)
    if _name_ is not None:
        view.display_name = _name_
