# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a WEA object using the original ASHRAE Clear Sky formula.
-

    Args:
        _location = The output from the importEPW or constructLocation component.
            This is essentially a list of text summarizing a location on the
            earth.
        clearness_: A factor that will be multiplied by the output of the model.
            This is to help account for locations where clear, dry skies predominate
            (e.g., at high elevations) or, conversely, where hazy and humid conditions
            are frequent. See Threlkeld and Jordan (1958) for recommended values.
            Typical values range from 0.95 to 1.05 and are usually never more than 1.2.
            Default is set to 1.0.
        timestep_: An integer representing the timestep with which to make the
            WEA object.  Default is set to 1 for 1 step per hour of the year.
    
    Returns:
        wea: A wea object from stat file. This wea object represents an original 
            ASHRAE Clear Sky, which is intended to determine peak solar load and
            sizing parmeters for HVAC systems.
"""

ghenv.Component.Name = 'HB ClearSky'
ghenv.Component.NickName = 'ClearSky'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.wea import Wea
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    timestep_ = 1 if timestep_ is None else timestep_
    clearness_ = 1 if clearness_ is None else clearness_
    wea = Wea.from_ashrae_clear_sky(_location, clearness_, timestep_)