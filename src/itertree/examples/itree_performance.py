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


This part of code contains the performance comparison with huge number of elements
"""

from __future__ import absolute_import

import timeit
import os
import tempfile
import sys



#max_items = 5000
max_items = 500000
#max_items = 50000
if len(sys.argv)==2:
    max_items = int(sys.argv[1])

itree_only=False
if len(sys.argv)==2:
    max_items=int(sys.argv[1])
if len(sys.argv)==3:
    max_items=int(sys.argv[1])
    itree_only=int(sys.argv[2])

repeat = 4


print('We run for tree-size: %i with %i repetitions'%(max_items,repeat))


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
    for i in range(max_items):
        dt.insert(1,iTree('%i' % i))

def performance_it_build():
    #tag access
    global dt_root,max_items
    dt = iTree('root')
    #dt.pre_alloc_list(max_items)
    #append itertree with items
    for i in range(max_items):
        dt.append(iTree('%i' % i))
    dt_root=dt

def performance_it_build2():
    #tag access
    global dt_root,max_items
    dt = iTree('root')
    #append itertree with items
    dt=iTree('root',subtree=[iTree('%i' % i) for i in range(max_items)])
    dt_root=dt

def performance_it_get_tags():
    #tag access
    global dt_root,max_items
    dt=dt_root

    #read itertree items per tag and index
    for i in range(max_items):
        a = dt['%i' % i]

def performance_it_get_tags():
    #tag access
    global dt_root,max_items
    dt=dt_root

    #read itertree items per tag and index
    for i in range(max_items):
        a = dt['%i' % i]

def performance_it_get_tag_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    # we use a pre allocation
    for i in range(max_items):
        a = dt[TagIdx('%i' % i,0)]
        #a = dt[('%i' % i,0)]

def performance_it_get_tag_idx_tuple():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    # we use a pre allocation
    for i in range(max_items):
        a = dt[('%i' % i,0)]

def performance_it_get_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    for i in range(max_items):
        a = dt[i]

def performance_it_iter_all_to_list():
    #tag access
    global dt_root,max_items
    dt=dt_root
    list(dt.iter_all())

def performance_it_dump():
    global dt_root,fh
    fh.seek(0)
    dt_root.dump(fh,calc_hash=False)

def performance_it_load():
    global dt_root, fh,load_root
    fh.seek(0)
    load_root=iTree('tmp').load(fh)

it_append = timeit.timeit(performance_it_build, number=repeat)/repeat
print('Execution time itertree build: {}'.format(it_append))
it_listcomprehension = timeit.timeit(performance_it_build2, number=repeat)/repeat
print('Execution time itertree build: with subtree list comprehension: {}'.format(it_listcomprehension))
if blist is None:
    print('Insertion of items will be relative slow because blist package is not available in your installation '
          '(normal list insertion must be used by the itertree package)')
it_insert = timeit.timeit(performance_it_build_insert, number=repeat)/repeat
print('Execution time itertree build (with insert): {}'.format(it_insert))


it_get_tag = timeit.timeit(performance_it_get_tags, number=repeat)/repeat
print('Execution time itertree tag access: {}'.format(it_get_tag))
it_get_tag_idx = timeit.timeit(performance_it_get_tag_idx, number=repeat)/repeat
print('Execution time itertree tag index access: {}'.format(it_get_tag_idx))
it_get_tag_idx_tuple = timeit.timeit(performance_it_get_tag_idx_tuple, number=repeat)/repeat
print('Execution time itertree tag index tuple access: {}'.format(it_get_tag_idx_tuple))
it_get_idx = timeit.timeit(performance_it_get_idx, number=repeat)/repeat
print('Execution time itertree index access: {}'.format(it_get_idx))
it_iter_all_list = timeit.timeit(performance_it_iter_all_to_list, number=repeat)/repeat
print('Execution time itertree convert iter_all iterator to list: {}'.format(it_iter_all_list))

it_dump = timeit.timeit(performance_it_dump, number=repeat)/ repeat
print('Execution time itertree save to file: {}'.format(it_dump ))
it_load = timeit.timeit(performance_it_load, number=repeat)/ repeat
print('Execution time itertree load from file: {}'.format(it_load ))

print('Loaded iTree is equal: %s'%(str(dt_root.equal(load_root))))

if itree_only:
    exit(0)

try:
    from pytoolingtree import Node

    print('-- PyTooling.Tree ---------------------------------')


    def performance_ptt_build():
        global dt_root, max_items
        dt = Node()
        for i in range(max_items):
            dt.AddChild(Node('%i' % i))
        dt_root = dt

    def performance_ptt_get_key():
        global dt_root, max_items
        dt = dt_root
        for i in range(max_items):
            a = dt.GetNodeByID('%i' % i)

    def performance_ptt_get_idx():
        global dt_root, max_items
        dt = dt_root
        for i in range(max_items):
            a = list(dt.GetChildren())[i]

    a = timeit.timeit(performance_ptt_build, number=repeat)/ repeat
    print('Execution time PyTooling.Tree build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
    a = timeit.timeit(performance_ptt_get_key, number=repeat)/ repeat
    print('Execution time PyTooling.Tree key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag/a)))
    if max_items<6000:
        a = timeit.timeit(performance_ptt_get_idx, number=repeat)/ repeat
        print('Execution time PyTooling.Tree index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_idx/a)))
    else:
        print('Execution time PyTooling.Tree index access skipped incredible slow')

except:
    pass

try:
    from lldict4 import llDict as llDict2

    print('-- llDict2 ---------------------------------')

    def performance_lldict_build():
        global dt_root,max_items
        dt = llDict2()
        for i in range(max_items):
            dt['%i' % i] = llDict2()
        dt_root=dt

    def performance_lldict_get_key():
        global dt_root, max_items
        dt=dt_root
        for i in range(max_items):
            a = dt['%i' % i]

    def performance_lldict_save():
        global dt_root, max_items
        dt_root.dump(TMP_FOLDER + '/perfomance1.cf2', overwrite=True,struct_str=False)

    def performance_lldict_load():
        global dt_root, max_items
        new_dict=dt_root.create_from_file(TMP_FOLDER + '/perfomance1.cf2')

    a = timeit.timeit(performance_lldict_build, number=repeat)/repeat
    print('Execution time llDict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
    a = timeit.timeit(performance_lldict_get_key, number=repeat)/repeat
    print('Execution time llDict key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag/a)))
    a = timeit.timeit(performance_lldict_save, number=repeat) / repeat
    print('Execution time llDict save: {} ~ {:.3f}x faster as iTree'.format(a,(it_dump/a)))
    a = timeit.timeit(performance_lldict_load, number=repeat)/ repeat
    print('Execution time llDict load: {} ~ {:.3f}x faster as iTree'.format(a,(it_load/a) ))

except ImportError:
    pass



# we compare here with dict, OrderedDict and list
print('-- Standard classes -----------------------------------')


def performance_dict_build():
    #tag access
    global dt_root,max_items
    dt = {}
    #append itertree with items
    for i in range(max_items):
        dt['%i' % i]=0
    dt_root=dt

def performance_dict_get_keys():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    for i in range(max_items):
        a = dt['%i' % i]

def performance_dict_get_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    for i in range(max_items):
        a = list(dt.keys())[i]

def performance_list_build():
    #tag access
    global dt_root,max_items
    dt = []
    #append itertree with items
    #for i in range(max_items):
    #    dt.append(['%i' % i])
    dt=['%i'%i for i in range(max_items)]
    dt_root=dt

def performance_list2_build():
    #tag access
    global dt_root,max_items
    dt = []
    #append itertree with items
    #for i in range(max_items):
    #    dt.append(['%i' % i])
    for i in range(max_items):
        dt.append('%i'%i)
    dt_root=dt

def performance_list3_build():
    #tag access
    global dt_root,max_items
    dt = []
    #append itertree with items
    #for i in range(max_items):
    #    dt.append(['%i' % i])
    for i in range(max_items):
        dt.insert(0,'%i'%i)
    dt_root=dt

def performance_list_get_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    for i in range(max_items):
        a = dt[i]

def performance_list_get_key():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    for i in range(max_items):
        a = dt[dt.index('%i'%i)]

a = timeit.timeit(performance_dict_build, number=repeat) / repeat
print('Execution time dict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
a = timeit.timeit(performance_dict_get_keys, number=repeat)/ repeat
print('Execution time dict key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag/a) ))
if max_items<6000:
    a = timeit.timeit(performance_dict_get_idx, number=repeat)/ repeat
    print('Execution time dict index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_idx/a)))
else:
    print('Execution time dict index access: skipped incredible slow')
a = timeit.timeit(performance_list_build, number=repeat)/ repeat
print('Execution time list build (via comprehension): {} ~ {:.3f}x faster as iTree'.format(a,(it_listcomprehension/a) ))
a = timeit.timeit(performance_list2_build, number=repeat)/ repeat
print('Execution time list build (via append): {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a) ))
if max_items<6000:

    a = timeit.timeit(performance_list3_build, number=repeat)/ repeat
    print('Execution time list build (via insert): {} ~ {:.3f}x faster as iTree'.format(a,(it_insert/a) ))
else:
    print('Execution time list build (via insert): Skipped very slow')

a = timeit.timeit(performance_list_get_idx, number=repeat) / repeat
print('Execution time list index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_idx/a)))
if max_items<6000:
    a = timeit.timeit(performance_list_get_key, number=repeat)/ repeat
    print('Execution time list key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag/a) ))
else:
    print('Execution time list key access: Skipped incredible slow')

from collections import OrderedDict,deque

def performance_odict_build():
    #tag access
    global dt_root,max_items
    dt = OrderedDict()
    #append itertree with items
    for i in range(max_items):
        dt['%i' % i]=0
    dt_root=dt

def performance_odict_get_keys():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    for i in range(max_items):
        a = dt['%i' % i]

def performance_deque_build():
    #tag access
    global dt_root,max_items
    dt = deque()
    #append itertree with items
    for i in range(max_items):
        dt.append(['%i' % i])
    dt_root=dt

def performance_deque_build2():
    #tag access
    global dt_root,max_items
    dt = deque()
    #append itertree with items
    for i in range(max_items):
        dt.insert(0,['%i' % i])

def performance_deque_get_idx():
    #tag access
    global dt_root,max_items
    dt=dt_root
    #read itertree items per tag and index
    for i in range(max_items):
        a = dt[i]

a = timeit.timeit(performance_odict_build, number=repeat)/ repeat
print('Execution time OrderedDict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a) ))
a = timeit.timeit(performance_odict_get_keys, number=repeat)/ repeat
print('Execution time OrderedDict key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag) ))
a = timeit.timeit(performance_deque_build, number=repeat)/ repeat
print('Execution time deque build (append): {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a) ))
a = timeit.timeit(performance_deque_build2, number=repeat)/ repeat
print('Execution time deque build (insert): {} ~ {:.3f}x faster as iTree'.format(a,(it_insert/a) ))
a = timeit.timeit(performance_deque_get_idx, number=repeat)/ repeat
print('Execution time deque index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_idx/a) ))

try:
    from indexed import IndexedOrderedDict
    def performance_iodict_build():
        #tag access
        global dt_root,max_items
        dt = IndexedOrderedDict()
        #append itertree with items
        for i in range(max_items):
            dt['%i' % i]=0
        dt_root=dt

    def performance_iodict_get_keys():
        #tag access
        global dt_root,max_items
        dt=dt_root
        #read itertree items per tag and index
        for i in range(max_items):
            a = dt['%i' % i]

    def performance_iodict_get_idx():
        #tag access
        global dt_root,max_items
        dt=dt_root
        #read itertree items per tag and index
        for i in range(max_items):
            a = dt.values()[i]


    a = timeit.timeit(performance_iodict_build, number=repeat)/ repeat
    print('Execution time IndexedOrderedDict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
    a = timeit.timeit(performance_iodict_get_keys, number=repeat)/ repeat
    print('Execution time IndexedOrderedDict key access: {} ~ {:.3f}x faster as iTree'.format(a , (it_get_tag)))
    a = timeit.timeit(performance_iodict_get_idx, number=repeat)/ repeat
    print('Execution time IndexedOrderedDict idx access: {} ~ {:.3f}x faster as iTree'.format(a , (it_get_idx/a)))

except ImportError:
    pass



# now we try some external packages (must be installed in the system for the test)

try:
    from sortedcontainers import SortedDict
    print('-- SortedDict ---------------------------------')

    def performance_sdict_build():
        global dt_root,max_items
        dt = SortedDict()
        for i in range(max_items):
            dt['%i' % i] = SortedDict()
        dt_root=dt

    def performance_sdict_get_key():
        global dt_root, max_items
        dt=dt_root
        for i in range(max_items):
            a = dt['%i' % i]

    def performance_sdict_get_idx():
        global dt_root, max_items
        dt=dt_root
        for i in range(max_items):
            a = dt.peekitem(i)

    a = timeit.timeit(performance_sdict_build, number=repeat)/ repeat
    print('Execution time SortedDict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a) ))
    a = timeit.timeit(performance_sdict_get_key, number=repeat)/ repeat
    print('Execution time SortedDict key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag/a) ))
    a = timeit.timeit(performance_sdict_get_idx, number=repeat)/ repeat
    print('Execution time SortedDict index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_idx/a)))


except ImportError:
    pass

try:
    from lldict2 import llDict as llDict2
    print('-- llDict2 ---------------------------------')

    def performance_lldict_build():
        global dt_root,max_items
        dt = llDict2()
        for i in range(max_items):
            dt['%i' % i] = llDict2()
        dt_root=dt

    def performance_lldict_get_key():
        global dt_root, max_items
        dt=dt_root
        for i in range(max_items):
            a = dt['%i' % i]

    def performance_lldict_get_idx():
        global dt_root, max_items
        dt=dt_root
        for i in range(max_items):
            a = dt.peekitem(i)

    a = timeit.timeit(performance_sdict_build, number=repeat)/ repeat
    print('Execution time llDict build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a) ))
    a = timeit.timeit(performance_sdict_get_key, number=repeat)/ repeat
    print('Execution time llDict key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag/a)))

except ImportError:
    pass

try:
    from lldict3 import llDict as llDict3
    print('-- llDict3 ---------------------------------')

    def performance_lldict_build():
        global dt_root,max_items
        dt = llDict3()
        for i in range(max_items):
            dt['%i' % i] = llDict3()
        dt_root=dt

    def performance_lldict_get_key():
        global dt_root, max_items
        dt=dt_root
        for i in range(max_items):
            a = dt['%i' % i]

    def performance_lldict_get_idx():
        global dt_root, max_items
        dt=dt_root
        for i in range(max_items):
            a = dt.peekitem(i)

    a = timeit.timeit(performance_sdict_build, number=repeat)/ repeat
    print('Execution time llDict3 build: {}  ~ {:.3f}x faster as iTree'.format(a ,(it_append/a)))
    a = timeit.timeit(performance_sdict_get_key, number=repeat)/ repeat
    print('Execution time llDict3 key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag/a)))

except ImportError:
    pass


print('-- xml ElementTree ---------------------------------')

import xml.etree.ElementTree as ET

def performance_et_build():
    global dt_root, max_items
    dt = ET.Element('root')
    for i in range(max_items):
        ET.SubElement(dt,'%i' % i)
    dt_root = dt


def performance_et_get_key():
    global dt_root, max_items
    dt = dt_root
    for i in range(max_items):
        a = dt.find('%i' % i)


def performance_et_get_idx():
    global dt_root, max_items
    dt = dt_root
    for i in range(max_items):
        a=dt[i]


a = timeit.timeit(performance_et_build, number=repeat)/ repeat
print('Execution time xml ElementTree build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a) ))
if max_items<6000:
    a = timeit.timeit(performance_et_get_key, number=repeat)/ repeat
    print('Execution time xml ElementTree key access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_idx/a)))
else:
    print('xml ElementTree key access skipped -> too slow')
a = timeit.timeit(performance_et_get_idx, number=repeat)/ repeat
print('Execution time xml ElementTree index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_tag/a)))

try:
    from anytree import Node, search

    print('-- anytree ---------------------------------')

    def performance_at_build():
        global dt_root, max_items,nodes
        dt = Node('root')
        for i in range(max_items):
            b=Node('%i' % i, parent=dt)
        dt_root = dt

    def performance_at_get_key():
        global dt_root, max_items
        dt = dt_root
        for i in range(max_items):
            b = search.find(dt, lambda node: node.name == "%i" % i)

    def performance_at_get_idx():
        global dt_root, max_items
        dt = dt_root
        for i in range(max_items):
            b = dt.children[i]

    a = timeit.timeit(performance_at_build, number=repeat)/ repeat
    print('Execution time Anytree build: {} ~ {:.3f}x faster as iTree'.format(a,(it_append/a)))
    if max_items<6000:
        a = timeit.timeit(performance_at_get_key, number=repeat)/ repeat
        print('Execution time Anytree key access (no cache): {} ~ {:.6f}x faster as iTree'.format(a,(it_get_tag/a)))
    else:
        print('Anytree key access skipped -> incredible slow')
    #this is somehow not woking:
    if max_items<6000: # not working for huge sizes!
        a = timeit.timeit(performance_at_get_idx, number=repeat)/ repeat
        print('Execution time Anytree index access: {} ~ {:.3f}x faster as iTree'.format(a,(it_get_idx/a) ))
    else:
        print('Execution time Anytree index access: not working')

except ImportError:
    pass