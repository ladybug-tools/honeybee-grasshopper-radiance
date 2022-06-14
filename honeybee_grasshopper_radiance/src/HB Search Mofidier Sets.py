# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Search for available Mofidier Sets within the honeybee standards library.
-

    Args:
        keywords_: Optional keywords to be used to narrow down the output list of
            modifier sets. If nothing is input here, all available modifier sets
            will be output.
        join_words_: If False or None, this component will automatically split
            any strings of multiple keywords (spearated by spaces) into separate
            keywords for searching. This results in a greater liklihood of
            finding an item in the search but it may not be appropropriate for
            all cases. You may want to set it to True when you are searching for
            a specific phrase that includes spaces. Default: False.
    
    Returns:
        mod_sets: A list of modifier sets within the honeybee radiance
            standards library (filtered by keywords_ if they are input).
"""

ghenv.Component.Name = 'HB Search Mofidier Sets'
ghenv.Component.NickName = 'SearchModSets'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Radiance'
ghenv.Component.SubCategory = '1 :: Modifiers'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the honeybee-core dependencies
    from honeybee.search import filter_array_by_keywords
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-radiance dependencies
    from honeybee_radiance.lib.modifiersets import MODIFIER_SETS
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))


if len(keywords_) == 0:
    mod_sets = sorted(MODIFIER_SETS)
else:
    split_words = True if join_words_ is None else not join_words_
    mod_sets = sorted(filter_array_by_keywords(MODIFIER_SETS, keywords_, split_words))
