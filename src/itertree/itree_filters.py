"""
This code is taken from the itertree package:
  _ _____ _____ _____ _____ _____ _____ _____
 | |_   _|   __| __  |_   _| __  |   __|   __|
 |-| | | |   __|    -| | | |    -|   __|   __|
 |_| |_| |_____|__|__| |_| |__|__|_____|_____|

https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license
For more information see: https://en.wikipedia.org/wiki/MIT_License

CONTENT DESCRIPTION:

This part of code contains the iTree filter classes

we use here lambda to create a method which is feed with an item and delivers then True/False depending on
the given condition so that it can be used in filter iterators

"""

from __future__ import absolute_import
import contextlib
import fnmatch
from operator import or_, and_

try:
    import numpy as np
except ImportError:
    np = None

import itertools
from .itree_mathsets import *

OR = or_
AND = and_

from numbers import Number


def iter_items_over_filter_method(filter_method, item_iter):
    """
    helper function that delivers an iterator of True/False based on given filter_method and the item iterator given

    :param filter_method: Item filter method
    :param item_iter: iterable where each item should be checked against the filter
    :return: iterator of True/False objects matches to filter or not
    """
    for item in item_iter:
        yield filter_method(item)


# predefined filter methods

class has_item_flags():
    """
    Check the iTree flags for match to the given flag mask

    :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

    :param flag_mask: flag mask
                      E.g. can be build like:
                      iTFLAG.READ_ONLY_TREE|iTFLAG.READ_ONLY_VALUE

    :rtype: bool
    :return:
            * True -> match
            * False -> no match
    """

    def __init__(self, flag_mask, invert=False):
        self._flag_mask = flag_mask
        self._invert = invert

    def __call__(self, item):
        return (
            (not bool(item.flags & self._flag_mask))
            if self._invert else
            bool(item.flags & self._flag_mask)
        )


class is_item_tag():
    """
    Check the iTree tag is equal to the given target_tag

    :param target_tag: tag string do not give Tag() objects here! Use Tag().tag if really required

    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """
    def __init__(self, target_tag,invert=False):
        """
        :param target_tag: tag string do not give Tag() objects here! Use Tag().tag if really required
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_tag = target_tag
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        return item.tag != self._target_tag if self._invert else item.tag == self._target_tag


class has_item_tag_fnmatch():
    """
    Check the iTree tag is matching to given fnmatch match_pattern

    :param match_pattern: str or bytes related to fnmatch pattern definitions

    """

    def __init__(self, tag_match_pattern, invert=False):
        """

        :param tag_match_pattern: str or bytes related to fnmatch pattern definitions
        """
        self._tag_match_pattern = tag_match_pattern
        self._tag_match_pattern_type = type(tag_match_pattern)
        self._invert = invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        tag = item.tag
        result=self._tag_match_pattern_type == type(tag) and fnmatch.fnmatch(tag, self._tag_match_pattern)
        return (
            not result
            if self._invert else
            result
        )


class has_item_value():
    """
    Check the iTree value is equal to given value

    :param target_value: value object that should be equal with iTree.value
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """
    def __init__(self, target_value,invert=False):
        """
        :param target_value: value object that should be equal with iTree.value
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_value = target_value
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        target_value=self._target_value
        if np is not None and type(item.value) is np.ndarray:
            try:
                if item.value.shape != target_value.shape:
                    return self._invert
            except AttributeError:
                # no numpy array to compare with
                return self._invert
            result = any(np.equal(item.value, target_value))
            return ( not result if self._invert else result)
        return  item.value != target_value if self._invert else item.value == target_value


class has_item_value_dict_value():
    """
    Check if in case the iTree value is a dict a value in the dict is equal to given value

    :param target_value: value object that should be equal with iTree.value
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """
    def __init__(self, target_value,invert=False):
        """
        :param target_value: value object that should be equal with iTree.value
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_value = target_value
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        with contextlib.suppress(Exception):
            if self._target_value in list(item.value.values()):
                return not self._invert
        return self._invert


class has_item_value_list_value():
    """
    Check if in case the iTree value is a list a value in the list is equal to given value

    :param target_value: value object that should be equal with iTree.value
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """
    def __init__(self, target_value,invert=False):
        """
        :param target_value: value object that should be equal with iTree.value
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_value = target_value
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        with contextlib.suppress(Exception):
            if self._target_value in list(item.value):
                return not self._invert
        return self._invert


class has_item_value_fnmatch():
    """
    Check if value matches to the given fnmatch pattern

    :param target_value_pattern: str or bytes related to fnmatch pattern definitions
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """
    def __init__(self, target_value_pattern,invert=False):
        """
        :param target_value_pattern: str or bytes related to fnmatch pattern definitions
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_value_pattern = target_value_pattern
        self._target_value_pattern_type = type(target_value_pattern)
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        e_value = item.value
        if type(e_value) == type(self._target_value_pattern) and fnmatch.fnmatch(e_value, self._target_value_pattern):
            return not self._invert
        return self._invert



class has_item_value_dict_value_fnmatch():
    """
    Check if in case the iTree value is a dict a value in the dict matches to the given pattern

    :param target_value_pattern: str or bytes related to fnmatch pattern definitions
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """

    def __init__(self, target_value_pattern,invert=False):
        """
        :param target_value_pattern: str or bytes related to fnmatch pattern definitions
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_value_pattern = target_value_pattern
        self._target_value_pattern_type = type(target_value_pattern)
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        e_value = item.value
        t = self._target_value_pattern_type
        pattern=self._target_value_pattern
        with contextlib.suppress(AttributeError):
            for v in e_value.values():  # dict like value
                if type(v) == t and fnmatch.fnmatch(v, pattern):
                    return not self._invert
        return self._invert


