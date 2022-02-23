# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Generate electric lighting schedules from annual daylight results, which can be
used to account for daylight controls in energy simulations.
_
Such controls will dim the lights in the energy simulation according to whether
the illuminance values at the sensor locations are at a target illuminance setpoint.
_
In addition to benefiting from the accuracy of Radiance, using this component has
several advantages over the "HB Apply Daylight Control" component under HB-Energy.
Notably, it can account for setups with multiple illuminance sensors.
_
This component will generate one schedule per sensor grid in the simulation. Each
grid should have sensors at the locations in space where daylight dimming sensors
are located. Grids with one, two, or more sensors can be used to model setups
where fractions of each room are controlled by different sensors. If the sensor
grids are distributed over the entire floor of the rooms, the resulting schedules
will be idealized, where light dimming has been optimized to supply the minimum
illuminance setpoint everywhere in the room.
-

    Args:
        _results: An list of annual Radiance result files from the "HB Annual Daylight"
            component (containing the .ill files and the sun-up-hours.txt).
            This can also be just the path to the folder containing these
            result files.
        _base_schedule_: A lighting schedule representing the usage of lights without
            any daylight controls. The values of this schedule will be multiplied
            by the hourly dimming fraction to yield the output lighting schedules.
            The format of this schedule can be a Ladybug Data Collection, a HB-Energy
            schedule object, or the identifier of a schedule in the HB-Energy
            schedule library. If None, a schedule from 9AM to 5PM on weekdays
            will be used.
        _ill_setpoint_: A number for the illuminance setpoint in lux beyond which
            electric lights are dimmed if there is sufficient daylight.
            Some common setpoints are listed below. (Default: 300 lux).
            -
            50 lux - Corridors and hallways.
            150 lux - Computer work spaces (screens provide illumination).
            300 lux - Paper work spaces (reading from surfaces that need illumination).
            500 lux - Retail spaces or museums illuminating merchandise/artifacts.
            1000 lux - Operating rooms and workshops where light is needed for safety.

        _min_power_in_: A number between 0 and 1 for the the lowest power the lighting
            system can dim down to, expressed as a fraction of maximum
            input power. (Default: 0.3).
        _min_light_out_: A number between 0 and 1 the lowest lighting output the lighting
            system can dim down to, expressed as a fraction of maximum light
            output. Note that setting this to 1 means lights aren't dimmed at
            all until the illuminance setpoint is reached. This can be used to
            approximate manual light-switching behavior when used in conjunction
            with the off_at_min_ output below. (Default: 0.2).
        off_at_min_: Boolean to note whether lights should switch off completely when
            they get to the minimum power input. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with simple daylight controls assigned to them.
"""

ghenv.Component.Name = 'HB Daylight Control Schedule'
ghenv.Component.NickName = 'DaylightSchedule'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os

try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee_radiance.postprocess.electriclight import daylight_control_schedules
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from honeybee_energy.lib.schedules import schedule_by_identifier
    from honeybee_energy.lib.scheduletypelimits import schedule_type_limit_by_identifier
    from honeybee_energy.schedule.fixedinterval import ScheduleFixedInterval
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values for all controls
    _ill_setpoint_ = 300 if _ill_setpoint_ is None else _ill_setpoint_
    _min_power_in_ = 0.3 if _min_power_in_ is None else _min_power_in_
    _min_light_out_ = 0.2 if _min_light_out_ is None else _min_light_out_
    off_at_min_ = False if off_at_min_ is None else off_at_min_

    # process the base schedule input into a list of values
    if _base_schedule_ is None:
        schedule = _base_schedule_
    elif isinstance(_base_schedule_, BaseCollection):
        schedule = _base_schedule_.values
    elif isinstance(_base_schedule_, str):
        schedule = schedule_by_identifier(_base_schedule_).values()
    else:  # assume that it is a honeybee schedule object
        try:
            schedule = _base_schedule_.values()
        except TypeError:  # it's probably a ScheduleFixedInterval
            schedule = _base_schedule_.values

    # get the relevant .ill files
    res_folder = os.path.dirname(_results[0]) if os.path.isfile(_results[0]) \
        else _results[0]
    sch_vals, sch_ids = daylight_control_schedules(
        res_folder, schedule, _ill_setpoint_, _min_power_in_, _min_light_out_, off_at_min_)

    # create the schedule by combining the base schedule with the dimming fraction
    type_limit = schedule_type_limit_by_identifier('Fractional')
    schedules = []
    for shc_val, sch_id in zip(sch_vals, sch_ids):
        schedules.append(ScheduleFixedInterval(sch_id, shc_val, type_limit))
