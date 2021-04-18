'''
helper classes used in DataTree object
'''
from __future__ import absolute_import
import time
import fnmatch
from collections import namedtuple
# We are testing here if numpy is available
import numpy as np

try:
    np_object=np.object_
except TypeError:
    np_object=np.object


#CONSTANTS used as parameters of methods in DataTree and related classes
#Filter constants
TEMPORARY=TMP=0b10
LINKED = LNK = 0b100
READ_ONLY= RO = 0b1000

#copy constants
COPY_OFF=0
COPY_NORMAL=1
COPY_DEEP=2
#match operation combine
AND=0
OR=1

PRE_ALLOC_SIZE = 300


class iTLink(object):
    '''
    Definition of a link to an element in another DataTree
    '''
    __slots__ = ("_file_path", "_key_path",'_loaded','_link_data','_link_tag')

    def __init__(self, file_path, key_path=None):
        self._file_path = file_path
        self._key_path = key_path
        self._loaded = None
        self._link_tag=None
        self._link_data=None

    @property
    def loaded(self):
        return self._loaded

    @property
    def is_loaded(self):
        return self._loaded is not None

    @property
    def file_path(self):
        return self._file_path

    @property
    def key_path(self):
        return self._key_path

    @property
    def is_iTLink(self):
        return True

    @property
    def link_tag(self):
        return self._link_tag

    @property
    def link_data(self):
        return self._link_data

    def set_loaded(self,tag=None,data=None):
        self._loaded=time.time()
        self._link_tag=tag
        self._link_data=data

    def dict_repr(self):
        return {'path':self._file_path,'key':self._key_path}

    def __repr__(self):
        return 'iTreeLink(file_path=%s, key_path=%s)' % (
        repr(self._file_path), repr(self._key_path), )


class iTMatch(object):
    '''
    The match object is used to defined match to elements in the DtaTree used in  iterations over the DataTree
    '''

    __slots__=('_pattern', '_op', '_check')

    def __init__(self, pattern, combine=OR):
        self._pattern = pattern
        self._op = combine
        self._check = self._analyse(pattern)

    @property
    def is_iTMatch(self):
        return True

    def _analyse(self, pattern):
        t = type(pattern)
        if t is int:
            return {self._check_idxs: [pattern]}
        elif t is slice:
            if self._op:
                # in case of or we will search in a set
                return {
                    self._check_idxs: {i for i in range(pattern._start, pattern.step, pattern.stop)}}
            else:
                # in case of and we have a list that will be checked
                # this is possible but makes no sense for the slice case
                # anyway we will deliver a result (mostly False)
                return {
                    self._check_idxs: {i for i in range(pattern.start, pattern.step, pattern.stop)}}
        elif t is TagIdx:
            check_dict={}
            tag=pattern[0]
            if type(tag) is str:
                check_dict[self._check_tag_str] = [tag]
            else:
                check_dict[self._check_tag_eq] = [tag]
            idx=pattern[1]
            t2=type(idx)
            if t2 is int:
                check_dict[self._check_idxs]= {idx}
            elif t2 is slice:
                check_dict[self._check_idxs]= {i for i in range(idx.start, idx.step, idx.stop)}
            else: #index list!
                check_dict[self._check_idxs] = idx

            return {
                self._check_idxs: {i for i in range(pattern._start, pattern.step, pattern.stop)}}
        elif t is str:
            return {self._check_tag_str: [pattern]}
        elif len(pattern) > 1:
            if self._op:
                return {self._check_sub: {i for i in pattern}}
            else:
                return {self._check_sub: [i for i in pattern]}
        else:
            raise AttributeError('Given search pattern could not be decode %s' % pattern)

    def _op_logic(self,pre_result,result):
        '''
        depending if "or" or "and" combine is set this method
        checks the logical combination and gives back if we should stop or not
        :param pre_result: last result
        :param result: result
        :return: stop (True/False), new result
        '''
        if self._op:
            if result or pre_result:
                return True,True
            else:
                return False,False
        else:
            if result and pre_result:
                return False, True
            else:
                return True, False

    def _check_tag_eq(self,item, item_filter=None, patterns=None):
        if patterns is None:
            return False
        tag = item._tag
        result=not self._op
        for pattern in patterns:
            if pattern=='*':
                #any match
                stop, result = self._op_logic(result, True)
            else:
                stop,result=self._op_logic(result,(tag==pattern))
            if stop:
                return result
        return result

    def _check_tag_str(self, item, item_filter=None, patterns=None):
        if patterns is None:
            return False
        tag = item._tag
        result=not self._op
        for pattern in patterns:
            stop, result = self._op_logic(result, self._generic_fnmatch(tag, pattern))
            if stop:
                return result
        return result

    def _check_idxs(self, item, item_filter=None, patterns=None):
        if patterns is None:
            return False
        if item.parent is None:
            return False
        if self._op:
            return item.parent.index(item, item_filter) in patterns
        else:
            idx = item.parent.index(item, item_filter)
            for pattern in patterns:
                if idx != pattern:
                    return False
            return True


    def _check_sub(self, item, item_filter=None, patterns=None):
        if patterns is None:
            return False
        result = not self._op
        for pattern in patterns:
            stop, result = self._op_logic(result, iTMatch(pattern).check(item, item_filter))
            if stop:
                return result
        return result

    def _generic_fnmatch(self,value,pattern):
        if type(value) not in {str,bytes}:
            return False
        return fnmatch.fnmatch(value,pattern)

    def check(self, item, item_filter=None):
        if item_filter is not None:
            if not item_filter(item):
                return False
        result=not self._op
        for check_method, patterns in self._check.items():
            stop, result = self._op_logic(result, check_method(item, item_filter, patterns))
            if stop:
                return result
        return result

    def __repr__(self):
        return 'iTreeMatch(pattern=%s, op=%s)' % (repr(self._pattern), repr(self._op))


