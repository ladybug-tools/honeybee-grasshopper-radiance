# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Honeybee.
#
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a State object representing a single dynamic group state.
-

    Args:
        modifier_: A Honeybee Radiance Modifier object to be applied to this state's
            parent in this state. This is used to swap out the modifier in
            multi-phase studies. If None, it will be the parent's default modifier.
        shades_: An optional array of StateGeometry objects to be included
            with this state.
    
    Returns:
        state: A Honeybee State object representing a single dynamic group state.
            This can be assigned to apertures or shades using the "HB Dynamic
            Aperture Group" componet or the "HB Dynamic Shade Group" component.
"""

ghenv.Component.Name = 'HB Dynamic State'
ghenv.Component.NickName = 'State'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from honeybee_radiance.dynamic import RadianceSubFaceState
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

state = RadianceSubFaceState(modifier_, [geo.duplicate() for geo in shades_])
