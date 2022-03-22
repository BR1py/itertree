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

This test suite focuses on the linking and "covering mechanisms" available in iTree
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

TEST_SELECTION = {1, 2, 3}

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

    def test1_linking(self):
        if not 1 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: external and internal linking')

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
        # data can be changed
        linked_item.d_set('DATA', 'TEST')
        # but not in the sub items!
        with pytest.raises(PermissionError):
            linked_item[1].d_set('DATA', 'TEST')
        for i, item in enumerate(root.iter_all()):
            if i == 0:
                assert not item.is_linked
            elif i == 1:
                assert item.tag == 'LINKED'
                assert item.is_linked
            elif i > 2 and i <= 101:
                assert item.is_linked
            elif i == 101:
                assert item.d_get('level') == 'n99'
            elif i == 102:
                assert not item.is_linked
                assert item.tag == 'c2'
            elif i > 102:
                assert not item.is_linked

        for i, item in enumerate(root.iter_all(Filter.iTFilterItemType(iTreeLink, invert=True))):
            assert not item.is_linked
        for i, item in enumerate(root.iter_all(Filter.iTFilterItemType(iTreeLink))):
            assert item.is_linked

        print('PASSED')

    def test2_link_external_and_internal(self):
        if not 2 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: external and internal linking part2')

        # first we create a simple tree and write it into a file
        root = iTree('root')
        root += iTree('A')
        root += (iTree('B'))
        root += (iTree('C'))

        A = root[0]
        A += (iTree('Aa'))
        A += (iTree('Ab'))
        A += (iTree('Ac'))

        root[1].append(iTree('Ba', 'dataBa'))
        root[1].append(iTree('Bb', 'dataBb'))
        root[1].append(iTree('Bc', 'dataBc'))
        root.get_deep([1, 0]).append(iTree('Baa', 'dataBaa'))
        root.get_deep([1, 0]).append(iTree('Bab', 'dataBab'))
        root.get_deep([1, 0]).append(iTree('Bac', 'dataBac'))

        root_data_path = get_relpath_to_root('tmp')
        if not os.path.exists(root_data_path):
            os.makedirs(root_data_path)
        target_path = root_data_path + '/out.dtz'
        root.dump(target_path=target_path, overwrite=True)
        # we build a second tree
        root = iTree('local_root')
        root += iTree('A')
        root.append(iTree('C'))
        root[1].append(iTree('Ca'))
        root[1].append(iTree('Cb'))
        root[1].append(iTree('Cc'))
        root.get_deep([1, 0]).append(iTree('Caa', 'dataCaa'))
        root.get_deep([1, 0]).append(iTree('Cab', 'dataCab'))
        root.get_deep([1, 0]).append(iTree('Cac', 'dataCac'))
        # Now we link a part of the first tree into the this tree (link to subtree in a file
        linked_item = iTreeLink('FILE_LINK', data=0, link_file_path=target_path, link_key_path=1, load_links=False)
        root.insert(1, linked_item)
        # as long as we did not load the links we expect in this case no children
        assert len(linked_item) == 0
        # now we load the linked items
        root.load_links()
        assert len(linked_item) == 3
        assert len(list(linked_item.iter_all())) == 6
        # data of the linked item can be changed
        linked_item.d_set('NEW_DATA', 'TEST')
        # we recheck if we cannot change the data of the linked sub items
        with pytest.raises(PermissionError):
            linked_item[1].d_set('DATA', 'TEST')

        # create an internal link:
        linked_item2 = iTreeLink('INTERNAL_LINK', data=0, link_file_path=None, link_key_path=['/', 2, 0],
                                 load_links=False)
        # we append the linked item at the end of the tree
        root.append(linked_item2)
        assert len(linked_item2) == 0
        # load the link
        root.load_links()
        assert len(linked_item2) == 3
        # data of the linked item can be changed
        linked_item2.d_set('NEW_DATA2', 'TEST2')
        # we recheck if we cannot change the data of the linked sub items
        with pytest.raises(PermissionError):
            linked_item2[1].d_set('DATA', 'TEST')
        # check that circular linking is denied
        linked_item3 = iTreeLink('INTERNAL_LINK2', data=0, link_file_path=None, link_key_path=['INTERNAL_LINK'],
                                 load_links=False)
        root.append(linked_item3)
        # check circular protection
        with pytest.raises(TypeError):
            root.load_links()
        # we load the links with delete_invalid_items_flag, this will clean the tree before the save!
        l1 = len(root)
        root.load_links(delete_invalid_items=True)
        assert (l1 - 1) == len(root)  # last item should be deleted!

        # save the tree with linked items
        root_data_path = get_relpath_to_root('tmp')
        if not os.path.exists(root_data_path):
            os.makedirs(root_data_path)
        target_path = root_data_path + '/out_linked.dt'
        root.dump(target_path=target_path, overwrite=True, pack=False)

        root2 = iTree('root').load(target_path, load_links=False)
        assert len(root2) == len(root)
        last = root2[-1]
        for i, item in enumerate(root2.iter_children()):
            if i == 1 or item == last:
                assert item.is_linked
            else:
                assert not item.is_linked

        root2.load_links()
        assert len(list(root2.iter_all())) == 19

        # print(root2.render())
        print('PASSED')

    def test3_overloading_tags(self):
        if not 3 in TEST_SELECTION:
            return

        print('\nRESULT OF TEST: local elements in linked items')

        # first we create a simple tree
        root = iTree('root')
        root += iTree('A')
        root += iTree('A')

        root.append(iTree('B', data='B0'))
        root.append(iTree('B', data='B1'))
        root.append(iTree('C'))

        A = root[1]
        A.append(iTree('Aa'))
        A.append(iTree('Ab'))
        A.append(iTree('Ab'))
        A.append(iTree('Ac'))

        root[3].append(iTree('Ba', 'dataBa'))
        root[3].append(iTree('Bb', 'dataBb0'))
        root[3].append(iTree('Bb', 'dataBb1'))
        root[3].append(iTree('Bc', 'dataBc'))
        root.get_deep([3, 0]).append(iTree('Baa', 'dataBaa'))
        root.get_deep([3, 0]).append(iTree('Bab', 'dataBab0'))
        root.get_deep([3, 0]).append(iTree('Bab', 'dataBab1'))
        root.get_deep([3, 0]).append(iTree('Bac', 'dataBac'))

        root.get_deep([3, 2]).append(iTree('Bba', 'dataBba'))
        root.get_deep([3, 2]).append(iTree('Bbb', 'dataBbb0'))
        root.get_deep([3, 2]).append(iTree('Bbb', 'dataBbb1'))
        root.get_deep([3, 2]).append(iTree('Bbc', 'dataBbc'))

        # we add an internal link
        linked_item2 = iTreeLink('INTERNAL_LINK', data=0, link_file_path=None, link_key_path=['/', TagIdx('B', 1)],
                                 load_links=False)
        root.append(linked_item2)
        root.load_links()
        l = len(list(root.iter_all()))
        assert l == 34
        #print(root.render())
        # we try to make a subitem local, this should fail
        sub_item = linked_item2.find('Ba/Baa')
        assert sub_item is not None
        assert type(sub_item) is iTreeLink

        with pytest.raises(TypeError):
            sub_item.make_self_local()

        print(repr(linked_item2))
        # one leve higher it shoudl work
        sub_item = linked_item2.find(TagIdx('Bb', 1))
        with pytest.raises(PermissionError):
            sub_item.append(iTree('new'))
        # print(root.render())
        # we make an item local and we "overload" the contants by changing the sub elements and the data
        local = sub_item.make_self_local()
        assert type(sub_item) != type(local)
        assert sub_item.tag == local.tag
        assert sub_item.data == local.data
        sub_item_new = linked_item2.find(TagIdx('Bb', 1))
        assert sub_item_new == local
        # we change the data
        local.d_set('OVERLOAD')

        # we change the subtree
        new = iTree('new')
        local.append(new)
        not_linked = {6, 7, 8, 9, 10, 11}
        # print(linked_item2.render())
        for i, item in enumerate(linked_item2.iter_all()):
            if i in not_linked:
                assert not item.is_linked, '%i' % i
            else:
                assert item.is_linked, '%i' % i
        new.d_set('NEW_DATA')

        # we run the other allowed operations
        linked_item2 += (iTree('append1'))
        linked_item2.append(iTree('append2'))
        new2 = iTree('extend', subtree=[iTree('sub_extend1'), iTree('sub_extend2')])
        linked_item2.append(new2)
        linked_item2.extend(new2)

        # we run the not allowed operations:
        sub_item = linked_item2.get_deep([TagIdx('Ba', 0), TagIdx('Baa', 0)])
        with pytest.raises(TypeError):
            sub_item.make_self_local()
        with pytest.raises(PermissionError):
            sub_item.append(iTree('TEST'))
        with pytest.raises(PermissionError):
            sub_item.d_set('KEY', 'DATA')
        with pytest.raises(PermissionError):
            sub_item.rename('new_name')
        with pytest.raises(PermissionError):
            linked_item2.insert(7, iTree('TEST'))
        with pytest.raises(PermissionError):
            linked_item2.appendleft(iTree('TEST'))
        with pytest.raises(PermissionError):
            linked_item2.extendleft([iTree('TEST')])
        with pytest.raises(PermissionError):
            linked_item2.rotate(2)

        # we store the tree for later reload (check if locals stored correctly)!
        root_data_path = get_relpath_to_root('tmp')
        if not os.path.exists(root_data_path):
            os.makedirs(root_data_path)
        target_path = root_data_path + '/out_linked.dt'
        root.dump(target_path=target_path, overwrite=True, pack=False)

        # now we check if we can delete the local and the old linked item appears again:
        l = len(linked_item2)
        del linked_item2[2]
        # check item and neighbors
        assert linked_item2[1].tag == 'Bb'
        assert linked_item2[1].is_linked
        assert linked_item2[2].tag == 'Bb'
        assert linked_item2[2].is_linked
        assert linked_item2[3].tag == 'Bc'
        assert linked_item2[3].is_linked

        l2 = len(linked_item2)
        assert l == l2
        del linked_item2['sub_extend2']
        assert l - 1 == len(linked_item2)

        # print(root.render())

        # reload data from file with load_links = False flag
        root2 = iTree('TMP').load(target_path, load_links=False)
        # check for placeholders!
        assert root2.get_deep([TagIdx('INTERNAL_LINK', 0), 0]).is_placeholder
        assert len(list(root2.iter_all())) == 36
        root2.load_links()
        assert len(list(root2.iter_all())) == 42

        # print(root2.render())
        print('PASSED')
