# -*- coding: utf-8 -*-
"""
This code is taken from the itertree package:
https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license:

The MIT License (MIT)
Copyright © 2022 <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information see: https://en.wikipedia.org/wiki/MIT_License


This part of code contains the main iTree object
"""

from __future__ import absolute_import
import os
import copy
import itertools
from collections import deque
from .itree_data import iTData, iTDataReadOnly, iTDataModel,__NOKEY__,FULL,VALUE
from .itree_filter import *

try:
    # This really recommended for faster operations!
    from blist import blist

    BLIST_ACTIVE = True
except:
    # if not available we take normal list
    blist = list
    BLIST_ACTIVE = False

# This is the second try after self._map[key] was not found!

__GETITEM_RETURN__ = {
    TagMultiIdx: lambda self, key, _: self.__get_tag_idxs__(key),
    TagIdx: lambda self, key, _: self._map[key[0]][key[1]],
    TagIdxStr: lambda self, key, _: self._map[key[0]][key[1]],
    TagIdxBytes: lambda self, key, _: self._map[key[0]][key[1]],
    slice: lambda self, key, _: itertools.islice(super(iTree, self).__iter__(), key.start, key.stop, key.step),
    iTMatch: lambda self, key, _: filter(lambda item: key.check(item), super(iTree, self).__iter__()),
    list: lambda self, key, _: accu_iterator(key, lambda c, k: self[k]),
    # list: lambda self, key, _: iter((self[k] for k in key)),
    tuple: lambda self, key, _: self._map[key[0]][key[1]],
    str: lambda self, key, str_index_separator: self.__getitem__(TagIdxStr(key, str_index_separator)),
    bytes: lambda self, key, str_index_separator: self.__getitem__(TagIdxBytes(key, str_index_separator))
}


