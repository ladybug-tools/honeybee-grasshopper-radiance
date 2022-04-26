# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply a section plane to a Honeybee Radiance View.
_
The plane will always be perpendicular to the view direction for perspective
and parallel view types. For fisheye view types, the clipping plane is actually
a clipping sphere, centered on the view point.
_
Objects in front of this imaginary plane will not be visible. This may be useful
for seeing through walls (to get a longer perspective from an exterior view point)
or for incremental rendering.
-

    Args:
        _view: A Honeybee Radiance View object to which a section plane should be applied.
        _origin: An point to set the origin of the section plane in 3D space. Note
            that the section plane is always perpenicular to the view direction
            for perspective and parallel views.

    Returns:
        view: A Honeybee View object that can be used in a view-based recipe.
"""

ghenv.Component.Name = 'HB Section Plane View'
ghenv.Component.NickName = 'SectionView'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_geometry.geometry3d.pointvector import Point3D
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.view import View
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # process the input view and origin
    if isinstance(_view, str):
        view = View.from_string(_view)
    else:
        assert isinstance(_view, View), \
            'Expected Honeybee View. Got {}.'.format(type(_view))
        view = _view.duplicate()
    view_pt = Point3D(*_view.position)
    origin = to_point3d(_origin)

    # set the fore clip according to the distance
    view.fore_clip = origin.distance_to_point(view_pt)
    #view.position = (origin.x, origin.y, origin.z)
