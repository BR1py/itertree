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


This part of code contains
helper classes used in DataTree object
"""

from __future__ import absolute_import

import abc
import time
import os
import zlib
import fnmatch
import operator
import itertools
from collections import namedtuple, deque

try:
    #raise ImportError
    # This really recommended for faster operations!
    from blist import blist
    itree_list=blist

    BLIST_SWITCH = 100  # break even from which size on blist should be used instead of normal list
    BLIST_ACTIVE = True


except ImportError:
    # if not available we take normal list
    itree_list = list
    BLIST_ACTIVE = False
    BLIST_SWITCH = -1  # never

try:
    import numpy as np
except ImportError:
    np = None



def accu_iterator(iterable, accu_method, initial_value=(None,)):
    """
    A method that enables itertools accumulation over a method
    .. note::  This method is just needed because in python <3.8 itertools accumulation has no initial parameter!
    :param iterable: iterable
    :param accu_method: accumulation method (will be fet by two parameters cumulated and new item)
    :return: accumulated iterator
    """
    for i in iterable:
        initial_value = accu_method(initial_value, i)
        yield initial_value


def is_iterator_empty(iterator):
    '''
    checks if the given iterator is empty

    :param iterator: iterator to be checked

    :rtype: tuple
    :return:
              *  (True, iterator) - empty
              *  (False, iterator) - item inside
    '''
    try:
        i = next(iterator)
    except StopIteration:
        return True, iterator
    return False, itertools.chain((i,), iterator)

def rindex(lst, value):
    '''
    find last occurance of a itme in the list
    :param lst: list
    :param value: search value
    :return:
    '''
    lst.reverse()
    i = lst.index(value)
    lst.reverse()
    return len(lst) - i - 1


class iTLink(object):
    '''
    Definition of a link to an element in another DataTree
    '''
    __slots__ = ("_file_path", "_target_path", '_loaded',
                 '_link_data', '_link_tag', '_link_item', '_source_path', '_file_crc', '_tags', '_keys')

    _linked_filter = lambda i: bool(i.is_link_root)

    def __init__(self, file_path=None, target_path=None, link_item=None):
        if file_path is None:
            self._file_path = file_path
        else:
            try:
                self._file_path =os.path.relpath(file_path)
            except:
                self._file_path = file_path
        self._target_path = target_path
        self._loaded = None
        self._link_tag = None
        self._link_data = None
        self._source_path = None
        self._link_item = link_item
        self._tags = set()
        self._keys = None
        self._file_crc = None

    def __eq__(self,other):
        if self._file_path != other._file_path:
            return False
        if self._target_path != other._target_path:
            return False
        if self._link_item != other._link_item:
            return False
        return True

    def get_init_args(self):
        if self._link_item is None:
            return (self._file_path, self._target_path)
        else:
            return (self._file_path, self._target_path, self._link_item)

    def get_target_tree(self, ABSOLUTE, source_dir=None):
        if self._file_path:
            if os.path.isabs(self._file_path) or not source_dir:
                file_path = self._file_path
            else:
                file_path = os.path.join(source_dir, self._file_path)
            if not os.path.exists(file_path):
                raise FileNotFoundError('Related source-file %s of the iTLink object not found!' % file_path)
            result_tree = ABSOLUTE.load(file_path, load_links=True)
            self._file_crc = self._get_file_crc(file_path)
        else:
            result_tree = ABSOLUTE.root
        if self._target_path:
            if type(self._target_path) is str:
                self._target_path=[self._target_path]
            if self._target_path[0]==result_tree.tag and Tag(self._target_path[0]) not in result_tree:
                self._target_path=self._target_path[1:]
            if self._target_path:
                result_tree = result_tree.get(*self._target_path)
        if hasattr(result_tree, '_itree_prt_idx'):
            return result_tree
        raise SyntaxError('No matching source_tree found')

    def is_file_updated(self, source_dir=None):
        if self._file_crc is None and self._file_path:
            return True
        else:
            if self._file_path:
                if os.path.isabs(self._file_path) or not source_dir:
                    file_path = self._file_path
                else:
                    file_path = os.path.join(source_dir, self._file_path)
                if not os.path.exists(file_path):
                    raise FileNotFoundError('Related source-file %s of the iTLink object not found!' % file_path)
                return self._file_crc == self._get_file_crc(file_path)
            else:
                return False

    def _get_file_crc(self, fpath):
        """With for loop and buffer."""
        crc = 0
        with open(fpath, 'rb', 65536) as ins:
            for x in range(int((os.stat(fpath).st_size / 65536)) + 1):
                crc = zlib.crc32(ins.read(65536), crc)
        return (crc & 0xFFFFFFFF)

    @property
    def loaded(self):
        return self._loaded

    @property
    def is_loaded(self):
        return self._loaded is not None

    @property
    def link_item(self):
        return self._link_item

    @property
    def file_path(self):
        return self._file_path

    @property
    def target_path(self):
        return self._target_path

    @property
    def link_tag(self):
        return self._link_tag

    @property
    def link_data(self):
        return self._link_data

    @property
    def source_path(self):
        return self._source_path

    def set_source_path(self, path):
        self._source_path = path

    def set_loaded(self, tag=None, data=None):
        self._loaded = time.time()
        self._link_tag = tag
        self._link_data = data

    @property
    def tags(self):
        return self._tags

    def set_tags_and_keys(self, tags, keys):
        self._keys = keys
        self._tags = tags

    @property
    def file_crc(self):
        return self._file_crc

    def get_args(self):
        return (self._file_path, self._target_path, self._link_item)

    def __repr__(self):
        if self._link_item is not None:
            return 'iTLink(file_path=%s, target_path=%s,link_item=%s)' % (
                repr(self._file_path), repr(self._target_path), repr(self._link_item),)

        return 'iTLink(file_path=%s, target_path=%s)' % (
            repr(self._file_path), repr(self._target_path),)

ORDER_PRE=1
ORDER_POST=0
ORDER_LEVEL=2

class iTFLAG():
    """
    public flags for setting the `iTree behavior during `__init__()`
    """
    READ_ONLY_TREE = 0b1
    READ_ONLY_VALUE = 0b10
    LOAD_LINKS = 0b100



class _iTFLAG():
    """
    internal used flags (must not be used by the user!)
    """
    LINKED = 0b1000
    PLACEHOLDER = 0b10000
    LINK_ROOT = 0b100000
    FLAG_MASK = 0b111111

INF=float('inf')
INF_PLUS=float('+inf')
INF_MINUS=float('-inf')

class Any(object):
    """
    Helper class used for marking that the ìTree()-object is "empty" no value is stored inside.

    If required use the class as it is, do not instance an object.
    """

    def __init__(self):
        raise SyntaxError('The object cannot be instanced')


class NoValue(object):
    """
    Helper class used for marking that the ìTree()-object is "empty" no value is stored inside.

    If required use the class as it is, do not instance an object.
    """

    def __init__(self):
        raise SyntaxError('The object cannot be instanced')



class NoTag(object):  # must be hashable!
    """
    Helper class used for the NoTag-family tag which is automatically used in case no explicit tag is
    given during creation of the ìTree()-object.

    If required use the class as it is, do not instance an object.
    """

    def __init__(self):
        raise SyntaxError('The object cannot be instanced')


class NoKey(object):  # must be hashable!

    """
    Helper class used for the NoKey entries in dicts stored as value object in the ìTree()-object.

    If required use the class as it is, do not instance an object.
    """

    def __init__(self):
        raise SyntaxError('The object cannot be instanced')

class NoTarget(object):  # must be hashable!

    """
    Helper class used for the NoKey entries in dicts stored as value object in the ìTree()-object.

    If required use the class as it is, do not instance an object.
    """

    def __init__(self):
        raise SyntaxError('The object cannot be instanced')

class ArgTuple(tuple):
    pass


class Tag():
    """
    Helper class used in get-methods for marking that the given value is a family-tag and not an index or key, etc.
    """

    __slots__ = ['tag']

    def __init__(self, tag=NoTag):
        self.tag = tag

    def __getitem__(self, key):
        return self.tag

    def __repr__(self):
        return 'Tag(%s)' % repr(self.tag)

    def __hash__(self):
        # We do not allow hashs of this object to avoid that it is used as tag of iTree objects
        raise TypeError("unhashable type: 'Tag'")


TagIdx = namedtuple('TagIdx',['tag','idx']) # For downward compatibility

def getter_to_list(get_result):
    """
    Helper function that always creates a list from a `iTree`get-method result.

        1. In case we have a iterator the list with the iterator items is created.
        2. In case we have a single item a list [single_item] is created
        3. In case we have no item or empty iterator an empty list is created.

    :param get_result: result coming from a getter method

    :rtype: list
    :return: result list
    """
    if hasattr(get_result, '_itree_prt_idx'):
        return [get_result]
    else:
        return list(get_result)

class ITER():
    """
    iter options for deep iterators
    """
    DOWN=0b1 #gives iteration direction top-> down (default)
    UP=DOWN <<1 # gives iteration direction bottom-> up
    # in case DOWN adn UP is in we use UP;
    # Both flags are just in because of downward compatibility
    REVERSE=UP<<1 # switches item iteration direction to high index -> low index
    SELF=REVERSE<<1 # include the calling object in the iteration (only if target matches)
    FILTER_ANY= SELF<<1 # Use build in filtering instead of hierarchical filtering (only in iter())
    MULTIPLE=FILTER_ANY<<1 # allows multiple matches of items in an iteration

    @staticmethod
    def get_option_str(option):
        """
        calculates a string representing the options used in given option
        :para option: integer containing the option-bits
        :return:
        """
        options=[]
        if option & ITER.DOWN:
            options.append('DOWN')
        if option&ITER.UP:
            options.append('UP')
        if option&ITER.REVERSE:
            options.append('REVERSE')
        if option&ITER.SELF:
            options.append('SELF')
        if option&ITER.FILTER_ANY:
            options.append('FILTER_ANY')
        if option & ITER.MULTIPLE:
            options.append('MULTIPLE')

        invalid=option&~(ITER.UP | ITER.REVERSE | ITER.SELF |ITER.FILTER_ANY |ITER.MULTIPLE)
        if invalid:
            options.append('%s'%bin(invalid))
        return ' | '.join(options)

    @staticmethod
    def valid_option(option,expected_option=DOWN |UP | REVERSE | SELF |FILTER_ANY  |MULTIPLE):
        """
        checks if given option is valid
        :para option: integer containing the options-bits
        :para expected_option: integer containing the full set of possible option-bits
        :return: None or string for exception containing the invalid flags used
        """
        invalid=option&(~expected_option)
        if invalid:
            return 'Invalid iteration option(s) given: %s'%ITER.get_option_str(invalid)
