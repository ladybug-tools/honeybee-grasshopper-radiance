#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2020, Mostapha Sadeghipour Roudsari <mostapha@ladybug.tools> 
# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
This component expects the annual daylight simulation to be run with one sensor
grid per room in the model. If the sensor grids within the annual daylight
simulation are distrbuted over the entire floor of each room, the resulting
schedules will be idealized, where light dimming has been optimized to supply
the minimum illuminance setpoint everywhere in the room. Grids with one, two,
or more sensors can be used to model setups where fractions of each room are
controlled by different sensors.
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
            approximate manual light-switching behaviour when used in conjunction
            with the off_at_min_ output below. (Default: 0.2).
        off_at_min_: Boolean to note whether lights should switch off completely when
            they get to the minimum power input. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with simple daylight controls assigned to them.
"""

ghenv.Component.Name = 'HB Daylight Control Schedule'
ghenv.Component.NickName = 'DaylightSchedule'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os

try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee_radiance.postprocess.annualdaylight import \
        generate_default_schedule, _process_input_folder
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


def diminng_from_ill(ill_val, ill_setpt, min_pow, min_light, off_at_min):
    """Compute the dimming fraction from an illuminance value."""
    if ill_val > ill_setpt:  # dimmed all of the way
        return 0 if off_at_min else min_pow
    elif ill_val <= min_light:  # not dimmed at all
        return 1
    else:  # partially dimmed
        fract_dim = (ill_setpt - ill_val) / (ill_setpt - min_light)
        return fract_dim + ((1 - fract_dim) * min_pow)


def file_to_dimming_fraction(ill_file, su_pattern, setpt, m_pow, m_lgt, off_m):
    """Compute hourly dimming fractions for a given result file."""
    # get a base schedule of dimming fractions for the sun-up hours
    su_values = [0] * len(su_pattern)
    sensor_count = 0
    with open(ill_file) as results:
        for pt_res in results:
            sensor_count += 1
            for i, val in enumerate(pt_res.split()):
                su_values[i] += diminng_from_ill(float(val), setpt, m_pow, m_lgt, off_m)
    su_values = [val / sensor_count for val in su_values]

    # account for the hours where the sun is not up
    dim_fract = [1] * 8760
    for val, hr in zip(su_values, su_pattern):
        dim_fract[hr] = float(val)
    return dim_fract


if all_required_inputs(ghenv.Component):
    # set default values for all controls
    _ill_setpoint_ = 300 if _ill_setpoint_ is None else _ill_setpoint_
    _min_power_in_ = 0.3 if _min_power_in_ is None else _min_power_in_
    _min_light_out_ = 0.2 if _min_light_out_ is None else _min_light_out_
    off_at_min_ = False if off_at_min_ is None else off_at_min_

    # process the base schedule input into a list of values
    if _base_schedule_ is None:
        schedule = generate_default_schedule()
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
    grids, sun_up_hours = _process_input_folder(res_folder, '*')
    sun_up_hours = [int(h) for h in sun_up_hours]

    # get the dimming fractions for each sensor grid from the .ill files
    dim_fracts = []
    for grid_info in grids:
        ill_file = os.path.join(res_folder, '%s.ill' % grid_info['full_id'])
        fract_list = file_to_dimming_fraction(
            ill_file, sun_up_hours, _ill_setpoint_, _min_power_in_,
            _min_light_out_, off_at_min_
        )
        dim_fracts.append(fract_list)

    # create the schedule by combining the base schedule with the dimming fraction
    type_limit = schedule_type_limit_by_identifier('Fractional')
    schedules = []
    for grid_info, dim_fract in zip(grids, dim_fracts):
        sch_vals = [b_val * d_val for b_val, d_val in zip(schedule, dim_fract)]
        sch_id = '{} Daylight Control'.format(grid_info['full_id'])
        schedules.append(ScheduleFixedInterval(sch_id, sch_vals, type_limit))
