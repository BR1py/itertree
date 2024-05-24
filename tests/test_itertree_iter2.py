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
Testcase checking all variations of iteration options
Some of the testcases can be found in the diagrams of the tutorial
"""

import os
import itertools
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
import sys
from types import GeneratorType
from collections import OrderedDict,deque
from itertree import *
from itertree.itree_helpers import NoValue, NoTag, BLIST_ACTIVE
from itertree.itree_mathsets import mSetInterval

DOWN = ITER.DOWN
UP = ITER.UP
REVERSE = ITER.REVERSE
SELF = ITER.SELF
FILTER_ANY = ITER.FILTER_ANY
MULTIPLE=ITER.MULTIPLE

iter_list = list if sys.version_info >= (3, 8) else deque  # from Python 3.8 on lists are quicker then deque

NONE_TUPLE = (None,)


root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

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


class Test1_iTree_deep_iter_options:

    def test1_iTree_iter_default(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep iter() default')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r210 = r21.append(iTree('210'))

        # default
        result = [r0, r00, r01, r010, r011, r1, r10, r11, r2, r20, r200, r201, r21, r210]
        assert list(root.deep)
        assert list(root.deep.iter()) == result
        assert list(root.deep.iter(options=ITER.DOWN)) == result

        # reverse
        result = [r2, r21, r210, r20, r201, r200, r1, r11, r10, r0, r01, r011, r010, r00]
        assert list(root.deep.iter(options=ITER.REVERSE)) == result
        assert list(root.deep.iter(options=ITER.DOWN | ITER.REVERSE)) == result

        # incl. self
        result = [root, r0, r00, r01, r010, r011, r1, r10, r11, r2, r20, r200, r201, r21, r210]
        assert list(root.deep.iter(options=ITER.SELF)) == result

        # incl. self; reverse
        result = [r2, r21, r210, r20, r201, r200, r1, r11, r10, r0, r01, r011, r010, r00, root]
        assert list(root.deep.iter(options=ITER.SELF | ITER.REVERSE)) == result

    def test2_iTree_iter_default_filtered(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep iter() filtered (default)')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r210 = r21.append(iTree('210'))

        myfilter = lambda i: bool(i.idx)

        # default
        # hierarchical filter
        result = [r1, r11, r2, r21]
        assert list(root.deep.iter(filter_method=myfilter)) == result  # normal filter
        result = [r01, r011, r1, r11, r2, r201, r21]
        assert list(root.deep.iter(filter_method=myfilter, options=ITER.FILTER_ANY)) == result
        assert list(filter(myfilter, root.deep)) == list(
            root.deep.iter(filter_method=myfilter, options=ITER.FILTER_ANY)) == result
        # reverse
        # hierarchical filter
        result = [r2, r21, r1, r11]
        assert list(root.deep.iter(myfilter, options=ITER.REVERSE)) == result  # normal filter
        result = [r2, r21, r201, r1, r11, r01, r011]
        assert list(root.deep.iter(filter_method=myfilter, options=ITER.REVERSE | ITER.FILTER_ANY)) == result
        # incl. self
        result = []
        assert list(root.deep.iter(myfilter, options=ITER.SELF)) == result
        result = [r01, r011, r1, r11, r2, r201, r21]
        assert list(root.deep.iter(filter_method=myfilter, options=ITER.SELF | ITER.FILTER_ANY)) == result
        # incl. self; reverse
        result = []
        assert list(root.deep.iter(myfilter, options=ITER.SELF | ITER.REVERSE)) == result
        result = [r2, r21, r201, r1, r11, r01, r011]
        assert list(root.deep.iter(myfilter, options=ITER.SELF | ITER.REVERSE | ITER.FILTER_ANY)) == result

    def test3_iTree_iter_up(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep iter() up')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r210 = r21.append(iTree('210'))

        # default
        result = [r00, r010, r011, r01, r0, r10, r11, r1, r200, r201, r20, r210, r21, r2]
        assert list(root.deep.iter(options=ITER.UP)) == result
        assert list(root.deep.iter(options=ITER.DOWN | ITER.UP)) == result

        # reverse
        result = [r210, r21, r201, r200, r20, r2, r11, r10, r1, r011, r010, r01, r00, r0]
        assert list(root.deep.iter(options=ITER.REVERSE | ITER.UP)) == result
        assert list(root.deep.iter(options=ITER.DOWN | ITER.REVERSE | ITER.UP)) == result

        # incl. self
        result = [r00, r010, r011, r01, r0, r10, r11, r1, r200, r201, r20, r210, r21, r2, root]
        assert list(root.deep.iter(options=ITER.SELF | ITER.UP)) == result

        # incl. self; reverse
        result = [r210, r21, r201, r200, r20, r2, r11, r10, r1, r011, r010, r01, r00, r0, root]
        assert list(root.deep.iter(options=ITER.SELF | ITER.REVERSE | ITER.UP)) == result

    def test3_iTree_iter_up_filtered(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep iter() filtered up')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r210 = r21.append(iTree('210'))

        myfilter = lambda i: bool(i.idx)

        # default
        # hierarchical filtering
        result = [r11, r1, r21, r2]
        assert list(root.deep.iter(myfilter, options=ITER.UP)) == result
        # normal filtering
        result = [r011, r01, r11, r1, r201, r21, r2]
        assert list(root.deep.iter(myfilter, options=ITER.UP | ITER.FILTER_ANY)) == result

        # reverse
        result = [r21, r2, r11, r1]
        assert list(root.deep.iter(myfilter, options=ITER.REVERSE | ITER.UP)) == result
        result = [r21, r201, r2, r11, r1, r011, r01]
        assert list(root.deep.iter(myfilter, options=ITER.REVERSE | ITER.UP | ITER.FILTER_ANY)) == result

        # incl. self
        result = []
        assert list(root.deep.iter(myfilter, options=ITER.UP | ITER.SELF)) == result
        # normal filtering
        result = [r011, r01, r11, r1, r201, r21, r2]
        assert list(root.deep.iter(myfilter, options=ITER.UP | ITER.FILTER_ANY | ITER.SELF)) == result

        # incl. self; reverse
        result = []
        assert list(root.deep.iter(myfilter, options=ITER.REVERSE | ITER.UP | ITER.SELF)) == result
        result = [r21, r201, r2, r11, r1, r011, r01]
        assert list(root.deep.iter(myfilter, options=ITER.REVERSE | ITER.UP | ITER.FILTER_ANY | ITER.SELF)) == result


class Test2_iTree_deep_siblings_options:

    def test1_iTree_siblings_positive_level(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep siblings() positive level')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        # default (level=0)
        # siblings full tree in level =0
        self_item = r10
        result = []
        assert list(self_item.deep.siblings(0)) == result
        assert list(self_item.deep.siblings(0, options=ITER.MULTIPLE)) == result
        assert list(self_item.deep.siblings(0, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(0, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        result = [r10]
        assert list(self_item.deep.siblings(0, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(0, options=ITER.SELF|ITER.MULTIPLE)) == result
        assert list(self_item.deep.siblings(0, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(0, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        # level=1
        # siblings full tree in level =0
        self_item = r01
        result = [r010, r011]
        assert list(self_item.deep.siblings(1)) == result
        assert list(self_item.deep.siblings(1, options=ITER.MULTIPLE)) == result
        # incl. self (same because self is in another level
        assert list(self_item.deep.siblings(1, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(1, options=ITER.SELF|ITER.MULTIPLE)) == result

        # reverse
        result = [r011, r010]
        assert list(self_item.deep.siblings(1, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(1, options=ITER.REVERSE|ITER.MULTIPLE)) == result

        # reverse incl. self (same because self is in another level
        assert list(self_item.deep.siblings(1, options=ITER.REVERSE | ITER.SELF)) == result
        assert list(self_item.deep.siblings(1, options=ITER.REVERSE | ITER.SELF|ITER.MULTIPLE)) == result

        self_item = r10
        result = [r1000, r1001]
        assert list(self_item.deep.siblings(2)) == result
        assert list(self_item.deep.siblings(2,ITER.MULTIPLE)) == result

        # incl. self (same because self is in another level
        assert list(self_item.deep.siblings(2, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(2, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result = [r1001, r1000]
        assert list(self_item.deep.siblings(2, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(2, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # reverse incl. self (same because self is in another level
        assert list(self_item.deep.siblings(2, options=ITER.REVERSE | ITER.SELF)) == result
        assert list(self_item.deep.siblings(2, options=ITER.REVERSE | ITER.SELF|ITER.MULTIPLE)) == result

        self_item = r2
        result = [r200, r201]
        assert list(self_item.deep.siblings(2)) == result
        assert list(self_item.deep.siblings(2,ITER.MULTIPLE)) == result
        # incl. self (same because self is in another level
        assert list(self_item.deep.siblings(2, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(2, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result = [r201, r200]
        assert list(self_item.deep.siblings(2, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(2, options=ITER.REVERSE|ITER.MULTIPLE)) == result

        # reverse incl. self (same because self is in another level
        assert list(self_item.deep.siblings(2, options=ITER.REVERSE | ITER.SELF)) == result
        assert list(self_item.deep.siblings(2, options=ITER.REVERSE | ITER.SELF|ITER.MULTIPLE)) == result

        self_item = r0
        result = [r0100, r0101]
        assert list(self_item.deep.siblings(3)) == result
        assert list(self_item.deep.siblings(3,ITER.MULTIPLE)) == result
        # incl. self (same because self is in another level
        assert list(self_item.deep.siblings(3, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(3, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result = [r0101, r0100]
        assert list(self_item.deep.siblings(3, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(3, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # reverse incl. self (same because self is in another level
        assert list(self_item.deep.siblings(3, options=ITER.REVERSE | ITER.SELF)) == result
        assert list(self_item.deep.siblings(3, options=ITER.REVERSE | ITER.SELF|ITER.MULTIPLE)) == result

    def test2_iTree_siblings_rel_negative_level(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep siblings() relative negative level')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('1000'))
        r1001 = r100.append(iTree('1001'))
        r2000 = r200.append(iTree('2000'))

        # level = -1
        # siblings full tree in level =0
        self_item = r10
        result = [r1000, r1001]
        assert list(self_item.deep.siblings(-1)) == result
        assert list(self_item.deep.siblings(-1,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.deep.siblings(-1, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.SELF|ITER.MULTIPLE)) == result
        result = [r1001, r1000]
        assert list(self_item.deep.siblings(-1, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.deep.siblings(-1, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        self_item = r1
        result = [r1000, r1001, r11]
        assert list(self_item.deep.siblings(-1)) == result
        assert list(self_item.deep.siblings(-1,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.deep.siblings(-1, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.SELF|ITER.MULTIPLE)) == result
        result = [r11, r1001, r1000]
        assert list(self_item.deep.siblings(-1, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.deep.siblings(-1, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        self_item = r1
        result = [r100]
        assert list(self_item.deep.siblings(-2)) == result
        result = [r100,r100]
        assert list(self_item.deep.siblings(-2,ITER.MULTIPLE)) == result
        # incl. self
        result = [r100, r1]
        assert list(self_item.deep.siblings(-2, options=ITER.SELF)) == result
        result = [r100, r100,r1]
        assert list(self_item.deep.siblings(-2, options=ITER.SELF|ITER.MULTIPLE)) == result
        result = [r100]
        assert list(self_item.deep.siblings(-2, options=ITER.REVERSE)) == result
        result = [r100,r100]
        assert list(self_item.deep.siblings(-2, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        result = [r1, r100]
        assert list(self_item.deep.siblings(-2, options=ITER.SELF | ITER.REVERSE)) == result
        result = [r1, r100,r100]
        assert list(self_item.deep.siblings(-2, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        self_item = root
        result = [r000, r0100, r0101, r011, r1000, r1001, r11, r2000, r201, r21]
        assert list(self_item.deep.siblings(-1)) == result
        assert list(self_item.deep.siblings(-1,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.deep.siblings(-1, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.SELF|ITER.MULTIPLE)) == result
        result.reverse()
        assert list(self_item.deep.siblings(-1, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.deep.siblings(-1, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(-1, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        result = [r00, r010, r01, r100, r1, r200, r20, r2]
        assert list(self_item.deep.siblings(-2)) == result
        result2 = [r00, r010, r010,r01, r100, r100,r1, r200, r20, r2]
        assert list(self_item.deep.siblings(-2,ITER.MULTIPLE)) == result2
        # incl. self
        assert list(self_item.deep.siblings(-2, options=ITER.SELF)) == result
        assert list(self_item.deep.siblings(-2, options=ITER.SELF|ITER.MULTIPLE)) == result2
        result.reverse()
        result2.reverse()
        assert list(self_item.deep.siblings(-2, options=ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(-2, options=ITER.REVERSE|ITER.MULTIPLE)) == result2

        # incl. self
        assert list(self_item.deep.siblings(-2, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.deep.siblings(-2, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result2

        result = [r0, r01, r10, r20, r2]
        assert list(self_item.deep.siblings(-3)) == result
        result = [r0, r01,r01,r0,r10, r10, r20, r2]
        assert list(self_item.deep.siblings(-3,ITER.MULTIPLE)) == result
        # incl. self
        result2 = [r0, r01, r10, root, r20, r2]
        assert list(self_item.deep.siblings(-3, options=ITER.SELF)) == result2
        result2 = [r0, r01, r01, r0, r10, r10,root, r20, r2,root]
        assert list(self_item.deep.siblings(-3, options=ITER.SELF|ITER.MULTIPLE,)) == result2
        result = [r2, r20, r10, r0, r01]
        assert list(self_item.deep.siblings(-3, options=ITER.REVERSE)) == result
        result = [r2, r20, r10, r10, r0, r01, r01,r0]
        assert list(self_item.deep.siblings(-3, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        result2 = [root, r2, r20, r10, r0, r01]
        assert list(self_item.deep.siblings(-3, options=ITER.SELF | ITER.REVERSE)) == result2
        result2 = [root, r2,r20,root,r10,  r10, r0, r01,r01,r0]
        assert list(self_item.deep.siblings(-3, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result2

        result = [r0, r1, r2]
        assert list(self_item.deep.siblings(-4)) == result
        result = [r0,r0,r1, r1, r2]
        assert list(self_item.deep.siblings(-4,ITER.MULTIPLE)) == result
        # incl. self
        result2 = [root, r0, r1, r2]
        assert list(self_item.deep.siblings(-4, options=ITER.SELF)) == result2
        result2 = [root, r0,r0,root, r1,r1, r2,root]

        assert list(self_item.deep.siblings(-4, options=ITER.SELF|ITER.MULTIPLE)) == result2
        result=[r2,r1,r0]
        assert list(self_item.deep.siblings(-4, options=ITER.REVERSE)) == result
        result = [r2, r1, r1,r0,r0]
        assert list(self_item.deep.siblings(-4, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        result2 = [root, r2, r1, r0]
        assert list(self_item.deep.siblings(-4, options=ITER.SELF | ITER.REVERSE)) == result2
        result2 = [root, r2, r1,r1,root, r0,r0,root]
        assert list(self_item.deep.siblings(-4, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result2

    def test3_iTree_siblings_abs_positive_level(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep siblings() absolute positive level')
        # build the standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        # siblings full tree in level =0
        self_item = r10
        result = []
        assert list(self_item.root.deep.siblings(0)) == result
        assert list(self_item.root.deep.siblings(0,ITER.MULTIPLE)) == result
        # incl. self
        result = [root]
        assert list(self_item.root.deep.siblings(0, options=ITER.SELF)) == result
        assert list(self_item.root.deep.siblings(0, options=ITER.SELF|ITER.MULTIPLE)) == result

        result = [r0, r1, r2]
        assert list(self_item.root.deep.siblings(1)) == result
        assert list(self_item.root.deep.siblings(1,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(1, options=ITER.SELF)) == result
        assert list(self_item.root.deep.siblings(1, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result = [r2, r1, r0]
        assert list(self_item.root.deep.siblings(1, options=ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(1, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(1, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(1, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        result = [r00, r01, r10, r11, r20, r21]
        assert list(self_item.root.deep.siblings(2)) == result
        assert list(self_item.root.deep.siblings(2,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(2, options=ITER.SELF)) == result
        assert list(self_item.root.deep.siblings(2, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result.reverse()
        assert list(self_item.root.deep.siblings(2, options=ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(2, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(2, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(2, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        # explicit self:
        result = [r00, r01, r10, r11, r20, r21]
        assert list(self_item.root.deep.siblings(self_item.level)) == result
        assert list(self_item.root.deep.siblings(self_item.level,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(self_item.level, options=ITER.SELF)) == result
        assert list(self_item.root.deep.siblings(self_item.level, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result.reverse()
        assert list(self_item.root.deep.siblings(self_item.level, options=ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(self_item.level, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(self_item.level, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(self_item.level, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        # exclude self:
        result = [r00, r01, r11, r20, r21]
        assert list(i for i in self_item.root.deep.siblings(self_item.level) if i is not self_item)
        assert list(i for i in self_item.root.deep.siblings(self_item.level,ITER.MULTIPLE) if i is not self_item)
        result.reverse()
        assert list(
            i for i in self_item.root.deep.siblings(self_item.level, ITER.REVERSE) if i is not self_item)
        assert list(
            i for i in self_item.root.deep.siblings(self_item.level, ITER.REVERSE|ITER.MULTIPLE) if i is not self_item)

        result = [r000, r010, r011, r100, r200, r201]
        assert list(self_item.root.deep.siblings(3)) == result
        assert list(self_item.root.deep.siblings(3,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(3, options=ITER.SELF)) == result
        assert list(self_item.root.deep.siblings(3, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result.reverse()
        assert list(self_item.root.deep.siblings(3, options=ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(3, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(3, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(3, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        result = [r0100, r0101, r1000, r1001, r2000]
        assert list(self_item.root.deep.siblings(4)) == result
        assert list(self_item.root.deep.siblings(4,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(4, options=ITER.SELF)) == result
        assert list(self_item.root.deep.siblings(4, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result.reverse()
        assert list(self_item.root.deep.siblings(4, options=ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(4, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(4, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(4, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

        result = []
        assert list(self_item.root.deep.siblings(5)) == result
        assert list(self_item.root.deep.siblings(5,ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(5, options=ITER.SELF)) == result
        assert list(self_item.root.deep.siblings(5, options=ITER.SELF|ITER.MULTIPLE)) == result
        # reverse
        result.reverse()
        assert list(self_item.root.deep.siblings(5, options=ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(5, options=ITER.REVERSE|ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(5, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(5, options=ITER.SELF | ITER.REVERSE|ITER.MULTIPLE)) == result

    def test4_iTree_siblings_abs_negative_level(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep siblings() absolute negative level')
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        # siblings full tree in level =0
        self_item = r10
        result = [r000, r0100, r0101, r011, r1000, r1001, r11, r2000, r201, r21]
        assert list(self_item.root.deep.siblings(-1)) == result
        assert list(self_item.root.deep.siblings(-1, ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(-1, options=ITER.SELF)) == result
        assert list(self_item.root.deep.siblings(-1, options=ITER.SELF | ITER.MULTIPLE)) == result
        result.reverse()
        assert list(self_item.root.deep.siblings(-1, ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(-1, ITER.REVERSE | ITER.MULTIPLE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(-1, options=ITER.SELF | ITER.REVERSE)) == result
        assert list(self_item.root.deep.siblings(-1, options=ITER.SELF | ITER.REVERSE | ITER.MULTIPLE
                                                 )) == result
        result = [r00, r010, r01, r100, r1, r200, r20, r2]
        assert list(self_item.root.deep.siblings(-2)) == result
        result2 = [r00, r010, r010, r01, r100, r100, r1, r200, r20, r2]
        assert list(self_item.root.deep.siblings(-2, ITER.MULTIPLE)) == result2
        # incl. self
        assert list(self_item.root.deep.siblings(-2, options=ITER.SELF)) == result
        result.reverse()
        assert list(self_item.root.deep.siblings(-2, ITER.REVERSE)) == result
        # incl. self
        assert list(self_item.root.deep.siblings(-2, options=ITER.SELF | ITER.REVERSE)) == result

        result = [r0, r01, r10, r20, r2]
        assert list(self_item.root.deep.siblings(-3)) == result
        # incl. self
        result = [r0, r01, r10, root, r20, r2]
        assert list(self_item.root.deep.siblings(-3, options=ITER.SELF)) == result
        result2 = [r0, r01, r01, r0, r10, r10, root, r20, r2, root]
        assert list(self_item.root.deep.siblings(-3, options=ITER.SELF | ITER.MULTIPLE)) == result2

        result = [r2, r20, r10, r0, r01]
        assert list(self_item.root.deep.siblings(-3, ITER.REVERSE)) == result
        result = [r2, r20, r10, r10, r0, r01, r01, r0]
        assert list(self_item.root.deep.siblings(-3, ITER.REVERSE | ITER.MULTIPLE)) == result
        # incl. self
        result = [root, r2, r20, r10, r0, r01]
        assert list(self_item.root.deep.siblings(-3, options=ITER.SELF | ITER.REVERSE)) == result
        result2.reverse()
        assert list(self_item.root.deep.siblings(-3, options=ITER.SELF | ITER.REVERSE | ITER.MULTIPLE)) == result2

        result = [r0, r1, r2]
        assert list(self_item.root.deep.siblings(-4)) == result
        result2 = [r0, r0, r1, r1, r2]
        assert list(self_item.root.deep.siblings(-4, ITER.MULTIPLE)) == result2
        # incl. self
        result = [root, r0, r1, r2]
        assert list(self_item.root.deep.siblings(-4, options=ITER.SELF)) == result
        result3 = [root, r0, r0, root, r1, r1, r2, root]
        assert list(self_item.root.deep.siblings(-4, options=ITER.SELF | ITER.MULTIPLE)) == result3
        result = [r2, r1, r0]
        assert list(self_item.root.deep.siblings(-4, ITER.REVERSE)) == result
        result2.reverse()
        assert list(self_item.root.deep.siblings(-4, ITER.REVERSE | ITER.MULTIPLE)) == result2
        # incl. self
        result = [root, r2, r1, r0]
        assert list(self_item.root.deep.siblings(-4, options=ITER.SELF | ITER.REVERSE)) == result
        result3.reverse()
        assert list(self_item.root.deep.siblings(-4, options=ITER.SELF | ITER.REVERSE | ITER.MULTIPLE)) == result3


class Test3_iTree_deep_levels_options:

    def test1_iTree_levels_positive_slices(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep levels() plus start plus steps slices')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        # default (level=0)
        # siblings full tree in level =0
        self_item = root

        result = [r0, r1, r2, r00, r01, r10, r11, r20, r21, r000, r010, r011, r100, r200, r201, r0100, r0101, r1000,
                  r1001,
                  r2000]
        assert list(self_item.deep.levels()) == result
        # incl. self
        result = [root, r0, r1, r2, r00, r01, r10, r11, r20, r21, r000, r010, r011, r100, r200, r201, r0100, r0101,
                  r1000,
                  r1001, r2000]
        assert list(self_item.deep.levels(options=ITER.SELF)) == result
        # reversed
        result = [r2, r1, r0, r21, r20, r11, r10, r01, r00, r201, r200, r100, r011, r010, r000, r2000, r1001, r1000,
                  r0101,
                  r0100]
        assert list(self_item.deep.levels(options=ITER.REVERSE)) == result
        # incl. self
        result = [root, r2, r1, r0, r21, r20, r11, r10, r01, r00, r201, r200, r100, r011, r010, r000, r2000, r1001,
                  r1000,
                  r0101, r0100]
        assert list(self_item.deep.levels(options=ITER.SELF | ITER.REVERSE)) == result

        # slice with step size 2
        result = [r00, r01, r10, r11, r20, r21, r0100, r0101, r1000,
                  r1001, r2000]
        assert list(self_item.deep.levels(slice(0, None, 2))) == result
        # incl. self
        result = [root, r00, r01, r10, r11, r20, r21, r0100, r0101, r1000,
                  r1001, r2000]
        assert list(self_item.deep.levels(slice(0, None, 2), options=ITER.SELF)) == result
        # reversed
        result = [r21, r20, r11, r10, r01, r00, r2000, r1001, r1000,
                  r0101, r0100]
        assert list(self_item.deep.levels(slice(0, None, 2), options=ITER.REVERSE)) == result
        # incl. self
        result = [root, r21, r20, r11, r10, r01, r00, r2000, r1001, r1000,
                  r0101, r0100]
        assert list(self_item.deep.levels(slice(0, None, 2), options=ITER.SELF | ITER.REVERSE)) == result

        # slice start with 0 and end with 2 (relative levels)
        self_item = r0
        result = [r00, r01]
        assert list(self_item.deep.levels(slice(0, 2))) == result
        # incl. self
        result = [r0, r00, r01]
        assert list(self_item.deep.levels(slice(0, 2), options=ITER.SELF)) == result
        # reversed
        result = [r01, r00]
        assert list(self_item.deep.levels(slice(0, 2), options=ITER.REVERSE)) == result
        # incl. self
        result = [r0, r01, r00]
        assert list(self_item.deep.levels(slice(0, 2), options=ITER.REVERSE | ITER.SELF)) == result
        self_item = r2
        result = [r20, r21, r200, r201]
        assert list(self_item.deep.levels(slice(0, 3))) == result
        # incl. self
        result = [r2, r20, r21, r200, r201]
        assert list(self_item.deep.levels(slice(0, 3), options=ITER.SELF)) == result
        # reversed
        result = [r21, r20, r201, r200]
        assert list(self_item.deep.levels(slice(0, 3), options=ITER.REVERSE)) == result
        # incl. self
        result = [r2, r21, r20, r201, r200]
        assert list(self_item.deep.levels(slice(0, 3), options=ITER.REVERSE | ITER.SELF)) == result

        # slice start with 1 and end with 3 (absolute levels)
        self_item = root
        result = [r0, r1, r2, r00, r01, r10, r11, r20, r21]
        assert list(self_item.deep.levels(slice(1, 3))) == result
        # incl. self
        assert list(self_item.deep.levels(slice(1, 3), options=ITER.SELF)) == result
        # reversed
        result = [r2, r1, r0, r21, r20, r11, r10, r01, r00]
        assert list(self_item.deep.levels(slice(1, 3), options=ITER.REVERSE)) == result
        # incl. self
        assert list(self_item.deep.levels(slice(1, 3), options=ITER.REVERSE | ITER.SELF)) == result

        # special cases with empty lists
        assert list(self_item.deep.levels(slice(0, 1), )) == []
        assert list(self_item.deep.levels(slice(0, 1), options=ITER.REVERSE)) == []
        assert list(self_item.deep.levels(slice(0, 2, 2), )) == []
        assert list(self_item.deep.levels(slice(0, 2, 2), options=ITER.REVERSE)) == []
        # special cases with only self
        assert list(self_item.deep.levels(slice(0, 1), options=ITER.SELF)) == [root]
        assert list(self_item.deep.levels(slice(0, 1), options=ITER.REVERSE | ITER.SELF)) == [root]
        assert list(self_item.deep.levels(slice(0, 2, 2), options=ITER.SELF)) == [root]
        assert list(self_item.deep.levels(slice(0, 2, 2), options=ITER.REVERSE | ITER.SELF)) == [root]



    def test2_iTree_levels_plus_start_minus_step_slices(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep levels() plus start minus step slices')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        # default (level=0)
        # siblings full tree in level =0
        self_item = root

        result = [r0100, r0101, r1000, r1001,
                  r2000, r000, r010, r011, r100, r200, r201, r00, r01, r10, r11, r20, r21, r0, r1, r2, ]
        assert list(self_item.deep.levels(slice(4, None, -1))) == result
        # incl. self
        result = [r0100, r0101, r1000, r1001,
                  r2000, r000, r010, r011, r100, r200, r201, r00, r01, r10, r11, r20, r21, r0, r1, r2, root]
        assert list(self_item.deep.levels(slice(4, None, -1), options=ITER.SELF)) == result
        # reversed
        result = [r2000, r1001, r1000, r0101,
                  r0100, r201, r200, r100, r011, r010, r000, r21, r20, r11, r10, r01, r00, r2, r1, r0]
        assert list(self_item.deep.levels(slice(4, None, -1), options=ITER.REVERSE)) == result
        # incl. self
        result = [r2000, r1001, r1000, r0101,
                  r0100, r201, r200, r100, r011, r010, r000, r21, r20, r11, r10, r01, r00, r2, r1, r0, root]
        assert list(self_item.deep.levels(slice(4, None, -1), options=ITER.SELF | ITER.REVERSE)) == result

        # slice with step size -2
        result = [r0100, r0101, r1000,
                  r1001, r2000, r00, r01, r10, r11, r20, r21]
        assert list(self_item.deep.levels(slice(4, None, -2))) == result
        # incl. self
        result = [r0100, r0101, r1000,
                  r1001, r2000, r00, r01, r10, r11, r20, r21, root]

        assert list(self_item.deep.levels(slice(4, None, -2), options=ITER.SELF)) == result
        # reversed
        result = [r2000, r1001, r1000,
                  r0101, r0100, r21, r20, r11, r10, r01, r00]
        assert list(self_item.deep.levels(slice(4, None, -2), options=ITER.REVERSE)) == result
        # incl. self
        result = [r2000, r1001, r1000,
                  r0101, r0100, r21, r20, r11, r10, r01, r00, root]
        assert list(self_item.deep.levels(slice(4, None, -2), options=ITER.SELF | ITER.REVERSE)) == result

        # slice start with 0 and end with 2 (relative levels)
        self_item = r0
        result = [r000, r010, r011, r00, r01]
        assert list(self_item.deep.levels(slice(2, 0, -1))) == result
        # incl. self
        assert list(self_item.deep.levels(slice(2, 0, -1), options=ITER.SELF)) == result
        # reversed
        result = [r011, r010, r000, r01, r00]
        assert list(self_item.deep.levels(slice(2, 0, -1), options=ITER.REVERSE)) == result
        # incl. self
        assert list(self_item.deep.levels(slice(2, 0, -1), options=ITER.REVERSE | ITER.SELF)) == result
        self_item = r2
        result = [r200, r201, r20, r21]
        assert list(self_item.deep.levels(slice(2, None, -1))) == result
        # incl. self
        result = [r200, r201, r20, r21, r2]
        assert list(self_item.deep.levels(slice(2, None, -1), options=ITER.SELF)) == result
        # reversed
        result = [r201, r200, r21, r20]
        assert list(self_item.deep.levels(slice(2, None, -1), options=ITER.REVERSE)) == result
        # incl. self
        result = [r201, r200, r21, r20, r2]
        assert list(self_item.deep.levels(slice(2, None, -1), options=ITER.REVERSE | ITER.SELF)) == result

        # slice start with 3 and end with 1 (absolute levels)
        self_item = root
        result = [r000, r010, r011, r100, r200, r201, r00, r01, r10, r11, r20, r21, r0, r1, r2]
        result=list(self_item.deep.siblings(3))
        result.extend((i for i in self_item.deep.siblings(2) if i not in result))
        result.extend((i for i in self_item.deep.siblings(1) if i not in result))
        assert list(self_item.deep.levels(slice(3, 0, -1))) == result
        # incl. self
        assert list(self_item.deep.levels(slice(3, 0, -1), options=ITER.SELF)) == result
        # reversed
        result = [r201, r200, r100, r011, r010, r000, r21, r20, r11, r10, r01, r00, r2, r1, r0]
        assert list(self_item.deep.levels(slice(3, 0, -1), options=ITER.REVERSE)) == result
        # incl. self
        assert list(self_item.deep.levels(slice(3, 0, -1), options=ITER.REVERSE | ITER.SELF)) == result

        # special cases with empty lists
        assert list(self_item.deep.levels(slice(1, 1, -1), )) == []
        assert list(self_item.deep.levels(slice(1, 1, -1), options=ITER.REVERSE)) == []
        assert list(self_item.deep.levels(slice(2, 3, -2), )) == list(self_item.deep.siblings(2))
        assert list(self_item.deep.levels(slice(2, 3, -2), options=ITER.REVERSE)) == list(self_item.deep.siblings(2,ITER.REVERSE))
        # special cases with only self
        assert list(self_item.deep.levels(slice(0, None, -1), options=ITER.SELF)) == [root]
        assert list(self_item.deep.levels(slice(0, None, -1), options=ITER.REVERSE | ITER.SELF)) == [root]
        assert list(self_item.deep.levels(slice(1, None, -2), options=ITER.SELF)) == list(self_item.deep.siblings(1))
        assert list(self_item.deep.levels(slice(1, None, -2), options=ITER.REVERSE | ITER.SELF)) ==list(self_item.deep.siblings(1, options=ITER.REVERSE | ITER.SELF))

        #ToDo MULTIPLE

    def test3_iTree_levels_plus_start_miuns_stop_slices(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep levels() plus start minus stop slices')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        self_item = root
        result = [r0, r1, r2, r00, r01, r10, r20, r010, r100, r200]
        assert list(self_item.deep.levels(slice(1, -1))) == result
        result = [r0, r1, r2, r00, r01, r10, r20, r010, r100, r200]
        assert list(self_item.deep.levels(slice(1, -1), ITER.SELF)) == result
        # reverse
        result = [r2, r1, r0, r20, r10, r01, r00, r200, r100, r010]
        assert list(self_item.deep.levels(slice(1, -1), ITER.REVERSE)) == result
        result = [r2, r1, r0, r20, r10, r01, r00, r200, r100, r010, ]
        assert list(self_item.deep.levels(slice(1, -1), ITER.SELF | ITER.REVERSE)) == result

        result = [r0, r1, r2, r00, r01, r10, r20, r010, r100, r200]
        assert list(self_item.deep.levels(slice(0, -1))) == result
        result = [root, r0, r1, r2, r00, r01, r10, r20, r010, r100, r200]
        assert list(self_item.deep.levels(slice(0, -1), ITER.SELF)) == result
        # reverse
        result = [r2, r1, r0, r20, r10, r01, r00, r200, r100, r010]
        assert list(self_item.deep.levels(slice(0, -1), ITER.REVERSE)) == result
        result = [root, r2, r1, r0, r20, r10, r01, r00, r200, r100, r010]
        assert list(self_item.deep.levels(slice(0, -1), ITER.SELF | ITER.REVERSE)) == result

        result = [r00, r01, r10, r20]
        assert list(self_item.deep.levels(slice(0, -1, 2))) == result
        result = [root, r00, r01, r10, r20]
        assert list(self_item.deep.levels(slice(0, -1, 2), ITER.SELF)) == result
        # reverse
        result = [r20, r10, r01, r00]
        assert list(self_item.deep.levels(slice(0, -1, 2), ITER.REVERSE)) == result
        result = [root, r20, r10, r01, r00]
        assert list(self_item.deep.levels(slice(0, -1, 2), ITER.SELF | ITER.REVERSE)) == result

        self_item = r2
        result = [r20, r200]
        assert list(self_item.deep.levels(slice(0, -1))) == result
        result2 = [r2, r20, r200]
        assert list(self_item.deep.levels(slice(0, -1), ITER.SELF)) == result2
        # reverse
        assert list(self_item.deep.levels(slice(0, -1), ITER.REVERSE)) == result
        assert list(self_item.deep.levels(slice(0, -1), ITER.SELF | ITER.REVERSE)) == result2

        self_item = r0
        result = [r010, r00, r01]
        assert list(self_item.deep.levels(slice(2, -1, -1))) == result
        result = [r010, r00, r01, r0]
        assert list(self_item.deep.levels(slice(2, -1, -1), ITER.SELF)) == result

        #ToDo MULTIPLE

    def test4_iTree_levels_minus_start_plus_stop_slices(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: deep levels() plus start minus stop slices')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('1000'))
        r1001 = r100.append(iTree('1001'))
        r2000 = r200.append(iTree('2000'))

        self_item = root
        assert list(self_item.deep.levels(slice(-1, None))) == [i for i in self_item.deep.siblings(-1) if i is not root]
        assert list(self_item.deep.levels(slice(-1, 10))) == [i for i in self_item.deep.siblings(-1) if i is not root]
        assert list(self_item.deep.levels(slice(-1, -10))) == [i for i in self_item.deep.siblings(-1) if i is not root]
        assert list(self_item.deep.levels(slice(-1, None, 2))) == [i for i in self_item.deep.siblings(-1) if
                                                                   i is not root]
        result=[i for i in self_item.deep.siblings(-2) if i is not root]
        result.extend([i for i in self_item.deep.siblings(-1) if i is not root and i not in result])

        assert list(self_item.deep.levels(slice(-2, None))) == result

        result=[i for i in self_item.deep.siblings(-1) if i is not root]
        result.extend([i for i in self_item.deep.siblings(-2) if i is not root and i not in result])
        result.extend([i for i in self_item.deep.siblings(-3) if i is not root and i not in result])
        result.extend([i for i in self_item.deep.siblings(-4) if i is not root and i not in result])

        assert list(self_item.deep.levels(slice(-1, None, -1))) == result
        result = [r000, r0100, r0101, r011, r1000, r1001, r11, r2000, r201, r21, r00, r010, r01, r100, r1, r200, r20,
                  r2, r0, r10, root]
        assert list(self_item.deep.levels(slice(-1, None, -1), ITER.SELF)) == result
        result = [r21, r201, r2000, r11, r1001, r1000, r011, r0101, r0100, r000,
                  r2, r20, r200, r1, r100, r01, r010,
                  r00, r10, r0]
        assert list(self_item.deep.levels(slice(-1, None, -1), ITER.REVERSE)) == result
        result = [r21, r201, r2000, r11, r1001, r1000, r011, r0101, r0100, r000,
                  r2, r20, r200, r1, r100, r01, r010,
                  r00, root, r10, r0]

        result=[i for i in self_item.deep.siblings(-1,ITER.SELF | ITER.REVERSE) if i is not root]
        result.extend([i for i in self_item.deep.siblings(-2,ITER.SELF | ITER.REVERSE) if i is not root and i not in result])
        result.extend([self_item])

        assert list(self_item.deep.levels(slice(-1, None, -1), ITER.SELF | ITER.REVERSE)) == result

        result = [r000, r0100, r0101, r011, r1000, r1001, r11, r2000, r201, r21,
                  r00, r010,r010, r01, r100,r100, r1, r200, r20, r2,
                  r0, r01, r01,r0,r10,r10,r20,r2,
                  r0,r0,r1,r1,r2]
        assert list(self_item.deep.levels(slice(-1,None, -1), ITER.MULTIPLE)) == result
        result = [r000, r0100, r0101, r011, r1000, r1001, r11, r2000, r201, r21,
                  r00, r010, r010, r01, r100, r100, r1, r200, r20, r2,
                  r0, r01, r01, r0, r10, r10, root,r20, r2,
                  root,root,r0, r0,root, r1, r1, r2,root,
                  root,root,root,root,root]
        assert list(self_item.deep.levels(slice(-1, None, -1), ITER.SELF|ITER.MULTIPLE)) == result

        #ToDo

        result = [r0, r1, r2, r00, r01, r10, r20, r010, r100, r200]
        assert list(self_item.deep.levels(slice(0, -1))) == result
        result = [root, r0, r1, r2, r00, r01, r10, r20, r010, r100, r200]
        assert list(self_item.deep.levels(slice(0, -1), ITER.SELF)) == result
        # reverse
        result = [r2, r1, r0, r20, r10, r01, r00, r200, r100, r010]
        assert list(self_item.deep.levels(slice(0, -1), ITER.REVERSE)) == result
        result = [root, r2, r1, r0, r20, r10, r01, r00, r200, r100, r010]
        assert list(self_item.deep.levels(slice(0, -1), ITER.SELF | ITER.REVERSE)) == result

        result = [r00, r01, r10, r20]
        assert list(self_item.deep.levels(slice(0, -1, 2))) == result
        result = [root, r00, r01, r10, r20]
        assert list(self_item.deep.levels(slice(0, -1, 2), ITER.SELF)) == result
        # reverse
        result = [r20, r10, r01, r00]
        assert list(self_item.deep.levels(slice(0, -1, 2), ITER.REVERSE)) == result
        result = [root, r20, r10, r01, r00]
        assert list(self_item.deep.levels(slice(0, -1, 2), ITER.SELF | ITER.REVERSE)) == result

        self_item = r2
        result = [r20, r200]
        assert list(self_item.deep.levels(slice(0, -1))) == result
        result2 = [r2, r20, r200]
        assert list(self_item.deep.levels(slice(0, -1), ITER.SELF)) == result2
        # reverse
        assert list(self_item.deep.levels(slice(0, -1), ITER.REVERSE)) == result
        assert list(self_item.deep.levels(slice(0, -1), ITER.SELF | ITER.REVERSE)) == result2

        self_item = r0
        result = [r010, r00, r01]
        assert list(self_item.deep.levels(slice(2, -1, -1))) == result
        result = [r010, r00, r01, r0]
        assert list(self_item.deep.levels(slice(2, -1, -1), ITER.SELF)) == result

class Test4_iTree_deep_iter_idxpath_tagidx_options:

    def idx_paths_old(self,itree, filter_method=None, up_to_low=True):
        """
        old idx_paths method
        """
        if itree:
            iterators = iter_list((itree.__iter__(),))  # in Python 3.9 lists are quicker than deque
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
                    iterators = iter_list((itree.__iter__(),))
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


    def test1_iTree_iter_idxpath_old_new(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: iter idxpath old/new')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        new_list=list(root.deep.idx_paths())
        old_list=list(self.idx_paths_old(root))
        for new,old in zip(new_list,old_list):
            assert new==old
        new_list=list(root.deep.idx_paths(options=UP))
        old_list=list(self.idx_paths_old(root,up_to_low=False))
        for new,old in zip(new_list,old_list):
            assert new==old

        myfilter = lambda i: i.idx and i.idx%2
        new_list=list(root.deep.idx_paths(myfilter))
        old_list=list(self.idx_paths_old(root,myfilter))
        for new,old in zip(new_list,old_list):
            assert new==old
        new_list=list(root.deep.idx_paths(myfilter,options=UP))
        old_list=list(self.idx_paths_old(root,myfilter,up_to_low=False))
        for new,old in zip(new_list,old_list):
            assert new==old


    def test2_iTree_iter_idxpath_full(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: iter idxpath full')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))


        # For the rest of the test we expect that iter behaves like idx_paths
        myfilter = lambda i: i.idx and i.idx%2
        mask=ITER.REVERSE|ITER.UP|ITER.FILTER_ANY|ITER.SELF
        tested_keys=set()
        for key in range((mask<<1)):
            try:
                key=key&mask
                if key in tested_keys:
                    continue
                tested_keys.add(key)
                new_items=list(root.deep.idx_paths(options=key))
                classic_items=list((i.idx_path,i) for i in root.deep.iter(options=key))
                for new,old in zip(new_items,classic_items):
                    assert new==old,'%s %s!=%s'%(ITER.get_option_str(key),new,old)
                new_items = root.deep.idx_paths(myfilter,options=key)
                classic_items = ((i.idx_path, i) for i in root.deep.iter(myfilter,options=key))
                for new, old in zip(new_items, classic_items):
                    assert new == old, '%s %s!=%s' % (ITER.get_option_str(key), new, old)
            except:
                print('Issue in: ',ITER.get_option_str(key))
                raise

            print(ITER.get_option_str(key)+' tested-> pass')


    def tag_idx_paths_old(self,itree, filter_method=None, up_to_low=True):
        """
        old idx_paths method
        """
        if itree:
            tag_indexes = [None]
            iterators = iter_list((itree.__iter__(),))
            if filter_method:
                if up_to_low:
                    none_tuple = NONE_TUPLE
                    tag_index_dict = [{tag: -1 for tag in itree._families.keys()}]
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                                tag_indexes[-1] = (tag, idx)
                                if filter_method(item):
                                    yield tuple(tag_indexes), item
                                    iterators.extend((none_tuple, filter(filter_method, item.__iter__())))
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
                    tag_index_dict = [{tag: -1 for tag in itree._families.keys()}]
                    while iterators:
                        for item in iterators[-1]:
                            if item:
                                tag = item._tag
                                tag_dict = tag_index_dict[-1]
                                item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                                tag_indexes[-1] = (tag, idx)
                                if filter_method(item):
                                    iterators.extend(
                                        ((None, (tuple(tag_indexes), item)), filter(filter_method, item.__iter__())))
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
                    tag_index_dict = [{tag: -1 for tag in itree._families.keys()}]
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
                    tag_index_dict = [dict.fromkeys(itree._families.keys(),-1)]
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


    def test3_iTree_iter_tagidxpath_old_new(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: iter tag_idx_path old/new')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        new_list=list(root.deep.tag_idx_paths())
        old_list=list(self.tag_idx_paths_old(root))
        for new,old in zip(new_list,old_list):
            assert new==old
        new_list=list(root.deep.tag_idx_paths(options=UP))
        old_list=list(self.tag_idx_paths_old(root,up_to_low=False))
        for new,old in zip(new_list,old_list):
            assert new==old

        myfilter = lambda i: i.idx and i.idx%2 or True
        new_list=list(root.deep.tag_idx_paths(myfilter))
        old_list=list(self.tag_idx_paths_old(root,myfilter))
        for new,old in zip(new_list,old_list):
            assert new==old
        new_list=list(root.deep.tag_idx_paths(myfilter,options=UP))
        old_list=list(self.tag_idx_paths_old(root,myfilter,up_to_low=False))
        for new,old in zip(new_list,old_list):
            assert new==old

    def test4_iTree_iter_tagidxpath_full(self):
        # filters are tested in a special test
        print('\nRESULT OF TEST: iter tag_idx_path full')
        # build teh standard tree
        root = iTree('root')
        r0 = root.append(iTree('0'))
        r00 = r0.append(iTree('00'))
        r000 = r00.append(iTree('000'))
        r01 = r0.append(iTree('01'))
        r010 = r01.append(iTree('010'))
        r011 = r01.append(iTree('011'))
        r1 = root.append(iTree('1'))
        r10 = r1.append(iTree('10'))
        r100 = r10.append(iTree('100'))
        r11 = r1.append(iTree('11'))
        r2 = root.append(iTree('2'))
        r20 = r2.append(iTree('20'))
        r200 = r20.append(iTree('200'))
        r201 = r20.append(iTree('201'))
        r21 = r2.append(iTree('21'))
        r0100 = r010.append(iTree('0100'))
        r0101 = r010.append(iTree('0101'))
        r1000 = r100.append(iTree('0100'))
        r1001 = r100.append(iTree('0101'))
        r2000 = r200.append(iTree('2000'))

        # For the rest of the test we expect that iter behaves like idx_pths
        myfilter = lambda i: i.idx and i.idx%2 or True
        mask=ITER.REVERSE|ITER.UP|ITER.FILTER_ANY|ITER.SELF
        tested_keys=set()
        for key in range((mask<<1)):
            try:
                key=key&mask
                if key in tested_keys:
                    continue
                tested_keys.add(key)
                new_items=list(root.deep.tag_idx_paths(options=key))
                classic_items=list((i.tag_idx_path,i) for i in root.deep.iter(options=key))
                for new,old in zip(new_items,classic_items):
                    assert new==old,'%s %s!=%s'%(ITER.get_option_str(key),new,old)
                new_items = root.deep.tag_idx_paths(myfilter,options=key)
                classic_items = ((i.tag_idx_path, i) for i in root.deep.iter(myfilter,options=key))
                for new, old in zip(new_items, classic_items):
                    assert new == old, '%s %s!=%s' % (ITER.get_option_str(key), new, old)
            except:
                print('Issue in: ',ITER.get_option_str(key))
                raise

            print(ITER.get_option_str(key)+' tested-> pass')


