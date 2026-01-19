# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Honeybee Luminaire.
_
The Luminaire object stores the photometric data of a light fixture and
provides methods to:
    - Parse IES LM-63 photometric data
    - Generate Radiance geometry via ies2rad
    - Generate photometric web geometry
    - Place and orient luminaire instances in space via a LuminaireZone
_
The Luminaire must be added to the Honeybee Model. The translation through ies2rad
happens in the recipe.
-
    Args:
        _ies: Path to an IES LM-63 photometric file.
        _name_: Optional name of the luminaire. If None the IES file is used as
            the luminaire name. If the Honeybee Model includes multiple luminaires,
            each luminaire must have an unique name.
        _luminaire_zone: A Honeybee LuminaireZone. The LuminaireZone specifices
            the location and rotation of the luminaire instances.
        custom_lamp_: A Honeybee CustomLamp. This can be used to specify custom
            chromaticity, color or color temperature.
        _loss_fac_:  A scalar multiplier applied to account for lamp lumen
            depreciation, dirt depreciation, or other system losses. Must be
            greater than 0 (default: 1).
        _cand_mult_: Additional scalar multiplier applied to candela values
            after parsing the IES file. Must be greater than 0 (default: 1).

    Returns:
        report: Reports, errors, warnings, etc.
        luminaire: A Honeybee Luminaire that can be used in a recipe.
"""

ghenv.Component.Name = 'HB Luminaire'
ghenv.Component.NickName = 'Luminaire'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from honeybee_radiance.luminaire import Luminaire, LuminaireZone
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults
    name = _name_ or None
    light_loss_factor = 1 if _loss_fac_ is None else _loss_fac_
    candela_multiplier = 1 if _cand_mult_ is None else _cand_mult_
    custom_lamp = custom_lamp_ or None

    # create luminaire
    luminaire = Luminaire(
        _ies, identifier=name, luminaire_zone=_luminaire_zone, custom_lamp=custom_lamp,
        light_loss_factor=light_loss_factor,candela_multiplier=candela_multiplier)
