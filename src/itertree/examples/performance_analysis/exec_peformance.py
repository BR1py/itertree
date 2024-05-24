from __future__ import absolute_import

import pickle
import timeit
import os
import tempfile
import sys
import copy
from itertools import dropwhile, islice
from itertree import *
import collections

EXEC_CONTROL = ['L1_5000', 'L1_50000', 'L1_500000', 'Ln_100', 'Ln_500', 'Ln_1000']
SUB_EXEC_CONTROL = [1,  # append
                    2,  # extend
                    3,
                    4,  # copy
                    5,  # compare
                    6,  # get by index
                    7,  # get by key
                    8,  # get index_slice
                    9,
                    10,
                    11,  # specific
                    12 # delete items
                    ]
CREATE_DOCS = [1]
# EXEC_CONTROL = ['Ln_100','Ln_500','Ln_1000']
EXEC_CONTROL = ['L1_500000','Ln_1000']
SUB_EXEC_CONTROL = [1]

# EXEC_CONTROL = ['L1_5000', 'L1_50000', 'L1_500000','Ln_100','Ln_500','Ln_1000']
# SUB_EXEC_CONTROL = [1,6]

TEST_OBJECTS = collections.OrderedDict([
    ('iTree', {'str': 'itertree.iTree', 'class': iTree}),
    ('list', {'str': 'build-in list', 'class': list}),
    ('dict', {'str': 'build-in dict', 'class': dict}),
    ('deque', {'str': 'collections.deque', 'module': collections, 'class': collections.deque}),
    ('odict', {'str': 'collections.OrderedDict', 'module': collections, 'class': collections.OrderedDict}),
])
try:
    import blist

    TEST_OBJECTS['blist'] = {'str': 'blist.blist', 'module': blist, 'class': blist.blist}
    if not CREATE_DOCS:
        # we do not append this part in the docs
        TEST_OBJECTS['bl_sorteddict'] = {'str': 'blist.sorteddict', 'module': blist, 'class': blist.sorteddict,
                                         'init': 'sorteddict'}

except ImportError:
    pass

try:
    import sortedcontainers as SC

    if not CREATE_DOCS:
        # we do not append this part in the docs
        TEST_OBJECTS['SC.SortedDict'] = {'str': 'sortedcontainers.SortedDict', 'module': SC, 'class': SC.SortedDict,
                                         'init': 'SortedDict'}
except ImportError:
    pass

try:
    import indexed

    TEST_OBJECTS['iodict'] = {'str': 'indexed.IndexedOrderedDict', 'module': indexed,
                              'class': indexed.IndexedOrderedDict, 'init': 'IndexedOrderedDict'}
    TEST_OBJECTS['idict'] = {'str': 'indexed.Dict', 'module': indexed, 'class': indexed.Dict, 'init': 'Dict'}
except ImportError:
    pass

import xml.etree.ElementTree as ET

TEST_OBJECTS['XML.Element'] = {'str': 'xml.etree.ElementTree.Element', 'module': ET, 'class': ET.Element,
                               'init': 'Element'}

try:
    import lxml.etree as LXML_ET

    TEST_OBJECTS['LXML.Element'] = {'str': 'lxml.etree.Element', 'module': LXML_ET, 'class': LXML_ET.Element,
                                    'init': 'Element'}
except ImportError:
    pass

try:
    import pyTooling.Tree as PT

    TEST_OBJECTS['PT.Node'] = {'str': 'pyTooling.Tree.Node', 'module': PT, 'class': PT.Node, 'init': 'Node'}
except ImportError:
    pass

try:
    import itertree.examples.performance_analysis.lldict4 as lldict

    if not CREATE_DOCS:
        # we do not append this part in the docs
        TEST_OBJECTS['llDict'] = {'str': 'lldict4.llDict', 'module': lldict, 'class': lldict.llDict}
except ImportError:
    pass

try:
    import treelib as TL

    TEST_OBJECTS['TL.Tree'] = {'str': 'treelib.Node', 'module': TL, 'class': TL.Tree, 'init': 'Tree'}
except ImportError:
    pass

