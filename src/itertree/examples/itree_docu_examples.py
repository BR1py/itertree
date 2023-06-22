"""# -*- coding: utf-8 -*-#"""
from __future__ import absolute_import

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

This file contains teh examples presented in the itertree related documentation
"""

import os
import sys
import time
import shutil
import io
import traceback
import contextlib
from itertree import *
import datetime

DOT_DIR = os.path.join(os.path.dirname(__file__), 'dot_files')
if not os.path.exists(DOT_DIR):
    os.makedirs(DOT_DIR)

tutorial_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs', 'docs')
TUTORIAL_FILE_PATH = os.path.join(tutorial_dir, 'tutorial_new.rst')
if os.path.exists(TUTORIAL_FILE_PATH):
    os.remove(TUTORIAL_FILE_PATH)
shutil.copy(os.path.join(tutorial_dir, 'tutorial.rst'), TUTORIAL_FILE_PATH)

index_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs')
INDEX_FILE_PATH = os.path.join(tutorial_dir, 'index_new.rst')
if os.path.exists(INDEX_FILE_PATH):
    os.remove(INDEX_FILE_PATH)
shutil.copy(os.path.join(index_dir, 'index.rst'), INDEX_FILE_PATH)


def place_code_in_tutorial(stdout):
    with open(TUTORIAL_FILE_PATH, 'r') as fh:
        tutorial_str = fh.read()
    with open(INDEX_FILE_PATH, 'r') as fh:
        index_str = fh.read()

    stdout_start = 0
    targets = [('>>> # .. start: tutorial-code', tutorial_str),
               ('>>> # .. start: index-code', index_str)]
    for index, (file_identifier, target_str) in enumerate(targets):
        a = 0
        while (1):
            i1 = stdout.find(file_identifier, stdout_start)
            if i1 == -1:
                if index == 0:
                    tutorial_str = target_str
                elif index == 1:
                    index_str = target_str
                break
            i2 = stdout.find('\n', i1)
            stdout_start = i2
            search_str = stdout[(i1 + 6):i2]
            i3 = stdout.find(file_identifier, i2)
            if i3 == -1:
                code_str = stdout[(i2 + 1):]
            else:
                code_str = stdout[(i2 + 1):i3]
            i1 = target_str.find(search_str)
            if i1 != -1:
                i2 = target_str.find('\n', i1)
                i2 = target_str.find('\n', i2)
                i3 = target_str.find('::', i2)
                spaces = i3 - i2
                start = target_str.find('\n', i3) + 1
                end = target_str.find('.. end', i2)
                end = target_str.find('\n', end)
                new_code = []
                for line in code_str.splitlines(keepends=True):
                    new_code.append(' ' * spaces)
                    new_code.append(line)
                target_str = target_str[:start] + ''.join(new_code) + '\n' + ' ' * (spaces - 4) + \
                             '.. end - entry created: %s' % datetime.datetime.now().isoformat(
                    timespec='seconds') + target_str[end:]

    with open(TUTORIAL_FILE_PATH, 'w') as fh:
        fh.write(tutorial_str)
    with open(INDEX_FILE_PATH, 'w') as fh:
        fh.write(index_str)


def exec_and_print(command_series, name=None):
    with contextlib.redirect_stdout(io.StringIO()) as f:
        print()
        for command in command_series:
            if command == '':
                print()
                continue
            print('>>> %s' % command)
            try:
                result = eval(command)
                if result is not None:
                    print(result)
            except SyntaxError:
                try:
                    exec(command)
                except:
                    tb = traceback.format_exc()
                    print(tb)
            except:
                tb = traceback.format_exc().splitlines()
                print(tb[0])
                print('...')
                print(tb[-1])
    stdout = f.getvalue()
    print(stdout)
    place_code_in_tutorial(stdout)
    # create dot output
    if name:
        try:
            out = ''
            if 'itree' in locals():
                out = iTreeRenderDot(locals()['itree'])
            elif 'root' in locals():
                out = iTreeRenderDot(locals()['root'])
            elif 'tree' in locals():
                out = iTreeRenderDot(locals()['tree'])
            elif 'itree_mul' in locals():
                out = iTreeRenderDot(locals()['itree_mul'])

            if out:
                with open(os.path.join(DOT_DIR, name + '.dot'), 'w') as fh:
                    fh.write(out)
        except:
            raise
            pass


tutorial_QS1 = [
    '# .. start: tutorial-code QS1',
    "",
    "# Instance an iTree object by giving a tag, value and two subtree items (children):",
    "root = iTree('root', value=0, subtree=[iTree('item0', value=0), iTree('item1', value=1)])",
    "# append additional child with same tag!",
    "root.append(iTree('item1', value={'value1':2,'value2':3})) # any object can be used as values",
    "# list like operations are supported; e.g. insert():",
    "root.insert(2,iTree((1,2), value=3)) # any hashable object can be used as tag",
    " # extend the tree by one more level",
    "root[1].append(iTree('sub_item0',0.1))",
    "root[-1].append(iTree('sub_item0',4.1))",
    "root.render()",

    "",
    '# .. start: tutorial-code QS2',
    "",
    "# Target a child in the tree via absolute index:",
    "root[1]",
    "# Target a child in the tree via tag-idx-key:",
    "root[('item1',0)]",
    "item=root[('item1',1)] # given index is the tag-family index in this case",
    "item.idx # delivers absolute index of the item",
    "item.tag_idx # delivers tag-index-key of the item",
    "item.parent # delivers the parent object of the item",
    "# if you give just the family tag without index the whole tag-family is given as a list",
    "root['item1']",

    "",
    '# .. start: tutorial-code QS3',
    "",
    "# Standard iterator over the children:",
    "[i.value for i in root]",
    "# iteration over items (like in dicts):",
    "[i for i in root.items()]",
    "",
    '# .. start: tutorial-code QS4',
    "",
    "# Copy the iTree:",
    "new_tree=root.copy()",
    "# compare:",
    "new_tree==root",
    "# and see we have different objects:",
    "new_tree is root",
    "# and all sub-items are copied too:",
    "new_tree[0] is root[0]",
    "new_tree[1][0] is root[1][0]",
    "",
    '# .. start: tutorial-code QS5',
    "",
    "# To access items in-depth target_paths can be given as parameters to get()",
    "target_item=root.get(('item1',1),0) # target types can be mixed (e.g. tag-idx and absolute index)",
    "# Get method delivers flatten lists in case multiple items are targeted (even in higher levels)",
    "root.get('item1',0) # delivers all matches in deepest level!",
    "# other in-depth operation are found via .deep:"
    "# contains (target-item of first get operation):",
    "target_item in root # item is not a level 1 child!",
    "target_item in root.deep # but item is part of the tree (in-depth)",
    "# size:",
    "len(root)",
    "len(root.deep)",
    "# flatten iterators over all in-depth items:",
    "[i for i in root.deep] # up-down order",
    "[i for i in root.deep.tag_idx_paths(up_to_low=False)] # tag_idx related iterator; down-up order",

    "",
    '# .. start: tutorial-code QS6',
    "",
    " # save tree to file",
    "root.dump('dt.itz',overwrite=True) # returns the sha1 hash of the tree stored in the file",
    " # load tree from file",
    "loaded_tree=iTree().load('dt.itz')",
    "loaded_tree==root",

]

exec_and_print(tutorial_QS1, 'tutorial_QS1')

tutorial_0 = [
    '# .. start: tutorial-code 0',
    "",
    "root = iTree('root')",
    "root.append(iTree('a', value={'mykey': 1}, subtree=[iTree('a1'), iTree('a2')]))",
    "root.append(iTree('a', value={'mykey': 1}, subtree=[iTree('a1'), iTree('a2')]))",
    "root.get([0, 1], [0, 1])",
    "",

]

exec_and_print(tutorial_0, 'tutorial_0')

tutorial_1 = [
    '# ---> Tutorial 1:',
    "",
    "itree = iTree('root', 0, subtree=[iTree('one', 1, subtree=[iTree('sub', 10)]), "
    "iTree('one', 1.1), iTree('two', 2)])",
    "itree.render()",
    "dict(itree.items())  # considers just first level children",
    "dict(itree.deep.tag_idx_paths())  # delivers a flatten dict with key_paths as keys",
]

exec_and_print(tutorial_1)

tutorial_2 = [
    '# .. start: tutorial-code 2',
    "",
    "item1 = iTree('item1')  # itertree item with the tag 'item1'",
    "item2 = iTree('item2', 2)  # instance a iTree-object with value content integer 2",
    "item2b = iTree('item2', {'mykey': 2})  # instance a iTree-object with a dict as value content",
    "item3 = iTree()  # instance an iTree-object with the default tag (==NoTag) and no data content (==NoValue)",
    "root = iTree('root', subtree=[item1, item2, item2b, item3])",
    "root.render()",
    ""
]
exec_and_print(tutorial_2, 'tutorial_2')

tutorial_3 = [
    '# .. start: tutorial-code 3',
    "",
    "root = iTree('root')",
    "root.append(iTree('child'))  # append a child",
    "# The append operation delivers the appended object back",
    "root += iTree('child')  # alternative way to append a child",
    "root.append('value_content')  # append a child with implicit iTree(tag=NoTag,value='value_content')",
    "root.insert(1, iTree('child','inserted'))  # insert the item in the given target position (the insert is done in this target (index)",
    "# the old item with given target (index) will be moved in next position",
    "root.render()",
    "root[0] = iTree('newchild')  # replace the child with index 0",
    "root.render()",
    "del root[('newchild', 0)]  # deletes the child with key=('newchild',0) family-tag='newchild' and family-index=0",
    "root.render()",
    "del root[1]  # deletes the child with absolute index 1",
    "root.render()",
    "# The tag can be any hashable type!",
    "root.append(iTree(1))  # append a child with tag 1",
    "root.append(iTree((1, 2, 3)))  # append a child with tag (1,2,3)",
    "root.append(iTree((1, 2, 3), 1))  # append a child with tag (1,2,3) and data content 1",
    "root.render()",
    "new_itree = iTree()",
    "root.append(new_itree)",
    "root.append(new_itree)  # appending same object again will not work because parent is already set"
    "",
    '# .. start: tutorial-code 3b',
    "",
    "family=root[{(1,2,3)}] # target the family with a set(): {(1,2,3)}",
    "family # is represented as a list of the related items (with same tag)",
    "family=root.get.by_tag((1,2,3)) # target via the süecial tag access function",
    "family # is represented as a list of the related items (with same tag)",
    "",
    '# .. start: tutorial-code 3c',
    "",
    "root[0], root[1], root[2] = root[2], root[0], root[1]",
    "root[0:3] = root[2], root[0], root[1]",
    "root[2], root[0], root[1] = root[0:3]",

]
exec_and_print(tutorial_3)

tutorial_3_1 = [
    '# .. start: tutorial-code 3_1',
    "",
    "import copy",
    "itree = iTree('root',value={'a':[1,2,3]})",
    "copied_itree=itree.copy()",
    "iTree(itree.tag,value=copy.copy(itree.value)) # root only copy (subtree eliminated)",
    "copied_itree.value is itree.value",
    "copied_itree.value['a'] is itree.value['a']",
    ""
    "deepcopied_itree=itree.deepcopy() # Inner values objects will be copied too",
    "deepcopied_itree_extern=iTree(itree.tag,value=copy.deepcopy(itree.value)) ",
    "deepcopied_itree.value is itree.value",
    "deepcopied_itree.value['a'] is itree.value['a']",
    ""
    "itree_only_copy=itree.copy_keep_value() # values will be taken over without copy",
    "itree_only_copy_extern=iTree(itree.tag,value=itree.value) ",
    "itree_only_copy.value is itree.value",
    ""
]

exec_and_print(tutorial_3_1)

# tutorial_4a=[
#    "root = iTree('root')",
#    "root.append(iTree('a', value={'mykey': 1}, subtree=[iTree('a1'), iTree('a2')]))",
#    "root.append(iTree('b', subtree=[iTree('b1'), iTree('b2')]))",
#    "root.get([0,1],[0,1])",
#    ]
# exec_and_print(tutorial_4a)


tutorial_4 = [
    '# .. start: tutorial-code 4',
    "",

    "a = iTree('a', value={'mykey': 1}, subtree=[iTree('a1'), iTree('a2')])",
    "b = iTree('b', subtree=[iTree('b1'), iTree('b2')])",
    "itree = a + b",
    "repr(itree) # repr() is required to get the un-shorten representation of iTree (str() shortens the subtree-parameter)"
]
exec_and_print(tutorial_4, 'tutorial_4')

tutorial_5 = [
    '# .. start: tutorial-code 5',
    "",

    "itree_list = iTree('a') * 1000  # creates a list of 1000 copies of the original iTree",
    "itree_list[0]==itree_list[1] # items are equal",
    "itree_list[0] is itree_list[1] # but we have different instances",
    "root = iTree('root')",
    "root.extend(iTree('a') * 10000) # append all 10000 items as children to root",
    "len(root)",
]
exec_and_print(tutorial_5)

tutorial_6 = [
    '# .. start: tutorial-code 6',
    "",
    "itree1=iTree('one',1,[iTree(1.0),iTree(1.1),iTree(1.2)])",
    "itree2=iTree('two',1,[iTree(2.0),iTree(2.1),iTree(2.2)])",
    "itree_mul=itree1*itree2",
    "itree_mul.render()"
]
exec_and_print(tutorial_6, 'tutorial_6')

tutorial_7 = [
    '# .. start: tutorial-code 7',
    "",
    "itree1=iTree('one',1,[iTree('a',1.0),iTree('a',1.1),iTree('a','str')])",
    "itree1[0]-itree1[1] # same tage different value -> diff of value is calculated (if possible)",
    "itree1[0]-itree1[2] # same tage different value -> diff not possible minuend is kept",
    "sub_tree=itree1-itree1 # minus same object",
    "sub_tree.tag # tag eliminated",
    "sub_tree.value # value eliminated",
    "sub_tree.render() # subtree eliminated"

]
exec_and_print(tutorial_7)

tutorial_8_dot = [
    "root = iTree('root')",
    "root += iTree('child', value=0)",
    "root += iTree('child', value=1)",
    "root += iTree('child', value=2)",
    "root += iTree('child', value=3)",
    "root += iTree('child', value=4)",
    "root += iTree(1, value=5)",
    "root += iTree(('child',1), value='tag conflict')",
    "# any hashable object can be used as tag!",
    "root += iTree((1, 2, 3), value=6)  # any hashable object can be used as tag!",
]
exec_and_print(tutorial_8_dot, 'tutorial_8')

tutorial_8_1_dot = [
    "root = iTree('root')",
    "root += iTree('child', value=0)",
    "root += iTree('child', value=1)",
    "root += iTree('child', value=2)",
    "root += iTree('child', value=3)",
    "root += iTree('child', value=4)",
    "root += iTree(1, value=5)",
    "root += iTree(('child',1), value='tag conflict')",
    "# any hashable object can be used as tag!",
    "root += iTree((1, 2, 3), value=6)  # any hashable object can be used as tag!",
    "root[0].append(iTree('sub_child',value=0))",

]
exec_and_print(tutorial_8_1_dot, 'tutorial_8_1')

tutorial_8 = [
    '# .. start: tutorial-code 8',
    "",
    "root = iTree('root')",
    "root += iTree('child', value=0)",
    "root += iTree('child', value=1)",
    "root += iTree('child', value=2)",
    "root += iTree('child', value=3)",
    "root += iTree('child', value=4)",
    "root += iTree(1, value=5)",
    "root += iTree(('child',1), value='tag conflict')",
    "# any hashable object can be used as tag!",
    "root += iTree((1, 2, 3), value=6)  # any hashable object can be used as tag!",
    "root.render()",
    "",
    '# .. start: tutorial-code 8_1',
    "",
    "# Common index access:",
    "root[0] # absolute index access",
    "root[-1] # absolute index access (negative values)",
    "root[5] # This child is not targeted in the next step even that it's tag==1!",
    "root[1] # The absolute index access has higher priority than access via tags",
    "# Specific index access:",
    "root.get.by_idx(0) # absolute index access",
    "root.get.by_idx(-1) # absolute index access (negative values)",
    "root.get.by_idx(5) # This child is not targeted in the next step even that it's tag==1!",
    "root.get.by_idx(1) # The absolute index access has higher priority than access via tags",

    "",
    '# .. start: tutorial-code 8_2',
    "",
    "# Common index-slice access:",
    "root[1:3]",
    "# Specific index-slice access:",
    "root.get.by_idx_slice(slice(1,3))",
    "",
    '# .. start: tutorial-code 8_3',
    "",
    "# Common index-list access:",
    "root[[0, 2]]",
    "# same as:",
    "[root[0],root[2]]",
    "root[[2, 0, 2]]  # The target-order is kept (even multiple same items are kept)",
    "# Specific index-list access:",
    "root.get.by_idx_list([0, 2])",
    "",

    '# .. start: tutorial-code 8_4',
    "",
    "# Common tag-idx-key access (given as tuple) ",
    "# and how it must be used for targeting in other commands e.g. `insert()` or `move()`:",
    "root[('child', 0)]  ",
    "root['child', 0]  # lazy way to give the tag-idx-key",
    "root[('child', -1)]  # negative family-index, is supported too",
    "root[('child',1), 0] # This child is not targeted in the next step even that it's tag==('child',1)!",
    "root[('child', 1)] # The key access has higher priority than access via tags",
    "# Specific tag-idx access (must be given as tuple)",
    "root.get.by_tag_idx(('child', 0))  # Give the tuple; multiple parameters would target in-depth!",

    "",
    '# .. start: tutorial-code 8_5',
    "",
    "# Common tag-idx-slice access (given as tuple) ",
    "root[('child',slice(0,3,2))]",
    "root['child',slice(0,3,2)] # lazy input supported",
    "# Specific tag-idx-slice access (must be given as tuple)",
    "root.get.by_tag_idx_slice(('child',slice(0,3,2)))",
    "",
    '# .. start: tutorial-code 8_6',
    "",
    "# Common tag-idx-list access (given as tuple) ",
    "root[('child',[0,2])]",
    "root[('child',[0,2])] # lazy input supported",
    "# Specific tag-idx-list access (must be given as tuple)",
    "root.get.by_tag_idx_list(('child',[0,2]))",
    "",
    '# .. start: tutorial-code 8_7',
    "",
    "root['child'] # In case of no conflicts a given family tag delivers the family directly",
    "# specific tag-family access",
    "root.get.by_tag('child')",
    "root.get.by_tag(('child',1)) # target ('child',1) tag-family with root[('child',1)] the tag-idx is targeted!",
    "# The tag=('child',1) is a family tag not a tag-idx-key!",
    "root.get.by_tag(1) # target again an item which cannot be reached via root[1]",
    "root[{1}] # In case of conflicts the user can use a tag-set with one item too (slower as specific access)",
    "# The tag=1 is a family tag not an absolute index!",
    "",
    '# .. start: tutorial-code 8_7b',
    "",
    "root[{(1,2,3),1,('child',1)}] # order of tags in the set is kept in the result",
    "root[{1,('child',1),(1,2,3),}] ",
    # specific access allows to gives list of tags too:
    "root.get.by_tags([1,('child',1),(1,2,3),]) # here the order of th tags in the list is kept; duplicates will be delivered too",
    "",
    '# .. start: tutorial-code 8_8',
    "",
    "# The following EXCEPTION is expected:",
    "root[lambda i: i.value%2==0] # filters all children which contains an even value, but we have an exception:",
    "root[lambda i: type(i.value) is int and i.value%2==0] # ensure that the filter-calculation matches to any child!",
    "root[(lambda i: i.value==2)] # This filter targets in our case one value only",
    "root.get.by_level_filter(lambda i: type(i.value) is int and i.value%2==0) # ensure that the filter-calculation matches to any child!",
    "root.get.by_level_filter(lambda i: i.value==2) # This filter targets in our case one value only",
    "",
    '# .. start: tutorial-code 8_9',
    "",
    "root[iter] # give build in iter to target all children",
    "list(root) # is the recommended equivalent function for this but here we need must create the list explicit from the iterator",
    "root[(lambda i: True)] # Delivers also the same result but is much slower",
    "",
    '# .. start: tutorial-code 8_10',
    "",
    "# Here we target absolute index, absolute index, tag-idx-key,family-set,filter",
    "root[[0,1,('child', 1),{1},lambda i: type(i.value) is int and i.value>4]] # in result the iTree children order is kept and duplicates are deleted",
    "root[[{1},('child', 1),lambda i: type(i.value) is int and i.value>4,0,1]] # same targets in other order delivers same result",
    "",
    '# .. start: tutorial-code 8_11',
    ""
    "root['child',slice(1,1)] # slice delivers no match",
    "root[{'child2'}] # invalid tag",
    "root[100] #  Index access out of range"
    "root['child',100] # family index out of range",
    "root[('child',100,1)] # Invalid family tag",
    "root[lambda i: i.value>2] # invalid calculation for child with value 'tag conflict'",
    "",
    '# .. start: tutorial-code 8_12',
    "",
    "root[0].append(iTree('sub_child',value=0)) # prepare one level deeper item",
    "",
    '# .. start: tutorial-code 8_13',
    "",
    "root[0][0] # access nested (deeper) items",
    "root['child'][0] # If the result of first operation is not a single item this will deliver the first item in the result-list",
    "# See that the result is in the first and not in the second level of the iTree!!",

    "",
    '# .. start: tutorial-code 8_14',
    "",
    "root.get(0,0)",
    "root.get(0,('sub_child',0))  # access nested (deeper) items via target-path-list (mixed target types)",
    "target_path=[0,0]",
    "root.get(*target_path) # targets deep",
    "root.get(*[0,0]) # targets deep -> single item arguments given will deliver single item only",
    "# be CAREFUL because:",
    "root.get(*[0,0]) # gives empty list because target single item has no subtree (type cast to list)",
    "root.get(target_path) #target first level only (absolute index-list given)",
    "root.get([0,0]) #target first level only (absolute index-list given)",
    "",
    '# .. start: tutorial-code 8_15',
    "",
    "root.get(lambda i: i.value==0,lambda i: i.value==0) # level filtering",
]
exec_and_print(tutorial_8)

tutorial_9_1 = [
    "",
    '# .. start: tutorial-code 9_1',
    "",
    "root = iTree('root', subtree=[iTree('child', 0), iTree((1, 2), 'tuple_child0'), iTree('child', 1), "
    "iTree('child', 2),iTree((1, 2), 'tuple_child1')])",
    "root[0] += iTree('subchild')",
    "root.render()",
    "root[0][0].root",
    "root[0][0].idx",
    "root[0][0].tag_idx",
    "root[0][0].idx_path",
    "root[0][0].tag_idx_path",
    "root[1].value",
    "root[1].tag_idx",
    "root[-1].value",
    "root[-1].tag_idx",
    "len(root) #  level 1 only",
    "len(root.deep) # all in-depth items",
    "root2=root.copy()",
    "root2[-1].append(iTree('subitem')) # we append one item in depth",
    "root2>root # level 1 only size-compare",
    "root2.deep>root.deep # all items size-compare",

]
exec_and_print(tutorial_9_1, 'tutorial_9_1')

a = Data.iTInt8Model()

tutorial_12 = [
    "",
    '# .. start: tutorial-code 12',
    "",
    "my_tree = iTree('root')",
    "my_tree.set_value(1)",
    "repr(my_tree.get_value())",
    "my_tree.set_value(Data.iTInt8Model())  # store a model limiting the matching values",
    "my_tree.set_value(1)  # store the value in the model",
    "repr(my_tree.value)  # delivers the whole object stored in value",
    "repr(my_tree.get_value())  # again we take the value out of the model",
    "my_tree.set_value(1024)  # value out of the valid range",
    "repr(my_tree.del_value())  # delete the model",
    "my_tree.value",
]
exec_and_print(tutorial_12)

tutorial_13 = [
    "",
    '# .. start: tutorial-code 13_1',
    "",
    "# create a small nested iTree:",
    "root = iTree('root', subtree=[iTree('one', 1, subtree=[iTree('subone', 1.1), "
    "iTree('subtwo', 1.2)]), iTree('two', 2), iTree('three', 3)])",
    "list(root)  # __iter__()",
    "list(root)",
    "list(root.values())",
    "list(root.tag_idxs())",
    "list(root.items())",
    "list(root.items(values_only=True))",
    "",
    '# .. start: tutorial-code 13_2',
    "",
    "# deep iterators:",
    "list(root.deep)  # deep counterpart of level1 __iter__() iterator",
    "list(root.deep.iter(up_to_low=False))  # changed iteration order bottom-> up",
    "list(root.deep.tag_idx_paths()) # deep counterpart of level1 items() iterator",
    "[(k,i.value) for k,i in root.deep.tag_idx_paths()]  # deep counterpart of level1 items(values_only=True) iterator",
    "[k for k,_ in root.deep.tag_idx_paths()]  # deep counterpart level1 to keys() iterator",
    "[k for k,_ in root.deep.idx_paths()]  # no level 1 counterpart (lists are automatically indexed 0->n)"
]
exec_and_print(tutorial_13)

tutorial_14 = [
    "",
    '# .. start: tutorial-code 14',
    "",

    "root = iTree('root', subtree=[iTree('one', 1, subtree=[iTree('subone', 1.1), "
    "iTree('subtwo', 1.2)]), iTree('two', 2), iTree('three', 3)])",
    "filter1 = lambda i: 'one' not in i.tag",
    "list(root.deep.tag_idx_paths(filter1))",
    "# the hierarchical filter did not consider the item iTree('subtwo',1.2) because parent is filtered out",
    "list(filter(lambda i: 'one' not in i[1].tag, root.deep.tag_idx_paths())) # for non-hierachical filtering use build-in",
    "# now the sub-items are considered even that parent did not match",
    "",
    '# .. start: tutorial-code 14_2',
    "",
    "# based on the root object we had in last example",
    "filter_a = lambda i: 'one' in i.tag  # This will filter for the first two elements",
    "filter_b = lambda i: i.value == 1.2  # First element doesn't have this level (no match)",
    "root.get(*[filter_a, filter_b]) # level filtering level=0~filter_a; level=1~filter_b"

]
exec_and_print(tutorial_14)

tutorial_15 = [
    "",
    '# .. start: tutorial-code 15',
    "",
    "root = iTree('root', subtree=[iTree(value=0), iTree(value=1), iTree(value=2)])",
    "filter1 = lambda i: i.value != 1",
    "root[{NoTag}]",
    "list(filter(filter1, root[{NoTag}]))",
]
exec_and_print(tutorial_15)

tutorial_15b = [
    "",
    '# .. start: tutorial-code 15_2',
    "",
    "import itertree.itree_serializer.itree_json_converter import Converter_1_1_1_to_2_0_0",
    "new_itree=Converter_1_1_1_to_2_0_0(old_source_file_path)",
    "# Exception can be ignored"
]
exec_and_print(tutorial_15b)

tutorial_16 = [
    "",
    '# .. start: tutorial-code 16_1',
    "",
    "# We create a small iTree:",
    "root = iTree('root')",
    "root += iTree('A')",
    "root += iTree('B')",
    "B = iTree('B')",
    "B += iTree('Ba')",
    "# we create multiple 'Bb' elements to show how the placeholders are used during save and load",
    "B += iTree('Bb')",
    "B += iTree('Bb')",
    "B += iTree('Bc')",
    "root += B",
    "# !! Now we create a internal link (but we disable the loading (no flag set))):",
    "# (internal link -> iTLink(file_path==None,target_path= item identification) (target_path like in get_deep())",
    "linked_element = iTree('internal_link', link=iTLink(target_path=[('B', 1)]))",
    "root.append(linked_element)",
    "root.render()",
    "root.load_links() # now we load the linked items",
    "root.render()  # The tree renderer marks linked items with \">>\"",

    "",
    '# .. start: tutorial-code 16_2',
    "",
    "root['B', 1] += iTree('B_post_append')",
    "root.render()",
    "root.load_links()  # The returning True signalizes that the tree was reloaded",
    "root.render()",
    "root.load_links()  # If we repeat the action the command detects that the tree is  unchanged and no update is needed",
    "root.load_links(force=True)  # Anyway the update can be forced",

    "",
    '# .. start: tutorial-code 16_3',
    "",

    "intern_link_item = root['internal_link', 0]  # get the linked item",
    "intern_link_item.append('new')  # append a local item",
    "local = intern_link_item[2].make_local()  # make a linked item local (cover the item with a local one)",
    "local.append(iTree('sublocal'))  # we change the subtree of the local item",
    "local.set_value('myvalue')  # we change the value of the local item",
    "root.render()  # see that in the linked tree we have local elements (linked items are marked with \">>\")",

    "",
    '# .. start: tutorial-code 16_4',
    "",
    "del intern_link_item[('Bb', 1)]",
    "print(root.render())",

]
exec_and_print(tutorial_16, 'tutorial_16')

tutorial_17 = [
    "",
    '# .. start: tutorial-code 17',
    "",
    "root = iTree('root',subtree=[iTree('one', 1, "
    "subtree=[iTree('subone', 1.1), iTree('subtwo', 1.2)]), iTree('two', 2), iTree('three', 3)])",
    "list(root)",
    "list(root.deep)  # flatten deep item list",
    "dict(root.items())",
    "{k:i for k,i in root.deep.tag_idx_paths()}  # flatten deep items dict"
]
exec_and_print(tutorial_17)

tutorial_18 = [
    "",
    '# .. start: tutorial-code 18',
    "",
    "root = iTree('root', subtree=[iTree('one', 1, subtree=[iTree('subone', 1.1), iTree('subtwo', 1.2)]), "
    "iTree('two', 2), iTree('three', 3)])",
    "list(root.values())  # targets only first level children deeper hierarchy is lost",
    "[i.value for i in root.deep]  # flatten iterator delivering in-depth values of items",
    "dict(root.items(values_only=True))  # targets only first level children deeper hierarchy is lost",
    "{k:i.value for k,i in root.deep.tag_idx_paths()}  # in-depth levels are flatten in the iterator"
]
exec_and_print(tutorial_18)

tutorial_19 = [
    "",
    '# .. start: tutorial-code 19',
    "",
    "root = iTree('root', subtree=[iTree('one', 1, subtree=[iTree('subone', 1.1), iTree('subtwo', 1.2)]), "
    "iTree('two', 2), iTree('two', 2.2),iTree('three', 3)])",
    "root['one'] # targets the family and will deliver a list which contains in this case only one item",
    "root.get.single('one')  # targets the same family but because we have just one value the item inside the list is delivered directly",
    "root.get.single('two')  # will raise an exception because we do not have a unique result",
    "root.get('one', 'subone')  # targets in-depth and delivers the resulting list",
    "root.get.single('one', 'subone')  # Same method exists in get sub-class too",
    "",
    '# .. start: tutorial-code 19_2',
    "",

    "root['two']  # family 'two' contains two items:",
    "root['two', 0].idx  # index of first item in 'two' family",
    "root['two']=(iTree('two', 'new')) # replace the two items in the family 'two'",
    "root.get.single('two')  # Now we get the unique item in this family",
    "root.get.single('two').idx  # Index is same as before!",
    "root['two']=iTree('two', 'new2')  # replace again",
    "root.get.single('two')",
    "root.get.single('two').idx  # Index is same as before!",
    "root[...]=iTree('two', 'new3')  # replace and add at the end",
    "root.get.single('two')",
    "root.get.single('two').idx  # Index is now last index",

]
exec_and_print(tutorial_19)

tutorial_20 = [
    "",
    '# .. start: tutorial-code 20',
    "",
    "root = iTree('root') ",
    "for i in range(2):\n"
    "    item=root.append(iTree('%i'%i, i))\n"
    "    for ii in range(2):\n"
    "        subitem = item.append(iTree('%i_%i' % (i,ii), i*10+ii))\n"
    "        for iii in range(2):\n"
    "            subitem.append(iTree('%i_%i_%i' % (i, ii,iii), i * 100 + ii*10+iii))",
    "[i for i in root.deep.iter(up_to_low=True)][0:5] # show just a part",
    "[i for i in root.deep.iter(up_to_low=False)][0:5] # show just a part",
]
exec_and_print(tutorial_20, 'tutorial_20')

index_1 = ["root=iTree('root','xyz',subtree=[iTree('subitem','abc'),iTree(('tuple','tag'),{'dict':'value'},"
           "subtree=[iTree('subtag',1),iTree('subtag',2)]),iTree('tag',[1,2,3])])",
           "root.render()"

           ]
exec_and_print(index_1)

index_2 = [
    "",
    '# .. start: index-code 1',
    "",
    "from itertree import * # required for all examples shown in the documentation",
    "# Create root item:",
    "root = iTree('root', value={'mykey': 0})",
    "# Append children:",
    "root.append(iTree('sub', value={'mykey': 1}))",
    "root.append(iTree('sub', value={'mykey': 2}))",
    "root.append(iTree('sub', value={'mykey': 3}))",
    "# Show tree content:",
    "root.render()",
    "# Address item via tag-index-pair (key):",
    "root['sub', 1]",
    "# Address item via absolute-index and check stored value:",
    "root[1].value"
    "",
]
exec_and_print(index_2)

index_3 = [
    "",
    '# .. start: index-code 2',
    "",
    "root = iTree('root')  # first we create a root element (parent)",
    "root.append(iTree(tag='child', value=0))  # add a child append method",
    "root.append(iTree((1, 2, 3), 1))  # add next child (the given tag is tuple, any hashable object can be used as tag)",
    "root += iTree(tag='child2', value=2)  # next child could be added via += operator too",
    "root.render()  # show the created tree",
    "",
    '# .. start: index-code 2_1',
    "",
    "root.append(iTree('child', 5))",
    "root.append(iTree('child', 6))",
    "root.render()",
    "",
    '# .. start: index-code 2_2',
    "",
    "print(root['child', 1])  # target via key -> tag_idx pair",
    "print(root[3])  # target via absolute index",
    "",
    '# .. start: index-code 2_3',
    "",
    "root[0].append(iTree('subchild'))",
    "print(root[0][0])",
    "",
    '# .. start: index-code 2_4',
    "",
    "a = [i for i in root]",
    "len(a)",
    "print(a)",
    "b = list(root.deep)  # The list is build by iterating over all nested children",
    "len(b)  # The item: root[0][0] is considered in this iteration too",
    "print(b)",
    "",
    '# .. start: index-code 2_5',
    "",
    "print(root['child', 1])  # target via key -> tag_idx pair",
    "print(root[3])  # target via absolute index",
    "",
    '# .. start: index-code 2_6',
    "",
    "root[0].append(iTree('subchild'))",
    "print(root[0][0])",

    "",
    '# .. start: index-code 2_7',
    "",
    "# ----> filtering method can be placed that targets specific properties of the items.",
    "a = [i for i in root.deep.iter(filter_method=lambda i: type(i.value) is int and i.value % 2 == 0)]  # search even data items",
    "print(a)",
    "",
    '# .. start: index-code 2_8',
    "",
    "root.dump('dt.itz',overwrite=True)  # itz is the recommended file ending for the zipped dataset file",
    "root2 = iTree().load('dt.itz')  # loading a iTree from a file",
    "print(root2 == root)",
    "root += iTree('link', link=iTLink('dt.itz',"
    "[('child', 0)]))  # The node item will integrate the children of the linked item.",
    "",
    '# .. start: index-code 2_9',
    "",
    "myresultlist = list(root.deep)  # this is quick even for huge number of items",
    "first_item = list(root.deep)[0]  # but this is slower (list-type-cast)  as:",
    "first_item = next(iter(root.deep)) # create an iterator from the generator object",
    "fifth_item = list(root.deep)[4]  # and this is slower as:",
    "import itertools",
    "fifth_item = next(itertools.islice(root.deep, 4, None))",
    "",

]
exec_and_print(index_3)

index_4 = [
    "",
    '# .. start: index-code 3',
    "",

    "empty_item = iTree()",
    "print(empty_item)",
    "print(empty_item.tag)",
    "print(empty_item.value)"
    "",
]
exec_and_print(index_4)
