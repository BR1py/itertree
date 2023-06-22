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



This part of code contains some examples for the usage of itertree module

"""

from __future__ import absolute_import
import os
import shutil
import tempfile
from itertree import *

# We create a small iTree:
root = iTree('root')
root += iTree('A')
root += iTree('B')
B = iTree('B')
B += iTree('Ba')
B += iTree('Bb')
B += iTree('Bb')  # we create multiple 'Bb' elements to show how the placeholders are used during save and load
B += iTree('Bc')
root += B

# Now we create a internal link:
linked_element = iTree('internal_link', link=iTLink(target_path=[('B', 1)]))
root.append(linked_element)
print('iTree with linked element but no links loaded:')
print(root.render())
updated=root.load_links()
if updated:
    print('iTree with linked element with links loaded')
else:
    print('iTree links loaded, but no update required')

print('iTree loaded links:\n')
root.render()

# changes in "B" are only considered after reloading the links
B += iTree('B_post_append')
print('iTree with updated linked element but no reload of the links:\n')
root.render()

updated=root.load_links()
if updated:
    print('iTree with linked element with links loaded')
else:
    print('iTree links loaded, but no update required')

print('iTree with updated linked element and with links reloaded:')


root.render()
# get the linked element
il = root[('internal_link', 0)]
# append an item
il.append(iTree('new'))
# we make second element local
local = il[2].make_local()
local.append(iTree('sublocal'))
local.set_value('myvalue')
print('iTree with linked element and additional local items:')
root.render()

# we store the iTree in a file for later usage:
temp_dir = tempfile.mkdtemp()
target_path = os.path.join(temp_dir, 'out_linked.itr')
root.dump(target_path=target_path, overwrite=True, pack=False)

# if we delete the local object the linked object will come back in the tree:
del il[('Bb', 1)]
print('iTree with linked element and the overloading local item deleted:')
root.render()

# we load without loading the links
reload_tree = iTree('root').load(target_path, load_links=False)
# we do not need the stored data anymore:
shutil.rmtree(temp_dir)
print('iTree load from file with load_links parameter disabled (to make internal structure visible):')
print('-> See the placeholder element that was added to keep the key of the local item Bb[1] (flags==0b10000)')

reload_tree.render()

# finally we load the links again and we expect the result before we saved the tree in the file
print('iTree load from file with load_links() executed:')
reload_tree.load_links()
reload_tree.render()
