# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Honeybee CustomLamp.
_
The CustomLamp can be used to set custom chromaticity, color or color temperature.
If only the _name is set a default CustomLamp of 3200K is created, unless the name
is a predefined lamp name.
-
The priority of input is from the top. This means that if, e.g., both color_temp_
and xy_cor_ are set by the user, the color temperature have priority and the CustomLamp
will be created from the color temperature.

-
    Args:
        _name: Set the name of the custom lamp. If the name is among the predefined
            list of lamp names, the lamp name will override any values in the other
            inputs.
            _
            The following lamp names are predefined. The values in parenthesis are
            the x, y 1931 chromaticity coordinates and lumen depreciation values:
                clear metal halide    (0.396, 0.39, 0.8)
                cool white            (0.376, 0.368, 0.85)
                cool white deluxe     (0.376, 0.368, 0.85)
                deluxe cool white     (0.376, 0.368, 0.85)
                deluxe warm white     (0.44, 0.403, 0.85)
                fluorescent           (0.376, 0.368, 0.85)
                halogen               (0.4234, 0.399, 1)
                incandescent          (0.453, 0.405, 0.95)
                mercury               (0.373, 0.415, 0.8)
                metal halide          (0.396, 0.39, 0.8)
                quartz                (0.424, 0.399, 1)
                sodium                (0.569, 0.421, 0.93)
                warm white            (0.44, 0.403, 0.85)
                warm white deluxe     (0.44, 0.403, 0.85)
                xenon                 (0.324, 0.324, 1)
        color_temp_: Set the color temperature in Kelvin for the lamp. This is used to
            calculate the chromaticity coordinates on the CIE 1931 xy diagram. Valid
            color temperature values are from 1000 to 25000. Will be ignored if the
            lamp name matches a predefined value.
        xy_cor_: Chromaticity coordinates for the lamp. This input must be a list
            of two values [x, y]. Will be ignored if color_temp_ is supplied. Or if
            the lamp name matches a predefined value.
        _color_space_: Color space for the chromaticity coordinates. The values and
            their corresponding color spaces are
             0 - CIE 1931 Color Space (default)
             1 - CIE 1960 Color Space
             2 - CIE 1976 Color Space
        rgb_color_: Specifiy the RGB color for the lamp. This can be a color from the
            "Colour Swatch" component or a text panel. Any alpha value of the color
            will be multiplied with the depreciation factor. Will be ignored if
            color_temp_ or xy_cor_ are supplied. Or if the lamp name matches a
            predefined value.
        _depr_fac_: A scalar multiplier applied to account for lamp lumen
            depreciation. Must be greater than 0. Default: 1.

    Returns:
        report: Reports, errors, warnings, etc.
        custom_lamp: A CustomLamp that can be plugged into a Luminaire.
"""

ghenv.Component.Name = 'HB Custom Lamp'
ghenv.Component.NickName = 'CustomLamp'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '2 :: Light Sources'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from honeybee_radiance.luminaire import Luminaire, LuminaireZone, CustomLamp, LAMPNAMES
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set defaults
    color_temp = color_temp_ or None
    x_cor, y_cor = xy_cor_ or (None, None)
    color_space = 0 if _color_space_ is None else _color_space_
    rgb_color = rgb_color_ or None
    depr_factor = 1 if _depr_fac_ is None else _depr_fac_
    
    # record inputs set by user; used for printing message
    inputs = {'_color_temp_': color_temp_, '_xy_cor_': xy_cor_, '_color_space_': _color_space_, '_rgb_color_': rgb_color_, '_depr_fac_': _depr_fac_}
    user_inputs = {k for k in inputs if inputs[k]}
    
    if _name in LAMPNAMES:
        custom_lamp = CustomLamp.from_lamp_name(_name, depreciation_factor=depr_factor)
        print('Custom lamp is a predefined lamp named "{}" with x, y chromaticity coordianes and depreciation factor: {}.'.format(_name, LAMPNAMES[_name]))
        if user_inputs:
            print('The input for _name will override the following inputs: {}.'.format(', '.join(user_inputs)))
    elif color_temp:
        custom_lamp = CustomLamp.from_color_temperature(_name, color_temp, depreciation_factor=depr_factor)
        print('Custom lamp will be defined as per the color temperature of: {}.'.format(color_temp))
        user_inputs.remove('_color_temp_')
        user_inputs.remove('_depr_fac_') if '_depr_fac_' in user_inputs else None
        if user_inputs:
            print('The input for _color_temp_ will override the following inputs: {}.'.format(', '.join(user_inputs)))
    elif x_cor and y_cor:
        custom_lamp = CustomLamp.from_xy_coordinates(_name, x_cor, y_cor, depreciation_factor=depr_factor, color_space=color_space)
        x, y, year = 'x', 'y', 1931
        if color_space == 1:
            x, y, year = 'u', 'v', 1960
        elif color_space == 2:
            x, y, year = "u'", "v'", 1976
        print('Custom lamp will be defined as per the following chromaticity coordinates : ({}, {}) = ({}, {}) for the {} CIE Color Space.'.format(x, y, x_cor, y_cor , year))
        user_inputs.remove('_xy_cor_')
        user_inputs.remove('_color_space_') if '_color_space_' in user_inputs else None
        user_inputs.remove('_depr_fac_') if '_depr_fac_' in user_inputs else None
        if user_inputs:
            print('The input for _xy_cor_ will override the following inputs: {}.'.format(', '.join(user_inputs)))
    elif rgb_color:
        custom_lamp = CustomLamp.from_rgb_colors(_name, rgb_color, depreciation_factor=depr_factor)
        print('Custom lamp will be defined as per the RGB color: {}.'.format(rgb_color))
        user_inputs.remove('_rgb_color_')
        user_inputs.remove('_depr_fac_') if '_depr_fac_' in user_inputs else None
        if user_inputs:
            print('The input for _rgb_color_ will override the following inputs: {}.'.format(', '.join(user_inputs)))
    else:
        custom_lamp = CustomLamp.from_default_white(_name, depreciation_factor=depr_factor)
        print('Custom lamp is a default lamp with color temperature of 3200K.')