class has_item_value_list_item_fnmatch():
    """
    Check if in case the iTree value is a list a value in the list matches to the given pattern

    :param target_value_pattern: str or bytes related to fnmatch pattern definitions
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """

    def __init__(self, target_value_pattern,invert=False):
        """
        :param target_value_pattern: str or bytes related to fnmatch pattern definitions
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_value_pattern = target_value_pattern
        self._target_value_pattern_type = type(target_value_pattern)
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        e_value = item.value
        t = self._target_value_pattern_type
        pattern=self._target_value_pattern
        with contextlib.suppress(AttributeError):
            for v in e_value:  # list like value
                if type(v) == t and fnmatch.fnmatch(v, pattern):
                    return not self._invert
        return self._invert


class is_item_value_in():
    """
    Check if iTree value is in the given iTInterval object, no numeric values will be ignored

    :param target_key_interval: msetInterval object defining the range (any object that supports "in" can be used)
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True
    """
    def __init__(self, target_value_interval,invert=False):

        """
        :param target_key_interval: msetInterval object defining the range (any object that supports "in" can be used)
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True
        """
        self._target_value_interval = target_value_interval
        self._invert=invert

    def __call__(self,item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        e_value = item.value
        if isinstance(e_value, Number) and e_value in self._target_value_interval:
            return not self._invert
        return self._invert


class has_item_value_dict_value_in():
    """
    Check if in case the iTree value is a dict a value in the dict is in the given iTInterval object,
    no numeric values will be ignored

    :param target_key_interval: msetInterval object defining the range (any object that supports "in" can be used)
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True
    """
    def __init__(self, target_value_interval,invert=False):

        """
        :param target_key_interval: msetInterval object defining the range (any object that supports "in" can be used)
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True
        """
        self._target_value_interval = target_value_interval
        self._invert=invert

    def __call__(self,item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        with contextlib.suppress(AttributeError):
            for v in item.value.values():  # dict like value
                if isinstance(v, Number) and v in self._target_value_interval:
                    return not self._invert
        return self._invert


class has_item_value_list_item_in( ):
    """
    Check if in case the iTree value is a list a value in the list is in the given iTInterval object,
    non numeric values will be ignored

    :param target_key_interval: msetInterval object defining the range (any object that supports "in" can be used)
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """
    def __init__(self, target_value_interval,invert=False):

        """
        :param target_key_interval: msetInterval object defining the range (any object that supports "in" can be used)
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True
        """
        self._target_value_interval = target_value_interval
        self._invert=invert

    def __call__(self,item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """

        with contextlib.suppress(TypeError, AttributeError):
            for v in item.value:  # list like value
                if isinstance(v, Number) and v in self._target_value_interval:
                    return not self._invert
        return self._invert


class has_item_value_dict_key():
    """
    Check if in case the iTree value is a dict a key in the dict is equal with the given target_key
    no numeric values will be ignored


    :param target_key: dict key

    """

    def __init__(self, target_key, invert=False):
        """
        :param target_key:  dict key we will search in item.value dict
        """
        self._target_key = target_key
        self._invert = invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """

        with contextlib.suppress(Exception):
            return (
                self._target_key not in item.value
                if self._invert
                else self._target_key in item.value
            )
        return self._invert


class has_item_value_list_idx():
    """
    Check if in case the iTree value is a list the given target_key is lower than list length (inside)
    no numeric values will be ignored

    :param target_idx: target-index
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """
    def __init__(self, target_idx,invert=False):

        """
        :param target_idx: target-index
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True
        """
        self._target_idx = target_idx
        self._invert=invert

    def __call__(self,item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        with contextlib.suppress(Exception):
            if hasattr(item.value, 'index') and item.value[self._target_idx]:
                return not self._invert
        return self._invert


class has_item_value_dict_key_fnmatch():
    """
    Check if in case the iTree value is a dict a key in the dict matches to the given key pattern (fnmatch)
    no numeric values will be ignored

    :param target_key_pattern: str or bytes related to fnmatch pattern definitions
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """

    def __init__(self, target_key_pattern,invert=False):
        """
        :param target_key_pattern: str or bytes related to fnmatch pattern definitions
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_key_pattern = target_key_pattern
        self._target_key_pattern_type = type(target_key_pattern)
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """

        e_value = item.value
        t = self._target_key_pattern_type
        pattern = self._target_key_pattern
        with contextlib.suppress(AttributeError):
            for k in e_value.keys():  # dict like value
                if type(k) == t and fnmatch.fnmatch(k, pattern):
                    return not self._invert
        return self._invert


class has_item_value_dict_key_in():
    """
    Check if in case the iTree value is a dict a key in the dict is in the given iTInterval object range
    no numeric values will be ignored


    :param target_key_interval: msetInterval object defining the range (any object that supports "in" can be used)
    :param invert:
            * False (default) -> unchanged result
            * True -> invert the result True->False; False->True

    """
    def __init__(self, target_key_interval,invert=False):
        """
        :param target_key_interval: msetInterval object defining the range (any object that supports "in" can be used)
        :param invert:
                * False (default) -> unchanged result
                * True -> invert the result True->False; False->True

        """
        self._target_key_interval = target_key_interval
        self._invert=invert

    def __call__(self, item):
        """
        :param item: `iTree`-item to be checked against the criteria of the method (for filtering out or not)

        :rtype: bool
        :return:
                * True -> match
                * False -> no match
        """
        with contextlib.suppress(Exception):
            for k in item.value.keys():  # dict like value
                if isinstance(k, Number) and k in self._target_key_interval:
                    return not self._invert
        return self._invert
