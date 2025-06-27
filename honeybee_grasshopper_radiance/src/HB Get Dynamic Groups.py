# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get all of the Dynamic Radiance Groups assigned to a Model.
-

    Args:
        _model: A Honeybee Model for which dynamic groups will be output.

    Returns:
        group_ids: The identifiers of the dynamic groups assigned to the Model.
        group_aps: A data tree of Dynamic Apertures in the Model. Each branch of the
            tree represents a different Dynamic Aperture Group and corresponds to
            the group_ids above. The data tree can be exploded with the native
            Grasshopper "Explod Tree" component to assign schedules to each
            Dynamic Group for postprocessing.
"""

ghenv.Component.Name = 'HB Get Dynamic Groups'
ghenv.Component.NickName = 'GetDyn'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import core honeybee dependencies
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_model, Model), \
        'Expected Honeybee Model. Got {}.'.format(type(_model))
    # get the dynamic group objects
    groups = _model.properties.radiance.dynamic_subface_groups
    groups.sort(key=lambda x: x.identifier)

    # get the group attributes
    group_ids, group_aps = [], []
    for group in groups:
        group_ids.append([group.identifier])
        group_aps.append(group.dynamic_objects)
    group_ids = list_to_data_tree(group_ids)
    group_aps = list_to_data_tree(group_aps)
