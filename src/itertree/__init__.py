"""
This code is taken from the itertree package:
  _ _____ _____ _____ _____ _____ _____ _____
 | |_   _|   __| __  |_   _| __  |   __|   __|
 |-| | | |   __|    -| | | |    -|   __|   __|
 |_| |_| |_____|__|__| |_| |__|__|_____|_____|

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
__version__ = '1.2.0'
__licence__ = 'MIT'
__author__ = 'B.R.'
__url__ = 'https://github.com/BR1py/itertree'
__description__ = 'Python tree structure for data storage and iterations'

from .itree_helpers import iTLink, NoTag, NoKey, NoValue, Tag, \
    iTFLAG, getter_to_list, INF, INF_PLUS, INF_MINUS, Any, TagIdx, ITER
from .itree_main import iTree

from . import itree_data as Data
itree_data=Data
from . import itree_filters as Filters
from .itree_serializer.itree_render_dot import _iTreeRenderDot

iTreeRenderDot = _iTreeRenderDot().renders
