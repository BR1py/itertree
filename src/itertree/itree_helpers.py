'''
helper classes used in DataTree object
'''
from __future__ import absolute_import
import time
import fnmatch
# We are testing here if numpy is available
import numpy as np
try:
    np_object=np.object_
except TypeError:
    np_object=np.object


#CONSTANTS used as parameters of methods in DataTree and related classes
#Filter constants
TEMPORARY=T=0b10
LINKED = L = 0b100
NORMAL= N = 0b1
ALL=T|L|N
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

    def check(self, item, item_filter=ALL):
        if type(item_filter) is int:
            i=item_filter
            item_filter=lambda item: ((item._flags & ~i) == 0)
        result=not self._op
        for check_method, patterns in self._check.items():
            stop, result = self._op_logic(result, check_method(item, item_filter, patterns))
            if stop:
                return result
        return result

    def __repr__(self):
        return 'iTreeMatch(pattern=%s, op=%s)' % (repr(self._pattern), repr(self._op))


class TagIdx():

    def __init__(self, tag, idx=None, tag_separator='#'):
        '''
        This is a special tuple containing a combination of tag,index used for the identification
        of elements in iTrees

        HINT: The object can be instanced by giving a tag and and index as parameters. But string only
        parameters will be parsed and split by the separator given e.g. "mytag#1" -> ("mytag",1)
        Obviously parsed tags can only be used if tags used in iTree are string objects!

        The content of the object can be reached via property obj.tag, obj.idx or per index obj[0](tag), obj[1] (index).

        :param tag: tag object (string or hashable object)
        :param idx: for single target integer object (or None for parsed tags)
                    for multi target None (pure tag without index -> tag_family target)
                                     slice
                                     index list/iterator
        :param tag_separator: separator for split of tag and index (default is "#")
        '''
        if idx is None:
            tag, idx = tag.split(tag_separator)
            if ':' in idx:
                tmp=idx.split(':')
                slice_parameter=[int(i) for i in tmp]
                idx=slice(*slice_parameter)
            else:
                idx=int(idx)
        self._tuple = (tag, idx)
        self._is_single=(type(self.idx) is int)
    @property
    def is_TagIdx(self):
        return True

    @property
    def tag(self):
        return self._tuple[0]

    @property
    def idx(self):
        return self._tuple[1]

    @property
    def is_single(self):
        return self._is_single

    def __getitem__(self, idx):
        return self._tuple[idx]

    def __hash__(self):
        return hash(self._tuple)

    def __repr__(self):
        return 'TagIdx(%s, %s)'%(repr(self.tag),repr(self.idx))

