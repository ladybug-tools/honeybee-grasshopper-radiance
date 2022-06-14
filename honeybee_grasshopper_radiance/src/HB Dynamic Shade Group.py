# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Combine Honeybee Shades into a single dynamic group. Shades that are a part
of the same dynamic group will have their states change in unison. If an shade
has no dynamic group, it is assumed to be static.
-
This component can also be used to combine shades that already have states
assigned to them into one group since existing states are not overwritten if
nothing is connected to states_. In this case, the total number of states in
the dynamic group is equal to that of the object with the highest number of
states. After a dynamic shade with fewer states than that of it's dynamic
group has hit its highest state, it remains in that state as the other dynamic
shades continue to change.
-

    Args:
        _shades: A list of Honeybee Shades to be grouped together into a
            single dynamic group.
        _name_: Text to be incorporated into a unique identifier for the dynamic
            Shade group. If the name is not provided, a random name will be assigned.
        states_: An optional list of Honeybee State objects ordered based on
            how they will be switched on. The first state is the default state
            and, typically, higher states are more shaded. If the objects in the
            group have no states, the modifiers already assigned the shades
            will be used for all states.
    
    Returns:
        group_shds: Honeybee shades that are a part of the same dynamic group.
            These can be used directly in radiance simulations or can be added
            to Honeybee faces and rooms.
"""

ghenv.Component.Name = 'HB Dynamic Shade Group'
ghenv.Component.NickName = 'ShadeGroup'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import uuid

try:  # import the core honeybee dependencies
    from honeybee.shade import Shade
    from honeybee.typing import clean_and_id_rad_string, clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.dynamic import RadianceShadeState
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check and duplicate the input objects
    group_shds = []
    for shd in _shades:
        assert isinstance(shd, Shade), 'Expected Shade ' \
            'for dynamic shade group. Got {}.'.format(type(shd))
        group_shds.append(shd.duplicate())

    # set the name of the dynamic group
    name = clean_and_id_rad_string('ShadeGroup') if _name_ is None else clean_rad_string(_name_)
    for shd in group_shds:
        shd.properties.radiance.dynamic_group_identifier = name

    # assign any states if they are connected
    if len(states_) != 0:
        # convert the sub-face states to shade states
        shd_states = [RadianceShadeState(st.modifier, st.shades) for st in states_]
        # assign states (including shades) to the first shade
        group_shds[0].properties.radiance.states = [state.duplicate() for state in shd_states]

        # remove shades from following shades to ensure they aren't double-counted
        states_wo_shades = []
        for state in shd_states:
            new_state = state.duplicate()
            new_state.remove_shades()
            states_wo_shades.append(new_state)
        for shd in group_shds[1:]:
            shd.properties.radiance.states = \
                [state.duplicate() for state in states_wo_shades]
