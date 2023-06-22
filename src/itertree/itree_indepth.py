# -*- coding: utf-8 -*-
"""
This code is taken from the itertree package:
https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license incl. human protect patch:

The MIT License (MIT) incl. human protect patch
Copyright © 2022 <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

Human protect patch:
The program and its derivative work will neither be modified or executed to harm any human being nor through
inaction permit any human being to be harmed.

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information see: https://en.wikipedia.org/wiki/MIT_License


This part of code contains the main iTree object
"""


from itertools import dropwhile,islice
import sys
from collections import deque

iter_list = list if sys.version_info >= (3, 8) else deque # from Python 3.8 on lists are quicker then deque

NONE_TUPLE=(None,)

class _iTreeIndepthTree():

    __slots__ = ('_itree','get','_active_iter')


    # To win some speed we set self._itree after init of the class in the main iTree object

    def unset_tree_read_only(self,filter_method=None,hierarchical=True):
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
        itree=self._itree
        unset_flags=itree._unset_flags
        read_only_tree_flag=itree._READ_ONLY_TREE
        if itree._itree_prt_idx is not None and itree._itree_prt_idx[0]._flags & itree._READ_ONLY_TREE:
            raise PermissionError('The structural protection flag can only be unset in '
                                  'case the parent is not protected. But here the parent holds the protection flag')
        if filter_method:
            if filter_method(itree):
                unset_flags(itree, read_only_tree_flag)
            if hierarchical:
                iterator=self.iter(filter_method)
            else:
                # not sure if this makes sense, hi risk of denied action because of protected parents
                iterator = filter(filter_method,self)
        else:
            unset_flags(itree, read_only_tree_flag)
            iterator=self.__iter__()
        for i in iterator:
            unset_flags(i, read_only_tree_flag)


    def unset_value_read_only(self,filter_method=None, hierarchical=True):
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
        itree=self._itree
        read_only_value_flag=itree._READ_ONLY_VALUE
        unset_flags=itree._unset_flags
        if itree._itree_prt_idx is not None and itree._itree_prt_idx[0]._flags & itree._READ_ONLY_TREE:
            raise PermissionError('The structural protection flag can only be unset in '
                                  'case the parent is not protected. But here the parent holds the protection flag')
        if filter_method:
            if filter_method(itree):
                unset_flags(itree, read_only_value_flag)
            if hierarchical:
                iterator=self.iter(filter_method)
            else:
                iterator=filter(filter_method, self)
        else:
            unset_flags(itree, read_only_value_flag)
            iterator=self.__iter__()
        # We consume the iterator and change the flag as quick as possible
        for i in iterator:
            unset_flags(i, read_only_value_flag)


    def set_value_read_only(self,filter_method=None, hierarchical=True):
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
        itree=self._itree
        read_only_value_flag=itree._READ_ONLY_VALUE
        set_flags=itree._set_flags
        if itree._itree_prt_idx is not None and itree._itree_prt_idx[0]._flags & itree._READ_ONLY_TREE:
            raise PermissionError('The structural protection flag can only be unset in '
                                  'case the parent is not protected. But here the parent holds the protection flag')
        if filter_method:
            if filter_method(itree):
                set_flags(itree, read_only_value_flag)
            if hierarchical:
                iterator=self.iter(filter_method)
            else:
                iterator=filter(filter_method, self)
        else:
            set_flags(itree, read_only_value_flag)
            iterator=self.__iter__()
        # We consume the iterator and change the flag as quick as possible
        for i in iterator:
            set_flags(i,read_only_value_flag)

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

    def count(self,item):
        """
        Call via **iTree().deep.count()**`

        Counts (in-depth) how many equal (`==`) items are inside the `iTree`-object.

        :type item: iTree
        :param item: The `iTree`-items will be compared with this item

        :rtype: int
        :return: Number of matching items found
        """
        return sum(item==i for i in self)

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
            return sum(1 for _ in filter(filter_method,self))

    def __contains__(self,item):
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

    def is_tag_in(self,tag):
        """
        Call via **iTree().deep.is_tag_in()**

        Checks if a iTree contains the given family-tag (in_depth (all levels))
        :param tag: family tag
        :return: True/False
        """
        for i in self: #iter over all items
            if i.is_tag_in(tag):
                return True
        return False

    def is_in(self,item):
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
        itree=self._itree
        p = item._itree_prt_idx is not None and item._itree_prt_idx[0] or None
        while p is not None:
            if p is itree:
                return True
            p = p._itree_prt_idx is not None and p._itree_prt_idx[0] or None
        return False


    def index(self,item,start=None,stop=None):
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
        itree=self._itree
        if itree:
            s = len(itree.idx_path)
            iterator=self.__iter__()
            if start is not None:
                if not hasattr(start,'_itree_prt_idx'):
                    start=self._itree.get.single(*start)
                try:
                    first_item=next(dropwhile(lambda i: i is not start,iterator))
                    if first_item==item:
                        return first_item.idx_path[s:]
                except StopIteration:
                    raise IndexError('No matching item found in iTree')
            if stop is not None:
                if not hasattr(stop,'_itree_prt_idx'):
                    stop=self._itree.get.single(*stop)
                try:
                    item = next(dropwhile(lambda i: i is not stop and i!=item, iterator))
                    if item is not stop:
                        return item.idx_path[s:]
                    raise StopIteration
                except StopIteration:
                    raise IndexError('No matching item found in iTree')
            else:
                try:
                    item = next(dropwhile(lambda i: i!=item, iterator))
                    return item.idx_path[s:]
                except StopIteration:
                    raise IndexError('No matching item found in iTree')

    def reverse(self):
        """
        Call via **iTree().deep.reverse()**

        In-depth reverse of the order of all children in the `iTree`. Same as method `reverse()`
        but this is the in-depth version
        of the
        method. This method dives deeper and the sub-children, sub-sub-children, ... orders are reversed too.

        .. note:: The implementation of this method is recursive for deep trees recursion limit might be reached.
        """
        itree=self._itree
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
        itree=self._itree
        flags = itree._flags
        if flags & itree._IS_TREE_PROTECTED:
            if not itree.is_link_root or itree._link.is_loaded:
                itree._raise_read_only_exception(itree)
        else:
            itree.sort(key=key, reverse=reverse)
            for i in itree:
                i.deep.sort(key, reverse)

    def remove(self,*target_path):
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

        del_items=self._itree.get(*target_path)
        if hasattr(del_items,'_itree_prt_idx'):
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
            iterators=iter_list((self._itree.__iter__(),))
            while iterators:
                for item in iterators[-1]:
                    yield item
                    if item:
                        iterators.append(item.__iter__())
                        break
                else: # for loop is finished and not broken
                    del iterators[-1]

    def iter(self,filter_method=None,up_to_low=True):
        """
        Call via **iTree().deep.iter()**

        In-depth iterator that iterates over all items in the nested `iTree`-structure. The iterator flattens the
        nested structure.


        Via the parameters the user can achieve hierarchical filtering of items. He can change the iteration order
        up-> down or down->up.

        If no parameter is given `iter()` behaves like the build in `__iter__()` method of the object.

        .. note:: The given iteration order must not be seen like the build-in  'reversed()' function which
                  changes the iteration direction in general! Furthermore, it means we iterate:

                  * `up_to_low==True`: parent-> child-> sub-child-> sub-sub-child-> ...

                  or we start from the most-inner nested item:

                  * `up_to_low==False`: item,  parent, parent-parent, ..., -> root

                  But we always start in the right order we have in `iTree` first the root or in second case
                  first most-inner nested item coming from the root.

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` is given no filtering will be performed.

        :type up_to_low: bool
        :param up_to_low:
                        * True (default) - we iterate in-depth from up to the lower inner structure of the `iTree`-object
                        * False - we iterate in-depth from lower to upper structure of the `iTree`-object

        :rtype: Generator
        :return: iterator over all nested ìTree`-items
        """
        if self._itree:
            if filter_method:
                iterators = iter_list((filter(filter_method, self._itree.__iter__()),))
                if up_to_low:
                    # hierarchical filtered up -> down iterator
                    while iterators:
                        for item in iterators[-1]:
                            yield item
                            if item:
                                iterators.append(filter(filter_method, item.__iter__()))
                                break
                        else:  # for loop is finished and not broken
                            del iterators[-1]
                else:
                    # hierarchical filtered down -> up iterator
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                iterators.extend(((None, item), filter(filter_method, item.__iter__())))
                                break
                            elif item is None:
                                yield iterators.pop()[-1]
                                break
                            else:
                                yield item
                        else:  # for loop is finished and not broken
                            del iterators[-1]
            else:
                iterators = iter_list((self._itree.__iter__(),))
                if up_to_low:
                    while iterators:
                        for item in iterators[-1]:
                            yield item
                            if item:
                                iterators.append(item.__iter__())
                                break
                        else:  # for loop is finished and not broken
                            del iterators[-1]
                else:
                    # low -> up iterator:
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                iterators.extend(((None, item), item.__iter__()))
                                break
                            elif item is None:
                                yield iterators.pop()[-1]
                                break
                            else:
                                yield item
                        else:  # for loop is finished and not broken
                            del iterators[-1]

    def idx_paths(self,filter_method=None,up_to_low=True):
        """
        Call via **iTree().deep.idx_paths()**

        In-depth generator (iterator) which iterates over all nested items of the `iTree`-object in
        top -> down direction.
        The iterator delivers per item the pair (relative idx_path, item).

        The index path is same as in the items `.idx_path` property which contains the absolute indexes
        to the root-parent. But in this iterator we deliver the relative idx_path related to the element the
        iteration is started and not the path to the root-parent.

        The iterator does exactly the same as the following code based on the main iterator and the
        extraction of the idx_paths:

            >>> # Let itree be the instanced iTree in which we like to iterate over all nested items (in-depth-iteration)
            >>> s=len(itree.idx_path) # required to create relative paths
            >>> idx_paths_generator=((i.idx_path[s:],i) for i in iter(itree.all))

        But this specific iterator is much quicker because the indexes are counted up internally during the iteration
        which is more efficent as the calculation of the idx_path for each item in this solution.

        The solution to deliver the pairs is chosen, because the user can choose by unpacking what's required for his
        needs and he still can filter based on item properties.

        E.g.:
        Store the ind_paths in a list:

            >>> my_idx_path_list=[idx_path for idx_path,_ in itree.all.idx_paths()]

        Store the filtered idx_paths in a list (because of the delivered items a filtering is possible):

            >>> my_idx_path_list=[idx_path for idx_path,_ in filter(lambda i: i[1].tag=='mytag', itree.all.idx_paths())]

        Convert the content of the `iTree` in a dict by using the idx_paths as keys:

            >>> my_dict={idx_path:item for idx_path,item in itree.all.idx_paths()}

        The user may store values only in the dict too:

            >>> my_dict={idx_path:item.value for idx_path,item in itree.all.idx_paths()}

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` is given no filtering will be performed.

        :type up_to_low: bool
        :param up_to_low:
                        * True (default) - we iterate in-depth from up to the lower inner structure of the `iTree`-object
                        * False - we iterate in-depth from lower to upper structure of the `iTree`-object


        :rtype: Generator
        :return: iterator over all ìTree`-items and yields for each item the pair (relative idx_path, item)
        """
        if self._itree:
            iterators = iter_list((self._itree.__iter__(),))  # in Python 3.9 lists are quicker than deque
            indexes = [-1]
            if filter_method:
                if up_to_low:
                    none_tuple = NONE_TUPLE
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                # In next line we update the cache too
                                item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                                if filter_method(item):
                                    yield tuple(indexes), item
                                    iterators.extend((none_tuple, item.__iter__()))
                                    indexes.append(-1)
                                    break
                            elif item is None:
                                del indexes[-1]
                                del iterators[-1]
                                break
                            else:
                                item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                                if filter_method(item):
                                    yield tuple(indexes), item
                        else:  # for loop is finished and not broken
                            del iterators[-1]
                else:
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                                if filter_method(item):
                                    iterators.extend(((None, (tuple(indexes), item)), item.__iter__()))
                                    indexes.append(-1)
                                    break
                            elif item is None:
                                yield iterators.pop()[-1]
                                del indexes[-1]
                                break
                            else:
                                item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                                if filter_method(item):
                                    yield tuple(indexes), item
                        else:  # for loop is finished and not broken
                            del iterators[-1]
            else:
                if up_to_low:
                    none_tuple = NONE_TUPLE
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                # In next line we update the cache too
                                item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                                yield tuple(indexes), item
                                iterators.extend((none_tuple, item.__iter__()))
                                indexes.append(-1)
                                break
                            elif item is None:
                                del indexes[-1]
                                del iterators[-1]
                                break
                            else:
                                item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                                yield tuple(indexes), item
                        else:  # for loop is finished and not broken
                            del iterators[-1]
                else:
                    iterators = iter_list((self._itree.__iter__(),))
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                                iterators.extend(((None, (tuple(indexes), item)), item.__iter__()))
                                indexes.append(-1)
                                break
                            elif item is None:
                                yield iterators.pop()[-1]
                                del indexes[-1]
                                break
                            else:
                                item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                                yield tuple(indexes), item
                        else:  # for loop is finished and not broken
                            del iterators[-1]

    def tag_idx_paths(self, filter_method=None, up_to_low=True):
        """
        Call via: **iTree().deep.tag_idx_paths()**

        In-depth generator (iterator) which iterates over all nested items of the `iTree`-object in
        top -> down direction.
        The iterator delivers per item the pair (relative idx_path, item).

        The index path is same as in the items `.key_path` property which contains the absolute indexes
        to the root-parent. But in this iterator we deliver the relative idx_path related to the element the
        iteration is started and not the path to the root-parent.

        The iterator does exactly the same as the following code based on the main iterator and the
        extraction of the key_paths:

            >>> # Let itree be the instanced iTree in which we like to iterate over all nested items (in-depth-iteration)
            >>> s=len(itree.tag_idx_path) # required to create relative paths
            >>> key_paths_generator=((i.tag_idx_path[s:],i) for i in iter(itree.all))

        But this specific iterator is much quicker because the family-indexes are counted up internally during the iteration
        which is more efficent as the calculation of the key_path for each item in this solution.

        The solution to deliver the pairs is chosen, because the user can choose by unpacking what's required for his
        needs and he still can filter based on item properties (see similar examples in method `idx_paths()`).

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                         and delivers `True`/`False`.
                         The `filter_method` targets always the `iTree`-child-object and checks a characteristic
                         of this object.

                         If `None` is given no filtering will be performed.

        :type up_to_low: bool
        :param up_to_low:
                        * True (default) - we iterate in-depth from up to the lower inner structure of the `iTree`-object
                        * False - we iterate in-depth from lower to upper structure of the `iTree`-object


        :rtype: Generator
        :return: iterator over all ìTree`-items and yields for each item the pair (relative idx_path, item)
        """
        if self._itree:
            tag_indexes = [None]
            iterators = iter_list((self._itree.__iter__(),))
            if filter_method:
                if up_to_low:
                    none_tuple = NONE_TUPLE
                    tag_index_dict = [{tag: -1 for tag in self._itree._families.keys()}]
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                                tag_indexes[-1] = (tag, idx)
                                if filter_method(item):
                                    yield tuple(tag_indexes), item
                                    iterators.extend((none_tuple, filter(filter_method,item.__iter__())))
                                    tag_indexes.append(None)
                                    tag_index_dict.append({tag: -1 for tag in item._families.keys()})
                                    break
                            elif item is None:
                                del tag_indexes[-1]
                                del tag_index_dict[-1]
                                del iterators[-1]
                                break
                            else:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                item._itree_prt_idx[2] = tag_dict[tag] = c = tag_dict[tag] + 1
                                tag_indexes[-1] = (tag, c)
                                if filter_method(item):
                                    yield tuple(tag_indexes), item
                        else:  # for loop is finished and not broken
                            del iterators[-1]
                else:
                    tag_index_dict = [{tag: -1 for tag in self._itree._families.keys()}]
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                                tag_indexes[-1] = (tag, idx)
                                if filter_method(item):
                                    iterators.extend(((None, (tuple(tag_indexes), item)), filter(filter_method,item.__iter__())))
                                    tag_indexes.append(None)
                                    tag_index_dict.append({tag: -1 for tag in item._families.keys()})
                                    break
                            elif item is None:
                                yield iterators.pop()[-1]
                                del tag_indexes[-1]
                                del tag_index_dict[-1]
                                break
                            else:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                item._itree_prt_idx[2] = tag_dict[tag] = c = tag_dict[tag] + 1
                                tag_indexes[-1] = (tag, c)
                                if filter_method(item):
                                    yield tuple(tag_indexes), item
                        else:  # for loop is finished and not broken
                            del iterators[-1]
            else:
                if up_to_low:
                    none_tuple = NONE_TUPLE
                    tag_index_dict = [{tag: -1 for tag in self._itree._families.keys()}]
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                                tag_indexes[-1] = (tag, idx)
                                yield tuple(tag_indexes), item
                                iterators.extend((none_tuple, item.__iter__()))
                                tag_indexes.append(None)
                                tag_index_dict.append({tag: -1 for tag in item._families.keys()})
                                break
                            elif item is None:
                                del tag_indexes[-1]
                                del tag_index_dict[-1]
                                del iterators[-1]
                                break
                            else:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                try:
                                    item._itree_prt_idx[2] = tag_dict[tag] = c = tag_dict[tag] + 1
                                except KeyError:
                                    item._itree_prt_idx[2] = tag_dict[tag] = c = 0
                                tag_indexes[-1] = (tag, c)
                                yield tuple(tag_indexes), item
                        else:  # for loop is finished and not broken
                            del iterators[-1]
                else:
                    tag_index_dict = [{tag: -1 for tag in self._itree._families.keys()}]
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                                tag_indexes[-1] = (tag, idx)
                                iterators.extend(((None, (tuple(tag_indexes), item)), item.__iter__()))
                                tag_indexes.append(None)
                                tag_index_dict.append({tag: -1 for tag in item._families.keys()})
                                break
                            elif item is None:
                                yield iterators.pop()[-1]
                                del tag_indexes[-1]
                                del tag_index_dict[-1]
                                break
                            else:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                try:
                                    item._itree_prt_idx[2] = tag_dict[tag] = c = tag_dict[tag] + 1
                                except KeyError:
                                    item._itree_prt_idx[2] = tag_dict[tag] = c = 0
                                tag_indexes[-1] = (tag, c)
                                yield tuple(tag_indexes), item
                        else:  # for loop is finished and not broken
                            del iterators[-1]

    def iter_family_items(self, order_last=False):
        """
        Call via: **iTree().deep.iter_family_items()**

        This is a special iterator that iterates over the families in `iTree`. It iters over the items of each family
        the ordered by the first or the last items of the families.

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
            o_idx=-1
        else:
            o_idx = 0
        if self._itree:
            none_tuple=NONE_TUPLE
            items=iter_list((self._itree,))
            family_iters=iter_list(none_tuple)
            iterators = iter_list((self._itree.tags(),))
            while iterators:
                break_main = False
                for tag in iterators[-1]:
                    if tag is None:
                        del iterators[-1]
                        del items[-1]
                        del family_iters[-1]
                    else:
                        family_iters[-1]=items[-1].get.by_tag(tag)
                        for item in family_iters[-1]:
                            yield item
                            if item:
                                iterators.extend((none_tuple,item.tags()))
                                family_iters.append(None)
                                items.append(item)
                                break_main=True
                                break
                    if break_main:
                        break
                else:  # for loop is finished and not broken
                    del iterators[-1]
