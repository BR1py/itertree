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
import sys
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
from itertree.itree_serializer.itree_json_converter import Converter_1_1_1_to_2_0_0

root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

TEST_SELECTION = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
# TEST_SELECTION={}

print('Test start')


def get_relpath_to_root(item_path):
    new_path = item_path.replace(root_path, '')
    if new_path.startswith('\\'):
        new_path = new_path[1:]
    if new_path.startswith('/'):
        new_path = new_path[1:]
    return root_path + '/' + new_path

def get_tmp_path(clean=False):
    if not sys.platform.startswith('win'):
        tmp_path= '/tmp/itertree_test'
        try:
            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path)
                clean=False
        except:
            tmp_path = get_relpath_to_root('tmp')
    else:
        tmp_path = get_relpath_to_root('tmp')
    if clean and os.path.exists(tmp_path):
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        os.makedirs(tmp_path)
    return tmp_path

class Test1_Serializers:

    def large_itree(self,number_per_level,tags=[],counter_var=None,_root=None,_count=0):
        counters=[]
        for tag in tags:
            if tag==counter_var:
                counters.append(0)

            elif type(tag) is tuple:
                sub_counters=[]
                for i,t in enumerate(tag):
                    if t ==counter_var:
                        sub_counters.append(i)
                counters.append(sub_counters)
            elif type(tag) is str and '%i' in tag:
                counters.append(1)
            else:
                counters.append(None)
        if _root is None:
            root=iTree('root')
        else:
            root=_root
        cnt=_count
        level=len(number_per_level)-1
        for i in range(number_per_level[0]):
            for update,tag in zip(counters,tags):
                if update==0:
                    cnt += 1
                    sub_item=iTree(i,cnt)
                elif update == 1:
                    cnt += 1
                    sub_item = iTree(tag % i, cnt)
                elif update is None:
                    cnt += 1
                    sub_item = iTree(tag, cnt)
                elif type(tag) is tuple:
                    tag = list(tag)
                    for ii in update:
                        tag[ii]=i
                    cnt += 1
                    sub_item = iTree(tuple(tag), cnt)
                else:
                    cnt += 1
                    sub_item = iTree(tag, cnt)
                if level!=0:
                    sub=number_per_level[1:]
                    sub_item,cnt=self.large_itree(sub,tags,counter_var,sub_item,cnt)
                root.append(sub_item)
        return root,cnt


    def test1_std_renderer_of_iTree(self):
        if not 1 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: std. renderer of iTree')
        # ToDo
        print('\nRESULT OF TEST: std. renderer of iTree - PASS')

    def test2_pickle_iTree(self):
        if not 2 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: pickle iTree')

        itree1 = iTree(0, 0)
        itree1 += iTree(11, 1)
        itree1 += iTree(11, 2)
        itree1 += iTree(11, 3)
        itree1 += iTree(11, 4)

        itree1b = itree1.copy()
        itree1[1].append(itree1b)

        itree2 = iTree(0, 0)
        itree2 += iTree(11, 1)
        itree2 += iTree(11, 2)
        itree2 += iTree(11, 3)
        itree2 += iTree(11, 4)
        itree2 += iTree(11, 5)

        itree1[2].append(itree2)
        itree1b.append(iTree('complex data', {1: 2, 'adsAD': 1213}))

        pickle_str = pickle.dumps(itree1)
        itree_new = pickle.loads(pickle_str)
        assert itree_new == itree1
        # but other instance
        assert itree_new is not itree1

        # value related test

        itree2.set_value([[1,2,3],[4,5,6]])
        itree3=itree2.copy()
        assert itree3.value is not itree2.value
        assert itree3.value[0] is itree2.value[0]
        assert itree3.value[1] is itree2.value[1]

        largetree,size=self.large_itree([4,32,1000],['itag',(1,'cnt')],'cnt') # 1 million items!
        pickle_str = pickle.dumps(largetree)
        itree_new = pickle.loads(pickle_str)
        assert largetree==itree_new
        t1=timeit.timeit(lambda: largetree==itree_new,number=1)
        t2=timeit.timeit(lambda: hash(largetree),number=1)
        print(size,t1,t2)

        print('\nRESULT OF TEST: pickle iTree - pass')

    def test3_save_load_serializers_iTree(self):
        if not 3 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: save load serializers iTree')
        #build a bigger tree
        root=iTree('root',0)
        root.extend([iTree('%i'%i,i) for i in range(1,1000)])
        #append some types of data
        root[0].append(iTree('str','data'))
        root[0].append(iTree('bytes', b'bytes'))
        root[0].append(iTree('float', 12.45))
        root[1].append(iTree('list', ['data', b'bytes', 1, 12.45]))
        root[1].append(iTree('tuple', ('data', b'bytes', 1, 12.45)))
        root[1].append(iTree('mix', [(0, 'data', b'bytes', 1, 12.45),
                                     (1, 'data', b'bytes', 1, 12.45),
                                     (2, 'data', b'bytes', 1, 12.45),
                                     [3, 'data', b'bytes', 1, 12.45]]))
        root[2].append(iTree('dict', {1: ('data', b'bytes', 1, 12.45),
                                      '2': ('data', b'bytes', 1, 12.45),
                                      3: ('data', b'bytes', 1, 12.45),
                                      (4, 0): ['data', b'bytes', 1, 12.45],
                                      }))
        root[2].append(iTree('odict', OrderedDict([(1, ('data', b'bytes', 1, 12.45)),
                                                   (2, ('data', b'bytes', 1, 12.45)),
                                                   (3, ('data', b'bytes', 1, 12.45)),
                                                   ((4, 0), ['data', b'bytes', 1, 12.45])])))
        root[2].append(iTree('dictdict', {1: {},
                                          '2': {'22': ('data', b'bytes', 1, 12.45),
                                                3: ('data', b'bytes', 1, 12.45),
                                                (4, 0): ['data', b'bytes', 1, 12.45]}}))
        if np is not None:
            root[3].append(iTree('numpy', np.zeros(100, dtype=np.int8)))
            root[3].append(iTree('numpy', np.ones(100, dtype=np.float64)))
            root[3].append(iTree('numpy', np.array([np.zeros(100, dtype=np.int8),
                                                    np.ones(100, dtype=np.int8)])))
            root[3].append(iTree('numpy', np.random.rand(3, 2)))


        #item=root[4]
        item=root.insert(0,iTree('level 1'))
        for i in range(3):
            item=item.append(iTree('level %i'%(i+2)))
        tmp_dir=get_tmp_path(True)
        file_path=os.path.join(tmp_dir,'test.itz')
        root.dump(file_path)
        print('iTree dumped in: {}'.format(file_path))

        load_tree=iTree().load(file_path)
        assert load_tree[3][0]==root[3][0]
        diff=root-load_tree
        for i,ii in zip(load_tree.deep, root.deep):
            if i!=ii:
                a=(i==ii)
                print(i)
                print(ii)
        assert load_tree==root
        print('\nRESULT OF TEST: save load serializers  iTree - pass')