# class iTree(iTMagicList):
class iTree(blist):
    """
    This is the main class related to iTrees.

    This object is the parent of a sub-tree (children, sub-children, etc.). The iTree object itself can also be a
    child of a parent iTree object. If this is not the case the iTree object is the root of the tree.

    A iTree object can only be integrated in one tree (one parent only)!

    Each iTree object contains a tag. In case your tags are stings it's recommended to use tag strings without
    wildcards "*","?" and without the standard separators "/" and "#". If you use these characters you might get
    confusing results in find, filter and match operations.

    In general we allow all hashable objects to be used as a tag in the iTree objects (only search operation might be
    limited in this case).
    But we have two exceptions: We do not allow integers and TagIdx objects as tags because those objects used for
    direct item access.

    Different than in dictionaries it is allowed to put multiple times the same tag inside the iTree. The items with
    the same tag are placed and ordered (enumerated) in the related tag-family. They can be reached via TagIdx
    objects by giving the tag, index pair (tag_idx).

    Linked iTree objects will behave different. They have a read only structure (children) and they contain
    the children (tree) of the linked iTree.
    The "local" attributes like tag, data, ... can be set independent from the linked item (local properties).
    To change the tree structure of such an object you must manipulated the source object and reload the link.

    Additionally a iTree object can contain:

    * data - a iTData object to store any kind of python objects

    * couple - you can couple the object to another one by giving a pointer

    * is_temporary - you can mark it as temporary. Those iTree items behave like normal ones. But they will not be
      considered during encoding for storage, etc.

    There are different ways to access the children and sub-children in the tree of a iTree object.

    The standard access for single items is via itree_obj[] (__getitem__()) call.

    More complex access is available via find() and findall() methods. Have a look in the documentation
    related to each method.

    The delivery of access related operations in the iTree objects is for unique targets an
    iTree object and for multi target operations an iterator over the matching items. We don't deliver
    something like a list.

    If really needed an iterator can be easily converted into a list by list() method but this may take a long time
    for huge iterators. The iterator should only be used in the final step of the operation. It's recommended to have
    a look into itertools for better usage of the delivered iterators.

    The design of the object is made to have best possible performance even that it is pure python.
    For more details you may run the performance tests in the test section (But you might have to install
    additional packages run the comparisons and to get the full picture.)

    The function related to iterations iter; iter_children and find_all can be used with an item_filter. By this
    mechanism you can create queries regarding any property in an iTree.

    To initialize the class the following parameters are available

    :param tag: tag string or hashable object used for the iTree identification
    :param data: data dict or item to be stored in the node
    :param subtree: The subtree is a iterable structure that contains sub-items (iTree objects) that should be \
                    the children of this iTree.

                    .. warning:: subtree: In case the given iTree objects have already a parent an implicit copy will
                                          be made.
    """

    # we define some static private variables:
    _is_read_only = False
    _is_temporary = False
    _is_placeholder = False
    _is_linked = False
    # make global local
    _get_return = __GETITEM_RETURN__

    __slots__ = ('_tag', '_parent', '_map', '_coupled', '_data', '_cache', '_def_serializer', '_link')

    def __init__(self, tag, data=None, subtree=None):
        super().__init__()

        t = type(tag)
        if (t is int) or (t is TagIdx):
            raise TypeError('Given tag cannot be used in iTree wrong type (int or TagIdx)')
        self._tag = tag
        self._parent = None
        self._map = None
        self._link = None
        self._coupled = None
        self._cache = (0, 0)

        if subtree is not None:
            self._load_subtree(subtree)

        if data is None:
            self._data = iTData()
        # elif hasattr(data,'is_iTData'):
        elif isinstance(data, iTData):
            self._data = data.__copy__()  # here we make an implicit copy!
        else:
            self._data = iTData(data)

    def init_serializer(self, force=False, exporter=None, importer=None, serializer=None, renderer=None) -> None:
        """
        Method sets the exchange environment that should be used. If you leave the parameters as default,
        the standard objects will be used.

        .. note:: The method logic is called only one time the first time serializing is needed.

        :param force: False (Default) - do not reload in case we have already loaded the items
        :param exporter: exporter object for file export of iTree (dump, dumps)
        :param importer: importer object in ces a file import is done (load, loads)
        :param serializer: Object serializer (especially needed for data objects!)
        :param renderer:  A renderer for pretty print output of the iTree object

        :return: None
        """
        # A post import must be done here against common python rules
        # reason is that a pre import will lead into cyclic importing

        if (not hasattr(self, '_def_serializer')) or (self._def_serializer is None) or force:
            if serializer is None:
                from .itree_serialize import iTStdObjSerializer
                serializer = iTStdObjSerializer
            if exporter is None or importer is None:
                from .itree_serialize import iTStdJSONSerializer
                if exporter is None:
                    exporter = iTStdJSONSerializer(obj_serializer=serializer())
                if importer is None:
                    importer = iTStdJSONSerializer(obj_serializer=serializer())
            if renderer is None:
                from .itree_serialize import iTStdRenderer
                renderer = iTStdRenderer()
            self._def_serializer = (exporter, importer, serializer, renderer)

    def __setitem__(self, key, value):
        """
        put the item in the iTree for (re)setting a child

        HINT: A iTree child can only be child of one iTree (one parent only)
        HINT2: Linked items cannot be changed change the linked item and reload the tree!

        :param key: single identifier for the item can be integer index or TagIdx
        :param value: iTree object that should be child of called iTree

        :return: value
        """
        old_item = self.__getitem__(key)
        try:
            if value._parent is not None:
                if value._parent == self:
                    # check for __iadd__()
                    if super().__getitem__(value.idx) is value:
                        return None
                if value._parent == old_item:
                    # check for __iadd__()
                    if old_item.__getitem__(value.idx) is value:
                        return None
                raise RecursionError('Given item has already a parent iTree!')
        except AttributeError:
            if type(value) is not iTree:
                raise TypeError('In iTree only children of type iTree can be integrated')
            raise
        idx = old_item.idx
        tag_idx = old_item.tag_idx
        old_item._parent = None
        o_tag = tag_idx[0]
        value._parent = self
        super().__setitem__(idx, value)
        v_tag = value._tag
        if v_tag == o_tag:
            family = self._map[v_tag]
            family.__setitem__(tag_idx[1], value)
        else:
            m = self._map
            m[old_item._tag].remove(old_item)
            try:
                family = m.__getitem__(v_tag)
                tag_idx = self.__get_family_insertion_idx(family, idx)
                value._cache = (idx, tag_idx)
                family.insert(tag_idx, value)
            except (KeyError, IndexError):
                m.__setitem__(v_tag, blist((value,)))
        return value

    def __getitem__(self, key, str_index_separator='#'):
        """
        Main getter for items

        If given key targets to only one item we will deliver an iTree. If no matching item is found an IndexError
        or KeyError exception will be raised.

        If the given key targets to multiple items (tag family, slice, iterable of single target keys) and iterator
        will be delivered.

        .. node:: If a tag is given a iterator of the tag family will be returned even if there is only one item
                  with the tag in the tree!!!

        :param key: single target: index, TagIdx or tuple (tag, index) (not recommended)
                    multi target: TagIdx_s; iMatch; slice or an iterable (like list) of these keys
        :return: iTree item or iterator (multi target)
        """
        m = self._map
        try:
            if key in m:
                # give iterator over whole family back
                return iter(m.__getitem__(key))
        except TypeError:
            # we might have a slice!
            pass
        t = type(key)
        if t is int:
            return super().__getitem__(key)
        try:
            return self._get_return[t](self, key, str_index_separator)
        except ValueError:
            raise KeyError('Key %s not found in iTree' % repr(key))

    def __delitem__(self, key):
        """
        delete an item in the tree

        :param key: key targeting the item to be deleted
                    single target: iTree object (remove), index, TagIdx or tuple (tag, index) (not recommended)
                    multi target: TagIdx_s or an iterable (like list) of these keys or a slice

        :return: deleted item
        """
        t = type(key)
        m = self._map
        if t is int:
            del_item = super(iTree, self).pop(key)
            family = m[del_item._tag]
            if len(family) == 1:
                del m[del_item._tag]
            else:
                del family[del_item.tag_idx[1]]
            del_item._parent = None
            return del_item
        elif isinstance(key, TagIdx):
            family = m[key[0]]
            del_item = family.pop(key[1])
            if len(family) == 0:
                del m[del_item._tag]
            # here we go for _delitem__ and not remove because we expect the item "knows" the correct index (cache)
            super(iTree, self).__delitem__(del_item.idx)
            del_item._parent = None
            return del_item
        elif t is TagMultiIdx:
            idxs = key[1]
            family = m[key[0]]
            t2 = type(idxs)
            if t2 is slice:
                del_list = list(itertools.islice(family, idxs.start, idxs.stop, idxs.step))
            elif t2 is list or hasattr(key, '__next__'):
                del_list = [family[k] for k in key]
            else:
                raise TypeError('TagIdx_s object contains invalid indexes')
            for i in del_list:
                super().__delitem__(i.idx)
                tag_idx = i.tag_idx
                family = m[tag_idx.tag]
                del_item = family.pop(tag_idx.idx)
                if len(family) == 0:
                    m.pop(tag_idx.tag)
                del_item._parent = None
            return iter(del_list)
        elif isinstance(key, iTree):
            idx = key.idx
            super().__delitem__(idx)
            tag_idx = key.tag_idx
            family = m[tag_idx.tag]
            del_item = family.pop(tag_idx.idx)
            if len(family) == 0:
                m.pop(tag_idx.tag)
            del_item._parent = None
            return del_item
        else:
            # family tag given?
            try:
                family = m.pop(key)
                for item in family:
                    super().remove(item)
                    item._parent = None
                return iter(family)
            except KeyError:
                # iterator or iterable given?
                if hasattr(key, '__iter__') or hasattr(key, '__next__'):
                    # return an iterator over the slice
                    return_list = list(self[key])
                    for i in return_list:
                        super().__delitem__(i.idx)
                        tag, tag_idx = i.tag_idx
                        family = m[tag]
                        del family[tag_idx]
                        if len(family) == 0:
                            del m[tag]
                        i._parent = None
                    return iter(return_list)
                else:
                    # no valid key found!
                    raise KeyError('No related item (key = %s) found for deletion' % key)

    def __mul__(self, factor):
        """
        Multiplication function a iTree is multiplied (copies) and put in a new iTree:

        my_single_item=iTree('multi')
        multi=my_single_item*1000

        HINT: In this operation multiple copies of the original item generated.

        :param factor: integer to multiply with
        :return: iTree object containing multiplied children
        """
        return iTree(self._tag, data=self._data, subtree=[self.__copy__() for _ in range(factor)])

    def __add__(self, other):
        """
        If two iTree objects are added the children in the two added iTrees are copied and combined
        to a new iTree object the other attributes are taken over from the first iTree in the sum

        :param other: iTree object that should be added
        :return: New iTree object containing copies of all children
        """
        self.extend(other)
        return self

    def __iadd__(self, other):
        try:
            if other._parent is not None:
                raise RecursionError('Given item has already a parent iTree!')
        except AttributeError:
            if type(other) is not iTree:
                raise TypeError('In iTree only children of type iTree can be integrated')
            raise
        self + [other]
        return self

    def __iter__(self, item_filter=None):
        """
        standard iterator over all items in the iTree
        :param item_filter: ALL = default
        :return:
        """
        return self.iter_children(item_filter=item_filter)

    def __contains__(self, item):
        """
        checks if an iTree object is part of the iTree
        :param item: iTree object we searching for
        :return:
        """
        if id(item._parent) == id(self):
            return True
        if item._parent is None:
            return False
        return item._parent in self

    def __eq__(self, other):
        """
        A iTree object is always unique we test therefore just for matching object IDs
        This is needed for quick index findings!
        ..node:: To check if properties content is equal use equal() instead
        :param other: iTree object to compare with
        :return:
        """
        return id(self) == id(other)

    def __ne__(self, other):
        """
        A iTree object is always unique we test therefore just for object for not matching IDs
        This is needed for quick index findings!
        ..node:: To check if attribute content is equal use not equal() instead
        :param other: other item to be compared with
        :return: True/False
        """
        if id(self) != id(other):
            return True
        return False

    def __lt__(self, other):
        """
        less than is a size comparison (length are compared)
        :param other: iTree object self should be compared with
        :return: True/False
        """
        return len(self) < len(other)

    def __le__(self, other):
        """
        less than or equal is a size comparison (length are compared)
        :param other: iTree object self should be compared with
        :return: True/False
        """
        return len(self) <= len(other)

    def __gt__(self, other):
        """
        greater than is a size comparison (length are compared)
        :param other: iTree object self should be compared with
        :return: True/False
        """
        return len(self) > len(other)

    def __ge__(self, other):
        """
        greater than or equal is a size comparison (length are compared)
        :param other: iTree object self should be compared with
        :return: True/False
        """
        return len(self) >= len(other)

    def __repr__(self):
        """
        create representation string from which the object can be reconstructed via eval (might not work in case of
        data that do not have a working repr method)
        :return: representation string
        """
        repr_str = '%s(%s' % (self.__class__.__name__,repr(self._tag))
        if not self._data.is_empty:
            if self._data.is_no_key_only:
                repr_str = repr_str + ', data=%s' % repr(self.d_get())
            else:
                repr_str = repr_str + ', data=%s' % repr(self._data)
        subtree = super(iTree, self).__repr__()
        if subtree[0] == 'b':
            # we shorten blist from definition
            subtree = subtree[6:-1]
            return repr_str + ', subtree=%s)' % subtree
        else:
            return repr_str + ')'

    def __hash__(self):
        """
        The hash operation is available but not a quick operation!
        ..node::: We do here not consider, parent and coupled item
        :return: integer hash
        """
        return hash((tuple(self.iter_children()), (self._tag, self._data)))

    def __len__(self):
        return super(iTree, self).__len__()

    # unsupported operands
    def __sub__(self, other):
        return self.__unsupport_op(other)

    def __isub__(self, other):
        return self.__unsupport_op(other)

    def __imul__(self, other):
        return self.__unsupport_op(other)

    def __rmul__(self, other):
        return self.__unsupport_op(other)

    def __reversed__(self):
        return self.__unsupport_op()

    def __reduce__(self):
        return self.__unsupport_op()

    def __reduce_ex__(self, protocol):
        return self.__unsupport_op()

    def sort(self, *arg, **kwargs):
        """
        sort operation is not supported, method exists just because super class supports it.
        Here a TypeError will be raised.
        """
        return self.__unsupport_op()

    # properties

    @property
    def data(self):
        """
        delivers the data-attribute object of the item

        :return: data object of the item
        """
        return self._data

    # These are the mandatory methods we expect in the data object

    def d_set(self, *args, **kwargs):
        """
        set function for a data-attribute

        In case the standard iTData object is used we have:

        :param key: give key under which the data will be stored, in case data is None the first key parameter is taken
                    as data object and it is stored in the "__NOKEY__" item

        :param value: data value the object that should be stored in the data structure of this iTree

        :return:  None
        """
        return self._data.__setitem__(*args, **kwargs)

    def d_get(self, key=__NOKEY__,return_type=VALUE):
        """
        get function for a data attribute

        In case the standard iTData object is used we have:

        :param key: key under which the data is stored, in case no key is given the "__NOKEY__" item will be returned

        :return: data attribute object
        """
        return self._data.__getitem__(key,return_type)

    def d_update(self, *args, **kwargs):
        """
        update function data-attribute

        In case the standard iTData object is used we have:

        :param key: give key under which the data will be stored, in case data is None the first key parameter is taken
                    as data object and it is stored in the "__NOKEY__" item

        :param value: data value the object that should be stored in the data structure of this iTree

        :return:  None
        """
        return self._data.update(*args, **kwargs)

    def d_check(self, value,key=__NOKEY__):
        """
        check if the given data-item can be stored under the given key. The check make only sense in case there is
        a iTreeDataModel or matching object is already stored under the key

        :exception:  check will raise an iDataValueError or  iDataTypeError exception in case the value is not matching
                     in case given key is not found a KeyError will be raised

        :param value: data value the object that should be checked

        :param key: give key under which contains the DataModel, in case key is not given the "__NOKEY__" item will be used

        :return: valid value
        """
        try:
            value=self._data.__getitem__(key=key, _return_type=FULL).validator(value)
        except AttributeError:
            pass
        except KeyError:
            if key!=__NOKEY__:
                raise
        return value

    def d_pop(self, *args, **kwargs):
        """
        data related pop (will delete the given key from data-attribute)

        :return: deleted value
        """
        return self._data.pop(*args, **kwargs)

    def d_del(self, *args, **kwargs):
        """
        data related del (will delete the given key)

        :return: deleted value
        """
        return self._data.__delitem__(*args, **kwargs)

    @property
    def parent(self):
        """
        property contains the parent item

        :return: iTree parent object (or None in case no parent exists)
        """
        return self._parent

    @property
    def is_root(self):
        """
        is this item a root item (has no parent)

        :return: True/False
        """
        return self._parent is None

    @property
    def root(self):
        """
        property delivers the root item of the tree

        :return: iTree root item
        """
        # We use an iterative not recursive solution here because we allow tree depth > recursion limit of the
        # interpreter!
        p = self
        while 1:
            p1 = p._parent
            if p1 is None:
                return p
            p = p1

    @property
    def is_read_only(self):
        """
        In contrast to iTreeReadOnly class this is False

        :return: False
        """
        return self._is_read_only

    @property
    def is_temporary(self):
        """
        In contrast to iTreeTemporary class this is False

        :return: False
        """
        return self._is_temporary

    @property
    def is_placeholder(self):
        """
        In contrast to iTreePlaceholder class this is False

        :return: False
        """
        return self._is_placeholder

    @property
    def is_linked(self):
        """
        In contrast to iTreeLinked class this is False

        :return: False
        """
        return self._is_linked

    @property
    def link_item(self):
        """
        in case we have "covered" a linked item this property delivers the original linked item
        (mainly for internal use)

        :return: None - no linked item
                 iTreeLink object the covered item
        """
        if self._link is not None:
            return self._link.link_item
        return None

    @property
    def pre_item(self):
        """
        delivers the pre item (predecessor) of this object

        :return: iTree predecessor or None (no match)
        """
        idx = self.idx - 1
        if idx < 0:
            return None
        return super(iTree, self._parent).__getitem__(idx)

    @property
    def post_item(self):
        """
        delivers the post item (successor)

        :return: iTree successor or None (no match)
        """
        idx = self.idx + 1
        sl = super(iTree, self._parent)
        if idx < sl.__len__():
            return sl.__getitem__(idx)
        return None

    @property
    def _a_debug_children_list(self):
        """
        This is a property for debugging only do not use for manipulations!

        :return: list of children
        """
        return list(self.iter_children())

    @property
    def _a_debug_children_map(self):
        """
        This is a property for debugging only do not use for manipulations!

        :return: dict of children
        """
        return self._map

    @property
    def depth_up(self):
        """
        delivers the distance (number of levels) to the root element of the tree

        :return: integer
        """
        # We use an iterative not recursive solution here because we allow tree depth > recursion limit of the
        # interpreter!
        p = self
        i = 0
        while 1:
            p = p._parent
            if p is None:
                return i
            i += 1

    @property
    def max_depth_down(self):
        """
        delivers the max_depth in the direction of the children

        :return: integer maximal children depth
        """
        if self.__len__() == 0:
            return 0
        max_depth = 0
        items = [self]
        while 1:
            new_items = []
            deque((new_items.extend(list(i.iter_children())) for i in items), maxlen=0)
            if len(items) == 0:
                break
            else:
                max_depth += 1
            items = new_items
        return max_depth - 1

    @property
    def idx_path(self):
        """
        delivers the a list of indexes from the root to this item

        :return: list of index integers (here we do not deliver an iterator)
        """
        # We use an iterative not recursive solution here because we allow tree depth > recursion limit of the
        # interpreter!
        p = self
        idx_list = []
        while 1:
            if p is None:
                return idx_list
            idx = p.idx
            if idx is None:
                break
            idx_list.insert(0, idx)
            p = p._parent
        return idx_list

    @property
    def tag_idx_path(self):
        """
        delivers the a list of TagIdx objects from the root to this item

        :return: list of TagIdx (here we do not deliver an iterator)
        """
        # We use an iterative not recursive solution here because we allow tree depth > recursion limit of the
        # interpreter!
        p = self
        idx_list = []
        while 1:
            tag_idx = p.tag_idx
            if tag_idx is None:
                return idx_list
            idx_list.insert(0, tag_idx)
            p = p._parent

    @property
    def tag_idx(self):
        """
        Get the TagIdx object related to this object
        (contains the tag and the index of the object in the tag-family)

        :return: TagIdx
        """
        parent = self.parent
        if parent is None:
            return None
        # we use cached index to be quicker
        cache = self._cache
        c_idx = cache[1]
        family = parent._map[self._tag]
        try:
            if family[c_idx] is self:
                return TagIdx(self._tag, c_idx)
        except IndexError:
            pass
        # full search cached index must be updated
        idx = parent._map[self._tag].index(self)
        self._cache = (cache[0], idx)
        return TagIdx(self._tag, idx)

    @property
    def tag(self):
        """
        This objects tag

        :return: tag object
        """
        return self._tag

    @property
    def idx(self):
        """
        Index of this object in the iTree

        :return: integer index
        """
        parent = self._parent
        if parent is None:
            return None
        # we use cached index to be quicker
        cache = self._cache
        sl = super(iTree, parent)  # do not delete parameters here!
        c_idx = cache[0]
        try:
            if sl.__getitem__(c_idx) is self:
                return c_idx
        except IndexError:
            pass
        # cached index must be updated
        idx = sl.index(self)
        self._cache = (idx, cache[1])
        return idx

    @property
    def coupled_object(self):
        """
        The iTree object can be couple with another python object. The pointer to the object is stored and can be
        reached via this property. (E.g. this can be helpful when connecting the iTree with a visual element
        (tree-list item) in a GUI)

        :return: pointer to coupled object
        """
        try:
            return self._coupled
        except AttributeError:
            return None

    # set properties
    def set_coupled_object(self, coupled_object):
        """
        User can couple this object with others with the help of this attribute
        .. note:: E.g. this might be an object in a GUI that are related to this item

        :param couple_object: object pointer to the object that should be coupled with this iTree item
        """
        self._coupled = coupled_object


    def equal(self, other, check_parent=False, check_coupled=False):
        """
        compares if the data content of another item matches with this item

        :param other: other iTree

        :param check_parent: check if item has same parent object too? (Default False)

        :param check_coupled: check the couple object too? (Default False)

        :return: boolean match result (True match/False no match)
        """
        if self == other:
            return True
        if type(other) is not iTree:
            return False
        if check_parent:
            if other._parent != self._parent:
                return False
        if self._map is None:
            l1 = 0
            if other._map is not None:
                return False
            l2 = 0
        else:
            l1 = len(self._map)
            l2 = len(other._map)
        my_data = (self._tag, super(iTree, self).__len__(), l1)
        other_data = (other._tag, super(iTree, other).__len__(), l2)
        if my_data != other_data:
            return False
        for si, oi in zip(other.iter_children(), self.iter_children()):
            if not si.equal(oi):
                return False
        if check_coupled:
            try:
                if self._coupled != other._coupled:
                    return False
            except AttributeError:
                if hasattr(self, '_coupled'):
                    return False
                if hasattr(other, '_coupled'):
                    return False
        return True

    def __copy__(self):
        """
        create a copy of this item

        The difference in between copy and deepcopy for iTree is just that we do in deepcopy a copy
        of all data items too. In copy we just copy the iTData object not the items itself, they stay as pointers
        to the original objects.

        The function is used internally in extend operations too. And we can see (profiler) that
        improvements in this method might have big impact.

        :return: copied iTree object
        """
        new = self.__class__(self._tag,
                    data=self._data.__copy__(),
                    subtree=[i.__copy__() for i in super(iTree, self).__iter__()]
                    # here we create a recursion -> subtree is copied!!
                    )

        return new

    def copy(self, *args, **kwargs):
        """
        create a copy of this item

        The difference in between copy and deepcopy for iTree is just that we do in deepcopy a copy
        of all data items too. In copy we just copy the iTData object not the items itself, they stay as pointers
        to the original objects.

        The function is used internally in extend operations too. And we can see (profiler) that
        improvements in this method might have big impact.

        :return: copied iTree object
        """
        return self.__copy__()

    def __deepcopy__(self):
        """
        create a deepcopy of this item

        The difference in between copy and deepcopy for iTree is just that we do in deepcopy a copy
        of all data items too. In copy we just copy the iTData object not the items itself, they stay as pointers
        to the original objects.

        :return: deep copied new iTree object
        """
        new = self.__class__(self._tag,
                    data=self._data.__deepcopy__(),
                    subtree=[i.__deepcopy__() for i in super(iTree, self).__iter__()]  # here we create a recursion!
                    )
        return new

    def deepcopy(self, *args, **kwargs):
        """
        create a deepcopy of this item

        The difference in between copy and deepcopy for iTree is just that we do in deepcopy a copy
        of all data items too. In copy we just copy the iTData object not the items itself, they stay as pointers
        to the original objects.

        :return: deep copied new iTree object
        """
        return self.__deepcopy__()

    def count(self, item_filter=None):
        """
        count the number of children that match to the given filter
        :: note: The operation is not very quick on huge iTrees and complicate filters!

        :param item_filter:

        :return: integer number of children matching to the filter
        """
        if item_filter is None:
            return super(iTree, self).__len__()
        return len(list(filter(item_filter, super(iTree, self).__iter__())))

    def count_all(self, item_filter=None):
        """
        count deep the number of children and sub children the element has and that match to the given filter
        :: note: The operation is not very quick on huge iTrees and complicate filters!

        :param item_filter:

        :return: integer number of children matching to the filter
        """
        cnt = 0
        i = -1
        for i, item in enumerate(self.iter_children(item_filter=item_filter)):
            cnt += item.count_all()
        cnt += (i + 1)
        return cnt

    # deep getter
    def get_deep(self, key_list):
        """
        deep key access
        the function is a replacement for `self[key_list[0]][key_list[1]]...[key_list[-1]]`
        but you can also feed with an iterator

        dives into the tree `key_list=[1,0,2]` -> second element level 1 -> first element level 2 ->
        third element level 3
        -> same as `self[1][0][2]`

        .. note:: Each key in the key list must target to a single item only!
                     E.g. do not use tags here they deliver always a family iterator not a single item
                     (the method will raise an exception). Use index integers or TagIdx objects instead

        :param key_list:  list or iterator of keys (indexes,TagIdx, tuple(tag,index) -> only in case no tuple tags!

        :return: iTree object the key list targets
        """
        item = self
        for key in key_list:
            item = item.__getitem__(key)
        return item

    # structural manipulations

    def clear(self):
        """
        deletes all children
        and data!
        All flags stay unchanged!
        """
        self._data = None
        self._coupled = None
        super().clear()
        self._map = {}

    def insert(self, insert_key, item):
        """
        Insert an item before a specific position

        :param insert_key: position key (integer index or TagIdx)

        :param item: item that should be inserted in the tree (new child)
        """
        try:
            if item._parent is not None:
                raise RecursionError('Given item has already a parent iTree!')
        except AttributeError:
            if not isinstance(item, iTree):
                raise TypeError('In iTree only children of type iTree can be integrated')
            raise
        if type(insert_key) is int:
            idx = insert_key
            if idx < 0:
                idx = super().__len__() - idx
        elif isinstance(insert_key, TagIdx):
            idx = self.__getitem__(insert_key).idx
        else:
            raise TypeError('In iTree only children of type iTree can be integrated')
        item._parent = self
        super().insert(idx, item)
        tag = item._tag
        try:
            m = self._map
            if m.__contains__(tag):
                family = m.__getitem__(tag)
                t_idx = self.__get_family_insertion_idx(family, idx)
                family.insert(t_idx, item)
            else:
                m.__setitem__(tag, blist((item,)))
                t_idx = 0
        except (AttributeError, IndexError):
            self._map = {tag: blist((item,))}
            t_idx = 0
        item._cache = (idx, t_idx)

    def append(self, item):
        """
        Append the given iTree object to the tree (new last child)

        :except: raise TypeError in case iTree object has already a parent

        :param item: iTree object to be appended

        :return: True in case append was successful
        """
        try:
            if item._parent is not None:
                raise RecursionError('Given item has already a parent iTree!')
        except AttributeError:
            if not isinstance(item, iTree):
                raise TypeError('In iTree only children of type iTree can be integrated')
            raise
        # append item:
        item._parent = self
        # append to blist:
        sl = super()
        idx = sl.__len__()
        sl.append(item)
        # append to map
        tag = item._tag
        if idx:
            m = self._map
            if m.__contains__(tag):
                family = m.__getitem__(tag)
                t_idx = family.__len__()
                family.append(item)
            else:
                # first time tag is used!
                t_idx = 0
                m.__setitem__(tag, blist((item,)))
        else:
            self._map = {tag: blist((item,))}
            t_idx = 0
        item._cache = (idx, t_idx)
        return True

    def appendleft(self, item):
        """
        Append the given iTree object to the left of the the tree (new first child)

        :except: raise TypeError in case iTree object has already a parent

        :param item: iTree object to be appended
        """
        return self.insert(0, item)

    def extend(self, extend_items):
        """
        We extend the iTree with given items (multi append)

        .. note:: In case the extend items have already a parent an implicit copy will be made. We do this because
               we might get an iTree-object as extend_items parameter and then the children will have automatically a
               parent even that the parent object might be a temporary one.

        :param extend_items: iterable object that contains iTree objects as items

        :return: True
        """
        # collect for operation
        return self._load_subtree(extend_items)

    def extendleft(self, extend_items):
        """
        We extend the iTree with given items in the beginning (multi appendleft)

        .. note:: In case the extend items have already a parent an implicit copy will be made. We do this because
               we might get an iTree-object as extend_items parameter and then the children will have automatically a
               parent even that the parent object might be a temporary one.

        .. note:: The `extendleft()` operation is a lot slower then the normal extend operation

        :param extend_items: iterable object that contains iTree objects as items
        """
        # start_idx=len(extend_items)-1
        # collect for operation
        sl = super(iTree, self)
        m = self._map
        il = len(extend_items)
        for i in range(il):
            item = extend_items[il - i - 1]
            if item._parent is not None:
                item = item.copy()
            item._parent = self
            item._cache = (0, 0)
            sl.insert(0, item)
            tag = item._tag
            try:
                family = m.__getitem__(tag)
                family.insert(0, item)
            except KeyError:
                m.__setitem__(tag, blist((item,)))
            except AttributeError:
                self._map = m = {tag: blist((item,))}
        return True

    def pop(self, key=-1):
        """
        pop the item out of the tree, if no key is given the last item will be popped out

        :param key: specific identification key for an item (integer index, TagIdx)

        :return: popped out item (parent will be set to None)
        """
        return self.__delitem__(key)

    def popleft(self):
        """
        pop the first item out of the tree

        :return: popped out item (parent will be set to None)
        """
        return self.__delitem__(0)

    def remove(self, item):
        """
        remove the given item out of the tree (delete the child)

        :param item: iTree object that should be removed from the tree

        :return: removed item will be returned (parent is set to None)
        """
        return self.__delitem__(item.idx)

    def move(self, insert_key):
        """
        move the item in another position

        :param insert_key: item will be insert before this key
        """
        if self._parent is None:
            raise LookupError('Given item is not a children of a iTree!')
        parent = self._parent
        # check if target exists:
        if type(insert_key) is not int:
            target_idx = parent.__getitem__(insert_key).idx
        else:
            target_idx = insert_key
        src_idx = self.idx
        move_item = parent.__delitem__(src_idx)
        parent.insert(target_idx, move_item)

    def rename(self, new_tag):
        """
        give the item a new tag

        :param new_tag: new tag object string or hashable object
        """
        t = type(new_tag)
        if t is int or t is TagIdx:
            raise TypeError('Given tag cannot be used in iTree wrong type (int or TagIdx)')
        parent = self.parent
        if parent is None:
            self._tag = new_tag
            return
        pm = parent._map
        tag = self._tag
        # remove old tag in the map-dict
        family = pm.__getitem__(tag)
        if len(family) == 1:
            pm.__delitem__(tag)
        else:
            family.remove(self)
        # insert new tag
        self._tag = new_tag
        if new_tag in pm:
            new_family = pm.__getitem__(new_tag)
            idx = self.__get_family_insertion_idx(new_family, self.idx)
            new_family.insert(idx, self)
            self._cache = (self._cache[0], idx)
        else:
            # create new family
            pm.__setitem__(new_tag, blist((self,)))
            self._cache = (self._cache[0], 0)

    def reverse(self):
        """
        reverse the order of all children in the iTree object

        """
        super(iTree, self).reverse()
        for item in self._map.values():
            item.reverse()

    def rotate(self, n):
        """
        rotate children of the iTree object n times
        (rotate  1 times means move last element to first position)

        :param n:

        """
        if n > 0:
            for i in range(n):
                rot_item = self.pop()
                self.insert(0, rot_item)
        elif n < 0:
            for i in range(n):
                rot_item = self.popleft()
                self.__iadd__(rot_item)

    # iterators

    def iter_all(self, item_filter=None, filter_or=True):
        """
        main iterator for whole tree runs in top-> down order
        e.g.
        ::
            iTree('child')
             └──iTree('sub0')
                 └──iTree('sub0_0')
                 └──iTree('sub0_1')
                 └──iTree('sub0_2')
                 └──iTree('sub0_3')
             └──iTree('sub1')
                 └──iTree('sub1_0')
        will be iterated like:
        ::
             iTree('child')
             iTree('sub0')
             iTree('sub0_0')
             iTree('sub0_1')
             iTree('sub0_2')
             iTree('sub0_3')
             iTree('sub1')
             iTree('sub1_0')

        :param item_filter: filter for filter the items you can give a filter constant or
                            a method for filtering (should return True/False)

        :param filter_or:

                          * True  - we combine the filtering with or this means even if we have no match in the higher
                            levels of the tree we will go deeper to find matches

                          * False - filters are combined with and which means children will only be parsed in
                            case the parent matches also to the filter condition

        :return: iterator
        """
        if filter_or:
            for item in self.iter_children(item_filter=None):
                if item_filter is None or item_filter(item):
                    yield item
                for subitem in item.iter_all(item_filter=item_filter, filter_or=filter_or):
                    yield subitem
        else:
            for item in self.iter_children(item_filter=item_filter):
                yield item
                for subitem in item.iter_all(item_filter=item_filter, filter_or=filter_or):
                    yield subitem

    def iter_all_bottom_up(self, item_filter=None, filter_or=True):
        """
        main iterator for whole tree runs in down-> top order (We start at the children and afterwards the parents:
        e.g.:
        ::
            iTree('child')
             └──iTree('sub0')
                 └──iTree('sub0_0')
                 └──iTree('sub0_1')
                 └──iTree('sub0_2')
                 └──iTree('sub0_3')
             └──iTree('sub1')
                 └──iTree('sub1_0')
        Will be iterated:
        ::
             iTree('sub0_0')
             iTree('sub0_1')
             iTree('sub0_2')
             iTree('sub0_3')
             iTree('sub0')
             iTree('sub1_0')
             iTree('sub1')
             iTree('child')

        :param item_filter: filter method for filtering (should return True/False when fet with an item) or
                            iTFilter object

        :param filter_or:

                          * True - we combine the filtering with or this means even if we have no match in the higher
                            levels of the tree we will go deeper to find matches

                          * False - filters are combined with and which means children will only be parsed in
                            case the parent matches also to the filter condition

        :return: iterator
        """
        if filter_or:
            for item in self.iter_children(item_filter=None):
                for subitem in item.iter_all(item_filter=item_filter, filter_or=filter_or):
                    yield subitem
                if item_filter is None or item_filter(item):
                    yield item
        else:
            for item in self.iter_children(item_filter=item_filter):
                for subitem in item.iter_all(item_filter=item_filter, filter_or=filter_or):
                    yield subitem
                yield item

    def iter_children(self, item_filter=None):
        """
        main iterator in children level

        :param item_filter: the items can be filtered by giving a filter constants or giving a filter method or
                            iTFilter object

        :return: iterator
        """
        if item_filter is None:
            return super(iTree, self).__iter__()
        else:
            return filter(item_filter, super(iTree, self).__iter__())

    def iter_tag_idxs(self, item_filter=None):
        """
        iter over all children and deliver the children TagIdx

        :param item_filter: the items can be filtered by giving a filter constants or giving a filter method or
                            iTFilter object

        :return: iterator over the TagIdx of the children
        """
        tag_cnts = {}
        for item in self.iter_children(item_filter=item_filter):
            tag = item._tag
            try:
                tag_cnts[tag] = cnt = tag_cnts[tag] + 1
            except KeyError:
                tag_cnts[tag] = cnt = 0
            yield TagIdx(tag, cnt)

    def iter_tag_idxs_all(self, item_filter=None):
        """
        Delivers an iterator over all items tag_idx_paths

        :param item_filter: the items can be filtered by giving a filter constants or giving a filter method or
                            iTFilter object

        :return: iterator over tuples of tag_idxs_paths of all items
        """
        tag_cnts = {}
        for item in self.iter_children(item_filter):
            tag = item._tag
            try:
                tag_cnts[tag] = cnt = tag_cnts[tag] + 1
            except KeyError:
                tag_cnts[tag] = cnt = 0
            ti_l = (TagIdx(tag, cnt),)
            yield ti_l
            for tag_idx_list in item.iter_tag_idxs_all(item_filter):
                yield ti_l + tag_idx_list

    def iter_idxs_all(self, item_filter=None):
        """
        Delivers an iterator over all items index path tuples
        .. note:: This method is mainly usd for internal proposes (max_depth_down)

        :param item_filter: item_filter filter method might be used

        :return: iterator over tuples of index paths of all items
        """
        i = 0
        for item in self.iter_children(item_filter):  # not use enumerate here because this consumes the iterator!
            i = i + 1  # quicker then i+=1  i =
            t = (i,)
            yield t
            for idx_list in item.iter_idxs_all(item_filter):
                yield t + idx_list

    def find_all(self, key_path, item_filter=None, str_path_separator='/', str_index_separator='#'):
        """
        The find all function works on all levels of the tree. The key_path given (e.g. a list of indexes) addresses
        the items into the depth first item first level, second item second level,....

        The method returns always an iterator or in case of no match an empty list! If you target to unique objects
        you will get anyway an iterator containing this unique element.

        .. warning:: It's possible to create invalid recursions when constructing the key_path. In these cases the
                  recursion depth exceeded exception will be raised by the interpreter

        In case the target in the upper keys is not unique, all matches will be delivered!
        e.g. The operation `my_tree.find_all(['child','sub_child'])` takes first all items in the "child" family:

             `TagIdx('child',0),TagIdx('child',1),...TagIdx('child',n)` in an iterator and in the next step the function
             will go one level deeper and will cumulate all the 'sub_child' families in these items as the result:

             This means we have something like this:

             `my_tree[TagIdx('child',0)][TagIdx('sub_child',0)],my_tree[TagIdx('child',0)][TagIdx('sub_child',1)],...,`

             `my_tree[TagIdx('child',1)][TagIdx('sub_child',0)],my_tree[TagIdx('child',0)][TagIdx('sub_child',1)],...,`

             ...

             and in case of no match in the keys items are skipped.

             .. note::  It's not at all the same as: my_tree['child']['sub_child'] -> this operation will raise an
                        exception!

        .. note::  When addressing a single item it's quicker (~10x faster depending on tree depth) to use the
                   `get_deep()` method instead of the `find_all()` method.

        The key_path parameter is very flexible in case of the objects you put in. We have several possibilities:

        0. Special keys: We have the following special keys that might be used in the key_path:

            - "/" default path separator (might be changed by str_path_separator parameter)
              If this is the first key the `find_all()` search will be started in the root element not in the
              element the method is called.

              .. note::  Be careful with "//" or "/" placed not in the beginning of the path this will rollback the
                     `find_all()` to the root which means anything in the key_path before this key will be ignored.

            - "*"-wildcard will iterate over all children of the item

            - "**"-wildcard will iterate over all items of the item. The item itself is the first element
              of the iterator delivered

              .. note::  `find_all('**')` creates an different iterator then `iter_all()`
                         `list(my_tree.find_all('**')) = [my_tree] + list(my_tree.iter_all())`

            .. warning::  It's always recommended to avoid the usage of string tags containing functional characters
                          like "**","*","/","#","?". E.g. In case the iTree contains a family with the tag "/" or "*"
                          or "**" the related family will be delivered. The special functionality is blocked in this
                          moment (for "/" you might use the str_path_separator parameter to keep the functionality).
                          Also filtering via iTMatch objects is limited in this case.

        1. Give normal keys like in `__getitem__()` method:
           normal keys can be:

             * index integers
             * tag strings
             * TagIdx,TagIdxStr,TagIdxBytes
             * TagMultiIdx,slices
             * for index lists you must give[[1,2,3,4]] because first level will be interpreted as
             * a list targeting into the depth of the tree

             e.g. by index

                 * `my_tree.find_all(1)` is same as `my_tree[1]`
                 * `my_tree.find_all('child')` is same as `my_tree['child']`
                 * `my_tree.find_all(TagIdx('child',1))`is same as `my_tree[TagIdx('child',1)]`
                 ...

        2. Give a list of normal keys:

           e.g. by index

            * `my_tree.find_all([1,2])`is same as my_tree[1][2]
            * `my_tree.find_all(['child','sub_child'])` delivers an iterator over all "sub_child" families found
               in all "child" families
            * `my_tree.find_all([TagIdx('child',1),TagIdx('sub_child',1)])`is  same as
              `my_tree[TagIdx('child',1)][TagIdx('sub_child',1)]`
            ...

        3. Give `iTMatch()` object or list of `iTMatch()` objects:

           An iterator of all matching tags will be created the matches will be combined with the and operation.
           You can also use an item_filter containing the Filter.iTFilterItemTagMatch to have the same functionality.
           In case a list is given the find_all() function is again going one level deeper for each element in the list.

        :param key_path: iterable/iterator that addresses items in the tree (see above explanations and examples)

        :param item_filter: item_filter method

        :param str_path_separator: In case of string tags the user can give also strings that are internally casted
                                   into a list by using the str_path_separator (default="/")
                                   e.g.: "/child_tag/sub_child_tag" -> ["child_tag","sub_child_tag"]

        :param str_index_separator: In case of string tags the user can give TgaIdx also by string definition this is
                                    the separator used to separate the index number from the tag (default="#")
                                    e.g. "child_tag#89" -> TagIdx("child_tag",89)

        :return: iterator over the matches or in case of no match found an empty list -> []

        """

        sl = super()
        m = self._map
        if m is None:
            m = {}
        try:  # direct match ?
            if key_path in m:
                return self.__build_find_all_result(m.__getitem__(key_path), item_filter)
        except TypeError:
            pass
        t = type(key_path)
        if t is str:
            lkp = key_path.__len__()
            if lkp == 0:
                return []
            if key_path[0] == '*':
                if lkp == 1:
                    # from here on the item must have children!
                    if sl.__len__() == 0:
                        return []
                    return itertools.chain(self.__build_find_all_result(self, item_filter),
                                           self.iter_children(item_filter=item_filter))
                if key_path[1] == '*':
                    if lkp == 2:
                        return self.iter_all(item_filter=item_filter)
            try:
                return self.__build_find_all_result(self.__getitem__(key_path, str_index_separator), item_filter)
            except KeyError:
                pass
            # from here on we create a list from the given keys by splitting
            key_list = key_path.split(str_path_separator)
            if len(key_list) == 1:  # single key this means the item was not found!
                return []
            if key_list[0] == '':
                # we must ensure we start from the root
                return self.root.find_all(key_list[1:], item_filter, str_path_separator, str_index_separator)
            return self.find_all(key_list, item_filter, str_path_separator, str_index_separator)
        # for those objects we do a direct search: (list is not in because in fnd we go deeper!!)
        if t in (int, str, TagIdx, TagIdxStr, TagIdxBytes, TagMultiIdx, iTMatch, slice):
            return self.__build_find_all_result(self.__getitem__(key_path, str_index_separator), item_filter)
        # from here on we expect a list or iterator
        # analyse iterator:
        key, new_key_iter = self.__extract_first_iter_items(key_path)
        # create the result of the key (first item)
        if key is None:
            # somethings wrong (empty iterator)
            return []
        if key == str_path_separator:
            if key not in m:
                # we switch up to root!
                if new_key_iter is not None:
                    return self.root.find_all(new_key_iter)
                else:
                    return self.__build_find_all_result(self.root, item_filter)
        try:
            result = self.__build_find_all_result(self.__getitem__(key, str_index_separator), item_filter)
            if not result:
                return []
        except (IndexError, KeyError):
            if type(key) is not str:
                # we had no match on the object!
                return []
            if key[0] == '*':
                if len(key) == 1:
                    result = self.iter_children(item_filter=item_filter)
                else:
                    if key[1] == '*':
                        if len(key) == 2:
                            result = itertools.chain(self.__build_find_all_result(self, item_filter),
                                                     self.iter_all(item_filter=item_filter))
                        else:
                            return []
            else:
                return []
        if new_key_iter is None:
            return result
        else:
            sub_method = lambda c, item: item.find_all(new_key_iter, item_filter,
                                                       str_path_separator, str_index_separator)
            # for debugging:
            # results = [item.find_all(new_key_iter, item_filter,
            #                          str_path_separator, str_index_separator) for item in result]
            # return result
            return itertools.chain.from_iterable(accu_iterator(result, sub_method))

    def find_all2(self, key_path, item_filter=None, str_path_separator='/', str_index_separator='#',
                  _initial=True):
        """
        Method is outdated use find_all instead!

        The find_all function targets over multiple levels of the datatree, it returns a list or iterator of the
        matching  items!

        The key_path parameter given is normally a list. This can be a list of keys or TagIdx objects. The function
        will search for the first item in the first level, fo next item in the next level and so on...

        Absolut and relative key_paths:

        If the first item is the separator (default: '/') the find search is like an absolute path and we start at the
        root of the datatree.
        If the first item is different, the key_path is relative and we start from the actual
        item and search the children and sub-children.

        Single string key_path:
        If the user searches for string type tags he can use a string with a separator (default: '/') in between the
        tags (These type of key_paths will be implicit translated in a list in the function). An index separator
        (default = '#') in between the tag and the index can also be used to identify to identify items in the tag
        family. If the key_path argument is already a list the single keys will not be parsed regarding the
        str_path_separator anymore.

        HINT: Quickest find operations can be performed by giving a list containing index integers or TagIdx objects

        The items can be filtered regarding specific content, for this a look into the available filer constructors:
        create_xxx_item_filter() might be interesting. The filter method or the filter constant can be given
        in the item_filter parameter

        The parameters in detail:

        :param key_path: single key or list of keys
                    identification path for the item/items to be searched.
                    Possible keys:
                    integer - behaves like normal __getitem__() -> itree_item[key]
                    TagIdx- behaves like normal __getitem__() -> itree_item[key]
                    iTreeTagSlice - select a tag sliced group of sub-elements
                    iTMatch - search pattern can be used too, but keep in mind it must deliver a unique result!
                    Slice - a slice of indexes (like a special index list)
                    string - will be parsed by the separators
                    iterable list/tuple/deque,... -
                             run over single keys if sub_key is again an iterable it will be taken as an index list
                             (e.g. [1,2,3] - will go deeper in the tree 1. item; 2. subitem; 3. subsubitem
                             but [[1,2,3]] - will stay in the first level and deliver 1. item; 2. item; 3. item)

        :param item_filter: filters the item content regarding NORMAL, TEMPORARY and LINKED flag or a given
                            filtering method
        :param str_path_separator: separator character in case of strings for the search levels (default: "/")
        :param str_index_separator: separator character for given tag indexes (default: "#")
        :param _initial: Internal flag that should protect against cyclic constructs
        :return: list or iterator of matching iTrees; in case of no match and empty list is returned
        """

        t = type(key_path)
        if t is str:
            # empty key?
            if len(key_path) == 0 or self.__len__() == 0:
                # empty string
                return []

            # is string matching to a tag?
            try:
                items = self.__getitem__(key_path, str_index_separator=str_index_separator)
                return self.__build_find_all_result(items,
                                                    item_filter=item_filter)
            except (KeyError, IndexError, ValueError):
                pass
            # we check some other quick exceptions:
            if key_path.strip(' ') == '*':
                return self.iter_children(item_filter=item_filter)
            if key_path.strip(' ') == '**':
                return self.iter_all(item_filter=item_filter)
            # now we split based on separator
            key_list = key_path.split(str_path_separator)
            if key_list[0] == '':
                # we must ensure we start from the root
                return self.root.find_all(key_list[1:], item_filter, str_path_separator, str_index_separator)
            if len(key_list) == 1:  # single key this means the item was not found!
                return []
            return self.find_all(key_list, item_filter, str_path_separator, str_index_separator)
        # first we check we have a valid tag:
        if (not _initial) or (t in (int, str, TagIdx, TagIdxStr, TagIdxBytes, TagMultiIdx, iTMatch, slice)):
            # if not _initial we are in deeper level of the iterator and we interpret here as an index list!
            items = self[key_path]
            return self.__build_find_all_result(items,
                                                item_filter=item_filter)
        # If we reach this point we expect an iterable object as key_path
        # that iterates deeper into the tree
        key = None  # will be overwritten anyway
        new_key_path = None
        sub_iter = iter(key_path)
        post_item = None
        post_post_item = None
        set_initial = False
        try:
            key = next(sub_iter)
        except StopIteration:
            # empty iterator!
            return []
        try:
            post_item = next(sub_iter)
            new_key_path = itertools.chain((post_item,), sub_iter)
            try:
                post_post_item = next(sub_iter)
                # create a new iterator that contains the post items and the original iterator
                new_key_path = itertools.chain((post_item, post_post_item), sub_iter)
                set_initial = True
            except StopIteration:
                # there is only one item left in iterator we will give the item directly
                # as key to the next level find()
                new_key_path = post_item
        except StopIteration:
            pass
        if key == str_path_separator:
            if new_key_path is None:
                # this is not possible we catch this already but we keep the code to complete the condition
                if item_filter(self.root):
                    return iter([self.root])
                else:
                    return []
            if not _initial:
                # cyclic construct we have to break!
                return []
            return self.root.find_all2(new_key_path,
                                       item_filter,
                                       str_path_separator,
                                       str_index_separator,
                                       _initial=set_initial
                                       )
        elif key == '*':
            result = itertools.chain((self,), self.iter_children(item_filter=item_filter))
        elif key == '**':
            result = itertools.chain((self,), self.iter_all(item_filter=item_filter))
        else:
            result = self.find_all2(key, item_filter,
                                    str_path_separator,
                                    str_index_separator,
                                    _initial=False)
        # result can only be a single item
        if new_key_path is None or result == []:
            # we will not go deeper
            return result
        # iter into the next level
        # We keep this for debugging proposes!
        # results = [item.find_all(new_key_path,
        #                         item_filter,
        #                         str_path_separator,
        #                         str_index_separator,
        #                         _initial=set_initial) for item in result]
        if True:
            results = itertools.islice(
                itertools.accumulate(
                    itertools.chain((None,), result), lambda c, item: item.find_all(new_key_path,
                                                                                    item_filter,
                                                                                    str_path_separator,
                                                                                    str_index_separator,
                                                                                    _initial=set_initial)), 1, None,
                1),  # python <3.8 no initial parameter
        return itertools.chain.from_iterable(*results)

    def find(self, key_path, item_filter=None, default_return=None, str_path_separator='/',
             str_index_separator='#'):
        """
        The find function targets over multiple levels of the iTree, it returns single items only! This means in
        case the key_path targets to multiple items the default_return will be given. If the key_path targets to a
        family with only one item inside  or the item_filter extracts only one item in a family
        the item will be given back as result. For multiple result utilize the `find_all()` method (which is slower).

        .. note:: The method will deliver a default_return when ever in the whole key_path a match is not unique.
                 This means iteration is stopped here and even that a deeper iteration with the defined filtering might
                 deliver at least a unique result. To ensure to find this deeper results you must utilize the slower
                 `find_all()` method.

        The key_path parameter given is normally a list. This can be a list of keys or TagIdx objects. The function
        will search for the first item in the first level, fo next item in the next level and so on...

        Absolut and relative key_paths:

        If the first item is the separator (default: '/') the find search is like an absolute path and we start at the
        root of the iTree. For compatibility reasons with find_all we accept  a leading "./"
        (or to be exact: ".%s"#str_path_separator) as absolute path indicator.
        If the first item is different, the key_path is relative and we start from the actual
        item and search the children and sub-children.

        Single string key_path:
        If the user searches for string type tags he can use a string with a separator (default: '/') in between the
        tags (Those key_paths will be implicit translated in a list). An index separator (default = '#') in between
        the tag and the index can also be used in this case. If the argument is already a list the single keys will not
        be parsed regarding the str_path_separator.

        .. note:: If iTree contains tags with characters that used for separators or the all match '*' character
              the find() result might contain that tagged item instead of the expected separated or wildcard match.

        .. note:: Quickest find operations can be performed by giving a list containing index integers or TagIdx objects

        The parameters in detail:

        :param key_path: single key or list of keys
                    identification path for the item/items to be searched.
                    Possible keys:
                    integer - behaves like normal __getitem__() -> itree_item[key]
                    TagIdx- behaves like normal __getitem__() -> itree_item[key]
                    iTreeTagSlice - select a tag sliced group of sub-elements
                    iTMatch - search pattern can be used too, but keep in mind it must deliver a unique result!
                    Slice - a slice of indexes (like a special index list)
                    string - will be parsed by the separators, special string '*" is as interpreted as any match
                    iterable list/tuple/deque,... -
                             run over single items

        :param item_filter: filters the item content regarding NORMAL, TEMPORARY and LINKED flag or a given
                            filtering method

        :param default_return: object will be return in case of no match (default = None)

        :param str_path_separator: separator character in case of strings for the search levels (default: "/")

        :param str_index_separator: separator character for given tag indexes (default: "#")

        :return: iTree single item
        """
        # internally we use the find_all() to get a list of items
        # and than return single match or default_return depending on result items

        result = self.find_all(key_path, item_filter=item_filter,
                               str_path_separator=str_path_separator,
                               str_index_separator=str_index_separator)
        # here we check if the iterator contains a unique item:
        item_iter = iter(result)
        try:
            item = next(item_iter)
            try:
                next(item_iter)
                # no StopIteration Exception! more then one element we return no match
                return default_return
            except (TypeError, StopIteration):
                # match!
                return item
        except StopIteration:
            # empty iterator!
            return default_return

    def index(self, item, item_filter=None):
        """
        The index method allows to search for the index of the item in a parent object
        This is especially useful if you must use a item_filter. The delivered index is delivered relative
        to the given item filter!

        For the item index of the item in the unfiltered tree (ALL) it's recommended
        to use the idx property instead: `(parent.index(item,ALL) == item.idx)`

        :param item: item index should be delivered for

        :param item_filter: filter integer; method can not handle filter methods yet!

        :return: index integer of the item relative to the given filter
        """
        if type(item) in {int, TagIdx}:
            item = self.__getitem__(item)
        if item.parent is not self:
            raise LookupError('Given item is not children of this iTree!')
        if item_filter is None:
            return super().index(item)
        else:
            for i, sibling in self.iter_children(item_filter=item_filter):
                if sibling == item:
                    return i

    # serialize + file operations

    def load_links(self, force=False, delete_invalid_items=False):
        """
        Runs ove all children and sub children in case a ITreeLink object is found the linked items are load in

        :param force: True - linked items will be reloaded even that they are already loaded

        :param delete_invalid_items: In case a iTreeLink refers to an invalid item (internal exception) the related
                                     iTreeLink object will be deleted from teh tree
        """
        for i in self.iter_all(item_filter=iTFilterItemType(iTreeLink)):
            i.load_links(force=force, delete_invalid_items=delete_invalid_items)
        # the following better code is is not working, don't know why?:
        # (i.load_links() for i in self.iter_all(item_filter=self.create_item_type_filter(iTreeLink)))

    def loads(self, data_str, check_hash=True, load_links=True):
        """
        create an iTree object by loading from a string

        If not overloaded or reinitialized the iTree Standard Serializer will be used. In this case we expect a
        matching JSON representation.

        :param data_str: source string that contains the iTree information

        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash

        :param load_links: True - linked iTree objects will be loaded

        :return: iTree object loaded from file
        """
        if (not hasattr(self, '_def_serializer')) or (self._def_serializer is None):
            self.init_serializer()
        return self._def_serializer[1].loads(data_str, check_hash=check_hash, load_links=load_links)

    def load(self, file_path, check_hash=True, load_links=True):
        """
        create an iTree object by loading from a file

        If not overloaded or reinitialized the iTree Standard Serializer will be used. In this case we expect a
        matching JSON representation.

        :param file_path: file path to the file that contains the iTree information

        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash

        :param load_links: True - linked iTree objects will be loaded

        :return: iTree object loaded from file
        """
        if (not hasattr(self, '_def_serializer')) or (self._def_serializer is None):
            self.init_serializer()
        return self._def_serializer[1].load(file_path, check_hash=check_hash, load_links=load_links)

    def dumps(self, calc_hash=True):
        """
        serializes the iTree object to JSON (default serializer)

        :param calc_hash: Tell if the hash should be calculated and stored in the header of string

        :return: serialized string (JSON in case of default serializer)
        """
        if (not hasattr(self, '_def_serializer')) or (self._def_serializer is None):
            self.init_serializer()
        return self._def_serializer[0].dumps(self, calc_hash=calc_hash)

    def dump(self, target_path, pack=True, calc_hash=True, overwrite=False):
        """
        serializes the iTree object to JSON (default serializer) and store it in a file

        :param target_path: target path of the file where the iTree should be stored in
        :param pack: True - data will be packed via gzip before storage
        :param calc_hash: True - create the hash information of iTree and store it in the header
        :param overwrite: True - overwrite an existing file
        :return: True if file is stored successful
        """
        if (not hasattr(self, '_def_serializer')) or (self._def_serializer is None):
            self.init_serializer()
        return self._def_serializer[0].dump(self, target_path, pack=pack, calc_hash=calc_hash, overwrite=overwrite)

    def renders(self, item_filter=None):
        """
        render the iTree into a string

        :param item_filter: the items can be filtered by giving a filter constants or giving a filter method or
                            iTFilter object

        :return: Tree representation as string
        """
        if (not hasattr(self, '_def_serializer')) or (self._def_serializer is None):
            self.init_serializer()
        return self._def_serializer[3].renders(self, item_filter)

    def render(self, item_filter=None):
        """
          print the rendered the iTree string to the terminal

          :param item_filter: the items can be filtered by giving a filter constants or giving a filter method or
                              iTFilter object
          """

        if (not hasattr(self, '_def_serializer')) or (self._def_serializer is None):
            self.init_serializer()
        return self._def_serializer[3].render(self, item_filter)

    # helpers
    def _load_subtree(self, extend_items):
        """
        We extend the iTree with given items (multi append)

        :note: In case the extend items have already a parent an implicit copy will be made. We do this because
               we might get an iTree-object as extend_items parameter and then the children will have automatically a
               parent even that the parent object might be a temporary one.

        :param extend_items: iterable object that contains iTree objects as items
        :return: True
        """
        # collect for operation
        sl = super()
        m = self._map
        idx = sl.__len__() - 1
        for item in extend_items:
            if item is None:
                continue
            if item._parent is not None:  # and (parent != self):
                item = item.__copy__()
            item._parent = self
            tag = item._tag
            idx += 1
            sl.append(item)
            try:
                if m.__contains__(tag):
                    family = m.__getitem__(tag)
                    item._cache = (idx, family.__len__())
                    family.append(item)
                else:
                    item._cache = (idx, 0)
                    m.__setitem__(tag, blist((item,)))
            except AttributeError:
                item._cache = (idx, 0)
                self._map = m = {tag: blist((item,))}
        return True

    def __get_family_insertion_idx(self, family, item_idx, last_index=0):
        fl = len(family)
        if fl == 1:
            if family[0].idx < item_idx:
                return 1 + last_index
            else:
                return last_index
        i = round(fl / 2)
        idx = family[i].idx
        if idx < item_idx:
            return self.__get_family_insertion_idx(family[i:], item_idx, last_index + i)
        else:
            return self.__get_family_insertion_idx(family[:i], item_idx, last_index)

    def __unsupport_op(self, *args, **kwargs):
        raise TypeError('unsupported operand or function in iTree')

    @property
    def __read_only_struct_exception_property(self):
        raise PermissionError('The iTree element is read_only (linked or read_only flag)!')

    # find helper methods for different types of keys

    def __extract_first_iter_items(self, iterator):
        """
        analysis the iterator
        :param iterator: iterator to be analysed
        :return: tuple  -> (None,None,None) -> empty iterator
                        -> (first_item,None,None) -> last element of iterator (no elements left afterwards)
                        -> (first_item,second_item,None) -> last two elements of iterator (no elements left afterwards)
                        -> (first_item,None,rest_iteratorNone) -> first item and the rest of the iterator
                           (without first item)
        """
        # iterator/generator
        if hasattr(iterator, '__len__'):
            l1 = len(iterator)
            if l1 == 0:
                return None, None
            elif l1 == 1:
                return iterator[0], None
            else:
                return iterator[0], iterator[1:]
        else:
            try:
                i1 = next(iterator)
            except StopIteration:
                return None, None
            try:
                i2 = next(iterator)
                return i1, itertools.chain((i2,), iterator)
            except StopIteration:
                return i1, None

    def __build_find_all_result(self, result, item_filter=None):
        """
        helper function for find method
        :param result: result found by the key
        :param item_filter: filter
        :return: final result
        """
        if isinstance(result, iTree):
            if item_filter is None:
                return iter((result,))
            elif item_filter(result):
                return iter((result,))
            else:
                return []
        if not result:  # != []
            return result
        if item_filter is None:
            return result
        return filter(lambda item: item_filter(item), result)

    def __find_single_item(self, key_path, item_filter=None):
        """
        find normal item via __getitem__ in the children
        :param key_path: key
        :param item_filter: filter method
        :return: list with one item
        """
        try:
            item = self.__getitem__(key_path)
        except (KeyError, IndexError):
            return []
        return self.__build_find_all_result(item, item_filter)

    def __find_tag_slice(self, tag_slice, item_filter=None):
        idx = tag_slice.idx  # slice!?
        if idx is int:
            return self.__find_single_item(key_path=tag_slice, item_filter=item_filter)
        tag = tag_slice.tag
        try:
            family = self._map[tag]
        except KeyError:
            return []
        return itertools.islice(self.__build_find_all_result(family, item_filter=item_filter), idx.start, idx.stop,
                                idx.step)

    def __find_slice(self, slice_obj, item_filter=None):
        return itertools.islice(self.iter_children(item_filter=item_filter), slice_obj.start, slice_obj.stop,
                                slice_obj.step)

    def __find_set(self, set_obj, item_filter=None):
        return filter(lambda item: item.idx in set_obj, self.iter_children(item_filter=item_filter))

    def __find_match(self, match, item_filter=None):
        return filter(lambda item: match.check(item)[0], self.iter_children(item_filter=item_filter))


