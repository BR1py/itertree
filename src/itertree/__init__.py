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


This part of code contains the initialization and publishing of the iTree related classes of the itertree package.
"""

from __future__ import absolute_import

__package__ = 'itertree'
__version__ = '1.1.3'
__licence__ = 'MIT incl. human protect patch'
__author__ = 'B.R.'
__url__ = 'https://github.com/BR1py/itertree'
__description__ = 'Python tree structure for data storage and iterations'

from .itree_helpers import iTLink, NoTag, NoKey, NoValue, Tag, \
    iTFLAG, getter_to_list, INF, INF_PLUS, INF_MINUS, Any, TagIdx, ITER
from .itree_main import iTree

from . import itree_data as Data
from . import itree_filters as Filters
from .itree_serializer.itree_render_dot import _iTreeRenderDot

iTreeRenderDot = _iTreeRenderDot().renders
