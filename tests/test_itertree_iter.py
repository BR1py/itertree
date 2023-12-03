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
    # only needed in case of numpy arrays in data
    # for serializing the data
except:
    np = None

import pickle
import timeit
from types import GeneratorType
from collections import OrderedDict
from itertree import *
from itertree.itree_helpers import NoValue, NoTag, BLIST_ACTIVE
from itertree.itree_mathsets import mSetInterval

root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

TEST_SELECTION = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
# TEST_SELECTION={}

print('Test start')
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
    for _ in range(number):
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

    def test1_iTree_iterators(self):
        # filters are tested in a special test
        if not 1 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree iterators')
        # build a small tree
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
        itree_root[3] += iTree(413, 10)
        itree_root[3] += iTree(408, 11)  # %3=0

        my_filter1 = lambda i: int(i.tag) % 2 == 0
        my_filter2 = lambda i: (int(i.tag) % 3) == 0 and my_filter1(i)

        #itree_root.render()
        # iter children
        i = -1
        for i, item in enumerate(itree_root):
            assert itree_root[i] is item
        assert i == 3
        i = -1
        for i, item in enumerate(itree_root[3]):
            assert itree_root[3][i] is item
        assert i == 5
        i = -1
        for i, item in enumerate(itree_root[2]):
            assert itree_root[2][i] is item
        assert i == 3
        assert len(itree_root[2]) == i + 1
        assert len(itree_root[2]) == len(itree_root[2])

        # iter children filtered
        i = -1
        for i, item in enumerate(filter(my_filter1,itree_root[0])):
            assert int(item.tag) % 2 == 0
        assert i == 1

        assert itree_root[0].filtered_len(my_filter1) == i + 1

        i = -1
        for i, item in enumerate(filter(my_filter2,itree_root[3])):
            assert (item.tag) % 2 == 0 and (item.tag) % 3 == 0
        assert i == 0
        assert itree_root[3].filtered_len(my_filter2) == i + 1

        # iter tag_idx
        for i, tag_idx in enumerate(itree_root[3].keys()):
            assert type(tag_idx) is tuple
            assert len(tag_idx) == 2
            assert itree_root[3][tag_idx] is itree_root[3][i]

        # iter_deep no filter
        check_items = [
            itree_root[0],
            itree_root[0][0],
            itree_root[0][1],
            itree_root[0][2],
            itree_root[0][3],
            itree_root[1],
            itree_root[1][0],
            itree_root[1][1],
            itree_root[1][2],
            itree_root[1][3],
            itree_root[2],
            itree_root[2][0],
            itree_root[2][1],
            itree_root[2][2],
            itree_root[2][3],
            itree_root[3],
            itree_root[3][0],
            itree_root[3][1],
            itree_root[3][2],
            itree_root[3][3],
            itree_root[3][4],
            itree_root[3][5],
        ]

        i = -1
        for i, item in enumerate(itree_root.deep):
            assert item is check_items[i]
        i += 1
        assert i == len(check_items)
        assert len(itree_root.deep) == i

        # filtered iter deep with cut on no match
        i = -1
        for i, item in enumerate(itree_root.deep.iter(my_filter1)):
            assert int(item.tag) % 2 == 0
        assert i == 5
        assert itree_root.deep.filtered_len(my_filter1, True) == i + 1

        # filtered iter deep with all matches
        i = -1
        for i, item in enumerate(filter(my_filter1, itree_root.deep)):
            assert int(item.tag) % 2 == 0
        assert i == 10
        assert itree_root.deep.filtered_len(my_filter1, False) == i + 1

        # idx lists
        i = -1
        for i, (idx_path,_) in enumerate(itree_root.deep.idx_paths()):
            assert itree_root.get(*idx_path) is check_items[i]
        assert i == len(check_items) - 1

        # tag_idx lists
        i = -1
        for i, (key_path,_) in enumerate(itree_root.deep.tag_idx_paths()):
            assert itree_root.get(*key_path) is check_items[i]
        assert i == len(check_items) - 1


        # check other deep iterators related to filters
        # hierarchical filtering
        i = -1
        for i, (idx_path,item) in enumerate(itree_root.deep.idx_paths(my_filter1)):
            pass
        assert i == 5
        # non hierachical filtering
        i = -1
        for i, item in enumerate(filter(lambda i: my_filter1(i[1]), itree_root.deep.idx_paths())):
            pass
        assert i == 10

        i = -1
        for i, item in enumerate(itree_root.deep.tag_idx_paths(my_filter1)):
            pass
        assert i == 5
        # filtered iter deep with all matches
        i = -1
        for i, item in enumerate(filter(lambda i: my_filter1(i[1]), itree_root.deep.tag_idx_paths())):
            pass
        assert i == 10

        # we create additional levels
        itree_root[3][0] += iTree(510, 6)
        itree_root[3][0] += iTree(511, 6)

        # dict related iterators
        for i, k in zip(itree_root, itree_root.keys()):
            assert i.tag_idx == k

        for i, v in zip(itree_root, itree_root.values()):
            assert i.value == v

        my_dict = OrderedDict(
            itree_root.items(values_only=True))  # we use ordered dict to be sure this works in all python versions
        assert len(itree_root) == len(my_dict)
        for i, ii in zip(itree_root, my_dict.items()):
            assert i.tag_idx == ii[0]
            assert i.value == ii[1]
        my_dict = OrderedDict(
            itree_root.items())  # we use ordered dict to be sure this works in all python versions
        assert len(itree_root) == len(my_dict)

        for i, ii in zip(itree_root, my_dict.items()):
            assert i.tag_idx == ii[0]
            assert i is ii[1]

        my_dict = OrderedDict([(key,i.value) for key,i in itree_root.deep.tag_idx_paths()])
        #  we use ordered dict to be sure this works in all python versions
        assert len(itree_root.deep) == len(my_dict)
        for i, ii in zip(itree_root.deep, my_dict.items()):
            assert i.tag_idx_path == ii[0]
            assert i.value == ii[1]

        my_dict = OrderedDict(itree_root.deep.tag_idx_paths())
        #  we use ordered dict to be sure this works in all python versions
        assert len(itree_root.deep) == len(my_dict)
        for i, ii in zip(itree_root.deep, my_dict.items()):
            assert i.tag_idx_path == ii[0]
            assert i is ii[1]

        #iter family
        itree_root.extend(iTree(itree_root[0].tag)*100)
        assert len(itree_root[{itree_root[0].tag}])==101
        assert len(itree_root.get.by_tag(itree_root[0].tag)) == 101
        assert len(list(itree_root[0].tags())) == itree_root.tag_number
        assert len(list(filter(lambda i: i.value==NoValue, itree_root.get.by_tag(itree_root[0].tag)))) == 100

        # ToDo large tree iterations of all types of iterators

        print('\nRESULT OF TEST: iTree iterators-> PASS')

    def test1b_iTree_iterators_first_level_only(self):
        # filters are tested in a special test
        if not 1 in TEST_SELECTION:
            return
        print('\nRUN: iTree iterators (first level only)')
        low_level_size = 1002
        low_level_size2 = int(low_level_size / 6)
        timeit_number = 10

        tree, size = self.large_itree([1, 2, low_level_size], ['cnt', 'mytag'], 'cnt')
        # create a deep tree
        tree2=iTree('root')
        sub=tree2
        for i in range(1000): # depth 1000!
            sub_tree=iTree('sub',i+1)*10
            sub=sub.append(sub_tree)

        # tree.render()

        test_filter = lambda i: bool(i.value % 2)
        # normal iter children
        i = i0 = tree[0][0][0].value
        i2 = 0
        for item in tree[0][0]:
            assert item.value == i
            if i % 2:
                assert item.tag == i2
                i2 += 1
            else:
                assert item.tag == 'mytag'
            i += 1
        assert i == low_level_size * 2 + i0
        s = len([i for i in tree[0][0]])
        compare_list = [iTree()] * s
        t = calc_timeit(lambda: [i for i in compare_list], number=timeit_number)
        print('normal list -> iteration-time over %s items: %es' % (s, t))

        # iter
        i = i0 = tree[0][0][0].value
        i2 = 0
        for item in tree[0][0]:
            assert item.value == i
            if i % 2:
                assert item.tag == i2
                i2 += 1
            else:
                assert item.tag == 'mytag'
            i += 1
        assert i == low_level_size * 2 + i0

        iter_method = tree[0][0].__iter__
        method_name = '__iter__'
        s = len([i for i in iter_method()])
        t = calc_timeit(lambda: [i for i in iter_method()], number=timeit_number)
        print('%s() -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in filter(lambda i: True,iter_method())])
        t = calc_timeit(lambda: [i for i in filter(lambda i: True,iter_method())], number=timeit_number)
        print('filter(lambda i: True,%s()) (always true) -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in filter(test_filter,iter_method())])
        t = calc_timeit(lambda: [i for i in filter(test_filter,iter_method())], number=timeit_number)
        print('filter(test_filter,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        # keys
        i = i0 = tree[0][0][0].value
        i2 = 0
        i3 = 0

        for key in tree[0][0].keys():
            if i % 2:
                assert key == (i2, 0)
                i2 += 1
            else:

                assert key == ('mytag', i3)
                i3 += 1
            i += 1
        assert i == low_level_size * 2 + i0

        iter_method = tree[0][0].keys
        method_name = 'keys'
        s = len([i for i in iter_method()])
        t = calc_timeit(lambda: [i for i in iter_method()], number=timeit_number)
        print('%s() -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in iter_method(lambda i: True)])
        t = calc_timeit(lambda: [i for i in iter_method(lambda i: True)], number=timeit_number)
        print('%s(lambda i: True) (always true) -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in iter_method(test_filter)])
        t = calc_timeit(lambda: [i for i in iter_method(test_filter)], number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        # values
        i = i0 = tree[0][0][0].value

        for v in tree[0][0].values():
            assert v == i
            i += 1
        assert i == low_level_size * 2 + i0

        iter_method = tree[0][0].values
        method_name = 'values'
        s = len([i for i in iter_method()])
        t = calc_timeit(lambda: [i for i in iter_method()], number=timeit_number)
        print('%s() -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in iter_method(lambda i: True)])
        t = calc_timeit(lambda: [i for i in iter_method(lambda i: True)], number=timeit_number)
        print('%s(lambda i: True) (always true) -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in iter_method(test_filter)])
        t = calc_timeit(lambda: [i for i in iter_method(test_filter)], number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        # items with iTree items
        i = i0 = tree[0][0][0].value
        i2 = 0
        i3 = 0

        for key, v in tree[0][0].items():
            assert v.value == i
            if i % 2:
                assert key == (i2, 0)
                i2 += 1
            else:

                assert key == ('mytag', i3)
                i3 += 1
            i += 1
        assert i == low_level_size * 2 + i0

        # items with values
        i = i0 = tree[0][0][0].value
        i2 = 0
        i3 = 0

        for key, v in tree[0][0].items(values_only=True):
            assert v == i
            if i % 2:
                assert key == (i2, 0)
                i2 += 1
            else:

                assert key == ('mytag', i3)
                i3 += 1
            i += 1
        assert i == low_level_size * 2 + i0

        iter_method = tree[0][0].items
        method_name = 'items'
        s = len([i for i in iter_method(values_only=True)])
        t = calc_timeit(lambda: [i for i in iter_method(values_only=False)], number=timeit_number)
        print('%s() -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in iter_method(lambda i: True)])
        t = calc_timeit(lambda: [i for i in iter_method(filter_method=lambda i: True)], number=timeit_number)
        print('%s(lambda i: True) (always true) -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in iter_method(filter_method=test_filter, values_only=True)])
        t = calc_timeit(lambda: [i for i in iter_method(filter_method=test_filter,
                                                        values_only=False)], number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))
        s = len([i for i in iter_method(values_only=True)])
        t = calc_timeit(lambda: [i for i in iter_method(values_only=True)], number=timeit_number)
        print('%s() -> iteration-time over %s items (values_only): %es' % (method_name, s, t))
        s = len([i for i in iter_method(lambda i: True)])
        t = calc_timeit(lambda: [i for i in iter_method(values_only=True,filter_method=lambda i: True)], number=timeit_number)
        print('%s(lambda i: True) (always true) -> iteration-time over %s items (values_only): %es' % (method_name, s, t))
        s = len([i for i in iter_method(filter_method=test_filter, values_only=True)])
        t = calc_timeit(lambda: [i for i in iter_method(filter_method=test_filter,
                                                        values_only=True)], number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items (values_only): %es' % (method_name, s, t))


        # tags
        iter_method = tree[0][0].tags
        method_name = 'tags'
        a=[i for i in iter_method()]
        assert len(a)==tree[0][0].tag_number
        last=-1
        for i in a:
            item=tree[0][0].get.by_tag(i)[0]
            assert item.idx>last
            last=item.idx
        t = calc_timeit(lambda: [i for i in iter_method()], number=timeit_number)
        print('%s() -> iteration-time: %es (%i)' % (method_name, t,len(a)))

        a=[i for i in iter_method(True)]
        assert len(a)==tree[0][0].tag_number
        t = calc_timeit(lambda: [i for i in iter_method(True)], number=timeit_number)
        print('%s(order_last=True) -> iteration-time: %es (%i)' % (method_name, t,len(a)))

        # iter_families
        iter_method = tree[0][0].iter_families
        method_name = 'iter_families'
        a=[i for i in iter_method()]
        assert len(a)==tree[0][0].tag_number
        last = -1
        for i,ii in a:
            item = tree[0][0].get.by_tag(i)[0]
            assert item.idx > last
            assert ii == tree[0][0].get.by_tag(i)
            last = item.idx

        t = calc_timeit(lambda: [i for i in iter_method()], number=timeit_number)
        print('%s() -> iteration-time: %es (%i)' % (method_name, t,len(a)))

        a=[i for i in iter_method(None,True)]
        assert len(a)==tree[0][0].tag_number
        t = calc_timeit(lambda: [i for i in iter_method(None,True)], number=timeit_number)
        print('%s(order_last=True) -> iteration-time: %es (%i)' % (method_name, t,len(a)))

        # iter_family_items
        iter_method = tree[0][0].iter_family_items
        method_name = 'iter_family_items'
        a=[i for i in iter_method()]
        assert len(a)==len(tree[0][0])
        assert a[0].idx==0
        t = calc_timeit(lambda: [i for i in iter_method()], number=timeit_number)
        print('%s() -> iteration-time: %es (%i)' % (method_name, t,len(a)))

        iter_method = tree[0][0].iter_family_items
        method_name = 'iter_family_items'
        a=[i for i in iter_method(True)]
        assert len(a)==len(tree[0][0])
        t = calc_timeit(lambda: [i for i in iter_method(True)], number=timeit_number)
        print('%s(order_last=True) -> iteration-time: %es (%i)' % (method_name, t,len(a)))

        # get_init_args
        iter_method = tree[0][0].get_init_args
        method_name = 'get_init_args'
        t = calc_timeit(lambda: [i for i in iter_method()], number=timeit_number)
        print('%s() -> iteration-time: %es' % (method_name, t))
        t = calc_timeit(lambda: [i for i in iter_method(test_filter)], number=timeit_number)
        print('%s(test_filter) -> iteration-time: %es' % (method_name, t))

        print('\nRESULT OF TEST: iTree iterators (first level) -> PASS')


    def test1c_iTree_iterators_deep(self):
        # filters are tested in a special test
        if not 1 in TEST_SELECTION:
            return
        print('\nRUN: iTree deep iterators')
        low_level_size = 1002
        low_level_size2 = int(low_level_size / 6)
        timeit_number = 10

        tree, size = self.large_itree([1, 2, low_level_size], ['cnt', 'mytag'], 'cnt')
        # create a deep tree
        tree2=iTree('root')
        sub=tree2
        depth2=1000
        for i in range(depth2): # depth 1000!
            sub_tree=iTree('sub',i+1)*10
            sub=sub.append(sub_tree)
        size2=len(tree2.deep)

        # tree.render()

        test_filter = lambda i: bool(i.value % 2)

        permutation_flags = [(None, False, False),
                             (None, True, False),
                             (None, False, True),
                             (None, True, True),
                             (test_filter, False, False),
                             (test_filter, True, False),
                             (test_filter, False, True),
                             (test_filter, True, True)
                             ]

        # timeit copy which uses internal iterator
        t = calc_timeit(lambda: tree.copy(), number=timeit_number)
        print('copy() -> (normal tree: %s items (depth %s)) internal iteration-time (incl. re-instance objects): %es' % (size,tree.max_depth,t))
        t = calc_timeit(lambda: tree2.copy(), number=timeit_number)
        print('copy() (deep_tree: %s items (depth %s)) -> internal iteration-time (incl. re-instance objects) : %es' % (size2,depth2,t))

        print('\nin-depth operator top->down:\n')

        # standard iter_deep
        i = 1
        for item in tree.deep:
            assert item.value == i
            i += 1
        assert i == size + 1

        iter_method = tree.deep.__iter__
        method_name = 'iTree().deep.__iter__'
        s = len([i for i in iter_method()])

        compare_list = [iTree(i) for i in range(s)]
        t = calc_timeit(lambda: [i for i in compare_list], number=timeit_number)
        print('normal list (flat) -> iteration-time over %s items: %es' % (s, t))

        s = len(list(i for i in iter_method()))
        # manipulate last item to get in update path!
        t1 = t = calc_timeit(lambda: list(i for i in iter_method()), number=timeit_number) 
        print('%s()-> iteration-time over %s items: %es' % (method_name, s, t))


        iter_method = tree.deep.iter
        method_name = 'tree.deep.iter'
        s = len(list(i for i in iter_method()))
        # manipulate last item to get in update path!
        t1 = t = calc_timeit(lambda: list(i for i in iter_method()), number=timeit_number)
        print('%s()-> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(lambda i: True)))
        t = calc_timeit(lambda: list(i for i in iter_method(lambda i: True)), number=timeit_number)
        print('%s(lambda i: True) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(lambda i: True, iter_method())))
        t = calc_timeit(lambda: list(i for i in filter(lambda i: True, iter_method())), number=timeit_number)
        print('filter(lambda i: True,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(test_filter)))
        t = calc_timeit(lambda: list(i for i in iter_method(test_filter)), number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(test_filter,iter_method())))
        t = calc_timeit(lambda: list(i for i in filter(test_filter,iter_method())), number=timeit_number)
        print('filter(test_filter,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))


        iter_method = tree2.deep.iter
        method_name = 'tree2.deep.iter'
        s = len([i for i in iter_method()])

        compare_list = [iTree(i) for i in range(s)]
        t = calc_timeit(lambda: [i for i in compare_list], number=timeit_number)
        print('\nnormal list (flat) -> iteration-time over %s items: %es' % (s, t))


        s = len(list(i for i in iter_method()))
        # manipulate last item to get in update path!
        t1 = t = calc_timeit(lambda: list(i for i in iter_method()), number=timeit_number)
        print('%s()-> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(lambda i: True)))
        t = calc_timeit(lambda: list(i for i in iter_method(lambda i: True)), number=timeit_number)
        print('%s(lambda i: True) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(lambda i: True, iter_method())))
        t = calc_timeit(lambda: list(i for i in filter(lambda i: True, iter_method())), number=timeit_number)
        print('filter(lambda i: True,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(test_filter)))
        t = calc_timeit(lambda: list(i for i in iter_method(test_filter)), number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(test_filter,iter_method())))
        t = calc_timeit(lambda: list(i for i in filter(test_filter,iter_method())), number=timeit_number)
        print('filter(test_filter,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))


        # standard iter_deep
        i = 1
        item_list = list(tree.deep.iter(up_to_low=False))
        #for i in item_list:
        #    print(i)
        assert len(item_list) == size
        # we check some items to see if bottom -> up structure is fine
        assert item_list[0] is tree[0][0][0]
        assert item_list[low_level_size * 2] is tree[0][0]
        assert item_list[low_level_size * 4 + 1] is tree[0][1]
        assert item_list[-1] is tree[-1]

        print('\nin-depth iterator: bottom->up\n')

        iter_method = tree.deep.iter
        method_name = 'tree.deep.iter'

        s = len(list(i for i in iter_method(up_to_low=False)))
        t = calc_timeit(lambda: list(i for i in iter_method(up_to_low=False)), number=timeit_number)
        print('%s(top_down=False) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(lambda i: True,up_to_low=False)))
        t = calc_timeit(lambda: list(i for i in iter_method(lambda i: True,up_to_low=False)), number=timeit_number)
        print('%s(lambda i: True) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(lambda i: True, iter_method(up_to_low=False))))
        t = calc_timeit(lambda: list(i for i in filter(lambda i: True, iter_method(up_to_low=False))), number=timeit_number)
        print('filter(lambda i: True,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(test_filter,up_to_low=False)))
        t = calc_timeit(lambda: list(i for i in iter_method(test_filter,up_to_low=False)), number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(test_filter,iter_method(up_to_low=False))))
        t = calc_timeit(lambda: list(i for i in filter(test_filter,iter_method(up_to_low=False))), number=timeit_number)
        print('filter(test_filter,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))


        iter_method = tree2.deep.iter_family_items
        method_name = 'tree2.deep.iter_family_items'
        s = len([i for i in iter_method()])
        # manipulate last item to get in update path!
        t1 = t = calc_timeit(lambda: list(i for i in iter_method()), number=timeit_number)
        print('%s()-> iteration-time over %s items: %es' % (method_name, s, t))


        print('\nRESULT OF TEST: iTree deep iterators -> PASS')

    def test1d_iTree_iterators_idx_paths(self):
        # filters are tested in a special test
        if not 1 in TEST_SELECTION:
            return
        print('\nRUN: iTree deep idx_paths iterators')
        low_level_size = 1002
        low_level_size2 = int(low_level_size / 6)
        timeit_number = 10

        tree, size = self.large_itree([1, 2, low_level_size], ['cnt', 'mytag'], 'cnt')
        # create a deep tree
        tree2=iTree('root')
        sub=tree2
        for i in range(1000): # depth 1000!
            sub_tree=iTree('sub',i+1)*10
            sub=sub.append(sub_tree)

        # tree.render()

        test_filter = lambda i: bool(i.value % 2)
        test_filter_outside = lambda i: bool(i[1].value % 2)

        # idx_paths()

        # check all items based on All.iter()
        for (idx_path,_), item in zip(tree.deep.idx_paths(), tree.deep.iter()):
            assert idx_path == item.idx_path, 'Issue in item %s' % (item)
        for (idx_path,_), item in zip(tree.deep.idx_paths(test_filter), tree.deep.iter(test_filter)):
            assert idx_path == item.idx_path, 'Issue in item %s' % (item)
        for (idx_path,_), item in zip(filter(lambda i: test_filter(i[1]), tree.deep.idx_paths()),
                                      filter(test_filter, tree.deep.iter())):
            assert idx_path == item.idx_path, 'Issue in item %s' % (item)
        for (idx_path,_), item in zip(tree.deep.idx_paths(up_to_low=False), tree.deep.iter(up_to_low=False)):
            assert idx_path == item.idx_path, 'Issue in item %s' % (item)
        for (idx_path,_), item in zip(tree.deep.idx_paths(test_filter, up_to_low=False), tree.deep.iter(test_filter, up_to_low=False)):
            assert idx_path == item.idx_path, 'Issue in item %s' % (item)
        for (idx_path,_), item in zip(filter(lambda i: test_filter(i[1]), tree.deep.idx_paths(up_to_low=False)),
                                      filter(test_filter, tree.deep.iter(up_to_low=False))):
            assert idx_path == item.idx_path, 'Issue in item %s' % (item)

        print('.deep.idx_paths() -> all parameter combinations check with success!')

        print('\n.deep.idx_paths() top->down:\n')

        iter_method = tree.deep.idx_paths
        method_name = 'tree.deep.idx_paths'

        s = len(list(i for i in iter_method()))
        # manipulate last item to get in update path!
        t1 = t = calc_timeit(lambda: list(i for i in iter_method()), number=timeit_number)
        print('%s()-> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(lambda i: True)))
        t = calc_timeit(lambda: list(i for i in iter_method(lambda i: True)), number=timeit_number)
        print('%s(lambda i: True) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(lambda i: True, iter_method())))
        t = calc_timeit(lambda: list(i for i in filter(lambda i: True, iter_method())), number=timeit_number)
        print('filter(lambda i: True,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(test_filter)))
        t = calc_timeit(lambda: list(i for i in iter_method(test_filter)), number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(test_filter_outside,iter_method())))
        t = calc_timeit(lambda: list(i for i in filter(test_filter_outside,iter_method())), number=timeit_number)
        print('filter(test_filter,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))


        print('\n.deep.idx_paths(): bottom->up\n')

        iter_method = tree.deep.idx_paths
        method_name = 'tree.deep.idx_paths'

        s = len(list(i for i in iter_method()))
        # manipulate last item to get in update path!
        t1 = t = calc_timeit(lambda: list(i for i in iter_method(up_to_low=True)), number=timeit_number)
        print('%s()-> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(lambda i: True,up_to_low=True)))
        t = calc_timeit(lambda: list(i for i in iter_method(lambda i: True,up_to_low=True)), number=timeit_number)
        print('%s(lambda i: True) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(lambda i: True, iter_method(up_to_low=True))))
        t = calc_timeit(lambda: list(i for i in filter(lambda i: True, iter_method(up_to_low=True))), number=timeit_number)
        print('filter(lambda i: True,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(test_filter,up_to_low=True)))
        t = calc_timeit(lambda: list(i for i in iter_method(test_filter,up_to_low=True)), number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(test_filter_outside,iter_method(up_to_low=True))))
        t = calc_timeit(lambda: list(i for i in filter(test_filter_outside,iter_method(up_to_low=True))), number=timeit_number)
        print('filter(test_filter,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))


        print('\nRESULT OF TEST: iTree deep idx_paths iterators -> PASS')

    def test1e_iTree_iterators_key_paths(self):
        # filters are tested in a special test
        print('\nRUN: iTree deep key_paths iterators')
        low_level_size = 1002
        low_level_size2 = int(low_level_size / 6)
        timeit_number = 10

        tree, size = self.large_itree([1, 2, low_level_size], ['cnt', 'mytag'], 'cnt')
        # create a deep tree
        tree2 = iTree('root')
        sub = tree2
        for i in range(1000):  # depth 1000!
            sub_tree = iTree('sub', i + 1) * 10
            sub = sub.append(sub_tree)

        # tree.render()

        test_filter = lambda i: bool(i.value % 2)
        test_filter_outside = lambda i: bool(i[1].value % 2)

        # key_paths()

        # check all items based on All.iter()
        for (key_path,_), item in zip(tree.deep.tag_idx_paths(), tree.deep.iter()):
            assert key_path == item.tag_idx_path, 'Issue in item %s' % (item)
        for (key_path,_), item in zip(tree.deep.tag_idx_paths(test_filter), tree.deep.iter(test_filter)):
            assert key_path == item.tag_idx_path, 'Issue in item %s' % (item)
        for (key_path,_), item in zip(filter(lambda i: test_filter(i[1]), tree.deep.tag_idx_paths()),
                                      filter(test_filter, tree.deep.iter())):
            assert key_path == item.tag_idx_path, 'Issue in item %s' % (item)
        for (key_path,_), item in zip(tree.deep.tag_idx_paths(up_to_low=False), tree.deep.iter(up_to_low=False)):
            assert key_path == item.tag_idx_path, 'Issue in item %s' % (item)
        for (key_path,_), item in zip(tree.deep.tag_idx_paths(test_filter, up_to_low=False), tree.deep.iter(test_filter, up_to_low=False)):
            assert key_path == item.tag_idx_path, 'Issue in item %s' % (item)
        for (key_path,_), item in zip(filter(lambda i: test_filter(i[1]), tree.deep.tag_idx_paths(up_to_low=False)),
                                      filter(test_filter, tree.deep.iter(up_to_low=False))):
            assert key_path == item.tag_idx_path, 'Issue in item %s' % (item)

        print('.deep.key_paths() -> all parameter combinations check with success!')

        print('\n.deep.key_paths() top->down:\n')

        iter_method = tree.deep.tag_idx_paths
        method_name = 'tree.deep.key_paths'

        s = len(list(i for i in iter_method()))
        # manipulate last item to get in update path!
        t1 = t = calc_timeit(lambda: list(i for i in iter_method()), number=timeit_number)
        print('%s()-> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(lambda i: True)))
        t = calc_timeit(lambda: list(i for i in iter_method(lambda i: True)), number=timeit_number)
        print('%s(lambda i: True) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(lambda i: True, iter_method())))
        t = calc_timeit(lambda: list(i for i in filter(lambda i: True, iter_method())), number=timeit_number)
        print('filter(lambda i: True,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(test_filter)))
        t = calc_timeit(lambda: list(i for i in iter_method(test_filter)), number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(test_filter_outside,iter_method())))
        t = calc_timeit(lambda: list(i for i in filter(test_filter_outside,iter_method())), number=timeit_number)
        print('filter(test_filter,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))


        print('\n.deep.key_paths(): bottom->up\n')

        iter_method = tree.deep.tag_idx_paths
        method_name = 'tree.deep.key_paths'

        s = len(list(i for i in iter_method()))
        # manipulate last item to get in update path!
        t1 = t = calc_timeit(lambda: list(i for i in iter_method(up_to_low=True)), number=timeit_number)
        print('%s()-> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(lambda i: True,up_to_low=True)))
        t = calc_timeit(lambda: list(i for i in iter_method(lambda i: True,up_to_low=True)), number=timeit_number)
        print('%s(lambda i: True) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(lambda i: True, iter_method(up_to_low=True))))
        t = calc_timeit(lambda: list(i for i in filter(lambda i: True, iter_method(up_to_low=True))), number=timeit_number)
        print('filter(lambda i: True,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in iter_method(test_filter,up_to_low=True)))
        t = calc_timeit(lambda: list(i for i in iter_method(test_filter,up_to_low=True)), number=timeit_number)
        print('%s(test_filter) -> iteration-time over %s items: %es' % (method_name, s, t))

        s = len(list(i for i in filter(test_filter_outside,iter_method(up_to_low=True))))
        t = calc_timeit(lambda: list(i for i in filter(test_filter_outside,iter_method(up_to_low=True))), number=timeit_number)
        print('filter(test_filter,%s()) -> iteration-time over %s items: %es' % (method_name, s, t))

        print('\nRESULT OF TEST: iTree deep key_paths iterators -> PASS')

    def test2_iTree_unit_filters(self):
        # filters are tested in a special test
        if not 2 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree unit test filters')
        # iTFilter class

        # normal definitions
        f = lambda i: i.tag == 'mytag'
        assert f(iTree('mytag'))
        assert not f(iTree('not_mytag'))

        # definition containg arguments
        f = lambda i: i.tag == 'mytag'
        assert f(iTree('mytag'))
        assert not f(iTree('not_mytag'))

        # cascaded with OR
        f2 = lambda i: i.value == 1 or f(i)
        assert f2(iTree('mytag'))
        assert not f2(iTree('not_mytag'))
        assert f2(iTree('not_mytag', 1))
        assert f2(iTree('mytag', 1))
        assert f2(iTree(value=1))
        assert not f2(iTree())

        # cascaded with AND
        f2 = lambda i: i.value == 1 and f(i)
        assert not f2(iTree('mytag'))
        assert not f2(iTree('not_mytag', 1))
        assert f2(iTree('mytag', 1))

        # ToDo multiple OR and AND and mixed with brackets

        print('\nRESULT OF TEST: iTree unit test filters-> PASS')

    def test3_iTree_filters_methods(self):
        # filters are tested in a special test
        if not 3 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree unit test filters')

        assert Filters.has_item_flags(iTFLAG.READ_ONLY_VALUE)(iTree(flags=iTFLAG.READ_ONLY_VALUE), )
        assert not Filters.has_item_flags(iTFLAG.READ_ONLY_VALUE)(iTree(flags=iTFLAG.READ_ONLY_TREE))
        assert Filters.has_item_flags( iTFLAG.READ_ONLY_VALUE | iTFLAG.READ_ONLY_TREE)(iTree(flags=iTFLAG.READ_ONLY_VALUE))
        assert Filters.has_item_flags(iTFLAG.READ_ONLY_VALUE | iTFLAG.READ_ONLY_TREE)(iTree(flags=iTFLAG.READ_ONLY_TREE))
        assert not Filters.has_item_flags( iTFLAG.READ_ONLY_VALUE | iTFLAG.READ_ONLY_TREE)(iTree())

        assert Filters.is_item_tag( 'mykey')(iTree('mykey'))
        assert Filters.is_item_tag( NoTag)(iTree())
        assert Filters.is_item_tag( (1, 2, 3, 4))(iTree((1, 2, 3, 4)))
        assert not Filters.is_item_tag( 'mykey')(iTree())

        assert Filters.has_item_tag_fnmatch( 'mykey')(iTree('mykey'))
        assert Filters.has_item_tag_fnmatch( '*key')(iTree('mykey'))
        assert Filters.has_item_tag_fnmatch( '*ke*')(iTree('mykey'))
        assert Filters.has_item_tag_fnmatch('*ke?')(iTree('mykey'))
        assert not Filters.has_item_tag_fnmatch( '*ke?')(iTree('mykey2'))
        assert not Filters.has_item_tag_fnmatch( '*ke?')(iTree())
        assert not Filters.has_item_tag_fnmatch( '*ke?')(iTree(1))

        assert Filters.has_item_value( 'myvalue')(iTree(value='myvalue'))
        assert Filters.has_item_value(1)(iTree(value=1))
        assert not Filters.has_item_value( 1)(iTree())
        assert Filters.has_item_value( [1, 2, 3])(iTree(value=[1, 2, 3]))
        assert not Filters.has_item_value( [1, 2])(iTree(value=[1, 2, 3]))
        assert not Filters.has_item_value( [1, 2])(iTree(value=[1]))
        assert not Filters.has_item_value( [1, 2])(iTree(value=[]))
        if np is not None:
            assert Filters.has_item_value( np.array([1, 2, 3]))(iTree(value=np.array([1, 2, 3])))
            assert not Filters.has_item_value( np.array([1, 2]))(iTree(value=np.array([1, 2, 3])))
            assert not Filters.has_item_value( [1, 2, 3])(iTree(value=np.array([1, 2, 3])))

        assert Filters.has_item_value_fnmatch( 'myvalue')(iTree(value='myvalue'))
        assert Filters.has_item_value_fnmatch( '*value')(iTree(value='myvalue'))
        assert Filters.has_item_value_fnmatch( '*valu?')(iTree(value='myvalue'))
        assert not Filters.has_item_value_fnmatch('*value')(iTree(value='myvalue2'))
        assert not Filters.has_item_value_fnmatch( '*value')(iTree(value=1))
        assert not Filters.has_item_value_fnmatch( '*value')(iTree(value=b'myvalue'))

        assert not Filters.is_item_value_in( mSetInterval(0, 100))(iTree(value='myvalue'))
        assert not Filters.is_item_value_in( mSetInterval(0, 100))(iTree(value=-1))
        assert not Filters.is_item_value_in(mSetInterval(0, 100))(iTree(value=101))
        assert Filters.is_item_value_in( mSetInterval(0, 100))(iTree(value=1))
        assert Filters.is_item_value_in( mSetInterval(0, 100))(iTree(value=99))
        assert not Filters.is_item_value_in( mSetInterval(0, 100))(iTree(value=[1, 99]))

        assert not Filters.has_item_value_dict_value( 'myvalue')(iTree(value='myvalue'))
        assert not Filters.has_item_value_dict_value( 'myvalue')(iTree(value=['myvalue']))
        assert not Filters.has_item_value_dict_value( 'myvalue')(iTree(value={'myvalue': 1}))
        assert Filters.has_item_value_dict_value( 'myvalue')(iTree(value={1: 'myvalue'}))

        assert Filters.has_item_value_dict_value_fnmatch( 'myvalue')(iTree(value={1: 'myvalue'}))
        assert Filters.has_item_value_dict_value_fnmatch( '*value')(iTree(value={2: 'myvalue'}))
        assert Filters.has_item_value_dict_value_fnmatch( '*valu?')(iTree(value={3: 'myvalue', 45: 'myvalue2'}))
        assert not Filters.has_item_value_dict_value_fnmatch( '*value')(iTree(value={45: 'myvalue2'}))
        assert not Filters.has_item_value_dict_value_fnmatch( '*value')(iTree(value={'myvalue': 1}))
        assert not Filters.has_item_value_dict_value_fnmatch( '*value')(iTree(value={1: b'myvalue'}))
        assert not Filters.has_item_value_dict_value_fnmatch( 'myvalue')(iTree(value='myvalue'))

        assert not Filters.has_item_value_dict_value_in( mSetInterval(0, 100))(iTree(value={1: 'myvalue'}))
        assert not Filters.has_item_value_dict_value_in( mSetInterval(0, 100))(iTree(value={1: -1}))
        assert not Filters.has_item_value_dict_value_in( mSetInterval(0, 100))(iTree(value={1: 101}))
        assert Filters.has_item_value_dict_value_in( mSetInterval(0, 100))(iTree(value={1: 200, 9: 1}))
        assert Filters.has_item_value_dict_value_in( mSetInterval(0, 100))(iTree(value={99: -100, 3: 99}))
        assert not Filters.has_item_value_dict_value_in( mSetInterval(0, 100))(iTree(value={1: [1, 99]}))
        assert not Filters.has_item_value_dict_value_in( mSetInterval(0, 100))(iTree(value=[1, 99]))
        assert not Filters.has_item_value_dict_value_in( mSetInterval(0, 100))(iTree(value=99))

        assert Filters.has_item_value_list_item_fnmatch( 'myvalue')(iTree(value=[1, 'myvalue']))
        assert Filters.has_item_value_list_item_fnmatch( '*value')(iTree(value=[2, 'myvalue']))
        assert Filters.has_item_value_list_item_fnmatch( '*valu?')(iTree(value=[3, 'myvalue', 45, 'myvalue2']))
        assert not Filters.has_item_value_list_item_fnmatch( '*value')(iTree(value=[45, 'myvalue2']))
        assert not Filters.has_item_value_list_item_fnmatch( '*value')(iTree(value=[1, b'myvalue']))
        assert not Filters.has_item_value_list_item_fnmatch( 'myvalue')(iTree(value='myvalue'))

        assert not Filters.has_item_value_list_item_in( mSetInterval(0, 100))(iTree(value=[1000, 'myvalue']))
        assert not Filters.has_item_value_list_item_in( mSetInterval(0, 100))(iTree(value=['1010', -1]))
        assert not Filters.has_item_value_list_item_in( mSetInterval(0, 100))(iTree(value=[-1, 101]))
        assert Filters.has_item_value_list_item_in( mSetInterval(0, 100))(iTree(value=[1, 200, 9, 1]))
        assert Filters.has_item_value_list_item_in( mSetInterval(0, 100))(iTree(value=[99, -100, 3, 99]))
        assert not Filters.has_item_value_list_item_in( mSetInterval(0, 100))(iTree(value=[-1, [1, 99]]))
        assert not Filters.has_item_value_list_item_in( mSetInterval(0, 100))(iTree(value=99))

        assert not Filters.has_item_value_dict_key( 'mykey')(iTree())
        assert not Filters.has_item_value_dict_key( 'mykey')(iTree(value=1))
        assert not Filters.has_item_value_dict_key( 'mykey')(iTree(value={1: 1}))
        assert not Filters.has_item_value_dict_key( 'mykey')(iTree(value=[1, 2, 3, 4]))
        assert Filters.has_item_value_dict_key( 'mykey')(iTree(value={'mykey': 1}))

        assert not Filters.has_item_value_list_idx( 2)(iTree())
        assert not Filters.has_item_value_list_idx( 2)(iTree(value=[1]))
        assert not Filters.has_item_value_list_idx( 0)(iTree(value={1: 1}))
        assert not Filters.has_item_value_list_idx( 10)(iTree(value=[1, 2, 3, 4]))
        assert not Filters.has_item_value_list_idx( -10)(iTree(value=[1, 2, 3, 4]))
        assert Filters.has_item_value_list_idx( 1)(iTree(value=[1, 2, 3, 4]))
        assert Filters.has_item_value_list_idx( -1)(iTree(value=[1, 2, 3, 4]))

        assert Filters.has_item_value_dict_key_fnmatch('myvalue')(iTree(value={'myvalue': 1}))
        assert Filters.has_item_value_dict_key_fnmatch('*value')(iTree(value={'myvalue': 2}))
        assert Filters.has_item_value_dict_key_fnmatch('*valu?')(iTree(value={'myvalue': 3, 'myvalue2': 45}))
        assert not Filters.has_item_value_dict_key_fnmatch('*value')(iTree(value={'myvalue2': 45}))
        assert not Filters.has_item_value_dict_key_fnmatch('*value')(iTree(value={1: 'myvalue'}))
        assert not Filters.has_item_value_dict_key_fnmatch('*value')(iTree(value={b'myvalue': 1}))
        assert not Filters.has_item_value_dict_key_fnmatch('myvalue')(iTree(value='myvalue'))

        assert not Filters.has_item_value_dict_key_in(mSetInterval(0, 100))(iTree(value={'myvalue': 1}))
        assert not Filters.has_item_value_dict_key_in(mSetInterval(0, 100))(iTree(value={-1: 1}))
        assert not Filters.has_item_value_dict_key_in(mSetInterval(0, 100))(iTree(value={101: 1}))
        assert Filters.has_item_value_dict_key_in(mSetInterval(0, 100))(iTree(value={200: 1, 1: 9}))
        assert Filters.has_item_value_dict_key_in(mSetInterval(0, 100))(iTree(value={-100: 99, 99: 3}))
        assert not Filters.has_item_value_dict_key_in(mSetInterval(0, 100))(iTree(value={(1, 99): 1}))
        assert not Filters.has_item_value_dict_key_in(mSetInterval(0, 100))(iTree(value=[1, 99]))
        assert not Filters.has_item_value_dict_key_in(mSetInterval(0, 100))(iTree(value=99))

        print('\nRESULT OF TEST: iTree unit test filters-> PASS')

    def test4_iTree_level_filters(self):
        # filters are tested in a special test
        if not 3 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree level filters in getters')
        tree, size = self.large_itree([1, 4, 4, 4], ['cnt'], 'cnt')
        # tree.render()

        filter1 = lambda i: i.value % 2 == 0
        filter2 = lambda i: i.value % 2 != 0

        print('even')
        result = list(tree.get(0, filter1))
        for i in result:
            # print(i)
            assert i.value % 2 == 0
        assert len(result) == 2

        print('odd')
        result = list(tree.get(*[0, filter2]))
        for i in result:
            # print(i)
            assert i.value % 2 != 0
        assert len(result) == 2

        print('level2 mixed')
        # deeper filtering
        result = list(tree.get(*[0, filter1, filter2]))
        for i in result:
            # print(i)
            assert i.value % 2 != 0
        assert len(result) == 2 * 2  # we expect two in first and two in second level

        print('level2 odd')
        # deeper filtering
        result = list(tree.get(*[0, filter1, filter1]))
        for i in result:
            # print(i)
            assert i.value % 2 == 0
        assert len(result) == 2 * 2  # we expect two in first and two in second level
        print('level2 even')
        # deeper filtering
        result = list(tree.get(0, filter2, filter2))
        for i in result:
            # print(i)
            assert i.value % 2 != 0
        assert len(result) == 2 * 2  # we expect two in first and two in second level

        print('level2 mixed')
        # deeper filtering
        result = list(tree.get(*[0, filter1, filter2]))
        for i in result:
            # print(i)
            assert i.value % 2 != 0
        assert len(result) == 2 * 2  # we expect two in first and two in second level

        print('level2 mixed2')
        # deeper filtering
        result = list(tree.get(*[0, filter2, filter1]))
        for i in result:
            # print(i)
            assert i.value % 2 == 0
        assert len(result) == 2 * 2  # we expect two in first and two in second level

        # In deepest level we do not test any permutation!

        print('level3 even')
        # deeper filtering
        result = list(tree.get(*[0, filter2, filter2, filter2]))
        for i in result:
            # print(i)
            assert i.value % 2 != 0
        assert len(result) == 2 * 2 * 2  # we expect two in first and two in second level and two in last level

        print('level3 odd')
        # deeper filtering
        result = list(tree.get(*[0, filter1, filter1, filter1]))
        for i in result:
            # print(i)
            assert i.value % 2 == 0
        assert len(result) == 2 * 2 * 2  # we expect two in first and two in second level and two in last level

        print('level3 mixed1')
        # deeper filtering
        result = list(tree.get(*[0, filter1, filter1, filter2]))
        for i in result:
            # print(i)
            assert i.value % 2 != 0
        assert len(result) == 2 * 2 * 2  # we expect two in first and two in second level and two in last level

        print('level3 mixed2')
        # deeper filtering
        result = list(tree.get(*[0, filter2, filter2, filter1]))
        for i in result:
            # print(i)
            assert i.value % 2 == 0
        assert len(result) == 2 * 2 * 2  # we expect two in first and two in second level and two in last level

        print('\nRESULT OF TEST: iTree level filters in getters-> PASS')

    def test5_iTree_other_filtered_methods(self):
        # filters are tested in a special test
        if not 5 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: iTree other filtered methods')
        tree, size = self.large_itree([4, 4, 4, 3], ['cnt'], 'cnt')
        # tree.render()

        filter1 = lambda i: bool(i.value % 2 == 0) if type(i.value) is int else True
        # filter2 = Filters.iTFilter(lambda i: i.value%2==0 if type(i.value) is int else True,iter_unfiltered=True)
        filter3 = lambda i: not filter1(i)
        # filter4 = Filters.iTFilter(lambda i: i.value%2==0 if type(i.value) is int else True, iter_unfiltered=True,invert=True)

        # we do not test again the normal iterators
        # The already tested methods might be used to verify the other methods,
        # also the invert is not tested for any methods

        # count
        assert len(tree[0]) == 4
        assert tree[0].filtered_len(filter1) == 2
        assert tree[0].filtered_len(filter3) == 2
        assert tree.get(*[0, 0, 0]).filtered_len(filter1) == 2
        assert tree.get(*[0, 0, 0]).filtered_len(filter3) == 1

        # count_deep
        assert len(tree.deep) == size
        assert tree.deep.filtered_len(filter1) == len(list(tree.deep.iter(filter1)))
        assert tree.deep.filtered_len(filter1, hierarcical=False) == len(
            list(filter(filter1, tree.deep)))
        assert tree.deep.filtered_len(filter3) == len(list(tree.deep.iter(filter3)))
        assert tree.deep.filtered_len(filter3, hierarcical=False) == len(
            list(filter(filter3, tree.deep)))

        # unset_tree_read_only_deep
        tree2 = tree.copy()
        tree.set_value(2)

        # This is a deep operation:
        tree2.set_tree_read_only()
        for i in tree2.deep:
            assert i.is_tree_read_only

        tree2.deep.unset_tree_read_only(filter1)
        for i in tree2.deep:
            if filter1(i) and not i.parent.is_tree_read_only:
                assert not i.is_tree_read_only, 'Item %s is read-only-tree' % repr(i)
            else:
                assert i.is_tree_read_only

        tree2.unset_tree_read_only()

        # set_value_read_only_deep
        tree2.deep.set_value_read_only(filter1, False)
        for i in tree2.deep:
            if filter1(i):
                assert i.is_value_read_only
            else:
                assert not i.is_value_read_only

        tree2.deep.unset_value_read_only()
        tree2.deep.set_value_read_only(filter1)
        for i in tree2.deep:
            if filter1(i) and i.parent.is_value_read_only:
                assert i.is_value_read_only
            else:
                assert not i.is_value_read_only

        # unset_value_read_only_deep
        tree2.deep.set_value_read_only()
        tree2.deep.unset_value_read_only(filter1, False)
        for i in tree2.deep:
            if filter1(i):
                assert not i.is_value_read_only
            else:
                assert i.is_value_read_only

        tree2.deep.set_value_read_only()
        tree2.deep.unset_value_read_only(filter1)
        for i in tree2.deep:
            if filter1(i) and not i.parent.is_value_read_only:
                assert not i.is_value_read_only
            else:
                assert i.is_value_read_only

        # renders
        # render we do not test hard to catch stdout and same code like renders
        # we create a very restrictive filter to create a very small output

        # this filter will be very restrictive because it will deliver just in first level
        filter1 = lambda i: i.value in {2, 100, 200}
        # filter2 = Filters.iTFilter(lambda i: i.value in{2,100,200}, iter_unfiltered=True)
        # tree.render(enumerate=True)
        out_str = tree.renders(filter_method=filter1)
        assert out_str.count('iTree') == 1


        # as for render we check just dumps not dump here
        filter1 = lambda i: i.tag in {'root', 0, 2}

        # dumps
        out_str = tree.dumps(False, filter1)
        new_tree = tree.loads(out_str)
        assert len(new_tree.deep) == 30
        for i in new_tree.deep:
            assert i.tag in {'root', 0, 2}

        filter1 = lambda i: i.tag in {'root', 0, 2}
        # This should be ignored (same result)
        # dumps
        out_str = tree.dumps(False, filter1)
        new_tree2 = tree.loads(out_str)
        assert new_tree2 == new_tree

        print('\nRESULT OF TEST: iTree other filtered methods-> PASS')