try:
    import anytree as AT

    TEST_OBJECTS['AT.Node'] = {'str': 'anytree.Node', 'module': AT, 'class': AT.Node, 'init': 'Node'}
except ImportError:
    pass

try:
    import bigtree as BT

    TEST_OBJECTS['BT.Node'] = {'str': 'bigtree.Node', 'module': BT, 'class': BT.Node, 'init': 'Node'}
except ImportError:
    pass

# -- part 1 huge level 1 tree ------------------------------------------------------------------------------------------


repeat = 3
WIDTH = 75

itree_only = False

from itertree import iTree, __version__, Tag, iTFLAG, iTLink

print('Python: ', sys.version)
try:
    import blist

    print('blist package is available and used')
except:
    print('blist package is not available (normal list is used)')
    blist = None

print('itertree version: %s' % __version__)

TMP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tmp'))
if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)
print('Using tmp folder: %s' % TMP_FOLDER)

print(
    'A relative values >1 related to iTree means the other object is faster\n(relative values <1 means iTree is faster)')
print('\nFor item access comparisons we use: idx for absolute index and tag_idx for key related access')
print('the relative values given are the specific (no type check) '
      '\nand (in brackets - with type check) the common access')
print('\nIn the item access operations we access each item in the object (via\nloop)!')

print('\n\nFor non nested classes (e.g. lists or dicts) we instance also a sub-structure. \n'
      'This means we store value and sub-structure.\n'
      'e.g. [("value1",[]),("value2",[])] or {"tag1":("value1",{}),"tag2":("value2",{})}\n'
      'But for item access we target the value-subtree-tuple only')

print('\n\nThe given operations are not in all cases executable (shorten string) '
      'it should just give an idea of the used functions.\n')

trees = {}
trees2 = {}

from itertree.examples.performance_analysis.test_append import TestBuildByAppendL1, TestBuildByAppendLn
from itertree.examples.performance_analysis.test_extend import TestBuildByExtendL1
from itertree.examples.performance_analysis.test_insert import TestBuildByInsertL1
from itertree.examples.performance_analysis.test_copy import TestCopyL1, TestCopyLn
from itertree.examples.performance_analysis.test_compare import TestCompareL1
from itertree.examples.performance_analysis.test_get_by_idx import TestGetByIdxL1, TestGetByIdxLn
from itertree.examples.performance_analysis.test_get_by_key import TestGetByKeyL1, TestGetByKeyLn
from itertree.examples.performance_analysis.test_get_by_idx_slice import TestGetByIdxSliceL1
from itertree.examples.performance_analysis.test_iter import TestIterL1, TestIterLn
from itertree.examples.performance_analysis.test_save_load import TestSaveLoadL1
from itertree.examples.performance_analysis.test_itree_specific import TestiTreeSpecificL1, TestiTreeSpecificLn
from itertree.examples.performance_analysis.test_delete import TestDeleteL1


