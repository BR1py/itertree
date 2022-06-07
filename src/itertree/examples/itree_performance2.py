# -*- coding: utf-8 -*-
"""
performance comparison with deep trees
"""

from __future__ import absolute_import

import timeit
import os
import tempfile
import itertools
import sys

max_items = 150
#max_items=20
if len(sys.argv)==2:
    max_items = int(sys.argv[1])

itree_only=False

if len(sys.argv)==2:
    max_items=int(sys.argv[1])
if len(sys.argv)==3:
    max_items=int(sys.argv[1])
    itree_only=int(sys.argv[2])

#max_items = 20

repeat = 4



print('We run for deep tree-size: depth of %i with %i items and %i repetitions'%(max_items,max_items*max_items,repeat))

from itertree import iTree, __version__,TagIdx
print('Python: ',sys.version)
try:
    import blist
    print('blist package is available and used')
except:
    print('blist package is not available (normal list is used)')
    blist=None

print('itertree version: %s'%__version__)
print('A relative values >1 related to iTree means the other object is faster\n(relative values <1 means iTree is faster)')

root=None
dt_root=None
load_root=None

fh=tempfile.TemporaryFile('wb+') #global file handle for write/read actions

TMP_FOLDER=os.path.abspath('../test/tmp')

if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)


def performance_it_build_insert():
    #tag access
    global dt_root,max_items
    dt = iTree('root')
    #dt.pre_alloc_list(max_items)
    #append itertree with items
    append_item=dt
    for i in range(max_items):
        for i in range(max_items):
            new=iTree('%i' % i)
            append_item.insert(1,new)
        append_item = new

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

def performance_it_find_all_by_tag():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    tag_list=['%i' % i for i in range(int(max_items))]
    a=dt.find_all(tag_list)
    b=next(itertools.islice(a,0,None))
    c=b.tag

def performance_it_dump():
    global dt_root,fh
    fh.seek(0)
    dt_root.dump(fh,calc_hash=False)

def performance_it_load():
    global dt_root, fh,load_root
    fh.seek(0)
    load_root=iTree('tmp').load(fh)

it_append = timeit.timeit(performance_it_build, number=repeat)/ repeat
print('Execution time itertree build append: {}'.format(it_append ))
it_insert = timeit.timeit(performance_it_build_insert, number=repeat)/ repeat
print('Execution time itertree build (with insert): {}'.format(it_insert ))
it_depth_down = timeit.timeit(performance_it_get_max_children_depth, number=1) # we run this only one time
print('Execution time itertree get max_depth_down~iter_all(): {}'.format(it_depth_down))
it_get_deep_idx = timeit.timeit(performance_it_get_deep_by_idx, number=repeat)/ repeat
print('Execution time itertree get deep indexes access (all items iterated): {}'.format(it_get_deep_idx))
it_find_all_by_idx = timeit.timeit(performance_it_find_all_by_idx, number=repeat)/ repeat
print('Execution time itertree get find_all by indexes access (all items iterated): {}'.format(it_find_all_by_idx))
it_find_all_by_tag = timeit.timeit(performance_it_find_all_by_tag, number=repeat)/ repeat
print('Execution time itertree find all by deep tag list (one deep search last item): {}'.format(it_find_all_by_tag))
if max_items <=60:
    it_dump = timeit.timeit(performance_it_dump, number=repeat)/ repeat
    print('Execution time itertree save to file: {}'.format(it_dump ))
    it_load = timeit.timeit(performance_it_load, number=repeat)/ repeat
    print('Execution time itertree load from file: {}'.format(it_load))
    print('Loaded iTree is equal: %s'%(str(dt_root.equal(load_root))))

if itree_only:
    exit(0)