class Test2_Converter:

    def test1_convert(self):
        source_file=root_path+'/test_converter/out.itr'
        try:
            new_itree=Converter_1_1_1_to_2_0_0(source_file)
        except ImportError:
            if np is None:
                print('numpy required for this test run')
                pass
        else:
            assert new_itree.tag=='root'
            assert len(new_itree.deep) == 119

    def test2_convert(self):
        source_file=root_path+'/test_converter/out.itz'
        try:
            new_itree=Converter_1_1_1_to_2_0_0(source_file)
        except ImportError:
            if np is None:
                print('numpy required for this test run')
                pass
        else:
            assert new_itree.tag=='root'
            assert len(new_itree.deep) == 12

    def test3_convert(self):
        source_file=root_path+'/test_converter/out2.itz'
        try:
            new_itree=Converter_1_1_1_to_2_0_0(source_file)
        except ImportError:
            if np is None:
                print('numpy required for this test run')
                pass
        else:
            assert new_itree.tag=='root'
            assert len(new_itree.deep) == 153
            new_itree.render()

    def test4_convert(self):
        source_file=root_path+'/test_converter/out_linked.itr'
        try:
            new_itree=Converter_1_1_1_to_2_0_0(source_file)
        except ImportError:
            if np is None:
                print('numpy required for this test run')
                pass
        else:
            assert new_itree.tag=='root'
            assert len(new_itree.deep) == 36
            #new_itree.render()




