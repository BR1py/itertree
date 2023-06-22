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



This part of code contains the profiling of nested iTree structures
"""

import os
import sys
import time
from itertree import *
mSetInterval=Filters.mSetInterval

"""
We run all the example (this will take a while and generate a huge print output!
"""
# first we build a very simple tree:
root = iTree('root')
root.append(iTree('Africa', value={'surface': 30200000, 'inhabitants': 1257000000}))
root.append(iTree('Asia', value={'surface': 44600000, 'inhabitants': 4000000000}))
root.append(iTree('America', value={'surface': 42549000, 'inhabitants': 1009000000}))
root.append(iTree('Australia&Oceania', value={'surface': 8600000, 'inhabitants': 36000000}))
# you might add items also via __iadd__() (+=) operator
root += iTree('Europe', value={'surface': 10523000, 'inhabitants': 746000000})
root += iTree('Antarctica', value={'surface': 14000000, 'inhabitants': 1100})

# for building next level here we select per index:
root[0] += iTree('Ghana', value={'surface': 238537, 'inhabitants': 30950000})
root[0] += iTree('Nigeria', value={'surface': 1267000, 'inhabitants': 23300000})
root[1].append(iTree('China', value={'surface': 9596961, 'inhabitants': 1411780000}))
root[1].append(iTree('India', value={'surface': 3287263, 'inhabitants': 1380004000}))
root[2].append(iTree('Canada', value={'surface': 9984670, 'inhabitants': 38008005}))
# here we select per TagIdx - remember in itertree you might put items with same tag multiple times:
root[('America', 0)].append(iTree('Mexico', value={'surface': 1972550, 'inhabitants': 127600000}))
# add multiple items via extend:
root[3].extend([iTree('Australia', value={'surface': 7688287, 'inhabitants': 25700000}),
                iTree('New Zealand', value={'surface': 269652, 'inhabitants': 4900000})])
root[4].append(iTree('France', value={'surface': 632733, 'inhabitants': 67400000}))
# use TagIdx for item selection
# remember itertree can have multiple items with same tag, we need here TagIdx object!
root[('Europe', 0)].append(iTree('Finland', value={'surface': 338465, 'inhabitants': 5536146}))

root.render()

# we might filter for data content:
inhabitants_interval = mSetInterval(0, 20000000)
filter_method = lambda i: i.value['inhabitants'] in inhabitants_interval
iterator = filter(filter_method, root.deep)

print('Filtered items; inhabitants in range: %s' % inhabitants_interval.math_repr())
for i in iterator:
    print(i)

# we do a mixed filtering:
inhabitants_interval = mSetInterval(0, 20000000)
filter_method1 = lambda i: i.value['inhabitants'] in inhabitants_interval
surface_interval = mSetInterval(0, 1000000)
filter_method2 = lambda i: i.value['surface'] in surface_interval and filter_method1(i)

iterator = filter(filter_method2, root.deep)

print('Filter2 items (we expect Antarctica does not match anymore!):')
for i in iterator:
    print(i)

