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

TEST_SELECTION = {1, 2, 3, 4, 5, 6, 7, 8, 10, 11}
#TEST_SELECTION={10}

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
            s4[i].set('level', 'n%i' % i)

        # Serializer.DTRenderer().render(root)
        return root

    def test0_dt_helpers(self):
        print('\nRESULT OF TEST: datatree helper classes')

        a = TagMultiIdx('aaa', slice(1, 2, 3))
        assert hasattr(a, 'is_TagMultiIdx')

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

        root.render()

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
        root2.render()
        assert root2[TagIdx((1,), 1)].get() == 6
        assert len(root2[TagIdx((0,), 0)][2]) == 14

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
        myfilter = Filter.iTFilterDataValue((0, 1))
        items = list(root.iter_all(item_filter=myfilter))
        assert len(items) == 1
        # combined filter
        myfilter = Filter.iTFilterDataValue('n10', item_filter=Filter.iTFilterDataKey('level'))
        items = list(root.iter_all(item_filter=myfilter))
        assert len(items) == 1
        assert items[0].get('level') == 'n10'
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
        assert items[0].tag == 'sub0'
        item = root.find(0)
        assert item.tag == 'sub0'

        # one level index list -> go deeper
        items = root.find_all([0, 2])
        item = root.find([0, 2])
        assert item.tag == 'sub0_2'

        item += iTree('sub0_2_0')

        item = root.find([0, 2, 0])
        assert item.tag == 'sub0_2_0'
        item += iTree('sub0_2_0_x', data=0)
        item += iTree('sub0_2_0_x', data=1)
        item = root.find([0, 2, 0, 0])
        assert item.tag == 'sub0_2_0_x'
        assert item.get() == 0

        item = root.find([0, 2, 0, 1])
        assert item.tag == 'sub0_2_0_x'
        assert item.get() == 1

        item = root.find([4, 20])
        assert item.tag == 'sub4_n'
        assert item.data.get('level') == 'n20'

        # print(Serializer.DTStdRenderer().render(root))

        # tag_idx
        item = root.find([TagIdx('sub4', 0), TagIdx('sub4_n', 10)])
        assert item.data.get('level') == 'n10'
        # search from the root
        item = item.find(['/', TagIdxStr('sub4#0'), TagIdxStr('sub4_n#34')])
        assert item.data.get('level') == 'n34'

        item = root.find([TagIdxStr('sub4#0'), TagIdxStr('sub4_n#99')])
        assert item.data.get('level') == 'n99'
        # not recommended but possible tuple based access
        item = root.find([('sub4', 0), ('sub4_n', 40)])
        assert item.data.get('level') == 'n40'

        # string path (works only for string tags; not for hashed object tags
        item = root.find('sub4#0/sub4_n#50')
        assert item.data.get('level') == 'n50'
        # search from the root
        item = item.find('/sub4#0/sub4_n#45')
        assert item.data.get('level') == 'n45'
        # search from the root with changed separators
        item = item.find('#sub4&0#sub4_n&45', str_path_separator='#', str_index_separator='&')
        assert item.data.get('level') == 'n45'

        # slice
        item = root.find([4, slice(1, 3)])
        # we expect here None because we don't get a single output
        assert item is None

        # with find_all we get the items 1,1+3=4,1+3+3=7
        items = list(root.find_all([4, slice(1, 9, 3)]))
        assert items[0].data.get('level') == 'n1'
        assert items[1].data.get('level') == 'n4'
        assert items[2].data.get('level') == 'n7'
        items = list(root.find_all([4, slice(99, 10000)]))
        assert items[0].data.get('level') == 'n99'  # pre last item
        assert items[1].tag == 'sub4_100'  # last item

        # tag slice
        item = root.find([4, TagIdx('sub4_n', slice(1, 3))])
        # we expect here None because we don't get a single output
        assert item is None
        item = root.find([4, TagIdx('sub4_n', slice(99, 10000))])  # this should work we got just one match
        assert item.data.get('level') == 'n99'  # last item

        # list of lists (two level list)
        items = list(root.find_all([[0, 4], [0, 1]]))
        assert len(items) == 4
        assert items[0].tag == 'sub0_0'
        assert items[3].tag == 'sub4_n'
        assert items[3].get('level') == 'n1'

        # todo matches and items with hashed objects

    def test5_data_access(self):
        if not 5 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: simple data access operations')

        root = iTree('root')
        assert len(root.data) == 0

        # we just check to reach the chack here for deeper data testing seet test_dt_data.py
        assert root.check('TEST')[0] == True

        # no key data:
        root.set('TEST')
        assert len(root.data) == 1
        assert root.get() == 'TEST'

        # key based data
        assert len(root.data) == 1
        root.set('a', 1)
        root.set('b', 2)
        assert len(root.data) == 3
        assert root.get('a') == 1
        assert root.get('b') == 2
        assert root.get() == 'TEST'

        assert root.pop_data() == 'TEST'
        assert len(root.data) == 2
        assert root.pop_data('a') == 1
        assert len(root.data) == 1

    def test6_filter_classes(self):
        if not 6 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: base find operations')
        root = self._build_base_tree()
        #we addd some items to be filtered out
        root.insert(2,iTreeReadOnly('READONLY'))
        root.insert(2, iTreeReadOnly('READONLY2'))
        root[0].insert(1, iTreeTemporary('TEMP'))
        root[0].insert(1, iTreeTemporary('TEMP2'))
        root[4].insert(1, iTreeTemporary('TEMP3'))
        #add some more data
        root[0][0].set('ev','n1')
        root[-1][10].set('ev', 'extra')

        root.render()

        #test filter factory with primitive logic
        #no item filter all combinations
        assert Filter.iTFilterTrue(item_filter=None, invert=False, use_and=False)(True)==True
        assert Filter.iTFilterTrue(item_filter=None, invert=False, use_and=True)(True)==True
        assert Filter.iTFilterTrue(item_filter=None,invert=True, use_and=False)(True)==False
        assert Filter.iTFilterTrue(item_filter=None, invert=True, use_and=True)(True)==False
        #with item filter
        assert Filter.iTFilterTrue(item_filter=lambda item: False, invert=False, use_and=False)(True)==True
        assert Filter.iTFilterTrue(item_filter=lambda item: False, invert=False, use_and=True)(True)==False
        assert Filter.iTFilterTrue(item_filter=lambda item: True, invert=True, use_and=False)(True)==True
        assert Filter.iTFilterTrue(item_filter=lambda item: True, invert=True,  use_and=True)(True)==False

        all = root.count_all()

        #True Filter matches to Any item!
        result=list(root.find_all('**',Filter.iTFilterTrue()))
        assert len(result)==all

        #iTree item Type filtering
        result = list(root.find_all('**', Filter.iTFilterItemType(iTreeTemporary)))
        assert len(result) == 3
        #invert
        result_inv = list(root.find_all('**', Filter.iTFilterItemType(iTreeTemporary,invert=True)))
        assert len(result_inv) == all-len(result)

        result = list(root.find_all('**', Filter.iTFilterItemType(iTreeReadOnly)))
        assert len(result) == 2
        #invert
        result_inv = list(root.find_all('**', Filter.iTFilterItemType(iTreeReadOnly,invert=True)))
        assert len(result_inv) == all-len(result)

        # item match filter
        result = list(root.iter_all(Filter.iTFilterItemTagMatch(iTMatch('*sub0*'))))
        assert len(result) == 5
        # invert
        result_inv = list(root.iter_all(Filter.iTFilterItemTagMatch(iTMatch('*sub0*'),invert=True)))
        assert all-len(result) == len(result_inv)

        result = list(root.iter_all(Filter.iTFilterItemTagMatch(iTMatch('sub0_?'))))
        assert len(result) == 4
        # invert
        result_inv = list(root.iter_all(Filter.iTFilterItemTagMatch(iTMatch('sub0_?'),invert=True)))
        assert all-len(result) == len(result_inv)

        # data filter
        result = list(root.find_all('**', Filter.iTFilterDataKey('ev')))
        assert len(result) == 2
        result = list(root.find_all('**', Filter.iTFilterDataValue('n1')))
        assert len(result) == 2
        result1 = list(root.find_all('**', Filter.iTFilterDataKeyMatch('*ev*')))
        assert len(result1) == 117
        result = list(root.find_all('**', Filter.iTFilterDataKeyMatch('ev*')))
        assert len(result) == 2
        result2 = list(root.find_all('**', Filter.iTFilterDataValueMatch('n*')))
        assert len(result2) == 101
        # invert (only some of the examples
        assert len(list(root.find_all('**', Filter.iTFilterDataKeyMatch('*ev*',invert=True))))==all-len(result1)
        assert len(list(root.find_all('**', Filter.iTFilterDataValueMatch('n*', invert=True)))) == all - len(result2)

        # combine filters (only a few examples)
        result = list(root.find_all('**', Filter.iTFilterItemTagMatch(iTMatch('sub4*'),
                                                                       invert=True,
                                                                       item_filter=Filter.iTFilterDataValueMatch('n*')
                                                                       )))
        assert len(result) == 1

        result = list(root.find_all('**', Filter.iTFilterItemTagMatch(iTMatch('sub0*'),
                                                               use_and=False,
                                                               item_filter=Filter.iTFilterDataValueMatch('n*')
                                                               )))
        assert len(result) == 105

    def test10_std_save_load(self):
        if not 10 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: serialize, dump and load')

        root = self._build_base_tree()
        root_data_path = get_relpath_to_root('tmp')
        if not os.path.exists(root_data_path):
            os.makedirs(root_data_path)
        target_path = root_data_path + '/out.dtz'
        target_path2 = root_data_path + '/out.dtr'
        target_path3 = root_data_path + '/out2.dtz'

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
        root.render()

        print('Outputfile2: %s' % os.path.abspath(target_path3))
        root2 = self._build_mix_tree()
        root2.dump(target_path3, overwrite=True)
        root2_loaded = root2.load(target_path3)
        assert root2.equal(root2_loaded)

        # print(root.renders())

    def test11_linking(self):
        if not 11 in TEST_SELECTION:
            return
        # first we create a file
        root = self._build_base_tree()
        root_data_path = get_relpath_to_root('tmp')
        if not os.path.exists(root_data_path):
            os.makedirs(root_data_path)
        target_path = root_data_path + '/out.dtz'
        root.dump(target_path=target_path, overwrite=True)

        # we build a new tree
        root = self._build_mix_tree()
        # we add a linked element
        linked_item = iTreeLink('LINKED', data=0, link_file_path=target_path, link_key_path=4, load_links=False)
        root.insert(1, linked_item)
        print()
        # root.render()
        assert len(linked_item) == 0
        root.load_links()
        assert len(linked_item) == 100
        with pytest.raises(PermissionError):
            linked_item += iTree('BASTARD')
        with pytest.raises(PermissionError):
            linked_item.insert(0, iTree('BASTARD'))
        with pytest.raises(PermissionError):
            del linked_item[0]
        # data can be changed
        linked_item.set('DATA', 'TEST')
        # but not in the sub items!
        with pytest.raises(PermissionError):
            linked_item[1].set('DATA', 'TEST')
        for i, item in enumerate(root.iter_all()):
            if i == 0:
                assert not item.is_linked
            elif i == 1:
                assert item.tag == 'LINKED'
                assert item.is_linked
            elif i > 2 and i <= 101:
                assert item.is_linked
            elif i == 101:
                assert item.get('level') == 'n99'
            elif i == 102:
                assert not item.is_linked
                assert item.tag == 'c2'
            elif i > 102:
                assert not item.is_linked

        for i, item in enumerate(root.iter_all(Filter.iTFilterItemType(iTreeLink,invert=True))):
            assert not item.is_linked
        for i, item in enumerate(root.iter_all(Filter.iTFilterItemType(iTreeLink))):
            assert item.is_linked
