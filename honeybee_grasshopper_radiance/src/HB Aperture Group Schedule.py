# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Dynamic Aperture Group Schedule, which can be used to process any dynamic
aperture geometry that was run in an annual simulation.

-
    Args:
        _group_aps: Honeybee Apertures that are a part of the same dynamic group and will
            be assigned the same schedule for postprocessing. Typically, this is
            the output of the "HB Dynamic Aperture Group" component but it can
            also be the output of the "HB Get Dynamic Groups" component, which
            returns all of the dynamic groups on a particular Model.
        _schedule: A list of 8760 integers refering to the index of the aperture group state
            to be used at each hour of the simulation. This can also be a single integer
            for a static state to be used for the entire period of the simulation
            or a pattern of integers that is less than 8760 in length and will be
            repeated until the 8760 is reached. Note that 0 refers to the first
            state, 1 refers to the second state, and so on. -1 can be used to
            completely discout the aperture from the simulation for a given hour.

    Returns:
        dyn_sch: A dynamic schedule object for the input aperture group, which can be plugged
            into any of the Results components with a syn_sch input.
"""

ghenv.Component.Name = 'HB Aperture Group Schedule'
ghenv.Component.NickName = 'GroupSch'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance_postprocess.dynamic import ApertureGroupSchedule
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, recipe_result
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    dyn_sch = []
    dyn_ids = set()
    for ap in _group_aps:
        assert isinstance(ap, Aperture), 'Expected Aperture. Got {}.'.format(type(ap))
        dyn_grp_id = ap.properties.radiance.dynamic_group_identifier
        if dyn_grp_id is None:
            raise ValueError(
                'Input Aperture "{}" is not a part of a dynamic group.'.format(ap.display_name))
        if dyn_grp_id not in dyn_ids:
            dyn_ids.add(dyn_grp_id)
            _ap_group_sch = ApertureGroupSchedule(dyn_grp_id, _schedule)
            dyn_sch.append(_ap_group_sch)
