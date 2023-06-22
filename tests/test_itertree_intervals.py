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



This part of code contains
the integration tests related to the base iTree functionalities
"""

import os
import timeit
import copy
import shutil
# import sys
import collections
# import timeit
import pytest

try:
    import numpy as np
    # only needed in case of numpy arrays in data
    # for serializing the data
except:
    np = None

import pickle
import timeit
from types import GeneratorType
from collections import OrderedDict
from itertree import *
from itertree.itree_helpers import *
from itertree.itree_filters import  *

root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)

print('Test start')


def get_relpath_to_root(item_path):
    new_path = item_path.replace(root_path, '')
    if new_path.startswith('\\'):
        new_path = new_path[1:]
    if new_path.startswith('/'):
        new_path = new_path[1:]
    return root_path + '/' + new_path


class Test1_mSetIntervals():

    def test1_numerical_definitions(self):
        print('\nRUN TEST: mSetInterval numerical definitions')

        interval=mSetInterval(1,2)
        assert interval.has_vars is False
        assert interval.vars == set()

        assert 1 in interval
        assert 2 in interval
        assert 2.1 not  in interval
        assert 0.9  not in interval
        # for this case we also check some lists:
        assert [1,1.5,2] in interval
        assert [0, 0.9999,2.0000011, 2.1] not in interval
        assert [0, 1, 1.5, 2] not in interval
        assert list(interval.iter_in([0, 1, 1.5,2.1, 2]))==[False,True,True,False,True]
        # we do not repeat because list actions internally go back on "in"

        assert interval.math_repr()=='[%s,%s]'%(repr(1),repr(2))

        interval=mSetInterval((-100,True),(200,True))
        assert -100 not in interval
        assert 200 not in interval
        assert -99.9999  in interval
        assert 199.9999 in interval
        assert interval.math_repr()=='(%s,%s)'%(repr(-100),repr(200))

        interval=mSetInterval(1,2,complement=True)
        assert 1 not in interval
        assert 2 not in interval
        assert 2.1 in interval
        assert 0.9 in interval
        assert interval.math_repr()=='![%s,%s]'%(repr(1),repr(2))

        # equal
        interval = mSetInterval(1, 1)
        assert 1 in interval
        assert 2 not in interval
        assert 1.1 not in interval
        assert 0.99999 not in interval
        assert interval.math_repr() == '[1,1]'

        interval = mSetInterval(1, (1, True))
        assert 1 in interval
        assert 2 not in interval
        assert 1.1 not in interval
        assert 0.99999 not in interval
        assert interval.math_repr() == '[1,1)'

        interval = mSetInterval((1,True), 1)
        assert 1 in interval
        assert 2 not in interval
        assert 1.1 not in interval
        assert 0.99999 not in interval
        assert interval.math_repr() == '(1,1]'

        #empty set
        interval = mSetInterval((1,True), (1,True))
        assert 1 not in interval
        assert 2 not in interval
        assert 1.1 not in interval
        assert 0.99999 not in interval
        assert interval.is_empty_set
        assert interval.math_repr() == '(1,1)'

        # not equal
        interval = mSetInterval(1, 1, False,True )
        assert 1 not in interval
        assert 2 in interval
        assert 1.1  in interval
        assert 0.99999  in interval
        assert not interval.is_empty_set_complement

        assert interval.math_repr() == '![1,1]'

        interval = mSetInterval(1, (1, True), complement=True )
        assert 1 not in interval
        assert 2 in interval
        assert 1.1  in interval
        assert 0.99999  in interval
        assert interval.math_repr() == '![1,1)'

        interval = mSetInterval((1,True), 1, complement=True )
        assert 1 not in interval
        assert 2 in interval
        assert 1.1  in interval
        assert 0.99999  in interval
        assert interval.math_repr() == '!(1,1]'

        interval = mSetInterval((1,True),(1, True), complement=True )
        assert 1 in interval
        assert 2 in interval
        assert 1.1  in interval
        assert 0.99999  in interval
        assert interval.math_repr() == '!(1,1)'
        assert interval.is_empty_set_complement

        # resort limits
        interval = mSetInterval((100,True), (1,True) )
        assert interval.math_repr() == '(%s,%s)' % (repr(1), repr(100))

        print('\nRESULT TEST: mSetInterval numerical definitions -> PASS')

    def test2_char_definitions(self):
        print('\nRUN TEST: mSetInterval char definitions')

        interval=mSetInterval('[1,2]')
        assert interval.get_init_args()==(mSetItem(1),mSetItem(2) )
        interval = mSetInterval('(-1,2]')
        assert interval.get_init_args() == (mSetItem(-1,True),mSetItem(2) )
        interval = mSetInterval('(-1,200)')
        assert interval.get_init_args()== (mSetItem(-1,True),mSetItem( 200,True))
        interval = mSetInterval(' ( -1.3 ,  200.3E3 ) ') #adding spaces
        assert interval.get_init_args() == (mSetItem(-1.3,True,'{:1.1f}'),mSetItem(200300.0,True, '{:3.1e}') )
        # outside
        interval = mSetInterval('! [ 1 , 2 ] ')
        assert interval.get_init_args() == (mSetItem(1), mSetItem(2), False, True )
        interval = mSetInterval('!(-1,2]')
        assert interval.get_init_args() == (mSetItem(-1,True),mSetItem(2), False, True )
        interval = mSetInterval('  !(-1,200)')
        assert interval.get_init_args() == (mSetItem(-1.0,True), mSetItem(200, True), False, True )
        interval = mSetInterval('! ( -1.3 ,  200.3E3 ) ')  # adding spaces
        assert interval.get_init_args() == (mSetItem(-1.3,True,'{:1.1f}'), mSetItem(200300,True,'{:3.1e}') ,False, True )

        #equal
        interval = mSetInterval('x==2.11 ') # double == is allowed
        assert interval.get_init_args() == (mSetItem(2.11,False,'{:1.2f}'), mSetItem(2.11,False,'{:1.2f}'))
        interval = mSetInterval(' x =  2.11  ') # single = is allowed too!
        assert interval.get_init_args() ==(mSetItem(2.11, False, '{:1.2f}'), mSetItem(2.11, False, '{:1.2f}'))
        interval = mSetInterval(' x !=  2.11  ') # single = is allowed too!
        assert interval.get_init_args() == (mSetItem(2.11, False, '{:1.2f}'), mSetItem(2.11, False, '{:1.2f}'),False,True)

        print('\nRESULT TEST: mSetInterval char definitions -> PASS')

    def test3_infinity_definitions(self):
        print('\nRUN TEST: mSetInterval infinity definitions')

        #numerical definitions
        interval = mSetInterval((float('-inf'),True,'{:.3f}'), (1, True,'{:.3f}'))
        assert -10000 in interval
        assert float('-inf') not in interval
        assert interval.math_repr() == '(-inf,1.000)'
        interval = mSetInterval((float('-inf'),False,'{:.3f}'), (1, True,'{:.3f}'))
        assert float('-inf') in interval
        assert interval.math_repr()=='[-inf,1.000)'
        interval = mSetInterval((float('inf'),True), (1, False)) # switch order!
        assert 1E34 in interval
        assert float('inf') not  in interval
        assert interval.math_repr()=='[1,inf)'
        interval = mSetInterval((float('inf'),False,'{:.3f}'), (1, True,'{:.3f}'))
        assert float('inf') in interval
        interval = mSetInterval((float('+inf'),False), (1, False) )
        assert float('inf') in interval
        assert interval.math_repr()=='[1,inf]'
        interval = mSetInterval(float('+inf'), float('+inf') )
        assert interval.math_repr() == '[inf,inf]'
        assert float('inf') in interval
        interval = mSetInterval(float('+inf'), float('+inf'), False, True )
        assert interval.math_repr() == '![inf,inf]'
        assert float('inf') not in interval
        assert float('-inf') in interval
        assert float('nan') in interval


        interval = mSetInterval('[1,inf]')
        assert interval.get_init_args()==(mSetItem(1), mSetItem(float('+inf')) )
        interval = mSetInterval('(-inf,1]')
        assert interval.get_init_args()==(mSetItem(float('-inf'),True),mSetItem(1) )
        interval = mSetInterval(' [ 1 , inf    )')
        assert interval.get_init_args()==(mSetItem(1), mSetItem(float('+inf'),True) )
        interval = mSetInterval('[ -inf , 1 ]')
        assert interval.get_init_args()==(mSetItem(float('-inf')),mSetItem(1)  )
        interval = mSetInterval('[ inf , -inf ]') # change order!
        assert interval.get_init_args()==(mSetItem(float('-inf')),mSetItem(float('inf')))
        interval = mSetInterval('x==inf')
        assert interval.get_init_args()==(mSetItem(float('+inf')), mSetItem(float('+inf')))
        interval = mSetInterval('x!=inf')
        assert interval.get_init_args() == (mSetItem(float('+inf')), mSetItem(float('+inf')), False, True )

        print('\nRESULT TEST: mSetInterval infinity definitions -> PASS')

    def test4_formatters(self):
        print('\nRUN TEST: mSetInterval formatters')
        low=-2.345678
        up= 1.234567
        interval=mSetInterval(low,up )
        assert interval.math_repr()=='[%s,%s]'%(str(low),str(up))
        l_formatter='{:.2f}'
        h_formatter='{:2.4f}'
        assert interval.math_repr(formatters=(l_formatter,h_formatter))=='[%s,%s]'%(l_formatter.format(low),
                                                                                    h_formatter.format(up))
        l_formatter='{:.2e}'
        h_formatter='{:2.4e}'
        assert interval.math_repr(formatters=(l_formatter,h_formatter))=='[%s,%s]'%(l_formatter.format(low),
                                                                                    h_formatter.format(up))
        l_formatter='%f'
        h_formatter='%2.3f'
        assert interval.math_repr(formatters=(l_formatter,h_formatter))=='[%s,%s]'%(l_formatter%low,
                                                                                    h_formatter%up)
        l_formatter='%e'
        h_formatter='%2.3e'
        assert interval.math_repr(formatters=(l_formatter,h_formatter))=='[%s,%s]'%(l_formatter%low,
                                                                                    h_formatter%up)

        print('\nRESULT TEST: mSetInterval formatters -> PASS')

    def test4_variable_definitions(self):
        print('\nRUN TEST: mSetInterval variable definitions')

        interval = mSetInterval('low', 'up')
        assert interval.has_vars


        var_dict = {'low': 1, 'up': 2}
        with pytest.raises(TypeError):
            assert 0 not in interval
        assert (0,var_dict) not in interval
        assert (1,var_dict) in interval
        assert (2, var_dict) in interval
        assert (3, var_dict) not in interval
        assert list(interval.iter_in([0,1,2,3],var_dict))==[False,True,True,False]
        assert interval.math_repr()=='[low,up]'

        interval = mSetInterval('low', 'up', False, True)

        var_dict = {'low': 1, 'up': 2}
        assert list(interval.iter_in([0, 1, 2, 3], var_dict)) == [True,False,False, True]

        interval = mSetInterval('[low,up]')
        assert interval.get_init_args()==('low', 'up')
        interval = mSetInterval('( low , up )')
        assert interval.get_init_args() == (mSetItem('low',True), mSetItem('up', True))

        interval = mSetInterval('! [ low , up ]   ')
        assert interval.get_init_args() == (mSetItem('low'), mSetItem('up'), False, True)
        interval = mSetInterval('!( low , up )')
        assert interval.get_init_args() == (mSetItem('low',True), mSetItem('up', True), False, True)

        interval = mSetInterval('x!=low ')
        assert interval.get_init_args() == (mSetItem('low'), mSetItem('low'), False, True)
        assert (1,{'low':2})  in interval
        assert (1, {'low': 1}) not in interval

        interval = mSetInterval(' x= low ')
        assert interval.get_init_args() == (mSetItem('low'), mSetItem('low'))
        assert (1,{'low':2})  not in interval
        assert (1, {'low': 1})  in interval

        print('\nRESULT TEST: mSetInterval variable definitions -> PASS')

    def test4_intersections(self):
        print('\nRUN TEST: iTIntersectionSets')

        interval1=mSetInterval((0,True),(100,True)) # open interval
        interval2 = mSetInterval((50,True), (500,True)) # open interval

        mix_interval=mSetCombine(interval1,interval2,is_union=False) # -> [50,100]
        assert 49 not in mix_interval
        assert 101 not in mix_interval
        assert 50 not in mix_interval
        assert 100 not in mix_interval
        assert 50.000001  in mix_interval
        assert 99.9999999 in mix_interval
        assert list(mix_interval.iter_in((50,51,99,100)))==[False,True,True,False]

        mix_interval = mSetCombine(interval1, interval2, False,True)
        assert 49 in mix_interval
        assert 101 in mix_interval
        assert 50 in mix_interval
        assert 100 in mix_interval
        assert 50.000001 not in mix_interval
        assert 99.9999999 not in mix_interval
        assert list(mix_interval.iter_in((50,51,99,100)))==[True,False,False,True]

        mix_interval = mSetCombine(interval1, interval2,{51,99}, False,True)  # mix of interval and set
        assert 50 in mix_interval
        assert 100 in mix_interval
        assert 51 not in mix_interval
        assert 99 not in mix_interval
        assert 52 in mix_interval
        assert 98 in mix_interval
        assert list(mix_interval.iter_in((51,52,98,99)))==[False,True,True,False]

        interval1=mSetInterval((0,True),(100,True)) # open interval
        interval2 = mSetInterval((400,True), (500,True)) # open interval
        mix_interval=mSetCombine(interval1,interval2)
        assert 0 not in mix_interval
        assert 100 not in mix_interval
        assert 400 not in mix_interval
        assert 500 not in mix_interval
        assert 1 in mix_interval
        assert 99 in mix_interval
        assert 401 in mix_interval
        assert 499 in mix_interval
        assert list(mix_interval.iter_in([0,100,400,500,1,99,401,499])) == [False,False,False,False,True, True,True,True]

        mix_interval = mSetCombine(interval1, interval2, complement=True)
        assert 0 in mix_interval
        assert 100 in mix_interval
        assert 400 in mix_interval
        assert 500 in mix_interval
        assert 1 not in mix_interval
        assert 99 not in mix_interval
        assert 401 not in mix_interval
        assert 499 not in mix_interval
        assert list(mix_interval.iter_in([0,100,400,500,1,99,401,499])) == [True, True,True,True,False,False,False,False]

        mix_interval = mSetCombine(interval1, interval2,{2000}, complement=False) # add a set
        assert 2000 in mix_interval
        assert 1 in mix_interval
        assert 99 in mix_interval
        assert 401 in mix_interval
        assert 499 in mix_interval

        mix_interval = mSetCombine(interval1, interval2,{2000}, complement=True)
        assert 2000 not in mix_interval
        assert 2001 in mix_interval
        assert 1999 in mix_interval
        assert 0 in mix_interval
        assert 100 in mix_interval
        assert 400 in mix_interval
        assert 500 in mix_interval

        #mix with other intersection sets
        interval1 = mSetInterval((0,True), (100,True))  # open interval
        interval2 = mSetInterval((50,True), (500,True))  # open interval
        interval3 = mSetInterval((0,True), (70,True))  # open interval
        interval4 = mSetInterval((75,True), (200,True))  # open interval
        mix_interval = mSetCombine(interval3, interval4)

        mix_interval2 = mSetCombine(interval1, interval2,mix_interval,False)
        assert all(mix_interval2.iter_in([51.69,76,99 ]))
        assert 50 not in mix_interval2
        assert 70 not in mix_interval2
        assert 75 not in mix_interval2
        assert 100 not in mix_interval2

        mix_interval3 = mSetCombine({100,50,1,900}, mix_interval2)
        assert all(mix_interval2.iter_in([51.69, 76, 99]))
        assert 100 in mix_interval3
        assert 50 in mix_interval3
        assert 1 in mix_interval3
        assert 900 in mix_interval3
        assert 70 not in mix_interval2
        assert 75 not in mix_interval2
        mix_interval4 = mSetCombine({100,50,1,900}, mix_interval2,mix_interval)
        assert 70 not in mix_interval4
        assert 1  in mix_interval4
        assert 69 in mix_interval4
        assert 75 not in mix_interval4
        assert 76 in mix_interval4
        assert 199 in mix_interval4
        assert 200 not in mix_interval4

        #use vars
        interval1 = mSetInterval(('a',True),(100,True))  # open interval
        interval2 = mSetInterval((50,True), ('b',True))  # open interval
        mix_interval = mSetCombine({100,50,1,900}, interval1,interval2)
        assert mix_interval.vars == {'a','b'}
        assert mix_interval.has_vars
        assert 100 in mix_interval
        #assert 60 not in mix_interval
        assert (60,{'b':61,'a':1000}) in mix_interval
        interval3 = mSetInterval('c', 10)  # open interval
        interval4 = mSetInterval(-1, 'd')  # open interval
        mix_interval2 = mSetCombine({100, 50, 2, 900}, interval3, interval4,False)
        assert mix_interval2.vars == {'c','d'}
        assert mix_interval2.has_vars
        #assert 2 not in mix_interval2
        assert (2,{'c':-10,'d':1.9}) not in mix_interval2
        assert (2, {'c': -10,
                      'd':100}) in mix_interval2
        mix_interval3=mSetCombine(mix_interval,mix_interval2)
        assert mix_interval3.vars == {'a','b','c', 'd'}
        assert mix_interval3.has_vars
        assert 100 in mix_interval3
        assert (-100, {'a':-1000} )in mix_interval3
        assert (-100, {'a':-1000} )in mix_interval3
        #assert 2 not in mix_interval3
        assert (2, {'c': -10,
                      'd':100}) in mix_interval3

        print('\nRESULT TEST: iTIntersectionSets -> PASS')
