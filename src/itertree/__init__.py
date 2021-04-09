from __future__ import absolute_import

__package__ = 'itertree'
__version__ = '0.5.0'
__licence__ = 'MIT'
__author__ = 'B.R.'
__url__ = 'https://github.com/BR1py/itertree'
__description__ = 'Python tree structure for data storage and iterations'

from .itree_helpers import iTLink,iTMatch,TagIdx,TEMPORARY,NORMAL,LINKED,L,T,N,COPY_DEEP,COPY_OFF,COPY_NORMAL
from .itree_main import iTree
from . import itree_data as Data
from . import itree_serialize as Serializer

