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


This part of code contains the performance comparison with deep trees
"""


from __future__ import absolute_import

import timeit
import os
import tempfile
import itertools
import sys

max_items = 150
#max_items=20
itree_only=False

if len(sys.argv)==2:
    max_items=int(sys.argv[1])
if len(sys.argv)==3:
    max_items=int(sys.argv[1])
    itree_only=int(sys.argv[2])

#max_items = 20

repeat = 4


print('We run for deep tree sizes: depth of %i with %i items and %i repetitions'%(max_items,max_items*max_items,repeat))

from itertree import iTree, __version__,TagIdx
print('itertree version: %s'%__version__)

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

a = timeit.timeit(performance_it_build_insert, number=repeat)
print('Exectime time itertree build (with insert): {}'.format(a / repeat))
a = timeit.timeit(performance_it_build, number=repeat)
print('Exectime time itertree build append: {}'.format(a / repeat))
a = timeit.timeit(performance_it_get_max_children_depth, number=1) # we run this only one time
print('Exectime time itertree get max_depth_down~iter_all(): {}'.format(a / repeat))
a = timeit.timeit(performance_it_get_deep_by_idx, number=repeat)
print('Exectime time itertree get deep indexes access (all items iterated): {}'.format(a / repeat))
a = timeit.timeit(performance_it_find_all_by_idx, number=repeat)
print('Exectime time itertree get find_all by indexes access (all items iterated): {}'.format(a / repeat))
a = timeit.timeit(performance_it_find_all_by_tag, number=repeat)
print('Exectime time itertree find all by deep tag list (one deep search last item): {}'.format(a / repeat))
if max_items <=60:
    a = timeit.timeit(performance_it_dump, number=repeat)
    print('Exectime time itertree save to file: {}'.format(a / repeat))
    a = timeit.timeit(performance_it_load, number=repeat)
    print('Exectime time itertree load from file: {}'.format(a / repeat))
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

    a = timeit.timeit(performance_lldict_build, number=repeat)
    print('Exectime time llDict build: {}'.format(a / repeat))
    a = timeit.timeit(performance_lldict_get_key, number=repeat)
    print('Exectime time llDict key access: {}'.format(a / repeat))
    if max_items<=60:
        a = timeit.timeit(performance_lldict_save, number=repeat)
        print('Exectime time llDict save: {}'.format(a / repeat))
        a = timeit.timeit(performance_lldict_load, number=repeat)
        print('Exectime time llDict load: {}'.format(a / repeat))

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

a = timeit.timeit(performance_dict_build, number=repeat)
print('Exectime time dict build: {}'.format(a / repeat))
a = timeit.timeit(performance_dict_get_keys, number=repeat)
print('Exectime time dict key access: {}'.format(a / repeat))
a = timeit.timeit(performance_list_build, number=repeat)
print('Exectime time list build (via comprehension): {}'.format(a / repeat))

a = timeit.timeit(performance_list_get_idx, number=repeat)
print('Exectime time list index access: {}'.format(a / repeat))

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

    a = timeit.timeit(performance_sdict_build, number=repeat)
    print('Exectime time SortedDict build: {}'.format(a / repeat))
    a = timeit.timeit(performance_sdict_get_key, number=repeat)
    print('Exectime time SortedDict key access: {}'.format(a / repeat))


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

a = timeit.timeit(performance_et_build, number=repeat)
print('Exectime time xml ElementTree build: {}'.format(a / repeat))
if max_items<6000:
    a = timeit.timeit(performance_et_get_key, number=repeat)
    print('Exectime time xml ElementTree key access: {}'.format(a / repeat))
else:
    print('xml ElementTree key access skipped -> too slow')
a = timeit.timeit(performance_et_get_idx, number=repeat)
print('Exectime time xml ElementTree index access: {}'.format(a / repeat))

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

    a = timeit.timeit(performance_at_build, number=repeat)
    print('Exectime time Anytree build: {}'.format(a / repeat))
    if max_items<20:
        a = timeit.timeit(performance_at_get_key, number=repeat)
        print('Exectime time Anytree key access (no cache): {}'.format(a / repeat))
    else:
        print('Anytree key access skipped -> slow')
    #this is somehow not woking:
    a = timeit.timeit(performance_at_get_idx, number=repeat)
    print('Exectime time Anytree index access: {}'.format(a / repeat))

except ImportError:
    pass