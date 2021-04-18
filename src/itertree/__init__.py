from __future__ import absolute_import

__package__ = 'itertree'
__version__ = '0.6.0'
__licence__ = 'MIT'
__author__ = 'B.R.'
__url__ = 'https://github.com/BR1py/itertree'
__description__ = 'Python tree structure for data storage and iterations'

from .itree_helpers import iTLink,iTMatch,TagIdx,TagIdxStr,TagMultiIdx,TagIdxBytes,TEMPORARY,READ_ONLY,LINKED,COPY_DEEP,COPY_OFF,COPY_NORMAL
from .itree_main import iTree,iTreeLink,iTreeTemporary,iTreeReadOnly

from . import itree_data as Data
from . import itree_serialize as Serializer
from . import itree_filter as Filter
