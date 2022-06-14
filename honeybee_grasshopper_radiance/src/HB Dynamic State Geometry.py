# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Honeybee.
#
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a StateGeometry object that can be assigned to the shades_ of a dynamic
state using the "HB Dynamic State" component.
-

    Args:
        _geo: Rhino Brep or Mesh geometry to be converted to StateGeometry.
        _name_: Text to set the name for the StateGeometry and to be incorporated into
            unique StateGeometry identifier. If the name is not provided, a random name
            will be assigned.
        _modifier_: A Honeybee Radiance Modifier object for the geometry. If None,
            it will be the Generic Exterior Shade modifier in the lib. (Default: None).
    
    Returns:
        geo: A Honeybee StateGeometry object representing planar geometry that
            can be assigned to Radiance states. This can be assigned using the
            "HB Dynamic State" component.
"""

ghenv.Component.Name = 'HB Dynamic State Geometry'
ghenv.Component.NickName = 'StateGeo'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import uuid

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.dynamic import StateGeometry
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    geo = []  # list of geometries that will be returned

    # set default name
    name = clean_and_id_rad_string('StateGeo') if _name_ is None \
        else clean_and_id_rad_string(_name_)

    # create the StateGeometry
    i = 0  # iterator to ensure each geometry gets a unique name
    for rh_geo in _geo:
        for lb_face in to_face3d(rh_geo):
            hb_geo = StateGeometry('{}_{}'.format(name, i), lb_face, _modifier_)
            if _name_ is not None:
                hb_geo.display_name = _name_
            geo.append(hb_geo)