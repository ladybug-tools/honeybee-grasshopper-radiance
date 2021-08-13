# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate Spatial Daylight Autonomy (sDA) from lists of daylight autonomy values.
_
As per IES-LM-83-12 Spatial Daylight Autonomy (sDA) is a metric describing
annual sufficiency of ambient daylight levels in interior environments.
It is defined as the percent of an analysis area (the area where calcuations
are performed -typically across an entire space) that meets a minimum
daylight illuminance level for a specified fraction of the operating hours
per year. The sDA value is expressed as a percentage of area.

-
    Args:
        _DA: A data tree of daylight autonomy values output from the "HB Annual Dalyight"
            recipe or the "HB Annual Daylight Metrics" component.
        mesh_: An optional list of Meshes that align with the _DA data tree above, which
            will be used to assign an area to each sensor. If no mesh is connected
            here, it will be assumed that each sensor represents an equal area
            to all of the others.
        _target_DA_: A number for the minimum target value for daylight autonomy
            at wich a given sensor is considered well daylit. (default: 50).

    Returns:
        report: Reports, errors, warnings, etc.
        sDA: Spatial daylight autonomy as percentage of area for each analysis grid.
        pass_fail: A data tree of zeros and ones, which indicate whether a given senor
            passes the criteria for being daylit (1) or fails the criteria (0). 
            Each value is for a different sensor of the grid. These can be plugged
            into the "LB Spatial Heatmap" component along with meshes of the
            sensor grids to visualize results.
"""

ghenv.Component.Name = 'HB Spatial Daylight Autonomy'
ghenv.Component.NickName = 'sDA'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '4 :: Results'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_rhino.togeometry import to_mesh3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree, \
        data_tree_to_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # process the input values into a rokable format
    da_mtx = [item[-1] for item in data_tree_to_list(_DA)]
    _target_DA_ = 50 if _target_DA_ is None else _target_DA_
    lb_meshes = [to_mesh3d(mesh) for mesh in mesh_]

    # determine whether each point passes or fails
    pass_fail = [[int(val > _target_DA_) for val in grid] for grid in da_mtx]

    # compute spatial daylight autonomy from the pass/fail results
    if len(lb_meshes) == 0:  # all sensors represent the same area
        sDA = [sum(pf_list) / len(pf_list) for pf_list in pass_fail]
    else:  # weight the sensors based on the area of mesh faces
        sDA = []
        for i, mesh in enumerate(lb_meshes):
            m_area = mesh.area
            weights = [fa / m_area for fa in mesh.face_areas]
            sDA.append(sum(v * w for v, w in zip(pass_fail[i], weights)))

    pass_fail = list_to_data_tree(pass_fail)  # convert matrix to data tree
