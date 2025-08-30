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

This part of code contains the access function targeting the siblings in a tree of the nested iTree structures
"""

import sys
from collections import deque
from ..itree_helpers import ITER
from .itree_indepth_levels import _iTreeIndepthLevels

DOWN = ITER.DOWN
UP = ITER.UP
REVERSE = ITER.REVERSE
SELF = ITER.SELF
FILTER_ANY = ITER.FILTER_ANY
MULTIPLE = ITER.MULTIPLE

iter_list = list if sys.version_info >= (3, 8) else deque  # from Python 3.8 on lists are quicker then deque


class _iTreeIndepthSiblings():

    @staticmethod
    def _siblings_plus(self, level, incl_self):
        """
        helper sibling generator
        Used for positive level values

        :param level: given positive level
        :param options: option flags to be considered
        :return:
        """
        if level < 0:
            return
        itree = self._itree
        iterators = iter_list((itree.__iter__(),))
        if level == 0:
            if incl_self:
                yield itree
            return
        if incl_self:
            while iterators:
                for item in iterators[-1]:
                    if len(iterators) == level:
                        yield item
                    else:
                        if item:
                            iterators.append(item.__iter__())
                            break
                else:  # for loop is finished and not broken
                    del iterators[-1]
        else:
            while iterators:
                for item in iterators[-1]:
                    if len(iterators) == level:
                        if item is not itree:
                            yield item
                    else:
                        if item:
                            iterators.append(item.__iter__())
                            break
                else:  # for loop is finished and not broken
                    del iterators[-1]

    @staticmethod
    def _siblings_plus_reverse(self, level, incl_self):
        """
        helper sibling generator
        Used for positive level values to iterated in reversed order

        :param level: given positive level
        :param options: option flags to be considered
        :return:
        """
        if level < 0:
            return
        itree = self._itree
        if level == 0:
            if incl_self:
                yield itree
            return
        iterators = iter_list((iter(reversed(itree)),))
        if incl_self:
            while iterators:
                for item in iterators[-1]:
                    if len(iterators) == level:
                        yield item
                    else:
                        if item:
                            iterators.append(iter(reversed(item)))
                            break
                else:  # for loop is finished and not broken
                    del iterators[-1]
        else:
            while iterators:
                for item in iterators[-1]:
                    if len(iterators) == level:
                        if item is not itree:
                            yield item
                    else:
                        if item:
                            iterators.append(iter(reversed(item)))
                            break
                else:  # for loop is finished and not broken
                    del iterators[-1]

    @staticmethod
    def _siblings_minus(self, level, incl_self):
        """
        helper sibling generator
        Used for negative level values

        :param level: given negative level
        :param options: option flags to be considered

        :return:
        """
        if level >= 0:
            return
        itree = self._itree
        iterator = itree.deep
        if level == -1:
            if incl_self:
                for i in iterator:
                    if not i:
                        yield i
            else:
                itree = self._itree
                for i in iterator:
                    if not i and i is not itree:
                        yield i
        else:
            empty_items = (i for i in iterator if not i)
            self_level = itree.level
            yielded_items = set()
            if incl_self:
                for item in empty_items:
                    ancestors = item.ancestors + [item]
                    l = len(ancestors)
                    if l >= self_level and l >= -level:
                        yield_item = ancestors[level]
                        if id(yield_item) not in yielded_items:
                            yield yield_item
                            yielded_items.add(id(yield_item))
            else:
                for item in empty_items:
                    ancestors = item.ancestors + [item]
                    l = len(ancestors)
                    if l >= self_level and l >= -level:
                        yield_item = ancestors[level]
                        if id(yield_item) not in yielded_items and yield_item is not itree:
                            yield yield_item
                            yielded_items.add(id(yield_item))

    @staticmethod
    def _siblings_minus_multi(self, level, incl_self):
        """
        helper sibling generator
        Used for negative level values

        :param level: given negative level
        :param options: option flags to be considered

        :return:
        """
        if level >= 0:
            return
        itree = self._itree
        iterator = itree.deep
        if level == -1:
            if incl_self:
                for i in iterator:
                    if not i:
                        yield i
            else:
                itree = self._itree
                for i in iterator:
                    if not i and i is not itree:
                        yield i
        else:
            empty_items = (i for i in iterator if not i)
            self_level = itree.level
            if incl_self:
                for item in empty_items:
                    ancestors = item.ancestors + [item]
                    l = len(ancestors)
                    if l >= self_level and l >= -level:
                        yield_item = ancestors[level]
                        yield yield_item
            else:
                for item in empty_items:
                    ancestors = item.ancestors + [item]
                    l = len(ancestors)
                    if l >= self_level and l >= -level:
                        yield_item = ancestors[level]
                        if yield_item is not itree:
                            yield yield_item

    @staticmethod
    def _siblings_minus_reverse(self, level, incl_self):
        """
        helper sibling generator
        Used for negative level values and reversed iteration order

        :param level: given positive level
        :param options: option flags to be considered
        :return:
        """
        if level >= 0:
            return
        itree = self._itree
        iterator = itree.deep.iter(options=REVERSE)
        if level == -1:
            if incl_self:
                for i in iterator:
                    if not i:
                        yield i
            else:
                itree = self._itree
                for i in iterator:
                    if not i and i is not itree:
                        yield i
        else:
            empty_items = (i for i in iterator if not i)
            self_level = itree.level
            yielded_items = set()
            if incl_self:
                for item in empty_items:
                    ancestors = item.ancestors + [item]
                    l = len(ancestors)
                    if l >= self_level and l >= -level:
                        yield_item = ancestors[level]
                        if id(yield_item) not in yielded_items:
                            yield yield_item
                            yielded_items.add(id(yield_item))
            else:
                for item in empty_items:
                    ancestors = item.ancestors + [item]
                    l = len(ancestors)
                    if l >= self_level and l >= -level:
                        yield_item = ancestors[level]
                        if id(yield_item) not in yielded_items and yield_item is not itree:
                            yield yield_item
                            yielded_items.add(id(yield_item))

    @staticmethod
    def _siblings_minus_multi_reverse(self, level, incl_self):
        """
        helper sibling generator
        Used for negative level values and reversed iteration order

        :param level: given positive level
        :param options: option flags to be considered
        :return:
        """
        if level >= 0:
            return
        itree = self._itree
        iterator = itree.deep.iter(options=REVERSE)
        if level == -1:
            if incl_self:
                for i in iterator:
                    if not i:
                        yield i
            else:
                itree = self._itree
                for i in iterator:
                    if not i and i is not itree:
                        yield i
        else:
            empty_items = (i for i in iterator if not i)
            self_level = itree.level
            if incl_self:
                for item in empty_items:
                    ancestors = item.ancestors + [item]
                    l = len(ancestors)
                    if l >= self_level and l >= -level:
                        yield_item = ancestors[level]
                        yield yield_item
            else:
                for item in empty_items:
                    ancestors = item.ancestors + [item]
                    l = len(ancestors)
                    if l >= self_level and l >= -level:
                        yield_item = ancestors[level]
                        if yield_item is not itree:
                            yield yield_item
