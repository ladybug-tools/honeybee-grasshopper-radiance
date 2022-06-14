# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Combine Honeybee Apertures into a single dynamic group. Apertures that are a part
of the same dynamic group will have their states change in unison. If an aperture
has no dynamic group, it is assumed to be static.
-
This component can also be used to combine apertures that already have states
assigned to them into one group since existing states are not overwritten if
nothing is connected to states_. In this case, the total number of states in
the dynamic group is equal to that of the object with the highest number of
states. After a dynamic aperture with fewer states than that of it's dynamic
group has hit its highest state, it remains in that state as the other dynamic
apertures continue to change.
-

    Args:
        _apertures: A list of Honeybee Apertures to be grouped together into a
            single dynamic group. Door objects can also be connected here to be
            included in the group.
        _name_: Text to be incorporated into a unique identifier for the dynamic
            Aperture group. If the name is not provided, a random name will be assigned.
        states_: An optional list of Honeybee State objects ordered based on
            how they will be switched on. The first state is the default state
            and, typically, higher states are more shaded. If the objects in the
            group have no states, the modifiers already assigned the apertures
            will be used for all states.

    Returns:
        group_aps: Honeybee apertures that are a part of the same dynamic group.
            These can be used directly in radiance simulations or can be added
            to Honeybee faces and rooms.
"""

ghenv.Component.Name = 'HB Dynamic Aperture Group'
ghenv.Component.NickName = 'ApertureGroup'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import uuid

try:  # import the core honeybee dependencies
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check and duplicate  the input objects
    group_aps = []
    for ap in _apertures:
        assert isinstance(ap, (Aperture, Door)), 'Expected Aperture or Door ' \
            'for dynamic group. Got {}.'.format(type(ap))
        group_aps.append(ap.duplicate())

    # set the name of the dynamic group
    name = clean_and_id_rad_string('ApertureGroup') if _name_ is None else clean_rad_string(_name_)
    for ap in group_aps:
        ap.properties.radiance.dynamic_group_identifier = name

    # assign any states if they are connected
    if len(states_) != 0:
        # assign states (including shades) to the first aperture
        group_aps[0].properties.radiance.states = [state.duplicate() for state in states_]

        # remove shades from following apertures to ensure they aren't double-counted
        states_wo_shades = []
        for state in states_:
            new_state = state.duplicate()
            new_state.remove_shades()
            states_wo_shades.append(new_state)
        for ap in group_aps[1:]:
            ap.properties.radiance.states = \
                [state.duplicate() for state in states_wo_shades]
