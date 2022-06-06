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


This part of code contains the profiling of nested iTree structures
"""

import cProfile
import sys
import itertools
from itertree import *

max_items = 102
#max_items = 5
if len(sys.argv)==2:
    max_items = int(sys.argv[1])

root=None



def performance_it_build():
    #tag access
    global dt_root,max_items
    dt = iTree('root')
    #dt.pre_alloc_list(max_items)
    #append itertree with items
    append_item = dt
    for i in range(max_items):
        for ii in range(max_items):
            new=iTree('%i' % i)
            append_item.append(new)
        append_item = new # we extend on last item (search for this element might be slower)
    dt_root=dt

def performance_it_get_max_children_depth():
    #tag access
    global dt_root,max_items
    print('Max tree depth %i' % dt_root.max_depth_down)

def performance_it_get_deep_by_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    key_list = []
    for i in range(max_items):
        key_list.append(None)
        for ii in range(max_items):
            key_list[-1] = ii
            c=dt.get_deep(key_list)
            if type(c) is not iTree:
                raise TypeError('%s is no iTree object'%repr(c))

def performance_it_find_all_by_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items via find
    key_list = []
    for i in range(max_items):
        key_list.append(None)
        for ii in range(max_items):
            key_list[-1] = ii
            a=dt.find_all(key_list)
            b = next(itertools.islice(a, 0, None))
            if type(b) is not iTree:
                raise TypeError('%s is no iTree object'%repr(b))

def performance_it_find_all2_by_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items via find
    key_list = []
    for i in range(max_items):
        key_list.append(None)
        for ii in range(max_items):
            key_list[-1] = ii
            a=dt.find_all2(key_list)
            b = next(itertools.islice(a, 0, None))
            if type(b) is not iTree:
                raise TypeError('%s is no iTree object'%repr(b))

performance_it_build()
#cProfile.run('performance_it_get_max_children_depth()')
#cProfile.run('performance_it_get_deep_by_idx()')
cProfile.run('performance_it_find_all_by_idx()')
#cProfile.run('performance_it_find_all2_by_idx()')



