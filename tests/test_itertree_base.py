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


This part of code contains
the integration tests related to the base iTree functionalities
"""


import os
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

from itertree import *

root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

TEST_SELECTION = {1, 2, 3, 4, 5, 6, 7, 8, 10}
# TEST_SELECTION={}

print('Test start')


def get_relpath_to_root(item_path):
    new_path = item_path.replace(root_path, '')
    if new_path.startswith('\\'):
        new_path = new_path[1:]
    if new_path.startswith('/'):
        new_path = new_path[1:]
    return root_path + '/' + new_path


class Test_iTreeBase:
    def _build_mix_tree(self):
        root = iTree('root')
        root += iTree('c1', data=0)
        root += iTree('c2', data=1)
        root += iTree((0,), data=2)
        root += iTree('c2', data=3)
        root += iTree((1,), data=4)
        root += iTree('c2', data=5)
        root += iTree((1,), data=6)
        root += iTree('c2', data=7)
        root += iTree((1,), data=8)
        root += iTree('c2', data=9)
        root += iTree('c3', data=10)
        root += iTree((2,), data=11)
        # this will do internal copies!
        root[2].extend(root)
        root[2][2].extend(root)
        root[3].extend(root)
        return root

    def _build_base_tree(self):
        # build a tree
        root = iTree('root', data={'level': ()})
        # append subitems via +=
        root += iTree('sub1', data={'level': (1, -1)})
        root += iTree('sub2', data={'level': (2, -1)})
        # append subitems via append()
        root.append(iTree('sub3', data={'level': (3, -1)}))
        # insert first element via appendleft
        root.appendleft(iTree('sub0', data={'level': (0, -1)}))
        # append in deeper level via += and select last subelement via [-1]
        sub3_0 = iTree('sub3_0', data={'level': (3, 0)})
        root[-1] += sub3_0
        # append next element via append()
        root[-1].append(iTree('sub3_2', data={'level': (3, 2)}))
        # insert in between the other elements
        root[TagIdx('sub3', 0)].insert(1, iTree('sub3_1', data={'level': (3, 1)}))
        # build alist and extend
        subtree = [iTree('sub2_0', data={'level': (2, 0)}),
                   iTree('sub2_1', data={'level': (2, 1)}),
                   iTree('sub2_3', data={'level': (2, 3)}),
                   iTree('sub2_4', data={'level': (2, 4)}),
                   iTree('sub2_2', data={'level': (2, 2)})
                   ]
        root[2].extend(subtree)

        # root[2][TagIdx('sub2_2', 0)]+=iTree('sub2_2_0')
        # root[2][TagIdx('sub2_2', 0)] += iTree('sub2_2_1')
        # root[2][TagIdx('sub2_2', 0)] += iTree('sub2_2_2')

        # move an existing item
        root[2][TagIdx('sub2_2', 0)].move(2)

        # extendleft a iTree
        root[0] += iTree('sub0_3', data={'level': (0, 3)})
        subtree = iTree('extend', subtree=[iTree('sub0_0', data={'level': (0, 0)}),
                                           iTree('sub0_1', data={'level': (0, 1)}),
                                           iTree('sub0_2', data={'level': (0, 2)})])
        root[0].extendleft(subtree)

        s4 = iTree('sub4', data={'level': (4, -1)})
        root += s4

        # append multiples
        s4.extend(iTree('sub4_n', data={'level': ('n')}) * 100)
        for i in range(len(s4)):
            s4[i].d_set('level', 'n%i' % i)

        # Serializer.DTRenderer().render(root)
        return root

    def test0_dt_helpers(self):
        print('\nRESULT OF TEST: datatree helper classes')

        a = TagMultiIdx('aaa', slice(1, 2, 3))
        assert hasattr(a, 'is_TagMultiIdx')
        print('PASSED')

    def test1_dt_base_test(self):
        ''''
        we build a tree with some entries and then we try to access the elements
        '''
        if not 1 in TEST_SELECTION:
            return
        print('\nRESULT OF TEST: datatree base test')
        root = self._build_base_tree()

        # access possibilities
        assert root[3][1].data['level'] == (3, 1)
        assert root[('sub2', 0)][0].data['level'] == (2, 0)
        assert root[TagIdx('sub2', 0)][1].data['level'] == (2, 1)
        assert root[TagIdxStr('sub4#0')][40].data['level'] == 'n40'
        assert root[TagIdxStr('sub4#0')][TagIdxStr('sub4_n#80')].data['level'] == 'n80'

        # test some properties
        assert root[('sub2', 0)].pre_item.tag == 'sub1'
        assert root[('sub2', 0)].post_item.tag == 'sub3'
        assert root[('sub2', 0)].depth_up == 1
        assert root[0][1].idx_path == [0, 1]
        assert root[0][1].tag_idx_path == [TagIdx(tag='sub0', idx=0), TagIdx(tag='sub0_1', idx=0)]

        # check for error in case item is already added
        item = root[-1][0]
        with pytest.raises(RecursionError):
            root[-1] += item

        # test some iterators
        for i, item in enumerate(root.iter_children()):
            assert item.data['level'][0] == i, "%i,%s" % (i, repr(item))

        for i, item in enumerate(root[0].iter_children()):
            assert item.data['level'][1] == i

        # top-> down iter
        lookup = [-1, 0, 1, 2, 3, -1, -1, 0, 1, 2, 3, 4, -1, 0, 1, 2, -1]
        cnt = 0

        #root.render()

        for i, item in enumerate(root.iter_all()):
            # print(i,lookup[i],repr(item))
            if i < len(lookup):
                assert item.data['level'][1] == lookup[i], "%i-> %i, %s" % (i, lookup[i], repr(item))
            else:
                cnt += 1
        assert cnt == len(list(root['sub4'])[0])

        # down->top iter
        lookup = [0, 1, 2, 3, -1, -1, 0, 1, 2, 3, 4, -1, 0, 1, 2, -1]
        for i, item in enumerate(root.iter_all_bottom_up()):
            # print(item,i,lookup[i])
            if i < len(lookup):
                assert item.data['level'][1] == lookup[i]
        a = repr(root)

        root2 = self._build_mix_tree()
        #root2.render()
        assert root2[TagIdx((1,), 1)].d_get() == 6
        assert len(root2[TagIdx((0,), 0)][2]) == 14

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
        assert root[len(root) - 1].tag == 'insert2', repr(root)
        assert root[-1].tag == 'insert2', repr(root)
        assert root[-1].parent == root

        # replace
        root[2] = iTree('replace2')
        assert root[2].tag == 'replace2'
        assert root[2].parent == root
        root[-1] = iTree('replace1')
        assert root[-1].tag == 'replace1'
        assert root[-1].parent == root

        # move
        root[2].move(-1)
        assert root[-1].tag == 'replace2'
        assert root[2].tag == 'extendleft2'
        root[-1].move(2)
        assert root[2].tag == 'replace2'

        # rename
        root[2].rename('rename')
        assert root[2].tag == 'rename'
        assert len(list(root['rename'])) == 1

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
        root2 = [iTree('1'), iTree('2'), iTree('3'), iTree('4')] + iTree('B', subtree=[iTree('5'),
                                                                                       iTree('6'),
                                                                                       iTree('7'),
                                                                                       iTree('8')])
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
        root[4] += iTree('sub4_100', data={'nolevel': 0})
        items = list(root[4].iter_children())
        assert len(items) == 101
        # data key filtering
        myfilter = Filter.iTFilterDataKey('level')
        items = list(root[4].iter_children(item_filter=myfilter))
        assert len(items) == 100
        myfilter = Filter.iTFilterDataKey('nolevel')
        # here we switch to iter_all!
        items = list(root[4].iter_all(item_filter=myfilter))
        assert len(items) == 1
        # data value filtering
        myfilter = Filter.iTFilterData(data_value=(0, 1))
        items = list(root.iter_all(item_filter=myfilter))
        assert len(items) == 1
        # combined filter
        myfilter = Filter.iTFilterData(data_value='n10', pre_item_filter=Filter.iTFilterDataKey('level'))
        items = list(root.iter_all(item_filter=myfilter))
        assert len(items) == 1
        assert items[0].d_get('level') == 'n10'
        # match filters
        myfilter = Filter.iTFilterDataKeyMatch('no*')
        items = list(root.iter_all(item_filter=myfilter))
        assert len(items) == 1
        myfilter = Filter.iTFilterDataValueMatch('*n1*')
        items = list(root.iter_all(item_filter=myfilter))
        assert len(items) == 11  # n10-n19 + n100
        # item match filter
        myfilter = Filter.iTFilterItemTagMatch(iTMatch('sub0*'))
        items = list(root.iter_all(item_filter=myfilter))
        assert len(items) == 5  # sub0_0-sub0_4

        # index
        items = root.find_all(key_path=0)
        item = next(items)
        assert item.tag == 'sub0'
        item = root.find(0)
        assert item.tag == 'sub0'

        # one level index list -> go deeper
        #items = root.find_all([0, 2])
        item = root.find([0, 2])
        assert item.tag == 'sub0_2'

        item += iTree('sub0_2_0')

        item = root.find([0, 2, 0])
        assert item.tag == 'sub0_2_0'
        item += iTree('sub0_2_0_x', data=0)
        item += iTree('sub0_2_0_x', data=1)
        item = root.find([0, 2, 0, 0])
        assert item.tag == 'sub0_2_0_x'
        assert item.d_get() == 0

        item = root.find([0, 2, 0, 1])
        assert item.tag == 'sub0_2_0_x'
        assert item.d_get() == 1

        item = root.find(iter([0, 2, 0, 1]))  # giving an iterator should work too!
        assert item.tag == 'sub0_2_0_x'
        assert item.d_get() == 1

        item = root.find([4, 20])
        assert item.tag == 'sub4_n'
        assert item.d_get('level') == 'n20'

        # print(Serializer.DTStdRenderer().render(root))

        # tag_idx
        item = root.find([TagIdx('sub4', 0), TagIdx('sub4_n', 10)])
        assert item.d_get('level') == 'n10'
        # search from the root
        item = item.find(['/', TagIdxStr('sub4#0'), TagIdxStr('sub4_n#34')])
        assert item.d_get('level') == 'n34'

        item = root.find([TagIdxStr('sub4#0'), TagIdxStr('sub4_n#99')])
        assert item.d_get('level') == 'n99'
        # not recommended but possible tuple based access
        item = root.find([('sub4', 0), ('sub4_n', 40)])
        assert item.d_get('level') == 'n40'

        # string path (works only for string tags; not for hashed object tags
        item = root.find('sub4#0/sub4_n#50')
        assert item.d_get('level') == 'n50'
        # search from the root
        item = item.find('/sub4#0/sub4_n#45')
        assert item.d_get('level') == 'n45'
        # search from the root with changed separators
        item = item.find('#sub4&0#sub4_n&45', str_path_separator='#', str_index_separator='&')
        assert item.d_get('level') == 'n45'

        # slice
        item = root.find([4, slice(1, 3)])
        # we expect here None because we don't get a single output
        assert item is None

        # with find_all we get the items 1,1+3=4,1+3+3=7
        items = list(root.find_all([4, slice(1, 9, 3)]))
        assert items[0].d_get('level') == 'n1'
        assert items[1].d_get('level') == 'n4'
        assert items[2].d_get('level') == 'n7'
        items = list(root.find_all([4, slice(99, 10000)]))
        assert items[0].d_get('level') == 'n99'  # pre last item
        assert items[1].tag == 'sub4_100'  # last item

        # tag slice
        item = root.find([4, TagIdx('sub4_n', slice(1, 3))])
        # we expect here None because we don't get a single output
        assert item is None
        item = root.find([4, TagIdx('sub4_n', slice(99, 10000))])  # this should work we got just one match
        assert item.d_get('level') == 'n99'  # last item

        # list of lists (two level list)
        items = list(root.find_all([[0, 4], [0, 1]]))
        assert len(items) == 4
        assert items[0].tag == 'sub0_0'
        assert items[3].tag == 'sub4_n'
        assert items[3].d_get('level') == 'n1'

        # todo matches and items with hashed objects

        print('PASSED')

    def test5_data_access(self):
        if not 5 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: simple data access operations')

        root = iTree('root')
        assert len(root.data) == 0
        assert root.data.is_empty

        # we just check to reach the check here for deeper data testing we have mor eunit tests
        assert root.d_check('TEST')=='TEST'

        # no key data:
        root.d_set('TEST')
        assert len(root.data) == 1
        assert root.d_get() == 'TEST'
        assert root.d_check('TEST') == 'TEST'

        # key based data
        assert len(root.data) == 1
        root.d_set('a', Data.iTDataModelAny(1))
        root.d_set('b', 2)
        assert len(root.data) == 3
        assert root.d_get('a') == 1
        assert root.d_check(2,'a') == 2

        assert root.d_get('b') == 2
        assert root.d_get() == 'TEST'

        assert root.d_pop() == 'TEST'
        assert len(root.data) == 2
        assert root.d_pop('a') == 1
        assert len(root.data) == 2

        subitem=iTree('subitem')
        root+=subitem
        #checking emoty states
        assert subitem.data.is_empty
        assert not subitem.data.is_no_key_only
        assert subitem.data.is_key_empty()

        subitem.d_set(Data.__NOKEY__,Data.__NOVALUE__) #we set __NOVALUE__ which will not be taken in the dict
        assert subitem.data.is_empty
        assert not subitem.data.is_no_key_only
        assert subitem.data.is_key_empty()

        subitem.d_set(Data.__NOVALUE__) #we set __NOVALUE__ in __NOKEY__ which will not be taken in the dict
        assert subitem.data.is_empty
        assert not subitem.data.is_no_key_only
        assert subitem.data.is_key_empty()

        subitem.d_set('TEST',Data.__NOVALUE__)  # we set __NOVALUE__
        assert not subitem.data.is_empty
        assert not subitem.data.is_no_key_only
        assert subitem.data.is_key_empty()
        assert subitem.data.is_key_empty('TEST')
        assert 'TEST' in subitem.data
        subitem.d_del('TEST')
        assert subitem.data.is_empty
        assert not subitem.data.is_no_key_only
        assert subitem.data.is_key_empty('TEST')
        assert 'TEST' not in subitem.data

        subitem.d_set(key='TEST')  # we set __NOVALUE__
        assert not subitem.data.is_empty
        assert not subitem.data.is_no_key_only
        assert subitem.data.is_key_empty()
        assert subitem.data.is_key_empty('TEST')
        assert 'TEST' in subitem.data
        subitem.d_del('TEST')

        print('PASSED')

    def test6_intervall_class(self):
        if not 6 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: Interval class')

        # base interval
        # open interval
        i = iTInterval(1, 2)
        assert not i.check(1)
        assert not i.check(2)
        assert i.check(1.0001)
        assert i.check(1.999)
        assert str(i) == "iTInterval(str_def='(1,2)')"
        assert repr(i) == 'iTInterval(lower_limit=1, upper_limit=2, lower_open=True, upper_open=True)'
        i2 = eval(str(i))
        # iterables
        assert list(i2.check([1, 2, 1.001, 1.999], return_iterator=True)) == [False, False, True, True]

        # close interval
        i = iTInterval(-10, 20, False, False)
        assert i.check(-10)
        assert i.check(20)
        assert not i.check(-10.0001)
        assert not i.check(20.00001)
        assert str(i) == "iTInterval(str_def='[-10,20]')"
        assert repr(
            i) == 'iTInterval(lower_limit=-10, upper_limit=20, lower_open=False, upper_open=False)'

        i2 = eval(str(i))
        # iterables
        assert list(i2.check([-10, 20, -10.0001, 20.00001], return_iterator=True)) == [True, True, False, False]

        # mixed
        i = iTInterval(-10, 20, True, False)
        assert not i.check(-10)
        assert i.check(20)
        i2 = eval(str(i))
        # iterables
        assert list(i2.check([-10, 20], return_iterator=True)) == [False, True]

        i = iTInterval(-10, 20, False, True)
        assert i.check(-10)
        assert not i.check(20)
        i2 = eval(str(i))
        # iterables
        assert list(i2.check([-10, 20], return_iterator=True)) == [True, False]

        # open interval not_in
        i = iTInterval(-31, -20, not_in=True)
        assert i.check(-31)
        assert i.check(-20)
        assert not i.check(-30.9999)
        assert not i.check(-20.01)
        assert str(i) == "iTInterval(str_def='!(-31,-20)')"
        i2 = eval(str(i))
        # iterables
        assert list(i2.check([-31, -20, -30.999, -20.01], return_iterator=True)) == [True, True, False, False]

        # close interval not_in
        i = iTInterval(1010, 2020, False, False, not_in=True)
        assert not i.check(1010)
        assert not i.check(2020)
        assert i.check(1009.999999)
        assert i.check(2020.00001)
        assert str(i) == "iTInterval(str_def='![1010,2020]')"
        i2 = eval(str(i))
        # iterables
        it = i2.check([1010, 2020, 1009.9999, 2020.000001], return_iterator=True)
        itl = list(it)
        assert all(itl) == False
        assert itl == [False, False, True, True]

        # infinity intervals
        i = iTInterval(1010, iTInterval.INF, )
        assert not i.check(1010)
        assert i.check(2020)
        assert i.check(202000001)
        assert str(i) == "iTInterval(str_def='(1010,+inf)')"
        i2 = eval(str(i))
        # iterables
        assert list(i2.check([1010, 2020, 2020000001], return_iterator=True)) == [False, True, True]

        i = iTInterval(1010, 'inf', True, False)
        assert i.check(202000001)
        assert str(i) == "iTInterval(str_def='(1010,+inf]')"
        i = iTInterval(1010, '+inf')
        assert i.check(202000001)
        assert str(i) == "iTInterval(str_def='(1010,+inf)')"
        i = iTInterval(iTInterval.INF, -10)
        assert not i.check(-10)
        assert i.check(-2020)
        assert i.check(-202000001)
        assert str(i) == "iTInterval(str_def='(-inf,-10)')"
        i = iTInterval('inf', 0, False)
        assert i.check(-202000001)
        assert str(i) == "iTInterval(str_def='[-inf,0)')"
        i = iTInterval('-inf', 10)
        assert i.check(-202000001)
        assert str(i) == "iTInterval(str_def='(-inf,10)')"
        # not in inf
        i = iTInterval('-inf', 10, not_in=True)
        assert not i.check(-202000001)
        assert i.check(10)
        # iterables
        assert list(i.check([-202000001, 10], return_iterator=True)) == [False, True]
        i = iTInterval(-33, 'inf', not_in=True)
        assert i.check(-33)
        assert not i.check(300000)
        # iterables
        assert list(i.check([-33, 300000], return_iterator=True)) == [True, False]

        # check iterables
        # equal
        i = iTInterval(10, None, False, True)
        assert i.check(10)
        assert not i.check(11)
        assert str(i) == "iTInterval(str_def='==10')"
        # not equal
        i = iTInterval(10, None, False, True, not_in=True)
        assert list(i.check([9, 10, 11], return_iterator=True)) == [True, False, True]
        assert str(i) == "iTInterval(str_def='!=10')"
        i2 = eval(str(i))
        assert list(i2.check([9, 10, 11], return_iterator=True)) == [True, False, True]

        # cascaded intervals
        i = iTInterval(-10, 10, True, False)
        i2 = iTInterval(30, 100, False, False, pre_interval=i)
        i3 = iTInterval(300, 'inf', False, False, pre_interval=i2)
        i4 = iTInterval(-300, -200, False, False, pre_interval=i3)
        assert list(i4.check([-301, -300, -200, -199,
                              -10, -9, 10, 11,
                              29, 30, 100, 101,
                              299, 300, 10000], return_iterator=True)) == [False, True, True, False,
                                                                           False, True, True, False,
                                                                           False, True, True, False,
                                                                           False, True, True]
        i5 = eval(str(i4))
        assert list(i5.check([-301, -300, -200, -199,
                              -10, -9, 10, 11,
                              29, 30, 100, 101,
                              299, 300, 10000], return_iterator=True)) == [False, True, True, False,
                                                                           False, True, True, False,
                                                                           False, True, True, False,
                                                                           False, True, True]

        # negative test
        i = iTInterval(-10, 10, True, False)
        # check some strings: (check should deliver False in this case!
        assert False == i.check('aaa')
        assert [True, True, True, False] == list(i.check([1, 2, 3, 'aaa'], return_iterator=True))
        with pytest.raises(ValueError):
            # lower_limit>upper_limit
            i = iTInterval(10, -10, True, False)
        with pytest.raises(ValueError):
            # lower_limit= +inf
            i = iTInterval('+inf', -10, True, False)
        with pytest.raises(ValueError):
            # upper_limit= -inf
            i = iTInterval('-inf', '-inf', True, False)

        with pytest.raises(ValueError):
            # equal to infinity
            i = iTInterval('inf', None, True, False)

        print('PASSED')

    def test7_filter_classes(self):
        if not 7 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: base find operations')
        root = self._build_base_tree()
        # we addd some items to be filtered out
        root.insert(2, iTreeReadOnly('READONLY'))
        root.insert(2, iTreeReadOnly('READONLY2'))
        root[0].insert(1, iTreeTemporary('TEMP'))
        root[0].insert(1, iTreeTemporary('TEMP2'))
        root[4].insert(1, iTreeTemporary('TEMP3'))
        # add some more data
        root[0][0].d_set('ev', 'n1')
        root[-1][10].d_set('ev', 'extra')

        #root.render()

        # test filter factory with primitive logic
        # no item filter all combinations
        assert Filter.iTFilterTrue(pre_item_filter=None, invert=False, use_and=False)(True) == True
        assert Filter.iTFilterTrue(pre_item_filter=None, invert=False, use_and=True)(True) == True
        assert Filter.iTFilterTrue(pre_item_filter=None, invert=True, use_and=False)(True) == False
        assert Filter.iTFilterTrue(pre_item_filter=None, invert=True, use_and=True)(True) == False
        # with item filter
        assert Filter.iTFilterTrue(pre_item_filter=lambda item: False, invert=False, use_and=False)(True) == True
        assert Filter.iTFilterTrue(pre_item_filter=lambda item: False, invert=False, use_and=True)(True) == False
        assert Filter.iTFilterTrue(pre_item_filter=lambda item: True, invert=True, use_and=False)(True) == True
        assert Filter.iTFilterTrue(pre_item_filter=lambda item: True, invert=True, use_and=True)(True) == False

        all = root.count_all()

        # True Filter matches to Any item!
        result = list(root.find_all('**', Filter.iTFilterTrue()))
        assert len(result) == all

        # iTree item Type filtering
        result = list(root.find_all('**', Filter.iTFilterItemType(iTreeTemporary)))
        assert len(result) == 3
        # invert
        result_inv = list(root.find_all('**', Filter.iTFilterItemType(iTreeTemporary, invert=True)))
        assert len(result_inv) == all - len(result)

        result = list(root.find_all('**', Filter.iTFilterItemType(iTreeReadOnly)))
        assert len(result) == 2
        # invert
        result_inv = list(root.find_all('**', Filter.iTFilterItemType(iTreeReadOnly, invert=True)))
        assert len(result_inv) == all - len(result)

        # item match filter
        result = list(root.iter_all(Filter.iTFilterItemTagMatch(iTMatch('*sub0*'))))
        assert len(result) == 5
        # invert
        result_inv = list(root.iter_all(Filter.iTFilterItemTagMatch(iTMatch('*sub0*'), invert=True)))
        assert all - len(result) == len(result_inv)

        result = list(root.iter_all(Filter.iTFilterItemTagMatch(iTMatch('sub0_?'))))
        assert len(result) == 4
        # invert
        result_inv = list(root.iter_all(Filter.iTFilterItemTagMatch(iTMatch('sub0_?'), invert=True)))
        assert all - len(result) == len(result_inv)

        # data filter
        result = list(root.find_all('**', Filter.iTFilterData(data_key='ev')))
        assert len(result) == 2
        result = list(root.find_all('**', Filter.iTFilterData(data_value='n1')))
        assert len(result) == 2
        result1 = list(root.find_all('**', Filter.iTFilterData(data_key=iTMatch('*ev*'))))
        assert len(result1) == 117
        result = list(root.find_all('**', Filter.iTFilterData(data_key=iTMatch('ev*'))))
        assert len(result) == 2
        result2 = list(root.find_all('**', Filter.iTFilterData(data_value=iTMatch('n*'))))
        assert len(result2) == 101
        # invert (only some of the examples
        assert len(list(root.find_all('**', Filter.iTFilterDataKeyMatch('*ev*', invert=True)))) == all - len(
            result1)

        assert len(list(root.find_all('**', Filter.iTFilterData(data_key=iTMatch('*ev*'), invert=True)))) == all - len(
            result1)
        assert len(list(root.find_all('**', Filter.iTFilterData(data_value=iTMatch('n*'), invert=True)))) == all - len(
            result2)

        # combine filters (only a few examples)
        result = list(root.find_all('**', Filter.iTFilterItemTagMatch(iTMatch('sub4*'),
                                                                      invert=True,
                                                                      pre_item_filter=Filter.iTFilterData(
                                                                          data_value=iTMatch('n*'))
                                                                      )))
        assert len(result) == 1

        result = list(root.find_all('**', Filter.iTFilterItemTagMatch(iTMatch('sub0*'),
                                                                      use_and=False,
                                                                      pre_item_filter=Filter.iTFilterData(
                                                                          data_value=iTMatch('n*'))
                                                                      )))
        assert len(result) == 105

        print('PASSED')

    def test10_std_save_load(self):
        if not 10 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: serialize, dump and load')

        root = self._build_base_tree()
        root_data_path = get_relpath_to_root('tmp')
        if not os.path.exists(root_data_path):
            os.makedirs(root_data_path)
        target_path = root_data_path + '/out.itz'
        target_path2 = root_data_path + '/out.itr'
        target_path3 = root_data_path + '/out2.itz'

        print('Outputfile: %s' % os.path.abspath(target_path))

        # append some special dat items:
        if np is not None:
            root += iTree('NUMPY', data={'myarray': np.array([1.5, 4, 3.6, 467])})
        root += iTree('OD', data={'od': collections.OrderedDict([('C', 'c'), ('A', 'a'), ('B', 'b')])})
        root.dump(target_path, overwrite=True)

        root.dump(target_path2, pack=False, overwrite=True)

        root_loaded = root.load(target_path)
        assert root.equal(root_loaded)
        root_loaded2 = root.load(target_path2)
        assert root.equal(root_loaded2)
        assert len(root.renders()) > 100
        assert root.renders() == root_loaded2.renders()
        assert hash(root) == hash(root_loaded)

        # finally we add a temporary item
        root += iTreeTemporary('temp')
        root.dump(target_path, overwrite=True)
        root_loaded = root.load(target_path)
        assert not root.equal(root_loaded)
        #root.render()

        print('Outputfile2: %s' % os.path.abspath(target_path3))
        root2 = self._build_mix_tree()
        root2.dump(target_path3, overwrite=True)
        root2_loaded = root2.load(target_path3)
        assert root2.equal(root2_loaded)

        # print(root.renders())

        print('PASSED')
