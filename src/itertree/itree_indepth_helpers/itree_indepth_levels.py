import sys
from collections import deque
from ..itree_helpers import ITER,itree_list

DOWN = ITER.DOWN
UP = ITER.UP
REVERSE = ITER.REVERSE
SELF = ITER.SELF
FILTER_ANY = ITER.FILTER_ANY
MULTIPLE=ITER.MULTIPLE

iter_list = list if sys.version_info >= (3, 8) else deque  # from Python 3.8 on lists are quicker then deque

class _iTreeIndepthLevels():

    @staticmethod
    def _levels_get_level_list(self,stop):
        """
        helper method that generates a list of lists of items for each level
        :param itree: root item that should be used
        :param stop: stop at a specific level (optimization)
        :return:
        """
        itree=self._itree
        level_items=itree_list([itree]) # slicing on blists is quicker as for normal lists!
        if stop is None:
            iterators = iter_list((itree.__iter__(),))
            while iterators:
                for item in iterators[-1]:
                    index = len(iterators)
                    l = len(level_items)
                    if index >= l:
                        for _ in range((l + 1 - index)):
                            level_items.append([])
                    level_items[index].append(item)
                    if item:
                        iterators.append(item.__iter__())
                        break
                else:  # for loop is finished and not broken
                    del iterators[-1]
        elif stop>1:
            iterators = iter_list((itree.__iter__(),))
            while iterators:
                for item in iterators[-1]:
                    index=len(iterators)
                    l=len(level_items)
                    if index>=l:
                        for _ in range((l+1-index)):
                            level_items.append([])
                    level_items[index].append(item)
                    if item and index<stop:
                        iterators.append(item.__iter__())
                        break
                else:  # for loop is finished and not broken
                    del iterators[-1]
        return level_items

    def _levels_via_siblings_iterable(self,levels,options):
        """
        helper levels iterable generator for not optimized iterations based on siblings()

        The method tries to find sections with slices in the iterable to optimize the behavior
        :param levels: iterable levels
        :param options: options flags given to the siblings method
        :return:
        """
        last_level=-1
        start_level=None
        for level in levels:
            if last_level+1==level:
                last_level=level
                if start_level is None:
                    start_level=level
                continue
            elif start_level is None:
                for item in self.siblings(level, options):
                    yield item
            else:
                if start_level==last_level:
                    for item in self.siblings(last_level, options):
                        yield item
                else:
                    if last_level>start_level:
                        step=1
                    else:
                        step=-1
                    for i in self.levels(slice(start_level,last_level,step)):
                        yield i
                start_level=None
                for item in self.siblings(level, options):
                    yield item
        if start_level is not None:
            if start_level == last_level:
                for item in self.siblings(last_level, options):
                    yield item
            else:
                if last_level > start_level:
                    step = 1
                else:
                    step = -1
                for i in self.levels(slice(start_level, last_level, step)):
                    yield i
