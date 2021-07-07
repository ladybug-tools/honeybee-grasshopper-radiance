# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Honeybee.
#
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Annual Daylight Metrics.

-

    Args:
        _results: An list of annual Radiance result files from the "HB Annual Daylight"
            component.  This should include both the .ill files and the
            sun-up-hours.txt
        _occ_sch_: An annual occupancy schedule as a Ladybug Data Collection or a HB-Energy
            schedule object. This can also be the identifier of a schedule in
            your HB-Energy schedule library. Any value in this schedule that is
            0.5 or above will be considered occupied. If None, a schedule from
            9AM to 5PM on weekdays will be used.
        _threshold_: Threshhold for daylight autonomy in lux (default: 300).
        _min_max_: A list for min, max value for useful daylight illuminance
                (default: (100, 3000)).

    Returns:
        report: Reports, errors, warnings, etc.
        DA: Daylight autonomy. The percentage of time that each sensor
            recieves equal or more than the threshold.
        UDI: Useful daylight illuminance. The percentage of time that illuminace
            falls between minimum and maximum thresholds.
        UDI_low: Numbers for the percent of time that is below the lower threshold
            of useful daylight illuminance.
        UDI_up: Numbers for the percent of time that is above the upper threshold
            of useful daylight illuminance.
"""

ghenv.Component.Name = "HB Annual Daylight Metrics"
ghenv.Component.NickName = 'AnnualMetrics'
ghenv.Component.Message = '1.2.2'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:  # honeybee schedule library is not available
    schedule_by_identifier = None

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def generate_default_schedule():
    """Create a list of 8760 values for a default occupancy schedule."""
    weekend = [0] * 24
    weekday = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    all_vals = []
    day_counter = 0
    week_counter = 1
    while day_counter < 365:
        day_counter += 1
        if week_counter < 7:
            if week_counter == 1:
                all_vals.extend(weekend)
            else:
                all_vals.extend(weekday)
            week_counter += 1
        else:
            all_vals.extend(weekend)
            week_counter = 1
    return all_vals


def parse_sun_up_hours(result_files, schedule):
    """Parse the sun-up hours from the result file .txt file.

    Args:
        result_files: A list of result files that contains the .txt file.
        schedule: A list of 8760 values for the occupancy schedule.
    """
    for i, r_file in enumerate(result_files):
        if r_file.endswith('.txt'):
            with open(r_file) as soh_f:
                occ_pattern = [schedule[int(float(h))] for h in soh_f]
            result_files.pop(i)  # remove it from the list
            return occ_pattern


def annual_metrics(ill_file, occ_pattern, total_occupied_hours,
                   threshold=300, min_t=100, max_t=2000):
    """Compute annual metrics for a given result file."""
    da, udi, udi_low, udi_up  = [], [], [], []
    with open(ill_file) as results:
        for pt_res in results:
            pda, pudi, pudi_low, pudi_up = 0, 0, 0, 0
            for is_occ, hourly_res in zip(occ_pattern, pt_res.split()):
                if is_occ < 0.5:
                    continue
                value = float(hourly_res)
                if value > threshold:
                    pda += 1
                if value < min_t:
                    pudi_low += 1
                elif value <= max_t:
                    pudi += 1
                else:
                    pudi_up += 1
            da.append(round(100.0 * pda / total_occupied_hours, 2))
            udi.append(round(100.0 * pudi / total_occupied_hours, 2))
            udi_low.append(round(100.0 * pudi_low / total_occupied_hours, 2))
            udi_up.append(round(100.0 * pudi_up / total_occupied_hours, 2))
    return da, udi, udi_low, udi_up



if all_required_inputs(ghenv.Component):
    # set default values for the thresholds
    _threshold_ = _threshold_ if _threshold_ else 300
    if len(_min_max_) != 0:
        assert len(_min_max_), 'Expected two values for _min_max_.'
        min_t = _min_max_[0]
        max_t = _min_max_[1]
    else:
        min_t = 100
        max_t = 2000

    # process the schedule and sun-up hours
    if _occ_sch_ is None:
        schedule = generate_default_schedule()
    elif isinstance(_occ_sch_, BaseCollection):
        schedule = _occ_sch_.values
    elif isinstance(_occ_sch_, str):
        if schedule_by_identifier is not None:
            schedule = schedule_by_identifier(_occ_sch_).values()
        else:
            raise ValueError('honeybee-energy must be installed to reference '
                             'occupancy schedules by identifier.')
    else:  # assume that it is a honeybee schedule object
        try:
            schedule = _occ_sch_.values()
        except TypeError:  # it's probably a ScheduleFixedInterval
            schedule = _occ_sch_.values
    total_occupied_hours = sum(schedule)
    occ_pattern = parse_sun_up_hours(_results, schedule)

    # compute the annual metrics
    DA, UDI, UDI_low, UDI_up = [], [], [], []
    for ill_file in _results:
        da, udi, udi_low, udi_up = \
            annual_metrics(ill_file, occ_pattern, total_occupied_hours,
                           _threshold_, min_t, max_t)
        DA.append(da)
        UDI.append(udi)
        UDI_low.append(udi_low)
        UDI_up.append(udi_up)
    DA = list_to_data_tree(DA)
    UDI = list_to_data_tree(UDI)
    UDI_low = list_to_data_tree(UDI_low)
    UDI_up = list_to_data_tree(UDI_up)