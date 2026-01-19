# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get Radiance Luminaires from a Honeybee Model.
-
    Args:
        _model: A Honeybee Model for which luminaires will be output.

    Returns:
        luminaires: A list of Honeybee-Radiance Luminaires that are assigned to the
            input _model.
"""

ghenv.Component.Name = 'HB Get Luminaires'
ghenv.Component.NickName = 'GetLuminaires'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

try:  # import core honeybee dependencies
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import honeybee_radiance dependencies
    from honeybee_radiance.writer import _filter_by_pattern
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_model, Model), \
        'Expected Honeybee Model. Got {}.'.format(type(_model))
    # get the honeybee-radiance objects
    luminaires = _model.properties.radiance.luminaires
    if luminaire_filter_ is not None:
        luminaires = _filter_by_pattern(luminaires, luminaire_filter_)
