# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate Annual Glare Metrics from result (.dgp) files.
_
Glare Autonmy is a metric describing the percentage of occupied
hours that each sensor is below the glare threshold.
_
Spatial Glare Autonomy is a metric describing the percentage of the sensor grid
that is free glare according to the glare threshold and the target time. The sGA
value is expressed as a percentage of the sensors in the analysis grid.

-
    Args:
        _results: An list of annual Radiance result files from the "HB Imageless Annual
            Glare" component (containing the .dgp files and the sun-up-hours.txt).
            This can also be just the path to the folder containing these result
            files.
        _occ_sch_: An annual occupancy schedule as a Ladybug Data Collection or a HB-Energy
            schedule object. This can also be the identifier of a schedule in
            your HB-Energy schedule library. Any value in this schedule that is
            0.1 or above will be considered occupied. If None, a schedule from
            9AM to 5PM on weekdays will be used.
        _glare_thresh_: Threshold for glare autonomy (GA) in DGP (default: 0.4).
        grid_filter_: The name of a grid or a pattern to filter the grids. For instance,
            first_floor_* will simulate only the sensor grids that have an
            identifier that starts with first_floor_. By default all the grids
            will be processed.
        _target_time_: A minimum threshold of occupied time (eg. 95% of the time), above
            which a given sensor passes and contributes to the spatial glare
            autonomy. (Default: 95%).

    Returns:
        report: Reports, errors, warnings, etc.
        GA: Glare autonomy results in percent. GA is the percentage of occupied hours
            that each sensor is free of glare according to the glare threshold.
            Each value is for a different sensor of the grid. These can be plugged
            into the "LB Spatial Heatmap" component along with meshes of the sensor
            grids to visualize results.
        sGA: Spatial glare autonomy as a percentage of the sensors for each analysis grid
            that does not exceed the glare threshold for a specified fraction of
            occupied hours, ie. the target time.
        pass_fail: A data tree of zeros and ones, which indicate whether a given sensor
            passes the criteria for being free of glare (1) or fails the criteria (0).
            Being free of glare does not necessarily mean that the sensor is glare-free
            for all hours, but that it is glare-free for a minimum percentage of
            occupied hours defined by the target time. Each value is for a different
            sensor of the grid. These can be plugged into the "LB Spatial Heatmap"
            component along with meshes of the sensor grids to visualize results.
"""

ghenv.Component.Name = "HB Annual Glare Metrics"
ghenv.Component.NickName = 'GlareMetrics'
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
    from honeybee_radiance.postprocess.annualglare import glare_autonomy_from_folder
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:  # honeybee schedule library is not available
    schedule_by_identifier = None

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree, \
        data_tree_to_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values for the thresholds and the grid filter
    grid_filter_ = '*' if grid_filter_ is None else grid_filter_
    _glare_thresh_ = _glare_thresh_ if _glare_thresh_ else 0.4

    # process the schedule
    if _occ_sch_ is None:
        schedule = None
    elif isinstance(_occ_sch_, BaseCollection):
        schedule = _occ_sch_.values
    elif isinstance(_occ_sch_, str):
        if schedule_by_identifier is not None:
            try:
                schedule = schedule_by_identifier(_occ_sch_).values()
            except TypeError:  # it's probably a ScheduleFixedInterval
                schedule = schedule_by_identifier(_occ_sch_).values
        else:
            raise ValueError('honeybee-energy must be installed to reference '
                             'occupancy schedules by identifier.')
    else:  # assume that it is a honeybee schedule object
        try:
            schedule = _occ_sch_.values()
        except TypeError:  # it's probably a ScheduleFixedInterval
            schedule = _occ_sch_.values
    if schedule is not None:
        bin_schedule = []
        for val in schedule:
            bin_val = 1 if val >= 0.1 else 0
            bin_schedule.append(bin_val)
        schedule = bin_schedule

    # compute the annual metrics
    res_folder = os.path.dirname(_results[0]) if os.path.isfile(_results[0]) \
        else _results[0]
    GA = glare_autonomy_from_folder(
        res_folder, schedule, _glare_thresh_, grid_filter_)
    GA = list_to_data_tree(GA)

    # process the input values into a readable format
    ga_mtx = [item[-1] for item in data_tree_to_list(GA)]
    _target_time_ = 95 if _target_time_ is None else _target_time_

    # determine whether each point passes or fails
    pass_fail = [[int(val > _target_time_) for val in grid] for grid in ga_mtx]

    # compute spatial glare autonomy from the pass/fail results
    sGA = [sum(pf_list) / len(pf_list) for pf_list in pass_fail]
    pass_fail = list_to_data_tree(pass_fail)  # convert matrix to data tree
