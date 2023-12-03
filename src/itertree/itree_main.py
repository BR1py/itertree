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

from __future__ import absolute_import
import copy
import pickle
import traceback
from itertools import chain, dropwhile, zip_longest, takewhile, repeat, tee, product
from contextlib import suppress
from collections import OrderedDict, deque
from itertools import dropwhile
# import fnmatch
# import functools
# import operator
import sys

try:
    from typing import Hashable, Iterable, Callable, Union, Optional
except ImportError:
    # <Python 3.5
    # Only required for doc strings!
    Hashable = None
    Iterable = None
    Callable = None
    Union = None
    Optional = None

from .itree_helpers import itree_list, TagIdx, NoTarget, iTFLAG, iTLink, _iTFLAG, NoTag, \
    NoValue, INF,BLIST_SWITCH,ITER
from .itree_serializer.itree_renderer import iTreeRender
from .itree_serializer.itree_json_serialize import iTStdJSONSerializer2
from .itree_indepth import _iTreeIndepthTree
from .itree_getitem import _iTreeGetitem
from .itree_private import _iTreePrivate

class iTree(_iTreePrivate):
    __slots__ = (  # Attributes
        '_tag', '_value', '_link', '_flags', '_coupled',
        # private helper classes
        '_itree_prt_idx', '_families', '_items',
        # serializing objects
        '__renderer', '__itree_serializer',
        # quick access methods
        '__len__', '__iter__', 'getitem_by_idx', '_is_list',
        # quick access methods
        '_setitem_list',
        '_getitem_fam', '_setitem_fam',"_get_fam",
        # helpers
        '_hc_tree', 'get'
    )

    # we define some static private variables:
    _filter_linked_roots = lambda i: i.is_link_root
    _filter_linked_roots_and_linked = lambda i: i.is_link_root or i.is_linked

    # flags
    _READ_ONLY_TREE = iTFLAG.READ_ONLY_TREE
    _READ_ONLY_VALUE = iTFLAG.READ_ONLY_VALUE
    _LOAD_LINKS = iTFLAG.LOAD_LINKS

    # internal flags
    _LINKED = _iTFLAG.LINKED
    _LINK_ROOT = _iTFLAG.LINK_ROOT
    _PLACEHOLDER = _iTFLAG.PLACEHOLDER
    _FLAG_MASK = _iTFLAG.FLAG_MASK
    _IS_TREE_PROTECTED = _READ_ONLY_TREE | _PLACEHOLDER | _LINKED | _LINK_ROOT
    _IS_VALUE_PROTECTED = _READ_ONLY_VALUE | _PLACEHOLDER | _LINKED
    _DEEP_FLAG_MASK = _LOAD_LINKS | _READ_ONLY_TREE

    _NoneSlice = slice(None)
    _ONE_ITEM_LIST = itree_list([0])  # used for quickest possible instance of blist

    def __init__(self,
                 tag=NoTag,  # family tag (any hashable object)
                 value=NoValue,  # data object to be stored in the item
                 subtree=None,  # subtree definition
                 link=None,  # link to another iTree
                 flags=0,  # property flags
                 ):
        """
        This is the main class related to itertree module. It represents the node in the nested tree structure.

        In case the object contains a subtree this object is the parent of the children in the subtree and its inner
        children (children, sub-children, etc.). The ´iTree´-object itself can also be a
        child of a parent ´iTree´-object. If this is not the case the ´iTree´-object is the root of the tree.

        *Limitation:* An ´iTree´-object can be integrated as a child in one ´iTree´ only (one parent only principle)!

        Each ´iTree´-object contains a "tag". The objects tag can be any hashable object.

        Different as dictionaries it is allowed to put multiple items with the same tag inside the ´iTree´.
        Those items with
        the same tag are placed and ordered (enumerated) in the related tag-family. The specific items can be targeted
        via a zag_idx tuple (family-tag,family-index) which is the items unique key.

        Linked ´iTree´-objects will behave a bit special. They have a read only structure (children) and they contain
        the children (tree) of the linked ´iTree´.
        The "local" attributes like tag, value, ... can be set independent of the linked item (local properties).

        To change the tree structure of such an object you can change the original link target. But an explicit reload
        ( ´load_links()´ ) is required to get the change active in the linked items.

        Beside the linked item the user can add local items and mix them with the linked ones. But the general
        structure is always determined by the linked in children.

        Beside the subtree the ´iTree´-object can also contain a value. The value can be any type of Python objects
        that is stored in the tree-node (comparable with the value of a dictionary). If it is required by the user to
        calculate the hash
        of the íTree´ via ´hash(item)´ some value objects might not be hashable and will raise an exception. But as long
        as the objects can be pickled a hash replacement will be found in the hash of ´iTree´. E.g. a dict placed
        as a value makes no troubles even if teh user likes to hash the tree.

        As a helper the ´iTree´-object can be coupled with other objects (which might be helpful if you have a displayed
        tree in a GUI that is connected with the ´íTree´. Be aware that this helper function has only temporary
        character.
        It is not stored when dumping (standard dump) or considered in comparisons, etc. The coupled object is
        ignored by all internal functionalities. Also in linked items the coupled object is not taken over from the link
        and can be set independent.

        The behavior of a íTree´ object can be influenced by specific properties or flags:

            * Read-only tree: An ´iTree´ object where the subtree is protected and cannot be changed
            * Read-only value: An ´iTree´ object where the value is protected and cannot be changed

        The ´iTree´ object contains a large number of properties which should help the user to reach the
        required information as comfortable as possible. Especially the tree related information might be interesting:

            * mytree.tag -> family-tag of the item
            * mytree.idx -> absolute index of the object
            * mytree.tag_idx -> key tuple (family-tag, family-index)
            * mytree.idx_path -> tuple of absolute indexes from the root to the item
            * mytree.tag_idx_path -> tuple of key-tuples from the root to the item
            * mytree.parent -> parent item of the item
            * mytree.root -> root item of the item (highest level parent)
            * mytree.pre_item -> pre item (the children in the parent that is before this item)
            * mytree.post_item -> post item (the children in the parent that is after this item)
            * mytree.level -> How deep the item is in the tree related to the root
            * mytree.max_depth -> How deep the sub-items (nested) of the ´iTree´ go in maximum (deep levels)

        In case the ´iTree´ object is not part of another ´iTree´ (is root) those attributes
        will deliver in most cases ´None´.

            * mytree.is_root -> True in case the item is a root ´iTree´)no parent)
            * mytree.is_tree_read_only -> True in case the subtree is protected and read-only
            * mytree.is_value_read_only -> True in case the item value is protected and read-only
            * mytree.is_linked -> True in case the item is a linked item (read_only)
            * mytree.is_link_root-> True in case the item is a root for a link to another ´iTree´
            * mytree.link_root-> Delivers the related link-root in case the item is linked

            * mytree.value-> Delivers the value object stored in the ´iTree´ item

        There are different ways to access the children and sub-children in the tree of a ´iTree´ object.

        The standard access for single items is via ´itree_obj[target]´ ( ´__getitem__(target)´) call.
        As targets the user has different options:

           * index - absolute target index integer (fastest operation)
           * key - key tuple (family_tag, family_index)
           * tag or tag sets- family_tag object targeting a whole family
           * target-list - absolute indexes or keys to be replaced (indexes and keys can be mixed)
           * index slice - slice of absolute indexes
           * key slice - tuple of (family_tag, family_index_slice)
           * filter-method - method to filtering specific children

        Beside the first level functions the `iTree`-object contains the helper class `.deep` which contains
        the in-depth functionalities targeting all the nested sub-children of the object.

        As the name itertree should suggest a wide range of iteration methods are available in the class.
        They can be combined with different kind of filters.

        .. _filter_method:

        .. note:: As optional `filter_method`-parameter the user can give:

                    * `None`- filter inactive
                    * `Callable` delivering `True`/`False` related to a characteristic of the
                      `ìTree`-object (iterated items)

                  Beside this the internal filtering is normally a hierarchical filtering (If the parent does not match
                  to the filter all children are excluded too, even that they match to the filter). Some methods contain
                  a switch
                  for non-hierarchical filtering too. But most often the non-hierarchical filtering can be realized via the
                  build-in `filter()` method and in this case the switch is not available.

        Here the power of the iterators is obvious because cascaded filter queries can be constructed and finally in
        only **one** full iteration over all the items is required to get the results back
        (sometimes the full iteration is not required).

        It's recommended to have a look into itertools package  for better usage of the delivered iteration-generators.

        The design of the ´iTree´´ object is made for best possible performance even that it is pure Python.
        Some part of
        the code might look less good readable or in the iteration-generators you find the if else outside the
        iteration functionality which is not realized via sub-functions we have here redundant codings.
        But its is made to avoid conditions or function calls inside the loops which would be bad for the performance.

        :type tag: Hashable
        :param tag: family tag of the iTree object (any hashable object)

        :type value: object
        :param value: value to be stored in the iTree object

        :type subtree: Optional[Iterable]
        :param subtree: Iterable or Iterator containing the subtree items or an argument list (internal functionality)

        :type link: Optional[iTLink]
        :param link: iTLink object targeting another iTree

        :type flags: int
        :param flags: flags taken from iTFLAG class:

                          * iTFLAG.READ_ONLY_TREE - mark the subtree of this iTree as read-only
                            the subtree will be protected from changes in this case

                          * iTFLAG.READ_ONLY_VALUE - mark the value of this iTree object as read-only

                          * iTFLAG.LOAD_LINKS - load the links during instance automatically

                      Multiple flags can be combined via `|`

        """
        # handle family tag:
        if not tag.__hash__:
            raise TypeError('Given tag is not hashable')
        self._tag = tag

        # set data value
        self._value = value

        # flags
        if flags:
            self._flags = flags = flags & self._FLAG_MASK
        else:
            self._flags = 0

        # _itree_prt_idx
        # 1. hasattr((o,'_itree_prt_idx') -> Used for class/object identification ->
        # 2. o._iter_parent is None -> iTree-object is not part of a parent iTree
        # 3. o._itree_prt_idx is list -> iTree-object is part of a iTree
        # list: [parent_itree_object, absolute_index_cache, family_index]
        #   a. o._itree_prt_idx[0] -> iTree parent-object
        #   b. o._itree_prt_idx[1] -> cached absolute index in iTree parent-object (might be outdated!)
        #   c. o._itree_prt_idx[3] -> cached family index in iTree parent-object (might be outdated!)
        self._itree_prt_idx = None
        self.get = getitem = _iTreeGetitem(self)

        # internals like self._families are created only in case elements added to the object

        # load the subtree
        if subtree:
            # we only mask out the flags that should be brought into the deeper levels!
            if flags:
                sl = list(self._iter_extend(self, subtree, flags & self._DEEP_FLAG_MASK, init=True))
            else:
                sl = list(self._iter_extend(self, subtree, init=True))
            self._items = sl = itree_list(sl)
        else:
            self._items = sl = []
        self.getitem_by_idx = getitem.getitem_by_idx = sl.__getitem__
        self.__len__, self.__iter__ = sl.__len__, sl.__iter__

        # links
        if link:
            t = type(link)
            if t is iTLink:
                # we create a new object -> to be sure that we have a virgin iTLink-object
                link = link.get_args()
            elif t is tuple and len(link) > 4:
                raise TypeError('Given link %s not supported!' % repr(link))
            self._link = iTLink(*link)
            self._flags = self._flags | self._LINK_ROOT
            # load links
            if flags & self._LOAD_LINKS:
                self.load_links()

    # *** parent related properties and methods ************************************************************************

    @property
    def parent(self):
        """
        Property delivers current items parent-object.

        :rtype: Union[iTree, None]
        :return: iTree parent-object or None (in case no parent exists)
        """
        # Implementation state: ready, tested, doc ok
        return self._itree_prt_idx[0] if self._itree_prt_idx else None

    @property
    def ancestors(self):
        """
        Property delivers current items parents list up to the oot.
        In case item has no parent an empty list will be delivered

        :rtype: list
        :return: list of all ancestors
        """
        ancestors = []
        p = self.parent
        while p != None:
            ancestors.append(p)
            p = p.parent
        # switch order to root->down
        ancestors.reverse()
        return ancestors

    @property
    def is_root(self):
        """
        Is this item a root-item (has no parent)?

        :rtype: bool
        :return:
                * *True* - is root
                * *False* - is not root
        """
        # Implementation state: ready, tested, doc ok
        return self._itree_prt_idx is None

    @property
    def root(self):
        """
        property delivers the root-item of the tree

        In case the item has no parent it will deliver itself

        :rtype: iTree
        :return: iTree root item
        """
        # Implementation state: ready, tested, doc ok
        p = self
        while p is not None:
            root, p = p, p.parent
        return root

    @property
    def tag(self):
        """
        This is the access to the object-tag. The tag gives the relation to the tag-family in `iTree`-objects.

        The tag is comparable with a key in dictionaries but in iTrees the tag is not unique! For unique iTree
        identification the `tag_idx` property must be used.

        Any hashable object can be used as a tag, but in case "exotic" objects are used and serialization is required
        the user may have to extend the functionality of the serializer.

        :rtype: Hashable

        :return: tag - hashable object giving the family relation

        """
        # Implementation state: ready, tested, doc ok
        return self._tag

    @property
    def idx(self):
        """
        Index of this object in the iTree (related to the absolute order)

        *Method is very important for internal functionalities*

        .. note::
            In general the item index is cached but in case of deleted items or reorder operations
            the cache might be outdated. In this case the index update based on a search might take longer.

        :rtype: Union[int, None]
        :return: unsigned integer representing the index (related to absolute order of iTree)
        """
        # Implementation state: ready, tested, doc ok
        parent_list = self._itree_prt_idx
        if parent_list:
            parent, abs_idx, _ = parent_list
            siblings = parent._items
            # create locals for multi use functions
            size = len(siblings)
            if abs_idx < size and siblings[abs_idx] is self:
                # cache matches
                return abs_idx
            # cache index must be updated
            # search in near area
            delta = 20
            limit = min(size, abs_idx + delta + 1)
            start = max(0, abs_idx - delta)
            for i in range(start, limit):
                if siblings[i] is self:
                    parent_list[1] = i
                    return i
            if abs_idx < size / 2:
                # start -> end
                i = 0
                for item in siblings:
                    item._itree_prt_idx.__setitem__(1, i) # update items idx cache
                    if item is self:
                        return i
                    i = i + 1
                raise IndexError('Internal error for this iTree we found no related index in the parent-object!')
            else:
                # end -> start
                for i in range((size - 1), -1, -1):
                    item = siblings[i]
                    item._itree_prt_idx.__setitem__(1, i) #update item idx cache
                    if item is self:
                        return i
                raise IndexError('Internal error for this iTree we found no related index in the parent-object!')

    @property
    def idx_path(self):
        """
        delivers a list of absolute indexes from the root to this item

        For items with no parent (root_item) an empty tuple will be delivered

        .. note::
                We deliver here a tuple because it might be helpful if the object is hashable
                (usage as a dict key)

        :rtype: tuple
        :return: tuple of index integers (here we do not deliver an iterator!)

        """
        # Implementation state: ready, tested, doc ok
        p = self
        idx_list = deque()
        while 1:
            root, p = p, p.parent
            if p is None:
                break
            else:
                idx_list.appendleft(root.idx)
        return tuple(idx_list)

    @property
    def tag_idx(self):
        """
        The tag_idx is a unique identification of the item. It is represented by a tuple containing the family-tag
        and the family related index of the item.

        If  the item is not part of a parent-tree (root-item) in this case the result will be `None`.

        :rtype: Union[tuple, None]
        :return: tuple (family-tag, family-index) or None (if item has no parent)
        """
        parent_list = self._itree_prt_idx
        if parent_list:
            parent = parent_list[0]
            getitem_fams = parent._getitem_fam
            tag = self._tag
            # we use cached index to be quicker
            family_idx = parent_list[2]
            family = getitem_fams(tag)
            fm_getitem = family.__getitem__
            size = family.__len__()
            if family_idx < size and fm_getitem(family_idx) is self:
                return tag, family_idx

            delta = 20

            limit = min(size, family_idx + delta + 1)
            start = max(0, family_idx - delta)
            for i in range(start, limit):
                if fm_getitem(i) is self:
                    parent_list[2] = i
                    return tag, i

            # update the whole list
            if family_idx < size / 2:
                # start -> end
                i = 0
                for item in family:
                    item._itree_prt_idx.__setitem__(2, i)
                    if item is self:
                        return i
                    i = i + 1
                raise IndexError('Internal error for this iTree we found no related index in the parent-object!')
            else:
                # end -> start
                for i in range((size - 1), -1, -1):
                    item = family[i]
                    item._itree_prt_idx.__setitem__(2, i)
                    if item is self:
                        return i
                raise IndexError('Internal error for this iTree we found no related index in the parent-object!')

    @property
    def tag_idx_path(self):
        """
        The path is a tuple of tag_idx tuples from root to this item.
        Each tag_idx is a tuple containing the pair family-tag and family-index.

        For items with no parent (rooot_item) an empty tuple will be delivered

        .. note::
                    We deliver here a tuple because it might be helpful if the object is hashable
                    (usage as a dict key)

        :rtype: tuple
        :return: tuple of key tuples containing family-tag and family-index

        """
        # Implementation state: ready, tested, doc ok

        p = self
        key_list = deque()
        while 1:
            root, p = p, p.parent
            if p is None:
                break
            else:
                key_list.appendleft(root.tag_idx)
        return tuple(key_list)

    def force_cache_update(self, idx=True, fam_keys=True, all_keys=True):
        """
        Forces the update of the index and keys in cache

        Normally this is not required the methode is mainly used for testing proposes

        :param idx: True - update absolute-indexes

        :param fam_keys: True - update this items family-indexes

        :param all_keys: True - update all families faimily-indexes

        """
        parent_list = self._itree_prt_idx
        if parent_list:
            parent = parent_list[0]
            if idx:
                list(item._itree_prt_idx.__setitem__(1, i) for i, item in enumerate(parent))
            if fam_keys and not all_keys:
                family = self._getitem_fam(self._tag)
                list(item._itree_prt_idx.__setitem__(2, i) for i, item in enumerate(family))
            elif all_keys:
                for family in parent._families.values():
                    list(item._itree_prt_idx.__setitem__(2, i) for i, item in enumerate(family))

    @property
    def pre_item(self):
        """
        Delivers the pre-item (predecessor) of this object in the parent-tree.
        If self is first item or there is no parent `None` will be delivered.

        :rtype: Union[iTree,None]
        :return: iTree predecessor or None (no match)
        """
        # Implementation state: ready, tested, doc ok
        if self._itree_prt_idx is None:
            return None
        idx = self.idx - 1
        return None if idx < 0 else self._itree_prt_idx[0]._items.__getitem__(idx)

    @property
    def post_item(self):
        """

        Delivers the post-item (successor) of this object in the parent-tree.
        If self is first item or there is no parent `None` will be delivered.

        :rtype: Union[iTree,None]
        :return: `iTree` successor or `None` (no match)
        """
        # Implementation state: ready, tested, doc ok
        if self._itree_prt_idx is None:
            return None
        idx = self.idx + 1
        sl = self._itree_prt_idx[0]._items
        return sl.__getitem__(idx) if idx < sl.__len__() else None

    @property
    def siblings(self):
        """
        Property delivers all siblings of the item. Iterates over all children of the parent and skips the item itself
            * In case of no siblings an empty list is delivered.
            * In case of an unique sibling a list with the unique sibling is delivered
            * In case of multiple siblings a generator (iterator) over all siblings is delivered
        :rtype Union(list,generator)
        :return: iterable over the siblings
        """
        if self._itree_prt_idx is None:
            return []
        parent=self._itree_prt_idx[0]
        return [i for i in parent if i is not self]

    @property
    def level(self):
        """
        Delivers the distance (number of levels) to the root-item of the tree. Or in other words how
        deep in tree the item is positioned.
        In case item has no parent (is a root-item) this method will deliver 0.

        :rtype: int
        :return: integer - number of levels (outer direction)
        """
        # Implementation state: ready, tested, doc ok
        i = 0
        pt = self._itree_prt_idx
        while (pt):
            p = pt[0]
            i = i + 1
            pt = p._itree_prt_idx
        return i

    @property
    def max_depth(self):
        """
        Relative from this item the method measures the maximum depth of the tree and delivers
        the maximum number of levels that are found in this object.

        If the user wants to now the maximum depth of the whole tree ensure that the property of the root-item is read.
        The user might use `my_tree.root.max_depth` to ensure this.

        :rtype: int

        :return: integer maximal number of levels that exists in the tree (inner direction)
        """
        # Implementation state: ready, tested, doc ok
        if not self:
            return 0
        max_depth = 0
        items = [self]
        while 1:
            new_items = []
            deque((new_items.extend(list(i)) for i in items), maxlen=0)
            if len(items) == 0:
                break
            else:
                max_depth += 1
            items = new_items
        return max_depth - 1

    @property
    def negative_levels(self):
        """
        The property delivers a list of all bottom->up levels of the item. Because any branch might have
        different depth
        each item can have multiple negative levels. If the item has np children an empty list will be delivered.

        ..note:: To check for a specific negative_level it's recommended to use the quicker `has_inverted_level()`
                 method.

        :rtype: list
        :return: list of negative levels
        """
        self_level = self.level
        return [(self_level-leave.level) for leave in self.deep.siblings(-1, ITER.INNER)]

    def equal_negative_level(self,target_level):
        """
        The method checks if this item matches to the given target_level (bottom->up level).
        The bottom up level is counted from the bottom of the tree upwards. The sub-tree of the item might
        have different depths in the different branches. Therefore each item might have multiple inverted_levels.

        :type target_level: int
        :param target_level: The given level can be a positive or negative number (method considers the
                             absolute level value)
        :return: True - The given target-level is a valid bottom->up distance for this item
                 False - This item has no matching bottom->up distance
        """
        target_level=abs(target_level)
        self_level=self.level
        for leave in self.deep.siblings(-1,ITER.INNER):
            if leave.level-self_level==target_level:
                return True
        return False

    def in_negative_level(self, target_level,equal=False,any=False):
        """
        The method checks if this item is greater or equal to the given target_level (bottom->up level).
        The bottom up level is counted from the bottom of the tree upwards. The sub-tree of the item might
        have different depths in the different branches. Therefor each item might have multiple inverted_levels.

        :type target_level: int
        :param target_level: The given level can be a positive or negative number
                             (A given zero makes no sense and function will deliver False)

        :type equal: bool
        :param equal: Flag if the in means upon the given negative level (False) or
                      upon or equal to given negative level (True) - default is False
        :param any: Check if the item is upon the given negative level for all containing children (True)
                    not just one (False - default)

        :return: True - The given target-level is a valid bottom->up distance for this item
                 False - This item has no matching bottom->up distance
        """
        target_level = abs(target_level)
        if self:
            if any:
                if equal:
                    self_level = self.level
                    for leave in self.deep.siblings(-1, ITER.INNER):
                        if leave.level - self_level < target_level:
                            return False
                    else:
                        return True
                else:
                    self_level = self.level
                    for leave in self.deep.siblings(-1, ITER.INNER):
                        if leave.level - self_level <= target_level:
                            return False
                    else:
                        return True
            else:
                if equal:
                    self_level = self.level
                    for leave in self.deep.siblings(-1, ITER.INNER):
                        if leave.level - self_level >= target_level:
                            return True
                else:
                    self_level = self.level
                    for leave in self.deep.siblings(-1, ITER.INNER):
                        if leave.level - self_level > target_level:
                            return True
        elif equal and target_level==1:
            return True
        return False

    @property
    def tag_number(self):
        """
        property contains the number of tags (families) the itree contains
        :return: integer
        """
        if self:
            return len(self._families)
        else:
            return 0

    # *** properties targeting internal sub/helper classes *************************************************************

    @property
    def deep(self):
        """
        Subclass containing the deep access to the nested structures of iTree
        :return:
        """
        try:
            return self._hc_tree
        except AttributeError:
            # The subclass is only instanced if it is first used
            tree, tree._itree, tree.get = _iTreeIndepthTree(), self, self.get
            self._hc_tree = tree
            return tree

    # flags

    @property
    def flags(self):
        """
        Give the flags value of the object. The integer value stored in this property contains the bit flags
        related to the constants iTFLAG or _iTFLAG.

        To see the details the user might use `bin()` or the helper property `flags_repr` which delivers a
        string containing all set flags.

        ;rtype: int
        :return: The flags set for this item
        """
        # Implementation state: ready, tested, doc ok
        return self._flags

    def flags_repr(self, public_only=True):
        """
        String representation of flags for this item

        :type public_only: bool
        :param public_only:
                        * True - Consider only the public flags (given by the user) -> default
                        * False - Show all flags (also linked and placeholder flags)

        ;rtype: str
        :return: String repr of the flags set for this item
        """
        # Implementation state: ready, partly tested, doc ok
        out = []
        if self._flags & self._READ_ONLY_TREE != 0:
            out.extend(('iTFLAG.READ_ONLY_TREE', '|'))
        if self._flags & self._READ_ONLY_VALUE != 0:
            out.extend(('iTFLAG.READ_ONLY_VALUE', '|'))

        if self._flags & self._LOAD_LINKS != 0:
            out.extend(('iTFLAG.LOAD_LINKS', '|'))
        if not public_only:
            if self._flags & self._LINKED != 0:
                out.extend(('_iTFLAG.LINKED', '|'))
            if self._flags & self._LINK_ROOT != 0:
                out.extend(('_iTFLAG.LINK_ROOT', '|'))
            if self._flags & self._PLACEHOLDER != 0:
                out.extend(('_iTFLAG.PLACEHOLDER', '|'))
        return ''.join(out).rstrip('|')

    @property
    def is_tree_read_only(self):
        """
        Is the tree protection flag set? In this case the tree structure cannot be changed

        This property targets the tree structure not the value!

        :rtype: bool
        :return:
                * False - subtree can be changed (writeable)
                * True -  subtree is protected (read-only)
        """
        # Implementation state: ready, tested, doc ok
        return bool(self._flags & (self._READ_ONLY_TREE | self._LINKED))

    def set_tree_read_only(self):
        """
        Set the tree protection flag. If the flag is set the subtree structure can not be changed anymore.

        .. Warning:: Setting the structural protection is always a deep operation. In all children and sub-children
                     the protection flag will be activated too! But when unset the behavior it is not automatically
                     made as a deep operation`. Here the differentiation in between the two methods
                     `unset_tree_read_only()` and `unset_tree_read_only_deep()` exists.
        """
        # Implementation state: ready, tested, doc ok
        if self._flags & self._LINKED:
            _iTreePrivate._raise_read_only_exception(self)
        set_flags = _iTreePrivate._set_flags
        read_only_tree_flag = self._READ_ONLY_TREE
        set_flags(self, read_only_tree_flag)
        for i in self.deep:
            set_flags(i, read_only_tree_flag)

    def unset_tree_read_only(self):
        """
        Unset the tree protection flag on the item. Only the children structure of this item is made
        writable by this operation.

        :except: If the parent contains the tree protection flag a PermissionError will be raised
        """
        # Implementation state: ready, tested, doc ok
        if self._itree_prt_idx is not None and self._itree_prt_idx[0]._flags & self._READ_ONLY_TREE:
            raise PermissionError('The structural protection flag can only be unset in '
                                  'case the parent is not protected. But here the parent holds the protection flag')

        self._unset_flags(self, self._READ_ONLY_TREE)

    @property
    def is_value_read_only(self):
        """
        Is iTree value read_only? Is the value protection flag iTFLAG.READ_ONLY_VALUE is set?

        :rtype: bool
        :return:
                True - read-only protection of value active
                False - value is writeable
        """
        # Implementation state: ready, tested, doc ok

        return bool(self._flags & (self._READ_ONLY_VALUE | self._LINKED))

    def set_value_read_only(self):
        """
        Set the write protection of the value (set flag: iTFLAG.READ_ONLY_VALUE)
        """
        # Implementation state: ready, tested, doc ok

        self._set_flags(self, self._READ_ONLY_VALUE)

    def unset_value_read_only(self):
        """
        Unset the write protection flag of the value (set flag: iTFLAG.READ_ONLY_VALUE).
        Value will be writeable afterwards
        """
        # Implementation state: ready, tested, doc ok

        if self._flags & self._LINKED:
            _iTreePrivate._raise_read_only_exception(self)
        self._unset_flags(self, self._READ_ONLY_VALUE)

    # *** value and coupled object related properties/methods **********************************************************

    @property
    def value(self):
        """
        Delivers the full value object stored in the `iTree`-object

        :rtype: object
        :return: value-object of the item
        """
        # Implementation state: ready, tested, doc ok
        return self._value

    def set_value(self, value):
        """
        Set/replace the value content of the `iTree`-object.

        The method returns the previous stored value object that was replaced by the operation.

        .. note:: If an `iTValueModel` is stored as value in the `iTree` by default the set_value() method will
                  target the value which is stored inside the model. If the model itself should be exchanged the
                  user must
                  give the new model as value parameter of this method. To replace the model with another Python
                  object the user must first delete the model via `del_value()` command and afterwards set the new value.

        :type value: object
        :param value: data-object that should be placed as value or in case we
                      have a `iTValueModel` already as value it is placed inside the model.

        :rtype: object
        :return: old value object that was stored in iTree before
        """
        # Implementation state: ready, tested, doc ok
        if self._flags & self._IS_VALUE_PROTECTED:
            raise PermissionError('%s value is read only'%self.__class__.__name__)
        old_value = self._value
        # do we have a model?
        if (
                hasattr(old_value, 'is_iTValueModel')
                and hasattr(value, 'is_iTValueModel')
                or not hasattr(old_value, 'is_iTValueModel')
        ):
            # new model given!
            self._value = value
        else:
            old_value = old_value.set(value)
        return old_value

    def set_key_value(self, key, value):
        """
        Depending on the already stored object this operation is a sub-replacement of a part only.

        The method returns the previous stored value object that was replaced by the operation.

        The user can influence the behavior by giving the `key` parameter. And it depends on the already
        stored value object (e.g. a `list` or `dict` ). Only the value of the related
        item will be replaced or in case the item did not exist yet the might object will be extended by the
        given value ( `dict` only).

        Depending on given key parameter and the already stored object we have the following possible behaviours:

            * dict stored in value -> store the value in the dict with the key given in key_index
            * dict stored in value and matching item-value is a `iTValueModel` -> replace value inside the model
            * list stored in value -> key_index must be an index and replace the related item in the list with the
              value given
            * list stored in value and matching (index) item-value is a `iTValueModel` -> replace value inside the model
            * key == `INF` and list stored in value -> append given value in the list

        .. note:: If an `iTValueModel` is stored as value in the `iTree` by default the `mytree.set_value()`-method will
                  target the value which is stored inside the model. If the model itself should be exchanged
                  the user must give a new model as value parameter of this method. To replace the model with another
                  Python object the user must first delete the model via `del mytree.value[key]` command and afterwards
                  set the new value or he sets  the value directly via `mytree.value[key]==new_value` .

        :type key: Optional[Hashable,int]
        :param key: key or index of the value object (depends on the object already stored in `iTree` ).
                    if `key==INF` the value will be appended in case a list-like object is already
                    stored in the `iTree`-object.

        :type value: object,
        :param value: value object that should be placed as value or in case a key is given the sub-value in
                      the `iTree`
                      or in case we have a `iTValueModel` is used inside the model.


        :rtype: object
        :return: old value object that was stored in iTree before
        """
        # Implementation state: ready, tested, doc ok
        if self._flags & self._IS_VALUE_PROTECTED:
            raise PermissionError('%s value is read only'%self.__class__.__name__)
        old_value = self._value
        try:
            old_value = old_value[key]
        except KeyError:
            old_value[key] = value
            return NoValue
        except TypeError:
            if key == INF:
                old_value.append(value)
                return NoValue
            raise
        # do we have a model?
        if (
                hasattr(old_value, 'is_iTValueModel')
                and hasattr(value, 'is_iTValueModel')
                or not hasattr(old_value, 'is_iTValueModel')
        ):
            # new model given!
            self._value[key] = value
        else:
            old_value = old_value.set(value)
        return old_value

    def get_value(self):
        """
        Delivers the value-object of the item or a sub-value in case key_index parameter is used and a
        matching object is stored in the `iTree` .

        .. note:: If `iTValueModel` is stored in `iTree` the method will not target the model it will
                  target the value inside. If the model itself is required the `value`-property of `iTree` must be used.

        :except: In case a key_index is given but the object is not a `dict` or a `list` like object an `AttributeError`
                 will be raised ( `__getitem__()`required). If no matching item is found an
                 `IndexError` or `KeyError` will be raised.

        :rtype: object
        :return: value object the `iTree` or `iTValueModel` (in case a model is stored in the `iTree` )
        """
        # Implementation state: ready, tested, doc ok
        value = self._value
        return value.value if hasattr(value, 'is_iTValueModel') else value

    def get_key_value(self, key):
        """
        Delivers the value-object of the item or a sub-value in case key_index parameter is used and a
        matching object is stored in the `iTree` .


        In case the stored value is a `dict`-like object the key will be used as the key of the dict.
        In case the stored value is a `list`-like object the keyx will be used as the index of the list.

        In case the target value is a `iTValueModel` the value inside will be targeted and not the model itself.

        .. note:: If `iTValueModel` is stored in `iTree` the method will not target the model it will
                  target the value inside. If the model itself is required the `value`-property of `iTree` must be used.

        :except: In case a key_index is given but the object is not a `dict` or `list` like object an `AttributeError`
                 will be raised ( `__getitem__()`-method required). If no matching item is found an
                 `IndexError` or `KeyError`
                 will be raised.

        :type key: Optional[Hashable,int]
        :param key: Optional key or index parameter

        :rtype: object
        :return: value object the `iTree` or `iTValueModel` (in case a model is stored in the `iTree`)
        """
        # Implementation state: ready, tested, doc ok
        value = self._value[key]
        return value.value if hasattr(value, 'is_iTValueModel') else value

    def del_value(self):
        """
        Deletes the full value-object stored in ´iTree´ ( ´NoValue´ is stored in iTree).

        This method will always delete the whole object stored in `iTree` even `iTValueModel`-objects are deleted. To
        delete the value content of a model `mytree.value.clear()` or 'set_value(NoValue)' might be used.

        :return: deleted value
        """
        # Implementation state: ready, tested, doc ok
        if self._flags & self._READ_ONLY_VALUE:
            raise PermissionError('%s value is read only'%self.__class__.__name__)
        old_value, self._value = self._value, NoValue
        return old_value

    def del_key_value(self, key):
        """
        If no parameter is given deletes the full value-object stored in ´iTree´ (store ´NoValue´ ).

        In case a key or index is given and the value contains a matching object we will only pop out the
        related sub-item.

        This method will always delete the whole targeted object even `iTValueModel`-objects are deleted. To
        delete the value content of a model `mytree.value.clear()` or 'set_value(NoValue)' might be used.

        :except: In case a key is given but the object is not `dict` or `list` like a TypeError or AttributeError
                 will be raised
                 ( `__delitem__()`-method is targeted);
                 If the given key does not exist or an invalid parameter is given a KeyError or IndexError
                 will be raised.

        :type key: Optional[Hashable,int]
        :param key: Optional key or index to exchange just sub-items in the value

        :return: deleted value
        """
        # Implementation state: ready, tested, doc ok
        if self._flags & self._READ_ONLY_VALUE:
            raise PermissionError('%s value is read only'%self.__class__.__name__)
        return self._value.pop(key)

    @property
    def coupled_object(self):
        """
        The `iTree`-object can be coupled with another Python-object. The pointer to the object is stored and can be
        reached via this property. (E.g. this can be helpful when connecting the `iTree` with a visual item
        (hypertree-list item) in a GUI)

        :return: pointer to coupled-object or None if no object is stored
        """
        # Implementation state: ready, tested, doc ok
        try:
            return self._coupled
        except AttributeError:
            return None

    # set properties
    def set_coupled_object(self, coupled_object):
        """
        Couple another Python-object with this `iTree`-object.

        Compared with the `value` the coupled-object is not tracked by any internal functions. We do not consider
        it in any relation (e.g. `__contains__()` and do not dump it in files, etc. Even in linked items the
        coupled-object is not protected. And in copies it is ignored and not taken over.

        .. note:: E.g. The coupled-object might be an object in a GUI that is related to this item.


        :param coupled_object: object pointer to the object that should be coupled with this iTree item
        """
        # Implementation state: ready, tested, doc ok
        self._coupled = coupled_object

    # *** structure related functions **********************************************************************************

    # setters:

    def append(self, item=NoValue):
        """
        Append the given `iTree`-object to the `iTree` (new last child)
        The `append()` method is the fastest way to add a single item to the end of the tree.

        :except: In case `iTree`-object has already a parent a `RecursionError` will be raised
                 Other exceptions might come up in case the `iTree` is protected (tree read-only mode).


        :type item: Union[iTree,object]
        :param item: `iTree`-object to be appended

                     .. warning::
                        In case the given item-object is not a `iTree`-object the item is interpreted
                        as a value and the `iTree` will be created implicit (with tag-family `NoTag`) in the way:

                        `iTree(tag=NoTag, value=item)` ~ ìTree(value=item)
                        If no item is given an empty iTree is created tag=`NoTag`; value=`NoValue`.

                            >>> root=iTree('root')
                            >>> root.append('myvalue')
                            iTree(value='myvalue')
                            >>> root.append() # append an empty iTree-object
                            iTree()

        :rtype: iTree
        :return: Delivers the appended item itself
                 (it might be useful for the user to get the updated information of the object).
        """
        if self._flags & self._IS_TREE_PROTECTED:
            if self.is_link_root:
                if hasattr(item, '_itree_prt_idx') and item.flags & (
                        self._LINKED | self._LINK_ROOT | self._PLACEHOLDER):
                    raise TypeError('Linked items cannot be appended to linked item as local item')
            else:
                self._raise_read_only_exception(self)
        try:
            if item._itree_prt_idx is not None:
                raise RecursionError('Given item has already a parent')
            tag = item._tag
        except AttributeError:
            # implicit definition of iTree:
            item = self.__class__(value=item)
            tag = NoTag
        # return self._append_item(self,item)
        # Just for performance we keep the code for append here and do not use the helper
        abs_idx = len(self)  # after tests here the len() is quicker (not understood why)
        if abs_idx:
            self._items.append(item)
            # append item to family
            family = self._get_fam(tag)
            if family is None:
                self._setitem_fam(tag, [item])
                item._itree_prt_idx = [self, abs_idx, 0]
            else:
                fm_idx = family.__len__()  # after tests here the .>__len__ is quicker (not understood why)
                family.append(item)
                if fm_idx==BLIST_SWITCH:
                    self._setitem_fam(tag,itree_list(family))
                item._itree_prt_idx = [self, abs_idx, fm_idx]
        else:
            # here we must init all family and item related attributes
            getitem = self.get
            # items
            self._items = sl = self._ONE_ITEM_LIST.copy()
            sl[0] = item
            self.getitem_by_idx = getitem.getitem_by_idx = sl.__getitem__
            self.__len__, self.__iter__, self._setitem_list = sl.__len__, sl.__iter__, sl.__setitem__
            # family
            self._families = families = {tag: sl.copy()}
            getitem._getitem_fam=self._getitem_fam=families.__getitem__
            self._get_fam, self._setitem_fam = families.get, families.__setitem__
            item._itree_prt_idx = [self, 0, 0]
        return item

    def __iadd__(self, other):
        """
        append the given item to the iTree (short form of `append()`)

        :except: In case `iTree`-object has already a parent a `RecursionError` will be raised
                 Other exceptions might come up in case the `iTree` is protected (tree read-only mode).

        :type other: Union[iTree,object]
        :param other: `iTree`-object to be appended.

                     .. warning::

                        As in `append()` in case the given item-object is not a `iTree`-object the item is interpreted
                        as a value and the `iTree` will be created implicit (with `NoTag` tag).

        :rtype: `ìTree`
        :return: self
        """
        # Implementation state: ready, tested, doc ok
        self.append(other)
        return self

    def appendleft(self, item=NoValue):
        """
        Append the given `iTree`-object to the left of the parent-tree (new first child)
        The `appendleft()` method is the recommended method to add a new first item to iTree
        (quicker than `insert(0,item)` ).
        Compared to `append()` the method is slower and the cache index information gets invalid after the operation
        (will be automatically updated later on if required).

        :except: In case `iTree`-object has already a parent a `RecursionError` will be raised.
                 Other exceptions might come up in case the `iTree` is protected (tree read-only mode).

        :type item: Union[iTree,object]
        :param item: `iTree`-object to be appended as first item.

                     .. warning::

                        As in `append()` in case the given item-object is not a `iTree`-object the item is interpreted
                        as a value and the `iTree` will be created implicit.

        :rtype: iTree
        :return: Delivers the appended item itself
                 (it might be useful for the user to get the updated information of the object).
        """
        # Implementation state: ready, tested, doc ok
        flags = self._flags
        if flags & self._IS_TREE_PROTECTED:
            if self.is_link_root:
                # if self is link_root and the tag of the given item is different then the linked
                # ones operation is allowed!
                if hasattr(item, '_itree_prt_idx'):
                    if item.flags & (self._LINKED | self._LINK_ROOT | self._PLACEHOLDER):
                        raise TypeError('Linked items cannot be appended to linked item as local item')
                    if self._link.is_loaded and item.tag in self._link.tags:
                        self._raise_read_only_exception(self)
                elif self._link.is_loaded and NoTag in self._link._tags:
                    self._raise_read_only_exception(self)
            else:
                self._raise_read_only_exception(self)
        try:
            if item._itree_prt_idx is not None:
                raise RecursionError('Given item has already a parent')
        except AttributeError:
            # implicit definition of iTree:
            item = self.__class__(value=item)
        if self:
            return self._append_item_left(self, item)
        else:
            return self._append_item(self, item)

    def insert(self, target, item=NoValue):
        """
        Insert an item **before** a given target-position. The insertion works like in lists.

        The insertion operation is slower as the append operations.

        If `target=None` is given the operation inserts in the last position (== `append()`).

        :except: In case `iTree`-object has already a parent a `RecursionError` will be raised
                 Other exceptions might come up in case the `iTree` is protected (tree read-only mode).

        :type target: Union[Integer,tuple,iTree,None]
        :param target: target position definition; **target must target a single/unique item!**
                       Possible targets:

                       * index - absolute target index integer, negative values supported too (count from the end).
                       * key - key-tuple (family_tag, family_index) pair
                       * item - `iTree`-item that is already a children (future successor)
                       * None - if `None` is given we will append the item in the last position of the ´iTree´-object

        :type item: Union[iTree,object]
        :param item: `iTree`-object to be inserted in the tree.

                     .. warning::

                        As in `append()` in case the given item-object is not a `iTree`-object the item is interpreted
                        as a value and the `iTree` will be created implicit.

        :rtype: iTree
        :return: Delivers the inserted item itself
                 (it might be useful for the user to get the updated information of the object).
        """
        # Implementation state: ready, tested, doc ok
        if target is None:
            return self.append(item)
        flags = self._flags
        if flags & self._IS_TREE_PROTECTED:
            if self.is_link_root:
                # if self is link_root and the tag of the given item is different then the linked
                # ones operation is allowed!
                if hasattr(item, '_itree_prt_idx'):
                    if item.flags & (self._LINKED | self._LINK_ROOT | self._PLACEHOLDER):
                        raise TypeError('Linked items cannot be appended to linked item as local item')
                    if self._link.is_loaded and item.tag in self._link._tags:
                        self._raise_read_only_exception(self)
                elif self._link.is_loaded and NoTag in self._link._tags:
                    self._raise_read_only_exception(self)
            else:
                self._raise_read_only_exception(self)
        try:
            if item._itree_prt_idx is not None:
                raise RecursionError('Given item has already a parent')
        except AttributeError:
            # implicit definition of iTree:
            item = self.__class__(value=item)
        if self:
            sl = self._items
            size = sl.__len__()
            if size == 0 and target != 0:
                raise KeyError('%s is empty no valid target given!'%self.__class__.__name__)
            # absolute index of the target
            if type(target) is int:  # is already the absolute index!
                abs_idx = size + target if target < 0 else target
            elif hasattr(target, '_itree_prt_idx'):
                if target._itree_prt_idx is not self:
                    raise ValueError('Given target is not part of the %s'%self.__class__.__name__)
                abs_idx = target.idx
            else:
                abs_idx = self.__getitem__(target).idx
            if abs_idx == 0:
                return self._append_item_left(self, item)
            # insert in list
            sl.insert(abs_idx, item)
            # insert item to family
            tag = item._tag
            family = self._get_fam(tag)
            if family is None:
                self._setitem_fam(tag, [item])
                item._itree_prt_idx = [self, abs_idx, 0]
            else:
                fm_idx = self._get_family_insertion_idx(family, abs_idx)
                family.insert(fm_idx, item)
                if fm_idx==BLIST_SWITCH:
                    self._setitem_fam(tag,itree_list(family))
                item._itree_prt_idx = [self, abs_idx, fm_idx]
            return item
        else:
            # first item insert is append
            return self._append_item(self, item)

    # multiple appends

    def extend(self, items):
        """
        We extend the `iTree` with given items (multi append). The function is high performant and if you have to
        append a large number of items it is recommended to create an iterator of the items and
        feed them into this method. This is quicker compared to a loop doing multiple normal `append()` operations.

        .. note:: In case the to be extended items have already a parent an implicit copy will be made.
                  We do this because the internal copy can be created more effective.
                  We accept also iTree-objects as extend_items parameter and the children which have a parent will be
                  automatically copied to be integrated in this second tree. We have the same situation with a
                  filtered iterator which might be used to extend this `iTree` too.

        :type items: Iterable
        :param items: iterable-object that contains `iTree`-objects as items it can be:

                     * iterator or generator of `iTree`-objects (using next)
                     * `iTree`-object (children will be copied and extended in this tree)
                     * iterable of `iTree`-objects (list, tuple, ...)
                     * argument list for `iTree`-instance ( ´__init__()´ ) (created by ´get_init_args()´
                       or ´get_init_args_deep()´ ) -> this is most often an internal functionality.
                     * iterator or generator of value-objects (using next) - implicit `iTree`-objects created
                     * iterable of value-objects (list, tuple, ...)- implicit `iTree`-objects created

        """
        if self._flags & self._IS_TREE_PROTECTED:
            if self.is_link_root:
                # extend is allowed on link_root items
                # we must check the items in this case!
                items, check_items = tee(items, 2)  # we must reuse the iterator in this case
                if self._link.is_loaded:
                    flag_mask = self._LINKED | self._LINK_ROOT | self._PLACEHOLDER
                    error = any(
                        hasattr(i, '_itree_prt_idx') and i.flags & flag_mask
                        for i in check_items
                    )
                    if error:
                        raise PermissionError(
                            'It is not allowed to append linked items in an already linked item')
            else:
                self._raise_read_only_exception(self)
        return self._items.extend(_iTreePrivate._iter_extend(self, items))

    def extendleft(self, items):
        """
        Multy item append on left hand-side (at the beginning) of the ´iTree´.

        The operation is slower than ´extend()´ because it requires a reordering of all items in the `iTree`.

        .. note::
                The order of extended items is kept in the operation. It's comparable with:
                ´[1,2,3]+[4,5,6]=[1,2,3,4,5,6]´ but the result is not a new instance, self is kept.

        .. note:: In case the to be extended items have already a parent an implicit copy will be made.
                  We do this because the internal copy can be created more effective.
                  We accept also iTree-objects as extend_items parameter and the children which have a parent will be
                  automatically copied to be integrated in this second tree. We have the same situation with a
                  filtered iterator which might be used to extend this `iTree` too.

        :type items: Iterable
        :param items: iterable-object that contains `iTree`-objects as items it can be:

                     * iterator or generator of `iTree`-objects (using next)
                     * `iTree`-object (children will be copied and extended in this tree
                     * iterable of `iTree`-objects (list, tuple, ...)
                     * argument list for `iTree`-instance ( ´__init__()´ ) (created by ´get_init_args()´
                       or ´get_init_args_deep()´ )
                     * iterator or generator of value-objects (using next) - implicit `iTree`-objects created
                     * iterable of value-objects (list, tuple, ...)- implicit `iTree`-objects created
        """
        if self._flags & self._IS_TREE_PROTECTED:
            if self.is_link_root:
                # extend is allowed on link_root items
                # we must check the items in this case!
                items, check_items = tee(items, 2)  # we must reuse the iterator in this case
                if self._link.is_loaded:
                    error = False
                    tags = self._link.tags
                    flag_mask = self._LINKED | self._LINK_ROOT | self._PLACEHOLDER
                    for i in check_items:
                        if hasattr(i, '_itree_prt_idx'):
                            if i.flags & flag_mask or i.tag in tags:
                                error = True
                                break
                        elif NoTag in tags:
                            error = True
                            break
                    if error:
                        self._raise_read_only_exception(self)
            else:
                self._raise_read_only_exception(self)
        # prepare a list of the items in the tree
        old_items = list(self._items.__iter__())
        for i in old_items:
            # delete parent so that no copy is required for later re-extend
            i._itree_prt_idx = None
        # clean the internal structure
        self._families = {}
        self._items.clear()
        # extend new and old itmes
        return self._items.extend(_iTreePrivate._iter_extend(self, chain(items, old_items)))

    # item manipulations

    def __setitem__(self, target, value):
        """
        Replace an item with the given new item given in the `value`-parameter. The method handles also
        multiple replaces (rearrangements) like:

        ::

            >>> mytree[1],mytree[0]=mytree[0],mytree[1]

        .. warning::

            Because of the parent only principle in rearrangements operations
            an implicit copy might be created.

        .. note:: Linked items cannot be changed. If changes are required The user
                  must change the link source tree items
                  and afterwards actively rerun `load_links()` to reload the linked tree.

        :except: In case the target is not found or the `iTree` is protected (read-only tree).

        :param target: target object defining the replacement target;
                       possible types are:

                       * index - absolute target index integer (fastest operation)
                       * key - key tuple (family_tag, family_index)
                       * tag - Tag(family_tag) object targeting a whole family
                       * target-list - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                       * index slice - slice of absolute indexes
                       * key slice - tuple:  (family_tag, family_index_slice)

                       For multi targets the given value must have a matching structure (item list with same length).

                       We have two special targets which are used for placing/replacing single items in the iTree:

                       * Ellipsis `...` - new_items tag-family will be deleted and the new-item is placed in families
                         first item position
                       * items_tag - new_items tag-family will be delted and the new-item is placed in families
                         last item position

                       If those two special targets are used and the new-items family does not exist yet, the method will
                       just append the new item, no exception will be raised.

        :param value: iTree object that should replace the target or in case of multi targets a
                      tuple of items that should be used for replacements

        :return: value added items (only for internal usage)
        """
        flags = self._flags
        if flags & self._IS_TREE_PROTECTED:
            if self.is_link_root:
                # if self is link_root and the tag of the given item is different then the linked
                # ones operation is allowed!
                if hasattr(value, '_itree_prt_idx'):
                    if value.flags & (self._LINKED | self._LINK_ROOT | self._PLACEHOLDER):
                        raise TypeError('Linked items cannot be appended to linked item as local item')
                    if self._link.is_loaded and value.tag in self._link._tags:
                        self._raise_read_only_exception(self)
                elif self._link.is_loaded and NoTag in self._link._tags:
                    self._raise_read_only_exception(self)
            else:
                self._raise_read_only_exception(self)

        old_item = self.__getitem__(target)
        if old_item is value:
            return value

        # rearrangement?
        t = type(value)
        if type(value) is tuple or type(value) is list or type(value) is itree_list:
            old_items = old_item
            it_setitem = self.__setitem__
            return [it_setitem(old_items[i].idx, new) for i, new in enumerate(value)]

        # prepare new item
        if hasattr(value, '_itree_prt_idx'):
            parent_list = value._itree_prt_idx
            if parent_list is not None:
                if parent_list[0] == self:
                    # reorder operation!
                    value = self._iter_copy(value, self.__class__._get_args_skip_subtree)
                else:
                    raise RecursionError('Given item has already a parent')
        else:
            # implicit iTree definition
            value = self.__class__(value=value)

        if target is ...:  # Ellipsis is used for single append
            if self:
                tag = value.tag
                if tag in self._families:
                    # delete family
                    self.__delitem__(tag)
            return self.append(value)
        elif target == value.tag:  # family tag replaces family with the single item (same position as fist item in family
            tag = value.tag
            family= self._get_fam(tag)
            if family is None:
                return self.append(value)
            else:
                list(
                    self._raise_exception(AttributeError('Single operations on linked items are not supported')) for
                    i
                    in family if i.is_link_cover)
                old_item_idx = family[0].idx
                sl = self._items
                for i in reversed(family[1:]):
                    sl.__delitem__(i.idx)
                sl.__setitem__(old_item_idx, value)
                self._families[tag] = [value]
                value._itree_prt_idx = (self, old_item_idx, 0)
                return value
        # normal setitem replaces old item
        # handle old item
        try:
            abs_idx = old_item.idx
        except AttributeError as e:
            raise LookupError(
                'Given target is not unique; set operation can only be made on unique items!'
            ) from e
        # if old_item.is_linked:
        #    raise PermissionError('The target item is read_only (linked)!')
        o_tag, o_fm_idx = old_item.tag_idx
        # start the manipulation
        old_item._itree_prt_idx = None
        # replace old item in super list
        self._items.__setitem__(abs_idx, value)
        v_tag = value._tag
        if v_tag == o_tag:  # same family
            family = self._getitem_fam(v_tag)
            # replace old item in family list
            family.__setitem__(o_fm_idx, value)
            fm_idx = o_fm_idx
        else:
            # different families
            # del old item from family
            self._getitem_fam(o_tag).__delitem__(o_fm_idx)
            try:
                family = self._getitem_fam(v_tag)
                fm_idx = self._get_family_insertion_idx(family, abs_idx)
                family.insert(fm_idx, value)
            except (KeyError, IndexError):
                self._setitem_fam(v_tag, [value])
                fm_idx = 0
        value._itree_prt_idx = [self, abs_idx, fm_idx]
        return value

    def move(self, target=None):
        """
        Move this item in given target position (item will be positioned **before** the given target).
        The given target must be a unique item! If None is given
        the item will be moved in the last position of the `iTree`. If an ìTree`-object
        is given as target it must be a children of the same parent (sibling).

        :type target: Union[Integer,tuple,iTree,None]
        :except: LookupError in case the target is not found or not unique!

        :param target: target-object defining the replacement target;
                       possible types are:

                       * index - absolute target index integer, negative values supported too (count from the end).
                       * key - key-tuple (family_tag, family_index) pair
                       * item - `iTree`-item that is already a children (future successor)
                       * None - if `None` is given we will move the item to the last position in the ´iTree´-object

        :return: self (with updated indexes)
        """
        if self._itree_prt_idx is None:
            raise LookupError('This item is not a children of a %s'%self.__class__.__name__)
        parent = self._itree_prt_idx[0]
        flags = parent._flags
        if flags & self._IS_TREE_PROTECTED:
            if parent.is_link_root:
                if parent._link.is_loaded and self.tag in parent._link._tags:
                    self._raise_read_only_exception(self)
            else:
                self._raise_read_only_exception(self)
        if target is None:
            move_item = parent.__delitem__(self.idx)
            return parent.append(move_item)
        # check if target exists:
        if type(target) is not int:
            try:
                target_idx = parent.__getitem__(target).idx
            except AttributeError as e:
                raise LookupError('Given target is not unique') from e
        else:
            target_idx = target
        src_idx = self.idx
        move_item = parent.__delitem__(src_idx)
        return parent.insert(target_idx, move_item)

    def rename(self, new_tag):
        """
        give the item a new family tag

        The renaming of the item implies a reordering of the items in the tree because the family order
        depends on the global/absolute order of items.

        :type new_tag: Hashable
        :param new_tag: new tag (any kind of hashable object)

        :rtype: iTree
        :return: Delivers the renamed item itself
                 (it might be useful for the user to get the updated information of the object).

        """
        parent_list = self._itree_prt_idx

        if parent_list is not None:
            parent = parent_list[0]
            flags = parent._flags
            if flags & self._IS_TREE_PROTECTED:
                if parent.is_link_root:
                    if parent._link.is_loaded:
                        tags = parent._link._tags
                        if new_tag in tags:
                            self._raise_read_only_exception(self)
                        if self._flags & (self._LINKED | self._PLACEHOLDER):
                            self._raise_read_only_exception(self)
                else:
                    self._raise_read_only_exception(self)
        else:
            self._tag = new_tag
            return
        families = parent._families
        tag = self._tag
        # remove old tag in the map-dict
        family = families.__getitem__(tag)
        if len(family) == 1:
            families.__delitem__(tag)
        else:
            family.remove(self)
        # insert new tag
        self._tag = new_tag
        if new_tag in families:
            new_family = families.__getitem__(new_tag)
            fm_idx = self._get_family_insertion_idx(new_family, self.idx)
            new_family.insert(fm_idx, self)
            self._itree_prt_idx[2] = fm_idx
        else:
            # create new family
            families.__setitem__(new_tag, [self])
            self._itree_prt_idx[2] = 0
        return self

    def reverse(self):
        """
        Reverse the order of all children in the `iTree`.

        If you do not want to change the object itself (in place operation) you might use the iterator
        `reversed()` instead.

        """
        flags = self._flags
        if flags & self._IS_TREE_PROTECTED:
            if not self.is_link_root or self._link.is_loaded:
                self._raise_read_only_exception(self)
        else:
            self._items.reverse()
            for family in self._families.values():
                family.reverse()

    def rotate(self, n=1):
        """
        Rotate children of the `iTree`-object n times (n positions)
        (rotate 1 times means move last item to first position)

        If no parameter is given we rotate by one position only.

        The rotation can be made in negative direction too (give negative numbers).

        In case zero is given the operation is neutral and nothing will be changed.

        .. note:: There is no in-depth counterpart of this method available.

        :type n: integer
        :param n: number of positions the items should be rotated
        """
        flags = self._flags
        if flags & self._IS_TREE_PROTECTED:
            if not self.is_link_root or self._link.is_loaded:
                self._raise_read_only_exception(self)
        elif n > 0:
            move_items = [self.pop() for _ in range(n)]
            move_items.reverse()
            self.extendleft(move_items)
        elif n < 0:
            move_items = [self.pop(0) for _ in range(-n)]
            # move_items.reverse()
            self.extend(move_items)

    def sort(self, key=None, reverse=False):
        """
        Sorting operation -> same behavior as sort of lists (parameter description is taken from list documentation).

        .. note:: This is an "in place" operation which changes the content of the object the build-in `sorted()`
                    might be use instead (if the original object should not be changed):

                        >>> a=iTree(subtree=[iTree(3),iTree(2),iTree(4),iTree(1)])
                        >>> a.render()
                        iTree()
                        > iTree(3)
                        > iTree(2)
                        > iTree(4)
                        > iTree(1)
                        >>> b=iTree(subtree=(a[i] for i in sorted(a.keys())))
                        iTree()
                        > iTree(1)
                        > iTree(2)
                        > iTree(3)
                        > iTree(4)



        Internally in this operation a copied sorted list is created, and afterwards the whole structure is cleared
        and rebuild based on the sorted list.

        The default-operation is to the sort based on the list of keys
        (tag-family, family_index) pair of the items. The base of the sorting can be modified by changing
        the `target_type` parameter.

        :param key:  specifies a function of one argument that is used to extract a comparison key
                     from each list element (for example, key=str.lower). The key corresponding to each item in
                     the list is calculated once and then used for the entire sorting process.
                     The default value of None means that list items are sorted directly without calculating
                     a separate key value.

        :param reverse: is a boolean value. If set to True, then the list elements are sorted
                        as if each comparison were reversed.

        """
        flags = self._flags
        if flags & self._IS_TREE_PROTECTED:
            if not self.is_link_root or self._link.is_loaded:
                self._raise_read_only_exception(self)
        else:
            sort_list = list(self._items.__iter__())
            sort_list.sort(key=key, reverse=reverse)
            self._items.clear()
            self._families = {}
            self.extend(sort_list)


    def __delitem__(self, target):
        """
        The function deletes the targeted item in the tree.

        :except: In case the target is not found or the `iTree` is protected (read-only tree).

        :type target: Union[int,tuple,Hashable,Iterable,slice]
        :param target: target object defining the replacement target;
                       possible types are:

                           * *index* - absolute target index integer (fastest operation)
                           * *key* - key tuple (family_tag, family_index)
                           * *tag* - Tag(family_tag) object targeting a whole family
                           * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                           * *index-slice* - slice of absolute indexes
                           * *key-slice* - tuple of (family_tag, family_index_slice)
                           * *itree_filter* - method (callable) for filtering the children of the object

        :return: deleted item
        """
        is_link_root = False
        if self._flags & self._IS_TREE_PROTECTED:
            if not self.is_link_root:
                self._raise_read_only_exception(self)
            elif self.is_link_loaded:
                is_link_root = True
        if self:
            t=type(target)
            if t is int:  # special very quick access:
                if is_link_root:
                    item = self.getitem_by_idx(target)
                    if item._flags & (self._LINKED | self._PLACEHOLDER):
                        self._raise_read_only_exception(self)
                del_item = self._items.pop(target)
                tag = del_item._tag
                family = self._getitem_fam(tag)
                size_fam = len(family)
                if hasattr(del_item, '_link') and del_item._link._link_item is not None:
                    f_idx = del_item.tag_idx[1]
                    link_item = del_item._link._link_item
                    self._items.insert(target, link_item)
                    family[f_idx] = link_item
                    link_item._itree_prt_idx = [self, target, f_idx]
                    del_item._itree_prt_idx = None
                    return del_item
                elif size_fam - 1:
                    # find family index
                    i = del_item._itree_prt_idx[2]
                    if i < size_fam and del_item is family[i]:
                        family.__delitem__(i)
                    else:
                        start = 0
                        for _ in family:  # for is quicker as while
                            i = family.index(del_item, start)
                            if family[i] is del_item:
                                f_idx = i
                                break
                            start = i + 1
                        family.__delitem__(f_idx)
                else:
                    self._families.__delitem__(tag)
                del_item._itree_prt_idx = None
                return del_item
            elif t is slice:  # special quick access:
                items=self._items
                del_items = items[target]
                if is_link_root:
                    for item in del_items:
                        if item._flags & (self._LINKED | self._PLACEHOLDER):
                            self._raise_read_only_exception(self)
                del items[target]
                for idx,del_item in zip(range(target.start,target.stop),del_items):
                    tag = del_item._tag
                    family = self._getitem_fam(tag)
                    size_fam = len(family)
                    if hasattr(del_item, '_link') and del_item._link._link_item is not None:
                        f_idx = del_item.tag_idx[1]
                        link_item = del_item._link._link_item
                        self._items.insert(idx, link_item)
                        family[f_idx] = link_item
                        link_item._itree_prt_idx = [self, idx, f_idx]
                        del_item._itree_prt_idx = None
                        return del_item
                    elif size_fam - 1:
                        # find family index
                        i = del_item._itree_prt_idx[2]
                        if i < size_fam and del_item is family[i]:
                            family.__delitem__(i)
                        else:
                            start = 0
                            for _ in family:  # for is quicker as while
                                i = family.index(del_item, start)
                                if family[i] is del_item:
                                    f_idx = i
                                    break
                                start = i + 1
                            family.__delitem__(f_idx)
                    del_item._itree_prt_idx = None
                    return del_items
            else:
                items = self.__getitem__(target)
                if hasattr(items, '_itree_prt_idx'):
                    return self.__delitem__(items.idx)
                else:
                    return [self.__delitem__(item.idx) for item in items]
        raise KeyError('Given target %s not found in item %s' % (repr(target), str(self)))

    def clear(self, keep_value=False, local_only=False):
        """
        deletes all children
        and the value!

        All flags stay unchanged, except the load_links flag!

        :type keep_value: bool
        :param keep_value:
                        * True - value is not deleted
                        * False - value will be replaced with NoValue

        :type local_only: bool
        :param local_only:

                        * True - clear only the local items
                        * False - clear whole object (The object is reset to the no links loaded
                          state and locals are deleted)
        """
        flags = self._flags
        if flags & self._IS_TREE_PROTECTED and not self.is_link_root:
            self._raise_read_only_exception(self)
        if self.is_link_root:
            if local_only:
                for item in self._iter_locals_add_placeholders(self):
                    if item.is_placeholder:
                        continue
                    self.__delitem__(item.idx)
            else:
                self._link._loaded = False
                self._unset_flags(self, self._LOAD_LINKS)
                self._items.clear()
                self._families = {}
        else:
            self._unset_flags(self, self._LOAD_LINKS)
            self._items.clear()
            self._families = {}
        if not keep_value:
            self._value = NoValue

    def pop(self, target=-1):
        """
        pop the item out of the tree, if no key is given the last item will be popped out

        We do not have the method popleft because `pop(0)` does the same.

        :type target: Union[int,tuple,Hashable,Iterable,slice,iTree]
        :param target: target of popped item(s):

                       * *index* - absolute target index integer (fastest operation)
                       * *key* - key tuple (family_tag, family_index)
                       * *tag* - Tag(family_tag) object targeting a whole family
                       * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                       * *index-slice* - slice of absolute indexes
                       * *key-slice* - tuple of (family_tag, family_index_slice)
                       * *itree_filter* - method (callable) for filtering the children of the object

        :return: popped out item(s) (parent will be set to None). In case multiple items are
                 removed an iterator over the removed items is given.
        """
        return self.__delitem__(target)

    def remove(self, item):
        """
        With remove the given target is a `iTree` child that should be removed.

        The method is only in because we like to be compatible with lists interface but the pop method target
        allows already to use a child as a target too.

        :except: If given item is not a child of the parent or the ìTree`-objects tree is protected

        :type item: Union[iTree,Iterable]
        :param item: Child or iterable of children to be removed from the tree

        :return: removed item(s) (parent will be set to None) - in case of multiple removes the
                 method delivers a list no iterator because anyway a list is created
        """
        if hasattr(item, '_itree_prt_idx'):
            if item._itree_prt_idx is not None and item._itree_prt_idx[0] is self:
                return self.__delitem__(item.idx)
            else:
                raise ValueError('Given item object is not a child of this %s-object'%self.__class__.__name__)
        try:
            is_link_root = self.is_link_root and self.is_link_loaded
            item_list = list(
                item)  # we consume the iterator here because we need it multiple times we used list to reverse later on
            for i in item_list:  # check if the items in the iterator are valid for the operation
                try:
                    if i._itree_prt_idx[0] is not self:
                        raise AttributeError()
                    if is_link_root and (i.is_linked or i.is_placeholder):
                        self._raise_read_only_exception(self)
                    continue
                except AttributeError as e:
                    raise ValueError(
                        'The object %r is not a child of this %s-object'
                        % (repr(i),self.__class__.__name__)
                    ) from e
            for i in reversed(item_list):  # we see advantage for most cases if we remove in reversed order
                self.__delitem__(i.idx)
            return item_list
        except (PermissionError, ValueError):
            raise
        except:
            raise TypeError('As item parameter we expect a tree child or an iterable of children')

    # *** getters: *****************************************************************************************************

    def __getitem__(self, target):
        """
        Main common get method for children (first level items).

        In case the given targets is a absolute index or a key (tag,family-index) pair the method will
        deliver a unique item back. This operation is prioritized over the other operations.

        For all other targets the method will deliver a list with the targeted items as result.

        In some cases an empty list might be delivered and no exception might be raised
        (e.g. filter query delivers no match).

        In case user likes to have other return-types he might check the other available get methods
        ( `get()`, `get.single()`, `get.iter()`) or he might also use the itertree helper method `getter_to_list()` to
        convert any of the possible results into a list.

        :except: In case of no match (even if a part is not matching (e.g. one index in an index-list) the
                 method will raise
                 a KeyError (no matching target given); IndexError (no matching index given) or
                 ValueError (no valid type of target given).

        :type target: Union[int,tuple,list,slice]
        :param target: target object targeting a child or multiple children in the ´iTree´.
                       Possible types are:

                           * *index* - absolute target index integer (fastest operation)
                           * *key* - key tuple (family_tag, family_index)
                           * *index-slice* - slice of absolute indexes
                           * *key-index-slice* - tuple of (family_tag, family_index_slice)
                           * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                           * *key-index-list* - tuple of (family_tag, family_index_list)
                           * *tag* - family_tag object targeting a whole family
                           * *tag-set* - a set of family-tags targeting the items of multiple families
                           * *itree_filter* - method (callable) for filtering the children of the object
                           * *all-children* - if build-in `iter` or `...`(Ellipsis) is given a list
                             of all children will be given (same like list(itree.__iter__())`)

        :rtype: Union[iTree,list]
        :return: Target was *index* or *key* -> one `iTree` item will be given;
                 for all other targets a list will be delivered.
        """
        if self:
            t = type(target)
            if t is tuple:
                try:
                    # check for key as quick as possible!
                    fam_tag, fam_idx = target  # unpack to be sure we have a tuple of two items
                    if fam_idx is ...:
                        return self._getitem_fam(fam_tag)[:]
                    # key, family-index or  key, family-index-slice:
                    return self._getitem_fam(fam_tag)[fam_idx]
                except TypeError:
                    try:
                        family = self._getitem_fam(fam_tag)
                        return [family[i] for i in fam_idx]
                    except:
                        try:
                            return list(self._getitem_fam(target))
                        except:
                            raise ValueError('Given target {} is invalid'.format(repr(target)))  # from e
                except IndexError:
                    try:
                        return list(self._getitem_fam(target))
                    except:
                        raise IndexError(
                            'Given family-idx of target {} not found'.format(repr(target)))  # from e
                except:
                    try:
                        return list(self._getitem_fam(target))
                    except:
                        if 'fam_idx' in locals():
                            raise KeyError(
                                'Given target {} invalid or not found'.format(repr(target)))  # from e
                        else:
                            raise ValueError('Given target {} is invalid'.format(repr(target)))  # from e
            elif t is int or t is slice:
                # absolute index or absolute index-slice
                try:
                    return self.getitem_by_idx(target)
                except IndexError:
                    try:
                        # Maybe we have a tag that matches?
                        return list(self._getitem_fam(target))
                    except:
                        raise IndexError(
                            'Given abs-idx in target {} is out of range'.format(repr(target)))  # from e

            elif t is TagIdx:  # downward compatibility
                fam_tag, fam_idx = target  # unpack
                return self._getitem_fam(fam_tag)[fam_idx]
            elif t is set:
                # tags-set
                result = []
                for tag in target:
                    result.extend(self._families[tag])
                if result:
                    return result
                raise KeyError('No matching item found')
            elif t is list:
                # multiple targets given they will be combined in one list
                result = []
                for sub_target in target:
                    r = self[sub_target]
                    if type(r) is list:
                        result.extend(r)
                    else:
                        result.append(r)
                if result:
                    return result
                raise KeyError('No matching item found')
            elif target is Ellipsis:
                return self.getitem_by_idx(self._NoneSlice)  # full slice is incredible fast on blists
            elif callable(target):
                if target is iter:
                    # give all items
                    return self.getitem_by_idx(self._NoneSlice)
                # filter given?
                try:
                    return list(filter(target, self))
                except Exception:
                    if "<lambda>" in str(target):
                        # We try to identify in this case which child made the troubles
                        for c in self:
                            try:
                                target(c)
                            except Exception:
                                raise TypeError('lambda: raised an exception in filter-calculation, the %i. child %s'
                                                ' is incompatible with the calculation' % (c.idx, str(c)))
            result= self._get_fam(target)
            if result is not None:
                return result[:] # slice is quicker then copy
        raise KeyError('Given target: %s not found' % repr(target))

    # *** math operations and operations creating new/copied representations *******************************************

    #use def __reverse__() from super class

    def __mul__(self, factor):
        """
        Multiplication function a iTree is multiplied (copies) and put in a new iTree:

        my_single_item=iTree('multi')
        multi=my_single_item*1000

        In case factor is another iTree the cartesian product will be calculated. The resulting iTree
        will have a length of: len(self)*len(factor)*2 (The factor 2 results
        from the difference of the cartesian to the normal product)
        The subtree looks like (item1_x from self item2_x from factor):
        item1_0, item_2_0, item1_0, item_2_1, item1_0, item2_2, ..., item1_1, item2_0, item1_1, item2_1, ...



        HINT: In this operation multiple copies of the original item generated.

        :param factor: integer to multiply with
        :return: iTree object containing multiplied children
        """
        if hasattr(factor, '_itree_prt_idx'):
            if self.is_link_root:
                raise TypeError('__mul__() on link-root items is not supported')
            subtree = chain.from_iterable(
                product((i.copy() for i in self), (i.copy() for i in factor)))
        else:
            subtree = repeat(self.copy(), factor)
        return self.__class__(self._tag, copy.copy(self._value), subtree, None, self._flags)

    def __rmul__(self, other):
        if hasattr(other, '_itree_prt_idx'):
            subtree = chain.from_iterable(
                product((i.copy() for i in self), (i.copy() for i in other)))
        else:
            subtree = repeat(self.copy(), other)
        return self.__class__(NoTag, NoValue, subtree)

    def __sub__(self, other):
        """
        To subtract two iTree objects we copy the self-object and we iterate over the other object items.
        In case a matching key is found in self the item will be deleted in the copy.

        :param other:
        :return:
        """
        new = self.copy()
        if self.tag == other.tag:
            new._tag = NoTag
        else:
            try:
                new._tag = new._tag - other._tag
            except Exception:
                t = type(new._tag)
                t2 = type(other._tag)
                if t == t2:
                    if t is str:
                        new._tag = new._tag.replace(other._tag, '')
                    if t is bytes:
                        new._tag = new._tag.replace(other._tag, b'')
        if self._value_equal(self.value, other.value):
            new._value = NoValue
        else:
            try:
                new._value = new._value - other._value
            except Exception:
                t = type(new._value)
                t2 = type(other._value)
                if t == t2:
                    if t is str:
                        new._value = new._value.replace(other._value, '')
                    if t is bytes:
                        new._value = new._value.replace(other._value, b'')
        # This code might be improved!
        del_idx = []
        for item in other:
            key = item.tag_idx
            if key in new and new[key] == item:
                del_idx.append(new[key].idx)
                continue
            new[key] = new[key] - item
        for i in reversed(del_idx):  # we delete from the end if not the index would change after deleting first one
            del new[i]
        return new

    def __add__(self, other):
        """
        If two iTree objects are added the children in the two added iTrees are copied and combined
        to a new iTree object the other attributes are taken over from the first iTree in the given sum.

        :param other: iTree object that should be added
        :return: New iTree object containing copies of all children
        """
        if hasattr(other, '_itree_prt_idx'):
            if self.is_link_root:
                raise TypeError('__add__() on link-root items is not supported')
            return self.__class__(copy.copy(self._tag), copy.copy(self._value),
                         subtree=chain((item.__copy__() for item in self),
                                       (item.__copy__() for item in other)), flags=self._flags)
        else:
            raise TypeError('Added item is not an instance of iTree')

    def __copy__(self):
        """
        create a copy of this item

        The difference in between copy and deepcopy for iTree is just that we do in deepcopy a copy
        of all data items too. In copy we just copy the iTData object not the items itself, they stay as pointers
        to the original objects.

        The operation is very important for `iTree`-class because of the one parent only principle we are forced to
        do a copy of all sub-items (in-depth). It's not possible to copy just the top-level element only.

        The function is used internally in extend operations too. And we can see (profiler) that
        improvements in this method have big impact.

        :return: copied iTree object
        """
        return self._iter_copy(self, self.__class__._get_copy_args)

    def copy_keep_value(self):
        """
        Create a copy of this item.

        The difference in between normal `copy()` and this method is that the value objects are
        completely untouched in this operation (for immutable objects there is no difference
        in between the two copy operations).

        :return: copied iTree object
        """
        return self._iter_copy(self, self.__class__._get_args_skip_subtree)

    def copy(self, *args, **kwargs):
        """
        create a copy of this item

        The difference in between `copy()` and `deepcopy()` for `iTree` is just that we do in `deepcopy()` a deepcopy
        of all value items. In `copy()` we just copy the value object not the items inside, the pointers
        to the original objects are kept (for immutable objects there is no difference).

        :return: copied iTree object
        """
        return self._iter_copy(self, self.__class__._get_copy_args)

    def __deepcopy__(self, *args, **kwargs):
        """
        create a deepcopy of this item

        The difference in between `copy()` and `deepcopy()` for `iTree` is just that we do in `deepcopy()` a deepcopy
        of all value items. In `copy()` we just copy the value object not the items inside, the pointers
        to the original objects are kept (for immutable objects there is no difference).

        :return: deep copied new iTree object
        """
        return self._iter_copy(self, self.__class__._get_deepcopy_args)

    def deepcopy(self, *args, **kwargs):
        """
        create a deepcopy of this item

        The difference in between `copy()` and `deepcopy()` for `iTree` is just that we do in `deepcopy()` a deepcopy
        of all value items. In `copy()` we just copy the value object not the items inside, the pointers
        to the original objects are kept (for immutable objects there is no difference).

        :return: deep copied new iTree object
        """
        return self._iter_copy(self, self.__class__._get_deepcopy_args)

    # *** size & comparisons *******************************************************************************************

    # __len__() of the super-class blist is not overloaded!

    def filtered_len(self, filter_method):
        """
        Calculates the number of filtered children.

        :type filter_method: Callable
        :param filter_method: filter method that checks for matching items
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches (see :ref:`filter_method <filter_method>`)

        :rtype: int
        :return: Number of matching items found
        """
        return sum(1 for _ in filter(filter_method, self))


    def __contains__(self, target):
        """
        Checks if an ´iTree´ object is part of the ´iTree´
        for comparison == -> ´__eq__()´ is used. For finding a specific object use ´is_parent()´ or 'is_in()` instead.
        
        In case no ´iTree´ object is given the function uses ´__getitem__´ to check 
        if matching item(s) exists.

        .. note:: There is no coresponding in-depth function available the user can easy search via:
                     >>> # Let itree be the iTree object the target should be searched in
                     >>> any(tag == i.tag for i in itree.deep)
                     >>> any(searchkey == i[0][-1] for i in itree.deep.tag_idx_paths())
                     >>> s=len(index_list)
                     >>> any(len(i[0])>s and index_list == i[0][(-s+1):] for i in itree.deep.idx_paths())


        :param target: iTree object searched for or a target used by ´__getitem__()´ method
        :return:
                * True - matching child is found
                * False - no matching item found
        """
        if hasattr(target, '_itree_prt_idx'):
            for child in self:
                if child == target:
                    return True
        else:
            with suppress(Exception):
                item = self.__getitem__(target)
                if not hasattr(item, '_itree_prt_idx'):
                    next(item)
                return True
        return False

    def is_tag_in(self, tag):
        """
        Checks if a iTree contains the given family-tag (first-level only)
        :param tag: family tag
        :return: True/False
        """
        if self:
            return tag in self._families
        else:
            return False

    def is_in(self, item):
        """
        Checks if the given object is child of the iTree.
        Different to ´__contains__()´ we check here for the instance (specific) object (is)
        and not based on ´__eq__()´.

        :param item: iTree object to be searched for
        :return:
                * True - matching child is found
                * False - no matching item found
        """
        if hasattr(item, '_itree_prt_idx'):
            p = item._itree_prt_idx
            return p is not None and p[0] is self
        else:
            raise TypeError('Given item is not an instance of iTree')

    def __eq__(self, other):

        """
        compares if the tag, value and children content of another item matches with this item

        .. note::

                If you like to check if it is really the same object you should use ´is´ instead of ´==´ operator

        :param other: other iTree

        :return: boolean match result (True match/False no match)
        """
        if self is other:
            return True
        try:
            if self._tag != other._tag or \
                    len(self) != len(other) or \
                    not self._value_equal(self._value, other._value):
                return False
            for i, ii in zip(self.deep, other.deep):
                try:
                    a1 = i.get_init_args(None, False)
                    a2 = ii.get_init_args(None, False)
                    if a1 == a2:
                        # quick compare might fail because of the value
                        continue
                    if self._value_equal(a1[1], a2[1]):
                        continue
                    return False
                except AttributeError:
                    return False  # None
                except Exception:
                    if not self._value_equal(a1[1], a2[1]):
                        return False
                    elif a1[0] != a2[0]:
                        return False
                    elif len(a1) > 2 and a1[2:] != a2[2:]:
                        return False
            return True
        except Exception:
            return False

    def __ne__(self, other):
        """
        This is just the inverse operation of __eq__
        :param other: other item to be compared with
        :return: True/False
        """
        return not self.__eq__(other)

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

    def equal(self, other, check_coupled=False, check_flags=False):
        """
        compares if the data content of another item matches with this item

        :param other: other iTree

        :param check_coupled: check the couple object too? (Default False)

        :param check_flags: check the flags of the objects? (Default False)

        :return: boolean match result (True match/False no match)
        """

        if self is other:
            return True

        if check_flags:
            check1 = lambda i, ii: i._flags == ii._flags
        else:
            check1 = lambda i, ii: True

        if check_coupled:
            check2 = lambda i, ii: (hasattr(i, '_coupled') and hasattr(ii, '_coupled')) and \
                                   i._coupled is ii._coupled if (hasattr(i, '_coupled') or hasattr(ii, '_coupled')) \
                else True
        else:
            check2 = lambda i, ii: True
        check = lambda i, ii: check1(i, ii) and check2(i, ii)
        if not check(self, other):
            return False
        try:
            if self._tag != other._tag or \
                    len(self) != len(other) or \
                    not self._value_equal(self._value, other._value):
                return False
            for i, ii in zip(self.deep, other.deep):
                if not check(i, ii):
                    return False
                a1 = i.get_init_args(None, False)
                a2 = ii.get_init_args(None, False)
                try:
                    if a1 == a2:
                        # quick compare might fail because of the value
                        continue
                    if self._value_equal(a1[1], a2[1]):
                        continue
                    return False
                except Exception:
                    if not self._value_equal(a1[1], a2[1]):
                        return False
                    elif a1[0] != a2[0]:
                        return False
                    elif len(a1) > 2 and a1[2:] != a2[2:]:
                        return False
            return True
        except Exception:
            return False

    def count(self, item):
        """
        Counts how many equal (`==`) children are in the `iTree`-object.

        :type item: iTree
        :param item: The `iTree`-items will be compared with this item

        :rtype: int
        :return: Number of matching items found
        """
        return sum(item == i for i in self)

    def index(self, item, start=None, stop=None):
        """
        The index method allows to search for the absolute index of a matching item in the `iTree`.
        The item must be a iTree object and the index will deliver the first match. The comparison is made via
        `==` operator.

        If item is not found a IndexError will be raised

        .. note:: To get the index of a specific item instance the `.idx`- property
                  should be used.

        :type item: iTree
        :param item: iTree object to be searched for

        :type start: Union[iTree,target_path]
        :param start: iTree item or start target_path where index search should be started (start item is included in search)

        :type stop: Union[iTree,target_path]
        :param stop: iTree item or stop target_path  where index search should be stopped (stop item is not included in search)

        ;rtype: int
        :return: absolute index of the found item
        """
        if self:
            iterator = self.__iter__()
            if start is not None:
                if not hasattr(start, '_itree_prt_idx'):
                    start = self.get.single(start)
                try:
                    first_item = next(dropwhile(lambda i: i is not start, iterator))
                    if first_item == item:
                        return first_item.idx
                except StopIteration:
                    raise IndexError('No matching item found')
            if stop is not None:
                if not hasattr(stop, '_itree_prt_idx'):
                    stop = self.get.single(stop)
                try:
                    item = next(dropwhile(lambda i: i is not stop and i != item, iterator))
                    if item is not stop:
                        return item.idx
                    raise StopIteration
                except StopIteration:
                    raise IndexError('No matching item found')
            else:
                try:
                    item = next(dropwhile(lambda i: i != item, iterator))
                    return item.idx
                except StopIteration:
                    raise IndexError('No matching item found')

    def __hash__(self):
        """
        The hash operation is available

        .. node::As for the `==` operator we do not consider, parent, coupled items or flags properties of the object

        :return: integer hash
        """
        try:
            h = hash(self._value)
        except TypeError:
            h = hash(pickle.dumps(self._value))
        return hash((tuple(self), self._tag, h))

    # *** ITERATORS ****************************************************************************************************

    # standard iterators list/dict

    # def __iter__(self): #use function of the super class!

    # dict like iterators:

    def keys(self, filter_method=None):
        """
        Iterates over all children and deliver the children tag-idx tuple (family-tag,family_index)

        .. note::
            This is a dict like iterator that delivers the unique keys for all children.

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks the item
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches

                            If `None` is given filtering is inactive.

        :rtype: Iterator
        :return: iterator over the tag-idx of the children
        """
        tag_cnts = {tag: -1 for tag in self._families.keys()}
        if filter_method:
            for item in self:
                tag = item._tag
                # as side effect we update the item cache too:
                item._itree_prt_idx[2] = tag_cnts[tag] = cnt = tag_cnts[tag] + 1
                if filter_method(item):
                    yield tag, cnt
        else:
            for item in self:
                tag = item._tag
                item._itree_prt_idx[2] = tag_cnts[tag] = cnt = tag_cnts[tag] + 1
                yield tag, cnt

    def values(self, filter_method=None):
        """
        Iterates over all children and deliver the children values

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches (see :ref:`filter_method <filter_method>`)

                            If `None` is given filtering is inactive.

        :rtype: Iterator
        :return: iterator over the values stored in the children
        """
        if filter_method is None:
            return (i._value for i in self)
        else:
            return (i._value for i in filter(filter_method,self))

    def items(self, filter_method=None, values_only=False):
        """
        Iterates over all children and deliver the children
        item-tuples (key,item) or (key,value). As key we use the unique tag-idx: (tag-family,family-index).

        The function is comparable with dicts `items()` function.


        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches (see :ref:`filter_method <filter_method>`)

                            If `None` is given filtering is inactive.

        :type values_only: bool
        :param values_only:
                    * `False` (default) - in the key,value tuple the iterator put the iTree object as value in
                    * `True` - in the key,value tuple the iterator put "only" the value object of the `iTree`-object in

        :rtype: Generator
        :return: iterator over the target keys and item value of the children
        """
        tag_cnts = {tag: -1 for tag in self._families.keys()}
        if values_only:
            if filter_method:
                for item in self:
                    tag = item._tag
                    # as side effect we update the item cache too:
                    item._itree_prt_idx[2] = tag_cnts[tag] = cnt = tag_cnts[tag] + 1
                    if filter_method(item):
                        yield (tag, cnt), item.value
            else:
                for item in self:
                    tag = item._tag
                    item._itree_prt_idx[2] = tag_cnts[tag] = cnt = tag_cnts[tag] + 1
                    yield (tag, cnt), item.value
        elif filter_method:
            for item in self:
                tag = item._tag
                # as side effect we update the item cache too:
                item._itree_prt_idx[2] = tag_cnts[tag] = cnt = tag_cnts[tag] + 1
                if filter_method(item):
                    yield (tag, cnt), item
        else:
            for item in self:
                tag = item._tag
                item._itree_prt_idx[2] = tag_cnts[tag] = cnt = tag_cnts[tag] + 1
                yield (tag, cnt), item

    def iter_families(self, filter_method=None, order_last=False):
        """
        This is a special iterator that iterates over the families in `iTree`. It delivers per family the tag and
        a list of the containing items. The order is defined by the absolute index of the first item in each family

        Method will be reached via `iTree.Families.iter()`

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                              and delivers `True`/`False`.
                              The filter_method targets always the `iTree`-child-object and checks a characteristic
                              of this object for matches (see :ref:`filter_method <filter_method>`)

                              If filter_method is None no filtering is performed

                              .. note:: An internal filtering is available because this may change the order of
                                        the delivered items. An external filter with same method might
                                        deliver a different result!

        :type order_last: bool
        :param order_last:
            * False (default) - The tag-order is based on the order of the first items in the family
            * True - The tag-order is based on the order of the last items in the family

        :rtype: Generator
        :return: iterator over all families delivers tuples of (family-tag, family-item-list)
        """
        if self:
            if order_last:
                index = -1
            else:
                index = 0

            if filter_method:

                return ((i.tag, [i for i in self._getitem_fam(i._tag) if filter_method(i)])
                        for i in sorted((v[index] for v in self._families.values()), key=lambda i: i.idx))
            else:
                return ((i.tag, list(self._getitem_fam(i._tag)))
                        for i in sorted((v[index] for v in self._families.values()), key=lambda i: i.idx))

    def iter_family_items(self, order_last=False):
        """
        This is a special iterator that iterates over the families in `iTree`. It iters over the items of each family
        the ordered by the first or the last items of the families.

        :type order_last: bool
        :param order_last:
            * False (default) - The tag-order is based on the order of the first items in the family
            * True - The tag-order is based on the order of the last items in the family

        :rtype: Generator
        :return: iterator over all families delivers tuples of (family-tag, family-item-list)
        """
        if self:
            if order_last:
                index = -1
            else:
                index = 0

            for i in sorted((v[index] for v in self._families.values()), key=lambda i: i.idx):
                for item in self._getitem_fam(i._tag):
                    yield item

    def tags(self, order_last=False):
        """
        iters over all family-tags in level 1 (children). The order is based on first or
        last item in the family.

        :type order_last: bool
        :param order_last:
            * False (default) - The tag-order is based on the order of the first items in the family
            * True - The tag-order is based on the order of the last items in the family

        :rtype: Iterator
        :return: tag iterator
        """
        if self:
            s = len(self._families)
            s2 = len(self)
            if s2 == 1:
                # only a single family tag exists
                yield self.getitem_by_idx(0).tag
            elif s == s2:
                # all items in the tree have another tag
                for i in self:
                    yield i.tag
            else:
                if order_last:
                    index = -1
                else:
                    index = 0
                for i in sorted((v[index] for v in self._families.values()), key=lambda i: i.idx):
                    yield i.tag

    # *** outputs/dumps ************************************************************************************************

    def __repr__(self):
        """
        Create representation string from which the object can be theoretically be reconstructed via `eval()`
        (might not work in case of
        value-objects that do not have a working `__repr()` method)

        :rtype: str
        :return: representation string
        """
        out = ['%s('%self.__class__.__name__]
        if self._tag is not NoTag:
            out.append(repr(self._tag))
            out.append(', ')
        if self._value is not NoValue:
            out.append('value=')
            out.append(repr(self._value))
            out.append(', ')
        if self:
            if self.level > (sys.getrecursionlimit() / 5):
                out.append('subtree=[ ... ]')
            else:
                subtree = self._items.__repr__()
                if subtree[0] == 'b':
                    # we shorten blist from definition
                    subtree = subtree[6:-1]
                out.append('subtree=')
                out.append(subtree)
                out.append(', ')
        is_links_loaded = False
        if hasattr(self, '_link'):
            link = self._link
            if link._link_item is not None:
                out.append('link=iTLink(link_item=%s)' % (repr(link._link_item)))
            else:
                out.append('link=iTLink(%s,%s)' % (repr(link.file_path), repr(link.target_path)))
            is_links_loaded = link.is_loaded
            out.append(', ')
        if self._flags or is_links_loaded:
            flags = self._flags
            if is_links_loaded:
                flags = flags | iTFLAG.LOAD_LINKS
            out.append('flags=%s' % (bin(flags)))
        if out[-1] == ', ':
            out = out[:-1]
        if out[-1] == ',':
            out = out[:-1]
        out.append(')')
        return ''.join(out)

    def __str__(self):
        """
        String repr of the item stripping the subtree to the first and last element only and giving ".." inbetween

        For full representation-string use `repr()`.

        :return: shorten representation string
        """
        out = ['%s('%self.__class__.__name__]
        if self._tag is not NoTag:
            out.append(repr(self._tag))
            out.append(', ')
        if self._value is not NoValue:
            out.append('value=')
            out.append(repr(self._value))
            out.append(', ')
        if len(self):
            if self.level > (sys.getrecursionlimit() / 5):
                out.append('subtree=[ ... ]')
            else:
                out.append('subtree=[')
                if len(self) <= 2:
                    for i in self:
                        out.append(str(i))
                        out.append(',')
                    out[-1] = ']'
                else:
                    out.append(str(self[0]))
                    out.append(',...,')
                    out.append(str(self[-1]))
                    out.append(']')
                out.append(', ')
        is_links_loaded = False
        if hasattr(self, '_link'):
            link = self._link
            if link._link_item is not None:
                out.append('link=iTLink(link_item=%s)' % (repr(link._link_item)))
            else:
                out.append('link=iTLink(%s,%s)' % (repr(link.file_path), repr(link.target_path)))
            is_links_loaded = link.is_loaded
            out.append(', ')
        if self._flags or is_links_loaded:
            flags = self._flags
            if is_links_loaded:
                flags = flags | iTFLAG.LOAD_LINKS
            out.append('flags=%s' % (bin(flags)))
        if out[-1] == ', ':
            out = out[:-1]
        if out[-1] == ',':
            out = out[:-1]
        out.append(')')
        return ''.join(out)

    def renders(self, filter_method=None, enumerate=None, renderer=iTreeRender):
        """
        render the iTree into a string

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches (see :ref:`filter_method <filter_method>`)

                            If `None` is given filtering is inactive.

                            The method uses the given filter always as an hierachical filter.

        :type enumerate: bool
        :param enumerate:
                            * True - Add an enumeration before the items
                            * False (default) - Output without enumeration

        :type renderer: class
        :param renderer: Give another renderer class for different formatting

        :rtype: str
        :return: Tree representation as string
        """
        render_obj = getattr(self, '__renderer', None)
        if render_obj is None or type(render_obj) != renderer:
            self.__renderer = render_obj = renderer()
        return render_obj.renders(self, filter_method, enumerate)

    def render(self, filter_method=None, enumerate=False, renderer=iTreeRender):
        """
        Print the rendered string of the `iTree`-object to the console (stdout).

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches.
                            If `None` is given filtering is inactive.

        :param enumerate:  add an enumeration before the rendered items

        :param renderer: Render to be used (The given render is stored and will be used until another renderer is given).

        :return:

        """
        print(
            self.renders(filter_method, enumerate, renderer=iTreeRender).encode(
                errors='replace').decode(
                'utf8')[:-1])

    # for pickle
    def __reduce__(self):
        return self.__class__, tuple(self.get_init_args())

    def get_init_args(self, filter_method=None, _subtree_not_none=True):
        """
        Method creates list of arguments that can be used as a pointer to create an equal instance of an iTree object.
        This is a method is used in most cases for internal functionalities (especially copy()).

        :type filter_method: Union[Callable,None]
        :param filter_method: filter method that checks for matching items
                            and delivers `True`/`False`.
                            The filter_method targets always the `iTree`-child-object and checks a characteristic
                            of this object for matches (see :ref:`filter_method <filter_method>`)

                            If `None` is given filtering is inactive.

        :param _subtree_not_none: internal parameter controlling if the subtree is added or not
        :return:
        """
        if _subtree_not_none and self:
            if self.is_link_root:
                if filter_method:
                    subtree = list(filter(filter_method, self._iter_locals_add_placeholders(self)))
                else:
                    subtree = list(self._iter_locals_add_placeholders(self))
            elif filter_method:
                subtree = list(filter(filter_method, self))
            else:
                subtree = list(self)
            if len(subtree) == 0:
                subtree = None
        else:
            subtree = None
        result = [self._tag, self._value, subtree]
        if self.is_link_root:
            result.append(iTLink(self._link.file_path, self._link.target_path))
        flags = self._flags
        if flags:
            if len(result) == 3:
                result.append(None)
            result.append(flags)
        return result

    # serialize + file operations

    def loads(self, data_str, check_hash=True, load_links=True,
              itree_serializer=iTStdJSONSerializer2):
        """
        create an iTree object by loading from a string

        If not overloaded or reinitialized the iTree Standard Serializer will be used. In this case we expect a
        matching JSON representation.

        :param data_str: source string that contains the iTree information

        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash

        :param load_links: True - linked iTree objects will be loaded

        :param itree_serializer: optional user defined serializer for iTree objects

        :return: iTree object loaded from file
        """
        serializer_obj = getattr(self, '__itree_serializer', None)
        if serializer_obj is None or type(serializer_obj) != itree_serializer:
            self.__itree_serializer = serializer_obj = itree_serializer(self.__class__)

        return serializer_obj.loads(data_str, check_hash=check_hash, load_links=load_links)

    def load(self, file_path, check_hash=True, load_links=True,
             itree_serializer=iTStdJSONSerializer2):
        """
        create an iTree object by loading from a file

        If not overloaded or reinitialized the iTree Standard Serializer will be used. In this case we expect a
        matching JSON representation.

        :param file_path: file path to the file that contains the iTree information

        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash

        :param load_links: True - linked iTree objects will be loaded

        :param itree_serializer: optional user defined serializer for iTree objects

        :return: iTree object loaded from file
        """
        serializer_obj = getattr(self, '__itree_serializer', None)
        if serializer_obj is None or type(serializer_obj) != itree_serializer:
            self.__itree_serializer = serializer_obj = itree_serializer(self.__class__)

        return serializer_obj.load(file_path, check_hash=check_hash, load_links=load_links)

    def dumps(self, calc_hash=False, filter_method=None,
              itree_serializer=iTStdJSONSerializer2):

        """
        serializes the iTree object to JSON (default serializer)

        :param calc_hash: Tell if the hash should be calculated and stored in the header of string

        :param itree_serializer: optional user defined serializer for iTree objects

        :return: serialized string (JSON in case of default serializer)
        """
        serializer_obj = getattr(self, '__itree_serializer', None)
        if serializer_obj is None or type(serializer_obj) != itree_serializer:
            self.__itree_serializer = serializer_obj = itree_serializer(self.__class__)
        return serializer_obj.dumps(self, calc_hash=calc_hash, filter_method=filter_method)

    def dump(self, target_path, pack=True, calc_hash=True, overwrite=False,
             filter_method=None,
             itree_serializer=iTStdJSONSerializer2):
        """
        serializes the iTree object to JSON (default serializer) and store it in a file

        :param target_path: target path of the file where the iTree should be stored in
        :param pack: True - data will be packed via gzip before storage
        :param calc_hash: True - create the hash information of iTree and store it in the header
        :param overwrite: True - overwrite an existing file

        :param itree_serializer: optional user defined serializer for iTree obbjects

        :return: True if file is stored successful
        """
        serializer_obj = getattr(self, '__itree_serializer', None)
        if serializer_obj is None or type(serializer_obj) != itree_serializer:
            self.__itree_serializer = serializer_obj = itree_serializer(self.__class__)
        return serializer_obj.dump(self,
                                   target_path,
                                   pack=pack,
                                   calc_hash=calc_hash,
                                   overwrite=overwrite,
                                   filter_method=filter_method)

    # *** link root related functions: *********************************************************************************
    # *** link related properties **************************************************************************************

    @property
    def is_placeholder(self):
        """
        Property shows that item is a placeholder class

        Normally there should be no placeholder class in the iTree but in case a loaded link does no more contain
        the expected items it might happen that such a class artifact is still in the tree.
        In placeholders the value contains the family index in the linked class.

        :rtype: bool
        :return: True/False
        """
        return bool(self._flags & self._PLACEHOLDER)

    @property
    def is_link_cover(self):
        """
        If the item is local and covers a linked item the property is True

        :rtype: bool
        :return: True/False

        """
        return hasattr(self, '_link') and self._link and (hasattr(self._link._link_item,'_itree_prt_idx'))

    @property
    def is_linked(self):
        """
        In contrast to iTreeLinked class this is False

        :rtype: bool
        :return: True/False

        """
        return bool(self._flags & self._LINKED)

    @property
    def is_link_loaded(self):
        if hasattr(self, '_link'):
            return self._link.is_loaded
        else:
            # we return False in case we have no link_roots inside the subtree
            return any(
                i.is_link_loaded for i in filter(self.__class__._filter_linked_roots, self.deep))

    @property
    def link_root(self):
        """
        delivers the highest level item that is linked
        in case item is not linked it delivers itself

        :rtype: iTree
        :return: highest level linked item found in the parents

        """
        if self.is_linked:
            parent = self._itree_prt_idx
            if (parent is not None) and parent[0].is_linked:
                return parent[0].link_root
            else:
                return self
        return None

    @property
    def is_link_root(self):
        """
        property that marks the iTree item as an item that contains a link

        :return:
                 * True - is a link root item
                 * False is no iTree link item
        """
        return bool(self._flags & self._LINK_ROOT)

    def load_links(self, force=False, delete_invalid_items=False, _items=None, _depth=0):
        """
        Runs ove all children and sub children in case a ITreeLink object is found the linked items are load in

        In case ´iTree´ is link root: load all linked items

        :param force:
                      * False (default) - load only if not already loaded
                      * True - load even if already loaded (update)

        :param delete_invalid_items:
                                     * False (default) - in case of invalid items we will raise an exception!
                                     * True - invalid items will be removed from parent no exception raised

        :param _items: internal list parameter used for recursive calls of the function

        :param _depth: Internal parameter related to current item depth
        :return:

                 * True - success
                 * False - load failed
        """
        if _depth > 200:
            raise RecursionError('Circular link definition couldnot integrate linked item '
                                 '%s' % (repr(self.tag_idx_path)))

        if self.is_link_root:
            load_ok = True
            load_item = None
            link_handler = self._link
            if link_handler is not None:
                if force:
                    load_active = True
                else:
                    # We try to detect if the original link was changed
                    load_active = False
                    if link_handler.is_loaded:
                        load_active = link_handler.is_file_updated()
                        if not load_active and link_handler.file_path is None:
                            # internal link check the source tree
                            try:
                                target_tree = link_handler.get_target_tree(self)
                                if len(target_tree) != len(link_handler._keys):
                                    raise Exception()
                                for key_old, key_new in zip(link_handler._keys,
                                                            target_tree.keys()):
                                    if key_old != key_new:
                                        raise ValueError()
                            except:
                                load_active = True
                    else:
                        load_active = True
                if load_active:
                    try:
                        load_item = link_handler.get_target_tree(self)
                    except:
                        if delete_invalid_items:
                            if self._itree_prt_idx is not None:
                                self._itree_prt_idx[0].remove(self)
                            return False
                        else:
                            raise
                    # keep the locals and coupled objects then clean all
                    sl = self._items
                    # now we take over the tree
                    local_items = OrderedDict()
                    for i in self._iter_locals_add_placeholders(self):
                        if i.is_placeholder:
                            local_items[(i._tag, i._value)] = i
                        else:
                            local_items[i.tag_idx] = i
                    old_coupled_objects = {i.tag_idx: i.coupled_object for i in self if
                                           i.is_linked and i.coupled_object}
                    sl.clear()
                    self._families = families = {}
                    linked_flag = self._LINKED
                    tags = set()
                    keys = []
                    append_item_to_tree = self._append_item
                    convert_to_linked_item = self._convert_to_linked_item
                    # load the linked items
                    for item in load_item:
                        if item.is_link_root:
                            try:
                                item.load_links(force=force, delete_invalid_items=delete_invalid_items,
                                                _depth=(_depth + 1))
                                new_item = item.copy()
                            except (TypeError, RecursionError):
                                raise RecursionError('Circular link definition couldnot integrate linked item '
                                                     '%s' % (repr(item.tag_idx_path)))
                            new_item._flags = new_item._flags | linked_flag
                        else:
                            new_item = convert_to_linked_item(item)
                        key = item.tag_idx
                        if key in old_coupled_objects:
                            new_item.set_coupled_object(old_coupled_objects[key])
                        keys.append(key)
                        tags.add(key[0])
                        # here we build the order of locals ("inheritance" of structure)
                        if key in local_items:
                            # append all locals before the match
                            append_list = []
                            for k, i in local_items.items():
                                if k == key:
                                    if i.is_placeholder:
                                        append_list.append((k, new_item))
                                    else:
                                        i._link = iTLink(link_item=new_item)
                                        append_list.append((k, i))
                                    break
                                elif k in load_item:
                                    append_list = []
                                elif not i.is_placeholder:
                                    # in case of placeholders the new linked tree is reordered
                                    # and we skip the old placeholders
                                    # the idea is to keep at least the order of the local items
                                    append_list.append((k, i))

                            # this does not work must investigate why
                            # sl.extend(
                            #    self._iter_extend(self, ((local_items.__delitem__(k ) or i) for k,i in append_list)))
                            for k, i in append_list:
                                del local_items[k]
                                append_item_to_tree(self, i)

                        else:
                            append_item_to_tree(self, new_item)

                    # append all other local_items
                    # we do not use _iter_extend() here to avoid copies
                    for i in filter(lambda i: not i.is_placeholder, local_items.values()):
                        append_item_to_tree(self, i)
                    link_handler.set_tags_and_keys(tags, keys)
                    link_handler.set_loaded(load_item.tag, load_item.value)
                    return True
                else:
                    return False
        else:
            loaded = False
            for i in filter(self.__class__._filter_linked_roots, self.deep):
                if i.load_links(force=force, delete_invalid_items=delete_invalid_items, _depth=(_depth + 1)):
                    loaded = True
            return loaded

    def make_local(self, copy_subtree=True):
        """
        make the current linked object a local object
        This is only possible if the parent is a iTree object is the link root->
        only the first level children in a linked iTree can be made local
        The operation raises an SyntaxError in case it is used on a deeper level of the linked tree

        :return: None
        """
        if self._itree_prt_idx is None or not self.is_linked:
            raise SyntaxError('Item is not linked or has no parent, invalid operation')
        parent = self._itree_prt_idx[0]
        if not parent.is_link_root:
            raise SyntaxError('local items can just be added to the root objects of links')
        local_item = self._convert_to_local_item(self, copy_subtree)
        abs_idx = self.idx
        tag, f_idx = self.tag_idx
        # replace old item in super list
        parent._items[abs_idx] = local_item
        # replace old item in family list
        parent._getitem_fam(tag)[f_idx] = local_item
        local_item._itree_prt_idx = [parent, abs_idx, f_idx]
        return local_item

    # *** unsupported methode (overload super() methods with exceptions ************************************************

    def __isub__(self, other):
        raise TypeError('Unsupported operand or function')

    def __imul__(self, other):
        raise TypeError('Unsupported operand or function')

    # *** helpers ******************************************************************************************************

    # property for debugging
    @property
    def _debug_children_list(self):
        """
        This is a property for debugging proposes only

        :return: list of children
        """
        return list(self)
