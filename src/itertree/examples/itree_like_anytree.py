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
"""

# This example shows how the tree related functions from anytree can be realized in itertree
# we show here two ways
# 1. use replacement functions for itertree
# 2. Create a new class NodeIT() with super class iTree and integrate the missing functions

from anytree import Node # example works only if anytree package is available
from anytree.iterators import PreOrderIter,PostOrderIter,LevelOrderIter
from itertree import *
from itertree.itree_indepth import _iTreeIndepthTree
from itertools import chain

# build a trees with some levels for the functional tests

# anytree
root_at=Node('root')
[Node('%i'%i ,parent=root_at) for i in range(10)]
for n in root_at.children:
    [Node('%s_%i'%(n.name,i) ,parent=n)  for i in range(10)]
for n in root_at.children:
    skip_first=False
    for n2 in n.children:
        tmp=[Node('%s_%i' %(n2.name,i), parent=n2) for i in range(10)]
        deep_item_at=tmp[-1]

# itertree
root_it=iTree('root')
[root_it.append(iTree('%i'%i)) for i in range(10)]
for n in root_it:
    b=[n.append(iTree('%s_%i' % (n.tag,i))) for i in range(10)]
    for n2 in b:
        [n2.append(iTree('%s_%i' % (n2.tag,i))) for i in range(10)]
deep_item_it=n2[-1]

# overload iTree with a new class containing the missing functions:

class NodeITDeep(_iTreeIndepthTree):

    def preorder(self):
        return self.iter(add_self=True)

    def postorder(self):
        return self.iter(up_to_low=False,add_self=True)

    def levelorder(self):
        return self.iter_levels(start_levels=0)


class NodeIT(iTree):

    @property
    def children(self):
        return tuple(self)

    @property
    def name(self):
        # depending on what you expected here you may use instead
        # return self.tag_idx
        return self.tag

    @property
    def leaves(self):
        return self.deep.iter_siblings(-1)

    @property
    def is_leave(self):
        return len(self)==0

    @property
    def descendants(self):
        return self.deep

    @property
    def deep(self):
        """
        Subclass containing the deep access to the nested structures of iTree
        :return:
        """
        try:
            return self._hc_tree
        except AttributeError:
            # The subclass is only instanced if it is first used
            tree, tree._itree, tree.get = NodeITDeep(), self, self.get
            self._hc_tree = tree
            return tree

    def __repr__(self):
        # this is a very lazy way to over load the method
        return super().__repr__().replace('iTree','NodeIT')

    def __str__(self):
        # this is a very lazy way to over load the method
        return super().__str__().replace('iTree','NodeIT')

# build a tree with the new class
root_it2=NodeIT('root')
[root_it2.append(NodeIT('%i'%i)) for i in range(10)]
for n in root_it2:
    b=[n.append(NodeIT('%s_%i' % (n.tag,i))) for i in range(10)]
    for n2 in b:
        [n2.append(NodeIT('%s_%i' %(n2.tag, i))) for i in range(10)]
deep_item_it2=n2[-1]


#children
print('Get children names/tags')
result_at=[n.name for n in root_at.children]
result_it=[n.tag for n in root_it]
result_it2=[n.name for n in root_it2.children]

print('anytree (root_at.children):\n',repr(result_at))
print('itertree (root_it.__iter__()):\n',repr(result_it))
print('itertree_node (root_it2.children):\n',repr(result_it2))
assert len(result_at)==len(result_it), '%i!=%i'%(len(result_at),len(result_it))
assert len(result_at)==len(result_it2), '%i!=%i'%(len(result_at),len(result_it2))

#anchestors
print('Get ancestors')
result_at=[n.name for n in deep_item_at.ancestors]
result_it=[]
p=deep_item_it
while p!=root_it:
    p=p.parent
    result_it.append(p.tag)
result_it.reverse()
result_it2=[n.name for n in deep_item_it2.ancestors]

print('anytree (deep_item_at.ancestors):\n',repr(result_at))
print('itertree (replacement function):\n',repr(result_it))
print('itertree_node (deep_item_at.ancestors):\n',repr(result_it2))
assert len(result_at)==len(result_it), '%i!=%i'%(len(result_at),len(result_it))
assert len(result_at)==len(result_it2), '%i!=%i'%(len(result_at),len(result_it2))

#siblings
print('Get siblings')
result_at=[n.name for n in deep_item_at.siblings]
result_it=[n.tag for n in deep_item_it.parent if  n is not deep_item_it]
result_it2=[n.name for n in deep_item_it2.siblings]

print('anytree (root_at.decendants):\n',repr(result_at))
print('itertree (root_it.__iter__()):\n',repr(result_it))
print('itertree_node (root_it2.decendants):\n',repr(result_it2))
assert len(result_at)==len(result_it), '%i!=%i'%(len(result_at),len(result_it))
assert len(result_at)==len(result_it2), '%i!=%i'%(len(result_at),len(result_it2))


#leaves
print('Get leaves')
result_at=[n.name for n in root_at.leaves]
result_it=[n.tag for n in root_it.deep if not n]
result_it2=[n.name for n in root_it2.leaves]

print('anytree (root_at.leaves):\n',repr(result_at))
print('itertree (replacement function):\n',repr(result_it))
print('itertree_node (root_it2.leaves):\n',repr(result_it2))
assert len(result_at)==len(result_it), '%i!=%i'%(len(result_at),len(result_it))
assert len(result_at)==len(result_it2), '%i!=%i'%(len(result_at),len(result_it2))



print('Get in_depth children (descendants) names/tags')
result_at=[n.name for n in root_at.descendants]
result_it=[n.tag for n in root_it.deep]
result_it2=[n.name for n in root_it2.descendants]

print('anytree (root_at.descendants):\n',repr(result_at))
print('itertree (root_it.deep):\n',repr(result_it))
print('itertree_node (root_it2.descendants):\n',repr(result_it2))
assert len(result_at)==len(result_it), '%i!=%i'%(len(result_at),len(result_it))
assert len(result_at)==len(result_it2), '%i!=%i'%(len(result_at),len(result_it2))

print('Get preorder iterator')
result_at=[n.name for n in PreOrderIter(root_at)]
result_it=[n.tag for n in chain([root_it],root_it.deep)]
result_it2=[n.name for n in root_it2.deep.preorder()]


print('anytree:\n',repr(result_at))
print('itertree:\n',repr(result_it))
print('itertree_node:\n',repr(result_it2))
assert len(result_at)==len(result_it), '%i!=%i'%(len(result_at),len(result_it))
assert len(result_at)==len(result_it2), '%i!=%i'%(len(result_at),len(result_it2))

print('Get postorder iterator')
result_at=[n.name for n in PostOrderIter(root_at)]
result_it=[n.tag for n in chain(root_it.deep.iter(up_to_low=False),[root_it])]
result_it2=[n.name for n in root_it2.deep.postorder()]


print('anytree:\n',repr(result_at))
print('itertree:\n',repr(result_it))
print('itertree_node:\n',repr(result_it2))
assert len(result_at)==len(result_it), '%i!=%i'%(len(result_at),len(result_it))
assert len(result_at)==len(result_it2), '%i!=%i'%(len(result_at),len(result_it2))


print('Get levelorder iterator')
result_at=[n.name for n in LevelOrderIter(root_at)]

result_it=[]
level_items = [root_it]
while level_items:
    next_level_items = []
    for i in level_items:
        result_it.append(i.tag)
        if len(i):
            next_level_items.extend(i)
    level_items = next_level_items

result_it2=[n.name for n in root_it2.deep.levelorder()]


print('anytree:\n',repr(result_at))
print('itertree:\n',repr(result_it))
print('itertree_node:\n',repr(result_it2))
assert len(result_at)==len(result_it), '%i!=%i'%(len(result_at),len(result_it))
assert len(result_at)==len(result_it2), '%i!=%i'%(len(result_at),len(result_it2))


