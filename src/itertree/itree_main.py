'''
This file contains the main iTree object
'''
from __future__ import absolute_import
import os
import itertools
import copy
from multiprocessing import RLock
from .itree_data import iTData
from .itree_helpers import *
try:
    # This really recommended for faster operations!
    from blist import blist
    BLIST_SWITCH=100 # for list > BLIST_SWITCH we switch to blist objects for better performance
except:
    # if not available we take normal list
    blist=list
    BLIST_SWITCH=-1

list_creator=(0,) # helper for quick list instance

#class iTree(iTMagicList):
class iTree(blist):

    '''
    This is the main class related to iTrees.

    We give here a short functional summary:

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
    :param link: in case the node should be linked to another (external file/key) a iTLink() object can be given
    :param is_temp: If the iTree is marked as temporary the iTree will not be stored during dump into a file
    :param subtree: The subtree is a iterable structure that contains sub-items (iTree objects) that should be \
                    the children of this iTree.

                    .. warning:: subtree: In case the given iTree objects have already a parent an implicit copy will
                                          be made.
    '''


    __slots__ = (
        '_tag', '_parent', '_map', '_flags', '_coupled', '_link', '_data', '_cache', '_def_serializer')
        #'_length','_items','_is_list')
    def __init__(self, tag, data=None, link=None, is_temp=False, subtree=None):
        super(iTree, self).__init__()
        if type(tag) in {int, TagIdx}:
            raise TypeError('Given tag cannot be used in iTree wrong type (int or TagIdx)')
        self._tag = tag
        self._parent = None
        self._map = {}
        self._flags = N
        self._coupled = None
        self._def_serializer = None
        self._cache = [0,0]

        if link is None:
            self._link = None
        else:
            if not hasattr(link, 'is_iTLink'):
                raise AttributeError('Error given link is not of type iTLink')
            self._link = link
            self._flags = LINKED

        if is_temp:
            self._flags = self._flags | TEMPORARY

        if subtree is not None:
            self.extend(subtree)

        if not hasattr(data, 'is_iTData'):
            self._data = data = iTData(data_items=data)
        else:
            self._data = data

    # These are the mandatory methods we expect in the data object

    @property
    def set(self):
        '''
        set function for a data-attribute

        In case the standard iTData object is used we have:

        :param key: give key under which the data will be stored, in case data is None the first key parameter is taken
                    as data object and it is stored in the "__NOKEY__" item

        :param value: data value the object that should be stored in the data structure of this iTree

        :return  None
        '''
        parent=self._parent
        if (parent is not None) and parent.is_linked:
            raise PermissionError('Linked item cannot be manipulated')
        return self._data.set

    @property
    def get(self):
        '''
        get function for a data attribute

        In case the standard iTData object is used we have:

        :param key: key under which the data is stored, in case no key is given the "__NOKEY__" item will be returned

        :return: data attribute object
        '''
        parent=self._parent
        return self._data.get

    @property
    def check(self):
        '''
        check if the given data-item can be stored under the given key. The check make only sense in case there is
        a iTreeDataModel or matching object is already stored under the key

        :param value: data value the object that should be checked
        :param key: give key under which contains the DataModel, in case key is None the "__NOKEY__" item will be used

        :return: tuple (True/False,'check details')
        '''
        parent=self._parent
        if parent is not None and parent.is_linked:
            raise PermissionError('Linked item cannot be manipulated')
        return self._data.check

    @property
    def pop_data(self):
        '''
        data related pop (will delete the given key
        :return:
        '''
        parent=self._parent
        if parent is not None and parent._is_linked:
            raise PermissionError('Linked item cannot be manipulated')
        return self._data.pop

    @property
    def data(self):
        return self._data


    def init_serializer(self, force=False, exporter=None, importer=None, serializer=None, renderer=None):
        '''
        Method sets the exchange environment that should be used. If you leave the parameters as default,
        the standard objects will be used.

        HINT: The method logic is called only one time the first time serializing is needed.
              For standard serializer post import must be done against common python rules
              because pre import will lead into cyclic importing

        :param force: False (Default) - do not reload in case we have already loaded the items
        :param exporter: exporter object for file export of iTree (dump, dumps)
        :param importer: importer object in ces a file import is done (load, loads)
        :param serializer: Object serializer (especially needed for data objects!)
        :param renderer:  A renderer for pretty print output of the iTree object

        :return: None
        '''
        if self._def_serializer is None or force:
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
        '''
        put the item in the iTree for (re)setting a child

        HINT: A iTree child can only be child of one iTree (one parent only)
        HINT2: Linked items cannot be changed change the linked item and reload the tree!

        :param key: single identifier for the item can be integer index or TagIdx
        :param value: iTree object that should be child of called iTree

        :return: value
        '''
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        try:
            if value._parent is not None:
                try:
                    # e.g. for __iadd__ operation we may find exactly same item already in the tree
                    if id(value)== id(super(iTree, self).__getitem__(value.idx)):
                        # we must do nothing in that case
                        return value
                except:
                    pass
                raise RecursionError('Given item has already a parent iTree!')
        except AttributeError:
            if type(value) is not iTree:
                raise TypeError('In iTree only children of type iTree can be integrated')
            raise
        old_item = self.__getitem__(key)
        idx = old_item.idx
        o_tag = old_item._tag
        value._parent = self
        super(iTree, self).__setitem__(idx, value)
        v_tag = value._tag
        if v_tag == o_tag:
            family = self._map[v_tag]
            family.__setitem__(old_item.tag_idx[1], value)
        else:
            m=self._map
            m[old_item._tag].remove(old_item)
            try:
                family = m[v_tag]
                idx = self.__get_family_insertion_idx(family, value.idx)
                value._cache[1]=idx
                if len(family)==BLIST_SWITCH:
                    m[v_tag] = family = blist(family)
                family.insert(idx, value)
            except:
                m[v_tag]=[value]
        return value

    def __getitem__(self, key,str_index_separator='#'):
        '''
        Main getter for items

        If given key targets to only one item we will deliver an iTree. If no matching item is found an IndexError
        or KeyError exception will be raised.

        If the given key targets to multiple items (tag family, slice, itearble of single target keys) and iterator
        will be delivered.

        .. node:: If a tag is given a iterator of the tag family will be returned even if there is only one item
                  with the tag in the tree!!!

        :param key: single target: index, TagIdx or tuple (tag, index) (not recommended)
                    multi target: TagIdx_s; iMatch; slice or an iterable (like list) of these keys
        :return: iTree item or iterator (multi target)
        '''
        t = type(key)
        if t is int:
            return super(iTree, self).__getitem__(key)
        elif t is TagIdx:
            if key.is_single:
                return self._map[key[0]][key[1]]
            idxs = key[1]
            family = self._map[key[0]]
            t2 = type(idxs)
            if t2 is slice:
                return itertools.islice(family, idxs.start, idxs.stop, idxs.step)
            elif t2 is list or hasattr(idxs, '__next__'):
                return iter([family[k] for k in idxs])
            else:
                raise TypeError('TagIdx object contains invalid indexes')
        elif t is slice:
            # return an iterator over the slice
            return itertools.islice(super(iTree, self).__iter__(), key.start, key.stop, key.step)
        elif t is iTMatch:
            return filter(lambda item: key.check(item),super(iTree, self).__iter__())
        elif t is list or hasattr(key, '__next__'):
            # list or iterator HINT: We expect that the items are valid items like integer index or TagIdx items
            # -> return an iterator
            return iter([self[k] for k in key])
        else:

            # here we expect a tag only and we deliver the related iterator
            m=self._map
            try:
                # we return a family iterator here
                return iter(m[key])
            except KeyError:
                # less quick not recommended options:
                if t is str and str_index_separator in key:
                    return self[TagIdx(key,tag_separator=str_index_separator)]
                if t is tuple:
                    # we recheck here for tuples (tag,index)
                    # but it's recommended to use TagIdx objects instead
                    return m[key[0]][key[1]]
                raise KeyError

    def __delitem__(self, key):
        '''
        delete an item in the tree
        :param key: key targeting the item to be deleted
                    single target: iTree object (remove), index, TagIdx or tuple (tag, index) (not recommended)
                    multi target: TagIdx_s or an iterable (like list) of these keys or a slice
        :return:
        '''
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        t = type(key)
        m=self._map
        if t is int:
            del_item = super(iTree, self).pop(key)
            family = m[del_item._tag]
            if len(family) == 1:
                del m[del_item._tag]
            else:
                del family[del_item.tag_idx[1]]
            del_item._parent = None
            return del_item
        elif t is TagIdx:
            if key.is_single:
                family = m[key[0]]
                del_item = family.pop(key[1])
                if len(family) == 0:
                    del m[del_item._tag]
                # here we go for _delitem__ and not remove because we expect the item "knows" the correct index (cache)
                super(iTree, self).__delitem__(del_item.idx)
                del_item._parent = None
                return del_item
            else:
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
        elif hasattr(key, 'is_iTree'):
            # ToDo delete in the parent?
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
            except KeyError:
                # iterator or iterable given?
                if hasattr(key, '__next__') or hasattr(key, '__next__'):
                    # return an iterator over the slice
                    return_list = list(self[key])
                    for i in return_list:
                        super().__delitem__(i.idx)
                        tag_idx = i.tag_idx
                        family = m[tag_idx.tag]
                        del_item = family.pop(tag_idx.idx)
                        if len(family) == 0:
                            m.pop(tag_idx.tag)
                        del_item._parent = None
                    return iter(return_list)
                else:
                    # no valid key found!
                    raise KeyError('No related item (key = %s) found for deletion' % key)
            for item in family:
                super(iTree, self).remove(item)
            for i in family:
                i._parent = None
            return iter(family)

    def __mul__(self, factor):
        '''
        Multiplication function a iTree is multiplied (copies) and put in a new iTree:

        my_single_item=iTree('multi')
        multi=my_single_item*1000

        HINT: In this operation multiple copies of the original item generated.

        :param factor: integer to multiply with
        :return: iTree object containing multiplied children
        '''
        if type(factor) is int:
            return iTree(self._tag, data=self._data, subtree=[self.copy() for i in range(factor)])

    def __add__(self, other):
        '''
        If two iTree objects are added the children in the two added iTrees are copied and combined
        to a new iTree object the other attributes are taken over from the first iTree in the sum

        :param other: iTree object that should be added
        :return: New iTree object containing copies of all children
        '''
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        items=[i.copy() for i in super(iTree, self).__iter__()]
        for i in other:
            if hasattr(i, '_parent'):
                if i._parent is not None:
                    items.append(i.copy())
                    continue
            items.append(i)
        return iTree(self._tag, data=self._data, subtree=items)

    def __iadd__(self, other):
        '''
        This is the same operation as append (is a bit quicker)
        :param other: iTree object that should be added
        :return: None
        '''
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        try:
            if other._parent is not None:
                raise RecursionError('Given item has already a parent iTree!')
        except AttributeError:
            if type(other) is not iTree:
                raise TypeError('In iTree only children of type iTree can be integrated')
            raise
        # append item:
        other._parent = self
        cache=other._cache
        cache[0]=super(iTree, self).__len__()
        super(iTree, self).append(other)
        m=self._map
        try:
            family=m[other._tag]
            cache[1] =l=family.__len__()
            if l==BLIST_SWITCH:
                m[other._tag]=family=blist(family)
            family.append(other)
        except KeyError:
            # first time tag is used!
            cache[1] = 0
            m[other._tag] =[other]
        return self

    def __iter__(self, item_filter=ALL):
        '''
        standard iterator over all items in the iTree
        :param item_filter: ALL = default
        :return:
        '''
        return self.iter_children(item_filter=item_filter)

    def __contains__(self, item):
        '''
        checks if an iTree object is part of the iTree
        :param item: iTree object we searching for
        :return:
        '''
        if id(item._parent) == id(self):
            return True
        if item._parent is None:
            return False
        return self.__contains__(item._parent)

    def __eq__(self, other):
        '''
        A iTree object is always unique we test therefore just for matching object IDs
        This is needed for quick index findings!
        ..node:: To check if properties content is equal use equal() instead
        :param other: iTree object to compare with
        :return:
        '''
        return id(self)==id(other)

    def __ne__(self, other):
        '''
        A iTree object is always unique we test therefore just for object for not matching IDs
        This is needed for quick index findings!
        ..node:: To check if attribute content is equal use not equal() instead
        :param other: other item to be compared with
        :return: True/False
        '''
        if id(self) != id(other):
            return True
        return False

    def __lt__(self, other):
        '''
        less than is a size comparison (length are compared)
        :param other: iTree object self should be compared with
        :return: True/False
        '''
        return len(self) < len(other)

    def __le__(self, other):
        '''
        less than or equal is a size comparison (length are compared)
        :param other: iTree object self should be compared with
        :return: True/False
        '''
        return len(self) <= len(other)

    def __gt__(self, other):
        '''
        greater than is a size comparison (length are compared)
        :param other: iTree object self should be compared with
        :return: True/False
        '''
        return len(self) > len(other)

    def __ge__(self, other):
        '''
        greater than or equal is a size comparison (length are compared)
        :param other: iTree object self should be compared with
        :return: True/False
        '''
        return len(self) >= len(other)

    def __repr__(self):
        '''
        create representation string from which the object can be reconstructed via eval (might not work in case of
        data that do not have a working repr method)
        :return: represenation string
        '''
        repr_str = 'iTree("%s"' % (repr(self._tag))
        if not self._data.is_empty:
            if self._data.is_no_key_only:
                repr_str = repr_str + ', data=%s' % repr(self._data.get())
            else:
                repr_str = repr_str + ', data=%s' % repr(self._data)
        if self._flags & LINKED:
            repr_str = repr_str + ', link=%s' % repr(self._link)
        if self._flags & TEMPORARY:
            repr_str = repr_str + ', is_temp=True'
        if super(iTree,self).__len__() > 0 and not self._flags&LINKED:
            subtree=super(iTree, self).__repr__()
            if subtree[0]=='b':
                # we shorten blist from definition
                subtree=subtree[6:-1]
            return repr_str + ', subtree=%s)' % subtree
        else:
            return repr_str + ')'

    def __hash__(self):
        '''
        The hash operation is available but not a quick operation!
        ..node::: We do here not consider, parent and coupled item
        :return: integer hash
        '''
        return hash(((i for i in self.iter_children(N | T)), (self._tag, self._flags, self._link, self._data)))

    def __len__(self):
        return super(iTree,self).__len__()

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

    def sort(self,*arg,**kwargs):
        return self.__unsupport_op()

    # properties

    @property
    def is_iTree(self):
        '''
        This property is used to quick identify the iTree objects (much quicker than isinstance())
        :return: True
        '''
        return True

    @property
    def is_linked(self):
        '''
        Are the sub items of this item linked ones?
        :return: True/False
        '''
        return self._flags&LINKED

    @property
    def is_link_loaded(self):
        '''
        For linked iTree objects we deliver here the state of loading the links
        :return: True/False
        '''
        if self._flags&LINKED:
            return False
        else:
            return self._link.is_loaded

    @property
    def parent(self):
        '''
        property contains the parent item

        :return: iTree parent object (or None in case no parent exists)
        '''
        return self._parent

    @property
    def is_root(self):
        '''
        is this item a root item (no parent)

        :return: True/False
        '''
        return self._parent is None

    @property
    def root(self):
        '''
        property delivers the root item of the tree

        :return: iTree root item

        '''
        if self._parent is None:
            return self
        else:
            return self._parent.root

    @property
    def pre_item(self):
        '''
        delivers the pre item (predecessor) of this object
        :return: iTree predecessor or None (no match)
        '''
        idx = self.idx - 1
        if idx < 0:
            return None
        return super(iTree, self).__getitem__(idx)

    @property
    def post_item(self):
        '''
        delivers the post item (successor)
        :return: iTree successor or None (no match)
        '''
        idx = self.idx + 1
        if idx < super(iTree, self).__len__():
            return None
        return super(iTree, self).__getitem__(idx)


    @property
    def depth(self):
        '''
        delivers the distance (number of levels) to the root element of the tree

        :return: integer

        '''
        if self._parent is None:
            return 0
        else:
            return self._parent.depth + 1

    @property
    def idx_path(self):
        '''
        delivers the a list of indexes from the root to this item

        :return: list of index integers (here we do not deliver an iterator)
        '''
        if self._parent is None:
            return []
        else:
            return self._parent.idx_path + [self.idx]

    @property
    def tag_idx_path(self):
        '''
        delivers the a list of TagIdx objects from the root to this item

        :return: list of TagIdx (here we do not deliver an iterator)
        '''
        if self._parent is None:
            return []
        else:
            return self._parent.tag_idx_path + [self.tag_idx]


    @property
    def tag_idx(self):
        '''
        Get the TagIdx object related to this object
        (contains the tag and the index of the object in the tag-family)
        :return: TagIdx
        '''
        parent = self.parent
        if parent is None:
            return None
        # we use cached index to be quicker
        cache=self._cahce
        c_idx = cache[1]
        family=parent._map[self._tag]
        try:
            if family[c_idx] is self:
                return TagIdx(self._tag,c_idx)
        except IndexError:
            pass
        # we search nearby
        try:
            i=family.index(self,(c_idx-10),(c_idx+10))
            if i != -1:
                cache[1]=idx=i
                return TagIdx(self._tag, idx)
        except (ValueError,IndexError):
            pass
        # full search cached index must be updated
        cache[1] = idx = parent._map[self._tag].index(self)
        return TagIdx(self._tag, idx)

    @property
    def tag(self):
        '''
        This objects tag
        :return: tag object
        '''
        return self._tag

    @property
    def idx(self):
        '''
        Index of this object in the iTree
        :return: integer index
        '''
        parent = self._parent
        if parent is None:
            return None
        # we use cached index to be quicker
        cache=self._cache
        order=super(iTree,parent)
        c_idx = cache[0]
        try:
            if order.__getitem__(c_idx) is self:
                return c_idx
        except IndexError:
            pass
        # we search nearby
        try:
            i=order.index(self,(c_idx-10),(c_idx+10))
            if i != -1:
               cache[0]=idx=i
               return idx
        except (ValueError,IndexError):
            pass
        # cached index must be updated
        cache[0] = idx = order.index(self)
        return idx

    @property
    def is_temporary(self):
        '''
        The iTree object can be marked as temporary (this means it will not be stored in a file if exported)
        This properties checks if the item is temporary
        :return: True/False
        '''
        return self._flags & T

    @property
    def coupled_obj(self):
        '''
        The iTree object can be couple with another python object. The pointer to the object is stored and can be
        reached via this property. (E.g. this can be helpful when connecting the iTree with a visual grafical element
        (treelist item) in a GUI)
        :return:
        '''
        return self._coupled


    # set properties

    def set_temporary(self):
        parent=self._parent
        if parent is not None and parent._is_linked:
            raise PermissionError('Linked item cannot be manipulated')
        if not self._flags & TEMPORARY:
            self._flags = self._flags | TEMPORARY  #

    def unset_temporary(self):
        parent=self._parent
        if parent is not None and parent._is_linked:
            raise PermissionError('Linked item cannot be manipulated')
        if self._flags & TEMPORARY:
            self._flags = self._flags & ~ TEMPORARY

    def set_couple_object(self, couple_object):
        '''
        User can couple this object with others with the help of this attribute
        HINT: E.g. this might be an object in a GUI that are related to this item
        :param couple_object:
        :return:
        '''
        self._coupled = couple_object

    def equal(self, other, check_parent=False, check_coupled=False):
        '''
        compares if the data content of another item matches with this item
        :param other: other iTree
        :param check_coupled: check the couple object too? (Default False)
        :return: boolean match result (True match/False no match)
        '''
        if self == other:
            return True
        if type(other) is not iTree:
            return False
        if check_parent:
            if other._parent != self._parent:
                return False
        my_data = (self._tag, self._flags, super(iTree, self).__len__(), len(self._map), self._link)
        other_data = (other._tag, other._flags, super(iTree,other).__len__(), len(other._map), other._link)
        if my_data != other_data:
            return False
        for si, oi in zip(other.iter_children(ALL), self.iter_children(ALL)):
            if not si.equal(oi):
                return False
        if check_coupled:
            if self._coupled != other._coupled:
                return False
        return True

    def copy(self, copy_data=COPY_NORMAL):
        '''
        create a copy of this item

        The function is used internally in extend operations too. And we can see (profiler) that
        improvements in this method might have big impact.

        :param copy_data: Type of copy
                          COPY_OFF - keep the data uncopied
                          COPY_NORMAL - (default) copy the data too
                          COPY_DEEP - do a deepcopy()
        :return:
        '''
        data = self._data.copy(copy_data)
        if self.is_linked:
            new = iTree(self._tag,
                        data=data,
                        link=self._link,
                        is_temp=(self._flags & T)
                        )
            if self.is_link_loaded:
                new.load_links()
        else:
            new = iTree(self._tag,
                        data=data,
                        is_temp=(self._flags & T),
                        subtree=self.iter_children() # here we create a recursion!
                        )
        return new

    def count(self, item_filter=ALL):
        '''
        count the number of children that match to the given filter
        ::Note: The operation is not very quick on huge iTrees and complicate filters!
        :param item_filter:
        :return: integer number of children matching to the filter
        '''
        if item_filter == ALL:
            return len(super())
        if type(item_filter) is int:
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)
        return len(list(filter(item_filter, super(iTree, self).__iter__())))

    # structure manipulations

    def clear(self):
        '''
        deletes all children
        and data!
        flags stay unchanged!
        :return: None
        '''
        self._data = None
        self._coupled = None
        if self._flags & LINKED:
            # we clear only data not the tree!
            return
        super().clear()
        self._map = {}

    def insert(self, insert_key, item):
        '''
        Insert an item before a specific position

        :param insert_key: position key (integer index or TagIdx)
        :param value: item that should be inserted in the tree (new child)
        :return: None
        '''
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        if type(item) is not iTree:
            raise TypeError('In iTree only children of type iTree can be integrated')
        if item.parent is not None:
            raise RecursionError('Given item has already a parent iTree!')
        t = type(insert_key)
        if type(insert_key) is int:
            idx = insert_key
            if idx < 0:
                idx = super(iTree, self).__len__() - idx
        elif type(insert_key) is TagIdx:
            idx = self.__getitem__(insert_key).idx
        else:
            raise TypeError('In iTree only children of type iTree can be integrated')
        super(iTree, self).insert(idx, item)
        tag = item._tag
        m=self._map
        cache=item._cache
        try:
            family = m[tag]
            l=family.__len__()
            cache[1] = l
            if l==BLIST_SWITCH:
                m[tag]=family=blist(family)
        except:
            m[tag] = family = [item]
            cache[1] = 0
        else:
            idx = self.__get_family_insertion_idx(family, idx)
            family.insert(idx, item)
            cache[1]= idx
        item._parent = self

    def append(self, item):
        '''
        Append the given iTree object to the tree (new last child)

        :except: raise TypeError in case iTree object has already a parent

        :param item: iTree object to be appended

        :return: None
        '''
        return self.__iadd__(item)

    def appendleft(self, item):
        '''
        Append the given iTree object to the left of the the tree (new first child)

        :except: raise TypeError in case iTree object has already a parent

        :param item: iTree object to be appended

        :return: None
        '''
        return self.insert(0,item)

    def extend(self, extend_items):
        '''
        We extend the iTree with given items (multi append)

        :note: In case the extend items have already a parent an implicit copy will be made. We do this because
               we might get an iTree-object as extend_items parameter and then the children will have automatically a
               parent even that the parent object might be a temporary one.

        :param extend_items: iterable object that contains iTree objects as items
        :return: None
        '''
        # collect for operation
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        sl=super(iTree, self)
        m=self._map
        for item in extend_items:
            if item._parent is not None:
                item = item.copy()
            item._parent = self
            cache = item._cache
            cache[0]=sl.__len__()
            sl.append(item)
            tag=item.tag
            try:
                family = m[tag]
                cache[1] = l = family.__len__()
                if l == BLIST_SWITCH:
                    m[tag] = family = blist(family)
                family.append(item)
            except KeyError:
                cache[1] = 0
                m[item._tag] = [item]
        return True

    def extendleft(self, extend_items):
        '''
        We extend the iTree with given items in the beginning (multi appendleft)

        :note: In case the extend items have already a parent an implicit copy will be made. We do this because
               we might get an iTree-object as extend_items parameter and then the children will have automatically a
               parent even that the parent object might be a temporary one.

        :note: The extendleft() operation is a lot slower then the normal extend operation

        :param extend_items: iterable object that contains iTree objects as items
        :return: None
        '''
        # start_idx=len(extend_items)-1
        # collect for operation
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        sl=super(iTree, self)
        m=self._map
        l=len(extend_items)
        for i in range(l):
            item=extend_items[l-i-1]
            if item._parent is not None:
                item = item.copy()
            item._parent = self
            item._cache=[0,0]
            sl.insert(0,item)
            tag=item._tag
            try:
                family = m[tag]
                l = family.__len__()
                if l == BLIST_SWITCH:
                    m[tag] = family = blist(family)
                family.insert(0,item)
            except KeyError:
                m[tag] = [item]
        return True

    def pop(self, key=-1):
        '''
        pop the item out of the tree, if no key is given the last item will be popped out

        :param key: specific identification key for an item (integer index, TagIdx)

        :return: popped out item (parent will be set to None)
        '''
        return self.__delitem__(key)

    def popleft(self):
        '''
        pop the first item out of the tree

        :return: popped out item (parent will be set to None)
        '''
        return self.__delitem__(0)

    def remove(self, item):
        '''
        remove the given item out of the tree (delete the child)

        :param item: iTree object that should be removed from the tree

        :return: removed item will be returned (parent is set to None)
        '''
        return self.__delitem__(item.idx)

    def move(self, insert_key):
        '''
        move the item in another position

        :param insert_key: item will be insert before this key

        :return: None
        '''
        if self._parent is None:
            raise LookupError('Given item is not a children of a iTree!')
        parent = self._parent
        # check if target exists:
        if type(insert_key) is not int:
            target_idx = parent.__getitem__(insert_key).idx
        else:
            target_idx = parent.__getitem__(insert_key).idx
            target_idx = insert_key
        src_idx = self.idx
        move_item = parent.__delitem__(src_idx)
        if target_idx > src_idx:
            target_idx -= 1
        parent.insert(target_idx, move_item)

    def rename(self, new_tag):
        '''
        give the item a new tag

        :param new_tag: new tag object string or hashable object

        :return: None
        '''
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        if type(new_tag) in {int, TagIdx}:
            raise TypeError('Given tag cannot be used in iTree wrong type (int or TagIdx)')
        parent = self.parent
        if parent is None:
            self._tag = new_tag
            return
        family = parent._map[self._tag]
        family.remove(self)
        if len(family) == 0:
            del parent._map[self._tag]
        self._tag = new_tag
        pm=parent._map
        try:
            new_family = pm[new_tag]
            if len(new_family)==BLIST_SWITCH:
                pm[new_tag]=new_family=blist(new_family)
        except:
            pm[new_tag] = [self]
        else:
            idx = self.__get_family_insertion_idx(new_family, self.idx)
            new_family.insert(idx, self)

    def reverse(self):
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        super(iTree, self).reverse()
        for item in self._map.values():
            item.reverse()

    def rotate(self, n):
        '''
        rotate the whole iTree n times
        (rotate means move last element to first position, ...)
        :param n:
        :return:
        '''
        if self._flags & LINKED:
            raise PermissionError('In linked iTrees we cannot change the structure')
        if n > 0:
            for i in range(n):
                rot_item = self.pop()
                self.insert(0, rot_item)
        elif n < 0:
            for i in range(n):
                rot_item = self.popleft()
                self += rot_item

    # iterators

    def iter_all(self, item_filter=ALL, top_down=True,filter_or=True):
        '''
        main iterator for whole tree runs in top-> down order

        :param item_filter: filter for filter the items you can give a filter constant or
                            a method for filtering (should return True/False)
        :param match: match pattern a iTMatch object
        :param top_down: True -  we start from parent to children
                          parent; child1; subchild1_1; subchild1_2; child2; subchild2_1
                         False - we start from children to parent
                          subchild1_1; subchild1_2; child1; subchild2_1;  child2; parent
        :param filter_or: True - we combine the filtering with or this means even if we have no match in the higher
                                 levels of the tree we will go deepere to find matches
                          False - filters are combined with and which means children will only be parsed in
                                  case the parent matches also to the filter condition
        :return: iterator
        '''
        if type(item_filter) is int:
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)

        if top_down:
            if filter_or:
                for item in self.iter_children(item_filter=ALL):
                    if item_filter(item):
                        yield item
                    for subitem in item.iter_all(item_filter=item_filter, top_down=top_down, filter_or=filter_or):
                        yield subitem
            else:
                for item in self.iter_children(item_filter=item_filter):
                    yield item
                    for subitem in item.iter_all(item_filter=item_filter,top_down=top_down,filter_or=filter_or):
                        yield subitem
        else:
            if filter_or:
                for item in self.iter_children(item_filter=ALL):
                    for subitem in item.iter_all(item_filter=item_filter, top_down=top_down, filter_or=filter_or):
                        yield subitem
                    if item_filter(item):
                        yield item
            else:
                for item in self.iter_children(item_filter=item_filter):
                    for subitem in item.iter_all(item_filter=item_filter,top_down=top_down,filter_or=filter_or):
                        yield subitem
                    yield item

    def iter_children(self, item_filter=ALL):
        '''
        main iterator in children level
        :param item_filter: the items can be filtered by giving a filter constants or giving a filter method
        :return: iterator
        '''
        if type(item_filter) is int:
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)
        return filter(item_filter, super(iTree, self).__iter__())

    def iter_tag_idxs(self, item_filter=ALL, top_down=True):
        tag_cnts = {}
        for item in iter(item_filter=item_filter, top_down=top_down):
            tag = item._tag
            try:
                cnt = tag_cnts[tag] + 1
                tag_cnts[tag] = cnt
                yield TagIdx(tag, cnt)
            except KeyError:
                tag_cnts[tag] = 0
                yield TagIdx(tag, 0)

    def find_all(self, key_path, item_filter=ALL, str_path_separator='/', str_index_separator='#',
                 _initial=True):
        '''
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
        :param default_return: object will be return in case of no match (default = None)
        :param path_separator: separator character in case of strings for the search levels (default: "/")
        :param index_separator: separator character for given tag indexes (default: "#")
        :param force_list: False (default) - function delivers sometimes iterators
                           True - function delivers always lists no iterators (can be much slower)
        :param _initial: Internal flag that should protect against cyclic constructs
        :return: list or iterator of matching iTrees; in case of no match and empty list is returned
        '''
        if item_filter is None:
            item_filter = lambda item: ((item._flags & ~ALL) == 0)
        if type(item_filter) is int:
            # create a filter method
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)

        t = type(key_path)
        if t is str:
            # empty key?
            l = len(key_path)
            if l == 0:
                # empty string
                return []
            # is string matching to a tag?
            try:
                items=self.__getitem__(key_path,str_index_separator=str_index_separator)
                return self.__build_find_all_result(items,
                                             item_filter=item_filter)
            except (KeyError,IndexError,ValueError):
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
                return self.root.find_all(key_list[1:],item_filter, str_path_separator, str_index_separator)
            return self.find_all(key_list, item_filter, str_path_separator, str_index_separator)
        # first we check we have a valid tag:
        if (not _initial) or (t in {int,str,TagIdx,iTMatch,slice}):
            # if not _initial we are in deeper level of the iterator and we interpret here as an index list!
            items=self[key_path]
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
            new_key_path = itertools.chain([post_item], sub_iter)
            try:
                post_post_item = next(sub_iter)
                # create a new iterator that contains the post items and the original iterator
                new_key_path = itertools.chain([post_item, post_post_item], sub_iter)
                set_initial=True
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
            return self.root.find_all(new_key_path,
                                      item_filter,
                                      str_path_separator,
                                      str_index_separator, _initial=set_initial)
        elif key=='*':
            result=self.iter_children(item_filter=item_filter)
        elif key=='**':
            result = self.iter_all(item_filter=item_filter)
        else:
            result = self.find_all(key, item_filter,
                               str_path_separator,
                               str_index_separator, _initial=False)
        # result can only be a single item
        if new_key_path is None or result == []:
            # we will not go deeper
            return result
        # iter into the next level
        results = [item.find_all(new_key_path,
                                 item_filter,
                                 str_path_separator,
                                 str_index_separator,
                                 _initial=set_initial) for item in result]
        return itertools.chain(*results)

    def find(self, key_path, item_filter=ALL, default_return=None, str_path_separator='/',
             str_index_separator='#'):
        '''
        The find function targets over multiple levels of the datatree, it returns single items only! This means in
        case the key_path targets to multiple items the default_return will be given. If the key_path targets to a
        family with only one item inside  or the item_filter extracts only one item in a family
        the item will be given back as result. For multiple result utilize the find_all() method (which is slower).
        HINT: The method will deliver a default_return when ever in the whole key_path a match is not unique.
              This means iteration is stopped here and even that a deeper iteration with the defined filtering might
              deliver at least a unique result. To ensure to find this deeper results you must utilize the slower
              find_all() method.

        The key_path parameter given is normally a list. This can be a list of keys or TagIdx objects. The function
        will search for the first item in the first level, fo next item in the next level and so on...

        Absolut and relative key_paths:

        If the first item is the separator (default: '/') the find search is like an absolute path and we start at the
        root of the datatree. For compatibility reasons with find_all we accept  a leading "./"
        (or to be exact: ".%s"#str_path_separator) as absolute path indicator.
        If the first item is different, the key_path is relative and we start from the actual
        item and search the children and sub-children.

        Single string key_path:
        If the user searches for string type tags he can use a string with a separator (default: '/') in between the
        tags (Those key_paths will be implicit translated in a list). An index separator (default = '#') in between
        the tag and the index can also be used in this case. If the argument is already a list the single keys will not
        be parsed regarding the str_path_separator.

        HINT: If datatree contains tags with characters that used for separators or the all match '*' character
              the find() result might contain that tagged item instead of the expected separated or wildcard match.

        HINT: Quickest find operations can be performed by giving a list containing index integers or TagIdx objects

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
        :param path_separator: separator character in case of strings for the search levels (default: "/")
        :param index_separator: separator character for given tag indexes (default: "#")
        :param _initial: Internal flag that should protect against cyclic constructs
        :return: iTree single item
        '''
        # internally we use the find_all() to get a list of items
        # and than return single match or default_return depending on result items

        result = self.find_all(key_path, item_filter=item_filter,
                               str_path_separator=str_path_separator,
                               str_index_separator=str_index_separator)
        # here we check if the iterator contains a unique item:
        item_iter = iter(result)
        try:
            item = next(item_iter)
        except StopIteration:
            # empty iterator!
            return default_return
        try:
            post_item = next(item_iter)
            # no StopIteration Exception! more then one element we return no match
            return default_return
        except StopIteration:
            # match!
            return item

    def index(self, item, item_filter=ALL):
        '''
        The index method allows to search for the index of the item in a parent object
        This is especially useful if you must use a item_filter. The delivered index is delivered relative
        to the given item filter!

        For the item index of the item in the unfiltered tree (ALL) it's recommended
        to use the idx property instead: (parent.index(item,ALL) == item.idx)

        :param item: item index should be delivered for
        :param item_filter: filter integer; method can not handle filter methods yet!
        :return: index integer of the item relative to the given filter
        '''
        if type(item) in {int, TagIdx}:
            item = self.__getitem__(item)
        if not item.parent is self:
            raise LookupError('Given item is not children of this iTree!')
        if item_filter == ALL:
            return super().index(item)
        elif item_filter == LINKED:
            if self._flags & LINKED:
                return super().index(item)
            else:
                raise LookupError('Given item is not found in this iTree!')
        else:
            for i, sibling in self.iter_children(item_filter=item_filter):
                if sibling == item:
                    return i

    # predefined filter queries

    def create_data_key_filter(self,  data_key='__NOKEY__',item_filter=ALL):
        '''
        create a item_filter method regarding a specific data key
        :param data_key: key that should be filtered out - if no key is given the no key item will be filtered
        :param item_filter: pre filtering method or integer with filter constant
        :return: specific item filter method that delivers True/False when item is given
        '''
        if type(item_filter) is int:
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)
        return lambda item: (item_filter(item) and (data_key in item.data))

    def create_data_key_match_filter(self,  match_pattern=None,item_filter=ALL,):
        '''
        create a item_filter method searching for a specific data content
        :param match_pattern: checks if a data key matches to the given pattern
                             (fnmatch() is internally used for the checks)
                             (non str, byte values will be taken as not matching)
        :param item_filter: pre filtering method or integer with filter constant
        :return: specific item filter method
        '''
        if type(item_filter) is int:
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)
        return lambda item: (item_filter(item) and (True in
                                    {((type(v) in {str,bytes})
                                           and (fnmatch.fnmatch(v,match_pattern)) or False) for v in item.data.keys()}))

    def create_data_value_filter(self, data_value=None, item_filter=ALL):
        '''
        create a item_filter method searching for a specific data content
        :param data_value: data content the method will search for
        :param item_filter: pre filtering method or integer with filter constant
        :return: specific item filter method
        '''
        if type(item_filter) is int:
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)
        return lambda item: (item_filter(item) and (True in {v == data_value for v in item.data.values()}))

    def create_data_value_match_filter(self, match_pattern=None, item_filter=ALL):
        '''
        create a item_filter method searching for a specific data content
        :param match_pattern: checks if a data value matches to the given pattern
                             (fnmatch() is internally used for the checks)
                             (non str, byte values will be taken as not matching)
        :param item_filter: pre filtering method or integer with filter constant
        :return: specific item filter method
        '''
        if type(item_filter) is int:
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)
        return lambda item: (item_filter(item) and (True in
                                    {((type(v) in {str,bytes})
                                           and (fnmatch.fnmatch(v,match_pattern)) or False) for v in item.data.values()}))


    def create_item_match_filter(self, match, item_filter=ALL):
        '''
        create a item_filter method searching for a specific data content
        :param match: iTMatch object or any match object with a check function for iTree objects
        :param item_filter: pre filtering method or integer with filter constant
        :return: specific item filter method
        '''
        if type(item_filter) is int:
            i = item_filter
            item_filter = lambda item: ((item._flags & ~i) == 0)
        return lambda item: (item_filter(item) and match.check(item))

    # serialize + file operations

    def load_links(self, force=False):
        '''
        load all linked items
        :param force: False (default) - load only if not already loaded
                      True - load even if already loaded (update)
        :return: True - success
                 False - load failed
        '''
        load_ok = False
        if self._link is not None:
            if force or  not self.is_link_loaded:
                if not os.path.exists(self._link.file_path):
                    raise FileNotFoundError('Source file of the link not found!')
                full_tree = self.load(self._link.file_path, load_links=True)
                if self._link.key_path is None:
                    load_item = full_tree
                else:
                    load_item = full_tree.find(self._link.key_path)
                    if type(load_item) is not iTree:
                        raise FileNotFoundError('Given key_path is not matching or unique!')
                # now we take over the tree
                super(iTree, self).clear()
                # here we run a special extend (we don't care about parents and is_linked flag)
                sl = super(iTree, self)
                m = self._map
                for item in load_item:
                    item._parent = self
                    cache = item._cache
                    cache[0] = sl.__len__()
                    sl.append(item)
                    tag = item.tag
                    try:
                        family = m[tag]
                        cache[1] = l = family.__len__()
                        if l == BLIST_SWITCH:
                            m[tag] = family = blist(family)
                        family.append(item)
                    except KeyError:
                        cache[1] = 0
                        m[item._tag] = [item]
                    item._flags = item._flags | LINKED
                    item.load_links(force=force)
                self._map = load_item._map
                self._link.set_loaded(load_item.tag,load_item.data)
                self._flags=self._flags|LINKED
                load_ok = True
        else:
            linked_flag = 0
            if self._parent is not None and self._parent.is_linked:
                linked_flag=LINKED

            for i in self.iter_children():
                load_ok = load_ok or i.load_links(force=force)
                i._flags=i._flags|linked_flag
        return load_ok

    def loads(self, data_str, check_hash=True, load_links=True):
        '''
        create an iTree object by loading from a string

        If not overloaded or reinitialized the iTree Standard Serializer will be used. In this case we expect a
        matching JSON representation.

        :param data_str: source string that contains the iTree information
        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash
        :param load_links: True - linked iTree objects will be loaded
        :return: iTree object loaded from file
        '''
        if self._def_serializer is None:
            self.init_serializer()
        return self._def_serializer[1].loads(data_str, check_hash=check_hash, load_links=load_links)

    def load(self, file_path, check_hash=True, load_links=True):
        '''
        create an iTree object by loading from a file

        If not overloaded or reinitialized the iTree Standard Serializer will be used. In this case we expect a
        matching JSON representation.

        :param file_path: file path to the file that contains the iTree information
        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash
        :param load_links: True - linked iTree objects will be loaded
        :return: iTree object loaded from file
        '''
        if self._def_serializer is None:
            self.init_serializer()
        return self._def_serializer[1].load(file_path, check_hash=check_hash, load_links=load_links)

    def dumps(self):
        if self._def_serializer is None:
            self.init_serializer()
        return self._def_serializer[0].dumps(self)

    def dump(self, target_path, pack=True, overwrite=False):
        if self._def_serializer is None:
            self.init_serializer()
        return self._def_serializer[0].dump(self, target_path, pack=pack, overwrite=overwrite)

    def renders(self):
        if self._def_serializer is None:
            self.init_serializer()
        return self._def_serializer[3].renders(self)

    def render(self):
        if self._def_serializer is None:
            self.init_serializer()
        return self._def_serializer[3].render(self)

    # helpers
    def __iter_to_match(self, iterator, match_key):
        for i in iterator:
            if i.parent.tag_index(i) == match_key:
                break
            yield i

    def __get_family_insertion_idx(self, family, item_idx, last_index=0):
        l = len(family)
        if l == 1:
            if family[0].idx < item_idx:
                return 1 + last_index
            else:
                return last_index
        i = round(l / 2)
        idx = family[i].idx
        if idx < item_idx:
            return self.__get_family_insertion_idx(family[i:], item_idx, last_index + i)
        else:
            return self.__get_family_insertion_idx(family[:i], item_idx, last_index)

    def __unsupport_op(self, *args, **kargs):
        raise TypeError('unsupported operand or function in iTree')

    # find helper methods for differenet types of keys

    def __build_find_all_result(self, result, item_filter=None):
        '''
        helper function for find method
        :param result: result found by the key
        :param default_result: flag
        :param item_filter: filter
        :return: final result
        '''
        if type(result) is iTree:
            if item_filter is None:
                return [result]
            elif item_filter(result):
                return [result]
            else:
                return []
        if result == []:
            return result
        return filter(lambda item: item_filter(item), result)

    def __find_single_item(self, key_path, item_filter=ALL):
        '''
        find normal item via __getitem__ in the children
        :param key_path: key
        :param item_filter: filter method
        :return: list with one item
        '''
        try:
            item = self.__getitem__(key_path)
        except (KeyError, IndexError):
            return []
        return self.__build_find_all_result(item, item_filter)

    def __find_tag_slice(self, tag_slice, item_filter=ALL):
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

    def __find_slice(self, slice_obj, item_filter=ALL):
        return itertools.islice(self.iter_children(item_filter=item_filter), slice_obj.start, slice_obj.stop,
                                slice_obj.step)

    def __find_set(self, set_obj, item_filter=ALL):
        return filter(lambda item: item.idx in set_obj, self.iter_children(item_filter=item_filter))

    def __find_match(self, match, item_filter=ALL):
        return filter(lambda item: match.check(item)[0], self.iter_children(item_filter=item_filter))

