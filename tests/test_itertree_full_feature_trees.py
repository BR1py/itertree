import os
import sys
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
from types import GeneratorType
from collections import OrderedDict
from itertree import *
#from itertree.itree_helpers import NoValue, NoTag, Tag


root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

def get_relpath_to_root(item_path):
    new_path = item_path.replace(root_path, '')
    if new_path.startswith('\\'):
        new_path = new_path[1:]
    if new_path.startswith('/'):
        new_path = new_path[1:]
    return root_path + '/' + new_path

def calc_timeit(check_method, number):
    min_time = float('inf')
    for i in range(number):
        t = timeit.timeit(check_method, number=1)
        if t < min_time:
            min_time = t
    return min_time



class Test_FullFeatureTreesTest():

    def test1_full_featured_tree1_test(self):

        print('\nRUN TEST: full featured iTree 1')
        print('we build a tree containing all kind of data models')
        print('nested children the tree will be stored in a file and used as a linked subtree in the next test!')
        root_data_path = get_relpath_to_root('tmp')
        if not os.path.exists(root_data_path):
            os.makedirs(root_data_path)
        target_path = root_data_path + '/out.itr'

        root=iTree('root')

        # we add some read_only elements:
        sub=root.append(iTree('read_only_branch'))
        sub.append(iTree('read_only_subtree',subtree=[iTree('read_only_subtree_sub'),
                                                              iTree('read_only_subtree_sub'),
                                                              iTree('read_only_subtree_sub')],
                                                              flags=iTFLAG.READ_ONLY_TREE)
                  )
        sub.append(iTree('read_only_value', value='read_only', subtree=[iTree('normal'),
                                                       iTree('read_only_value',value='read_only',
                                                             flags=iTFLAG.READ_ONLY_VALUE),
                                                       iTree('read_only_value', value='read_only',
                                                              flags=iTFLAG.READ_ONLY_VALUE),
                                                       iTree('normal')],
                         flags=iTFLAG.READ_ONLY_VALUE)
                   )
        sub.append(iTree('read_only_mix', value='read_only', subtree=[iTree('read_only_tree'),
                                                                        iTree('read_only_tree_value', value='read_only',
                                                                              flags=iTFLAG.READ_ONLY_VALUE),
                                                                        iTree('read_only_tree_value', value='read_only',
                                                                              flags=iTFLAG.READ_ONLY_VALUE),
                                                                        iTree('read_only_tree')],
                         flags=iTFLAG.READ_ONLY_VALUE|iTFLAG.READ_ONLY_TREE)
                   )


        sub=root.append(iTree('int',value=Data.iTIntModel(description='Attribute takes integer values')))

        sub.set_value(10)
        assert sub.get_value()==10

        sub = root.append(iTree('int_round', value=Data.iTRoundIntModel(description='Attribute takes integer values')))
        sub.set_value(20.51)
        assert sub.get_value() == 21

        sub_sub=sub.append(iTree('int8',Data.iTInt8Model()))
        sub_sub.set_value(-120)
        assert sub_sub.get_value() == -120
        sub_sub=sub.append(iTree('uint8',Data.iTUInt8Model()))
        sub_sub.set_value(240)
        assert sub_sub.get_value() == 240
        sub_sub = sub.append(iTree('int16', Data.iTInt16Model()))
        sub_sub.set_value(-1024)
        assert sub_sub.get_value() == -1024
        sub_sub = sub.append(iTree('uint16', Data.iTUInt16Model()))
        sub_sub.set_value(1024)
        assert sub_sub.get_value() == 1024
        sub_sub = sub.append(iTree('int32', Data.iTInt32Model()))
        sub_sub.set_value(-2147483600)
        assert sub_sub.get_value() == -2147483600
        sub_sub = sub.append(iTree('uint32', Data.iTUInt32Model()))
        sub_sub.set_value(2147483600)
        assert sub_sub.get_value() == 2147483600
        sub_sub = sub.append(iTree('int64', Data.iTInt64Model()))
        sub_sub.set_value(-2800000000)
        assert sub_sub.get_value() == -2800000000
        sub_sub = sub.append(iTree('uint64', Data.iTUInt64Model()))
        sub_sub.set_value(2800000000)
        assert sub_sub.get_value() == 2800000000
        # we add some items with same tag
        sub_sub = sub.append(iTree('int64', Data.iTInt64Model()))
        sub_sub.set_value(2800000000)
        assert sub_sub.get_value() == 2800000000
        sub_sub = sub.append(iTree('uint64', Data.iTUInt64Model()))
        sub_sub.set_value(4800000000)
        assert sub_sub.get_value() == 4800000000
        assert len(sub)==10
        sub=root.append(iTree(('tuple_tag','float')))
        sub_sub = sub.append(iTree('float', Data.iTFloatModel()))
        sub_sub.set_value(123.456)
        assert sub_sub.get_value() == 123.456
        sub = root.append(iTree('str', Data.iTStrModel()))
        sub.set_value('abc')
        assert sub.get_value()=='abc'
        sub_sub = sub.append(iTree('ascii_str', Data.iTASCIIStrModel()))
        with pytest.raises(ValueError):
            sub_sub.set_value('^°abc')
        sub_sub.set_value('abc')
        assert sub_sub.get_value() == 'abc'
        sub_sub = sub.append(iTree('utf8_str', Data.iTUTF8StrModel()))
        sub_sub.set_value('^°abc')
        assert sub_sub.get_value() == '^°abc'
        sub_sub = sub.append(iTree('utf16_str', Data.iTUTF8StrModel()))
        sub_sub.set_value(u'^°abc')
        assert sub_sub.get_value() == u'^°abc'
        sub_sub = sub.append(iTree('fnmatch', Data.iTStrFnPatternModel('?b?')))
        sub_sub.set_value('abc')
        assert sub_sub.get_value() == 'abc'
        sub_sub = sub.append(iTree('regex', Data.iTStrRegexPatternModel('a[a,b,c][a,b,c]')))
        sub_sub.set_value('abc')
        assert sub_sub.get_value() == 'abc'
        root.extend(iTree('empty')*10)
        root.extend(iTree(value=1) * 10)

        interval=Data.mSetCombine(Data.mSetInterval('[1,10]'),Data.mSetInterval('[100,200]'),True)
        sub=root.append(iTree('interval',value=Data.iTValueModel(contains=interval)))
        sub.set_value(150)
        assert sub.get_value()==150
        root.dump(target_path,overwrite=True)

        sub = root.append(iTree('int_array', value=Data.iTIntModel(shape=[100])))
        sub.set_value([150,200])
        assert sub.get_value() == [150,200]

        sub = root.append(iTree('str_array', value=Data.iTStrModel(shape=[10,10])))
        sub.set_value(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0123456789'])
        assert sub.get_value() == ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0123456789']

        with pytest.raises(ValueError):
            sub.set_value(['abc', '1234567890_def'])
        with pytest.raises(ValueError):
            sub.set_value(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0123456789','too much'])
        a=repr(root)


        sub=root
        print('Current recursion limit is: %s'%sys.getrecursionlimit())
        depth=sys.getrecursionlimit()-100
        #depth=300
        for i in range(depth):
            # serializer cannot handle deeper trees at the moment
            sub.append(iTree((i,), i))
            sub.append(iTree((i,), i))
            sub=sub.append(iTree((i,),i))
        print('The build iTree has a depth of %i'%depth)

        print('The build iTree contains  %i items' % len(root.deep))

        assert root['read_only_branch',0][0].is_tree_read_only
        assert root['read_only_branch',0][1].is_value_read_only
        assert root['read_only_branch',0][2].is_tree_read_only
        assert root['read_only_branch', 0][2].is_value_read_only

        # We do some tests to see if we get recursion errors and we measure some timings by teh way

        print('Exec iter_deep() time: %f s' % (calc_timeit(lambda: collections.deque(root.deep, maxlen=0), number=10)))
        print('Exec count_deep() time: %f s' % (calc_timeit(lambda: len(root.deep), number=10)))
        assert len(root.deep) == depth * 3 + 43 + 15
        print('Get max_depth time: %f s'%(calc_timeit(lambda: root.max_depth,number=10)))
        assert root.max_depth==depth
        print('Exec set_read_only() time: %f s' % (calc_timeit(lambda: root[-1].set_tree_read_only(), number=10) ))
        print('Exec unset_tree_read_only_deep() time: %f s' % (calc_timeit(lambda: root[-1].deep.unset_tree_read_only(), number=10)))

        last_item=root.get(*[-1] * depth)
        assert last_item.level==depth
        print('Get key_path time: %f s' % calc_timeit(lambda: last_item.tag_idx_path, number=1))
        print('Get key_path again time: %f s' % calc_timeit(lambda: last_item.tag_idx_path, number=1))
        print('Get idx_path time: %f s'%calc_timeit(lambda: last_item.idx_path,number=1))
        print('Get idx_path again time: %f s' % calc_timeit(lambda: last_item.idx_path, number=1))

        assert len(last_item.tag_idx_path) == depth
        assert last_item.idx_path==tuple([30]+[2]*(depth-1))
        last_item.set_value([1,2,3,4,5,6,7,8,9,0])
        print('Exec dump() time: %f s' % (calc_timeit(lambda: root.dump(target_path,pack=False,overwrite=True), number=1)))
        root2 = iTree().load(target_path)
        print('Exec load() time: %f s' % (
                    calc_timeit(lambda: iTree().load(target_path), number=1) ))
        assert root==root2
        print('Exec __eq__() time: %f s' % (
                calc_timeit(lambda: root == root2, number=1) ))
        assert root.equal(root2,True,True)
        print('Exec equal() time: %f s' % (
                calc_timeit(lambda: root.equal(root2, True, True), number=1) ))

        # did we save the flags and rebuild correctly?
        assert root2['read_only_branch',0][0].is_tree_read_only
        assert root2['read_only_branch',0][1].is_value_read_only
        assert root2['read_only_branch',0][2].is_tree_read_only
        assert root2['read_only_branch', 0][2].is_value_read_only
        root2['read_only_branch', 0][2].unset_value_read_only()
        assert root == root2
        assert not root.equal(root2, True, True)
        root2['read_only_branch', 0][2].set_value(1)
        assert root != root2

        assert root==root.copy()
        print('Exec copy() time: %f s' % (
                calc_timeit(lambda: root2.copy(), number=1)))

        print('Exec sort() time: %f s' % (
                calc_timeit(lambda: root2.sort(), number=1) ))
        #print('Exec sort_deep() time: %f s' % (
        #            timeit.timeit(lambda: root2.sort_deep(), number=1) / 1))

        assert  last_item in root.deep
        print('Exec contains_deep() time: %f s' % (
                calc_timeit(lambda: root.deep.__contains__(last_item), number=10) ))
        assert root.deep.is_in(last_item)
        print('Exec all.is_in() time: %f s' % (
                calc_timeit(lambda: root.deep.is_in(last_item), number=10)))
        assert root.deep.index(last_item)
        print('Exec index_deep() time: %f s' % (
                calc_timeit(lambda: root.deep.index(last_item), 10) ))
        print('Exec .all.idx_paths() time: %f s' % (
                calc_timeit(lambda: list(root.deep.idx_paths()), 1)))

        #root.render()
        print('\nRESULT OF TEST: full featured iTree 1 -> PASS')

    def test2_full_featured_tree2_test(self):
        print('\nRUN OF TEST: full featured iTree 2 (linked)')

        # we create 2 deep items load the link in second level of both trees
        print('Current recursion limit is: %s' % sys.getrecursionlimit())
        depth = sys.getrecursionlimit() - 100
        root_data_path = get_relpath_to_root('tmp')
        print('Temporary files stored in %s'%root_data_path)
        target_path = root_data_path + '/out.itr'
        assert os.path.exists(target_path), 'We need resulting file of test1 for this test, related file not found'
        target_path2 = root_data_path + '/out2.itr'

        root=iTree('root')
        p1=root.append(iTree('part1'))
        sub=p1
        for i in range(depth):
            # serializer cannot handle deeper trees at the moment
            sub = sub.append(iTree(i, i))

        p2=root.append(iTree('part2'))
        sub=p2
        for i in range(depth):
            # serializer cannot handle deeper trees at the moment
            sub = sub.append(iTree((i,i), i))

        print('The build iTree has a depth of %i' % (depth+1))

        #create the link elements:
        link1=p1.append(iTree('link1',link=iTLink(target_path)))
        p1.append(iTree('after item'))
        link2=p2.append(iTree('link2', link=iTLink(target_path, ['root'])))
        p2.append(iTree('after item'))
        assert Tag('after item') not in p2
        a=len(root.deep)

        root.load_links()
        #insert some locals
        link1.insert(0, iTree('local', 0))
        link1.insert(1,iTree('local',1))
        link1.insert(2, iTree('local',2))
        link1.insert(-1, iTree('local', 3))

        link2.insert(0, iTree('local', 0))
        link2.insert(1,iTree('local',1))
        link2.insert(2, iTree('local',2))
        link2.insert(-1, iTree('local', 3))
        s=len(root.deep)
        b=link2[3]
        assert link2[3].is_linked
        s2=len(link2[3].deep)
        link2[3].make_local()
        assert not link2[3].is_linked
        assert s2==len(link2[3].deep)
        assert link2[4].is_linked
        link2[4].make_local()
        assert not link2[4].is_linked
        assert len(root.deep) == s

        n=len(iTree().load(target_path).deep)
        print('Exec time number of all items: %f s:' % calc_timeit(root.deep.__len__, 10))
        print('iTree size before load: %i'%a)
        print('iTree size of linked items: %i' % (2*n))
        assert len(root.deep) == a + 2 * n + 8 # 8 locals added
        print('iTree size after load links: %i -> checked: ok' % (2 * n+a+8))
        #assert root.tree.filtered_len(filter_method=lambda i: i.is_value_read_only, hierarcical=False) == 12
        #assert root.tree.filtered_len(filter_method=lambda i: i.is_tree_read_only, hierarcical=False) == 18
        #assert root.tree.filtered_len(filter_method=lambda i: i.is_value_read_only, hierarcical=False) == 12
        print('Exec time max_depth(): %f s:' % calc_timeit(lambda: root.max_depth, 10))
        print('iTree max_depth: %i' % root.max_depth)
        assert root.max_depth==902
        copy_root=root.copy()
        assert root == copy_root
        print('Exec time copy(): %f s:' % calc_timeit(lambda: root.copy(), 10))
        root.load_links()
        print('Exec dump() time: %f s' % (calc_timeit(lambda: root.dump(target_path2,pack=False,overwrite=True),1)))
        root2 = iTree().load(target_path2,load_links=False)
        root2.load_links()
        print('Exec load() time: %f s' % (calc_timeit(lambda: iTree().load(target_path,load_links=True), 1)))
        assert len(root.deep) == len(root2.deep)

        assert root == root2

        for i0,(i,ii) in enumerate(zip(root.deep, root2.deep)):
            args1=i.get_init_args(_subtree_not_none=False)
            args2=ii.get_init_args(_subtree_not_none=False)
            assert any(a==b for a,b in zip(args1,args2)),'%i: %s != %s -> expected equal items'%(i0,repr(args1),repr(args2))

        # root.render()

        print('\nRESULT OF TEST: full featured iTree 2 (linked) -> PASS')






