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
from itertree.itree_helpers import *

root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

TEST_SELECTION = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
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


class Test1_iTree_FLAGS():

    def test1_read_only_value(self):
        if not 1 in TEST_SELECTION:
            return
        print('\nRESULT OF SUB-TEST: Read only value')
        # build a read only value tree
        root=iTree('root',[1],subtree=[iTree(1,[1,1],subtree=[iTree(1,[1,1,1],flags=iTFLAG.READ_ONLY_VALUE),
                                                              iTree(2,[1,1,2],flags=iTFLAG.READ_ONLY_VALUE),
                                                              iTree(3,[1,1,3],flags=iTFLAG.READ_ONLY_VALUE)],
                                             flags=iTFLAG.READ_ONLY_VALUE),
                                       iTree(2, [1, 2],
                                             subtree=[iTree(1, [1, 2, 1],flags=iTFLAG.READ_ONLY_VALUE),
                                                      iTree(2, [1, 2, 2],flags=iTFLAG.READ_ONLY_VALUE),
                                                      iTree(3, [1, 2, 3],flags=iTFLAG.READ_ONLY_VALUE)],
                                             flags=iTFLAG.READ_ONLY_VALUE),
                                       iTree(3, [1, 3],
                                             subtree=[iTree(1, [1, 3, 1],flags=iTFLAG.READ_ONLY_VALUE),
                                                      iTree(2, [1, 3, 2],flags=iTFLAG.READ_ONLY_VALUE),
                                                      iTree(3, [1, 3, 3],flags=iTFLAG.READ_ONLY_VALUE)],
                                             flags=iTFLAG.READ_ONLY_VALUE)
                                       ],flags=iTFLAG.READ_ONLY_VALUE)
        assert root.flags&iTFLAG.READ_ONLY_VALUE
        assert root.flags_repr() =='iTFLAG.READ_ONLY_VALUE'
        for i in root.deep:
            assert i.flags&iTFLAG.READ_ONLY_VALUE

        with pytest.raises(PermissionError):
            root.set_value(1)
        with pytest.raises(PermissionError):
            root[1].set_value(1)
        with pytest.raises(PermissionError):
            root[2][0].set_value(1)
        # switch a child to writeable
        root[1].unset_value_read_only()
        root[1].set_value(1)
        assert root[1].value==1
        # children should be still protected
        with pytest.raises(PermissionError):
            root[1][0].set_value(1)
        # parent should be still protected
        with pytest.raises(PermissionError):
            root.set_value(1)
        #set the item back to read-only value
        root[1].set_value_read_only()
        with pytest.raises(PermissionError):
            root[1].set_value(2)
        # set the whole sub-tree into writeable value
        root[1].deep.unset_value_read_only()
        root[1].set_value(8)
        assert root[1].value == 8
        root[1][0].set_value(8)
        assert root[1][0].value == 8
        root[1][-1].set_key_value(0,8)
        assert root[1][-1].value[0] == 8
        # parent is still protected
        with pytest.raises(PermissionError):
            root.set_value(2)
        # set single item back in protected mode
        root[1].set_value_read_only()
        with pytest.raises(PermissionError):
            root[1].set_value(2)
        root[1][0].set_value(9)
        assert root[1][0].value == 9

        # set whole tree back to read_only
        root.deep.set_value_read_only()
        with pytest.raises(PermissionError):
            root[1][0].set_value(9)

        print('\nRESULT OF SUB-TEST: Read only value')

    def test2_read_only_tree(self):
        if not 2 in TEST_SELECTION:
            return
        print('\nRESULT OF SUB-TEST: Read only tree')
        # build a read only value tree
        root=iTree('root',[1],subtree=[iTree(1,[1,1],
                                             subtree=[iTree(1,[1,1,1]),
                                                      iTree(2,[1,1,2]),
                                                      iTree(3,[1,1,3])]),
                                       iTree(2, [1, 2],
                                             subtree=[iTree(1, [1, 2, 1]),
                                                      iTree(2, [1, 2, 2]),
                                                      iTree(3, [1, 2, 3])]),
                                       iTree(3, [1, 3],
                                             subtree=[iTree(1, [1, 3, 1]),
                                                      iTree(2, [1, 3, 2]),
                                                      iTree(3, [1, 3, 3])])
                                       ],
                   flags=iTFLAG.READ_ONLY_TREE)
        # The whole tree should have a protected structure
        with pytest.raises(PermissionError):
            root.append(1)
        for i in root.deep:
            with pytest.raises(PermissionError):
                i.append(1)

        # we test al tree manipulating methods first:
        with pytest.raises(PermissionError):
            root+= 0
        with pytest.raises(PermissionError):
            root.insert(0,0)
        with pytest.raises(PermissionError):
            root.appendleft(0)
        with pytest.raises(PermissionError):
            root.extend([0,1])
        with pytest.raises(PermissionError):
            root.extendleft([0, 1])
        with pytest.raises(PermissionError):
            root[1],root[0]=root[0],root[1]
        with pytest.raises(PermissionError):
            root[1].move(0)
        with pytest.raises(PermissionError):
            root[1].rename('tag')
        with pytest.raises(PermissionError):
            del root[1]
        with pytest.raises(PermissionError):
            root[1].pop(1)
        with pytest.raises(PermissionError):
            root[1].remove(root[1][0])
        with pytest.raises(PermissionError):
            root.reverse()
        with pytest.raises(PermissionError):
            root.deep.reverse()
        with pytest.raises(PermissionError):
            root.sort()
        with pytest.raises(PermissionError):
            root.deep.sort()
        with pytest.raises(PermissionError):
            root.rotate()
        with pytest.raises(PermissionError):
            root.clear()
        # not allowed changes of the flag
        with pytest.raises(PermissionError):
            root[1].unset_tree_read_only()
        root.unset_tree_read_only()
        root.append(iTree(3,1))
        # lower tree is still locked
        with pytest.raises(PermissionError):
            root[1].append(1)
        # lock tree again:
        root.set_tree_read_only()
        with pytest.raises(PermissionError):
            root.append(1)
        # unlock whole tree
        # not allowed in lower levels:
        with pytest.raises(PermissionError):
            root[1].deep.unset_tree_read_only()
        # unlock whole tree
        root.deep.unset_tree_read_only()
        root[0][0].append(iTree('new',1))
        # lock a subtree part
        root[0].set_tree_read_only()
        # recheck that the whole suptree is locked
        with pytest.raises(PermissionError):
            root[0].append(2)
        with pytest.raises(PermissionError):
            root[0][0].append(2)
        # sibling works
        root[1].append(iTree(2))
        # parent works
        root.append(iTree(2))
        # lock whole tree again
        root.set_tree_read_only()
        with pytest.raises(PermissionError):
            root.append(iTree(2))
        with pytest.raises(PermissionError):
            root[1].append(iTree(2))

        print('\nRESULT OF SUB-TEST: Read only tree')



