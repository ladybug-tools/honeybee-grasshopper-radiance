# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Add radiance Sensor Grids and/or Views to a Honeybee Model.
_
This assignment is necessary for any Radiance study, though whether a grid or a
view is required for a particular type of study is depenednet upon the recipe
used.

-

    Args:
        _model: A Honeybee Model to which the input grids_ and views_ will be assigned.
        grids_: A list of Honeybee-Radiance SensorGrids, which will be assigned to
            the input _model.
        views_: A list of Honeybee-Radiance Views, which will be assigned to the
            input _model.

    Returns:
        model: The input Honeybee Model with the grids_ and views_ assigned to it.
"""

ghenv.Component.Name = 'HB Assign Grids and Views'
ghenv.Component.NickName = 'AssignGridsViews'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

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
    if len(grids_) != 0:
        model.properties.radiance.sensor_grids = grids_
    if len(views_) != 0:
        model.properties.radiance.views = views_
