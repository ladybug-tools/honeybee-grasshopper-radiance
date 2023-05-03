# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate Aperture groups for exterior Apertures.
_
The Apertures are grouped by orientation unless _view_factor_ is set to True.
_
If grouping based on view factor the component calculates view factor from
Apertures to sky patches (rfluxmtx). Each Aperture is represented by a sensor
grid, and the view factor for the whole Aperture is the average of the grid. The
RMSE of the view factor to each sky patch is calculated between all Apertures.
Agglomerative hierarchical clustering (with complete-linkage method) is used to
group the Apertures by using a distance matrix of the RMSE values.

The view factor approach is Radiance-based (and slower) and will likely group
Apertures more accurately considering the context geometry of the Honeybee
Model.
-

    Args:
        _model: A Honeybee Model for which Apertures will be grouped automatically.
            Note that this model must have Apertures with Outdoors boundary
            condition assigned to it.
        _room_based_: A boolean to note whether the Apertures should be grouped on a
            room basis. If grouped on a room basis Apertures from different
            room cannot be in the same group. (Default: True).
        _view_factor_: A boolean to note whether the Apertures should be grouped by
            calculating view factors for the Apertures to a discretized sky or
            simply by the normal orientation of the Apertures. (Default: False).
        _size_: Aperture grid size for view factor calculation. A lower number
            will give a finer grid and more accurate results but the calculation
            time will increase. This option is only used if _view_factor_ is set
            to True. (Default: 0.2).
        vert_tolerance_: A float value for vertical tolerance between two Apertures.
            If the vertical distance between two Apertures is larger than this
            tolerance the Apertures cannot be grouped. If no value is given the
            vertical grouping will be skipped. (Default: None).
        _run: Set to True to run the automatic Aperture grouping.

    Returns:
        model: A Honeybee Model object where all Apertures with Outdoors
            boundary condition have been assigned a dynamic group identifier.
"""

ghenv.Component.Name = 'HB Automatic Aperture Group'
ghenv.Component.NickName = 'AutoGroup'
ghenv.Component.Message = '1.6.2'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import json

try:  # import honeybee_radiance dependencies
    from ladybug.futil import write_to_file_by_name
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.model import Model
    from honeybee.boundarycondition import Outdoors
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.oconv import Oconv
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance_command:\n\t{}'.format(e))

try:
    from honeybee_radiance.config import folders as rad_folders
    from honeybee_radiance.cli.multiphase import _aperture_view_factor, \
        _aperture_view_factor_postprocess, cluster_view_factor, \
        cluster_orientation, cluster_output
    from honeybee_radiance.lightsource.sky.skydome import SkyDome
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    assert isinstance(_model, Model), \
        'Input _model must be a Model. Got {}'.format(type(_model))
    # duplicate model
    model = _model.duplicate()

    # set defaults
    room_based = True if _room_based_ is None else _room_based_
    view_factor = False if _view_factor_ is None else _view_factor_
    size = 0.2 if _size_ is None else _size_
    vertical_tolerance = None if vert_tolerance_ is None else vert_tolerance_

    # create directory
    folder_dir = os.path.join(folders.default_simulation_folder, 'aperture_groups')
    if not os.path.isdir(folder_dir):
        os.makedirs(folder_dir)

    apertures = []
    room_apertures = {}
    # get all room-based apertures with Outdoors boundary condition
    for room in model.rooms:
        for face in room.faces:
            for ap in face.apertures:
                if isinstance(ap.boundary_condition, Outdoors):
                    apertures.append(ap)
                    if not room.identifier in room_apertures:
                        room_apertures[room.identifier] = {}
                    if not 'apertures' in room_apertures[room.identifier]:
                        room_apertures[room.identifier]['apertures'] = \
                            [ap]
                    else:
                        room_apertures[room.identifier]['apertures'].append(ap)
                    if not 'display_name' in room_apertures[room.identifier]:
                        room_apertures[room.identifier]['display_name'] = \
                            room.display_name
    assert len(apertures) != 0, \
        'Found no apertures. There should at least be one aperture ' \
        'in your model.'

    if view_factor:
        # write octree
        model_content, modifier_content = model.to.rad(model, minimal=True)
        scene_file, mat_file = 'scene.rad', 'scene.mat'
        write_to_file_by_name(folder_dir, scene_file, model_content)
        write_to_file_by_name(folder_dir, mat_file, modifier_content)
        
        octree = 'scene.oct'
        oconv = Oconv(inputs=[mat_file, scene_file], output=octree)
        oconv.options.f = True
        
        # run Oconv command
        env = None
        if rad_folders.env != {}:
            env = rad_folders.env
        env = dict(os.environ, **env) if env else None
        oconv.run(env, cwd=folder_dir)
        
        rflux_sky = SkyDome()
        rflux_sky = rflux_sky.to_file(folder_dir, name='rflux_sky.sky')
        
        # calculate view factor
        mtx_file, ap_dict = _aperture_view_factor(
            folder_dir, apertures, size=size, ambient_division=1000,
            receiver=rflux_sky, octree=octree, calc_folder=folder_dir
        )
        rmse = _aperture_view_factor_postprocess(
            mtx_file, ap_dict, room_apertures, room_based
        )

    # cluster apertures into groups
    if view_factor:
        ap_groups = cluster_view_factor(
            rmse, room_apertures, apertures, 0.001, room_based, vertical_tolerance)
    else:
        ap_groups = cluster_orientation(
            room_apertures, apertures, room_based, vertical_tolerance
        )

    # process clusters
    group_names, group_dict = \
        cluster_output(ap_groups, room_apertures, room_based)

    # write aperture groups to JSON file
    dyn_gr = os.path.join(folder_dir, 'aperture_groups.json')
    with open(dyn_gr, 'w') as fp:
        json.dump(group_names, fp, indent=2)

    # write dynamic group identifiers to JSON file
    dyn_gr_ids = os.path.join(folder_dir, 'dynamic_group_identifiers.json')
    with open(dyn_gr_ids, 'w') as fp:
        json.dump(group_dict, fp, indent=2)

    # assign dynamic group identifiers for each aperture
    for room in model.rooms:
        for face in room.faces:
            for ap in face.apertures:
                if isinstance(ap.boundary_condition, Outdoors):
                    dyn_group_id = group_dict[ap.identifier]
                    ap.properties.radiance.dynamic_group_identifier = \
                        dyn_group_id
