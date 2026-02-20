# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
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
        _scale_: A scalar value to scale the geometry. By default the geometry
            is normalized to Rhino model units as a base scale. The scalar value
            is multiplied with this base scale.

    Returns:
        report: Reports, errors, warnings, etc.
        lum_poly: Geometric representation of the luminous opening.
        lum_web: Geometric representation of the candela distribution of the luminaire.
        lum_axes: Line representation of the C0-G0 axes of the luminaire.
"""

ghenv.Component.Name = 'HB Visualize Luminaire'
ghenv.Component.NickName = 'VizLuminaire'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.fromobjects import luminaire_objects
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree,   \
        give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    base_scale = 1 / conversion_to_meters()
    scale = base_scale if _scale_ is None else base_scale * _scale_
    
    luminaire_web, luminaire_poly, luminaire_axes = luminaire_objects(_luminaire, scale)
    
    lum_web = list_to_data_tree(luminaire_web)
    lum_poly = list_to_data_tree(luminaire_poly)
    lum_axes = list_to_data_tree(luminaire_axes)
