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

This part of code contains the main iTree object
"""

from itertools import dropwhile, islice, chain
import sys
import warnings
import copy
from collections import deque
from .itree_helpers import ORDER_PRE, ORDER_POST, ORDER_LEVEL, ITER
from .itree_indepth_helpers.itree_indepth_iter import _iTreeIndepthIter

DOWN = ITER.DOWN
UP = ITER.UP
REVERSE = ITER.REVERSE
SELF = ITER.SELF
FILTER_ANY = ITER.FILTER_ANY
MULTIPLE=ITER.MULTIPLE

iter_list = list if sys.version_info >= (3, 8) else deque  # from Python 3.8 on lists are quicker then deque

NONE_TUPLE = (None,)


class _iTreeIndepthTree(_iTreeIndepthIter):
    __slots__ = ('_itree', 'get', '_active_iter')

    # To win some speed we set self._itree after init of the class in the main iTree object

    _ITER_HELPERS = {
        0: _iTreeIndepthIter._iter_normal,
        UP:_iTreeIndepthIter._iter_up,
        REVERSE: _iTreeIndepthIter._iter_reverse,
        UP | REVERSE: _iTreeIndepthIter._iter_up_reverse,
    }

    _ITER_IDXPATH_HELPERS = {
        0: _iTreeIndepthIter._iter_normal_idxpath,
        UP:_iTreeIndepthIter._iter_up_idxpath,
        REVERSE: _iTreeIndepthIter._iter_reverse_idxpath,
        UP | REVERSE: _iTreeIndepthIter._iter_up_reverse_idxpath,
    }

    _ITER_TAGIDXPATH_HELPERS = {
        0: _iTreeIndepthIter._iter_normal_tagidxpath,
        UP:_iTreeIndepthIter._iter_up_tagidxpath,
        REVERSE: _iTreeIndepthIter._iter_reverse_tagidxpath,
        UP | REVERSE: _iTreeIndepthIter._iter_up_reverse_tagidxpath,
    }

    def unset_tree_read_only(self, filter_method=None, hierarchical=True):
        """
        Call method via `iTree().deep.unset_tree_read_only()`

        Unset the tree protection flag on the item and all its sub-items.

        In case a filter_method is given this will always work as hierarchical filter. We cannot unset tree_read_only
        flag in a children if the flag is not unset at the parent too.

        :except: If the parent contains the tree protection flag a PermissionError will be raised

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` is given no filtering will be performed.

        :type hierarchical: bool
        :param hierarchical: Switches hierarchical filtering ON or OFF

                             * True
                                     hierarchical filtering active (if a parent does not match to the filter
                                     the children are taken out too, and they are not considered)
                             * False
                                     non-hierarchical filtering in active (all items are checked against the
                                     filter and considered in the result (even that the parent might
                                     not match to the filter))

        """
        itree = self._itree
        unset_flags = itree._unset_flags
        read_only_tree_flag = itree._READ_ONLY_TREE
        if itree._itree_prt_idx is not None and itree._itree_prt_idx[0]._flags & itree._READ_ONLY_TREE:
            raise PermissionError('The structural protection flag can only be unset in '
                                  'case the parent is not protected. But here the parent holds the protection flag')
        if filter_method:
            if filter_method(itree):
                unset_flags(itree, read_only_tree_flag)
            if hierarchical:
                iterator = self.iter(filter_method)
            else:
                # not sure if this makes sense, hi risk of denied action because of protected parents
                iterator = filter(filter_method, self)
        else:
            unset_flags(itree, read_only_tree_flag)
            iterator = self.__iter__()
        for i in iterator:
            unset_flags(i, read_only_tree_flag)

    def unset_value_read_only(self, filter_method=None, hierarchical=True):
        """
        Call via **iTree().deep.unset_value_read_only()**

        Unset the value protection flag on the item and all its sub-items.

        :except: If the parent contains the tree protection flag a PermissionError will be raised

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` is given no filtering will be performed.

        :type hierarchical: bool
        :param hierarchical: Switches hierarchical filtering ON or OFF

                             * True
                                     hierarchical filtering active (if a parent does not match to the filter
                                     the children are taken out too, and they are not considered)
                             * False
                                     non-hierarchical filtering in active (all items are checked against the
                                     filter and considered in the result (even that the parent might
                                     not match to the filter))
        """
        itree = self._itree
        read_only_value_flag = itree._READ_ONLY_VALUE
        unset_flags = itree._unset_flags
        if itree._itree_prt_idx is not None and itree._itree_prt_idx[0]._flags & itree._READ_ONLY_TREE:
            raise PermissionError('The structural protection flag can only be unset in '
                                  'case the parent is not protected. But here the parent holds the protection flag')
        if filter_method:
            if filter_method(itree):
                unset_flags(itree, read_only_value_flag)
            if hierarchical:
                iterator = self.iter(filter_method)
            else:
                iterator = filter(filter_method, self)
        else:
            unset_flags(itree, read_only_value_flag)
            iterator = self.__iter__()
        # We consume the iterator and change the flag as quick as possible
        for i in iterator:
            unset_flags(i, read_only_value_flag)

    def set_value_read_only(self, filter_method=None, hierarchical=True):
        """
        Call via **iTree().deep.set_value_read_only()**

        Set the value protection flag on the item and all its sub-items.

        :except: If the parent contains the tree protection flag a PermissionError will be raised

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` is given no filtering will be performed.

        :type hierarchical: bool
        :param hierarchical: Switches hierarchical filtering ON or OFF

                             * True
                                     hierarchical filtering active (if a parent does not match to the filter
                                     the children are taken out too, and they are not considered)
                             * False
                                     non-hierarchical filtering in active (all items are checked against the
                                     filter and considered in the result (even that the parent might
                                     not match to the filter))
        """
        itree = self._itree
        read_only_value_flag = itree._READ_ONLY_VALUE
        set_flags = itree._set_flags
        if itree._itree_prt_idx is not None and itree._itree_prt_idx[0]._flags & itree._READ_ONLY_TREE:
            raise PermissionError('The structural protection flag can only be unset in '
                                  'case the parent is not protected. But here the parent holds the protection flag')
        if filter_method:
            if filter_method(itree):
                set_flags(itree, read_only_value_flag)
            if hierarchical:
                iterator = self.iter(filter_method)
            else:
                iterator = filter(filter_method, self)
        else:
            set_flags(itree, read_only_value_flag)
            iterator = self.__iter__()
        # We consume the iterator and change the flag as quick as possible
        for i in iterator:
            set_flags(i, read_only_value_flag)

    def __len__(self):
        """
        Call via **len(iTree().deep)**

        Delivers number of all items (in-depth) inside the `iTree`-object

        :rtype: int
        :return: number of children and sub-children in `iTree`-object
        """
        return sum(1 for _ in self)

    def __lt__(self, other):
        """
        Call via **iTree().deep<other.deep**

        less than is a size comparison (length are compared)

        :type other: iTree
        :param other: iTree object self should be compared with

        :rtype: bool
        :return: True/False
        """
        return self.__len__() < len(other)

    def __le__(self, other):
        """
        Call via **iTree().deep<=other.deep**

        less than or equal is a size comparison (length are compared)

        :type other: iTree
        :param other: iTree object self should be compared with

        :rtype: bool
        :return: True/False
        """
        return self.__len__() <= len(other)

    def __gt__(self, other):
        """
        Call via **iTree().deep>other.deep**

        greater than is a size comparison (length are compared)

        :type other: iTree
        :param other: iTree object self should be compared with

        :rtype: bool
        :return: True/False
        """
        return self.__len__() > len(other)

    def __ge__(self, other):
        """
        Call via **iTree().deep>=other.deep**

        greater than or equal is a size comparison (length are compared)

        :type other: iTree
        :param other: iTree object self should be compared with

        :rtype: bool
        :return: True/False
        """
        return self.__len__() >= len(other)

    def count(self, item):
        """
        Call via **iTree().deep.count()**`

        Counts (in-depth) how many equal (`==`) items are inside the `iTree`-object.

        :type item: iTree
        :param item: The `iTree`-items will be compared with this item

        :rtype: int
        :return: Number of matching items found
        """
        return sum(item == i for i in self)

    def filtered_len(self, filter_method, hierarcical=True):
        """
        Call via **iTree().deep.filtered_len()**`

        Calculates in-depth the number of filtered items.

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches (see :ref:`filter_method <filter_method>`)
        :type hierarchical: bool
        :param hierarchical:

                            * True - hierarchical filtering if a parent does not match to the filter
                                      the children are taken out too, and they are not considered
                            * False - non-hierarchical filtering (all items are checked against the
                                      filter and considered in the result)


        :rtype: int
        :return: Number of matching items found
        """
        if hierarcical:
            return sum(1 for _ in self.iter(filter_method))
        else:
            return sum(1 for _ in filter(filter_method, self))

    def __contains__(self, item):
        """
        Call via **x in iTree().deep**

        Checks if given ´iTree´ is child or sub-child of the ´iTree´ (inside).
        For comparison == -> ´__eq__()´ is used. For finding the exact object instance
        use ´is_in()´ instead.

        :type item: iTree
        :param item: iTree object to be searched for
        :rtype: bool
        :return:
                * True - matching child is found
                * False - no matching item found
        """
        if not hasattr(item, '_itree_prt_idx'):
            return False
        try:
            next(dropwhile(lambda i: i != item, self))
            return True
        except StopIteration:
            return False

    def is_tag_in(self, tag):
        """
        Call via **iTree().deep.is_tag_in()**

        Checks if a iTree contains the given family-tag (in_depth (all levels))
        :param tag: family tag
        :return: True/False
        """
        for i in self:  # iter over all items
            if i.is_tag_in(tag):
                return True
        return False

    def is_in(self, item):
        """
        Call via **iTree().deep.is_in()**

        Checks if the given object is in thee iTree.
        Different to ´__contains__()´ we check here for the instance (specific) object (`is`)
        and not based on ´__eq__()´.

        :type item: iTree
        :param item: iTree object to be searched for
        :rtype: bool
        :return:
                * True - matching child is found
                * False - no matching item found
        """
        # search is done based on parents:
        itree = self._itree
        p = item._itree_prt_idx is not None and item._itree_prt_idx[0] or None
        while p is not None:
            if p is itree:
                return True
            p = p._itree_prt_idx is not None and p._itree_prt_idx[0] or None
        return False

    def index(self, item, start=None, stop=None):
        """
        Call via **iTree().deep.index()**

        The index method allows to search for the index_path of a matching item in the `iTree`.
        The item must be a iTree object and the index will deliver the first match. The comparison is made via
        `==` operator.

        .. warning:: If the user gives the `start` or `stop` argument not as an `iTree`-item but as a `target_path` he
                     must give a list (or iterable) for
                     targeting each level in the tree! The arguments are interpreted as the
                     arguments for `iTree.get()`.

                     This means if the user targets an element in first level by an absolute index he must give it as
                     `index(item,[index])` giving just the integer value will not work in this case!

        If item is not found a IndexError will be raised

        .. note:: To get the index of a specific item instance in his parent tree the `.idx_path`- property
                  should be used.

        :type item: iTree
        :param item: iTree object to be searched for

        :type start: Union[iTree,target_path]
        :param start: iTree item or start target_path where index search should be started (start item is included in search)

        :type stop: Union[iTree,target_path]
        :param stop: iTree item or stop target_path  where index search should be stopped (stop item is not included in search)

        ;rtype: list
        :return: index_path of the found item
        """
        itree = self._itree
        if itree:
            s = len(itree.idx_path)
            iterator = self.__iter__()
            if start is not None:
                if not hasattr(start, '_itree_prt_idx'):
                    start = self._itree.get.single(*start)
                try:
                    first_item = next(dropwhile(lambda i: i is not start, iterator))
                    if first_item == item:
                        return first_item.idx_path[s:]
                except StopIteration:
                    raise IndexError('No matching item found')
            if stop is not None:
                if not hasattr(stop, '_itree_prt_idx'):
                    stop = self._itree.get.single(*stop)
                try:
                    item = next(dropwhile(lambda i: i is not stop and i != item, iterator))
                    if item is not stop:
                        return item.idx_path[s:]
                    raise StopIteration
                except StopIteration:
                    raise IndexError('No matching item found')
            else:
                try:
                    item = next(dropwhile(lambda i: i != item, iterator))
                    return item.idx_path[s:]
                except StopIteration:
                    raise IndexError('No matching item found')

    def reverse(self):
        """
        Call via **iTree().deep.reverse()**

        In-depth reverse of the order of all children in the `iTree`. Same as method `reverse()`
        but this is the in-depth version
        of the
        method. This method dives deeper and the sub-children, sub-sub-children, ... orders are reversed too.

        .. note:: The implementation of this method is recursive for deep trees recursion limit might be reached.
        """
        itree = self._itree
        flags = itree._flags
        if flags & itree._IS_TREE_PROTECTED:
            if not itree.is_link_root or itree._link.is_loaded:
                itree._raise_read_only_exception(itree)
        else:
            if itree:
                itree._items.reverse()
                for family in itree._families.values():
                    family.reverse()
                for i in itree:
                    i.deep.reverse()

    def sort(self, key=None, reverse=False):
        """
        Call via **iTree().deep.sort()**

        sort operation running also over the deeper levels of the tree
        -> same behavior as sort of lists (parameter description is taken from list documentation)

        In this operation internally a copied sorted list is created, the structure is cleared and rebuild
        based on the sorted list. The default-operation is to the sort based on the list of keys (tag-family.family_index)
        pair of the items. This might be modified by changing the target_type.

        .. Warning:: In case of really deep `iTree`s (depth >100) the sorting might take a lot of time.
                     We made a test with an `iTree` containing ~2500 items and a depth of 9000. Result was:
                     `itree.all.sort() time: 83.772834 s` (Python 3.9).

        .. note:: The implementation of this method is recursive for deep trees recursion limit might be reached.

        :param key:  specifies a function of one argument that is used to extract a comparison key
                     from each list element (for example, key=str.lower). The key corresponding to each item in
                     the list is calculated once and then used for the entire sorting process.
                     The default value of None means that list items are sorted directly without calculating
                     a separate key value.

        :param reverse: is a boolean value. If set to True, then the list elements are sorted
                        as if each comparison were reversed.

        """
        itree = self._itree
        flags = itree._flags
        if flags & itree._IS_TREE_PROTECTED:
            if not itree.is_link_root or itree._link.is_loaded:
                itree._raise_read_only_exception(itree)
        else:
            itree.sort(key=key, reverse=reverse)
            for i in itree:
                i.deep.sort(key, reverse)

    def remove(self, *target_path):
        """
        Call via **iTree().deep.remove()**

        In-depth remove multiple items in specific level defined by given `target_path`. The target items are
        collected internally via the `iTree.get()` (have a look on this related function to understand how
        you can select the to be removed items.

        :except: In case a parent is protected (e.g. read_only) the related exception will be raised (a part of the operation might be already executed in this case)

        :type *target_path: Iterable
        :param *target_path:  iterable of targets for the different levels
                                The supported targets in each level are (same like `__getitem__()`:
                                   * *index* - absolute target index integer (fastest operation)
                                   * *key* - key tuple (family_tag, family_index)
                                   * *index-slice* - slice of absolute indexes
                                   * *key-index-slice* - tuple of (family_tag, family_index_slice)
                                   * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                                   * *key-index-list* - tuple of (family_tag, family_index_list)
                                   * *tag* - family_tag object targeting a whole family
                                   * *tag-set* - a set of family-tags targeting the items of multiple families
                                   * *itree_filter* - method (callable) for filtering the children of the object
                                   * *iter* - if build-in `iter` a list of all children will be given (same like `__iter__()`)

        :rtype: Union[iTree,list]
        :return: In case only a single item is targeted the deleted object will be returned. If we have multiple items
                 a list of the deleted objects will be delivered
        """

        del_items = self._itree.get(*target_path)
        if hasattr(del_items, '_itree_prt_idx'):
            # single result
            return del_items.parent.pop(del_items.idx)
        for i in del_items:
            i.parent.remove(i)
        return del_items

    def __iter__(self):
        """
        Call via: **iter(iTree().deep)**

        In-depth generator (iterator) which iterates over all nested items of `iTree` top -> down direction

        :rtype: Generator
        :return: iterator over all ìTree`-items
        """
        if self._itree:
            iterators = iter_list((self._itree.__iter__(),))
            while iterators:
                for item in iterators[-1]:
                    yield item
                    if item:
                        iterators.append(item.__iter__())
                        break
                else:  # for loop is finished and not broken
                    del iterators[-1]


    def iter(self, filter_method=None, options=DOWN, up_to_low=None):
        """

        In-depth iterator that iterates over all items in the nested `iTree`-structure. The iterator flattens the
        nested structure. In an instanced `iTree`-object the method is reached via: **iTree().deep.iter()**.

        The way we iterate depends on the given iteration options (combine options with | (OR bit operator)):

            * ITER.UP - Iteration will be made bottom->up (from the deepest items to the root),
              The default iteration direction is top -> down

            * ITER.REVERSE - The children of a item are iterated in the reversed direction (high index -> zero index).
              The default iteration direction for the children is zero index ->o highest index)

            * ITER.SELF - In the iteration the calling object (self) will be included.
              The default is that the calling object is not part of the iteration

            * ITER.FILTER_ANY - This flag has effect if a filter_method is given. It enables the pythons
              build_in `filter()` on any iterated object. The default is a hierarchical filtering.

        Other iteration flags are not supported by this function

        .. note:: The call `for item in mytree.deep.iter():` is same as `for i in mytree.deep`. Calling `iter() `
                  without parameters is same as `__iter__()'.

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` (default) is given no filtering will be performed.

        :type option: int
        :param option: Supported iteration options:
                       ITER.UP | ITER.REVERSE | ITER.SELF | ITER.FILTER_ANY

        :rtype: Generator
        :return: iterator over all nested ìTree`-items
        """
        # for downward compatibility:
        # the option: ITER.DOWN is ignored because this is the default behavior.
        # ITER.DOWN exists only for downward compatibility
        if options == 0:
            options = options | UP
        if up_to_low is not None:
            if not up_to_low:
                options = options | UP
            warnings.warn(
                "The parameter up_to_low will be removed soon. Use options=ITER.UP instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        if ITER.valid_option(UP | DOWN | REVERSE | SELF | FILTER_ANY):
            raise AttributeError(ITER.valid_option(options))
        if options & FILTER_ANY:
            if filter_method:
                return filter(filter_method, self._ITER_HELPERS[options & (UP | REVERSE)](self,None, options & SELF))
            else:
                return self._ITER_HELPERS[options & (UP | REVERSE)](self, None, options & SELF)
        else:
            return self._ITER_HELPERS[options & (UP | REVERSE)](self,filter_method, options & SELF)

    def siblings(self, level, options=0):
        """
        Call via **iTree().deep.siblings()**

        This generator iterates over all siblings in the targeted level in the calling item.

        The way we iterate depends on the given iteration options (combine options with | (OR bit operator)):

            * ITER.REVERSE - The item in the level will be iterated  in the reversed direction (high index -> low index).
              The default iteration direction  is low index ->o highest index)

            * ITER.SELF - In the iteration the calling object (self) will be included.
              The default is that the calling object is not part of the iteration

            * ITER.MULTIPLE - allows multiple matches of one item during the iteration 
                              (can happen in case of negative level values)

        Other iteration flags are not supported by this method. For better understanding we recommend
        the related section in the tutorial where the behavior is explained in diagrams.

        .. note :: The method supports negative target levels. In this case the iteration might not stay in same
                   absolute level! (e.g. The  call `mytree.deep.siblings(-1)` will deliver all ending items (no children)
                   of mytree. In case the branches inside mytree have different depth the iteration will step in
                   the related positive levels up and down. In case of the iteration finds same item again it will not
                   be delivered again in the resulting generator (a sibling will be considered only one
                   time during the iteration).


        :type level: int
        :param level: target level. The target level can be negative too.

        :type option: int
        :param option: Supported iteration options: ITER.REVERSE | ITER.SELF | ITER.MULTIPLE

        :rtype: Generator
        :return: iterator over specif level of the tree
        """
        if ITER.valid_option(options, REVERSE | SELF|MULTIPLE):
            raise AttributeError(ITER.valid_option(options))
        if level < 0:
            return self._SIBLINGS_MINUS_HELPERS[options & (MULTIPLE | REVERSE)](self,level, options & SELF)
        else:
            return self._SIBLINGS_PLUS_HELPERS[options & (MULTIPLE | REVERSE)](self,level, options & SELF)

    def levels(self, levels=slice(0, None, 1), options=0):
        """
        Multilevel iteration generator. This method iterates over the items level by level based on the given levels.

        As options the user can give:

            * ITER.SELF - the calling object itself will be included, by default it is excluded

            * ITER.REVERSE - Go from high to low index per level

            * ITER.MULTIPLE - Allows that one item can be iterated multiple times
                              (especially in case of negative levels this is possible)


        .. note:: In general the method behaves like the siblings method executed on multiple levels.
                  ::
                        def levels(levels, options):
                            for level in levels:
                                for item in siblings(level,options)
                                    yield item

                  Different to the shown replacement function the level function is optimized and should be quicker
                  compared to the shown code. Especially if the user give `slices` of levels (which is possible too).

        .. note:: In case a list or iterable of levels is given and level values are repeated (e.g. `levels = [1,1,1]`)
                  This generator function will iterate multiple times over the level items. But without the flag,
                  ITER.MULTIPLE an already yielded item will not be repeated!


        :type levels: Union(Iterable,Slice)
        :param levels: Iterable of level values (each item must be an integer). If slices are given they are
                             translated in a loop with related `range()` parameters.

        :type options: int
        :param options:  ITER option flags, possible values are ITER.SELF|ITER.REVERSE|ITER.MULTIPLE
        :return: Iteration generator
        """
        if ITER.valid_option(options, REVERSE | SELF|MULTIPLE):
            raise AttributeError(ITER.valid_option(options))
        if type(levels) is slice:
            if levels==slice(None,None,None):
                return
            start = levels.start
            stop = levels.stop
            if start is None:
                start=0
            step = levels.step
            if step is None:
                step=1
            cnt = start
            if stop is None:
                stop_items = set()
            else:
                stop_items = {id(i) for i in self.siblings(stop, options)}
            itree = self._itree
            siblings = self.siblings(start, options)
            yielded_items = set()
            if step > 0:
                if options & SELF:
                    if options & MULTIPLE:
                        items_found = True
                        modulo_ok = True
                        while items_found:
                            items_found = (cnt == start)
                            for item in siblings:
                                items_found = True
                                item_id = id(item)
                                if item_id in stop_items:
                                    if item:
                                        stop_items.update({id(i) for i in item})
                                elif modulo_ok:
                                    yield item
                                if not item:
                                    stop_items.add(item_id)
                            cnt = cnt + 1
                            modulo_ok = not ((cnt - start) % step)
                            siblings = self.siblings(cnt, options)
                    else:
                        items_found = True
                        modulo_ok = True
                        while items_found:
                            items_found = (cnt == start)
                            for item in siblings:
                                items_found = True
                                item_id = id(item)
                                if item_id in stop_items:
                                    if item:
                                        stop_items.update({id(i) for i in item})
                                elif modulo_ok and item_id not in yielded_items:
                                    yield item
                                    yielded_items.add(id(item))
                                if not item:
                                    stop_items.add(item_id)
                            cnt = cnt + 1
                            modulo_ok = not ((cnt - start) % step)
                            siblings = self.siblings(cnt, options)
                else:
                    if options & MULTIPLE:
                        items_found = True
                        modulo_ok = True
                        while items_found:
                            items_found = (cnt == start)
                            for item in siblings:
                                items_found = True
                                item_id = id(item)
                                if item_id in stop_items:
                                    if item:
                                        stop_items.update({id(i) for i in item})
                                elif modulo_ok and item is not itree:
                                    yield item
                                if not item:
                                    stop_items.add(item_id)
                        cnt = cnt + 1
                        modulo_ok = not ((cnt - start) % step)
                        siblings = self.siblings(cnt, options)
                    else:
                        yielded_items.add(id(itree))
                        items_found = True
                        modulo_ok = True
                        while items_found:
                            items_found = (cnt == start)
                            for item in siblings:
                                items_found = True
                                item_id = id(item)
                                if item_id in stop_items:
                                    if item:
                                        stop_items.update({id(i) for i in item})
                                elif modulo_ok and item_id not in yielded_items:
                                    yield item
                                    yielded_items.add(id(item))
                                if not item:
                                    stop_items.add(item_id)
                            cnt = cnt + 1
                            modulo_ok = not ((cnt - start) % step)
                            siblings = self.siblings(cnt, options)
            else:
                if options & SELF:
                    if options & MULTIPLE:
                        if itree.parent:
                            stop_items.add(itree.parent)
                        items_found=True
                        modulo_ok =True
                        while items_found:
                            items_found=(cnt==start)
                            for item in siblings:
                                items_found = True
                                item_id = id(item)
                                if item_id in stop_items:
                                    if item:
                                        stop_items.update({id(i) for i in item})
                                elif modulo_ok:
                                    yield item
                            cnt = cnt - 1
                            modulo_ok=not((cnt-start) % step)
                            siblings = self.siblings(cnt, options)
                    else:
                        items_found=True
                        modulo_ok=True
                        while items_found:
                            items_found=(cnt==start)
                            for item in siblings:
                                items_found=True
                                item_id = id(item)
                                if item_id in stop_items:
                                    if item:
                                        stop_items.update({id(i) for i in item})
                                elif modulo_ok and item_id not in yielded_items:
                                    yield item
                                    yielded_items.add(id(item))
                                if item is itree:
                                    items_found = False
                                    break
                            cnt = cnt - 1
                            modulo_ok = not ((cnt - start) % step)
                            siblings = self.siblings(cnt, options)
                else:
                    if options & MULTIPLE:
                        if itree.parent:
                            stop_items.add(itree.parent)
                        items_found=True
                        modulo_ok=True
                        while items_found:
                            items_found=(cnt==start)
                            for item in siblings:
                                items_found=True
                                item_id = id(item)
                                if item_id in stop_items:
                                    if item:
                                        stop_items.update({id(i) for i in item})
                                elif modulo_ok and item is not itree:
                                    yield item
                            cnt = cnt - 1
                            modulo_ok = not ((cnt - start) % step)
                            siblings = self.siblings(cnt, options)
                    else:
                        yielded_items.add(id(itree))
                        items_found=True
                        modulo_ok=True
                        while items_found:
                            items_found=(cnt==start)
                            for item in siblings:
                                items_found=True
                                item_id = id(item)
                                if item_id in stop_items:
                                    if item:
                                        stop_items.update({id(i) for i in item})
                                elif modulo_ok and item_id not in yielded_items:
                                    yield item
                                    yielded_items.add(id(item))
                                if item is itree:
                                    items_found = False
                                    break
                            cnt = cnt - 1
                            modulo_ok = not ((cnt - start) % step)
                            siblings = self.siblings(cnt, options)
        else:
            # list or iterable of levels given
            # this iterator is slower as the slices
            if options&MULTIPLE:
                for i in self._levels_via_siblings_iterable(levels,options):
                    yield i
            else:
                yielded_items=set()
                for i in self._levels_via_siblings_iterable(levels,options):
                    if id(i) not in yielded_items:
                        yield i
                        yielded_items.add(id(i))


    def idx_paths(self, filter_method=None, options=DOWN, up_to_low=None):
        """
        Call via: **iTree().deep.idx_paths()**

        In-depth iterator that iterates over all items in the nested `iTree`-structure. The iterator flattens the
        nested structure.
        In general the method iters the same way as the "normal" `deep.iter()`-method but it yields
        the tuple `(item.idx_path, item)` per item.

        The way we iterate depends on the given iteration options (combine options with | (OR bit operator)):

            * ITER.UP - Iteration will be made bottom->up (from the deepest items to the root),
              The default iteration direction is top -> down

            * ITER.REVERSE - The children of a item are iterated in the reversed direction (high index -> zero index).
              The default iteration direction for the children is zero index ->o highest index)

            * ITER.SELF - In the iteration the calling object (self) will be included.
              The default is that the calling object is not part of the iteration

            * ITER.FILTER_ANY - This flag has effect if a filter_method is given. It enables the pythons
              build_in `filter()` on any iterated object. The default is a hierarchical filtering.

        Other iteration flags are not supported by this function.

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` (default) is given no filtering will be performed.

        :type option: int
        :param option: Supported iteration options:
                       ITER.UP | ITER.REVERSE | ITER.SELF | ITER.FILTER_ANY

        :rtype: Generator
        :return: iterator over all nested ìTree`-items (delivers the tuple `(item.idx_path, item)` per item)
        """
        # for downward compatibility:
        # the option: ITER.DOWN is ignored because this is the default behavior.
        # ITER.DOWN exists only for downward compatibility
        if options == 0:
            options = options | UP
        if up_to_low is not None:
            if not up_to_low:
                options = options | UP
            warnings.warn(
                "The parameter up_to_low will be removed soon. Use options=ITER.UP instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        if ITER.valid_option(UP | DOWN | REVERSE | SELF | FILTER_ANY):
            raise AttributeError(ITER.valid_option(options))
        if options & FILTER_ANY:
            gen = self._ITER_IDXPATH_HELPERS[options & (UP | REVERSE)](self, None, options & SELF)
            if filter_method:
                return ((idx_path,item) for idx_path,item in gen if filter_method(item))
            else:
                return gen
        else:
            return self._ITER_IDXPATH_HELPERS[options & (UP | REVERSE)](self,filter_method, options & SELF)


    # ToDo:

    def tag_idx_paths(self, filter_method=None, options=DOWN, up_to_low=None):
        """
        Call via: **iTree().deep.tag_idx_paths()**

        In-depth iterator that iterates over all items in the nested `iTree`-structure. The iterator flattens the
        nested structure.
        In general the method iters the same way as the "normal" `deep.iter()`-method but it yields
        the tuple `(item.tag_idx_path, item)` per item.

        The way we iterate depends on the given iteration options (combine options with | (OR bit operator)):

            * ITER.UP - Iteration will be made bottom->up (from the deepest items to the root),
              The default iteration direction is top -> down

            * ITER.REVERSE - The children of a item are iterated in the reversed direction (high index -> zero index).
              The default iteration direction for the children is zero index ->o highest index)

            * ITER.SELF - In the iteration the calling object (self) will be included.
              The default is that the calling object is not part of the iteration

            * ITER.FILTER_ANY - This flag has effect if a filter_method is given. It enables the pythons
              build_in `filter()` on any iterated object. The default is a hierarchical filtering.

        Other iteration flags are not supported by this function.

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` (default) is given no filtering will be performed.

        :type option: int
        :param option: Supported iteration options:
                       ITER.UP | ITER.REVERSE | ITER.SELF | ITER.FILTER_ANY

        :rtype: Generator
        :return: iterator over all nested ìTree`-items (delivers the tuple `(item.tag_idx_path, item)` per item)
        """
        # for downward compatibility:
        # the option: ITER.DOWN is ignored because this is the default behavior.
        # ITER.DOWN exists only for downward compatibility
        if options == 0:
            options = options | UP
        if up_to_low is not None:
            if not up_to_low:
                options = options | UP
            warnings.warn(
                "The parameter up_to_low will be removed soon. Use options=ITER.UP instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        if ITER.valid_option(UP | DOWN | REVERSE | SELF | FILTER_ANY):
            raise AttributeError(ITER.valid_option(options))
        if options & FILTER_ANY:
            gen = self._ITER_TAGIDXPATH_HELPERS[options & (UP | REVERSE)](self, None, options & SELF)
            if filter_method:
                return ((idx_path,item) for idx_path,item in gen if filter_method(item))
            else:
                return gen
        else:
            return self._ITER_TAGIDXPATH_HELPERS[options & (UP | REVERSE)](self,filter_method, options & SELF)

    def iter_family_items(self, order_last=False):
        """
        Call via: **iTree().deep.iter_family_items()**

        This is a special iterator that iterates over the families in `iTree`-class. It iters over the items of each
        family the ordered by the first or the last items of the families.

        .. note:: As an exception this in-depth iteration-method does not support level-filtering because in an
                  iteration based on tag-family items we do not see any sense in hierarchical filtering. Only
                  external filtering of the resulting elements makes sense.

        :type order_last: bool
        :param order_last:
            * False (default) - The tag-order is based on the order of the first items in the family
            * True - The tag-order is based on the order of the last items in the family

        :rtype: Generator
        :return: iterator over all families delivers tuples of (family-tag, family-item-list)
        """
        if order_last:
            o_idx = -1
        else:
            o_idx = 0
        if self._itree:
            none_tuple = NONE_TUPLE
            items = iter_list((self._itree,))
            family_iters = iter_list(none_tuple)
            iterators = iter_list((self._itree.tags(),))
            while iterators:
                break_main = False
                for tag in iterators[-1]:
                    if tag is None:
                        del iterators[-1]
                        del items[-1]
                        del family_iters[-1]
                    else:
                        family_iters[-1] = items[-1].get.by_tag(tag)
                        for item in family_iters[-1]:
                            yield item
                            if item:
                                iterators.extend((none_tuple, item.tags()))
                                family_iters.append(None)
                                items.append(item)
                                break_main = True
                                break
                    if break_main:
                        break
                else:  # for loop is finished and not broken
                    del iterators[-1]
