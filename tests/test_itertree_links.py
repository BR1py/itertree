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


This test suite focuses on the linking and "covering mechanisms" available in iTree
"""
import os
import sys
import collections
import timeit
import itertools
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

print('Test start: itertree linked items test')


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
    for i in range(number):
        t = timeit.timeit(check_method, number=1)
        if t < min_time:
            min_time = t
    return min_time

def large_itree(number_per_level,tags=[],counter_var=None,_root=None,_count=0):
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
                sub_item,cnt=large_itree(sub,tags,counter_var,sub_item,cnt)
            root.append(sub_item)
    return root,cnt



class Test_iTree_linked_items:

    def test_internal_links_creation_and_not_loaded_behavior(self):

        print('\nRUN TEST: Test not loaded internal link and allowed operations')

        root = iTree('root', subtree=[iTree('A'), iTree('B'),
                                      iTree('B', subtree=[iTree('Ba'), iTree('Bb'), iTree('Bb'), iTree('Bc')]),
                                      iTree('internal_link', link=iTLink(None, [('B', 1)]))])

        #check properties
        assert not root.is_link_loaded
        link_root_item=root[-1]
        assert not link_root_item.is_link_loaded
        assert link_root_item.is_link_root
        assert not link_root_item.is_linked

        #we excute the next operation and we do not expect any exceptions!
        link_root_item.append(iTree('test'))
        link_root_item+=iTree('test')
        link_root_item.insert(0,iTree('test'))
        link_root_item.appendleft(iTree('test'))
        link_root_item[0].rename('new_name')
        link_root_item[0].move(-1)
        link_root_item.extend([iTree(),iTree()])
        link_root_item.extendleft([iTree(), iTree()])
        link_root_item[0].rename('new_name2')
        link_root_item.reverse()
        link_root_item.deep.reverse()
        link_root_item.rotate()
        link_root_item.rotate(2)
        link_root_item.rotate(-3)
        link_root_item.sort()
        link_root_item.deep.sort()
        del link_root_item[2]
        link_root_item.pop(1)
        link_root_item.remove(filter(lambda i: i.tag == NoTag, link_root_item))
        with pytest.raises(SyntaxError):
            link_root_item[2].make_local()

        print('\nRESULT OF TEST: Test not loaded internal link and allowed operations -> PASS')

    def test_internal_links_creation_and_after_loaded_behavior(self):

        print('\nRUN TEST: Test loaded internal link and allowed afterwards operations')

        root = iTree('root', subtree=[iTree('A'), iTree('B'),
                                      iTree('B', subtree=[iTree('Ba'), iTree('Bb'), iTree('Bb'), iTree('Bc')]),
                                      iTree('internal_link', link=iTLink(None, [('B', 1)]))])

        assert root.load_links()
        #check properties
        assert root.is_link_loaded
        link_root_item=root[-1]
        assert link_root_item.is_link_loaded
        assert link_root_item.is_link_root
        assert not link_root_item.is_linked
        assert len(link_root_item) == len(root.get(*[('B', 1)]))
        assert link_root_item._link.tags=={i.tag for i in root.get(*[('B', 1)])}
        for i in link_root_item:
            assert i.is_linked
            assert not i.is_link_loaded
            assert not i.is_link_root
            assert not i.link_root is link_root_item
            assert root.get(*[('B', 1), i.tag_idx]) == i
            assert root.get(*[('B', 1), i.tag_idx]) is not i

        #we excute the next operation and we do not expect any exceptions!
        # append is allowed in all variations
        a=len(link_root_item)
        link_root_item.append(iTree('test')) #new tag
        local_with_link_tag=link_root_item.append(iTree('Bb')) # linked tag the item is required for later tests!
        link_root_item.append(iTree())  # empty tag (tag=NoTag)
        link_root_item.append('myvalue') # implicit definition (tag=NoTag)
        # append via __iadd__()
        link_root_item+=iTree('test')
        link_root_item += iTree('Bb')
        link_root_item+=iTree()

        # appendleft allowed operations
        link_root_item.appendleft(iTree('test_appendleft'))  # unlinked new tag
        link_root_item.appendleft(iTree('test')) # unlinked tag
        link_root_item.appendleft(iTree())  # unlinked tag==NoTag
        link_root_item.appendleft('appendleft_value')  # unlinked tag==Notag (implicit definition)
        # appendleft blocked operations
        with pytest.raises(PermissionError):
            link_root_item.appendleft(iTree('Ba'))  # linked tag

        # insert allowed operations
        link_root_item.insert(1, iTree('test_insert'))  # unlinked new tag
        link_root_item.insert(1, iTree('test'))  # unlinked tag
        link_root_item.insert(1, iTree())  # unlinked tag==NoTag
        link_root_item.insert(1, 'insert_value')  # unlinked tag==Notag (implicit definition)
        linked_item_idx=next(itertools.dropwhile(lambda i: not i.is_linked, link_root_item)).idx
        link_root_item.insert(linked_item_idx, iTree())  # targeting a linked item
        # insert blocked operations
        with pytest.raises(PermissionError):
            link_root_item.insert(1,iTree('Ba'))  # linked tag

        #rename
        link_root_item[0].rename('new_name') # rename a not linked item with no linked tag
        local_with_link_tag.rename('new_name')  # rename a not linked item with no linked tag
        # we must recreate the local_with_link for following tests:
        local_with_link_tag = link_root_item.append(iTree('Bb'))  # linked tag the item is required for later tests!
        # rename blocked operations
        with pytest.raises(PermissionError):
            link_root_item[0].rename('Ba')  # rename a not linked item with linked tag
        linked_item_idx = next(itertools.dropwhile(lambda i: not i.is_linked, link_root_item)).idx
        with pytest.raises(PermissionError):
            link_root_item[linked_item_idx].rename('new_name')  # rename a linked item

        # move
        link_root_item[0].move(-2) # move local
        linked_item_idx = next(itertools.dropwhile(lambda i: not i.is_linked, link_root_item)).idx
        with pytest.raises(PermissionError): # move linked
            link_root_item[linked_item_idx].move(-2)  # move a linked item
        with pytest.raises(PermissionError):
            local_with_link_tag.move(-2) #  move a local with linked item tag

        # extend should work without limitation
        link_root_item.extend([iTree(), iTree('extend_name'),iTree('Bb'),iTree('Ba')]) # all kinds of tags used here

        # extendleft like appenmdleft but a precheck is required and we must recheck if in case one extended
        # item was wrong no item is extended
        link_root_item.extendleft([iTree(), iTree('extendleft_name')])
        with pytest.raises(PermissionError): # extend left a linked tag
            link_root_item.extendleft([iTree(value='extend_left'), iTree('Bb')])
        assert link_root_item[0].value != 'extend_left'

        # not allowed operations:
        with pytest.raises(PermissionError):
            link_root_item.reverse()
        with pytest.raises(PermissionError):
            link_root_item.deep.reverse()
        with pytest.raises(PermissionError):
            link_root_item.rotate()
        with pytest.raises(PermissionError):
            link_root_item.rotate(2)
        with pytest.raises(PermissionError):
            link_root_item.rotate(-3)
        with pytest.raises(PermissionError):
            link_root_item.sort()
        with pytest.raises(PermissionError):
            link_root_item.deep.sort()

        # __del__()
        del link_root_item[2]
        linked_item_idx = next(itertools.dropwhile(lambda i: not i.is_linked, link_root_item)).idx
        with pytest.raises(PermissionError):
            del link_root_item[linked_item_idx]
        with pytest.raises(PermissionError):
            del link_root_item['Bb'] # family contains links!
        with pytest.raises(PermissionError):
            del link_root_item[lambda i: i.tag=='Bb']  # Filter result contains links
        del link_root_item[NoTag]  # family contains no links
        # we do not test pop() here because it uses internally __del__()

        # we check a corner case for remove:
        link_root_item.remove(filter(lambda i: i.tag in {'extend_name','extendleft_name'} ,link_root_item))
        with pytest.raises(PermissionError):
            link_root_item.remove(filter(lambda i: i.tag == 'Bb' ,link_root_item))

        print('\nRESULT OF TEST: Test loaded internal link and allowed afterwards operations ->')


    def test_internal_links_creation_on_complex_local_structure(self):

        print('\nRUN TEST: Test loaded internal link over complex local structure')
        root = iTree('root', subtree=[iTree('A'), iTree('B'),
                                      iTree('B', subtree=[iTree('Ba'), iTree('Bb',0), iTree('Bb',1), iTree('Bc')]),
                                      iTree('internal_link', link=iTLink(None, [('B', 1)]))])

        link_root_item=root[-1]

        # we add them items with different tags and check how the items are integrated after we load the links
        # some should be reordered
        link_root_item.append(iTree(value=0))
        link_root_item.append(iTree('Bc'))
        link_root_item.append(iTree('Bb2'))
        Bb=link_root_item.append(iTree('Bb'))
        Bb.append('sub_item_value')
        link_root_item.append(iTree('Ba'))
        link_root_item.append(iTree(value=1))

        root.load_links()

        #expected=[('Ba',NoValue),('Bb',NoValue),('Bb',1),('Bc',NoValue),(NoTag,0),('Bb2',NoValue),(NoTag,1)]
        expected = [('Ba', NoValue), ('Bb2', NoValue),('Bb', NoValue), ('Bb', 1),(NoTag, 0),
                    ('Bc', NoValue),
                    (NoTag, 1)]
        for i,item in enumerate(link_root_item):
            assert item.tag==expected[i][0]
            assert item.value == expected[i][1]
            if i ==3:
                assert item.is_linked
            else:
                assert not item.is_linked
            if i in {0,2,5}:
                assert item._link._link_item.tag==item.tag
            else:
                assert not hasattr(item,'_link')

        # finally we insert a new item in the source and we see if reordering is made correctly
        root[2].insert(-1,iTree('Bb2'))

        # reload of subtrees has no effect
        root[2].load_links()
        assert link_root_item[1].tag=='Bb2'
        link_root_item[0].load_links()
        assert link_root_item[1].tag == 'Bb2'

        # full reload
        #root.render()
        root.load_links()
        #root.render()
        expected = [('Ba', NoValue), ('Bb', NoValue), ('Bb', 1),  ('Bb2', NoValue), (NoTag, 0),('Bc', NoValue),
                    (NoTag, 1)]
        for i, item in enumerate(link_root_item):
            assert item.tag == expected[i][0]
            assert item.value == expected[i][1]

        # delete some items
        del link_root_item[('Bc',0)]
        assert link_root_item[('Bc',0)].tag=='Bc'
        link_root_item.insert(0, iTree(tag='first_item'))

        link_root_item.insert(('Bc',0),iTree('afterwards we need placeholder'))
        # Now we check for all placeholders
        # we expect the place holder for the 'Bc' item
        dump_str=root.dumps()
        root2=iTree().loads(dump_str,load_links=False)
        assert root2!=root # links not yet loaded
        link_item2=root2[-1]
        for i,item in enumerate(link_item2):
            if i==3 or i==7:
                assert item.is_placeholder
            else:
                assert not item.is_placeholder
        root2.load_links()
        assert root==root2

        print('\nRESULT TEST: Test loaded internal link over complex local structure -> PASS')

    def test_internal_links_creation_detect_circular_definitions(self):

        print('\nRUN TEST: Test internal links circular detection')

        root = iTree('root', subtree=[iTree('A',subtree=[iTree('Aa'), iTree('Ab', 0), iTree('Ab', 1), iTree('Ac')]),
                                      iTree('B'),
                                      iTree('B', subtree=[iTree('Ba'), iTree('Bb', 0), iTree('Bb', 1), iTree('Bc')]),
                                      iTree('C', subtree=[iTree('internal_link', link=iTLink(None, [('B', 1)]))])
                                      ]
                     )

        # add a non circular link
        root[2].append(iTree('internal_link1', link=iTLink(None, [('A', 0)])))
        # we do not expect an exception here
        root.load_links()
        #root.render()
        assert len(root.deep) == 27
        root[2].append(iTree('internal_link2', link=iTLink(None, [('C', 0)]))) # circular link
        #root.render()
        def detect_recursion(root):
            with pytest.raises(RecursionError):
                root.load_links()

        print('Exec time to detect a circular definition: {:.3e} s'.format(calc_timeit(lambda:detect_recursion,4 )))

        print('\nRESULT TEST: Test internal links circular detection -> PASS')

    def test_order_locals_correctly(self):

        print('\nRUN TEST: Test order locals correctly after reload')
        root = iTree('root', subtree=[iTree('A'), iTree('B'),
                                      iTree('B', subtree=[iTree('Ba'), iTree('Bb',0), iTree('Bb',1), iTree('Bc')]),
                                      iTree('internal_link', link=iTLink(None, [('B', 1)]))])

        #create locals
        link_locals=[]
        link_item=root[-1]
        link_item.append(iTree('Ba before',0))
        link_item.append(iTree('Ba before',1))
        link_locals.append(link_item.append(iTree('Ba',2)))
        link_item.append(iTree('Bb0 before',3))
        link_item.append(iTree('Bb0 before',4))
        link_locals.append(link_item.append(iTree('Bb',5)))
        link_item.append(iTree('Bb1 before',6))
        link_item.append(iTree('Bb1 before',7))
        link_locals.append(link_item.append(iTree('Bb',8)))
        link_item.append(iTree('Bc before',9))
        link_item.append(iTree('Bc before',10))
        link_locals.append(link_item.append(iTree('Bc',11)))
        link_item.append(iTree('after',12))
        link_item.append(iTree('after',13))

        root.load_links()

        assert link_locals==list(filter(lambda i: i.is_link_cover,link_item))
        assert list(link_item.values())==list(range(14))

        # delete the covering items:
        a=link_locals
        keys=[]
        for item in list(link_locals):
            key=item.tag_idx
            keys.append(key)
            del link_item[key]

        for key in keys:
            assert link_item[key].is_linked
            assert not link_item[key].is_link_cover

        root_data_path = get_tmp_path()

        target_path = root_data_path + '/out.itr'
        root.dump(target_path,pack=False,overwrite=True)

        root2=iTree().load(target_path,load_links=False)

        link_item2=root2[-1]

        for key in keys:
            item=link_item2[key]
            assert item.is_placeholder

        root2.load_links()


        for i,item in enumerate(link_item2):
            key=item.tag_idx
            if key in keys:
                assert item.is_linked
                assert not item.is_placeholder
            else:
                assert i==item.value

        assert root2==root

        root2[2][-1].move(1)

        root2.load_links()

        #recheck that the reordering took place:

        start_idx=link_item2[('Ba',0)].idx
        assert link_item2[start_idx+1].tag_idx == ('Bc before', 0)
        assert link_item2[start_idx+2].tag_idx == ('Bc before', 1)
        assert link_item2[start_idx+3].tag_idx == ('Bc', 0)
        assert link_item2[start_idx+4].tag_idx == ('Bb0 before', 0)


        print('\nRESULT TEST: Test order locals correctly after reload -> PASS')
