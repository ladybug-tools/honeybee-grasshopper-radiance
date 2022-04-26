# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Honeybee View for an image-based analysis using a Rhino viewport.
-

    Args:
        _name_: Text to set the name for the modifier and to be incorporated into
            a unique modifier identifier.
        _viewport_: The Rhino viewport name which will be used to generate a radiance
            View object. Typical inputs include "Perspective", "Top", "Bottom",
            "Left", "Right", "Front", "Back" or any viewport name that you have
            saved within the Rhino file.  If no text is input here, the default
            will be the currently active viewport (the last viewport in which
            you navigated).
        _view_type_: An integer to set the view type (-vt). Choose from the choices
            below. Default: 0 if the viewport is in perspective; 2 if it is parallel.
                * 0 Perspective (v)
                * 1 Hemispherical fisheye (h)
                * 2 Parallel (l)
                * 3 Cylindrical panorama (c)
                * 4 Angular fisheye (a)
                * 5 Planisphere [stereographic] projection (s)
            For more detailed description about view types check rpict manual
            page (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
        refresh_: Connect a Grasshopper "button" component to refresh the orientation
            upon hitting the button.

    Returns:
        view: A Honeybee View object that can be used in a view-based recipe.
"""

ghenv.Component.Name = 'HB View from Viewport'
ghenv.Component.NickName = 'Viewport'
ghenv.Component.Message = '1.4.2'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.view import View
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.viewport import viewport_by_name, viewport_properties
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

VIEW_TYPES = ('v', 'h', 'l', 'c', 'a', 's')


# set the default values
name = clean_and_id_rad_string('View') if _name_ is None else _name_
if _view_type_ is None:
    _type_= 0
else:
    _type_= VIEW_TYPES.index(_view_type_) if _view_type_ in VIEW_TYPES else int(_view_type_)

# process the Rhino viewport
viewp = viewport_by_name(_viewport_)
v_props = viewport_properties(viewp, _type_)

# create the view object
view = View(
    clean_rad_string(name), v_props['position'], v_props['direction'],
    v_props['up_vector'], VIEW_TYPES[v_props['view_type']],
    v_props['h_angle'], v_props['v_angle'])
view.standardize_fisheye()
if _name_ is not None:
    view.display_name = _name_
