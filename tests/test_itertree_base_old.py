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
import sys
import collections
import timeit
import pytest

try:
    import numpy as np
    # only needed in case of numpy arrays in data
    # for serializing the data
except:
    np = None

from itertree import *
from itertree.itree_data import iTData
from itertree.itree_helpers import BLIST_ACTIVE
mSetInterval=Filters.mSetInterval
mSetCombine=Filters.mSetCombine

root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

TEST_SELECTION = {1, 2, 3, 4, 5, 6, 7, 8, 10}
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

def get_tmp_path():
    if not sys.platform.startswith('win'):
        tmp_path= '/tmp/itertree_test'
        try:
            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path)
        except:
            tmp_path = get_relpath_to_root('tmp')
    else:
        tmp_path = get_relpath_to_root('tmp')
    return tmp_path

def calc_timeit(check_method, number):
    min_time = float('inf')
    for _ in range(number):
        t = timeit.timeit(check_method, number=1)
        if t < min_time:
            min_time = t
    return min_time


class Test_iTreeBase:
    def _build_mix_tree(self):
        root = iTree('root')
        root += iTree('c1', value=0)
        root += iTree('c2', value=1)
        root += iTree((0,), value=2)
        root += iTree('c2', value=3)
        root += iTree((1,), value=4)
        root += iTree('c2', value=5)
        root += iTree((1,), value=6)
        root += iTree('c2', value=7)
        root += iTree((1,), value=8)
        root += iTree('c2', value=9)
        root += iTree('c3', value=10)
        root += iTree((2,), value=11)
        # this will do internal copies!
        root[2].extend(root)
        root[2][2].extend(root)
        root[3].extend(root)
        return root

    def _build_base_tree(self):
        # build a tree
        root = iTree('root', value={'level': ()})
        # append subitems via +=
        root += iTree('sub1', value={'level': (1, -1)})
        root += iTree('sub2', value={'level': (2, -1)})
        # append subitems via append()
        root.append(iTree('sub3', value={'level': (3, -1)}))
        # insert first element via appendleft
        root.appendleft(iTree('sub0', value={'level': (0, -1)}))
        # append in deeper level via += and select last subelement via [-1]
        sub3_0 = iTree('sub3_0', value={'level': (3, 0)})
        root[-1] += sub3_0
        # append next element via append()
        root[-1].append(iTree('sub3_2', value={'level': (3, 2)}))
        # insert in between the other elements
        root[('sub3', 0)].insert(1, iTree('sub3_1', value={'level': (3, 1)}))
        # build alist and extend
        subtree = [iTree('sub2_0', value={'level': (2, 0)}),
                   iTree('sub2_1', value={'level': (2, 1)}),
                   iTree('sub2_3', value={'level': (2, 3)}),
                   iTree('sub2_4', value={'level': (2, 4)}),
                   iTree('sub2_2', value={'level': (2, 2)})
                   ]
        root[2].extend(subtree)

        # root[2][TagIdx('sub2_2', 0)]+=iTree('sub2_2_0')
        # root[2][TagIdx('sub2_2', 0)] += iTree('sub2_2_1')
        # root[2][TagIdx('sub2_2', 0)] += iTree('sub2_2_2')

        # move an existing item
        root[2][('sub2_2', 0)].move(2)

        # extendleft a iTree
        root[0] += iTree('sub0_3', value={'level': (0, 3)})
        subtree = iTree('extend', subtree=[iTree('sub0_0', value={'level': (0, 0)}),
                                           iTree('sub0_1', value={'level': (0, 1)}),
                                           iTree('sub0_2', value={'level': (0, 2)})])
        root[0].extendleft(subtree)

        s4 = iTree('sub4', value={'level': (4, -1)})
        root += s4

        # append multiples
        s4.extend(iTree('sub4_n', value={'level': ('n')}) * 100)
        for i in range(len(s4)):
            s4[i].set_value({'level': 'n%i' % i})

        # Serializer.DTRenderer().render(root)
        return root

    def test1_dt_base_test(self):
        ''''
        we build a tree with some entries and then we try to access the elements
        '''
        if not 1 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: datatree base test')
        root = self._build_base_tree()

        # access possibilities
        assert root[3][1].value['level'] == (3, 1)
        assert root[('sub2', 0)][0].value['level'] == (2, 0)
        assert root[('sub2', 0)][1].value['level'] == (2, 1)

        # test some properties
        assert root[('sub2', 0)].pre_item.tag == 'sub1'
        assert root[('sub2', 0)].post_item.tag == 'sub3'
        assert root[('sub2', 0)].level == 1
        assert root[0][1].idx_path == (0, 1)
        assert root[0][1].tag_idx_path == (('sub0', 0), ('sub0_1', 0))

        # check for error in case item is already added
        item = root[-1][0]
        with pytest.raises(RecursionError):
            root[-1] += item

        # test some iterators
        for i, item in enumerate(root):
            assert item.value['level'][0] == i, "%i,%s" % (i, repr(item))

        for i, item in enumerate(root[0]):
            assert item.value['level'][1] == i

        # top-> down iter
        lookup = [-1, 0, 1, 2, 3, -1, -1, 0, 1, 2, 3, 4, -1, 0, 1, 2, -1]
        cnt = 0

        #root.render()

        for i, item in enumerate(root.deep):
            # print(i,lookup[i],repr(item))
            if i < len(lookup):
                assert item.value['level'][1] == lookup[i], "%i-> %i, %s" % (i, lookup[i], repr(item))
            else:
                cnt += 1
        assert i == len(root.deep) - 1

        # down->top iter
        lookup = [0, 1, 2, 3, -1, -1, 0, 1, 2, 3, 4, -1, 0, 1, 2, -1]
        for i, item in enumerate(root.deep.iter(up_to_low=False)):
            # print(item,i,lookup[i])
            if i < len(lookup):
                assert item.value['level'][1] == lookup[i]
        a = repr(root)

        root2 = self._build_mix_tree()
        #root2.render()
        assert root2[((1,), 1)].value == 6
        #root2[((0,), 0)][2].render()
        assert len(root2[((0,), 0)][2]) == root2[((0,), 0)][2][-1].value+1

        #appending data only:
        new_tree=iTree('root')
        new_tree.append(1)
        new_tree.append('hello')
        new_tree.append(2)
        new_tree.append(3)
        new_tree.append(4)

        assert new_tree[0].value==1
        assert new_tree[1].value == 'hello'
        assert new_tree[0].tag==NoTag
        assert new_tree[1].tag_idx == (NoTag, 1)
        assert list(new_tree[(NoTag,slice(1,4,2))])==[new_tree[1],new_tree[3]]
        
        print('PASSED')

    def test2_tree_manipulations(self):
        if not 2 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: base tree manipulations functions')
        '''
        testing all setters: append(),insert(), replace, rename(),...
        '''
        root = self._build_base_tree()

        # append/appendleft
        root.append(iTree('append'))
        assert root[-1].tag == 'append'
        assert root[-1].parent == root

        root.appendleft(iTree('appendleft'))
        assert root[0].tag == 'appendleft'
        assert root[0].parent == root

        # extend/extendleft
        extend_dt = iTree('extend_dt', subtree=[iTree('extend1'), iTree('extend2')])
        root.extend(extend_dt)
        assert root[-2].tag == 'extend1'
        assert root[-2].parent == root
        assert root[-1].tag == 'extend2'
        assert root[-2].parent == root

        root.extend([iTree('extend3'), iTree('extend4')])
        assert root[-2].tag == 'extend3'
        assert root[-2].parent == root
        assert root[-1].tag == 'extend4'
        assert root[-1].parent == root

        extendl_dt = iTree('extendl_dt', subtree=[iTree('extendleft1'), iTree('extendleft2')])
        root.extendleft(extendl_dt)
        assert root[0].tag == 'extendleft1'
        assert root[0].parent == root
        assert root[1].tag == 'extendleft2'
        assert root[1].parent == root
        root.extendleft([iTree('extendleft3'), iTree('extendleft4')])
        assert root[0].tag == 'extendleft3'
        assert root[0].parent == root
        assert root[1].tag == 'extendleft4'
        assert root[1].parent == root

        # insert
        root.insert(5, iTree('insert'))
        assert root[5].tag == 'insert'
        assert root[5].parent == root

        root.insert(-1, iTree('insert2'))
        assert root[len(root) - 2].tag == 'insert2', repr(root)
        assert root[-2].tag == 'insert2', repr(root)
        assert root[-2].parent == root

        # replace
        root[2] = iTree('replace2')
        assert root[2].tag == 'replace2'
        assert root[2].parent == root
        root[-1] = iTree('replace1')
        assert root[-1].tag == 'replace1'
        assert root[-1].parent == root

        # move
        root[2].move(-1)
        assert root[-2].tag == 'replace2'
        assert root[2].tag == 'extendleft2'
        root[-2].move(2)
        assert root[2].tag == 'replace2'

        # rename
        root[2].rename('rename')
        assert root[2].tag == 'rename'
        assert root['rename'][0] is root[2]
        with pytest.raises(KeyError):
            assert root['replace2']

        print('PASSED')

    def test3_base_operators(self):
        '''
        operator test
        += -> append
        -= -> append left
        << -> replace
        * -> multiply list of copied elements (is already tested )
        and delete
        del item
        '''
        if not 3 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: base operators and delete')
        root = iTree('root')

        # iadd
        root += iTree('SUB1')
        assert len(root) == 1
        assert root[0].tag == 'SUB1'

        # multiple append
        root = root[0] * 100
        assert len(root) == 100
        assert root[99].tag == 'SUB1'
        assert id(root[99]) != id(root[0])

        # add two iterables
        root2 = [iTree('1'), iTree('2'), iTree('3'), iTree('4')] + list(iTree('B', subtree=[iTree('5'),
                                                                                       iTree('6'),
                                                                                       iTree('7'),
                                                                                       iTree('8')]))
        # equal, etc.
        assert len(root2) == 8
        assert root2[0].tag == '1'
        assert root2[-1].tag == '8'

        assert root > root2
        assert root >= root2
        assert not root < root2
        assert not root <= root2
        assert not root == root2
        assert root != root2

        # delete
        del root2[0]
        assert len(root2) == 7
        assert root2[0].tag == '2'
        del root2[-1]
        assert len(root2) == 6
        assert root2[-1].tag == '7'

        print('PASSED')

    def test4_base_find_iteration(self):
        if not 4 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: base find operations')
        root = self._build_base_tree()

        # iteratoren and filters
        root[4] += iTree('sub4_100', value={'nolevel': 0})
        items = list(root[4])
        assert len(items) == 101
        # data key filtering
        # via filter
        myfilter = Filters.has_item_value_dict_key('level')
        items = list(filter(myfilter,root[4]))
        assert len(items) == 100


        myfilter = Filters.has_item_value_dict_key('nolevel')
        # here we switch to iter_deep!
        items = list(filter(myfilter, root[4].deep))
        assert len(items) == 1
        # data value filtering
        myfilter = Filters.has_item_value_dict_value((0, 1))
        items = list(filter(myfilter, root.deep))
        assert len(items) == 1
        # combined filter
        myfilter =lambda i: Filters.has_item_value_dict_value('n10')(i) and Filters.has_item_value_dict_key('level')(i)
        items = list(filter(myfilter, root.deep))
        assert len(items) == 1
        assert items[0].value['level'] == 'n10'
        # match filters
        myfilter = Filters.has_item_value_dict_key_fnmatch('no*')
        items = list(filter(myfilter, root.deep))
        assert len(items) == 1
        # item match filter
        myfilter = Filters.has_item_tag_fnmatch('sub0*')
        items = list(filter(myfilter, root.deep))
        assert len(items) == 5  # sub0_0-sub0_4
        
        item = root.get(0, 2)
        assert item.tag == 'sub0_2'

        item += iTree('sub0_2_0')

        item = root.get(0, 2, 0)
        assert item.tag == 'sub0_2_0'
        item += iTree('sub0_2_0_x', value=0)
        item += iTree('sub0_2_0_x', value=1)
        item = root.get(0, 2, 0, 0)
        assert item.tag == 'sub0_2_0_x'
        assert item.get_value() == 0

        item = root.get(*[0, 2, 0, 1])
        assert item.tag == 'sub0_2_0_x'
        assert item.get_value() == 1

        item = root.get(*iter([0, 2, 0, 1]))  # giving an iterator should work too!
        assert item.tag == 'sub0_2_0_x'
        assert item.get_value() == 1

        item = root.get(4, 20)
        assert item.tag == 'sub4_n'
        assert item.get_key_value('level') == 'n20'

        
        # key based access
        item = root.get(*[('sub4', 0), ('sub4_n', 10)])
        assert item.value.get('level') == 'n10'
        #root[('sub4', 0)].render()
        item = root.get(*[('sub4', 0), ('sub4_n', 40)])
        assert item.value.get('level') == 'n40'
        # slice
        item = root.get(4, slice(1, 3))
        # we expect here None because we don't get a single output
        assert len(list(item)) == 2

        # with find_all we get the items 1,1+3=4,1+3+3=7
        items = list(root.get(4, slice(1, 9, 3)))
        assert items[0].get_key_value('level') == 'n1'
        assert items[1].get_key_value('level') == 'n4'
        assert items[2].get_key_value('level') == 'n7'
        items = list(root.get(4, slice(99, 101)))
        assert items[0].get_key_value('level') == 'n99'  # pre last item
        assert items[1].tag == 'sub4_100'  # last item

        # tag slice
        with pytest.raises(ValueError):
            item = root.get.single(4, ('sub4_n', slice(1, 3)))
            # we expect here None because we don't get a single output
        item = root.get(4, ('sub4_n', slice(99, 101)))  # this should work we got just one match
        assert item[-1].get_key_value('level') == 'n99'  # last item

        # list of lists (two level list)
        items = list(root.get([0, 4], [0, 1]))
        assert len(items) == 4
        assert items[0].tag == 'sub0_0'
        assert items[3].tag == 'sub4_n'
        assert items[3].get_key_value('level') == 'n1'

        print('PASSED')

    def test5_data_access(self):
        if not 5 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: simple data access operations')

        root = iTree('root')
        assert root.value is NoValue

        # no key data:
        root.set_value({NoKey:'TEST'})
        assert len(root.value) == 1
        assert root.value[NoKey] == 'TEST'

        # key based data
        root.value['a']=Data.iTDataModelAny(1)
        root.value['b']=2
        assert len(root.value) == 3
        assert root.value.get('a') == 1
        assert root.value['a'].validator(2) == 2

        assert root.value.get('b') == 2
        assert root.value.get(NoKey) == 'TEST'

        assert root.value.pop(NoKey) == 'TEST'
        assert len(root.value) == 2
        assert root.value.get('a').clear() == 1
        assert len(root.value) == 2

        subitem=iTree('subitem')
        root+=subitem
        #checking emoty states
        #This is obsoltete  but we keep object for downward compatibility
        subitem.set_value(iTData())
        assert subitem.value.is_empty
        assert not subitem.value.is_no_key_only
        assert subitem.value.is_key_empty()

        subitem.value[NoKey]=NoValue #we set __NOVALUE__ which will not be taken in the dict
        assert subitem.value.is_empty
        assert not subitem.value.is_no_key_only
        assert subitem.value.is_key_empty()

        subitem.value['TEST']=NoValue  # we set __NOVALUE__
        assert not subitem.value.is_empty
        assert not subitem.value.is_no_key_only
        assert subitem.value.is_key_empty()
        assert subitem.value.is_key_empty('TEST')
        assert 'TEST' in subitem.value
        del subitem.value['TEST']
        assert subitem.value.is_empty
        assert not subitem.value.is_no_key_only
        assert subitem.value.is_key_empty('TEST')
        assert 'TEST' not in subitem.value

        subitem.value['TEST']=NoValue  # we set __NOVALUE__
        assert not subitem.value.is_empty
        assert not subitem.value.is_no_key_only
        assert subitem.value.is_key_empty()
        assert subitem.value.is_key_empty('TEST')
        assert 'TEST' in subitem.value
        del subitem.value['TEST']

        print('PASSED')

    def test6_mset_interval_class(self):
        if not 6 in TEST_SELECTION:
            return

        # The iTInterval class is outdated, but we keep it for downward compatibility
        # In future the user should use the mSetInterval instead!
        print('\nRESULT OF TEST: mSetInterval class')

        # base interval
        # open interval
        i = mSetInterval((1,True), (2,True))
        assert 1 not in i
        assert 2 not in i
        assert 1.0001 in i
        assert 1.999 in i
        assert str(i) == "mSetInterval('(1,2)')"
        assert repr(i) == 'mSetInterval(mSetItem(1, True), mSetItem(2, True))'
        i2 = eval(str(i))
        # iterables
        assert list(i2.iter_in([1, 2, 1.001, 1.999])) == [False, False, True, True]

        # close interval
        i = mSetInterval(-10, 20)
        assert -10 in i
        assert 20 in i
        assert -10.0001 not in i
        assert 20.00001 not in i
        assert str(i) == "mSetInterval('[-10,20]')"
        assert repr(
            i) == 'mSetInterval(mSetItem(-10), mSetItem(20))'

        i2 = eval(str(i))
        # iterables
        assert list(i2.iter_in([-10, 20, -10.0001, 20.00001])) == [True, True, False, False]

        # mixed
        i = mSetInterval((-10,True), 20)
        assert -10 not in i
        assert 20 in i
        i2 = eval(str(i))
        # iterables
        assert list(i2.iter_in([-10, 20])) == [False, True]

        i = mSetInterval(-10, (20, True))
        assert -10 in i
        assert 20 not in i
        i2 = eval(str(i))
        # iterables
        assert list(i2.iter_in([-10, 20])) == [True, False]

        # open interval not_in
        i = mSetInterval((-31,True) ,(-20,True), complement=True)
        assert -31 in i
        assert -20 in i
        assert -30.9999 not in i
        assert -20.01 not in i
        assert str(i) == "mSetInterval('!(-31,-20)')"
        i2 = eval(str(i))
        # iterables
        assert list(i2.iter_in([-31, -20, -30.999, -20.01])) == [True, True, False, False]

        # close interval not_in
        i = mSetInterval(1010, 2020, complement=True)
        assert 1010 not in i
        assert 2020 not in i
        assert 1009.999999 in i
        assert 2020.00001 in i
        assert str(i) == "mSetInterval('![1010,2020]')"
        i2 = eval(str(i))
        # iterables
        it = i2.iter_in([1010, 2020, 1009.9999, 2020.000001])
        itl = list(it)
        assert all(itl) == False
        assert itl == [False, False, True, True]

        # infinity intervals
        i = mSetInterval((1010,True), INF )
        assert 1010 not in i
        assert 2020 in i
        assert 202000001 in i
        assert str(i) == "mSetInterval('(1010,inf]')"
        i2 = eval(str(i))
        # iterables
        assert list(i2.iter_in([1010, 2020, 2020000001])) == [False, True, True]

        i = mSetInterval((1010,True), INF)
        assert 202000001 in i
        assert str(i) == "mSetInterval('(1010,inf]')"
        i = mSetInterval((1010,True), (INF_PLUS,True))
        assert 202000001 in i
        assert str(i) == "mSetInterval('(1010,inf)')"
        i = mSetInterval(INF_MINUS, (-10,True))
        assert -10 not in i
        assert -2020 in i
        assert i.__contains__(-202000001)
        assert str(i) == "mSetInterval('[-inf,-10)')"
        i = mSetInterval(INF, (0,True))  # reorder the limits
        assert 202000001 in i
        assert str(i) == "mSetInterval('(0,inf]')"
        i = mSetInterval((INF_MINUS,True),(10,True))
        assert -202000001 in i
        assert str(i) == "mSetInterval('(-inf,10)')"
        # not in inf
        i = mSetInterval(INF_MINUS, (10,True), complement=True)
        assert -202000001 not in i
        assert 10 in i
        # iterables
        assert list(i.iter_in([-202000001, 10])) == [False, True]
        i = mSetInterval((-33,True), INF, complement=True)
        assert -33 in i
        assert 300000 not in i
        # iterables
        assert list(i.iter_in([-33, 300000])) == [True, False]

        # check iterables
        # equal
        i = mSetInterval(10, (10, True))
        assert 10 in i
        assert 11 not in i
        assert str(i) == "mSetInterval('[10,10)')"
        # not equal
        i = mSetInterval(10, (10, True), complement=True)
        assert list(i.iter_in([9, 10, 11])) == [True, False, True]
        assert str(i) == "mSetInterval('![10,10)')"
        i2 = eval(str(i))
        assert list(i2.iter_in([9, 10, 11])) == [True, False, True]

        # cascaded intervals
        i0 = mSetInterval((-10,True), 10)
        i1 = mSetInterval(30 ,100)
        i2 = mSetInterval(300, INF)
        i3 = mSetInterval(-300, -200)
        i4 = mSetCombine(i0, i1, i2, i3,True)
        test_list = [-301, -300, -200, -199,
                     -10, -9, 10, 11,
                     29, 30, 100, 101,
                     299, 300, 10000]
        result_list = [False,
                       True,
                       True,
                       False,
                       False,
                       True,
                       True,
                       False,
                       False,
                       True,
                       True,
                       False,
                       False,
                       True,
                       True]

        assert list(i4.iter_in(test_list)) == result_list
        i5 = eval(str(i4))
        assert repr(i5) == repr(i4)  # this is not working because of formatters in i5
        assert list(i5.iter_in(test_list)) == list(i4.iter_in(test_list))
        # negative test
        i = mSetInterval((-10,True), 10)
        # check some strings: (check should deliver False in this case!
        assert 'aaa' not in i
        assert [True, True, True, False] == list(i.iter_in([1, 2, 3, 'aaa']))
        i = mSetInterval((10,False), -10)
        assert i.upper_value == 10
        assert i.lower_value == -10

        i = mSetInterval(INF, -10)
        assert i.upper_value == INF
        assert i.lower_value == -10

        i = mSetInterval(INF_MINUS, INF_MINUS)
        assert INF_MINUS in i
        assert -10000000 not in i

        print('PASSED')

    def test7_Filter(self):
        if not 7 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: base find operations')
        root = self._build_base_tree()
        # we addd some items to be filtered out
        root.insert(2, iTree('READONLY',flags=iTFLAG.READ_ONLY_TREE))
        root.insert(2, iTree('READONLY2',flags=iTFLAG.READ_ONLY_TREE))
        root[0].insert(1, iTree('TEMP',1,flags=iTFLAG.READ_ONLY_VALUE))
        root[0].insert(1, iTree('TEMP2',2,flags=iTFLAG.READ_ONLY_VALUE))
        root[4].insert(1, iTree('TEMP3',3,flags=iTFLAG.READ_ONLY_VALUE))
        # add some more data
        root[0][0].set_value({'ev': 'n1'})
        root[-1][10].set_value({'ev': 'extra'})

        #root.render()

        # test filter factory with primitive logic
        # no item filter all combinations


        all = len(root.deep)

        # iTree item Type filtering
        result = list(filter(Filters.has_item_flags(iTFLAG.READ_ONLY_VALUE), root.deep))
        assert len(result) == 3
        print('Exectime for Filters.has_item_flags: %f' % (
            calc_timeit(lambda: list(filter(Filters.has_item_flags(iTFLAG.READ_ONLY_VALUE), root.deep)), 1)))
        print('Exectime for lambda-> check item flags: %f' % (
            calc_timeit(lambda: list(filter(lambda i: bool(i.flags&iTFLAG.READ_ONLY_VALUE), root.deep)), 1)))

        # invert
        result_inv = list(filter(Filters.has_item_flags(iTFLAG.READ_ONLY_VALUE,invert=True), root.deep))
        assert len(result_inv) == all - len(result)

        result = list(filter(Filters.has_item_flags(iTFLAG.READ_ONLY_TREE), root.deep))
        assert len(result) == 2

        # invert
        result_inv = list(filter(Filters.has_item_flags(iTFLAG.READ_ONLY_TREE,invert=True), root.deep))
        assert len(result_inv) == all - len(result)

        # item match filter
        result = list(filter(Filters.has_item_tag_fnmatch('*sub0*'), root.deep))
        assert len(result) == 5
        # invert
        result_inv = list(filter(Filters.has_item_tag_fnmatch('*sub0*', invert=True), root.deep))
        assert all - len(result) == len(result_inv)

        result = list(filter(Filters.has_item_tag_fnmatch('sub0_?'), root.deep))
        assert len(result) == 4
        # invert
        result_inv = list(filter(Filters.has_item_tag_fnmatch('sub0_?', invert=True), root.deep))
        assert all - len(result) == len(result_inv)

        # data filter
        result = list(filter(Filters.has_item_value_dict_key('ev'), root.deep))
        assert len(result) == 2
        result = list(filter(Filters.has_item_value_dict_value('n1'), root.deep))
        assert len(result) == 2
        result1 = list(filter(Filters.has_item_value_dict_key_fnmatch('*ev*'), root.deep))
        assert len(result1) == 117
        result = list(filter(Filters.has_item_value_dict_key_fnmatch('ev*'), root.deep))
        assert len(result) == 2
        result2 = list(filter(Filters.has_item_value_dict_value_fnmatch('n*'), root.deep))
        assert len(result2) == 100
        # invert (only some of the examples
        assert len(
            list(
                filter(
                    Filters.has_item_value_dict_key_fnmatch('*ev*',
                                                            invert=True), root.deep))) == all - len(result1)
        assert len(
            list(
                filter(
                    Filters.has_item_value_dict_value_fnmatch('n*',
                    invert=True), root.deep))) == all - len(result2)

        # combine filters (only a few examples)
        result = list(filter(lambda i: not (Filters.has_item_value_dict_value_fnmatch(
                                              'n*')(i) and
                                              Filters.has_item_tag_fnmatch(
                                              'sub4*')(i)), root.deep))
        assert len(result) == 23

        result = list(filter(lambda i: not (Filters.has_item_value_dict_value_fnmatch(
                                              'n*')(i) and
                                              Filters.has_item_tag_fnmatch(
                                              'sub0*')(i)), root.deep))
        assert len(result) == 121

        print('PASSED')

    def test10_std_save_load(self):
        if not 10 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: serialize, dump and load')

        root = self._build_base_tree()
        root_data_path = get_tmp_path()
        target_path = root_data_path + '/out.itz'
        target_path2 = root_data_path + '/out.itr'
        target_path3 = root_data_path + '/out2.itz'

        print('Outputfile: %s' % os.path.abspath(target_path))

        # append some special dat items:
        if np is not None:
            root += iTree('NUMPY', value={'myarray': np.array([1.5, 4, 3.6, 467])})
        root += iTree('OD', value={'od': collections.OrderedDict([('C', 'c'), ('A', 'a'), ('B', 'b')])})
        root.dump(target_path, overwrite=True)

        root.dump(target_path2, pack=False, overwrite=True)

        root_loaded = root.load(target_path)
        diff=root-root_loaded

        assert root==root_loaded
        root_loaded2 = root.load(target_path2)
        assert root.equal(root_loaded2)
        assert len(root.renders()) > 100
        assert root.renders() == root_loaded2.renders()
        assert hash(root) == hash(root_loaded)

        root.dump(target_path, overwrite=True)
        root_loaded = root.load(target_path)
        assert root.equal(root_loaded)
        #root.render()

        print('Outputfile2: %s' % os.path.abspath(target_path3))
        root2 = self._build_mix_tree()
        root2.dump(target_path3, overwrite=True)
        root2_loaded = root2.load(target_path3)
        assert root2.equal(root2_loaded)

        # print(root.renders())
        print('PASSED')
