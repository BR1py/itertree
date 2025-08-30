"""
This code is taken from the itertree package:

  ___ _____ _____ ____ _____ ____  _____ _____
 |_ _|_   _| ____|  _ \_   _|  _ \| ____| ____|
  | |  | | |  _| | |_) || | | |_) |  _| |  _|
  | |  | | | |___|  _ < | | |  _ <| |___| |___
 |___| |_| |_____|_| \_\|_| |_| \_\_____|_____|


https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license
For more information see: https://en.wikipedia.org/wiki/MIT_License

CONTENT DESCRIPTION:

This part of code contains the initialization and publishing of the iTree related classes of the itertree package.
"""

from __future__ import absolute_import

__package__ = 'itertree'
__version__ = '1.1.4'
__licence__ = 'MIT'
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