try:
    from lldict4 import llDict as llDict2
    print('-- llDict2 ---------------------------------')


    def performance_lldict_build():
        # tag access
        global dt_root, max_items
        dt = llDict2()
        # dt.pre_alloc_list(max_items)
        # append itertree with items
        append_item = dt
        for i in range(max_items):
            for ii in range(max_items):
                new = llDict2()
                append_item['%i_%i' % (i,ii)] = new
            append_item = new  # we extend on last item (search for this element might be slower)
        dt_root = dt

    def performance_lldict_get_key():
        global dt_root, max_items
        dt=dt_root
        key_list = []
        for i in range(max_items):
            key_list.append(None)
            for ii in range(max_items):
                key_list[-1]='%i_%i' % (i,ii)
                a=dt.get_deep(key_list)
                if type(a) is not llDict2:
                    raise TypeError('%s is no llDict'%repr(a))

    def performance_lldict_save():
        global dt_root, max_items
        dt_root.dump(TMP_FOLDER + '/perfomance1.cf2', overwrite=True,struct_str=False)

    def performance_lldict_load():
        global dt_root, max_items
        new_dict=dt_root.create_from_file(TMP_FOLDER + '/perfomance1.cf2')

    a = timeit.timeit(performance_lldict_build, number=repeat)/ repeat
    print('Execution time llDict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
    a = timeit.timeit(performance_lldict_get_key, number=repeat)/ repeat
    print('Execution time llDict key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_find_all_by_tag/a)))
    if max_items<=60:
        a = timeit.timeit(performance_lldict_save, number=repeat)/ repeat
        print('Execution time llDict save: {} ~ {:.3f}x faster as iTree'.format(a,(it_dump/a)))
        a = timeit.timeit(performance_lldict_load, number=repeat)/ repeat
        print('Execution time llDict load: {} ~ {:.3f}x faster as iTree'.format(a,(it_load/a)))

except ImportError:
    pass



# we compare here with dict, OrderedDict and list
print('-- Standard classes -----------------------------------')




def performance_dict_build():
    # tag access
    global dt_root, max_items
    dt = {}
    # dt.pre_alloc_list(max_items)
    # append itertree with items
    append_item = dt
    for i in range(max_items):
        for ii in range(max_items):
            new = {}
            append_item['%i_%i' % (i,ii)] = new
        append_item = new  # we extend on last item (search for this element might be slower)
    dt_root = dt

def performance_dict_get_keys():
    global dt_root, max_items
    dt=dt_root
    key_list = []
    for i in range(max_items):
        key_list.append(None)
        for ii in range(max_items):
            key_list[-1] = '%i_%i' % (i, ii)
            a = dt
            for k in key_list:
                a = a[k]
            if type(a) is not dict:
                raise TypeError('%s is no dict' % repr(a))


def performance_list_build():
    #tag access
    global dt_root,max_items
    dt = []
    #append itertree with items
    #for i in range(max_items):
    #    dt.append(['%i' % i])
    global dt_root, max_items
    # dt.pre_alloc_list(max_items)
    # append itertree with items
    dt=append_item = ['0']
    for i in range(max_items):
        for ii in range(max_items):
            new = ['%i_%i' % (i, ii)]
            append_item.append(new)
        append_item = new  # we extend on last item (search for this element might be slower)
    dt_root = dt

def performance_list_get_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    key_list = []
    for i in range(max_items):
        key_list.append(None)
        for ii in range(max_items):
            key_list[-1] = ii+1
            a = dt
            for k in key_list:
                a = a[k]
            if type(a) is not list and type(a) is not str:
                raise TypeError('%s is no str/list (key_list = %s)' % (repr(a),repr(key_list)))

a = timeit.timeit(performance_dict_build, number=repeat) / repeat
print('Execution time dict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
a = timeit.timeit(performance_dict_get_keys, number=repeat) / repeat
print('Execution time dict key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_find_all_by_tag/a)))
a = timeit.timeit(performance_list_build, number=repeat) / repeat
print('Execution time list build (via comprehension): {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))

a = timeit.timeit(performance_list_get_idx, number=repeat) / repeat
print('Execution time list index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_deep_idx/a)))

# now we try some external packages (must be installed in the system for the test)

try:
    from sortedcontainers import SortedDict
    print('-- SortedDict ---------------------------------')

    def performance_sdict_build():
        global dt_root,max_items
        dt = append_item=SortedDict()
        for i in range(max_items):
            for ii in range(max_items):
                append_item['%i_%i' % (i, ii)] = new = SortedDict()
            append_item = new  # we extend on last item (search for this element might be slower)
        dt_root=dt

    def performance_sdict_get_key():
        global dt_root, max_items
        dt=dt_root
        key_list = []
        for i in range(max_items):
            key_list.append(None)
            for ii in range(max_items):
                key_list[-1] = '%i_%i' % (i, ii)
                a = dt
                for k in key_list:
                    a = a[k]
                if type(a) is not SortedDict:
                    raise TypeError('%s is no SortedDict' % repr(a))

    a = timeit.timeit(performance_sdict_build, number=repeat)/ repeat
    print('Execution time SortedDict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
    a = timeit.timeit(performance_sdict_get_key, number=repeat)/ repeat
    print('Execution time SortedDict key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_find_all_by_tag/a)))


except ImportError:
    pass


print('-- xml ElementTree ---------------------------------')

import xml.etree.ElementTree as ET

def performance_et_build():
    global dt_root, max_items
    dt = append_item=ET.Element('root')
    for i in range(max_items):
        for ii in range(max_items):
            new=ET.SubElement(append_item,'%i' % i)
        append_item=new
    dt_root = dt


def performance_et_get_key():
    global dt_root, max_items
    dt = dt_root
    key_list = []
    for i in range(max_items):
        key_list.append(None)
        for ii in range(max_items):
            key_list[-1] = '%i_%i' % (i, ii)
            key='/'.join(key_list)
            a = dt.find(key)

def performance_et_get_idx():
    global dt_root, max_items
    dt = dt_root
    key_list = []
    for i in range(max_items):
        key_list.append(None)
        for ii in range(max_items):
            key_list[-1] = ii
            a = dt
            for k in key_list:
                a=a[k]

a = timeit.timeit(performance_et_build, number=repeat)/ repeat
print('Execution time xml ElementTree build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
if max_items<6000:
    a = timeit.timeit(performance_et_get_key, number=repeat)/ repeat
    print('Execution time xml ElementTree key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_find_all_by_tag/a)))
else:
    print('xml ElementTree key access skipped -> too slow')
a = timeit.timeit(performance_et_get_idx, number=repeat)/ repeat
print('Execution time xml ElementTree index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_deep_idx/a)))

try:
    from anytree import Node, search

    print('-- anytree ---------------------------------')

    def performance_at_build():
        global dt_root, max_items,nodes
        dt = append_item=Node('root')
        for i in range(max_items):
            for ii in range(max_items):
                new = Node('%i' % i,parent=append_item)
            append_item = new
        dt_root = dt

    def performance_at_get_key():
        global dt_root, max_items
        dt = dt_root
        key_list = []
        for i in range(max_items):
            key_list.append(None)
            for ii in range(max_items):
                key_list[-1] = '%i_%i' % (i, ii)
                key = '/'.join(key_list)
                b = search.find(dt, lambda node: node.name == key)
    def performance_at_get_idx():
        global dt_root, max_items
        dt = dt_root
        key_list = []
        for i in range(max_items):
            key_list.append(None)
            for ii in range(max_items):
                key_list[-1] = ii
                a = dt
                for k in key_list:
                    a = a.children[k]

    a = timeit.timeit(performance_at_build, number=repeat) / repeat
    print('Execution time Anytree build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
    if max_items<20:
        a = timeit.timeit(performance_at_get_key, number=repeat) / repeat
        print('Execution time Anytree key access (no cache): {} ~ {:.3f}x faster as iTree'.format(a,(it_find_all_by_tag/a)))
    else:
        print('Anytree key access skipped -> slow')
    #this is somehow not woking:
    a = timeit.timeit(performance_at_get_idx, number=repeat) / repeat
    print('Execution time Anytree index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_deep_idx/a)))

except ImportError:
    pass