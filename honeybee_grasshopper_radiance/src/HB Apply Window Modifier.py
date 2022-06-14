# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply Modifier to Honeybee Apertures or glass Doors. Alternatively, it can assign
Modifiers to the child apertures of input Faces or the apertures within Room walls.
_
This component supports the assigning of different modifiers based on cardinal
orientation, provided that a list of Modifiers are input to the _mod. 
-

    Args:
        _hb_objs: Honeybee Apertures, Faces, Doors or Rooms to which the input
            _mod should be assigned. For the case of a Honeybee Room, the
            modifier will only be applied to the apertures in the the
            Room's outdoor walls. Note that, if you need to assign a modifier
            to all the skylights, glass doors, etc. of a Room, the best practice
            is to create a ModifierSet and assing that to the Room.
        _mod: A Honeybee Modifier to be applied to the input _hb_objs.
            This can also be text for a modifier to be looked up in the window
            modifier library. If an array of text or modifier objects
            are input here, different modifiers will be assigned based on
            cardinal direction, starting with north and moving clockwise.
    
    Returns:
        hb_objs: The input honeybee objects with their modifiers edited.
"""

ghenv.Component.Name = 'HB Apply Window Modifier'
ghenv.Component.NickName = 'ApplyWindowMod'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '6'


try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.facetype import Wall
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


def is_exterior_wall(face):
    """Check whether a given Face is an exterior Wall."""
    return isinstance(face.boundary_condition, Outdoors) and \
        isinstance(face.type, Wall)


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # process the input modifiers
    for i, constr in enumerate(_mod):
        if isinstance(constr, str):
            _mod[i] = modifier_by_identifier(constr)

    # error message for unrecognized object
    error_msg = 'Input _hb_objs must be a Room, Face, Aperture, or Door. Not {}.'

    # assign the modifiers
    if len(_mod) == 1:  # assign indiscriminately, even if it's a horizontal object
        for obj in hb_objs:
            if isinstance(obj, (Aperture, Door)):
                obj.properties.radiance.modifier = _mod[0]
            elif isinstance(obj, Face):
                for ap in obj.apertures:
                    ap.properties.radiance.modifier = _mod[0]
            elif isinstance(obj, Room):
                for face in obj.faces:
                    if is_exterior_wall(face):
                        for ap in face.apertures:
                            ap.properties.radiance.modifier = _mod[0]
            else:
                raise TypeError(error_msg.format(type(obj)))
    else:  # assign modifiers only to non-horizontal objects based on cardinal direction
        angles = angles_from_num_orient(len(_mod))
        for obj in hb_objs:
            if isinstance(obj, (Aperture, Door)):
                orient_i = face_orient_index(obj, angles)
                if orient_i is not None:
                    obj.properties.radiance.modifier = _mod[orient_i]
            elif isinstance(obj, Face):
                orient_i = face_orient_index(obj, angles)
                if orient_i is not None:
                    for ap in obj.apertures:
                        ap.properties.radiance.modifier = _mod[orient_i]
            elif isinstance(obj, Room):
                 for face in obj.faces:
                     if is_exterior_wall(face):
                         orient_i = face_orient_index(face, angles)
                         if orient_i is not None:
                            for ap in face.apertures:
                                ap.properties.radiance.modifier = _mod[orient_i]
            else:
                raise TypeError(error_msg.format(type(obj)))

