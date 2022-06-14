# Honeybee: A Plugin for Environmental Analysis
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get the recommended ambient resoluation (-ar) needed to resolve details with a
given dimension in model units.
_
This recommendation is derived from the overall dimensions of the Radince scene
being simulated as well as the ambient accuracy (-aa) being used in the simulation.
_
The result from this component can be plugged directly into the additional_par_
of the "HB Radiance Parameter" component or into the radiance_par of any
recipe components.

-
    Args:
        _model: The Honeybee Model being used for Radiance simulation.
        _detail_dim: A number in model units that represents the dimension of the
            smallest detail that must be resolved in the Radiance simulation.
        _aa_: An number for ambient accuracy (-aa) being used in the Radiance smiulation.
            This value should be matched between this component and the component
            into which the ouput ar is being input. (Default: 0.25 for
            low-resolution Radiance studies).

    Returns:
        ar: The abmient resolution needed to resolve the _detail_dim as a text string.
            These can be plugged into the additional_par_ of the "HB Radiance
            Parameter" component or the radiance_par_ input of the recipes.
"""

ghenv.Component.Name = 'HB Ambient Resolution'
ghenv.Component.NickName = 'AR'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_rhino.grasshopper import all_required_inputs, recipe_result
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default -aa
    aa = 0.25 if _aa_ is None else _aa_

    # get the longest dimension
    min_pt, max_pt = _model.min, _model.max
    x_dim = max_pt.x - min_pt.x
    y_dim = max_pt.y - min_pt.y
    z_dim = max_pt.z - min_pt.z
    longest_dim = max((x_dim, y_dim, z_dim))
    
    # calculate the ambient resolution.
    a_res = int((longest_dim * aa) / _detail_dim)
    ar = '-ar {}'.format(a_res)