class iTreeReadOnly(iTree):
    """
    This iTree object is read only the initial parameters given cannot be changed the object remains
    static in the tree and can only be changed when deleted and replaced
    """
    _is_read_only = True
    _is_temporary = False
    _is_placeholder = False
    _is_linked = False

    __slots__ = (
        '_tag', '_parent', '_map', '_coupled', '_data', '_cache', '_def_serializer')

    def __init__(self, tag, data=None, subtree=None, freeze_struct_only=False):
        if freeze_struct_only:
            if data is None:
                data = iTDataReadOnly()
            else:
                data = iTDataReadOnly(data)
        if subtree is None:
            super(iTreeReadOnly, self).__init__(tag, data)
        else:
            super(iTreeReadOnly, self).__init__(tag, data, [iTreeReadOnly(item.tag,item.data,subtree=item) for item in subtree])

    # block all setting commands
    def __setitem__(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def __delitem__(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def __iadd__(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def insert(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def append(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def appendleft(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def extend(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def extendleft(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def rotate(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def reverse(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def pop(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def popleft(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def remove(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def clear(self):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('The iTreeReadOnly element is read_only (linked or read_only flag)!')

    def __repr__(self):
        """
        create representation string from which the object can be reconstructed via eval (might not work in case of
        data that do not have a working repr method)
        :return: representation string
        """
        repr_str = 'iTreeReadOnly("%s"' % (repr(self._tag))
        if not self._data.is_empty:
            if self._data.is_no_key_only:
                repr_str = repr_str + ', data=%s' % repr(self._data[__NOKEY__])
            else:
                repr_str = repr_str + ', data=%s' % repr(self._data)
            subtree = super(iTree, self).__repr__()
            if subtree[0] == 'b':
                # we shorten blist from definition
                subtree = subtree[6:-1]
            return repr_str + ', subtree=%s)' % subtree
        else:
            return repr_str + ')'


class iTreeTemporary(iTree):
    """
    This is a temporary item that will not be considered if the iTree is saved into a file.
    """
    _is_read_only = False
    _is_temporary = True
    _is_placeholder = False
    _is_linked = False

    def __repr__(self):
        """
        create representation string from which the object can be reconstructed via eval (might not work in case of
        data that do not have a working repr method)
        :return: representation string
        """
        repr_str = 'iTreeTemporary("%s"' % (repr(self._tag))
        if not self._data.is_empty:
            if self._data.is_no_key_only:
                repr_str = repr_str + ', data=%s' % repr(self._data[__NOKEY__])
            else:
                repr_str = repr_str + ', data=%s' % repr(self._data)
            subtree = super(iTree, self).__repr__()
            if subtree[0] == 'b':
                # we shorten blist from definition
                subtree = subtree[6:-1]
            return repr_str + ', subtree=%s)' % subtree
        else:
            return repr_str + ')'


class iTreeLink(iTree):
    """
    This class is used to define linked subtrees in a iTree object.
    The target source can be a subtree in another iTree related file (external links) or
    internal links to a subtree of the already loaded subtree.

    Linking has some functional limitations so is it not allowed to link to already linked objects
    (we must protect iTree from circular definitions).

    The iTreeLink objects supports local items which can be added additional to the linked items.
    Furthermore there is also a mechanism so that local items can overlay the linked items in the tree. This is done
    by localizing the linked items with the `make_child_local()` or `make_self_local()` method. Afterwards the item can
    be manipulated as a normal iTree object. Only exception is that after deleting such a overlaying item the linked
    item will come back into the iTree.

    """

    _is_read_only = False
    _is_temporary = False
    _is_placeholder = False
    _is_linked = True

    __slots__ = (
        '_tag', '_parent', '_map', '_data', '_cache', '_def_serializer', '_link')

    def __init__(self, tag, data=None, subtree=None, link_file_path=None, link_key_path=None, load_links=True):
        t = type(tag)
        if t is int or t is TagIdx:
            raise TypeError('Given tag cannot be used in iTree wrong type (int or TagIdx)')
        else:
            self._tag = tag

        super(iTreeLink, self).__init__(tag, data, subtree=subtree)

        if link_file_path is not None or link_key_path is not None:
            self._link = iTLink(link_file_path, link_key_path)
            if load_links:
                self.load_links()
        else:
            self._link = None

    def __setitem__(self, key, item):
        """

        :except: PermissionError will be raised if the parent is not the root linked element
                 PermissionError will be raised if target is a linked element
                 TypeError if given item is temporary (not supported)

        :param key: single identifier for the item can be integer index or TagIdx

        :param item: item to be placed in iTree

        """
        if self._parent is not None:
            if self._parent._is_linked:
                raise PermissionError('The parent is read_only (linked)!')
        if item._is_temporary:
            raise TypeError('Given item is temporary and we cannot add temporary items as locals in a linked tree')
        try:
            old_item = super().__getitem__(key)
        except (KeyError, IndexError):
            return super().__setitem__(key, item)
        if old_item._is_linked:
            raise PermissionError('The target element is read_only (linked)!')
        else:
            return super().__setitem__(key, item)

    def __delitem__(self, key):
        """
        delete a child item in the tree (only on local items)

        :except: Method will raise a PermissionError if delete is done on a linked item

        :param key: single identifier for the item can be integer index or TagIdx for item to be deleted

        :return: deleted item will be returned
        """
        if self._parent is not None:
            if self._parent._is_linked:
                raise PermissionError('The parent is read_only (linked)!')
        item = self.__getitem__(key)
        if isinstance(item, iTree):
            if item._is_linked:
                raise PermissionError('The target element is read_only (linked)!')
            else:
                # maybe the deleted local item must be replaced by a linked item:
                if item._link is not None:
                    if item._link._link_item is not None:
                        super().__setitem__(item.tag_idx, item._link._link_item)
                        return item
            # else no overloaded item we just delete
            return super().__delitem__(item.idx)
        else:
            if key in self._map:
                del_items = []
                for item in self._map[key]:
                    del_items.append(item)
                    self.__delitem__(item.idx)
                return del_items
            else:
                raise KeyError('Given key not found in iTree object, delete not possible')

    def __iadd__(self, other):
        if self._parent is not None:
            if self._parent._is_linked:
                raise PermissionError('The parent is read_only (linked)!')
        if other._is_temporary:
            raise TypeError('Given item is temporary and we cannot add temporary items as locals in a linked tree')
        if other._is_linked:
            raise PermissionError('__iadd__ operation is not possible with a linked element!')
        return super().__iadd__(other)

    def rotate(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('Rotation operation is not possible on a linked element!')

    def reverse(self, *args, **kwargs):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('Reverse operation is not possible on a linked element!')

    def append(self, item):
        """
        append of items is allowed (items are appended as locals
        :param item: item to be appended
        :return:
        """
        if self._parent is not None:
            if self._parent._is_linked:
                raise PermissionError('The parent is read_only (linked)!')
        if item._is_temporary:
            raise TypeError('Given item is temporary and we cannot add temporary items as locals in a linked tree')
        if item._link is not None:
            if item._link._file_path is None and item._link._key_path is None:
                raise TypeError('Linked items cannot be appended to linked item as local item')
        return super().append(item)

    def extend(self, items):
        """
        extend of items is allowed, items are appended as locals
        :param items: items to be appended (iterator)
        :return: None
        """

        for item in items:
            if item._parent is not None:
                self.append(item.copy())
            else:
                self.append(item)

    def extendleft(self, item):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('extendleft operation is not possible on a linked element!')

    def appendleft(self, item):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('appendleft operation is not possible on a linked element!')

    def insert(self, insert_key, item):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('insert operation is not possible on a linked element!')

    def pop(self, key):
        """
        pop the object out of the tree (only possible on local objects)

        :except: In case a linked item is selected an PermissionError is raised

        :param key: identification key for the child that should be popped out

        :return: popped out item (parent set to None)
        """
        if self._parent is not None:
            if self._parent._is_linked:
                raise PermissionError('The parent is read_only (linked)!')
        item = super().__getitem__(key)
        if item._is_linked:
            raise PermissionError('The target element is read_only (linked)!')
        else:
            # maybe the deleted local item must be replaced by a linked item:
            if item._link is not None:
                if item._link._link_item is not None:
                    super().__setitem__(item.tag_idx, item._link._link_item)
                    item._parent = None
                    return item
            # else no overloaded item we just delete
            return super().pop(key)

    def popleft(self):
        """
        pop the first child out of the tree (only possible on local object)

        :except: In case a linked item is selected an PermissionError is raised

        :return: popped first item (parent set to None)
        """

        return self.__delitem__(0)

    def remove(self, item):
        """
        remove the given child item out of the tree (only possible on local object)

        :except: In case a linked item is selected an PermissionError is raised

        :param item: item to be removed from the iTree

        :return: removed item (parent set to None)
        """

        return self.__delitem__(item.idx)

    def rename(self, item_tag):
        """
        :except: PermissionError not possible on iTreeReadOnly objects
        """
        raise PermissionError('rename operation is not possible on a linked element!')

    @property
    def is_link_root(self):
        """
        Is this item the highest level linked element?

        :return: True/False
        """
        return self.link_root == self

    @property
    def link_root(self):
        """
        delivers the highest level element that is  linked
        in case item is not linked it delivers it self

        :return: highest level linked item found in the parents
        """
        if self._is_linked:
            parent = self._parent
            if (parent is not None) and parent._is_linked:
                return self._parent.link_root
            else:
                return self
        return None

    @property
    def is_link_loaded(self):
        """
        For linked iTree objects we deliver here the state of loading the links

        :return: True/False
        """
        return self._link.is_loaded

    def _convert_to_linked_item(self, item):
        """
        helper function that creates a linked clone of a normal item
        helper method is need in the load_links method

        :param item: item to be "cloned"

        :return: converted item
        """
        if item._is_linked:
            return item
        data = item._data
        if type(data) is not iTDataReadOnly:
            data = iTDataReadOnly(data)
        return iTreeLink(item._tag, data, subtree=[self._convert_to_linked_item(i) for i in item.iter_children()])

    def _convert_to_local_item(self, item):
        """
        helper method to clone a none linked item from a linked item
        this helper function is needed for localizing items

        :param item: linked item to be cloned as none linked item

        :return: result of the conversion
        """
        if not item._is_linked:
            return item
        try:
            data = iTData(item._data)
        except:
            data = None
        sub_items = [self._convert_to_local_item(i) for i in item.iter_children()]
        new_item = iTree(item._tag, data, subtree=sub_items)
        new_item._link = iTLink(link_item=item)
        return new_item

    def make_self_local(self):
        """
        make the current linked object a local object
        This is only possible if the parent parent is a normal iTree object ->
        only the first level children in a linked iTree can be made local
        The operation raises an SyntaxError in case it is used on a deeper level of the linked tree

        :return: None
        """
        if self._parent is None or not self._is_linked:
            raise SyntaxError('Item is not linked or has no parent, invalid operation!')
        return self._parent.make_child_local(self)

    def make_child_local(self, key):
        """
        make the item related to the given key a local object
        This is only possible if the parent of self is a normal iTree object ->
        only the first level children in a linked iTree can be made local
        The operation raises an SyntaxError in case it is used on a deeper level of the linked tree

        :param key: identification key for the child item that should be converted in a local item
        :return: None
        """
        if isinstance(key, iTree):
            item = key
        else:
            item = self.__getitem__(key)
        if not item._is_linked:
            raise TypeError('The addressed item is already local!')
        parent = self._parent
        if parent is None:
            raise SyntaxError('The item has no valid parent we cannot change to local!')
        if parent._is_linked:
            raise TypeError('The item parent is linked we cannot make this item local!')
        local_item = self._convert_to_local_item(item)
        # keep the link to the overloaded element
        local_item._link = iTLink(link_item=item)
        super().__setitem__(item.idx, local_item)
        return local_item

    def iter_locals(self, add_placeholders=False):
        """
        iterator that iterates only over the local elements

        :param add_placeholders: If this flag is set the (normally ignored) placeholder items are included
                                 in the iteration

        :return: iterator over local items
        """
        if add_placeholders:
            tags = {}
            for i in self.iter_children():
                tag = i._tag
                if tag not in tags:
                    tags[tag] = self.get_last_local_idx(tag)
                if tags[tag] is None:
                    continue
                if not i._is_linked and not i._is_placeholder and not i._is_temporary:
                    yield i
                else:
                    idx = tags.get(tag)
                    if idx is not None:
                        if idx >= i.idx:
                            yield iTreePlaceHolder(tag)
                        else:
                            tags[tag] = None
        else:
            for i in self.iter_children():
                if not i._is_linked:
                    yield i

    def get_last_local_idx(self, tag):
        """
        helper function which searches for local items in the tag family and
        delivers the last index of a local item found in the family. If no local item is found it delivers None.

        iTreePlaceHolder items ignored in this operation!

        :param tag: tag to identify the family to be searched in

        :return: last local item idx in tag family or None (no local item found)
        """
        for item in reversed(self._map[tag]):
            if not item._is_linked and not item._is_placeholder and not item._is_temporary:
                return item.tag_idx[1]
        return None

    def load_links(self, force=False, delete_invalid_items=False, _items=None):
        """
        load all linked items

        :param force: False (default) - load only if not already loaded
                      True - load even if already loaded (update)

        :param delete_invalid_items: False (default) - in case of invalid items we will raise an exception!
                                     True - invalid items will be removed from parent no exception raised

        :param _items: internal list parameter used for recursive calls of the function

        :return:

                 * True - success
                 * False - load failed
        """
        if _items is None:
            _items = []
        load_ok = True
        load_item = None
        if self._link is not None:
            if force or not self.is_link_loaded:
                if self._link.file_path is not None:
                    if not os.path.exists(self._link.file_path):
                        if delete_invalid_items:
                            if self._parent is not None:
                                self._parent.remove(self)
                            return False
                        else:
                            raise FileNotFoundError('Source file of the link not found!')
                    full_tree = self.load(self._link.file_path, load_links=True)
                    if self._link.key_path is None:
                        load_item = full_tree
                else:
                    full_tree = self._parent
                if self._link is not None and self._link.key_path is not None:
                    load_item = full_tree.find(self._link.key_path)
                    if load_item is None:
                        if delete_invalid_items:
                            if self._parent is not None:
                                self._parent.remove(self)
                            return False
                        else:
                            raise KeyError('Given key_path not found;'
                                           'loading of linked items is stopped at item %s!' % self.tag_idx_path)
                    t = type(load_item)
                    if t is not iTree and t is not iTreeReadOnly:
                        if delete_invalid_items:
                            if self._parent is not None:
                                self._parent.remove(self)
                            return False
                        else:

                            if load_item._is_linked:
                                raise TypeError('Given key_path is already linked (circular protection); '
                                                'loading of linked items is stopped at item %s!' % self.tag_idx_path)
                            else:
                                raise LookupError('Given key_path is not matching or is not distinct; '
                                                  'loading of linked items is stopped at item %s!' % self.tag_idx_path)
                sl = super(iTree, self)
                # now we take over the tree
                local_items = {i.tag_idx: i for i in self.iter_children() if not i._is_linked}
                sl.clear()
                # here we run a special extend (we don't care about parents and is_linked flag)
                m = self._map = {}
                if load_item is not None:
                    for item in load_item:
                        if item._is_linked:
                            if not item.load_links(force=force, delete_invalid_items=delete_invalid_items):
                                load_ok = False
                                continue
                            new_item = item
                        else:
                            new_item = self._convert_to_linked_item(item)
                        tag_idx = item.tag_idx
                        if tag_idx in local_items:
                            # overloading with local!
                            new_item = local_items.pop(tag_idx)
                            new_item._parent = None
                            new_item._link = iTLink(link_item=item)
                            if new_item._is_placeholder:
                                new_item = self._convert_to_linked_item(item)
                        new_item._parent = self
                        idx = sl.__len__()
                        sl.append(new_item)
                        tag = new_item.tag
                        try:
                            if m.__contains__(tag):
                                family = m.__getitem__(tag)
                                new_item._cache = (idx, family.__len__())
                                family.append(new_item)
                            else:
                                new_item._cache = (idx, 0)
                                m.__setitem__(tag, blist((new_item,)))
                        except AttributeError:
                            new_item._cache = (idx, 0)
                            self._map = m = {tag: blist((new_item,))}
                    # append the locals that were not integrated
                    for item in local_items.values():
                        item._parent = None
                        sl.append(item)
                    self._link.set_loaded(load_item.tag, load_item.data)
        return load_ok

    def clear(self, local_only=False):
        """
        We clear the object

        :param local_only:

                        * True - clear only the local items
                        * False - clear whole object (The object is reset to the no links loaded state and locals
                                   are deleted)
        :return:
        """
        if local_only:
            for item in self.iter_locals(add_placeholders=True):
                self.__delitem__(item.idx)
        else:
            self._data = None
            self._coupled = None
            super().clear()
            self._map = {}
            self._link._loaded = False

    def equal(self, other, check_parent=False, check_coupled=False, check_link=False):
        """
        compares if the data content of another item matches with this item

        :param other: other iTree

        :param check_parent: check the parent object too? (Default False)

        :param check_coupled: check the couple object too? (Default False)

        :param check_link: check the internal link variable too? (Default False)


        :return: boolean match result (True match/False no match)
        """
        if self == other:
            return True
        if type(other) is not iTree:
            return False
        if check_parent:
            if other._parent != self._parent:
                return False
        if check_link:
            if self._link != other._link:
                return False
        my_data = (self._tag, super(iTree, self).__len__(), len(self._map), self._link)
        other_data = (other._tag, super(iTree, other).__len__(), len(other._map), other._link)
        if my_data != other_data:
            return False
        for si, oi in zip(other.iter_children(), self.iter_children()):
            if not si.equal(oi):
                return False
        if check_coupled:
            try:
                if self._coupled != other._coupled:
                    return False
            except AttributeError:
                if hasattr(self, '_coupled'):
                    return False
                if hasattr(other, '_coupled'):
                    return False
        return True

    def __repr__(self):
        """
        create representation string from which the object can be reconstructed via eval (might not work in case of
        data that do not have a working repr method)
        :return: representation string
        """
        repr_str = 'iTreeLink("%s"' % (repr(self._tag))
        if not self._data.is_empty:
            if self._data.is_no_key_only:
                repr_str = repr_str + ', data=%s' % repr(self._data.__getitem__())
            else:
                repr_str = repr_str + ', data=%s' % repr(self._data)
            if self._link is not None:
                if self._link.file_path is not None:
                    repr_str = repr_str + ', link_file_path=%s' % repr(self._link.file_path)
                if self._link.key_path is not None:
                    repr_str = repr_str + ', link_key_path=%s' % repr(self._link.key_path)
            locals = list(self.iter_locals(add_placeholders=True))
            if len(locals) > 0:
                repr_str = repr_str + ', subtree=%s' % repr(locals)
        return repr_str + ')'


class iTreePlaceHolder(iTreeReadOnly):
    """
    place holder item that helps to keep items name in the overloading mechanism
    """

    _is_read_only = False
    _is_temporary = False
    _is_placeholder = True
    _is_linked = False

    __slots__ = (
        '_tag', '_parent', '_map', '_coupled', '_data', '_cache', '_def_serializer', '_link')

    def __init__(self, tag):
        t = type(tag)
        if t is int or t is TagIdx:
            raise TypeError('Given tag cannot be used in iTree wrong type (int or TagIdx)')
        else:
            self._tag = tag
        super().__init__(tag)

    def __repr__(self):
        """
        create representation string from which the object can be reconstructed via eval (might not work in case of
        data that do not have a working repr method)
        :return: representation string
        """
        return 'iTreePlaceHolder("%s")' % (repr(self._tag))
