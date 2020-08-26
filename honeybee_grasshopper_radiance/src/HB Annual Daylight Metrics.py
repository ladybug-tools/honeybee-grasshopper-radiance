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
        _results: An list of annual Radiance result files from the "HB Run Workflow"
            component.  This should include both the .ill files and the
            sun-up-hours.txt
        _occ_sch_: An annual occupancy schedule as a Data Collection. Such a Data
            collection can be obtained from any honeybee energy schedule using
            the "HB Schedule To Data" component. By default, a schedule from
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
"""

ghenv.Component.Name = "HB Annual Daylight Metrics"
ghenv.Component.NickName = 'AnnualMetrics'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

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
    da = []
    udi = []
    with open(ill_file) as results:
        for pt_res in results:
            pda = 0
            pudi = 0
            for is_occ, hourly_res in zip(occ_pattern, pt_res.split()):
                if is_occ == 0:
                    continue
                value = float(hourly_res)
                if value > threshold:
                    pda += 1
                if min_t <= value <= max_t:
                    pudi += 1
            da.append(round(100.0 * pda / total_occupied_hours, 2))
            udi.append(round(100.0 * pudi / total_occupied_hours, 2))
    return da, udi



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
    schedule = _occ_sch_.values if _occ_sch_ else generate_default_schedule()
    total_occupied_hours = sum(schedule)
    occ_pattern = parse_sun_up_hours(_results, schedule)

    # compute the annual metrics
    DA, UDI = [], []
    for ill_file in _results:
        da, udi = annual_metrics(ill_file, occ_pattern, total_occupied_hours,
                                 _threshold_, min_t, max_t)
        DA.append(da)
        UDI.append(udi)
    DA = list_to_data_tree(DA)
    UDI = list_to_data_tree(UDI)