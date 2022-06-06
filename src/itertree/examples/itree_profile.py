# -*- coding: utf-8 -*-
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


This part of code contains a profiling analysis of iTree objects and functions
"""

import cProfile
import sys
from itertree import *
import itertree

max_items = 100000
if len(sys.argv)==2:
    max_items = int(sys.argv[1])

root=None
print('Running on itertree version:',itertree.__version__)

def performance_dt():
    global root,max_items
    it = iTree('root')
    #insert
    for i in range(max_items):
        it.insert(1,iTree('%i' % i))
    #append datatree with items
    for i in range(max_items):
        it.append(iTree('%i' % i))

    it=iTree('root',subtree=[iTree('%i' % i) for i in range(max_items)])
    #read datatree items per tag and index
    for i in range(max_items):
        a = it['%i' % i]
        b = it[i]
    for i in range(max_items):
        del it[0]
    new_it=it*max_items
    it.extend(new_it)
    # measure also __iadd__
    #for i in range(max_items):
    #    it += iTree('%i' % i)

    if False:
        for i in range(max_items):
            for ii in range(10):
                it[i].append(iTree(str(ii)))
        it.count_all()
    root=it

cProfile.run('performance_dt()')


