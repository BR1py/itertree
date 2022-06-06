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


This part of code contains
helper classes used in DataTree object
"""

from __future__ import absolute_import
import time
import fnmatch
import operator
import itertools
from collections import namedtuple


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

PRE_ALLOC_SIZE = 300

def accu_iterator(iterable, accu_method,initial_value=(None,)):
    """
    A method that enables itertools accumulation over a method
    .. note::  This method is just needed because in python <3.8 itertools accumulation has no initial parameter!
    :param iterable: iterable
    :param accu_method: accumulation method (will be fet by two parameters cumulated and new item)
    :return: accumulated iterator
    """
    for i in iterable:
        initial_value=accu_method(initial_value,i)
        yield initial_value

def is_iterator_empty(iterator):
    '''
    checks if the given iterator is empty
    :param iterator: iterator to be checked
    :return: tuple (True,iterator) - empty
                   (False, iterator) - item inside
    '''
    try:
        i=next(iterator)
    except StopIteration:
        return True,iterator
    return False,itertools.chain((i,),iterator)


__INTERVAL_RESULTS__ = (
    # 0 -normal range check
    lambda v,ll,ul,lc,uc,pc,pl: lc(v,ll) and uc(v,ul),
    # 1 -not in 0
    lambda v,ll,ul,lc,uc,pc,pl: not (lc(v,ll) and uc(v,ul)),
    # 0b10~2 up_limit is None (equal)
    lambda v,ll,ul,lc,uc,pc,pl: v == ll ,
    # 0b11~3 up_limit is None (not equal)
    lambda v, ll, ul, lc, uc, pc,pl: v != ll,
    # 0b100~4 low_limit is inf
    lambda v,ll,ul,lc,uc,pc,pl: uc(v,ul),
    # 0b101~5 low_limit is inf not in
    lambda v, ll, ul, lc, uc, pc,pl: not uc(v,ul),
    # 0b110~6 up_limit is inf
    lambda v, ll, ul, lc, uc, pc,pl: lc(v, ll),
    # 0b111~7 up_limit is inf not in
    lambda v, ll, ul, lc, uc, pc,pl: not lc(v, ll),
    # 0b1000~8 - pre and normal range check
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) and lc(v, ll) and uc(v, ul),
    # 0b1001~9 - pre and normal range check; not in
    lambda v, ll, ul, lc, uc, pc,pl: not (pc.check(v,pl) and lc(v, ll) and uc(v, ul)),
    # 0b1010~10 - pre and up_limit is None (equal)
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) and v == ll,
    # 0b1011~11 pre and up_limit is None (not equal)
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) and v != ll,
    # 0b1100~12 pre and low_limit is inf
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) and uc(v, ul),
    # 0b1101~13 pre and low_limit is inf not in
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) and not uc(v, ul),
    # 0b1110~14 pre and up_limit is inf
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) and lc(v, ll),
    # 0b1111~15 pre and up_limit is inf not in
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) and not lc(v, ll),
    # 0b10000~8 - pre or normal range check
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) or lc(v, ll) and uc(v, ul),
    # 0b10001~9 - pre or normal range check; not in
    lambda v, ll, ul, lc, uc, pc,pl: not (pc.check(v,pl) or lc(v, ll) and uc(v, ul)),
    # 0b10010~10 - pre or up_limit is None (equal)
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) or v == ll,
    # 0b10011~11 pre or up_limit is None (not equal)
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) or v != ll,
    # 0b10100~12 pre or low_limit is inf
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) or uc(v, ul),
    # 0b10101~13 pre or low_limit is inf not in
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) or not uc(v, ul),
    # 0b10110~14 pre or up_limit is inf
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) or lc(v, ll),
    # 0b10111~15 pre or up_limit is inf not in
    lambda v, ll, ul, lc, uc, pc,pl: pc.check(v,pl) or not lc(v, ll),
    )


class iTInterval():
    """
    helper class that defines an interval for range definitions in Data Models or Filters

    the class contains a check if a given value is in the defined interval or not

    The class might be a little bit under estimated in all the itertree functionalities but its a short but very
    powerful implementation of an Interval class for python.

    The class contains anything you might need in case of a Interval functionality. You can given open/closed interval
    definitions including infinite limits. The intervals can be combined to a mathematical set via
    the pre_interval parameter. And the check method allows to give other limits as defined.
    This is especially useful for dynamically calculated limits.

    The interval definition is also possible via a mathematical string like: "(1,2)" or "[10,+inf)".

    If you need a more advanced implementation you might have a look on  the intervals/portion python package.

    .. note::  For equal just set upper_limit to None (upper_open, lower_open parameter will be ignored in this case)
    """
    INF = 'inf'  # constant defining infinity limit

    def __init__(self, lower_limit=INF, upper_limit=INF, lower_open=True, upper_open=True,
                 not_in=False , pre_interval=None, pre_and=False, str_def=None):
        """
        helper class that defines an interval for range definitions

        the class contains a check if a given value is in the defined interval or not

        .. note::  For equal you give lower_limit and set upper_limit to None (lower_open,upper_open parameters will be
        ignored in this case). The math representation in this case is "== %s"%lower_limit

        .. note::  The not_in=True can be given to invert the interval check result (match is anything outside the interval)
               in the math representation we add in this case a "!" before the interval
        .. note::  Cascade interval definitions can be created the pre_interval definition
                             e.g. math_repr= "(([1,5]) and [9,12]) and [100,200]' valid values: 1...5,9...12,100..200


        :param lower_limit: lower limit of the interval
        :param upper_limit: upper limit of the interval
        :param lower_open: True - open interval (x>lower_limit)
                           False - closed interval (x>=lower_limit)
        :param upper_open: True - open interval (x<upper_limit)
                            False - closed interval (x<=upper_limit)
        :param not_in:  False - check for in interval
                        True - check for not in interval (outside)
        :param pre_interval: Interval object to be checked before this interval
        :param pre_and: True - combine the result of pre check with and this Interval check with the and operator
                        False - combine the result of pre check with and this Interval check with the or operator
        :param str_def: instance the object from given math_repr string (other parameters will be ignored in this case)
        """
        if str_def is not None:
            self.from_str(str_def)
        else:
            self.__init(lower_limit, upper_limit, lower_open, upper_open,
                 not_in, pre_interval, pre_and)

    def __init(self, lower_limit=INF, upper_limit=INF, lower_open=True, upper_open=True,
                     not_in=False , pre_interval=None, pre_and=True):
            method_key = 0
            if not_in:
                method_key = 1
            #pre check?
            self.pre_check=None
            self.pre_interval = None
            if pre_interval is not None:
                if type(pre_interval) is not iTInterval:
                    raise TypeError(
                        'Given pre_interval an interval object')
                self.pre_interval=pre_interval
                if pre_and:
                    self.pre_check=operator.and_
                    method_key = method_key | 0b1000
                else:
                    self.pre_check=operator.or_
                    method_key = method_key | 0b10000

            if upper_limit is None:
                method_key = method_key | 0b10 #equal/not equal
                if type(lower_limit) is str:
                    raise ValueError('Error iTInterval definition check on equal with %s limit is not possible'%lower_limit)
                self.lower_limit=lower_limit
                self.upper_limit = None
                self._low_check = lambda v, limit: v == limit
                self._up_check = lambda v, limit: True
            else:
                if type(lower_limit) is str:
                    if lower_limit.strip(' -') != self.INF:
                        raise ValueError('Invalid lower_limit given %s' % lower_limit)
                    self.lower_limit = self.INF
                    method_key = method_key | 0b100
                else:
                    self.lower_limit = lower_limit
                if type(upper_limit) is str:
                    if upper_limit.strip(' +') != self.INF:
                        raise ValueError('Invalid upper_limit given %s' % upper_limit)
                    self.upper_limit = self.INF
                    method_key = method_key | 0b110
                else:
                    self.upper_limit = upper_limit

                if self.upper_limit!=self.INF and self.lower_limit!=self.INF:
                    if lower_limit>upper_limit:
                        raise ValueError('lower_limit must be smaller the upper_limit!')

                if lower_open:
                    self._low_check = self._gt
                else:
                    self._low_check = self._ge
                if upper_open:
                    self._up_check = self._lt
                else:
                    self._up_check = self._le

                if self.lower_limit==self.INF:
                    # for corner case both are INF!
                    self._low_check=lambda a,b: True
            self.not_in=not_in
            self.upper_open = upper_open
            self.lower_open = lower_open
            self.method_key=method_key

    def _lt(self,a,b):
        try:
            return (a<b)
        except TypeError:
            return False
    def _le(self,a,b):
        try:
            return (a<=b)
        except TypeError:
            return False
    def _gt(self,a,b):
        try:
            return (a>b)
        except TypeError:
            return False
    def _ge(self,a,b):
        try:
            return (a>=b)
        except TypeError:
            return False


    @property
    def is_equal(self):
        return self.upper_limit is None

    def check(self, value, use_limits=None,return_iterator=False):
        """
        main check function
        :param value: value to be check if in interval or not (you might give iterables too!
        :param use_limits: You can replace the static limits in the interval with dynamic ones given in the check, any
                           nested iterable can be used here (do not use iterators!).
                           None - use static limit
                           (lower,_limit, upper_limit) - replace limits in highest level interval if lower_limit or
                                                        upper_limit is None the static one is used
                          (((lower_limit_l2,upper_limit_l2),(lower_limit_l1,upper_limit_l1)),(lower_limit_l0,upper_limit_l0))
                          - use nested tuples to give replacement limits to deeper levels (use None for using static ones)
        :return: True/False or iterator over single value check use any() to get a summary!
        """
        lower_limit = self.lower_limit
        upper_limit = self.upper_limit
        pre_limits=None
        if use_limits is not None:
            if len(use_limits)==2:
                if use_limits[0] is not None:
                    lower_limit = use_limits[0]
                if use_limits[1] is not None:
                    lower_limit = use_limits[1]
            elif len(use_limits)==3:
                if use_limits[1] is not None:
                    lower_limit = use_limits[1]
                if use_limits[2] is not None:
                    lower_limit = use_limits[2]
                if use_limits[0] is not None:
                    pre_limits = use_limits[0]
            else:
                raise SyntaxError('Given use_limits %s not matching'%use_limits)
            # use pre defined limit
        check_method=__INTERVAL_RESULTS__[self.method_key]
        if type(value) in (str,bytes):
            # we may miss here some types the generator object might be delivered in case an iterable is detected!
            if self.not_in:
                return_item= True
            else:
                return_item= False
        elif hasattr(value, '__iter__') or hasattr(value, '__next__'):
            # iterable
            if return_iterator:
                return_item= (check_method(v,lower_limit,upper_limit,
                                           self._low_check,self._up_check,
                                           self.pre_interval, pre_limits) for v in value)
            else:
                return_item= any((check_method(v, lower_limit, upper_limit,
                                               self._low_check, self._up_check,
                                               self.pre_interval, pre_limits)
                        for v in value))
        else:
            if return_iterator:
                return_item= iter((check_method(value, lower_limit, upper_limit,
                                                self._low_check, self._up_check,
                                                self.pre_interval, pre_limits),))

            else:
                return_item= check_method(value, lower_limit, upper_limit,
                                          self._low_check,self._up_check,
                                          self.pre_interval, pre_limits)
        return return_item

    def math_repr(self):
        """
        mathematical string representation of the interval
        :return: string
        """

        if self.upper_limit is None:
            if self.not_in:
                return '!=%s' % str(self.lower_limit)
            else:
                return '==%s'%str(self.lower_limit)
        elif self.lower_open:
            out_str = '('
        else:
            out_str = '['
        if self.lower_limit == self.INF:
            out_str = out_str + '-inf,'
        else:
            out_str = out_str + str(self.lower_limit) +','
        if self.upper_limit == self.INF:
            out_str = out_str + '+inf'
        else:
            out_str = out_str + str(self.upper_limit)
        if self.upper_open:
            out_str = out_str + ')'
        else:
            out_str = out_str + ']'
        if self.not_in:
            out_str = '!'+out_str
        if self.pre_check is not None:
            if self.pre_check==operator.and_:
                out_str = '(%s) and '%self.pre_interval.math_repr() + out_str
            else:
                out_str = '(%s) or ' % self.pre_interval.math_repr() + out_str
        return out_str

    def from_str(self, interval_str):
        """
        create the interval from a math representation string
        .. note::  Give inf for infinity
        :param interval_str: math string representation
        :return:
        """
        interval_str=interval_str.strip(' ')
        i=interval_str.rfind(') and ')
        ii=interval_str.rfind(') or ')
        if i>ii:
            pre_and=True
            pre_interval=iTInterval(str_def=interval_str[1:i])
            interval_str=interval_str[(i+6):]
        elif ii>i:
            pre_and = False
            pre_interval = iTInterval(str_def=interval_str[1:ii])
            interval_str = interval_str[(ii + 5):]
        else:
            pre_and = True
            pre_interval = None
        if interval_str.startswith('=='):
            self.__init(float(interval_str[2:]),None,pre_interval=pre_interval,pre_and=pre_and)
            return
        if interval_str.startswith('!='):
            self.__init(float(interval_str[2:]), None, not_in=True, pre_interval=pre_interval, pre_and=pre_and)
            return
        if interval_str[0]=='!':
            not_in=True
            interval_str=interval_str[1:].strip(' ')
        else:
            not_in = False
        if interval_str[0] == '[':
            lower_open=False
        elif interval_str[0] == '(':
            lower_open=True
        else:
            raise AttributeError('given upper interval border unknown')

        if interval_str[-1] == ']':
            upper_open=False
        elif interval_str[-1] == ')':
            upper_open=True
        else:
            raise AttributeError('given upper interval border unknown')
        i = interval_str.find(',')
        if i == -1:
            raise AttributeError('No comma separator found in interval_string')
        if interval_str[1:i].strip(' +-') == self.INF:
            lower_limit = self.INF
        else:
            lower_limit = float(interval_str[1: i])
        if interval_str[(i + 1): -1].strip(' +-') == self.INF:
            upper_limit = self.INF
        else:
            upper_limit = float(interval_str[(i + 1): -1])

        self.__init(lower_limit, upper_limit,lower_open,upper_open, not_in, pre_interval=pre_interval, pre_and=pre_and)

    def __repr__(self):
        """
        object representation (with all parameters)
        :return: object representation string
        """
        out_str='iTInterval('
        out_str=out_str+'lower_limit=%s,'%str(self.lower_limit)
        if self.upper_limit is None: #EQUAL
            out_str = out_str + ' upper_limit=None,'
        else:
            out_str = out_str + ' upper_limit=%s,' % str(self.upper_limit)
            if self.lower_open:
                out_str = out_str + ' lower_open=True,'
            else: # CLOSED
                out_str = out_str + ' lower_open=False,'
            if self.upper_open:
                out_str = out_str + ' upper_open=True,'
            else:  # CLOSED
                out_str = out_str + ' upper_open=False,'
        if self.not_in:
            out_str = out_str + ' not_in=True,'
        if self.pre_interval is not None:
            if self.pre_check==operator.or_:
                out_str = out_str + ' pre_interval=%s, pre_and=False'%repr(self.pre_interval)
            else:
                out_str = out_str + ' pre_interval=%s, pre_and=True' % repr(self.pre_interval)
        out_str = out_str[:-1]+')'
        return out_str

    def __str__(self):
        """
        object representation based on math_repr
        :return: object representation string
        """
        return 'iTInterval(str_def=%s)' % repr(self.math_repr())

class iTLink(object):
    '''
    Definition of a link to an element in another DataTree
    '''
    __slots__ = ("_file_path", "_key_path",'_loaded','_link_data','_link_tag','_link_item','_source_path')

    def __init__(self, file_path=None, key_path=None,link_item=None):
        self._file_path = file_path
        self._key_path = key_path
        self._loaded = None
        self._link_tag=None
        self._link_data=None
        self._source_path=None
        self._link_item = link_item

    @property
    def loaded(self):
        return self._loaded

    @property
    def is_loaded(self):
        return self._loaded is not None


    @property
    def link_item(self):
        return self._link_item

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

    @property
    def source_path(self):
        return self._source_path

    def set_source_path(self,path):
        self._source_path=path

    def set_loaded(self,tag=None,data=None):
        self._loaded=time.time()
        self._link_tag=tag
        self._link_data=data


    def dict_repr(self):
        return {'path':self._file_path,'key':self._key_path}

    def __repr__(self):
        if self._link_item is not None:
            return 'iTreeLink(file_path=%s, key_path=%s,link_item=%s)' % (
                repr(self._file_path), repr(self._key_path),repr(self._link_item),)

        return 'iTreeLink(file_path=%s, key_path=%s)' % (
        repr(self._file_path), repr(self._key_path), )


class iTMatch(object):
    '''
    The match object is used to defined match to elements in the DtaTree used in  iterations over the DataTree
    The defined iMatch object can be used for checks against iTree objects (mainly for checks against the tag and also
    for string matches e.g. for finding iTree.data.keys() or .values() in filters.
    '''

    __slots__=('_pattern', '_op', '_check')

    def __init__(self, pattern, combine_or=True):
        """
        Create a match pattern for different proposes. Depending on the type we have following functions:

         * int     - check for an index
         * TagIdx  - check for a TagIdx
         * str - string pattern using fnmatch
         * iterable like list, tuple, ... combine the given patterns with the combine key

        :param pattern: give pattern

        :param combine_or: True - or ; False - and; combination of matches/match patterns
        """
        self._pattern = pattern
        self._op = combine_or
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
        if hasattr(item, '_tag'):
            tag = item._tag
        else:
            tag=item
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
        if hasattr(item,'_tag'):
            tag = item._tag
        else:
            tag=item
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

    .. note::  This makes only sense and can only be used if the tag is a string (not for other objects)

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

    .. note::  This makes only sense and can only be used if the tag is a byte (not for other objects)

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
