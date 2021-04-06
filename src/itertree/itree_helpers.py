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

class iTMagicList():
    '''
    This object should increase th performance on huge lists by allocating the memory in blocks
    and using numpy
    '''
    __slots__ = ('_length','_items2','_is_list')

    
    def __init__(self, def_list=None):
        self._is_list = True
        if def_list is not None:
            self._length = len(def_list)
            if self._length > PRE_ALLOC_SIZE:
                self._items2 = np.array(def_list, dtype=np_object)
                self.pre_alloc_list()
            else:
                self._items2 =list(def_list)
        else:
            self._length = 0
            self._items2 = []

    def pre_alloc_list(self,length=None):
        if length is None:
            length=PRE_ALLOC_SIZE
        else:
            length=length+PRE_ALLOC_SIZE
        self._items2 = np.hstack([self._items2[:self._length], np.empty(length, dtype=np_object)])
        self._is_list = False

    def _valid_idx_except(self,idx):
        t = type(idx)
        if t is int:
            if idx >= self._length or idx < -self._length:
                return IndexError('Given index is out of range')
            return idx
        elif t is slice:
            self._valid_idx_except(idx.start)
            if idx.stop is not None:
                self._valid_idx_except(idx.stop)
            return idx
        else: # index list
            try:
                if len(idx)>PRE_ALLOC_SIZE:
                    idx=np.array(idx)
                    if len(np.where(idx >= self._length | idx < -self._length)[0])>0:
                        return IndexError('Given index is out of range')
                    return idx
            except AttributeError:
                pass
            return [self._valid_idx_except(i) for i in idx]

    def __getitem__(self, key):
        if self._is_list:
            if type(key) in {int,slice}:
                self._valid_idx_except(key)
                return self._items2[key]
            return [self.___getitem__(k) or None for k in key]
        else:
            self._valid_idx_except(key)
            return self._items2[key]

    def __setitem__(self, key, item):
        if key < 0:
            key = self._length - key
        try:
            self._items2[key] = item
            if key>=self._length:
                self._length += 1
        except IndexError:
            self.pre_alloc_list()
            self._items2[key] = item
            if key>=self._length:
                self._length += 1

    def __delitem__(self, key):
        key=self._valid_idx_except(key)
        if self._is_list:
            if type(key) is int:
                del self._items2[key]
                self._length-=1
            else:
                self._length-=len((self._items2.__delete__(k) for k in key))
        else:
            if type(key) is int:
                key = [key]
            self._items2 = np.delete(self._items2, key)
            self._length-=len(key)
            if len(self._items2)-self._length>PRE_ALLOC_SIZE:
                #free mem
                self._items2=self._items2[:self._length]

    def __len__(self):
        return self._length

    def __contains__(self,other):
        return other in self._items2

    def __iter__(self):
        return iter(self._items2)

    @property
    def delta(self):
        return len(self._items2)-self._length

    def remove(self, item):
        if self._is_list:
            self._items2.remove(item)
            self._length-=1
        else:
            i = np.where(self._items2 == item)[0]
            if len(i) > 0:
                self._items2 = np.delete(self._items2, i)
                self._length-=len(i)
                if self.delta>PRE_ALLOC_SIZE:
                    #free mem
                    self._items2=self._items2[:self._length]

    def insert(self,key,item):
        '''
        the insert operation  is by far th eslowest operation and should be avoided
        :param key: insert position
        :param item: item to be inserted
        :return: True
        '''
        self._valid_idx_except(key)
        if key<0:
            key=self._length-key
        if key>self._length:
            # we append
            try:
                self._items2[self._length] = item
                self._length += 1
            except IndexError:
                self.pre_alloc_list()
                self._items2[self._length] = item
                self._length += 1
        else:
            if self._is_list:
                self._items2.insert(key,item)
                self._length += 1
            else:
                #self._items[(key+1):(self._length+1)]=self._items[key:self._length]
                #self._items[key]=item
                l=len(self._items2)
                self._items2=np.insert(self._items2,key,item)
                self._length += (len(self._items2)-l)

    def append(self, item):
        if not self._is_list:
            if self._length>=len(self._items2):
                self.pre_alloc_list()
            self._items2[self._length] = item
            self._length += 1
        else:
            if self._length>=PRE_ALLOC_SIZE:
                self.pre_alloc_list()
                self._items2[self._length] = item
                self._length += 1
            else:
                self._items2.append(item)
                self._length +=1
        # positive return needed for list comprehensions
        return True

    def extend(self, items):
        try:
            size=len(items)
            delta=self.delta
            if delta<=size:
                self.pre_alloc_list((size-delta))
        except AttributeError:
            # we might have an iterator therefore we cannot pre allocate!
            size=None
        if self._is_list:
            self._items2.extend(items)
            if len(self._items2)>PRE_ALLOC_SIZE:
                self._items2=np.array(self._items2,dtype=np_object)
        else:
            if size is None:
                self._items2=np.insert(self._items2,self._depth,items)
            else:
                self._items2[np.arange(self._depth,(self._depth+size))]=items
        # positive return needed for list comprehensions
        return True

    def pop(self,key=None):
        if key is None:
            key=self._length-1
        else:
            self._valid_idx_except(key)
        if self._is_list:
            if type(key) is int:
                item = self._items2[key]
                del self._items2[key]
                self._length-=1
            else:
                item=[self._items2.pop(k) for k in key]
                self._length -=len(item)
        else:
            item = self._items2[key]
            self._items2 = np.delete(self._items2, key)
            self._length-=len(item)
            if self.delta > PRE_ALLOC_SIZE:
                # free mem
                self._items2 = self._items2[:self._length]
        return item

    def __repr__(self):
        return str(list(self._items2[:self._length]))

class iTLink(object):
    '''
    Definition of a link to an element in another DataTree
    '''
    __slots__ = ("_ref_path", "_ref_key",'_loaded')

    def __init__(self, ref_path, ref_key, ref_first=False):
        self._ref_path = ref_path
        self._ref_key = ref_key
        self._loaded = None

    @property
    def loaded(self):
        return self._loaded

    @property
    def is_iTreeLink(self):
        return True

    def set_loaded(self):
        self._loaded=time.time()

    def dict_repr(self):
        return {'ref_path':self._ref_path,'ref_key':self._ref_key}

    def __repr__(self):
        return 'iTreeLink(ref_path=%s, ref_key=%s)' % (
        repr(self._ref_path), repr(self._ref_key), )


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
    def is_iTreeMatch(self):
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
        check=fnmatch.fnmatch
        for pattern in patterns:
            stop, result = self._op_logic(result, check(tag, pattern))
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

