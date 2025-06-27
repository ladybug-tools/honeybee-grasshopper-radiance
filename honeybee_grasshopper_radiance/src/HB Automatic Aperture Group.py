# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate Aperture groups for exterior Apertures.
_
The Apertures are grouped by orientation unless _view_factor_ is set to True.
_
If grouping based on view factor the component calculates view factor from
Apertures to sky patches (rfluxmtx). Each Aperture is represented by a sensor
grid, and the view factor for the whole Aperture is the average of the grid. The
RMSE of the view factor to each sky patch is calculated between all Apertures.
Agglomerative hierarchical clustering (with complete-linkage method) is used to
group the Apertures by using a distance matrix of the RMSE values.

The view factor approach is Radiance-based (and slower) and will likely group
Apertures more accurately considering the context geometry of the Honeybee
Model.
-

    Args:
        _model: A Honeybee Model for which Apertures will be grouped automatically.
            Note that this model must have Apertures with Outdoors boundary
            condition assigned to it.
        _room_based_: A boolean to note whether the Apertures should be grouped on a
            room basis. If grouped on a room basis Apertures from different
            room cannot be in the same group. (Default: True).
        _view_factor_: A boolean to note whether the Apertures should be grouped by
            calculating view factors for the Apertures to a discretized sky or
            simply by the normal orientation of the Apertures. (Default: False).
        _size_: Aperture grid size for view factor calculation. A lower number
            will give a finer grid and more accurate results but the calculation
            time will increase. This option is only used if _view_factor_ is set
            to True. (Default: 0.2).
        vert_tolerance_: A float value for vertical tolerance between two Apertures.
            If the vertical distance between two Apertures is larger than this
            tolerance the Apertures cannot be grouped. If no value is given the
            vertical grouping will be skipped. (Default: None).
        states_: An optional list of Honeybee State objects to be applied to all the generated groups.
            These states should be ordered based on how they will be switched on.
            The first state is the default state and, typically, higher states
            are more shaded. If the objects in the group have no states, the
            modifiers already assigned the apertures will be used for all states.
        _run: Set to True to run the automatic Aperture grouping.

    Returns:
        model: The input Honeybee Model object where all Apertures with Outdoors
            boundary condition have been assigned a dynamic group identifier.
"""

ghenv.Component.Name = 'HB Automatic Aperture Group'
ghenv.Component.NickName = 'AutoGroup'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.oconv import Oconv
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance_command:\n\t{}'.format(e))

try:
    from honeybee_radiance.dynamic.multiphase import automatic_aperture_grouping
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    assert isinstance(_model, Model), \
        'Input _model must be a Model. Got {}'.format(type(_model))
    # duplicate model
    model = _model.duplicate()

    # set defaults
    room_based = True if _room_based_ is None else _room_based_
    view_factor = False if _view_factor_ is None else _view_factor_
    size = 0.2 if _size_ is None else _size_
    vertical_tolerance = None if vert_tolerance_ is None else vert_tolerance_

    # automatically assign groups
    automatic_aperture_grouping(
        model, size=size, room_based=room_based, view_factor_or_orientation=view_factor,
        vertical_tolerance=vertical_tolerance, states=states_)