class Test_level1_tree():

    def __init__(self):
        self.trees = {}
        self.trees2 = {}
        self.trees3 = {}

        self.max_items, self.slice_operation_factor = 5000, 1
        self.test_class_key = 'L1_5000'
        self.print_main_header()

    def print_main_header(self):
        print(
            '\n###########################################################'
            '####################################################')
        print('Performance analysis related to L1 only trees with a size of %i (slice operations limited to %i)' % (
            self.max_items, self.max_items / self.slice_operation_factor))
        print(
            '###########################################################'
            '####################################################\n')

    def exec_test(self, nr):
        global EXEC_CONTROL, SUB_EXEC_CONTROL
        return self.test_class_key in EXEC_CONTROL and nr in SUB_EXEC_CONTROL

    def instance_test_item(self, test_class):
        return test_class(
            TEST_OBJECTS,
            self.trees,
            self.trees2,
            self.max_items,
            self.slice_operation_factor,
            WIDTH,
            repeat,
            itree_only,
            TMP_FOLDER
        )

    def test1_append_level1_tree(self):
        test_item = self.instance_test_item(TestBuildByAppendL1)
        if self.exec_test(1):
            self.trees, self.trees2 = test_item.test_exec()
        else:
            print(test_item.get_header())
            print('Test (1) skipped')

    def test2_extend_level1_tree(self):
        test_item = self.instance_test_item(TestBuildByExtendL1)
        if self.exec_test(2):
            self.trees, self.trees2 = test_item.test_exec()
        else:
            print(test_item.get_header())
            print('Test (2) skipped')

    def test3_insert_level1_tree(self):
        test_item = self.instance_test_item(TestBuildByInsertL1)
        if self.exec_test(3):
            self.trees, self.trees2 = test_item.test_exec()
        else:
            print(test_item.get_header())
            print('Test (3) skipped')

    def test4_copy_level1_tree(self):
        test_item = self.instance_test_item(TestCopyL1)
        if self.exec_test(4):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2, it_t3 = test_item.test_exec(key, it_t1, it_t2, it_t3)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (4) skipped')

    def test5_compare_level1_tree(self):
        test_item = self.instance_test_item(TestCompareL1)
        if self.exec_test(5):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees2:  # here we target trees2!
                    try:
                        _, _, it_t1, it_t2 = test_item.test_exec(key, it_t1, it_t2)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (5) skipped')

    def test6_get_item_by_index_level1_tree(self):
        test_item = self.instance_test_item(TestGetByIdxL1)
        if self.exec_test(6):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2 = test_item.test_exec(key, it_t1, it_t2)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (6) skipped')

    def test7_get_item_by_key_level1_tree(self):
        test_item = self.instance_test_item(TestGetByKeyL1)
        if self.exec_test(7):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2 = test_item.test_exec(key, it_t1, it_t2)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (7) skipped')

    def test8_get_item_by_index_slice_level1_tree(self):
        test_item = self.instance_test_item(TestGetByIdxSliceL1)
        if self.exec_test(8):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2 = test_item.test_exec(key, it_t1, it_t2)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (8) skipped')

    def test9_iter_level1_tree(self):
        test_item = self.instance_test_item(TestIterL1)
        if self.exec_test(9):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2 = test_item.test_exec(key, it_t1, it_t2)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (9) skipped')

    def test_10_save_load_level1_tree(self):
        test_item = self.instance_test_item(TestSaveLoadL1)
        if self.exec_test(10):
            print(test_item.get_header())
            it_t1, it_t2, it_t3, it_t4 = None, None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2, it_t3, it_t4 = test_item.test_exec(key, it_t1, it_t2, it_t3, it_t4)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (10) skipped')

    def test_11_itree_specific_level1_tree(self):
        test_item = self.instance_test_item(TestiTreeSpecificL1)
        if self.exec_test(11):
            print(test_item.get_header())
            test_item.test_exec()
        else:
            print(test_item.get_header())
            print('Test (11) skipped')

    def test_12_delete_tree(self):
        test_item = self.instance_test_item(TestDeleteL1)
        if self.exec_test(12):
            print(test_item.get_header())
            test_item.prepare_test_trees()
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2,it_t3 = test_item.test_exec(key, it_t1, it_t2,it_t3)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (12) skipped')


class Test2_level1_tree(Test_level1_tree):

    def __init__(self):
        self.trees = {}
        self.trees2 = {}
        self.max_items, self.slice_operation_factor = 50000, 10
        self.test_class_key = 'L1_50000'
        self.print_main_header()


class Test3_level1_tree(Test_level1_tree):

    def __init__(self):
        self.trees = {}
        self.trees2 = {}
        self.max_items, self.slice_operation_factor = 500000, 100
        self.test_class_key = 'L1_500000'
        self.print_main_header()


