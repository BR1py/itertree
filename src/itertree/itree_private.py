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


This part of code contains the private helper functions in iTree object

Those methods are all defined as static methods which means in case self is required as
first parameter it must be placed explicit in

"""

import copy
import sys
from collections import deque
from contextlib import suppress
from itertools import chain, dropwhile, islice,tee
from operator import length_hint
from itertree.itree_helpers import np,iTLink, itree_list, NoValue, BLIST_SWITCH

NONE_TUPLE=(None,)

# items

class _iTreeParent():
    __slots__ = ('parent', 'abs_idx_cache', 'fam_idx_cache', 'flags', 'link','families','super_list')

# For the following important class we distinguish in between the different Python versions to take advantages
# from new features available (like yield from and `:=`

class _iTreePrivate():

    __slots__=()
    """
    super class of iTree which contains all private static methods

    This class was created because the number of public methods is already large and
    so we can split the functionality a bit over two files/modules

    This class contains especially all variants of required iterators.

    """

    # --- other static helpers ---------------------------------------------------------------------

    @staticmethod
    def _value_equal(self_value, other_value):
        """
        helper function for comparison of value data
        :param self_value: own value-data-object against the other_value object should be checked
                           (given explicit for recursive usage)
        :param other_value: other data object we like to compare with
        :return:
                * True - match
                * False - no match

        """
        t = type(self_value)
        if t != type(other_value):
            return False
        try:
            equal = (self_value == other_value)
        except Exception:
            equal = None
        if equal is True or equal is False:
            return equal
        try:
            return all(equal)
        except Exception:
            with suppress(Exception):
                if np is not None and t is np.ndarray:
                    # numpy objects
                    if self_value.shape != other_value.shape or self_value.dtype != other_value.dtype:
                        return False
                    return all(np.equal(np.frombuffer(self_value, dtype=np.uint8),
                                        np.frombuffer(other_value, dtype=np.uint8)))
        # we must look deeper
        value_equal = _iTreePrivate._value_equal
        if hasattr(self_value, 'items'):
            try:
                next(dropwhile(lambda i: value_equal(i[0][0],i[1][0]) and value_equal(i[0][1],i[1][1])
                          ,zip(self_value.items(), other_value.items())))
                return False
            except StopIteration:
                return True
            except Exception:
                pass
        # if we reach this point we expect an iterables or just a mutable object
        try:
            next(dropwhile(value_equal, zip(self_value, other_value)))
            return False
        except StopIteration:
            return True
        except Exception:
            return False


    @staticmethod
    def _raise_read_only_exception(itree_item):
        raise PermissionError('The item (%s) is read_only (linked or read_only flag)!' % repr(itree_item))

    @staticmethod
    def _raise_exception(exception):
        raise exception

    # --- flags related helpers ----------------------------------------------------------------
    # private helpers for setting flags

    @staticmethod
    def _set_flags(itree_item, flags, _init=False):
        """
        Set the given flags on the `iTree`-object

        :type flags: int
        :param flags: flags (flag-mask) changing item behavior
                      Multiple flags can be combined via `|`
        """
        if not _init and itree_item._flags & itree_item._LINKED:
            _iTreePrivate._raise_read_only_exception(itree_item)
        itree_item._flags = itree_item._flags | flags

    @staticmethod
    def _set_flags_deep(itree_item, flags, filter_method=None, iter_unfiltered=False, _init=False):
        """
        Change the flags of the item and the nested items in the subtree; sub-subtree, ...

        :type flags: int
        :param flags: flags (flag-mask) changing item behavior
                      Multiple flags can be combined via `|`

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches (see :ref:`filter_method <filter_method>`)

                            If `None` is given filtering is inactive.

        :type iter_unfiltered: bool
        :param iter_unfiltered:
                               * False (default)
                                    the iteration will be stopped in case a item is not matching. The
                                    whole branch will be out in this case.
                               * True
                                    The iteration will be continued if that a parent is not matching., It will
                                    iterate over the whole subtree and deliver all matching items.

        """
        if itree_item._flags & itree_item._LINKED and not _init:
            _iTreePrivate._raise_read_only_exception(itree_item)
        set_flags=_iTreePrivate._set_flags
        if filter_method:
            if filter_method(itree_item):
                set_flags(itree_item, flags, _init=_init)
                for i in itree_item.deep.iter(filter_method):
                    set_flags(i, flags, _init=_init)
            elif iter_unfiltered:
                for i in filter(filter_method, itree_item.deep):
                    set_flags(i,flags,_init=_init)
        else:
            set_flags(itree_item,flags, _init=_init)
            for i in itree_item.deep:
                set_flags(i,flags, _init=_init)

    @staticmethod
    def _unset_flags(itree_item, flags):
        if itree_item._flags & itree_item._LINKED:
            _iTreePrivate._raise_read_only_exception(itree_item)
        s_flags = itree_item._flags
        itree_item._flags = result=s_flags & (~s_flags & flags)
        return result

    @staticmethod
    def _unset_flags_deep(itree_item, flags, filter_method=None, iter_unfiltered=False):
        if itree_item._flags & itree_item._LINKED:
            _iTreePrivate._raise_read_only_exception(itree_item)
        unset_flags=_iTreePrivate._unset_flags
        if filter_method:
            if filter_method(itree_item):
                unset_flags(itree_item,flags)
                for i in itree_item.deep.iter(filter_method):
                    unset_flags(i,flags)
            elif iter_unfiltered:
                for i in filter(filter_method, itree_item.deep):
                    unset_flags(i, flags)
        else:
            unset_flags(itree_item,flags)
            for i in itree_item.deep:
                unset_flags(i,flags)

    # --- item integration -------------------------------------------------------------------------


    @staticmethod
    def _iter_extend(itree_item, items, flags_deep=0,init=False):
        """
        Generator which iterates over items given and extends them into the `iTree`-object

        The generator extends the items to the families and yields the items to be extended to
        the super() blist-object of `iTree`.

        This is the main extend function and the additional parameters are used for instance `iTree`-objects too.

        .. note::
               In case the items have already a parent an implicit copy will be made. We do this because
               we might get an `iTree`-object as `extend_items`-parameter and then the children will have automatically
               a parent.

        :type param: Iterable
        :param items: iterable object that contains `iTree`-objects as items it can be:

                        * iterator or generator of `iTree`-objects (using next)
                        * `iTree`-object (children will be copied in this case
                        * iterable of `iTree`-objects (list, tuple, ...)
                        * argument list for `iTree`-instance ( ´__init__()´ )(created by ´get_init_args()´
                          or ´get_init_args_deep()´)
                        * iterator or generator of value-objects (using next) - implicit `iTree`objects created
                        * iterable of value-objects (list, tuple, ...)- implicit `iTree`objects created

        :type _decoder: Option[Callable]
        :param _decoder: _decoder internal parameter used for load/loads operations decodes tags and values

        :type flags_deep: int
        :param flags_deep: set the given flags deep in the tree

        :rtype: Iterator/Generator
        :return: An iterator of all items to be added in super_class (blist)
        """
        # Implementation state: ready, tested, doc ok
        itree_class = itree_item.__class__
        if init:
            idx=0
        else:
            idx = len(itree_item)
            if hasattr(items,'_itree_prt_idx') and items.root is itree_item.root:
                # here we must create an independent object if not we might implicit extend the source in parallel
                items=items.copy()
        if idx:
            # make multi called functions local:
            fs_getitem = itree_item._get_fam
            fs_setitem = itree_item._setitem_fam
        else: # empty!
            # In the moment the first child is added we set all pointers to the quick access functions
            getitem=itree_item.get
            #families
            itree_item._families = families = {}
            getitem._getitem_fam=itree_item._getitem_fam=families.__getitem__
            itree_item._setitem_fam = fs_setitem = families.__setitem__
            fs_getitem=itree_item._get_fam  = families.get
        if flags_deep:
            set_flags_deep=_iTreePrivate._set_flags_deep
            for item in items:
                if hasattr(item, '_itree_prt_idx'):
                    if item._itree_prt_idx:
                        item = item.__copy__()
                else:
                    item = itree_class(*item) if type(item) is list else itree_class(value=item)
                tag = item._tag
                family = fs_getitem(tag)
                if family is None:
                    fs_setitem(tag, [item])
                    item._itree_prt_idx = [itree_item, idx, 0]
                else:
                    fm_idx = family.__len__()
                    family.append(item)
                    if fm_idx == BLIST_SWITCH:
                        itree_item._setitem_fam(tag, itree_list(family))
                    item._itree_prt_idx = [itree_item, idx, fm_idx]
                set_flags_deep(item,flags_deep, _init=True)
                yield item  # yields the item to extend it to super() list
                idx = idx + 1
        else:
            for item in items:
                if hasattr(item, '_itree_prt_idx'):
                    if item._itree_prt_idx:
                        item = item.__copy__()
                else:
                    item = itree_class(*item) if type(item) is list else itree_class(value=item)
                # append to tag family
                tag = item._tag
                family = fs_getitem(tag)
                if family is None:
                    fs_setitem(tag, [item])
                    item._itree_prt_idx = [itree_item, idx, 0]
                else:
                    fm_idx = family.__len__()
                    family.append(item)
                    if fm_idx == BLIST_SWITCH:
                        itree_item._setitem_fam(tag, itree_list(family))
                    item._itree_prt_idx = [itree_item, idx, fm_idx]
                yield item  # yields the item to extend it to super() list
                idx = idx + 1

    @staticmethod
    def _append_item(itree_item, item):
        """
        Internal append for building `iTrees` in internal load operations (we do not check any properties here)
        (is quicker than normal append (makes less plausibility checks))

        :type itree_item: iTree
        :param itree_item: iTree where the item should be appended

        :type item: iTree
        :param item: `iTree`-object to be appended

        :rtype: iTree
        :return: Delivers the appended iTree-item
                 (it might be useful for the user to get the updated information of the object).
        """
        # Implementation state: ready, tested, doc ok
        # append item to super list:
        tag = item._tag
        if itree_item:
            abs_idx = len(itree_item)
            itree_item._items.append(item)
            # append item to family
            family = itree_item._get_fam(tag)
            if family is None:
                itree_item._setitem_fam(tag, [item])
                item._itree_prt_idx = [itree_item, abs_idx, 0]
            else:
                fm_idx = family.__len__()
                family.append(item)
                if fm_idx == BLIST_SWITCH:
                    itree_item._setitem_fam(tag, itree_list(family))
                item._itree_prt_idx = [itree_item, abs_idx, fm_idx]
        else:
            # In the moment the item gets the first child we set all pointers for the quick access functions
            getitem=itree_item.get
            # items
            itree_item._items = sl = itree_item._ONE_ITEM_LIST.copy()
            sl[0] = item
            itree_item.getitem_by_idx = getitem.getitem_by_idx = sl.__getitem__
            itree_item.__len__, itree_item.__iter__, itree_item._setitem_list = \
                sl.__len__, sl.__iter__, sl.__setitem__
            # family
            itree_item._families = families = {tag: sl.copy()}
            itree_item._setitem_fam, itree_item._get_fam = families.__setitem__, families.get
            getitem._getitem_fam = itree_item._getitem_fam = families.__getitem__
            item._itree_prt_idx = [itree_item, 0, 0]
        return item

    @staticmethod
    def _append_item_left(itree_item, item):
        """
        Internal append for building `iTrees` in internal load operations (we do not check any properties here)
        (is quicker than normal append (makes less plausibility checks))

        :type itree_item: iTree
        :param itree_item: iTree where the item should be appended

        :type item: iTree
        :param item: `iTree`-object to be appended

        :rtype: iTree
        :return: Delivers the appended item ititree_item
                 (it might be useful for the user to get the updated information of the object).
        """
        # Implementation state: ready, tested, doc ok
        # append item to super list:
        sl = itree_item._items
        sl.insert(0,item)
        # append item to family
        tag = item._tag
        family = itree_item._get_fam(tag)
        if family is None:
            itree_item._setitem_fam(tag, [item])
        else:
            family.insert(0, item)
        item._itree_prt_idx = [itree_item, 0, 0]
        return item

    @staticmethod
    def _append(itree_item, item=NoValue):
        """
        Internal append for building iTrees
        (ignores read only and is quicker than normal append (makes less plausibility checks)

        :except: In case `iTree`-object has already a parent a `RecursionError` will be raised
                 Other exceptions might come up in case the `iTree` is protected (tree read-only mode).


        :type item: Union[iTree,object]
        :param item: `iTree`-object to be appended

        :rtype: iTree
        :return: Delivers the appended item itself
                 (it might be useful for the user to get the updated information of the object).
        """
        # Implementation state: ready, tested, doc ok
        if (
                itree_item._flags & itree_item._IS_TREE_PROTECTED
                and itree_item.is_link_root
                and hasattr(itree_item, '_itree_prt_idx')
                and itree_item._flags & (itree_item._LINKED | itree_item._LINK_ROOT | itree_item._PLACEHOLDER)
        ):
            raise TypeError('Linked items cannot be appended to linked item as local item')
        _iTreePrivate._append_item(itree_item, item)

    @staticmethod
    def _get_family_insertion_idx(family, item_idx, _last_index=0):
        """
        Internal function to find the family index for insert as quick as possible,
        it uses interval search based on absolute indexes

        :param family: family list
        :param item_idx: absolute index of item to be searched for
        :param last_index: last index which was checked
        :return: family index
        """
        s = len(family)
        if s == 1:
            return (1 + _last_index) if family[0].idx < item_idx else _last_index
        i = round(s / 2)
        idx = family[i].idx
        # recursive call:
        return (
            _iTreePrivate._get_family_insertion_idx(family[i:], item_idx, _last_index + i)
            if idx < item_idx else
            _iTreePrivate._get_family_insertion_idx(family[:i], item_idx, _last_index)
        )

    @staticmethod
    def _get_copy_args(itree_item):
        value = itree_item._value
        flags = itree_item._flags
        if itree_item.is_link_root:
            if flags:
                return (
                    (
                        itree_item._tag,
                        value,
                        None,
                        iTLink(itree_item._link.file_path, itree_item._link.target_path),
                        flags
                    )
                    if callable(value.__hash__)
                    else (
                        itree_item._tag,
                        copy.copy(value),
                        None,
                        iTLink(itree_item._link.file_path, itree_item._link.target_path),
                        flags
                    )
                )
            else:
                return (
                    (
                        itree_item._tag,
                        value,
                        None,
                        iTLink(itree_item._link.file_path, itree_item._link.target_path)
                    )
                    if callable(value.__hash__)
                    else (
                        itree_item._tag,
                        copy.copy(value),
                        None,
                        iTLink(itree_item._link.file_path, itree_item._link.target_path)
                    )
                )
        elif flags:
            return (
                   (itree_item._tag, value, None, None, flags)
                   if callable(value.__hash__)
                   else (itree_item._tag, copy.copy(value), None, None, flags)
            )
        elif callable(value.__hash__):
            return (itree_item._tag, value)
        else:
            return (itree_item._tag, copy.copy(value))

    @staticmethod
    def _get_args_skip_subtree(itree_item):
        flags = itree_item._flags
        if itree_item.is_link_root:
            if flags:
                return itree_item._tag, itree_item._value,None,iTLink(itree_item._link.file_path, itree_item._link.target_path),flags
            else:
                return itree_item._tag,itree_item._value,None,iTLink(itree_item._link.file_path, itree_item._link.target_path)
        elif flags:
                return itree_item._tag, itree_item._value, None, None, flags
        else:
            return itree_item._tag, itree_item._value

    @staticmethod
    def _get_deepcopy_args(itree_item):
        flags = itree_item._flags
        if itree_item.is_link_root:
            if flags:
                return (
                        itree_item._tag,
                        copy.deepcopy(itree_item._value),
                        None,
                        iTLink(itree_item._link.file_path, itree_item._link.target_path),
                        flags
                       )

            else:
                return (
                        itree_item._tag,
                        copy.deepcopy(itree_item._value),
                        None,
                        iTLink(itree_item._link.file_path, itree_item._link.target_path)
                        )
        elif flags:
                return (itree_item._tag, copy.deepcopy(itree_item._value), None, None, flags)
        return itree_item._tag, copy.deepcopy(itree_item._value)

    # --- iterative iterators --------------------------------------------------------------------------------

    @staticmethod
    def _get_deep_sub_iterator( items, target):
        for item in items:
            with suppress(KeyError, IndexError):
                result = item.__getitem__(target)
                if hasattr(result, '_itree_prt_idx'):
                    yield result
                else:
                    for i in result:
                        yield i


    # copy related iterators

    @staticmethod
    def _iter_copy(itree_item,get_copy_args):
        """
        create a copy of this item

        The helper method runs the copy in a iterative (non-recursive way)

        :param itree_item: item to be copied

        :param get_copy_args: argument creation method should be one of:
                              * _get_copy_args -> normal copy
                              * _get_deepcopy_args -> deepcopy
                              * _get_args_skip_subtree  -> copy and keep value references

        :return: copied iTree object
        """
        # Iterative copy required
        itree_class=itree_item.__class__
        append_item=_iTreePrivate._append_item
        new_itree = itree_class(*get_copy_args(itree_item))
        if itree_item:
            none_tuple = NONE_TUPLE
            items = [new_itree]
            iterators = [itree_item.__iter__()]  # in Python 3.9 lists are quicker than deque
            while iterators:
                for item in iterators[-1]:
                    if item:
                        iterators.extend((none_tuple,item.__iter__()))
                        items.append(append_item(items[-1], itree_class(*get_copy_args(item))))
                        break
                    elif item is None:
                        del items[-1]
                    else:
                        append_item(items[-1], itree_class(*get_copy_args(item)))
                else: # for loop is finished and not broken
                    del iterators[-1]
        return new_itree

    # link related iterators

    @staticmethod
    def _convert_to_linked_item_chained(root_item):
        """
        helper function that creates a linked clone of a normal item
        helper method is need in the load_links method

        :param root_item: item to be "cloned"

        :return: converted item
        """
        get_copy_args=_iTreePrivate._get_args_skip_subtree
        append_item=_iTreePrivate._append_item
        itree_class = root_item.__class__
        linked_flag = root_item._LINKED
        if root_item.is_linked:
            return root_item
        new_item = itree_class(root_item._tag,
                               copy.copy(root_item._value),
                               flags=root_item._flags | linked_flag)
        if root_item:
            iterator = root_item.__iter__()
            none_tuple=NONE_TUPLE
            items = [new_item]
            with suppress(StopIteration):
                while 1:
                    item=next(iterator)
                    if item:
                        iterator = chain(item.__iter__(), none_tuple, iterator)
                        new=append_item(items[-1], itree_class(*get_copy_args(item)))
                        new._flags=new._flags|linked_flag
                        items.append(new)
                    elif item is None:
                        del items[-1]
                    else:
                        new=append_item(items[-1], itree_class(*get_copy_args(item)))
                        new._flags=new._flags|linked_flag
        return new_item

    @staticmethod
    def _convert_to_linked_item(root_item):
        """
        helper function that creates a linked clone of a normal item
        helper method is need in the load_links method

        :param root_item: item to be "cloned"

        :return: converted item
        """
        get_copy_args = _iTreePrivate._get_args_skip_subtree
        append_item = _iTreePrivate._append_item
        itree_class = root_item.__class__
        linked_flag = root_item._LINKED
        if root_item.is_linked:
            return root_item
        new_item = itree_class(root_item._tag,
                               copy.copy(root_item._value),
                               flags=root_item._flags | linked_flag)

        if root_item:
            iterators=[root_item.__iter__()] # in Python 3.9 lists are quicker than deque
            none_tuple=NONE_TUPLE
            items = [new_item]
            while iterators:
                for item in iterators[-1]:
                    if item:
                        iterators.extend((none_tuple, item.__iter__()))
                        new = append_item(items[-1], itree_class(*get_copy_args(item)))
                        new._flags = new._flags | linked_flag
                        items.append(new)
                        break
                    elif item is None:
                        del iterators[-1]
                        break
                    else:
                        new=append_item(items[-1], itree_class(*get_copy_args(item)))
                        new._flags=new._flags|linked_flag
                else: # for loop is finished and not broken
                    del iterators[-1]
        return new_item

    @staticmethod
    def _convert_to_local_item_chained(root_item,copy_subtree=True):
        """
        helper function that creates a linked clone of a normal item
        helper method is need in the load_links method

        :param root_item: item to be "cloned"

        :return: converted item
        """
        get_copy_args=_iTreePrivate._get_args_skip_subtree
        append_item=_iTreePrivate._append_item
        if not root_item.is_linked:
            # is already local
            return root_item
        itree_class = root_item.__class__
        linked_flag = root_item._LINKED
        cp = copy.copy

        new_item = itree_class(root_item._tag,
                               cp(root_item._value),
                               flags=(root_item._flags & (~linked_flag)))
        new_item._link = iTLink(link_item=root_item)
        if root_item and copy_subtree:
            iterator = root_item.__iter__()
            none_tuple=NONE_TUPLE
            items = [new_item]
            with suppress(StopIteration):
                while 1:
                    item=next(iterator)
                    if item:
                        iterator = chain(item.__iter__(), none_tuple, iterator)
                        new=append_item(items[-1], itree_class(*get_copy_args(item)))
                        new._flags=new._flags & (~linked_flag)
                        items.append(new)
                    elif item is None:
                        del items[-1]
                    else:
                        new=append_item(items[-1], itree_class(*get_copy_args(item)))
                        new._flags=new._flags & (~linked_flag)
        return new_item

    @staticmethod
    def _convert_to_local_item(root_item,copy_subtree=True):
        """
        helper function that creates a linked clone of a normal item
        helper method is need in the load_links method

        :param root_item: item to be "cloned"

        :return: converted item
        """
        get_copy_args=_iTreePrivate._get_args_skip_subtree
        append_item=_iTreePrivate._append_item
        if not root_item.is_linked:
            # is already local
            return root_item
        itree_class = root_item.__class__
        linked_flag = root_item._LINKED
        cp = copy.copy

        new_item = itree_class(root_item._tag,
                               cp(root_item._value),
                               flags=(root_item._flags & (~linked_flag)))
        new_item._link = iTLink(link_item=root_item)
        if root_item and copy_subtree:
            iterators=[root_item.__iter__()] # in Python 3.9 lists are quicker than deque
            none_tuple=NONE_TUPLE
            items = [new_item]
            while iterators:
                for item in iterators[-1]:
                    if item:
                        iterators.extend((none_tuple, item.__iter__()))
                        new = append_item(items[-1], itree_class(*get_copy_args(item)))
                        new._flags = new._flags | linked_flag
                        items.append(new)
                        break
                    elif item is None:
                        del iterators[-1]
                        break
                    else:
                        new=append_item(items[-1], itree_class(*get_copy_args(item)))
                        new._flags=new._flags|linked_flag
                else: # for loop is finished and not broken
                    del iterators[-1]
        return new_item

    @staticmethod
    def _iter_locals_add_placeholders(itree_item):
        if itree_item:
            itree_class=itree_item.__class__
            placeholder_flag=itree_item._PLACEHOLDER
            add_placeholder=False
            tag_dict={i.tag:-1 for i in itree_item}
            for item in itree_item:
                tag=item.tag
                item._itree_prt_idx[2]=k=tag_dict[tag]=tag_dict[tag]+1
                if item.is_linked and add_placeholder:
                    yield itree_class(item._tag,k, flags=placeholder_flag)  # placeholder item (we store the index in the value)
                    add_placeholder = False
                else:
                    yield item
                    add_placeholder = True

    @staticmethod
    def _iter_deep_locals_add_placeholders_filtered(itree_item,filter_method):
        """
        Most important iterator which iterates over all elements top->down. It returns the index_path of the items.
        Internally the index path in the cache are recalculated during the iteration.

        The design of the iterator allows an iteration speed which is somehow 4x slower as
        normal list iterations which is very quick for a python solution!
        The solution is iterative not recursive to avoid RecursionErrors for deep trees.

        :type itree_item: iTree
        :param itree_item: root item

        :rtype: Iterator
        :return: deep iterator over all index-paths (`.idx_path` attribute)
        """
        iter_locals_add_placeholders=_iTreePrivate._iter_locals_add_placeholders
        if itree_item:
            iterators = [filter(filter_method,itree_item.__iter__())]  # in Python 3.9 lists are quicker than deque
            none_tuple = NONE_TUPLE
            tag_index_dict = [{tag: -1 for tag in itree_item._families.keys()}]
            depth=1
            while iterators:
                for item in iterators[-1]:
                    if item:
                        tag = item._tag
                        tag_dict = tag_index_dict[-1]
                        tag_dict[tag] = fidx = tag_dict[tag] + 1
                        yield depth,fidx, item
                        if item.is_link_root:
                            iterators.extend((none_tuple, filter(filter_method,iter_locals_add_placeholders(item))))
                        else:
                            iterators.extend((none_tuple, filter(filter_method,item.__iter__())))
                        depth = depth + 1
                        tag_index_dict.append({tag: -1 for tag in item._families.keys()})
                        break
                    elif item is None:
                        depth=depth-1
                        del tag_index_dict[-1]
                        del iterators[-1]
                        break
                    else:
                        tag = item._tag
                        tag_dict = tag_index_dict[-1]
                        tag_dict[tag] = fidx = tag_dict[tag] + 1
                        yield depth,fidx, item
                else:  # for loop is finished and not broken
                    del iterators[-1]

    @staticmethod
    def _iter_deep_locals_add_placeholders(itree_item):
        """
        Most important iterator which iterates over all elements top->down.

        The design of the iterator allows an iteration speed which is somehow 5x slower as
        normal list iterations which is very quick for a python solution!
        The solution is iterative not recursive to avoid RecursionErrors for deep trees.

        :type itree_item: iTree
        :param itree_item: root item

        :rtype: Iterator
        :return: deep iterator over all items
        """
        iter_locals_add_placeholders=_iTreePrivate._iter_locals_add_placeholders
        if itree_item:
            iterators = [itree_item.__iter__()]  # in Python 3.9 lists are quicker than deque
            none_tuple = NONE_TUPLE
            tag_index_dict = [{tag: -1 for tag in itree_item._families.keys()}]
            depth=1
            while iterators:
                for item in iterators[-1]:
                    if item:
                        tag = item._tag
                        tag_dict = tag_index_dict[-1]
                        tag_dict[tag] = fidx = tag_dict[tag] + 1
                        yield depth,fidx, item
                        if item.is_link_root:
                            iterators.extend((none_tuple, iter_locals_add_placeholders(item)))
                        else:
                            iterators.extend((none_tuple, item.__iter__()))
                        depth = depth + 1
                        tag_index_dict.append({tag: -1 for tag in item._families.keys()})
                        break
                    elif item is None:
                        depth=depth-1
                        del tag_index_dict[-1]
                        del iterators[-1]
                        break
                    else:
                        tag = item._tag
                        tag_dict = tag_index_dict[-1]
                        tag_dict[tag] = fidx = tag_dict[tag] + 1
                        yield depth,fidx, item
                else:  # for loop is finished and not broken
                    del iterators[-1]