#base object for TagIdx definitions:

TagIdx = namedtuple('TagIdx',['tag','idx'])

class TagIdxStr(TagIdx):
    '''
    Define a TagIdx by a sting with an index separator (default='#')

    Example: "mytag#1" will be translated in the TagIdx("mytag",1)

    Note:: This makes only sense and can only be used if the tag is a string (not for other objects)

    :param tag_idx_str: string containing the definition

    '''

    def __new__(cls,tag_idx_str, tag_separator='#'):
        tag,idx= tag_idx_str.split(tag_separator)
        idx = int(idx)
        return super(TagIdxStr,cls).__new__(cls,tag,idx)

    @property
    def is_TagIdxStr(self):
        return True

class TagIdxBytes(TagIdxStr):
    '''
    Define a TagIdx by bytes with an index separator (default=b'#')

    Example: b"mytag#1" will be translated in the TagIdx(b"mytag",1)

    Note:: This makes only sense and can only be used if the tag is a byte (not for other objects)

    :param tag_idx_bytes: bytes containing the definition

    '''

    def __new__(cls, tag_idx_bytes, tag_separator=b'#'):
        return super(TagIdxBytes, cls).__new__(cls, tag_idx_bytes, tag_separator)

    @property
    def is_TagIdxBytes(self):
        return True


class TagMultiIdx(TagIdx):
    '''
    Define a TagMultiIdx

    :param tag: item tag (can be any hashable object)

    :param idxs: This parameter can be:
                 list of integer indexes
                 any iterable or iterator containing index integers
                  slice object
    '''
    def __new__(cls,tag, idxs):
        if type(idxs) in {str,bytes}:
            raise TypeError('We expect a multi target here that should be an iterable, '
                            'an iterator or a slice object!')
        if not hasattr(idxs,'__iter__'):
            if not hasattr(idxs,'__next__'):
                if type(idxs) is not slice:
                    raise TypeError('We expect a multi target here that should be an iterable, '
                                    'an iterator or a slice object!')
        return super(TagMultiIdx,cls).__new__(cls,tag,idxs)

    @property
    def is_TagMultiIdx(self):
        return True
