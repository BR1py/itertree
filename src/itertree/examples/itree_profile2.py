"""
profile a nested structure
"""
import cProfile
import itertools
from itertree import *

max_items = 102
#max_items = 5

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



