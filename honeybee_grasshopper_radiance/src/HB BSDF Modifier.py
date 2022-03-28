# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Bidirectional Scattering Distribution Function (BSDF) radiance modifier
from an XML file.
-

    Args:
        _xml_file: Path to an XML file contining BSDF data. These files can
            be produced using the LBNL WINDOW software among other sources.
        _up_vec_: A vector that sets the hemisphere that the BSDF modifier faces.
            For materials that are symmetrical about the face plane (like
            non-angled venetian blinds), this can be any vector that is not
            perfectly normal/perpendicular to the face. For asymmetrica
            materials like angled venetian blinds, this variable should be
            coordinated with the direction that the geometry is facing.
            The default is set to (0.01, 0.01, 1.00), which should hopefully
            not be normal to any typical face.
        thickness_: Optional number to set the thickness of the BSDF. Thickness
            is not supported for aBSDF type. (Default: 0).
        _bsdf_type_: An integer to set the bsdf type. Choose from the choices
            below. (Default: 0).
                * 0 BSDF
                * 1 aBSDF
            Choose aBSDF (peak extraction) for systems with a strong specular
            transmission component. A proposed guideline for when to use aBSDF
            can be found in chapter 6 in "BSDF generation procedures for
            daylighting systems". Find the white paper at:
            * https://task61.iea-shc.org/publications

    Returns:
        modifier: A BSDF modifier that can be assigned to a Honeybee geometry
            or Modifier Sets.
"""

ghenv.Component.Name = 'HB BSDF Modifier'
ghenv.Component.NickName = 'BSDFMod'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.modifier.material import BSDF, aBSDF
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

BSDF_TYPES = ('bsdf', 'absdf')

if all_required_inputs(ghenv.Component):
    # process the vector input
    if _up_vec_ is not None:
        _up_vec_ = (_up_vec_.X, _up_vec_.Y, _up_vec_.Z)

    if _bsdf_type_ is None:
        _type_= 'bsdf'
    else:
        _type_= _bsdf_type_ if _bsdf_type_ in BSDF_TYPES else BSDF_TYPES[int(_bsdf_type_)]

    # create the modifier
    if _type_ == 'bsdf':
        modifier = BSDF(
            _xml_file, up_orientation=_up_vec_, thickness=thickness_)
    else:
        modifier = aBSDF(
            _xml_file, up_orientation=_up_vec_)
