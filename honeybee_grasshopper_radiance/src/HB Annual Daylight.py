# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run an annual daylight study for a single model.

    Args:
        _model: A Honeybee Model for which Annual Daylight will be simulated.
            Note that this model should have grids assigned to it in order
            to produce meaningfule results.
        _wea: A Honeybee-Radiance Wea object produced from the Wea components
            that are under the the Light Sources tab.
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. Note that this is different than the
            convention used in EnergyPlus, which uses clockwise difference
            instead of counterclockwise difference. This can also be Vector
            for the direction to North.
            Default [0]
        _sensor_grids_: Data type [string]
            A list of input grid display names to simulate. If None, all grids
            within the input _model will be simulated.
            Default [None]
        sensor_count_: Data type [string]
            The maximum number of grid points per parallel execution.
            Default [200]
        radiance_parameters_: Data type [string]
            Text with the radiance parameters for ray tracing.
            Default [-ab 2]

    Returns:
        recipe: A simulation recipe that contains a simulation instructions and
            input arguments. Use the "HB Run Recipe" component to execute the
            recipe and get results.
"""

ghenv.Component.Name = 'HB Annual Daylight'
ghenv.Component.NickName = 'AnnualDaylight'
ghenv.Component.Message = '0.2.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import json
import os

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_vector2d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from ladybug.futil import preparedir, nukedir
    from ladybug.config import folders as lb_folders
    from ladybug.wea import Wea
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.model import Model
    from honeybee.config import folders as hb_folders
    from honeybee.typing import clean_rad_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


class Workflow(object):
    """Workflow class that remains the same for every type of recipe."""

    def __init__(self, workflow_json):
        self._info = workflow_json

    @property
    def owner(self):
        """Get text for workflow owner."""
        return self._info['recipe']['owner']

    @property
    def name(self):
        """Get text for workflow name."""
        return self._info['recipe']['name']

    @property
    def tag(self):
        """Get text for workflow tag."""
        return self._info['recipe']['tag']

    @property
    def path(self):
        """Get text for the local path to the workflow's YAML recipe."""
        return self._info['recipe']['path']

    @property
    def default_simulation_path(self):
        """Get text for the default directory in which the simulation is run."""
        try:
            return self._info['recipe']['default-simulation-path']
        except KeyError:
            return None

    @property
    def simulation_id(self):
        """Get text for the default simulation ID to use."""
        try:
            return self._info['recipe']['simulation-id']
        except KeyError:
            return None

    @property
    def result_file_extension(self):
        """Get text for the result file extension."""
        try:
            return self._info['recipe']['result-file-extension']
        except KeyError:
            return None

    @property
    def inputs(self):
        """Get text for formatted inputs."""
        inputs = ['  {}: {}'.format(*p) for p in self._info['inputs'].items()]
        return '\n'.join(inputs)

    @property
    def inputs_dict(self):
        """Get a dictionary for the inputs."""
        return self._info['inputs']

    def write_inputs_json(self, simulation_folder=None, indent=4):
        """Write the inputs.json file that gets passed to queenbee luigi.
        
        Args:
            simulation_folder: The full path to where the inputs.json file
                will be written and where the simulation will be run. If None
                the default_simulation_path on this Wirkflow will be used.
            indent: The indent at which the JSON will be written (Default: 4).
        """
        sim_fold = simulation_folder if simulation_folder else self.default_simulation_path
        inputs = self._info['inputs'].copy()  # avoid editing the base dictionary
        process_inputs(inputs, sim_fold)
        if self.simulation_id:
            inputs['simulation-id'] = self.simulation_id
        # write the inputs dictionary into a file
        if not os.path.isdir(sim_fold):
            preparedir(sim_fold)
        file_path = os.path.join(sim_fold, '{}-inputs.json'.format(self.name))
        with open(file_path, 'w') as fp:
            json.dump(inputs, fp, indent=indent)
        return file_path

    @staticmethod
    def process_inputs(inputs, simulation_folder):
        """A method that can be overwritten to process inputs in write_inputs_json.

        Args:
            inputs: A dictionay with the inputs of the workflows as keys.
            simulation_folder: Path to the folder in which the workflow is executed.
        """
        pass

    def ToString(self):
        return '%s:\n%s' % (self.name, self.inputs)


if all_required_inputs(ghenv.Component):
    # this part involves some checks that should be eventually integrated to Queenbee
    assert isinstance(_model, Model), \
        'Expected Honeybee Model. Got {}.'.format(type(_model))
    if len(_model.properties.radiance.sensor_grids) == 0:
        msg = 'Input _model contains no sensor grids, which will result in a ' \
            'meaningless simulation.\nMake sure that you have assigned grids to ' \
            'the Model with the "HB Assign Grids and Views" component.'
        give_warning(ghenv.Component, msg)
        print(msg)
    all_grids = [g.display_name for g in _model.properties.radiance.sensor_grids]
    if len(_sensor_grids_) == 0 or _sensor_grids_[0] is None:
        _sensor_grids_ = all_grids  # use all the Model's sensor grids
    else:
        for grid in _sensor_grids_:
            assert grid in all_grids, \
                'Sensor grid "{}" was not found in the Model.'.format(grid)
    assert isinstance(_wea, Wea), 'Expected Wea object. Got {}.'.format(type(_wea))
    try:
        north_vector = to_vector2d(north_)
        north_angle = math.degrees(north_vector.angle_clockwise(Vector2D(0, 1)))
    except AttributeError:  # north angle instead of vector
        north_angle = float(north_)

    # this part is an optional step for each recipe to process the model for luigi input
    def default_simulation_path(self):
        return os.path.join(
            hb_folders.default_simulation_folder,
            self._info['inputs']['model'].identifier, 'Radiance')

    def process_inputs(inputs, folder):
        model_fold = os.path.join(folder, 'model')
        if os.path.isdir(model_fold):
            nukedir(model_fold, rmdir=True)  # delete the folder if it already exists
        model = inputs['model']
        model.to.rad_folder(model, folder)
        inputs['model'] = 'model'
        wea = inputs['wea']
        f_name = '{}.wea'.format(clean_rad_string(wea.location.city))
        wea.write(os.path.join(folder, f_name))
        inputs['wea'] = f_name

    Workflow.default_simulation_path = property(default_simulation_path)
    Workflow.process_inputs = staticmethod(process_inputs)

    #  this part will be different for each recipe but standardized
    local_path = os.path.join(
        lb_folders.ladybug_tools_folder, 'resources', 'recipes',
        'honeybee_radiance_recipe', 'annual_daylight.yaml')
    recipe = {
        'owner': 'ladybug-tools',
        'name': 'annual-daylight',
        'tag': '9d5d49c529514f1cb3873657142233ff4cf947d52c0722875dc8cbda50c9239b',
        'path': local_path,
        'default-simulation-path': None,
        'simulation-id': 'annual_daylight',
        'result-file-extension': 'ill'
      }
    _inputs = {
        'model': _model,
        'wea': _wea,
        'north': north_angle,
        'sensor-grids': _sensor_grids_,
        'sensor-count': sensor_count_,
        'radiance-parameters': radiance_parameters_
    }

    # this part will always stay the same for every recipe
    inputs = {}
    for key, val in _inputs.items():
        if bool(val):
            inputs[key] = val
    workflow_json ={
      "recipe": recipe,
      "inputs": inputs
    }
    recipe = Workflow(workflow_json)