class Test_n_LevelTree():

    def __init__(self):
        global trees, trees2
        tree = {}
        trees2 = {}
        self.max_items, self.slice_operation_factor = 100, 1
        self.items_per_level = 10
        self.test_class_key = 'Ln_100'
        self.print_main_header()

    def print_main_header(self):
        print(
            '\n###########################################################'
            '####################################################')
        print(
            'Performance analysis related to trees with depth %i and a size of %i (slice operations limited to %i)' % (
                self.max_items, self.max_items * self.items_per_level, self.max_items / self.slice_operation_factor))
        print(
            '###########################################################'
            '####################################################\n')

    def exec_test(self, nr):
        global EXEC_CONTROL, SUB_EXEC_CONTROL
        return self.test_class_key in EXEC_CONTROL and nr in SUB_EXEC_CONTROL

    def instance_test_item(self, test_class):
        tc = test_class(
            TEST_OBJECTS,
            trees,
            trees2,
            self.max_items,
            self.slice_operation_factor,
            WIDTH,
            repeat,
            itree_only,
            TMP_FOLDER
        )
        tc.set_items_per_level = self.items_per_level
        return tc

    def test1_append_n_levels_tree(self):
        global trees, trees2
        test_item = self.instance_test_item(TestBuildByAppendLn)
        if self.exec_test(1):
            self.trees, self.trees2 = test_item.test_exec()
        else:
            print(test_item.get_header())
            print('Test (1) skipped')

    def test4_copy_n_levels_tree(self):
        global trees, trees2
        test_item = self.instance_test_item(TestCopyLn)
        if self.exec_test(4):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2, it_t3 = test_item.test_exec(key, it_t1, it_t2, it_t3)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
            else:
                print('%s no test source was build (append())                             '
                      '-> operation skipped' % TEST_OBJECTS[key]['str'])
        else:
            print(test_item.get_header())
            print('Test (4) skipped')

    def test6_get_item_by_index_n_levels_tree(self):
        global trees, trees2
        test_item = self.instance_test_item(TestGetByIdxLn)
        if self.exec_test(6):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2 = test_item.test_exec(key, it_t1, it_t2)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])

        else:
            print(test_item.get_header())
            print('Test (6) skipped')

    def test7_get_item_by_key_n_levels_tree(self):
        global trees, trees2
        test_item = self.instance_test_item(TestGetByKeyLn)
        if self.exec_test(7):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2 = test_item.test_exec(key, it_t1, it_t2)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])

        else:
            print(test_item.get_header())
            print('Test (7) skipped')

    def test9_iter_level1_tree(self):
        global trees, trees2
        test_item = self.instance_test_item(TestIterLn)
        if self.exec_test(9):
            print(test_item.get_header())
            it_t1, it_t2, it_t3 = None, None, None
            for key in TEST_OBJECTS.keys():
                if key in self.trees:
                    try:
                        _, _, it_t1, it_t2 = test_item.test_exec(key, it_t1, it_t2)
                    except AssertionError:
                        print('*** Test issue in %s' % key)
                        raise
                else:
                    print('%s no test source was build (append())                             '
                          '-> operation skipped' % TEST_OBJECTS[key]['str'])

        else:
            print(test_item.get_header())
            print('Test (9) skipped')

    def test_11_itree_specific_level1_tree(self):
        test_item = self.instance_test_item(TestiTreeSpecificLn)
        if self.exec_test(11):
            print(test_item.get_header())
            test_item.test_exec()
        else:
            print(test_item.get_header())
            print('Test (11) skipped')


class Test2_n_LevelTree(Test_n_LevelTree):

    def __init__(self):
        global trees, trees2
        tree = {}
        trees2 = {}
        self.max_items, self.slice_operation_factor = 500, 100
        self.test_class_key = 'Ln_500'
        self.items_per_level = 10
        self.print_main_header()


class Test3_n_LevelTree(Test_n_LevelTree):

    def __init__(self):
        global trees, trees2
        tree = {}
        trees2 = {}
        self.max_items, self.slice_operation_factor = 1000, 100
        self.test_class_key = 'Ln_1000'
        self.items_per_level = 10
        self.print_main_header()


if __name__ == '__main__':
    test_classes = [Test_level1_tree, Test2_level1_tree, Test3_level1_tree, Test_n_LevelTree, Test2_n_LevelTree,
                    Test3_n_LevelTree]
    for test_class in test_classes:
        test_obj = test_class()
        if test_obj.test_class_key in EXEC_CONTROL:
            for item in dir(test_obj):
                method = test_obj.__getattribute__(item)
                if item.startswith('test') and callable(method):
                    method()
        else:
            print('---> disabled')
