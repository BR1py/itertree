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
the integration tests related to the base iTree functionalities
"""

import os
import timeit
import copy
import shutil
# import sys
import collections
# import timeit
import pytest

try:
    import numpy as np
except Exception:
    np = None

import pickle
import timeit
from types import GeneratorType
from collections import OrderedDict
from itertree import *
from itertree.itree_helpers import itree_list, BLIST_ACTIVE

if BLIST_ACTIVE:
    from blist import blist

root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

TEST_SELECTION = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
# TEST_SELECTION={}

print('Test start: itertree  base test 1')
if BLIST_ACTIVE: print('blist module imported for the test')

def get_relpath_to_root(item_path):
    new_path = item_path.replace(root_path, '')
    if new_path.startswith('\\'):
        new_path = new_path[1:]
    if new_path.startswith('/'):
        new_path = new_path[1:]
    return root_path + '/' + new_path


def calc_timeit(check_method, number):
    min_time = float('inf')
    for i in range(number):
        t = timeit.timeit(check_method, number=1)
        if t < min_time:
            min_time = t
    return min_time


class Test1_iTreeInstance:

    def large_itree(self, number_per_level, tags=[], counter_var=None, _root=None, _count=0):
        counters = []
        for tag in tags:
            if tag == counter_var:
                counters.append(0)

            elif type(tag) is tuple:
                sub_counters = []
                for i, t in enumerate(tag):
                    if t == counter_var:
                        sub_counters.append(i)
                counters.append(sub_counters)
            elif type(tag) is str and '%i' in tag:
                counters.append(1)
            else:
                counters.append(None)
        if _root is None:
            root = iTree('root')
        else:
            root = _root
        cnt = _count
        level = len(number_per_level) - 1
        for i in range(number_per_level[0]):
            for update, tag in zip(counters, tags):
                if update == 0:
                    cnt += 1
                    sub_item = iTree(i, cnt)
                elif update == 1:
                    cnt += 1
                    sub_item = iTree(tag % i, cnt)
                elif update is None:
                    cnt += 1
                    sub_item = iTree(tag, cnt)
                elif type(tag) is tuple:
                    tag = list(tag)
                    for ii in update:
                        tag[ii] = i
                    cnt += 1
                    sub_item = iTree(tuple(tag), cnt)
                else:
                    cnt += 1
                    sub_item = iTree(tag, cnt)
                if level != 0:
                    sub = number_per_level[1:]
                    sub_item, cnt = self.large_itree(sub, tags, counter_var, sub_item, cnt)
                root.append(sub_item)
        return root, cnt

    def test1_instance_iTree(self):
        ''''
        we build a tree with some entries and then we try to access the items
        '''
        if not 1 in TEST_SELECTION:
            return
        print('\nRESULT OF SUB-TEST: instance iTree')

        # define empty iTree without tag
        itree = iTree()
        assert itree.tag is NoTag
        assert itree.parent is None
        assert itree.is_root is True
        assert itree.tag_idx is None
        assert len(itree.tag_idx_path) == 0
        assert itree.idx is None
        assert len(itree.idx_path) == 0

        assert len(itree) == 0
        assert not itree.is_linked

        assert itree.value is NoValue

        # implicit iTree definition via value
        itree2 = itree.append(0)

        assert itree2.tag is NoTag
        assert itree2.parent is itree
        assert itree2.is_root is False
        assert itree2.tag_idx == (NoTag, 0)
        assert itree2.tag_idx_path == ((NoTag, 0),)
        assert itree2.idx == 0
        assert itree2.idx_path == (0,)

        assert len(itree2) == 0
        assert itree2.value == 0

        # replace and implicit iTree creation
        itree[0] = 1
        itree2 = itree[0]
        assert itree2.tag is NoTag
        assert itree2.value == 1
        assert itree2.parent is itree

        itree2 = itree.append(iTree(12, value=3))  # int object as tag
        assert itree2.tag == 12
        assert [itree[1]] == itree[{12}]  # access via index and Tag (use set() as helper)
        assert [itree[1]] == itree.get.by_tag(12)  # access via specific tag method

        assert itree[(12, 0)].value == 3  # access via tag_idx

        itree += iTree(12, value=[1, 2, 3], subtree=[iTree(0, 0), iTree(1, 1)])

        itree3 = itree[(12, 1)]  # access via tag_idx
        assert itree3.value == [1, 2, 3]

        assert len(itree) == 3

        # init a iTree with another itree
        itree4 = iTree('tree3', 3, itree)
        assert itree4.tag == 'tree3'
        assert len(itree4) == 3
        assert itree4[0] == itree[0]
        assert itree4[0].parent != itree[0].parent
        assert itree4[0] is not itree[0]
        assert itree4[1].value == itree[1].value
        assert itree4[2].value == itree3.value
        assert itree4[2].value is not itree[2].value
        assert itree3.value is itree[2].value  # short recheck

        itree4 = iTree(('tree4', 1), 3, ((i, i) for i in range(5)))
        assert len(itree4) == 5
        assert itree4.tag == ('tree4', 1)

        # check different tags:
        tags = [None, 1, (1, 2), 'my_tag', b'my_bytes_tag', NoTag, NoValue]
        for tag in tags:
            assert iTree(tag).tag == tag

        # Tags are not allowed as iTree tag
        with pytest.raises(TypeError):
            assert iTree({1}).tag == 1

        assert iTree(NoTag).tag == NoTag

        # instance via itree iterator
        itree5 = iTree(('tree5', 3), 5, itree)
        assert len(itree5) == len(itree)
        for i in range(len(itree5)):
            assert itree5[i] == itree[i]
        assert itree[-1][1] == itree5[-1][1]

        # instance via arg_list (this is like copy)
        itree6 = iTree(*itree5.get_init_args())
        assert len(itree5) == len(itree6)
        assert itree6 == itree5
        assert itree6 is not itree5
        for i in range(len(itree6)):
            assert itree6[i] == itree5[i]
        assert itree6[-1][1] == itree5[-1][1]

        # negative test not allowed data types:

        with pytest.raises(TypeError):
            iTree([1, 2])

        print('\nRESULT OF TEST: instance iTree -> PASS')

    def test2_add_items_to_iTree(self):
        ''''
        we build a tree with some entries and then we try to access the items
        '''
        if not 2 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: add items to iTree')

        # define empty iTree without tag
        itree = iTree()

        # use normal append of different data types (implicit type cast to itree):
        data_items = [None, 1, (1, 2), 'data', [], {}]
        for i, data in enumerate(data_items):
            itree.append(data)
            assert itree[i].value == data
            assert itree[i].tag == NoTag
            assert itree[(NoTag, i)].value == data

        # append itree (NoTag key)
        itree.append(iTree())

        assert itree[i + 1].value == NoValue
        assert itree[i + 1].tag == NoTag
        assert itree[(NoTag, i + 1)].value == NoValue

        # check the lenghts
        assert len(itree) == len(data_items) + 1
        # Family:
        assert len(list(itree[NoTag])) == len(data_items) + 1

        # append normal tagged iTree item with data
        new_tree = itree.append(iTree('tag', 1))
        assert itree[-1].tag == 'tag'
        assert itree[-1].value == 1
        assert itree[-1] == new_tree
        assert itree[-1] is new_tree

        # append via iadd
        itree += iTree('tag', 1)
        assert itree[-1].tag == 'tag'
        assert itree[-1].value == 1
        assert itree[-1] == new_tree
        assert itree[-1] is not new_tree

        # insert (we do not check the different ways of targeting here this is made in the get tests
        old_item = itree[1]
        new_item = itree.insert(1, iTree('new', -1))

        assert itree[1].tag == 'new'
        assert itree[1].value == -1
        assert itree[1] == new_item
        assert itree[1] is new_item
        # check that old item has the right position
        assert itree[2] is old_item

        old_item = itree[-2]
        new_item = itree.insert(-2, iTree('new', -2))
        itree.render()
        assert itree[-3].tag == 'new'
        assert itree[-3].value == -2
        assert itree[-3] == new_item
        assert itree[-3] is new_item
        # check that old item has the right position
        assert itree[-2] is old_item

        # appendleft
        first = itree[0]
        tag_idx_old_new = new_item.tag_idx
        itree.appendleft(iTree('new'))
        assert itree[0].tag == 'new'
        assert itree[1] is first
        assert new_item.tag_idx[1] == tag_idx_old_new[1] + 1

        # appendleft() should be quicker then insert(0,..)
        testtree = iTree()
        t1 = calc_timeit(lambda: testtree.appendleft(iTree()), number=100)
        testtree = iTree()
        t2 = calc_timeit(lambda: testtree.insert(0, iTree()), number=100)
        if BLIST_ACTIVE and False: #  we skip the test it fails on newer python versions
            assert t1 < t2

        # extend list
        l = len(itree)
        itree.extend([iTree('new2') for i in range(5)])
        assert len(itree) == l + 5
        assert itree[-1].tag_idx[1] == 4
        # extend iTree items
        itree2 = iTree('root')
        for i in range(10):
            itree2.append(iTree('new3', i))
        l = len(itree)
        itree.extend(itree2)
        assert len(itree) == l + len(itree2)
        assert itree[-1] == itree2[-1]
        assert itree[-1] is not itree2[-1]

        # extendleft
        l = len(itree)
        a = 5
        itree.extendleft([iTree('new2', i) for i in range(a)])
        assert len(itree) == l + a
        assert itree[0] == iTree('new2', 0)
        assert itree[(a - 1)] == iTree('new2', (a - 1))

        l = len(itree)
        itree.extendleft(itree2)
        assert len(itree) == l + len(itree2)
        assert itree[0] == itree2[0]
        assert itree[len(itree2) - 1] == itree2[len(itree2) - 1]

        # test the special set_single() method

        test_item = itree.append(
            iTree('single', 1, subtree=[iTree('single_2', 2), iTree('double', 1), iTree('double', 2)]))

        test_item['single_2'] = iTree('single_2', 3)  # replace existing item (single operation
        assert test_item.get.single('single_2').value == 3
        with pytest.raises(ValueError):
            test_item.get.single('double')
        test_item['double'] = iTree('double', 4)  # replace existing multiple items in family with one
        assert test_item.get.single('double').value == 4
        test_item[...] = iTree('new', 5)  # append new item
        assert test_item.get.single('new').value == 5

        print('\nRESULT OF TEST: add items to iTree -> PASS')

    def test3_get_items_from_iTree(self):

        if not 3 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: get items from iTree')

        # first we create a tree to target the items
        itree_root = iTree('root')
        itree_root.append(iTree('sub', 0))
        itree_root.append(iTree('sub', 1))
        itree_root.append(iTree('sub', 2))
        itree_root.append(iTree('sub2', 0))
        itree_root.append(iTree('sub2', 1))
        itree_root.append(iTree('sub2', 2))
        itree_root.append(iTree('sub3', 0))
        itree_root.append(iTree('sub3', 1))
        itree_root.append(iTree('sub3', 2))

        itree_root[0].append(iTree('subsub', 0))
        itree_root[0].append(iTree('subsub', 1))
        itree_root[0].append(iTree('subsub', 2))
        itree_root[0].append(iTree('subsub2', 0))
        itree_root[0].append(iTree('subsub2', 1))
        itree_root[0].append(iTree('subsub2', 2))

        itree_root[1].append(iTree('sub2sub', 0))
        itree_root[1].append(iTree('sub2sub', 1))
        itree_root[1].append(iTree('sub2sub', 2))
        itree_root[1].append(iTree('sub2sub2', 0))
        itree_root[1].append(iTree('sub2sub2', 1))
        itree_root[1].append(iTree('sub2sub2', 2))

        itree_root[1][2].append(iTree('sub2subsub', 0))
        itree_root[1][2].append(iTree('sub2subsub', 1))
        itree_root[1][2].append(iTree('sub2subsub', 2))
        itree_root[1][2].append(iTree('sub2subsub2', 0))
        itree_root[1][2].append(iTree('sub2subsub2', 1))
        itree_root[1][2].append(iTree('sub2subsub2', 2))

        itree_root[2].append(iTree('sub3sub', 0))
        itree_root[2].append(iTree('sub3sub', 1))
        itree_root[2].append(iTree('sub3sub', 2))
        itree_root[2].append(iTree('sub3sub2', 0))
        itree_root[2].append(iTree('sub3sub2', 1))
        itree_root[2].append(iTree('sub3sub2', 2))
        itree_root[2].append(iTree('sub3sub2', 3))
        itree_root[2].append(iTree('sub3sub2', 4))
        itree_root[2].append(iTree('sub3sub2', 5))
        itree_root[2].append(iTree('sub3sub2', 6))

        itree_root.render()

        # target via tag
        family = itree_root['sub']
        assert type(family) is itree_list
        assert len(family) == 3
        # access via get helepr class
        family = itree_root.get.by_tag('sub')
        assert type(family) is itree_list
        assert len(family) == 3
        # access via get helper class (multi tag access (not recommended for this case))
        family = itree_root.get.by_tags(['sub'])
        assert type(family) is list
        assert len(family) == 3
        # access via set() as helper
        family = itree_root[{'sub'}]
        assert type(family) is list
        assert len(family) == 3
        # access via specific tag access
        family = itree_root.get.by_tag('sub')
        assert type(family) is itree_list
        assert len(family) == 3

        # recheck the most common access methods:

        family = itree_root['sub']
        assert family[0].tag == 'sub'
        assert family[0].value == 0
        assert family[1].tag == 'sub'
        assert family[1].value == 1
        assert family[2].tag == 'sub'
        assert family[2].value == 2

        family = itree_root.get.by_tag('sub')
        assert family[0].tag == 'sub'
        assert family[0].value == 0
        assert family[1].tag == 'sub'
        assert family[1].value == 1
        assert family[2].tag == 'sub'
        assert family[2].value == 2

        # target a sub item by index
        assert itree_root[0].tag == 'sub'
        assert itree_root[0].value == 0
        assert itree_root[1].tag == 'sub'
        assert itree_root[1].value == 1
        assert itree_root[2].tag == 'sub'
        assert itree_root[2].value == 2
        assert itree_root[3].tag == 'sub2'
        assert itree_root[3].value == 0
        assert itree_root[4].tag == 'sub2'
        assert itree_root[4].value == 1
        assert itree_root[5].tag == 'sub2'
        assert itree_root[5].value == 2
        assert itree_root[6].tag == 'sub3'
        assert itree_root[6].value == 0
        assert itree_root[7].tag == 'sub3'
        assert itree_root[7].value == 1
        assert itree_root[8].tag == 'sub3'
        assert itree_root[8].value == 2
        # negative indexes
        assert itree_root[-1].tag == 'sub3'
        assert itree_root[-1].value == 2
        assert itree_root[-9].tag == 'sub'
        assert itree_root[-9].value == 0
        # same via get helper class:
        assert itree_root.get.by_idx(0).tag == 'sub'
        assert itree_root.get.by_idx(0).value == 0
        assert itree_root.get.by_idx(1).tag == 'sub'
        assert itree_root.get.by_idx(1).value == 1
        assert itree_root.get.by_idx(2).tag == 'sub'
        assert itree_root.get.by_idx(2).value == 2
        assert itree_root.get.by_idx(3).tag == 'sub2'
        assert itree_root.get.by_idx(3).value == 0
        assert itree_root.get.by_idx(4).tag == 'sub2'
        assert itree_root.get.by_idx(4).value == 1
        assert itree_root.get.by_idx(5).tag == 'sub2'
        assert itree_root.get.by_idx(5).value == 2
        assert itree_root.get.by_idx(6).tag == 'sub3'
        assert itree_root.get.by_idx(6).value == 0
        assert itree_root.get.by_idx(7).tag == 'sub3'
        assert itree_root.get.by_idx(7).value == 1
        assert itree_root.get.by_idx(8).tag == 'sub3'
        assert itree_root.get.by_idx(8).value == 2
        # negative indexes
        assert itree_root.get.by_idx(-1).tag == 'sub3'
        assert itree_root.get.by_idx(-1).value == 2
        assert itree_root.get.by_idx(-9).tag == 'sub'
        assert itree_root.get.by_idx(-9).value == 0

        # target via tag-idx tuple
        assert itree_root[('sub', 0)].tag == 'sub'
        assert itree_root[('sub', 0)].value == 0
        assert itree_root[('sub', 1)].tag == 'sub'
        assert itree_root[('sub', 1)].value == 1
        assert itree_root[('sub', 2)].tag == 'sub'
        assert itree_root[('sub', 2)].value == 2
        assert itree_root[('sub2', 0)].tag == 'sub2'
        assert itree_root[('sub2', 0)].value == 0
        assert itree_root[('sub2', 1)].tag == 'sub2'
        assert itree_root[('sub2', 1)].value == 1
        assert itree_root[('sub2', 2)].tag == 'sub2'
        assert itree_root[('sub2', 2)].value == 2
        assert itree_root[('sub3', 0)].tag == 'sub3'
        assert itree_root[('sub3', 0)].value == 0
        assert itree_root[('sub3', 1)].tag == 'sub3'
        assert itree_root[('sub3', 1)].value == 1
        assert itree_root[('sub3', 2)].tag == 'sub3'
        assert itree_root[('sub3', 2)].value == 2
        # same via get helper class:
        assert itree_root.get.by_tag_idx(('sub', 0)).tag == 'sub'
        assert itree_root.get.by_tag_idx(('sub', 0)).value == 0
        assert itree_root.get.by_tag_idx(('sub', 1)).tag == 'sub'
        assert itree_root.get.by_tag_idx(('sub', 1)).value == 1
        assert itree_root.get.by_tag_idx(('sub', 2)).tag == 'sub'
        assert itree_root.get.by_tag_idx(('sub', 2)).value == 2
        assert itree_root.get.by_tag_idx(('sub2', 0)).tag == 'sub2'
        assert itree_root.get.by_tag_idx(('sub2', 0)).value == 0
        assert itree_root.get.by_tag_idx(('sub2', 1)).tag == 'sub2'
        assert itree_root.get.by_tag_idx(('sub2', 1)).value == 1
        assert itree_root.get.by_tag_idx(('sub2', 2)).tag == 'sub2'
        assert itree_root.get.by_tag_idx(('sub2', 2)).value == 2
        assert itree_root.get.by_tag_idx(('sub3', 0)).tag == 'sub3'
        assert itree_root.get.by_tag_idx(('sub3', 0)).value == 0
        assert itree_root.get.by_tag_idx(('sub3', 1)).tag == 'sub3'
        assert itree_root.get.by_tag_idx(('sub3', 1)).value == 1
        assert itree_root.get.by_tag_idx(('sub3', 2)).tag == 'sub3'
        assert itree_root.get.by_tag_idx(('sub3', 2)).value == 2

        # some negative tests related key access
        with pytest.raises(KeyError):
            # invalid tag
            _ = itree_root[('notag', 2)]
        with pytest.raises(KeyError):
            # invalid tag
            _ = itree_root.get.by_tag_idx(('notag', 2))

        with pytest.raises(IndexError):
            # invalid index
            _ = itree_root[('sub3', 2000)]
        with pytest.raises(IndexError):
            # invalid index
            _ = itree_root.get.by_tag_idx(('sub3', 2000))

        with pytest.raises(ValueError):
            # tuple to long
            _ = itree_root[('sub3', 2, 10, 11)]
        with pytest.raises(ValueError):
            # tuple to long
            _ = itree_root.get.by_tag_idx(('sub3', 2, 10, 11))

        with pytest.raises(ValueError):
            # tuple to long
            _ = itree_root[('sub3', slice(0, 2), 10, 11)]
        with pytest.raises(ValueError):
            # tuple to long
            _ = itree_root.get.by_tag_idx_slice(('sub3', slice(0, 2), 10, 11))

        with pytest.raises(ValueError):
            # tuple to long
            _ = itree_root[('sub3', 'abdcs')]
        with pytest.raises(TypeError):
            # tuple to long
            _ = itree_root.get.by_tag_idx(('sub3', 'abdcs'))

        s = len(itree_root)
        # append an item with a long tag:
        long_tag = itree_root.append(iTree(('sub3', 2, 10, 11)))
        # we try to reach the family tag now:
        assert itree_root[('sub3', 2, 10, 11)][0] is long_tag
        assert itree_root.get.by_tag(('sub3', 2, 10, 11))[0] is long_tag

        # clean the tree
        del itree_root[('sub3', 2, 10, 11)]
        assert s == len(itree_root)

        # TagIdx for downward compatibility
        assert itree_root[TagIdx('sub', 0)].tag == 'sub'
        assert itree_root[TagIdx('sub', 0)].value == 0

        # access via implicit tag:
        assert len(itree_root['sub3']) == 3
        # access via get helper class :
        assert len(itree_root.get.by_tag('sub3')) == 3
        # access via get helper class target single tag with multi tag method (not recommended):
        assert len(itree_root.get.by_tags(['sub3'])) == 3
        # access set() :
        assert len(itree_root[{'sub3'}]) == 3
        # access via Families :
        assert len(itree_root.get.by_tag('sub3')) == 3

        # ToDo test sets of tags
        a = itree_root[{'sub3'}]
        b = itree_root[{'sub'}]
        # order might be lost depends on python Version
        assert itree_root[{'sub3', 'sub'}] == a + b or itree_root[{'sub3', 'sub'}] == b + a
        assert itree_root.get.by_tags(['sub3', 'sub']) == a + b  # here the order is kept

        # access via index list (multi item target)
        assert [i.value for i in itree_root[[3, 5]]] == [0, 2]
        assert [i.value for i in itree_root[[1, 4, 5]]] == [1, 1, 2]
        assert [i.value for i in itree_root.get.by_idx_list([1, 4, 5])] == [1, 1, 2]

        # access via tag_idx_list
        assert [i.value for i in itree_root[('sub', [0, 2])]] == [0, 2]
        assert [i.value for i in itree_root.get.by_tag_idx_list(('sub', [0, 2]))] == [0, 2]

        # access via index slice (multi item target)
        assert [i.value for i in itree_root[slice(1, 4)]] == [1, 2, 0]
        assert [i.value for i in itree_root.get.by_idx_slice(slice(1, 4))] == [1, 2, 0]
        assert [i.tag for i in itree_root[slice(1, 4)]] == ['sub', 'sub', 'sub2']
        assert [i.tag for i in itree_root.get.by_idx_slice(slice(1, 4))] == ['sub', 'sub', 'sub2']
        # The specific get.idx_slice does not support implicit slicing!
        assert [i.value for i in itree_root[1:4]] == [1, 2, 0]
        assert [i.value for i in itree_root[:4]] == [0, 1, 2, 0]

        # access via index slice ->full slices
        assert itree_root[:] == list(itree_root)
        assert list(itree_root.get.by_idx_slice(slice(None))) == list(itree_root)

        # access all elements via Ellipsis
        assert itree_root[...] == list(itree_root)
        assert itree_root.get.by_idx_list(...) == list(itree_root)

        # access via tag index slice (multi item target)
        assert [i.value for i in itree_root[('sub', slice(1, 3))]] == [1, 2]
        assert [i.value for i in itree_root['sub', slice(1, 3)]] == [1, 2]
        assert [i.value for i in itree_root.get.by_tag_idx_slice(('sub', slice(1, 3)))] == [1, 2]

        # access via filter (multi item target)
        myfilter = lambda item: type(item.value) is int and item.value < 2
        assert [i.value for i in itree_root[myfilter]] == [0, 1, 0, 1, 0, 1]
        assert [i.value for i in itree_root.get.by_level_filter(myfilter)] == [0, 1, 0, 1, 0, 1]

        # use get_single()
        result = itree_root.get.single('sub', default=None)
        assert result is None
        with pytest.raises(ValueError):
            itree_root.get.single('sub')

        # deep gets

        # get deep via index
        assert itree_root[1][2][1].tag == 'sub2subsub'
        assert itree_root[1][2][4].tag == 'sub2subsub2'

        # get
        # with pytest.raises(TypeError):
        assert itree_root.get() is itree_root

        assert itree_root.get(1, 2, 1) is itree_root[1][2][1]
        assert itree_root.get.by_idx(1, 2, 1) is itree_root[1][2][1]
        assert itree_root.get(*[1, 2, 1]) is itree_root[1][2][1]
        assert itree_root.get.by_idx(*[1, 2, 1]) is itree_root[1][2][1]

        target_path = [1, 2, 1]
        assert itree_root.get(*target_path) is itree_root[1][2][1]
        assert itree_root.get.by_idx(*target_path) is itree_root[1][2][1]

        assert itree_root.get(('sub', 1), 2, ('sub2subsub', 1)) is itree_root[1][2][1]
        assert itree_root.get.by_tag_idx(('sub', 1), ('sub2sub', 2), ('sub2subsub', 1)) is itree_root[1][2][1]
        assert itree_root.get(*[('sub', 1), 2, ('sub2subsub', 1)]) is itree_root[1][2][1]
        assert itree_root.get.by_tag_idx(*[('sub', 1), ('sub2sub', 2), ('sub2subsub', 1)]) is itree_root[1][2][1]

        assert len(itree_root.get(iter, 0)) == 3  # delivers a list of all first items in 2 level
        # use Ellipsis to target all items
        assert len(itree_root.get(..., 0)) == 3  # delivers a list of all first items in 2 level
        assert len(itree_root.get('sub', ..., 0)) == 1  # delivers a list of all first items in 3 level

        # IndexError
        with pytest.raises(IndexError):
            itree_root.get(1, 2, 100)

        # KeyError
        with pytest.raises(KeyError):
            itree_root.get(1, 2, ('FAIL', 1))

        # KeyError
        with pytest.raises(KeyError):
            itree_root.get(1, 2, 'FAIL')

        larger_tree, size = self.large_itree([3, 3, 3], ['tag1', 'tag2', 'tag3', 'tag4'], None)
        # not unique results
        result = list(larger_tree.get('tag1', 'tag2', 'tag3'))
        # The multiple findings in each level should be considered!
        s1 = len(result)  # Based on given filter the result is hard to estimate here!
        assert s1 == 3 * 3 * 3
        for i in result:
            assert i.tag == 'tag3'
            assert i.level == 3

        # get_single() -> deep access
        result = larger_tree.get.single(1, 2, 3)
        assert result is larger_tree[1][2][3]
        result = larger_tree.get.single(1, 2, 300, default=(1, 2))
        assert result == (1, 2)
        with pytest.raises(IndexError):
            result = larger_tree.get.single(1, 2, 300)
        result = larger_tree.get.single(1, 2, 'tag4', default=(1, 2))
        assert result == (1, 2)
        with pytest.raises(ValueError):
            result = larger_tree.get.single(1, 2, 'tag4')

        # contains:
        # contains item
        search_item = itree_root[1][2][1]
        assert search_item not in itree_root
        assert itree_root[2] in itree_root
        assert itree_root[2].copy() in itree_root  # checks for equal not for instance!

        # contains item deep
        assert search_item in itree_root.deep
        assert search_item.copy() in itree_root.deep

        # contains tag
        assert not itree_root.is_tag_in(search_item.tag)
        assert itree_root.is_tag_in(itree_root[2].tag)

        # contains tag deep
        assert any(search_item.tag == i.tag for i in itree_root.deep)

        # contains tag_idx
        assert search_item.tag_idx not in itree_root
        assert itree_root[2].tag_idx in itree_root

        # contains tag_idx deep
        searchkey = itree_root[1][2][0].tag_idx
        assert any(searchkey == i[0][-1] for i in itree_root.deep.tag_idx_paths())

        # contains idx
        assert 7 in itree_root
        assert 9 not in itree_root
        assert any(9 == i[0][-1] for i in itree_root.deep.idx_paths())

        # testing is_in
        assert itree_root.is_in(itree_root[3])
        with pytest.raises(TypeError):
            itree_root.is_in(itree_root[3].tag_idx)
        assert not itree_root.is_in(itree_root[3].copy())  # this function checks for the instance not for equal!

        # testingall.is_in
        assert itree_root.deep.is_in(search_item)
        with pytest.raises(AttributeError):
            itree_root.deep.is_in(search_item.tag_idx)
        assert not itree_root.deep.is_in(search_item.copy())  # this function checks for the instance not for equal!

        # use a very large tree to test index_deep

        largetree, size = self.large_itree([10, 10, 10], ['tag%i', (1, 'cnt'), 'tag_it'], 'cnt')

        assert len(largetree.deep) == size

        a = largetree[7][7].copy()
        largetree[7][1].insert(4, a)

        assert largetree.index(largetree[6]) == 6
        assert largetree.deep.index(a) == (7, 1, 4)
        next_item = a.post_item
        if next_item is None:
            next_item = a[0]
        assert largetree.deep.index(a, next_item) == largetree[7][7].idx_path
        with pytest.raises(IndexError):
            largetree.deep.index(a, next_item, largetree[7][7].pre_item)
        next_item = largetree[7][7].post_item
        if next_item is None:
            next_item = largetree[7][7][0]
        with pytest.raises(IndexError):
            largetree.deep.index(a, next_item)

        # test index
        largetree, size = self.large_itree([10000], ['tag_it', 'tag%i', (1, 'cnt'), 'cnt'], 'cnt')

        assert len(largetree.deep) == size

        a = largetree[700].copy()
        largetree.insert(70, a)
        largetree.insert(9999, a.copy())

        assert largetree.index(largetree[6]) == 6
        assert largetree.index(a) == 70
        next_item = a.post_item
        assert largetree.index(a, next_item) == 701
        with pytest.raises(IndexError):
            largetree.deep.index(a, next_item, largetree[600])
        assert largetree.index(a, 702) == 9999

        # check the family type
        try:
            from blist import blist
        except ImportError:
            blist = list
        assert type(largetree._families['tag_it']) is blist

        print('\nRESULT OF TEST: get items from iTree -> PASS')

    def test3b_get_items_from_iTree(self):

        if not 3 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: get items (timings) from iTree')

        # timings
        # create a large tree for timing tests
        larger_tree_timeit, size = self.large_itree([1000, 3, 3], ['tag1', 'tag2', 'tag3', 'tag4'], None)
        # level 0 access
        s = 1000
        s2 = 10
        repeat = 3
        w = 50  # string with

        print('\n#### LEVEL 0 ACCESS ####')

        print('\nPython standard class access ({} items targeted):'.format(s * s2))
        l = list(range(s))
        t = calc_timeit(lambda: [l[i] for i in range(s) for ii in range(s2)], repeat)
        out = 'list[idx]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        t = calc_timeit(lambda: [l[1:1000] for i in range(s) for _ in range(s2)], repeat)
        out = 'list[1:1000]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        t = calc_timeit(lambda: [l[:] for i in range(s) for _ in range(s2)], repeat)
        out = 'list[:]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        if BLIST_ACTIVE:
            bl = blist(range(s))
            t = calc_timeit(lambda: [bl[i] for i in range(s) for _ in range(s2)], repeat)
            out = 'blist[idx]'
            print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
            t = calc_timeit(lambda: [bl[1:1000] for i in range(s) for _ in range(s2)], repeat)
            out = 'blist[1:1000]'
            print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
            t = calc_timeit(lambda: [bl[:] for i in range(s) for _ in range(s2)], repeat)
            out = 'blist[:]'
            print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        d = {('tag1', i): i for i in range(s)}
        t = calc_timeit(lambda: [d[('tag1', i)] for i in range(s) for _ in range(s2)], repeat)
        out = 'dict[key]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        print('\nAbsolute index access ({} items targeted):'.format(s * s2))
        assert larger_tree_timeit[0].idx == 0
        t = calc_timeit(lambda: [larger_tree_timeit[i] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[idx]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert larger_tree_timeit.get.by_idx(0).idx == 0
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_idx(i) for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree.get.by_idx(idx)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert larger_tree_timeit.getitem_by_idx(0).idx == 0
        t = calc_timeit(lambda: [larger_tree_timeit.getitem_by_idx(i) for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree.getitem_by_idx(idx)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        print('\nTag-index access ({} items targeted):'.format(s * s2))
        assert larger_tree_timeit[('tag1', 0)].idx == 0
        t = calc_timeit(lambda: [larger_tree_timeit[('tag1', i)] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[tag_idx]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert larger_tree_timeit.get.by_tag_idx(('tag1', 0)).idx == 0
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_tag_idx(('tag1', i)) for i in range(s) for _ in range(s2)],
                        repeat)
        out = 'iTree.get.by_tag_idx(tag_idx)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        print('\nTag (family) access ({} items targeted):'.format(s * s2))
        assert len(larger_tree_timeit['tag1']) == s
        t = calc_timeit(lambda: [larger_tree_timeit['tag1'] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[tag]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_tag('tag1')) == s
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_tag('tag1') for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree.get.by_tag(tag)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit[{'tag1'}]) == s
        t = calc_timeit(lambda: [larger_tree_timeit[{'tag1'}] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[set(tag)]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_tags(['tag1'])) == s
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_tags(['tag1']) for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree.get.by_tags([tag])'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        print('\nAbsolute index slice ({} slices targeted):'.format(s * s2))
        assert len(larger_tree_timeit[0:s]) == s
        assert type(larger_tree_timeit[0:s]) in (list, itree_list)
        t = calc_timeit(lambda: [larger_tree_timeit[0:s] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[0:{}]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_idx_slice(slice(0, s))) == s
        assert type(larger_tree_timeit.get.by_idx_slice(slice(0, s))) in (list, itree_list)
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_idx_slice(slice(0, s)) for i in range(s) for _ in range(s2)],
                        repeat)
        out = 'iTree.get.by_idx_slice(slice(0,{}))'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit[:]) == 4 * s
        assert type(larger_tree_timeit[:]) in (list, itree_list)
        t = calc_timeit(lambda: [larger_tree_timeit[:] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[:]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_idx_slice(slice(None))) == 4 * s
        assert type(larger_tree_timeit.get.by_idx_slice(slice(None))) in (list, itree_list)
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_idx_slice(slice(None)) for i in range(s) for _ in range(s2)],
                        repeat)
        out = 'iTree.get.by_idx_slice(slice(None))'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        s3 = int(s / 2)
        index_list = [i for i in range(s3)]
        print('\nAbsolute index list ({} lists targeted; list-length{}):'.format(s * s2, s3))
        assert len(larger_tree_timeit[index_list]) == len(index_list)
        t = calc_timeit(lambda: [larger_tree_timeit[index_list] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[[index_list]]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_idx_list(index_list)) == s3
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_idx_list(index_list) for i in range(s) for _ in range(s2)],
                        repeat)
        out = 'iTree.get.by_idx_list([index_list])'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit[...]) == 4 * s
        t = calc_timeit(lambda: [larger_tree_timeit[...] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[...]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_idx_list(...)) == 4 * s
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_idx_list(...) for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree.get.by_idx_list(...)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        s3 = 990
        print('\ntag (family) index slice ({} slices targeted):'.format(s * s2))
        assert len(larger_tree_timeit['tag1', 0:s]) == s
        assert type(larger_tree_timeit['tag1', 0:s]) in (list, itree_list)
        t = calc_timeit(lambda: [larger_tree_timeit['tag1', 0:s] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree["tag1",0:{}]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_tag_idx_slice(('tag1', slice(0, s)))) == s
        t = calc_timeit(
            lambda: [larger_tree_timeit.get.by_tag_idx_slice(('tag1', slice(0, s))) for i in range(s) for _ in
                     range(s2)], repeat)
        out = 'iTree.get.by_tag_idx_slice(("tag1",slice(0,{})))'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit['tag1', slice(None)]) == s
        t = calc_timeit(lambda: [larger_tree_timeit['tag1', slice(None)] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree["tag1",slice(None)]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_tag_idx_slice(('tag1', slice(None)))) == s
        t = calc_timeit(
            lambda: [larger_tree_timeit.get.by_tag_idx_slice(('tag1', slice(None))) for i in range(s) for _ in
                     range(s2)], repeat)
        out = 'iTree.get.by_tag_idx_slice(("tag1",slice(None)))'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        s3 = int(s / 2)
        index_list = [i for i in range(s3)]
        print('\ntag (family) index list ({} lists targeted; list-length{}):'.format(s * s2, s3))
        assert len(larger_tree_timeit['tag1', index_list]) == s3
        assert type(larger_tree_timeit['tag1', index_list]) in (list, itree_list)
        t = calc_timeit(lambda: [larger_tree_timeit['tag1', index_list] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree[["tag1",index_list]]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_tag_idx_list(('tag1', index_list))) == s3
        assert type(larger_tree_timeit.get.by_tag_idx_list(('tag1', index_list))) in (list, itree_list)
        t = calc_timeit(
            lambda: [larger_tree_timeit.get.by_tag_idx_list(('tag1', index_list)) for i in range(s) for _ in range(s2)],
            repeat)
        out = 'iTree.get.by_tag_idx_list(("tag1",index_list))'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit["tag1", ...]) == s
        assert type(larger_tree_timeit["tag1", ...]) in (list, itree_list)
        t = calc_timeit(lambda: [larger_tree_timeit["tag1", ...] for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree["tag1",...]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert len(larger_tree_timeit.get.by_tag_idx_list(("tag1", ...))) == s
        assert type(larger_tree_timeit.get.by_tag_idx_list(("tag1", ...))) in (list, itree_list)
        t = calc_timeit(
            lambda: [larger_tree_timeit.get.by_tag_idx_list(("tag1", ...)) for i in range(s) for _ in range(s2)],
            repeat)
        out = 'iTree.get.by_idx_list(("tag1",...))'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        print('\n#### LEVEL 1 ACCESS ####')

        print('\nPython standard class access ({} items targeted):'.format(s * s2))
        l = [[i, i, i] for i in range(s)]
        t = calc_timeit(lambda: [l[i][1] for i in range(s) for _ in range(s2)], repeat)
        out = 'list[idx][idx]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        d = {('tag1', i): {('tag1', 0): i, ('tag2', 1): i} for i in range(s)}
        t = calc_timeit(lambda: [d[('tag1', i)][('tag2', 1)] for i in range(s) for _ in range(s2)], repeat)
        out = 'dict[key][key]'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        print('\nAbsolute index access ({} items targeted):'.format(s * s2))
        assert larger_tree_timeit.get(0, 1).idx == 1
        assert type(larger_tree_timeit.get(0, 1)) is iTree
        t = calc_timeit(lambda: [larger_tree_timeit.get(i, 1) for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree.get(idx,1)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert larger_tree_timeit.get.by_idx(0, 1).idx == 1
        assert type(larger_tree_timeit.get.by_idx(0, 1)) is iTree
        t = calc_timeit(lambda: [larger_tree_timeit.get.by_idx(i, 1) for i in range(s) for _ in range(s2)], repeat)
        out = 'iTree.get.by_idx(idx,1)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        print('\nTag-index access ({} items targeted):'.format(s * s2))
        assert larger_tree_timeit.get(('tag1', 0), ('tag1', 1)).idx == 4
        t = calc_timeit(lambda: [larger_tree_timeit.get(('tag1', i), ('tag1', 1)) for i in range(s) for _ in range(s2)],
                        repeat)
        out = 'iTree.get(tag_idx,tag_idx)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))
        assert larger_tree_timeit.get.by_tag_idx(('tag1', 0), ('tag1', 1)).idx == 4
        t = calc_timeit(
            lambda: [larger_tree_timeit.get.by_tag_idx(('tag1', i), ('tag1', 1)) for i in range(s) for _ in range(s2)],
            repeat)
        out = 'iTree.get.by_tag_idx(tag_idx,tag_idx)'
        print('Execution time {}:{: ^{width}} {:.6f} s'.format(out, '', t, width=w - len(out)))

        print('\nRESULT OF TEST: get items from iTree -> PASS')

    def test4_delete_items_from_iTree(self):
        if not 4 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: delete items from iTree')

        # build a tree to delete some items from
        itree_root = iTree(0, 1)
        itree_root += iTree(10, 2)
        itree_root += iTree(11, 3)
        itree_root += iTree(12, 4)
        itree_root += iTree(13, 5)

        itree_root[0] += iTree(100, 6)
        itree_root[0] += iTree(101, 7)
        itree_root[0] += iTree(102, 8)
        itree_root[0] += iTree(103, 9)

        itree_root[1] += iTree(210, 6)
        itree_root[1] += iTree(211, 7)
        itree_root[1] += iTree(212, 8)
        itree_root[1] += iTree(213, 9)

        itree_root[2] += iTree(310, 6)
        itree_root[2] += iTree(311, 7)
        itree_root[2] += iTree(313, 8)
        itree_root[2] += iTree(314, 9)

        itree_root[3] += iTree(410, 6)
        itree_root[3] += iTree(411, 7)
        itree_root[3] += iTree(412, 8)
        itree_root[3] += iTree(413, 9)

        # delete
        # delete based on idx
        l = len(itree_root[1])
        target_item = itree_root[1][0]
        del itree_root[1][0]
        assert itree_root[1][0].tag == 211
        assert len(itree_root[1]) == l - 1
        assert target_item.parent == None
        # re-insert the deleted item
        itree_root[1].appendleft(target_item)

        # del tag idx
        target_item = itree_root.get(1, (211, 0))
        del itree_root[1][(211, 0)]  # tag_idx targeting iTree(211,7)
        assert itree_root[1][1].tag == 212
        assert len(itree_root[1]) == l - 1
        assert target_item.parent == None
        # re-insert the deleted item
        itree_root[1].insert(1, target_item)

        # del whole tag
        l = len(itree_root)
        del itree_root[{11}]
        assert itree_root[1].tag == 12
        assert len(itree_root) == l - 1
        with pytest.raises(KeyError):
            itree_root[{11}]
        # re-insert the deleted item
        itree_root.insert(1, iTree(11, 3))
        itree_root[1] += iTree(210, 6)
        itree_root[1] += iTree(211, 7)
        itree_root[1] += iTree(212, 8)
        itree_root[1] += iTree(213, 9)

        # pop (right)
        item = itree_root[3][-1]
        l = len(itree_root[3])
        tag_idx = item.tag_idx
        assert item.parent == itree_root[3]
        popped_item = itree_root[3].pop()
        assert popped_item is item
        assert len(itree_root[3]) == (l - 1)
        assert tag_idx[0] not in itree_root[3]

        # pop (specific)
        # pop based on idx
        l = len(itree_root[1])
        target_item = itree_root[1].pop(0)
        assert itree_root[1][0].tag == 211
        assert len(itree_root[1]) == l - 1
        assert target_item.parent == None
        # re-insert the deleted item
        itree_root[1].appendleft(target_item)

        # remove
        s1 = len(itree_root[1])
        item = itree_root[1].remove(itree_root[1][1])
        assert len(itree_root[1]) == s1 - 1
        assert item.parent is None  # parent removed?
        # reinsert the item:
        itree_root[1].insert(1, item)
        # multiple remove (all children)
        items = itree_root[1].remove(iter(itree_root[1]))
        assert len(itree_root[1]) == 0
        # re insert:
        itree_root[1].extend(items)
        assert len(itree_root[1]) == s1
        # remove an item that is not a children:
        with pytest.raises(ValueError):
            itree_root[1].remove(iTree())
        with pytest.raises(ValueError):
            itree_root[1].remove(itree_root[2][0])

        # del tag idx,
        target_item = itree_root[1].pop((211, 0))  # tag_idx targeting iTree(211,7)
        assert itree_root[1][1].tag == 212
        assert len(itree_root[1]) == l - 1
        assert target_item.parent == None
        # re-insert the deleted item
        itree_root[1].insert(1, target_item)

        # del whole tag
        l = len(itree_root)
        target_item = itree_root.pop({11})
        assert itree_root[1].tag == 12
        assert len(itree_root) == l - 1
        assert target_item[0].value == 3
        assert target_item[0].parent is None

        largetree, size = self.large_itree([1000000], ['tag_it'], 'cnt')

        # test idx update after deletes
        # first ensure the indexes are uptodate:
        largetree[-1].idx
        largetree[-1].tag_idx

        size = len(largetree)
        t = calc_timeit(lambda: largetree[-1].idx, number=1)
        tb = calc_timeit(lambda: largetree[-1].tag_idx, number=1)
        # check the values:
        assert largetree[largetree[-1].idx] is largetree[-1]
        key = largetree[-1].tag_idx
        assert list(largetree[{key[0]}])[key[1]] is largetree[-1]

        del largetree[1]
        assert len(largetree) == size - 1
        t1 = calc_timeit(lambda: largetree[-1].idx, number=1)
        tb1 = calc_timeit(lambda: largetree[-1].tag_idx, number=1)
        # check the values:
        assert largetree[largetree[-1].idx] is largetree[-1]
        key = largetree[-1].tag_idx
        assert list(largetree[{key[0]}])[key[1]] is largetree[-1]

        del largetree[1:10]
        assert len(largetree) == size - 1 - 9
        t2 = calc_timeit(lambda: largetree[-1].idx, number=1)
        tb2 = calc_timeit(lambda: largetree[-1].tag_idx, number=1)
        # check the values:
        assert largetree[largetree[-1].idx] is largetree[-1]
        key = largetree[-1].tag_idx
        assert largetree[{key[0]}][key[1]] is largetree[-1]
        t = calc_timeit(lambda: largetree.__delitem__(slice(101,201)), number=1)
        print('Delete time of 100 items via slice: %.6fs'%t)
        del largetree[-102:-2]
        del largetree[201:301]
        del largetree[1201:1301]

        assert len(largetree) == size - 1 - 9 - 400
        t3 = calc_timeit(lambda: largetree[-1].idx, number=1)
        tb3 = calc_timeit(lambda: largetree[-1].tag_idx, number=1)
        # check the values:
        assert largetree[largetree[-1].idx] is largetree[-1]
        key = largetree[-1].tag_idx
        assert list(largetree[{key[0]}])[key[1]] is largetree[-1]

        print('Info:')
        print('Itree size: %i: update times .idx: No delete: %es; '
              '1 delete: %es; 10 deletes: %es; 100 deletes: %es' % (size, t, t1, t2, t3))
        print('Itree size: %i: update times .key: No delete: %es; '
              '1 delete: %es; 10 deletes: %es; 100 deletes: %es' % (size, tb, tb1, tb2, tb3))

        print('Itree size: %i: forced idx update: %es' % (
        size, calc_timeit(lambda: largetree.force_cache_update(True, False, False), 2)))
        print('Itree size: %i: forced key_update on family update: %es' % (
        size, calc_timeit(lambda: largetree.force_cache_update(False, True, False), 2)))
        print('Itree size: %i: forced key_update all families update: %es' % (
        size, calc_timeit(lambda: largetree.force_cache_update(False, False, True), 2)))

        largetree.extend(iTree('family1') * 100)
        largetree.extend(iTree('family2') * 100)
        delitems = largetree.pop({'family1', 'family2'})
        assert len(delitems) == 200

        # deep access with delete,pop,remove
        test_tree = iTree('1',
                          subtree=[iTree('1_1'),
                                   iTree('1_2'),
                                   iTree('1_3'),
                                   iTree('1_4', subtree=[iTree('1_1_1'),
                                                         iTree('1_1_2'),
                                                         iTree('1_1_3', subtree=[iTree('delete')])])])
        assert len(test_tree.get(-1, -1)) == 1
        del test_tree.get(-1, -1)[-1]
        assert len(test_tree.get(-1, -1)) == 0
        test_tree.get(-1, -1).append(iTree('delete'))
        assert len(test_tree.get(-1, -1)) == 1
        assert test_tree.get(-1, -1).pop(-1).tag == 'delete'
        assert len(test_tree.get(-1, -1)) == 0
        assert test_tree[-1].pop(1).tag == '1_1_2'
        assert test_tree[-1].remove(test_tree.get(-1, 0)).tag == '1_1_1'
        s = len(test_tree[-1])
        del test_tree[-1][0]
        assert len(test_tree[-1]) == s - 1

        # in depth remove
        test_tree = iTree('1',
                          subtree=[iTree('1_1'),
                                   iTree('1_2'),
                                   iTree('1_3', subtree=[iTree('1_1_1'),
                                                         iTree('1_1_1'),
                                                         iTree('1_1_1')]),
                                   iTree('1_4', subtree=[iTree('1_1_1'),
                                                         iTree('1_1_1'),
                                                         iTree('1_1_1')])])

        # test_tree.render()
        assert len(test_tree.get(iter, '1_1_1')) == 6
        assert len(test_tree.deep.remove(iter, '1_1_1')) == 6
        # test_tree.render()
        assert len(test_tree.get(-1)) == 0
        assert len(test_tree.get(-2)) == 0
        return

        print('\nRESULT OF TEST: delete items from iTree - PASS')

    def test5_rearrange_items_from_iTree(self):
        if not 5 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: set(replace)/rearrange items  in iTree')
        itree_root = iTree('root')
        itree_root.append(iTree('sub', 0))
        itree_root.append(iTree('sub', 1))
        itree_root.append(iTree('sub', 2))
        itree_root.append(iTree('sub2', 0))
        itree_root.append(iTree('sub2', 1))
        itree_root.append(iTree('sub2', 2))
        itree_root.append(iTree('sub3', 0))
        itree_root.append(iTree('sub3', 1))
        itree_root.append(iTree('sub3', 2))

        # replace by index
        itree_root[3] = iTree('replace1', 4)
        assert itree_root[3].tag == 'replace1'
        # replace by tag index
        itree_root[('sub3', 2)] = iTree('replace2', 5)
        assert itree_root[-1].tag == 'replace2'

        # not unique target for replacement leads into an exception
        with pytest.raises(LookupError):
            itree_root[{'sub3'}] = iTree('replace3', 6)

        # rearrange items
        itree_root[0], itree_root[3] = itree_root[3], itree_root[0]
        assert itree_root[0].tag == 'replace1'
        assert itree_root[0].value == 4
        assert itree_root[3].tag == 'sub'
        assert itree_root[3].value == 0

        # rearrange via slice
        print([i for i in itree_root[:3]])

        itree_root[2], itree_root[0], itree_root[1] = itree_root[:3]

        # print(list(itree_root[:3]))
        # old 0 is now 2
        assert itree_root[2].tag == 'replace1'
        assert itree_root[2].value == 4
        # old 1 is now 0
        assert itree_root[0].tag == 'sub'
        assert itree_root[0].value == 1
        # old 2 is now 1
        assert itree_root[1].tag == 'sub'
        assert itree_root[1].value == 2

        # slice on left side
        itree_root[:3] = itree_root[2], itree_root[0], itree_root[1]
        assert itree_root[0].tag == 'replace1'
        assert itree_root[0].value == 4
        # old 1 is now 0
        assert itree_root[1].tag == 'sub'
        assert itree_root[1].value == 1
        # old 2 is now 1
        assert itree_root[2].tag == 'sub'
        assert itree_root[2].value == 2

        # slices on both sides

        itree_root[2::-1] = itree_root[0:3]

        assert itree_root[0].tag == 'sub'
        assert itree_root[0].value == 2
        # old 1 is now 0
        assert itree_root[1].tag == 'sub'
        assert itree_root[1].value == 1
        # old 2 is now 1
        assert itree_root[2].tag == 'replace1'
        assert itree_root[2].value == 4

        # neutralize last operation for following steps
        itree_root[0], itree_root[1] = itree_root[1], itree_root[0]

        # the move operation keeps the original instances!
        itree_root[1].move(2)
        assert itree_root[2].tag == 'sub'
        assert itree_root[2].value == 2
        assert itree_root[1].tag == 'replace1'
        assert itree_root[1].value == 4
        item = itree_root[0]
        lastitem = itree_root[-1]
        itree_root[0].move(-1)
        assert itree_root[-2] is item
        assert itree_root[-1] is lastitem
        item = itree_root[0]
        itree_root[0].move()
        assert itree_root[-1] is item
        assert itree_root[-2] is lastitem
        # negative test in case no unique target is given
        with pytest.raises(LookupError):
            itree_root[0].move({'sub'})

        value = itree_root[2].value
        itree_root[2].rename('new_tag')
        assert itree_root[2].tag == 'new_tag'
        assert itree_root[2].value == value

        # rotate single
        a = itree_root[0]
        a_ti = a.tag_idx
        itree_root.append(iTree('sub', 10))
        b = itree_root[-1]
        b_ti = b.tag_idx
        itree_root.rotate()
        assert itree_root[1] is a
        assert a_ti != a.tag_idx  # tag_idx changed after we have new first item
        assert itree_root[0] is b
        assert b_ti != b.tag_idx  # tag_idx changed after beeing first item
        # rotade multiple positions
        a = itree_root[0]
        a_ti = a.tag_idx
        itree_root.insert(-3, iTree('sub', 11))
        b = itree_root[-4]
        b_ti = b.tag_idx
        itree_root.rotate(4)
        assert itree_root[4] is a
        assert a_ti != a.tag_idx  # tag_idx changed after we have new first item
        assert itree_root[0] is b
        assert b_ti != b.tag_idx  # tag_idx changed after beeing first item

        # rotate minus single
        first = itree_root[0]
        second = itree_root[1]
        last = itree_root[-1]
        itree_root.rotate(-1)
        assert itree_root[0] is second
        assert itree_root[-1] is first
        assert itree_root[-2] is last
        first = itree_root[0]
        last = itree_root[-1]
        fifth = itree_root[4]
        fourth = itree_root[3]
        itree_root.rotate(-4)
        assert fifth is itree_root[0]
        assert fourth is itree_root[-1]
        assert first is itree_root[-4]
        assert last is itree_root[-5]

        # reverse
        b = itree_root.appendleft(iTree('reverse0', 1))
        a = itree_root.appendleft(iTree('reverse0', 0))
        c = itree_root.append(iTree('reverse0', 2))
        d = itree_root.append(iTree('reverse0', 3))
        a_ti = a.tag_idx
        assert a_ti[1] == 0
        b_ti = b.tag_idx
        assert b_ti[1] == 1
        c_ti = c.tag_idx
        assert c_ti[1] == 2
        d_ti = d.tag_idx
        assert d_ti[1] == 3

        old_itree = itree_root.copy()
        # reversed
        new_reversed = list(reversed(itree_root))

        assert itree_root[0].tag_idx == a_ti
        assert itree_root[1].tag_idx == b_ti
        assert itree_root[-2].tag_idx == c_ti
        assert itree_root[-1].tag_idx == d_ti

        assert new_reversed[-1].tag_idx == a_ti
        assert new_reversed[-2].tag_idx == b_ti
        assert new_reversed[1].tag_idx == c_ti
        assert new_reversed[0].tag_idx == d_ti

        # reverse
        itree_root.reverse()

        for i,ii in zip(itree_root,new_reversed):
            assert i is ii

        assert itree_root[0] is d
        assert itree_root[1] is c
        assert itree_root[-2] is b
        assert itree_root[-1] is a

        assert itree_root[0].tag_idx == a_ti
        assert itree_root[1].tag_idx == b_ti
        assert itree_root[-2].tag_idx == c_ti
        assert itree_root[-1].tag_idx == d_ti

        # reverse back
        itree_root.reverse()
        assert itree_root == old_itree

        # reverse deep
        b = itree_root[1].appendleft(iTree('reverse2', 1))
        a = itree_root[1].appendleft(iTree('reverse2', 0))
        c = itree_root[1].append(iTree('reverse2', 2))
        d = itree_root[1].append(iTree('reverse2', 3))

        a_ti = a.tag_idx
        assert a_ti[1] == 0
        b_ti = b.tag_idx
        assert b_ti[1] == 1
        c_ti = c.tag_idx
        assert c_ti[1] == 2
        d_ti = d.tag_idx
        assert d_ti[1] == 3

        itree_root.deep.reverse()

        assert itree_root[-2][0] is d
        assert itree_root[-2][1] is c
        assert itree_root[-2][-2] is b
        assert itree_root[-2][-1] is a

        assert itree_root[-2][0].tag_idx == a_ti
        assert itree_root[-2][1].tag_idx == b_ti
        assert itree_root[-2][-2].tag_idx == c_ti
        assert itree_root[-2][-1].tag_idx == d_ti

        # sort (no deep test of sorted made we use the function of the list
        root = iTree('root', subtree=[iTree('d'), iTree('e'), iTree('c'), iTree('b'), iTree('a')])

        root.sort(key=lambda i: i.tag)
        assert root[0].tag == 'a'
        assert root[1].tag == 'b'
        assert root[2].tag == 'c'
        assert root[3].tag == 'd'
        assert root[4].tag == 'e'

        root = iTree('root', subtree=[iTree('d', subtree=[iTree('d'), iTree('e'), iTree('c'), iTree('b'), iTree('a')]),
                                      iTree('e'), iTree('c'), iTree('b'), iTree('a')])
        root.deep.sort(key=lambda i: i.tag)
        assert root[0].tag == 'a'
        assert root[1].tag == 'b'
        assert root[2].tag == 'c'
        assert root[3].tag == 'd'
        assert root[4].tag == 'e'
        assert root[3][0].tag == 'a'
        assert root[3][1].tag == 'b'
        assert root[3][2].tag == 'c'
        assert root[3][3].tag == 'd'
        assert root[3][4].tag == 'e'

        print('\nRESULT OF TEST: set(replace)/rearrange items in iTree -> PASS')

    def test6_iTree_properties(self):
        if not 6 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree properties')
        # build a small tree
        itree_root = iTree(1, 1)
        itree_root += iTree(1.0, 2)
        itree_root += iTree(1.1, 3)
        itree_root += iTree(1.2, 4)
        itree_root += iTree(1.3, 5)

        itree_root[0] += iTree(1.00, 6)
        itree_root[0] += iTree(1.01, 7)
        itree_root[0] += iTree(1.02, 8)
        itree_root[0] += iTree(1.03, 9)

        itree_root[1] += iTree(1.10, 6)
        itree_root[1] += iTree(1.12, 7)
        itree_root[1] += iTree(1.13, 8)
        itree_root[1] += iTree(1.14, 9)

        itree_root[2] += iTree(1.20, 6)
        itree_root[2] += iTree(1.22, 7)
        itree_root[2] += iTree(1.23, 8)
        itree_root[2] += iTree(1.24, 9)

        itree_root[3] += iTree(1.30, 6)
        itree_root[3] += iTree(1.32, 7)
        itree_root[3] += iTree(1.33, 8)
        itree_root[3] += iTree(1.34, 9)
        itree_root[3] += iTree(1.34, 10)

        single = iTree()

        # parent
        assert itree_root[1].parent is itree_root
        assert itree_root[1][1].parent is itree_root[1]
        assert itree_root.parent is None

        # check if the properties are really protected from overwriting:
        with pytest.raises(AttributeError):
            itree_root.parent = 'abc'

        # is_root
        assert single.is_root
        assert itree_root.is_root
        assert not itree_root[1][1].is_root

        # root
        assert itree_root[1][1].root is itree_root
        assert itree_root.root is itree_root
        assert single.root is single

        # tag
        assert itree_root.tag == 1
        assert itree_root[1].tag == 1.1
        assert single.tag is NoTag

        # idx
        for i, item in enumerate(itree_root):
            assert item.idx == i

        # idx path
        assert itree_root[1][1].idx_path == (1, 1)
        assert itree_root[3][1].idx_path == (3, 1)
        assert itree_root[3][2].idx_path == (3, 2)

        # key
        assert itree_root.tag_idx is None
        assert single.tag_idx is None
        assert itree_root[1].tag_idx == (1.1, 0)
        assert itree_root[1][3].tag_idx == (1.14, 0)
        assert itree_root[3][3].tag_idx == (1.34, 0)
        assert itree_root[3][4].tag_idx == (1.34, 1)

        # key path
        assert itree_root.tag_idx_path == tuple()
        assert itree_root[1].tag_idx_path == ((1.1, 0),)
        assert itree_root[3][3].tag_idx_path == ((1.3, 0), (1.34, 0))
        assert itree_root[3][4].tag_idx_path == ((1.3, 0), (1.34, 1))

        # the following properties are tested in specific test
        assert not itree_root[2].is_tree_read_only
        assert not itree_root[2].is_value_read_only
        assert not itree_root[0].is_placeholder
        assert not itree_root[1].is_linked
        assert not itree_root[2][0].is_linked

        # pre_item
        assert itree_root[1][3].pre_item is itree_root[1][2]
        assert itree_root[1][0].pre_item is None
        assert itree_root.pre_item is None

        # post_item
        assert itree_root[1][2].post_item is itree_root[1][3]
        assert itree_root[1][3].post_item is None
        assert itree_root[-1].post_item is None
        assert itree_root.post_item is None

        # tag number
        assert itree_root.tag_number == len(list(itree_root._families.keys()))

        # depth_up
        assert itree_root[1][3].level == 2
        assert itree_root[2].level == 1
        assert itree_root.level == 0

        # max_depth_down
        assert itree_root[1][3].max_depth == 0
        assert itree_root[2].max_depth == 1
        assert itree_root.max_depth == 2

        # we check couple object detection in all directions
        coupled_obj = {1: 1}
        itree_root[1].set_coupled_object(coupled_obj)
        assert itree_root[1].coupled_object is coupled_obj
        # coupled object is not copied:
        new_itree = itree_root[1].copy()
        assert new_itree.coupled_object is not coupled_obj
        assert new_itree.coupled_object is None
        assert new_itree == itree_root[1]  # it's not considered in compair
        # self has but other has no coupled object
        assert not itree_root[1].equal(new_itree, check_coupled=True)
        # other has different coupled object
        new_itree2 = new_itree.copy()
        coupled_obj2 = {2, 2}
        new_itree2.set_coupled_object(coupled_obj2)
        assert not itree_root[1].equal(new_itree2, check_coupled=True)
        # self has no coupled object other has
        assert not new_itree.equal(new_itree2, check_coupled=True)
        # self and other have same coupled object
        new_itree2.set_coupled_object(coupled_obj)
        assert itree_root[1].equal(new_itree2, check_coupled=True)
        # self and other have equal but not same coupled object
        coupled_obj3 = {1: 1}
        new_itree2.set_coupled_object(coupled_obj3)
        assert not itree_root[1].equal(new_itree2, check_coupled=True)

        print('\nRESULT OF TEST: iTree properties-> PASS')

    def test6b_iTree_properties(self):
        if not 6 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree properties(b)')
        # build a small tree
        itree_root = iTree(1, 1)
        itree_root += iTree(1.0, 2)
        itree_root += iTree(1.1, 3)
        itree_root += iTree(1.2, 4)
        itree_root += iTree(1.3, 5)

        itree_root[0] += iTree(1.00, 6)
        itree_root[0] += iTree(1.01, 7)
        itree_root[0] += iTree(1.02, 8)
        itree_root[0] += iTree(1.03, 9)

        itree_root[1] += iTree(1.10, 6)
        itree_root[1] += iTree(1.12, 7)
        itree_root[1] += iTree(1.13, 8)
        itree_root[1] += iTree(1.14, 9)

        itree_root[2] += iTree(1.20, 6)
        itree_root[2] += iTree(1.22, 7)
        itree_root[2] += iTree(1.23, 8)
        itree_root[2] += iTree(1.24, 9)

        itree_root[3] += iTree(1.30, 6)
        itree_root[3] += iTree(1.32, 7)
        itree_root[3] += iTree(1.33, 8)
        itree_root[3] += iTree(1.34, 9)
        itree_root[3] += iTree(1.34, 10)

        #ancestors

        low_level_item=itree_root[1].append(iTree('sub')).append(iTree('subsub'))
        a=low_level_item.ancestors
        assert len(a)==3
        assert a[0] == itree_root
        assert a[1]==itree_root[1]
        assert a[2]==itree_root[1][-1]

        #siblings

        s=list(itree_root[1].siblings)
        s2=list(itree_root)
        assert len(s)+1==len(s2)
        i=0
        for item in s2:
            if item is not itree_root[1]:
                assert item==s[i]
                i += 1

        print('\nRESULT OF TEST: iTree properties(b) -> PASS')

    def test7_iTree_internals_methods(self):
        if not 7 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree internals')

        # _value_equal
        root = iTree()
        a = {1: 2, 2: 3, 'asdlkj': 4}
        b = a.copy()
        assert root._value_equal(a, b)
        a = OrderedDict(a.items())
        b = a.copy()
        assert root._value_equal(a, b)

        a = [1, 2, 3, 4, 5, 6, 7, 8]
        b = a.copy()
        assert root._value_equal(a, b)
        if np:
            a = {'myarray': np.array([1.5, 4., 3.6, 467.])}
            b = a.copy()
            assert root._value_equal(a, b)

        print('\nRESULT OF TEST: iTree internals-> PASS')

    def test8_iTree_value_related_methods(self):
        if not 7 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree value methods')
        # data types  will be tested in special test

        # create test trees
        itree_root = iTree('root', subtree=[iTree('sub_int', 3),
                                            iTree('sub_dict', {'mykey': 1, 'mykey2': 2}),
                                            iTree('sub_list', [1, 2, 3]),
                                            iTree()
                                            ])

        # check if value equal works
        mycopy = itree_root.copy()
        assert mycopy == itree_root
        del mycopy[2].get_value()[0]
        assert mycopy != itree_root
        mycopy = itree_root.copy()
        del mycopy[1].get_value()['mykey']
        assert mycopy != itree_root

        # but we do some tests on the value

        # value property
        assert itree_root[0].value == 3
        assert itree_root[3].value is NoValue

        # get_value()
        assert itree_root[0].get_value() == 3

        # get_key_value()

        with pytest.raises(TypeError):
            itree_root[0].get_key_value('mykey')
        with pytest.raises(TypeError):
            itree_root[0].get_key_value(key='mykey')
        # dict in value
        assert itree_root[1].get_value() == {'mykey': 1, 'mykey2': 2}
        assert itree_root[1].get_key_value('mykey') == 1
        assert itree_root[1].get_key_value(key='mykey2') == 2
        # list in value
        assert itree_root[2].get_value() == [1, 2, 3]
        assert itree_root[2].get_key_value(0) == 1
        assert itree_root[2].get_key_value(key=1) == 2
        assert itree_root[2].get_key_value(-1) == 3
        # slices are possible too
        assert itree_root[2].get_key_value(key=slice(1, 3)) == [2, 3]
        if np is not None:
            itree_root[3].set_value(np.array([[1, 2, 3], [4, 5, 6]]))
            assert any(itree_root[3].get_key_value(0) == np.array([1, 2, 3]))
            assert any(itree_root[3].get_key_value(1) == np.array([4, 5, 6]))
            assert itree_root[3].get_key_value(0)[1] == 2

        # set_value
        # negative test
        with pytest.raises(TypeError):
            itree_root[0].set_key_value(key='mykey', value=1)

        # set any kind of object as value
        assert 3 == itree_root[0].set_value(Exception)
        assert itree_root[0].value is Exception
        # dict in value
        assert NoValue == itree_root[1].set_key_value('new_key', 6)
        assert itree_root[1].get_key_value('new_key') == 6
        assert 1 == itree_root[1].set_key_value('mykey', 10)
        assert itree_root[1].get_key_value('mykey') == 10
        assert len(itree_root[1].value) == 3
        # list in value
        assert NoValue == itree_root[2].set_key_value(INF, 6)  # None key is used for append
        with pytest.raises(IndexError):
            itree_root[2].set_key_value(1000, 7)  # index out of range is used for append
        assert len(itree_root[2].value) == 4
        assert itree_root[2].get_key_value(-1) == 6
        assert itree_root[2].get_key_value(-2) == 3
        assert 2 == itree_root[2].set_key_value(1, 10)
        assert itree_root[2].get_key_value(1) == 10
        assert 6 == itree_root[2].set_key_value(-1, 16)
        assert itree_root[2].get_key_value(-1) == 16

        # delete values
        # dict
        v = itree_root[1].get_key_value('mykey')
        assert itree_root[1].del_key_value('mykey') == v
        with pytest.raises(KeyError):
            assert itree_root[1].get_key_value('mykey')
        # list
        v1 = itree_root[2].get_key_value(1)
        v2 = itree_root[2].get_key_value(2)
        assert itree_root[2].del_key_value(1) == v1
        assert itree_root[2].get_key_value(1) == v2
        # np -> del is not working on numpy arrays!
        if np is not None:
            with pytest.raises(AttributeError):
                itree_root[3].del_key_value(0)
        # full delete
        v = itree_root[2].value
        assert itree_root[2].del_value() == v
        assert itree_root[2].value is NoValue
        v = itree_root[1].value
        assert itree_root[1].del_value() == v
        assert itree_root[1].value is NoValue
        v = itree_root[0].value
        assert itree_root[0].del_value() == v
        assert itree_root[0].value is NoValue

        # models
        model = Data.iTAnyValueModel()
        item = itree_root[0]
        v = item.get_value()
        assert item.set_value(model) == v
        assert item.set_value(1)
        assert item.value is model
        assert item.get_value() == 1
        item.value.clear()
        assert item.value is model
        assert item.del_value()
        assert item.value is NoValue

        model = Data.iTAnyValueModel()
        item = itree_root[1]
        item.set_value({'model': model})
        assert item.set_key_value('model', 1) is NoValue
        assert item.get_key_value('model') == 1

        model = Data.iTAnyValueModel()
        item = itree_root[2]
        item.set_value([1, model])
        assert item.set_key_value(1, 100) is NoValue
        assert item.get_key_value(1) == 100

        print('\nRESULT OF TEST: iTree value methods-> PASS')

    def test8_iTree_other_methods(self):
        if not 8 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree other methods')
        largetree, size = self.large_itree([10000, 2], ['tag_it'], 'cnt')

        # do some tests on count and len
        assert len(largetree) == 10000
        assert len(largetree.deep) == size

        myfilter = lambda i: type(i.value) is int and i.value <= 100
        for i in largetree:
            if i.value > 100:
                break
        assert largetree.filtered_len(myfilter) == i.idx
        myfilter = lambda i: i.value > 100
        assert largetree.filtered_len(myfilter) == len(largetree) - i.idx
        myfilter = lambda i: False
        assert largetree.filtered_len(myfilter) == 0
        myfilter = lambda i: True
        assert largetree.filtered_len(myfilter) == len(largetree)

        # do some tests on count_deep
        assert len(largetree.deep) == size
        myfilter = lambda i: type(i.value) is int and i.value <= 1000
        assert sum(1 for _ in filter(myfilter, largetree.deep)) == 1000
        assert largetree.deep.filtered_len(myfilter, True) == 1000
        assert largetree.deep.filtered_len(myfilter, False) == 1000

        myfilter = lambda i: type(i.value) is int and i.value > 1000
        assert largetree.deep.filtered_len(myfilter, True) == size - 1001 - 1
        assert largetree.deep.filtered_len(myfilter, False) == size - 1000
        assert sum(1 for _ in filter(myfilter, largetree.deep)) == size - 1000
        myfilter = lambda i: False
        assert largetree.deep.filtered_len(myfilter, True) == 0
        assert largetree.deep.filtered_len(myfilter, False) == 0
        assert sum(1 for _ in filter(myfilter, largetree.deep)) == 0
        myfilter = lambda i: True
        assert largetree.deep.filtered_len(myfilter, True) == size
        assert largetree.deep.filtered_len(myfilter, False) == size
        assert sum(1 for _ in filter(myfilter, largetree.deep)) == size
        print('\nRESULT OF TEST: iTree other methods-> PASS')

    def test9_math_operations_iTree(self):
        if not 9 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: math operations with iTrees')

        root = iTree('root', 'value')
        # multiplication with integer
        multi_tree = 1000 * root
        assert multi_tree.tag == NoTag
        assert multi_tree.value == NoValue
        for i in multi_tree:
            assert i == root
            assert i is not root
        multi_tree.rename('multi')
        multi_tree.set_value('multi')

        root2 = iTree('root2', 'value2')
        multi2 = 1000 * root2
        a = iTree('a')
        b = iTree('b')
        for i in range(10):
            a.append(iTree('a', i))
            b.append(iTree('b', i))

        c = a * b

        # multiplication in between two itree objects
        multi_both = multi_tree * multi2  # the resulting tree is quite large!
        print('Len multi_both: %i' % len(multi_both))
        assert multi_both.tag == multi_tree.tag
        assert multi_both.value == multi_tree.value
        assert len(multi_both) == len(multi_tree) * len(multi2) * 2  # ToDo why two times ?
        # we do not do here a deeper check because this goes back to itertools function product/chain

        # check some size related compare operations
        assert multi_both > multi_tree
        assert multi_both >= multi_tree
        assert multi_tree < multi_both
        assert multi_tree <= multi_both
        assert multi_tree <= multi2
        assert multi_tree >= multi2
        assert not multi_tree < multi2
        assert not multi_tree > multi2

        # addition of two iTrees:
        add_both = multi_tree + multi2
        assert add_both.tag == multi_tree.tag
        assert add_both.value == multi_tree.value

        assert len(add_both) == len(multi_tree) + len(multi2)
        for i, item in enumerate(add_both):
            if i < 1000:
                assert item == multi_tree[i]
                assert item is not multi_tree[i]
            else:
                i = i - 1000
                assert item == multi2[i]
                assert item is not multi2[i]

        # substraction
        empty_tree = add_both - add_both
        assert len(empty_tree) == 0
        assert empty_tree.tag == NoTag
        assert empty_tree.value == NoValue

        print('\nRESULT OF TEST: math operations with iTrees - pass')

    def test10_contains_operations_iTree(self):
        print('\nRESULT OF TEST: contains operations with iTrees')
        # build an test tree
        root = iTree('root', 0, subtree=[iTree(0, 0), iTree(1, 1), iTree(2, 2), iTree(3, 3), iTree(4, 4), iTree(4, 4)])
        for i in root:
            i.extend([iTree(0, 0), iTree(1, 1), iTree(2, 2), iTree(3, 3), iTree(4, 4), iTree(4, 5)])
        test_item = root[3].append(iTree('test'))

        # inside
        not_in_item = iTree(4, 4, [iTree(0, 0), iTree(1, 1), iTree(2, 2), iTree(3, 3), iTree(4, 4), iTree(4, 5)])
        assert root.is_in(root[3])
        assert not root.is_in(not_in_item)
        assert root.is_tag_in(0)
        assert root.is_tag_in(1)
        assert root.is_tag_in(2)
        assert root.is_tag_in(3)
        assert root.is_tag_in(4)
        assert not root.is_tag_in(5)
        assert root[2] in root
        assert not_in_item in root  # equal

        # in depth
        assert root.deep.is_in(root[3][0])
        assert root.deep.is_in(test_item)
        assert not root.deep.is_in(not_in_item)
        assert not_in_item in root.deep
        assert root.deep.is_tag_in('test')
        assert not root.deep.is_tag_in(5)

        print('\nRESULT OF TEST: contains operations with iTrees - pass')
