# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Honeybee.
#
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Import the hourly illuminance or irradiance results of an annual daylight or irradiance
study to a list of data collections.
_
The resulting data collections can be visulized using the ladybug components or
deconstructed for detailed analysis with native Grasshopper math components.

-
    Args:
        _results: An list of annual Radiance result files from the "HB Annual Daylight"
            component (containing the .ill files and the sun-up-hours.txt).
            This can also be just the path to the folder containing these
            result files.
        sel_pts_: An optional point or list of points, which will be used to filter
            the sensors for which data collections will be imported. If there
            is an input here, the all_pts_ must be connected.
        all_pts_: The data tree of all sensor points that were used in the simulation.
            This is required in order to look up the index of the sel_pts_ in
            the results matrices. 

 Returns:
        report: Reports, errors, warnings, etc.
        data: A list of hourly data collections containing illuminance or irradiance results.
            These can be visulized using the ladybug components or deconstructed
            for detailed analysis with native Grasshopper math components.
"""

ghenv.Component.Name = 'HB Annual Results to Data'
ghenv.Component.NickName = 'AnnualToData'
ghenv.Component.Message = '1.2.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os

try:
    from ladybug.datatype.illuminance import Illuminance
    from ladybug.datatype.energyflux import Irradiance
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.header import Header
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee_radiance.postprocess.annualdaylight import _process_input_folder
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree, \
        data_tree_to_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def file_to_data(ill_file, point_filter, su_pattern, header, timestep):
    """Get a list of data collections for a given result file."""
    data_colls = []
    with open(ill_file) as results:
        if point_filter is None:
            for pt_res in results:
                base_values = [0] * 8760 * timestep
                for val, hr in zip(pt_res.split(), su_pattern):
                    base_values[hr] = float(val)
                data_colls.append(HourlyContinuousCollection(header, base_values))
        else:
            for i, pt_res in enumerate(results):
                if i in point_filter:
                    base_values = [0] * 8760 * timestep
                    for val, hr in zip(pt_res.split(), su_pattern):
                        base_values[hr] = float(val)
                    data_colls.append(HourlyContinuousCollection(header, base_values))
    return data_colls


def find_point_in_grid(s_pt, all_pts):
    """Find the index of a point in a list of list of grids."""
    for i, grid_pts in enumerate(all_pts):
        for j, g_pt in enumerate(grid_pts):
            if g_pt.is_equivalent(s_pt, tolerance):
                return i, j


if all_required_inputs(ghenv.Component):
    # get the relevant .ill files
    res_folder = os.path.dirname(_results[0]) if os.path.isfile(_results[0]) \
        else _results[0]
    grids, sun_up_hours = _process_input_folder(res_folder, '*')

    # check the sel_pts and all_pts input
    pt_filter = [None for i in grids]
    if len(sel_pts_) != 0:
        pt_filter = [[] for i in grids]
        all_pts = [[to_point3d(pt) for pt in dat[-1]] for dat in data_tree_to_list(all_pts_)]
        assert len(all_pts) != 0, 'all_pts_ must be connected in order to use sel_pts_.'
        sel_pts = [to_point3d(pt) for pt in sel_pts_]
        for s_pt in sel_pts:
            i, j = find_point_in_grid(s_pt, all_pts)
            pt_filter[i].append(j)

    # extract the timestep if it exists
    timestep, is_irr = 1, False
    tstep_file = os.path.join(res_folder, 'timestep.txt')
    if os.path.isfile(tstep_file):  # it's an annual irradiance simulation
        with open(tstep_file) as tf:
            timestep = int(tf.readline())
        is_irr = True

    # parse the sun-up-hours
    sun_up_hours = [int(h * timestep) for h in sun_up_hours]

    # create the header that will be used for all of the data collections
    aper = AnalysisPeriod(timestep=timestep)
    head =  Header(Irradiance(), 'W/m2', aper) if is_irr else \
        Header(Illuminance(), 'lux', aper)

    # create the data collections from the .ill files
    data = []
    for grid_info, p_filt in zip(grids, pt_filter):
        ill_file = os.path.join(res_folder, '%s.ill' % grid_info['full_id'])
        data_list = file_to_data(ill_file, p_filt, sun_up_hours, head, timestep)
        data.append(data_list)
    data = list_to_data_tree(data)
