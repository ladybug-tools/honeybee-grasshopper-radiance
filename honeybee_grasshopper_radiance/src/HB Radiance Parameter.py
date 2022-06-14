# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get recommended Radiance parameters given a recipe type and a level of detail.
_
The original recommendation for the various Radiance paramters comes from this document.
http://radsite.lbl.gov/radiance/refer/Notes/rpict_options.html
_
This presentation by John Mardaljevic gives a good overview of the meaning of each
radiance paramter.
http://radiance-online.org/community/workshops/2011-berkeley-ca/presentations/day1/JM_AmbientCalculation.pdf

-
    Args:
        _recipe_type: An integer or text for the type of recipe. Acceptable text inputs are
            either the full text of the recipe type (eg. point-in-time-grid) or
            the name of the Radiance command for which the parameters are being
            used (eg. rtrace). Choose from the following options.
                * 0 | rtrace     | point-in-time-grid | daylight-factor
                * 1 | rpict      | point-in-time-view
                * 2 | rfluxmtx   | annual
        _detail_level_: An integer or text for the level of detail/quality for which
            radiance parameters will be output. (Default: 0 for low).
            Choose from the following options.
                * 0 | low
                * 1 | medium
                * 2 | high
        additional_par_: Text to override the Radiance parameters as needed. Radiance's
            standard syntax must be followed (e.g. -ps 1 -lw 0.01).

    Returns:
        rad_par: Radiance parameters as a text string. These can be plugged into the
            radiance_par_ input of the various recipes.
"""

ghenv.Component.Name = 'HB Radiance Parameter'
ghenv.Component.NickName = 'RadPar'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '3 :: Recipes'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

try:  # import honeybee_radiance_command dependencies
    from honeybee_radiance_command.options.rtrace import RtraceOptions
    from honeybee_radiance_command.options.rpict import RpictOptions
    from honeybee_radiance_command.options.rfluxmtx import RfluxmtxOptions
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance_command:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, recipe_result
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionaries of the various recommendations for radiance parameters
RTRACE = {
    'ab': [2, 3, 6],
    'ad': [512, 2048, 4096],
    'as_': [128, 2048, 4096],
    'ar': [16, 64, 128],
    'aa': [.25, .2, .1],
    'dj': [0, .5, 1],
    'ds': [.5, .25, .05],
    'dt': [.5, .25, .15],
    'dc': [.25, .5, .75],
    'dr': [0, 1, 3],
    'dp': [64, 256, 512],
    'st': [.85, .5, .15],
    'lr': [4, 6, 8],
    'lw': [.05, .01, .005],
    'ss': [0, .7, 1]
}

RPICT = {
    'ab': [2, 3, 6],
    'ad': [512, 2048, 4096],
    'as_': [128, 2048, 4096],
    'ar': [16, 64, 128],
    'aa': [.25, .2, .1],
    'ps': [8, 4, 2],
    'pt': [.15, .10, .05],
    'pj': [.6, .9, .9],
    'dj': [0, .5, 1],
    'ds': [.5, .25, .05],
    'dt': [.5, .25, .15],
    'dc': [.25, .5, .75],
    'dr': [0, 1, 3],
    'dp': [64, 256, 512],
    'st': [.85, .5, .15],
    'lr': [4, 6, 8],
    'lw': [.05, .01, .005],
    'ss': [0, .7, 1]
}

RFLUXMTX = {
    'ab': [3, 5, 6],
    'ad': [5000, 15000, 25000],
    'as_': [128, 2048, 4096],
    'ds': [.5, .25, .05],
    'dt': [.5, .25, .15],
    'dc': [.25, .5, .75],
    'dr': [0, 1, 3],
    'dp': [64, 256, 512],
    'st': [.85, .5, .15],
    'lr': [4, 6, 8],
    'lw': [0.000002, 6.67E-07, 4E-07],
    'ss': [0, .7, 1],
    'c': [1, 1, 1]
}


# dictionaries to convert between input formats
RECIPE_TYPES = {
    '0': 'rtrace',
    'point-in-time-grid': 'rtrace',
    'daylight-factor': 'rtrace',
    'rtrace': 'rtrace',
    '1': 'rpict',
    'point-in-time-image': 'rpict',
    'rpict': 'rpict',
    '2': 'rfluxmtx',
    'annual': 'rfluxmtx',
    'rfluxmtx': 'rfluxmtx',
}

DETAIL_LEVELS = {
    '0': 0,
    'low': 0,
    '1': 1,
    'medium': 1,
    '2': 2,
    'high': 2
}


if all_required_inputs(ghenv.Component):
    # process the recipe type and level of detail
    _detail_level_ = DETAIL_LEVELS[_detail_level_.lower()] \
        if _detail_level_ is not None else 0
    command_name = RECIPE_TYPES[_recipe_type.lower()]
    if command_name == 'rtrace':
        option_dict = RTRACE
        option_obj = RtraceOptions()
    elif command_name == 'rpict':
        option_dict = RPICT
        option_obj = RpictOptions()
    elif command_name == 'rfluxmtx':
        option_dict = RFLUXMTX
        option_obj = RfluxmtxOptions()

    # assign the defualts to the object and output the string
    for opt_name, opt_val in option_dict.items():
        setattr(option_obj, opt_name, opt_val[_detail_level_])
    if additional_par_:
        option_obj.update_from_string(additional_par_)
    rad_par = option_obj.to_radiance()
