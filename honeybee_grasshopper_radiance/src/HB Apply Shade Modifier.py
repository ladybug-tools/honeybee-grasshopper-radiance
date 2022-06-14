# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply a Modifier to Honeybee Shade objects. Alternatively, it can assign a Modifier
to all of the child shades of an Aperture, Door, Face, or a Room.
_
This component supports the assigning of different modifiers based on cardinal
orientation, provided that a list of Modifiers are input to the _mod. 
-

    Args:
        _hb_objs: Honeybee Shades, Apertures, Doors, Faces, or Rooms to which the
            input _mod should be assigned. For the case of a Honeybee Aperture,
            Door, Face or Room, the Modifier will be assigned to only the
            child shades directly assigned to that object. So passing in a Room
            will not change the modifier of shades assigned to Apertures
            of the Room's Faces. If this is the desired outcome, then the Room
            should be deconstructed into its child objects before using
            this component.
        _mod: A Honeybee Modifier to be applied to the input _hb_objs.
            This can also be text for a modifier to be looked up in the shade
            modifier library. If an array of text or modifier objects
            are input here, different modifiers will be assigned based on
            cardinal direction, starting with north and moving clockwise.
    
    Returns:
        hb_objs: The input honeybee objects with their modifiers edited.
"""

ghenv.Component.Name = 'HB Apply Shade Modifier'
ghenv.Component.NickName = 'ApplyShadeMod'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '6'


try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.shade import Shade
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.orientation import angles_from_num_orient, face_orient_index
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # process the input modifiers
    for i, mod in enumerate(_mod):
        if isinstance(mod, str):
            _mod[i] = modifier_by_identifier(mod)

    # error message for unrecognized object
    error_msg = 'Input _hb_objs must be a Room, Face, Aperture, Door, or Shade. Not {}.'

    # assign the modifiers
    if len(_mod) == 1:
        for obj in hb_objs:
            if isinstance(obj, Shade):
                obj.properties.radiance.modifier = _mod[0]
            elif isinstance(obj, (Aperture, Face, Room, Door)):
                for shd in obj.shades:
                    shd.properties.radiance.modifier = _mod[0]
            else:
                raise TypeError(error_msg.format(type(obj)))
    else:  # assign modifiers based on cardinal direction
        angles = angles_from_num_orient(len(_mod))
        for obj in hb_objs:
            if isinstance(obj, (Aperture, Face, Door)):
                orient_i = face_orient_index(obj, angles)
                if orient_i is not None:
                    for shd in obj.shades:
                        shd.properties.radiance.modifier = _mod[orient_i]
            elif isinstance(obj, Shade):
                obj.properties.radiance.modifier = _mod[0]
            elif isinstance(obj, Room):
                 for shd in obj.shades:
                    shd.properties.radiance.modifier = _mod[0]
            else:
                raise TypeError(error_msg.format(type(obj)))

