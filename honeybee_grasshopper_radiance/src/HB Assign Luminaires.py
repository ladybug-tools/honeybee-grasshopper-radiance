# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add Radiance Luminaires to a Honeybee Model.
_
This assignment is necessary for any Radiance study, though whether a grid or a
view is required for a particular type of study is depenednet upon the recipe
used.
_
Multiple copies of this component can be used in series and each will add the
luminaires to any that already exist.

-
    Args:
        _model: A Honeybee Model to which the input _luminaires will be assigned.
        _luminaires: A list of Honeybee-Radiance Luminaires, which will be assigned to
            the input _model.

    Returns:
        model: The input Honeybee Model with the luminaires assigned to it.
"""

ghenv.Component.Name = 'HB Assign Luminaires'
ghenv.Component.NickName = 'AssignLuminaires'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

try:  # import core honeybee dependencies
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_model, Model), \
        'Expected Honeybee Model. Got {}.'.format(type(_model))
    model = _model.duplicate()  # duplicate to avoid editing the input
    model.properties.radiance.add_luminaires(_luminaires)
