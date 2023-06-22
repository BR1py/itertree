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
#from itertree import *
#from itertree.itree_helpers import *
from itertree.itree_mathsets import  *

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

class Test1_MathSets_mSetItem():

    def test1_instance_values(self):

        print('\nRUN TEST: mSetItem instance values')
        item=mSetItem(1)
        assert item.value==1
        assert type(item.value) is int
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr()=='1'
        assert item.get_init_args()==(1,)

        item = mSetItem(1.1)
        assert item.value == 1.1
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '1.1'
        assert item.get_init_args() == (1.1,)

        item = mSetItem(-1.1)
        assert item.value == -1.1
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-1.1'
        assert item.get_init_args() == (-1.1,)

        item = mSetItem(-1.1e-1)
        assert item.value == -0.11
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-0.11'
        assert item.get_init_args() == (-0.11,)

        item = mSetItem(float('-inf'))
        assert item.value == float('-inf')
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-inf'
        assert item.get_init_args() == (float('-inf'),)

        item = mSetItem(float('inf'))
        assert item.value == float('inf')
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == 'inf'
        assert item.get_init_args() == (float('inf'),)

        item = mSetItem(float('+inf'))
        assert item.value == float('inf')
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == 'inf'
        assert item.get_init_args() == (float('inf'),)

        item = mSetItem('abc_var')
        assert item.value == 'abc_var'
        assert type(item.value) is str
        assert not item.is_complement
        assert item.is_var
        assert item.math_repr() == 'abc_var'
        assert item.get_init_args() == ('abc_var',)

        item = mSetItem('var1')
        assert item.value == 'var1'
        assert type(item.value) is str
        assert not item.is_complement
        assert item.is_var
        assert item.math_repr() == 'var1'
        assert item.get_init_args() == ('var1',)

        # invalid vars
        with pytest.raises(TypeError):
            item = mSetItem('abc var')
        with pytest.raises(TypeError):
            item = mSetItem('1abc')
        with pytest.raises(TypeError):
            item = mSetItem('!abc')
        with pytest.raises(TypeError):
            item = mSetItem((1,2,3))

        #named parameters
        item = mSetItem(value='var1')
        assert item.value == 'var1'
        assert type(item.value) is str
        assert not item.is_complement
        assert item.is_var
        assert item.math_repr() == 'var1'
        assert item.get_init_args() == ('var1',)

        with pytest.raises(TypeError):
            item = mSetItem(1,value=10)

        print('\nRESULT TEST: mSetItem instance values -> PASS')

    def test2_instance_values_via_str(self):

        print('\nRUN TEST: mSetItem instance values via str')
        item=mSetItem('1')
        assert item.value==1
        assert type(item.value) is int
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr()=='1'
        assert item.get_init_args()==(1,)

        item = mSetItem('1.1')
        assert item.value == 1.1
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '1.1'
        assert item.get_init_args() == (1.1, False, '{:1.1f}')

        item = mSetItem('-1.1')
        assert item.value == -1.1
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-1.1'
        assert item.get_init_args() == (-1.1, False, '{:1.1f}')

        item = mSetItem('-1.1e1')
        assert item.value == -11
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-1.1e+01'
        assert item.get_init_args() == (-11, False, '{:1.1e}')

        item = mSetItem('-1.11e-01')
        assert item.value == -0.111
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-1.11e-01'
        assert item.get_init_args() == (-0.111, False, '{:1.2e}')

        item = mSetItem('01.11E+01')
        assert item.value == 11.1
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '1.11e+01'
        assert item.get_init_args() == (11.1, False, '{:2.2e}')

        item = mSetItem('-inf')
        assert item.value == float('-inf')
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-inf'
        assert item.get_init_args() == (float('-inf'),)

        item = mSetItem('inf')
        assert item.value == float('inf')
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == 'inf'
        assert item.get_init_args() == (float('inf'),)

        item = mSetItem('+inf')
        assert item.value == float('inf')
        assert type(item.value) is float
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == 'inf'
        assert item.get_init_args() == (float('inf'),)

        item = mSetItem(' 0x123 ')
        assert item.value == 0x123
        assert type(item.value) is int
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '0x123'
        assert item.get_init_args() == (0x123,False,hex)

        item = mSetItem(' 0o123 ')
        assert item.value == 0o123
        assert type(item.value) is int
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '0o123'
        assert item.get_init_args() == (0o123,False,oct)

        item = mSetItem(' 0b101010 ')
        assert item.value == 0b101010
        assert type(item.value) is int
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '0b101010'
        assert item.get_init_args() == (0b101010,False,bin)

        item = mSetItem(' - 0x123 ')
        assert item.value == -0x123
        assert type(item.value) is int
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-0x123'
        assert item.get_init_args() == (-0x123,False,hex)

        item = mSetItem(' -0o123 ')
        assert item.value == -0o123
        assert type(item.value) is int
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-0o123'
        assert item.get_init_args() == (-0o123,False,oct)

        item = mSetItem(' -0b101010 ')
        assert item.value == -0b101010
        assert type(item.value) is int
        assert not item.is_complement
        assert not item.is_var
        assert item.math_repr() == '-0b101010'
        assert item.get_init_args() == (-0b101010,False,bin)

        print('\nRESULT TEST: mSetItem instance values via str-> PASS')

    def test3_complement(self):
        print('\nRUN TEST: mSetItem complement')

        item = mSetItem(123)
        assert not item.is_complement
        assert item.get_init_args() == (123,)
        item = mSetItem(123,True)
        assert item.is_complement
        assert item.get_init_args() == (123,True)


        item = mSetItem(456,True)
        assert item.is_complement
        assert item.get_init_args() == (456, True)

        item = mSetItem(456)
        assert not item.is_complement
        assert item.get_init_args() == (456,)

        print('\nRESULT TEST: mSetItem complement-> PASS')

    def test4_formatter(self):
        print('\nRUN TEST: mSetItem complement')

        item = mSetItem(123,formatter=bin)
        assert item.formatter is bin
        assert item.formatter_type == 0 # _CALL
        assert item.math_repr() == bin(123)
        assert item.math_repr(hex) == hex(123)

        with pytest.raises(TypeError):
            item = mSetItem(123.123, formatter=int)

        item = mSetItem(123.123, formatter='{:2.2f}')
        assert item.math_repr() == '{:2.2f}'.format(123.123)

        item = mSetItem(123.123, formatter='%02.2e')
        assert item.math_repr() == '%02.2e'%(123.123)

        print('\nRESULT TEST: mSetItem formatter-> PASS')

    def test5_other_methods(self):
        print('\nRUN TEST: mSetItem other methods')
        # comparisons: greater and etc.
        item1 = mSetItem(1)
        item2 = mSetItem(1)
        item3 = mSetItem(2)
        assert item1 ==1
        assert item1 == item2
        assert item1 <= item2
        assert item1 >= item2
        assert item1 !=2
        assert item1 != item3
        assert item1 <= 2
        assert item1 <= item3
        assert not item1 >= item3
        assert not item1 >= 2
        assert item3 >= item1
        assert 2 >= item1
        assert item1 < item3
        assert item1 < 2
        assert not item1 > item3
        assert not item1 > 2
        assert item3 > item1
        assert 2 > item1
        assert not item3 < item1
        assert not 2 < item1

        # repr/str
        assert repr(item1)=='mSetItem(1)'
        item=mSetItem(1.234,formatter='{:1.2f}')
        assert repr(item) == "mSetItem(1.234, False, '{:1.2f}')"
        assert str(item) == "mSetItem(1.23, False, '{:1.2f}')"

        item = mSetItem('abc', formatter='{:1.2f}')
        assert repr(item) == "mSetItem('abc', False, '{:1.2f}')"
        assert str(item) == "mSetItem('abc', False, '{:1.2f}')"

        print('\nRESULT TEST: mSetItem other methods-> PASS')


class Test2_MathSets_mSetInterval():

    def test1_instance_numerical_values(self):
        print('\nRUN TEST: mSetInterval normal numerical values')

        i=mSetInterval(1,2)
        for interval in [mSetInterval(2,1),
                        mSetInterval(1,upper=2),
                        mSetInterval(lower=1,upper=2),
                        mSetInterval(lower=2, upper=1),
                        ]:
            assert interval==i
        assert i.lower_value==1
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 2
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem(1),mSetItem(2))
        assert i.math_repr()=='[1,2]'
        assert repr(i)=='mSetInterval(mSetItem(1), mSetItem(2))'
        assert str(i) == "mSetInterval('[1,2]')"
        # contains
        assert 0.9999 not in i
        assert 1 in i
        assert 2 in i
        assert 2.1111 not in i
        # call
        assert not i(0.9999)
        assert i(1)
        assert i(2)
        assert not i(2.1111)
        # iter_in
        assert list(i.iter_in([0.9999,1,2,2.11]))==[False,True,True,False]
        assert list(i.filter([0.9999, 1, 2, 2.11])) == [1,2]

        i=mSetInterval(-1) # upper = inf!
        #other defintions with same result
        for interval in [mSetInterval(-1,None),
                        mSetInterval(-1,float('inf')),
                        mSetInterval(lower=-1),
                        mSetInterval(-1,upper=None),
                        mSetInterval(-1, upper=float('inf')),
                        mSetInterval(float('inf'),-1), # auto switch
                        mSetInterval(float('inf'),upper=-1), # auto switch
                        mSetInterval(lower=float('inf'), upper=-1),  # auto switch
                        ]:
            assert interval==i

        assert i.lower_value==-1
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == float('inf')
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem(-1),mSetItem(float('inf')))
        assert i.math_repr()=='[-1,inf]'
        assert repr(i)=="mSetInterval(mSetItem(-1), mSetItem('inf'))"
        assert str(i) == "mSetInterval('[-1,inf]')"
        # contains
        assert -1.1111not in i
        assert -1 in i
        assert 2000000 in i
        # call
        assert not i(-1.1111)
        assert i(-1)
        assert i(200000)
        # iter_in
        assert list(i.iter_in([-1.111,-1,2,2.11]))==[False,True,True,True]
        assert list(i.filter([-1.111, -1, 2, 2.11])) == [-1,2,2.11]

        i=mSetInterval(None,2) # lower = -inf!
        for interval in [mSetInterval(2,float('-inf')),
                        mSetInterval(float('-inf'),2),
                        mSetInterval(lower=None,upper=2),
                        mSetInterval(lower=2,upper=float('-inf')),
                         mSetInterval(mSetItem(2), mSetItem(float('-inf'))),
                         mSetInterval(mSetItem(float('-inf')), mSetItem(2)),
                         mSetInterval(lower=None, upper=mSetItem(2)),
                         mSetInterval(lower=mSetItem(2), upper=mSetItem(float('-inf'))),
                         mSetInterval((2,), (float('-inf'),)),
                         mSetInterval((float('-inf'),0), (2,0)),
                         mSetInterval(lower=None, upper=(2,)),
                         mSetInterval(lower=(2,), upper=(float('-inf'),)),
                         ]:
            assert interval==i
        assert i.lower_value==float('-inf')
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 2
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem('-inf'),mSetItem(2))
        assert i.math_repr()=='[-inf,2]'
        assert repr(i)=="mSetInterval(mSetItem('-inf'), mSetItem(2))"
        assert str(i) == "mSetInterval('[-inf,2]')"
        # contains
        assert -1.1111 in i
        assert -1 in i
        assert 2 in i
        assert 2.000001 not in i

        # call
        assert i(-1.1111)
        assert i(-1)
        assert i(2)
        assert not i(2.000001)
        # iter_in
        assert list(i.iter_in([-1.111,-1,2,2.11]))==[True,True,True,False]
        assert list(i.filter([-1.111, -1, 2, 2.11])) == [-1.111,-1,2]

        print('\nRESULT TEST: mSetInterval normal numerical values-> PASS')

    def test2_instance_numerical_values_open(self):
        print('\nRUN TEST: mSetInterval normal numerical values open interval')

        i=mSetInterval((1,True),(2,True))
        for interval in [mSetInterval((2,True),(1,True)),
                        mSetInterval((1,1),upper=(2,1)),
                        mSetInterval(lower=mSetItem(1,True),upper=mSetItem(2,True)),
                        mSetInterval(lower=(2,1), upper=(1,1))
                        ]:
            assert interval==i
        assert i.lower_value==1
        assert i.is_lower_closed is False
        assert i.is_lower_open is True
        assert i.upper_value == 2
        assert i.is_upper_closed is False
        assert i.is_upper_open is True
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem(1,True), mSetItem(2,True))
        assert i.math_repr()=='(1,2)'
        assert repr(i)=='mSetInterval(mSetItem(1, True), mSetItem(2, True))'
        assert str(i) == "mSetInterval('(1,2)')"
        # contains
        assert 0.9999 not in i
        assert 1 not in i
        assert 1.00001 in i
        assert 1.9999999 in i
        assert 2 not in i
        assert 2.1111 not in i
        # call
        assert not i(0.9999)
        assert not i(1)
        assert i(1.00001)
        assert i(1.9999999)
        assert not i(2)
        assert not i(2.1111)
        # iter_in
        assert list(i.iter_in([0.9999,1,1.000001,1.99999,2,2.11]))==[False,False,True,True,False,False]
        assert list(i.filter([0.9999, 1,1.000001,1.99999, 2, 2.11])) == [1.000001,1.99999]

        i=mSetInterval((-1,True)) # upper = inf!
        #other defintions with same result
        for interval in [mSetInterval((-1,1),None),
                        mSetInterval((-1,True),float('inf')),
                        mSetInterval(lower=(-1,True)),
                        mSetInterval((-1,True),upper=None),
                        mSetInterval((-1,True), upper=float('inf')),
                        mSetInterval(float('inf'),(-1,True)), # auto switch
                        mSetInterval(float('inf'),upper=(-1,True)), # auto switch
                        mSetInterval(lower=float('inf'), upper=(-1,True)),  # auto switch
                        ]:
            assert interval==i

        assert i.lower_value==-1
        assert i.is_lower_closed is False
        assert i.is_lower_open is True
        assert i.upper_value == float('inf')
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem(-1,True),mSetItem(float('inf')))
        assert i.math_repr()=='(-1,inf]'
        assert repr(i)=="mSetInterval(mSetItem(-1, True), mSetItem('inf'))"
        assert str(i) == "mSetInterval('(-1,inf]')"
        # contains
        assert -1.1111 not in i
        assert -1 not in i
        assert -0.99999 in i
        assert 2000000 in i
        # call
        assert not i(-1.1111)
        assert not i(-1)
        assert i(0.999)
        assert i(200000)
        # iter_in
        assert list(i.iter_in([-1.111,-1,-0.9999,2,2.11]))==[False,False,True,True,True]
        assert list(i.filter([-1.111, -1,-0.999, 2, 2.11])) == [-0.999,2,2.11]

        i=mSetInterval(None,(2,True)) # lower = -inf!
        for interval in [mSetInterval((2,True),float('-inf')),
                        mSetInterval(float('-inf'),(2,True)),
                        mSetInterval(lower=None,upper=(2,True)),
                        mSetInterval(lower=(2,True),upper=float('-inf')),
                         mSetInterval(mSetItem(2,True), mSetItem(float('-inf'))),
                         mSetInterval(mSetItem(float('-inf')), mSetItem(2,True)),
                         mSetInterval(lower=None, upper=mSetItem(2,True)),
                         mSetInterval(lower=mSetItem(2,True), upper=mSetItem(float('-inf'))),
                         mSetInterval((2,1), (float('-inf'),)),
                         mSetInterval((float('-inf'),), (2,1)),
                         mSetInterval(lower=None, upper=(2,1)),
                         mSetInterval(lower=(2,1), upper=(float('-inf'),)),
                         ]:
            assert interval==i
        assert i.lower_value==float('-inf')
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 2
        assert i.is_upper_closed is False
        assert i.is_upper_open is True
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem('-inf'),mSetItem(2,True))
        assert i.math_repr()=='[-inf,2)'
        assert repr(i)=="mSetInterval(mSetItem('-inf'), mSetItem(2, True))"
        assert str(i) == "mSetInterval('[-inf,2)')"
        # contains
        assert -1.1111 in i
        assert -1 in i
        assert 1.999 in i
        assert 2 not in i
        assert 2.000001 not in i

        # call
        assert i(-1.1111)
        assert i(-1)
        assert i(1.999)
        assert not i(2)
        assert not i(2.000001)
        # iter_in
        assert list(i.iter_in([1.999,-1.111,-1,2,2.11]))==[True,True,True,False,False]
        assert list(i.filter([1.999,-1.111, -1, 2, 2.11])) == [1.999,-1.111,-1]

        print('\nRESULT TEST: mSetImterval normal numerical values open interval-> PASS')

    def test3_instance_numerical_values_mixed_complement(self):
        print('\nRUN TEST: mSetInterval numerical values complement interval')

        i=mSetInterval((1,True),(2),complement=True)
        assert i.lower_value==1
        assert i.is_lower_closed is False
        assert i.is_lower_open is True
        assert i.upper_value == 2
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is False
        assert i.is_complement is True
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem(1,True), mSetItem(2,False),False,True)
        assert i.math_repr()=='!(1,2]'
        assert repr(i)=='mSetInterval(mSetItem(1, True), mSetItem(2), False, True)'
        assert str(i) == "mSetInterval('!(1,2]')"
        # contains

        assert 0.9999 in i
        assert 1 in i
        assert 1.00001 not in i
        assert 1.9999999 not in i
        assert 2 not in i
        assert 2.1111 in i
        # call
        assert i(0.9999)
        assert i(1)
        assert not i(1.00001)
        assert not i(1.9999999)
        assert not i(2)
        assert i(2.1111)
        # iter_in
        assert list(i.iter_in([0.9999,1,1.000001,1.99999,2,2.11]))==[True,True,False,False,False,True]
        assert list(i.filter([0.9999, 1,1.000001,1.99999, 2, 2.11])) == [0.9999, 1,2.11]

        i=mSetInterval((1),(2,True),complement=True)
        assert i.lower_value==1
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 2
        assert i.is_upper_closed is False
        assert i.is_upper_open is True
        assert i.is_int_only is False
        assert i.is_complement is True
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem(1,False), mSetItem(2,True),False,True)
        assert i.math_repr()=='![1,2)'
        assert repr(i)=='mSetInterval(mSetItem(1), mSetItem(2, True), False, True)'
        assert str(i) == "mSetInterval('![1,2)')"
        # contains
        assert 0.9999 in i
        assert 1 not in i
        assert 1.00001 not in i
        assert 1.9999999 not in i
        assert 2  in i
        assert 2.1111 in i
        # call
        assert i(0.9999)
        assert not i(1)
        assert not i(1.00001)
        assert not i(1.9999999)
        assert  i(2)
        assert i(2.1111)
        # iter_in
        assert list(i.iter_in([0.9999,1,1.000001,1.99999,2,2.11]))==[True,False,False,False,True,True]
        assert list(i.filter([0.9999, 1,1.000001,1.99999, 2, 2.11])) == [0.9999, 2,2.11]

        print('\nRESULT TEST: mSetInterval numerical values complement interval-> PASS')

    def test4_instance_single_and_empty_sets_for_floats(self):
        print('\nRUN TEST: mSetInterval single and empty sets for floats')

        #single value
        i=mSetInterval((1),(1,True))
        assert i.lower_value==1
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 1
        assert i.is_upper_closed is False
        assert i.is_upper_open is True
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==1
        assert i.get_init_args()==(mSetItem(1,False), mSetItem(1,True))
        assert i.math_repr()=='[1,1)'
        assert repr(i)=='mSetInterval(mSetItem(1), mSetItem(1, True))'
        assert str(i) == "mSetInterval('[1,1)')"
        # contains
        assert 0.9999 not in i
        assert 1 in i
        assert 1.00001 not in i

        assert not i(0.9999)
        assert i(1)
        assert not i(1.00001)

        # iter_in
        assert list(i.iter_in([0.9999,1,1.000001]))==[False,True,False]
        assert list(i.filter([0.9999, 1,1.000001])) == [1]

        #empty set
        i=mSetInterval((1,True),(1,True))
        assert i.lower_value==1
        assert i.is_lower_closed is False
        assert i.is_lower_open is True
        assert i.upper_value == 1
        assert i.is_upper_closed is False
        assert i.is_upper_open is True
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is True
        assert i.is_empty_set_complement is False
        assert i.cardinality ==0
        assert i.get_init_args()==(mSetItem(1,True), mSetItem(1,True))
        assert i.math_repr()=='(1,1)'
        assert repr(i)=='mSetInterval(mSetItem(1, True), mSetItem(1, True))'
        assert str(i) == "mSetInterval('(1,1)')"
        # contains
        assert 0.9999 not in i
        assert 1 not in i
        assert 1.00001 not in i

        assert not i(0.9999)
        assert not i(1)
        assert not i(1.00001)

        # iter_in
        assert list(i.iter_in([0.9999,1,1.000001]))==[False,False,False]
        assert list(i.filter([0.9999, 1,1.000001])) == []

        #fullset
        i=mSetInterval((1,True),(1,True),False,True)
        assert i.lower_value==1
        assert i.is_lower_closed is False
        assert i.is_lower_open is True
        assert i.upper_value == 1
        assert i.is_upper_closed is False
        assert i.is_upper_open is True
        assert i.is_int_only is False
        assert i.is_complement is True
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is True
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem(1,True), mSetItem(1,True),False,True)
        assert i.math_repr()=='!(1,1)'
        assert repr(i)=='mSetInterval(mSetItem(1, True), mSetItem(1, True), False, True)'
        assert str(i) == "mSetInterval('!(1,1)')"
        # contains
        assert 0.9999 in i
        assert 1 in i
        assert 1.00001 in i

        assert i(0.9999)
        assert i(1)
        assert i(1.00001)

        # iter_in
        assert list(i.iter_in([0.9999,1,1.000001]))==[True,True,True]
        assert list(i.filter([0.9999, 1,1.000001])) == [0.9999,1,1.000001]

        print('\nRESULT TEST: mSetInterval single and empty sets for floats-> PASS')



    def test5_instance_numerical_values_integers_only(self):
        print('\nRUN TEST: mSetInterval normal numerical values integer interval')

        i=mSetInterval(1,2,True)
        assert i.lower_value==1
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 2
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is True
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==2
        assert len(list(i))==2 # iterator
        assert i.get_init_args()==(mSetItem(1),mSetItem(2),True)
        assert i.math_repr()=='[1..2]'
        assert repr(i)=='mSetInterval(mSetItem(1), mSetItem(2), True)'
        assert str(i) == "mSetInterval('[1..2]')"
        # contains
        assert 0 not in i
        assert 0.9999 not in i
        assert 1 in i
        assert 1.5 not in i
        assert 2 in i
        assert 2.1111 not in i
        assert 3 not in i

        # call
        assert not i(0)
        assert  not i(0.9999)
        assert i(1)
        assert not i(1.5)
        assert i(2)
        assert  not  i(2.1111)
        assert not  i(3)
        # iter_in
        assert list(i.iter_in([0,0.9999,1,1.5,2,2.11,3]))==[False,False,True,False,True,False,False]
        assert list(i.filter([0,0.9999, 1,1.5, 2, 2.11,3])) == [1,2]


        i=mSetInterval(-1,int_only=True) # upper = inf!
        assert i.lower_value==-1
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == float('inf')
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is True
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert len(list(i)) == 0  # iterator
        assert i.get_init_args()==(mSetItem(-1),mSetItem(float('inf')),True)
        assert i.math_repr()=='[-1..inf]'
        assert repr(i)=="mSetInterval(mSetItem(-1), mSetItem('inf'), True)"
        assert str(i) == "mSetInterval('[-1..inf]')"
        # contains
        assert -1.1111not in i
        assert -1 in i
        assert 2000000 in i
        assert 50000.1 not in i

        # call
        assert not i(-1.1111)
        assert i(-1)
        assert i(200000)
        assert not i(50000.1)

        # iter_in
        assert list(i.iter_in([-1.111,-1,2,2.11]))==[False,True,True,False]
        assert list(i.filter([-1.111, -1, 2, 2.11])) == [-1,2]

        i=mSetInterval(None,2,True) # lower = -inf!
        assert i.lower_value==float('-inf')
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 2
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is True
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert len(list(i)) == 0  # iterator

        assert i.get_init_args()==(mSetItem('-inf'),mSetItem(2),True)
        assert i.math_repr()=='[-inf..2]'
        assert repr(i)=="mSetInterval(mSetItem('-inf'), mSetItem(2), True)"
        assert str(i) == "mSetInterval('[-inf..2]')"
        # contains
        assert -1.1111 not in i
        assert -1 in i
        assert 2 in i
        assert 2.000001 not in i

        # call
        assert not i(-1.1111)
        assert i(-1)
        assert i(2)
        assert not i(2.000001)
        # iter_in
        assert list(i.iter_in([-1.111,-1,2,2.11]))==[False,True,True,False]
        assert list(i.filter([-1.111, -1, 2, 2.11])) == [-1,2]

        # some tests related cardinality and empty sets
        i = mSetInterval((1, True), (2, True), True)
        assert i.cardinality == 0
        assert i.is_empty_set
        assert not i.is_empty_set_complement
        assert 1.5 not in i
        assert 1 not in i
        assert 2 not in i

        i=mSetInterval((1,True),(2,True),True,True)
        assert i.cardinality==float('inf')
        assert not i.is_empty_set
        assert i.is_empty_set_complement
        assert 1.5 in i
        assert 1 in i
        assert 2 in i
        assert -10000 in i
        assert Decimal(10000) in i

        i = mSetInterval((1, True), (2, False), True)
        assert i.cardinality == 1
        assert len(list(i)) == 1  # iterator

        assert not i.is_empty_set
        assert not i.is_empty_set_complement
        assert 2 in i
        assert 2.1 not in i
        assert 1 not in i
        i.switch_complement()
        assert 2 not in i
        assert 2.1 in i
        assert 1 in i

        i = mSetInterval((1, False), (3, False), True)
        assert i.cardinality == 3
        assert len(list(i)) == 3  # iterator

        assert not i.is_empty_set
        assert not i.is_empty_set_complement
        assert 1 in i
        assert 1.5 not in i
        assert 2 in i
        assert 3 in i
        assert 4 not in i

        i = mSetInterval((1, False), (2, True), True)
        assert i.cardinality == 1
        assert len(list(i)) == 1  # iterator
        assert not i.is_empty_set
        assert not i.is_empty_set_complement
        assert 1 in i
        assert 2 not in i

        i = mSetInterval((1, False), (1, True), True)
        assert i.cardinality == 1
        assert not i.is_empty_set
        assert not i.is_empty_set_complement
        assert 1 in i

        i = mSetInterval((1, False), (1, False), True)
        assert i.cardinality == 1
        assert not i.is_empty_set
        assert not i.is_empty_set_complement
        assert 1 in i

        i = mSetInterval((1, True), (1, False), True)
        assert i.cardinality == 1
        assert not i.is_empty_set
        assert not i.is_empty_set_complement
        assert 1 in i

        i = mSetInterval((1, True), (1, True), True)
        assert i.cardinality == 0
        assert i.is_empty_set
        assert not i.is_empty_set_complement
        assert 1 not in i

        i = mSetInterval((1, True), (1, True), True,True)
        assert i.cardinality == float('inf')
        assert not i.is_empty_set
        assert i.is_empty_set_complement
        assert 1 in i
        assert 1.2342314 in i
        assert -12391238 in i

        print('\nRESULT TEST: mSetInterval normal numerical values integer interval->PASS')


    def test7_instance_variable_limits(self):
        print('\nRUN TEST: mSetInterval variable limits')

        i=mSetInterval('var1',2)
        assert i.has_vars
        assert i.vars=={'var1'}
        assert i.lower_value=='var1'
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 2
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem('var1'),mSetItem(2))
        assert i.math_repr()=='[var1,2]'
        assert repr(i)=="mSetInterval(mSetItem('var1'), mSetItem(2))"
        assert str(i) == "mSetInterval('[var1,2]')"

        with pytest.raises(TypeError):
            assert 1 not in i
        assert (1,{'var1':-1}) in i
        with pytest.raises(TypeError):
            assert (1, {'var2': -1}) not in i
        assert (1, {'var1': 1}) in i

        i=mSetInterval('var1','var1')
        assert i.has_vars
        assert i.vars=={'var1'}
        assert i.lower_value=='var1'
        assert i.is_lower_closed is True
        assert i.is_lower_open is False
        assert i.upper_value == 'var1'
        assert i.is_upper_closed is True
        assert i.is_upper_open is False
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==1
        assert i.get_init_args()==(mSetItem('var1'),mSetItem('var1'))
        assert i.math_repr()=='[var1,var1]'
        assert repr(i)=="mSetInterval(mSetItem('var1'), mSetItem('var1'))"
        assert str(i) == "mSetInterval('[var1,var1]')"

        with pytest.raises(TypeError):
            assert 1 not in i
        assert (-1,{'var1':-1}) in i
        with pytest.raises(TypeError):
            assert (1, {'var2': -1}) not in i
        assert (2, {'var1': 1}) not in i

        i=mSetInterval(('var1',True),('var2',True))
        assert i.has_vars
        assert i.vars=={'var1','var2'}
        assert i.lower_value=='var1'
        assert i.is_lower_closed is False
        assert i.is_lower_open is True
        assert i.upper_value == 'var2'
        assert i.is_upper_closed is False
        assert i.is_upper_open is True
        assert i.is_int_only is False
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.cardinality ==float('inf')
        assert i.get_init_args()==(mSetItem('var1',True),mSetItem('var2',True))
        assert i.math_repr()=='(var1,var2)'
        assert repr(i)=="mSetInterval(mSetItem('var1', True), mSetItem('var2', True))"
        assert str(i) == "mSetInterval('(var1,var2)')"

        with pytest.raises(TypeError):
            assert 1 not in i
        assert list(i.iter_in([-1.1,-1,-0.9,1.9,2,2.1],{'var1':-1,'var2':2})) ==[False,False,True,True,False,False]
        with pytest.raises(TypeError):
            assert list(i.iter_in([-1.1, -1, -0.9, 1.9, 2, 2.1], {'var2': 2})) == [False, False, True, True,
                                                                                         False, False]
        print('\nRESULT TEST: mSetInterval variable limits->PASS')

class Test1_MathSets_mSetIntervalParser():

    def test1_math_set_repr_def_str(self):

        print('\nRUN TEST: mSetInterval normal def parser')
        i=mSetInterval('[1,2]')
        assert i.get_init_args()==(mSetItem(1),mSetItem(2))
        i = mSetInterval('(1,2]')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2))
        i = mSetInterval('[1,2)')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2,True))
        i = mSetInterval('(1,2)')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2,True))
        #is_int and we add some spaces
        i = mSetInterval(' [ 1 .. 2 ]')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2),True)
        i = mSetInterval('(1..2]')
        assert i.get_init_args() == (mSetItem(1, True), mSetItem(2),True)
        i = mSetInterval(' [ 1 .. 2)')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2, True),True)
        i = mSetInterval('( 1 .. 2)')
        assert i.get_init_args() == (mSetItem(1, True), mSetItem(2, True),True)
        # complements
        i = mSetInterval('![1,2]')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2),False,True)
        i = mSetInterval('!(1,2]')
        assert i.get_init_args() == (mSetItem(1, True), mSetItem(2),False,True)
        i = mSetInterval('![1,2)')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2, True),False,True)
        i = mSetInterval('!(1,2)')
        assert i.get_init_args() == (mSetItem(1, True), mSetItem(2, True),False,True)
        i = mSetInterval('[1,2]\'')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2),False,True)
        i = mSetInterval('(1,2]\'')
        assert i.get_init_args() == (mSetItem(1, True), mSetItem(2),False,True)
        i = mSetInterval('[1,2)\'')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2, True),False,True)
        i = mSetInterval('(1,2)\'')
        assert i.get_init_args() == (mSetItem(1, True), mSetItem(2, True),False,True)
        # two times complement does nothing
        i = mSetInterval('![1,2]\'')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2))
        i = mSetInterval('!(1,2]\'')
        assert i.get_init_args() == (mSetItem(1, True), mSetItem(2))
        i = mSetInterval('![1,2)\'')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2, True))
        i = mSetInterval('!(1,2)\'')
        assert i.get_init_args() == (mSetItem(1, True), mSetItem(2, True))

        #alread checked in mSetItems but a short reacheck
        i=mSetInterval('[-inf,2]')
        assert i.get_init_args()==(mSetItem(float('-inf')),mSetItem(2))
        i=mSetInterval('[1,inf]')
        assert i.get_init_args()==(mSetItem(1),mSetItem(float('inf')))
        # variables
        i = mSetInterval('[var1,var2]')
        assert i.get_init_args() == (mSetItem('var1'), mSetItem('var2'))
        # invalid variables
        with pytest.raises(TypeError):
            i = mSetInterval('[var 1,var 2]')
        with pytest.raises(TypeError):
            i = mSetInterval('[1var,2var]')

        print('\nRESULT TEST: mSetInterval normal def parser->PASS')

    def test2_math_set_builder_type_def_str(self):

        print('\nRUN TEST: mSetInterval builder definitions')

        i=mSetInterval('{x| x>=1}')
        assert i.get_init_args() == (mSetItem(1), mSetItem('inf'))
        i=mSetInterval('{x| x>1}')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem('inf'))
        i=mSetInterval('{x| 1<=x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem('inf'))
        i=mSetInterval('{x| 1<x}')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem('inf'))

        i=mSetInterval('{x| x<=-1}')
        assert i.get_init_args() == (mSetItem('-inf'),mSetItem(-1), )
        i=mSetInterval('{x| x<-1}')
        assert i.get_init_args() == (mSetItem('-inf'),mSetItem(-1,True), )
        i=mSetInterval('{x| -1>=x}')
        assert i.get_init_args() == (mSetItem('-inf'),mSetItem(-1), )
        i=mSetInterval('{x| -1>x}')
        assert i.get_init_args() == (mSetItem('-inf'),mSetItem(-1,True), )


        i=mSetInterval('{x| x>=1, x<=2}')
        assert i.get_init_args()==(mSetItem(1),mSetItem(2))
        i = mSetInterval('{x| x>1, x<=2}')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2))
        i = mSetInterval('{x|  x >= 1 , x < 2 }')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2,True))
        i = mSetInterval('{x|  x > 1 , x < 2 }')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2,True))

        i=mSetInterval('{x| 1<=x, 2>=x}')
        assert i.get_init_args()==(mSetItem(1),mSetItem(2))
        i = mSetInterval('{x| 1<x, 2>=x}')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2))
        i = mSetInterval('{x| 1<=x, 2>x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2,True))
        i = mSetInterval('{x| 1<x, 2>x}')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2,True))

        i=mSetInterval('{x| 1<=x<=2}')
        assert i.get_init_args()==(mSetItem(1),mSetItem(2))
        i = mSetInterval('{x| 1 < x <= 2}')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2))
        i = mSetInterval('{x| 1 <= x < 2 }')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2,True))
        i = mSetInterval('{x| 1 < x < 2 }')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2,True))

        i=mSetInterval('{x| 2>=x>=1 }')
        assert i.get_init_args()==(mSetItem(1),mSetItem(2))
        i = mSetInterval('{x| 2>=x>1}')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2))
        i = mSetInterval('{x| 2>x>=1 }')
        assert i.get_init_args() == (mSetItem(1), mSetItem(2,True))
        i = mSetInterval('{x| 2>x>1 }')
        assert i.get_init_args() == (mSetItem(1,True), mSetItem(2,True))

        # variables
        i = mSetInterval('{x| var<=x, 2>=x}')
        assert i.get_init_args() == (mSetItem('var'), mSetItem(2))
        i=mSetInterval('{x| x>=var, x<=2}')
        assert i.get_init_args() == (mSetItem('var'), mSetItem(2))
        i = mSetInterval('{x| 2>=x>=var}')
        assert i.get_init_args() == (mSetItem('var'), mSetItem(2))
        i = mSetInterval('{x| 1<=x, var>=x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem('var'))
        i=mSetInterval('{x| x>=1, x<=var}')
        assert i.get_init_args() == (mSetItem(1), mSetItem('var'))
        i=mSetInterval('{x| var>=x>=1 }')
        assert i.get_init_args() == (mSetItem(1), mSetItem('var'))

        # equal / not equal
        i = mSetInterval('{x| x=1}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1))
        i = mSetInterval('{x| x==1}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1))
        i = mSetInterval('{x| x!=1}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1),False,True)
        i = mSetInterval('{x| x!==1}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1),False,True)
        i = mSetInterval('{x| 1=x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1))
        i = mSetInterval('{x| 1==x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1))
        i = mSetInterval('{x| 1!=x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1),False,True)
        i = mSetInterval('{x| 1!==x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1),False,True)
        i = mSetInterval('{x| my_var==x}')
        assert i.get_init_args() == (mSetItem('my_var'), mSetItem('my_var'))

        # numerical sets
        check_list=['bool','boolean','Boolean']
        for item in check_list:
            i = mSetInterval('{x| x e %s}'%item)
            assert i.get_init_args() == (mSetItem(0), mSetItem(1), True)

        i = mSetInterval('{x| x e N}')
        assert i.get_init_args() == (mSetItem(0), mSetItem(float('inf')), True)
        i = mSetInterval('{x| x e N+}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(float('inf')), True)
        i = mSetInterval('{x| x e N0+}')
        assert i.get_init_args() == (mSetItem(0), mSetItem(float('inf')), True)

        check_list = ['Z', 'int', 'integer','Integer']
        for item in check_list:
            i = mSetInterval('{x| x e %s}'%item)
            assert i.get_init_args() == (mSetItem(float('-inf')), mSetItem(float('inf')), True)
        i = mSetInterval('{x| x e Z}')
        assert i.get_init_args() == (mSetItem(float('-inf')), mSetItem(float('inf')), True)
        i = mSetInterval('{x| x e Z+}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(float('inf')), True)
        i = mSetInterval('{x| x e Z0+}')
        assert i.get_init_args() == (mSetItem(0), mSetItem(float('inf')), True)
        i = mSetInterval('{x| x e Z-}')
        assert i.get_init_args() == (mSetItem(float('-inf')), mSetItem(-1), True)
        i = mSetInterval('{x| x e Z0-}')
        assert i.get_init_args() == (mSetItem(float('-inf')), mSetItem(0), True)

        check_list = ['Q', 'float', 'Float','Double','double','R']
        for item in check_list:
            i = mSetInterval('{x| x e %s}'%item)
            assert i.get_init_args() == (mSetItem(float('-inf')), mSetItem(float('inf')))
        i = mSetInterval('{x| x e Q}')
        assert i.get_init_args() == (mSetItem(float('-inf')), mSetItem(float('inf')))
        i = mSetInterval('{x| x e R}')
        assert i.get_init_args() == (mSetItem(float('-inf')), mSetItem(float('inf')))
        i = mSetInterval('{x| x e Q+}')
        assert i.get_init_args() == (mSetItem(0,True), mSetItem(float('inf')))
        i = mSetInterval('{x| x e R+}')
        assert i.get_init_args() == (mSetItem(0,True), mSetItem(float('inf')))
        i = mSetInterval('{x| x e Q0+}')
        assert i.get_init_args() == (mSetItem(0), mSetItem(float('inf')))
        i = mSetInterval('{x| x e R0+}')
        assert i.get_init_args() == (mSetItem(0), mSetItem(float('inf')))

        i = mSetInterval('{x| x e Q-}')
        assert i.get_init_args() == (mSetItem(float('-inf'),mSetItem(0,True)))
        i = mSetInterval('{x| x e R-}')
        assert i.get_init_args() == (mSetItem(float('-inf'),mSetItem(0,True)))
        i = mSetInterval('{x| x e Q0-}')
        assert i.get_init_args() == (mSetItem(float('-inf'),mSetItem(0)))
        i = mSetInterval('{x| x e R0-}')
        assert i.get_init_args() == (mSetItem(float('-inf'),mSetItem(0)))

        # mix numerical and normal
        i=mSetInterval('{x| x e N, x<=255}')
        assert i.get_init_args() == (mSetItem(0),mSetItem(255),True)
        i=mSetInterval('{x| x<=255,x e N+ }')
        assert i.get_init_args() == (mSetItem(1),mSetItem(255),True)

        #complements
        i = mSetInterval('{x| 1!==x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1), False, True)
        i = mSetInterval('!{x| 1!==x}')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1))
        i = mSetInterval('{x| 1!==x}\'')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1))
        i = mSetInterval('!{x| 1!==x}\'')
        assert i.get_init_args() == (mSetItem(1), mSetItem(1), False, True)


        print('\nRESULT TEST: mSetInterval builder definitions->PASS')

    def test3_math_set_simple_builder_type_def_str(self):

        print('\nRUN TEST: mSetInterval simple builder definitions')

        i=mSetInterval('x<=255')
        assert i.get_init_args() == (mSetItem(float('-inf')),mSetItem(255))
        i = mSetInterval('n<=255')
        assert i.get_init_args() == (mSetItem(float('-inf')), mSetItem(255),True)

        print('\nRESULT TEST: mSetInterval simple builder definitions->PASS')

class Test3_MathSets_mSetRoster():

    def test1_math_set_instance(self):

        print('\nRUN TEST: mSetRoster instance')
        i=mSetRoster(1,2,3,4)
        assert i==mSetRoster(items={1,2,3,4})
        assert i == mSetRoster(items=[4,3,2,1])
        assert i == mSetRoster(items=[mSetItem(4), 3, 2, 1])
        assert i == mSetRoster('{ 1, 2, 3, 4}')

        assert i.get_init_args()==(mSetItem(1),mSetItem(2),mSetItem(3),mSetItem(4))
        assert i.has_vars is False
        assert i.vars==set()
        assert i.cardinality == 4
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert tuple(i.items())== i.get_init_args()
        assert i.math_repr()== '{1,2,3,4}'

        assert 1 in i
        assert i(1)

        assert 2 in i
        assert 3 in i
        assert 4 in i
        assert 0 not in i
        assert not i(0)
        assert 1.5 not in i
        assert list(i.iter_in([2,3,4,1,5,0,1.5]))==[True,True,True,True,False,False,False]
        assert list(i.filter([2, 3, 4, 1, 5, 0, 1.5])) == [2,3,4,1]

        i=mSetRoster()
        assert i == mSetRoster(' {  } ')
        assert i.get_init_args()==tuple()
        assert i.has_vars is False
        assert i.vars==set()
        assert i.cardinality == 0
        assert i.is_complement is False
        assert i.is_empty_set is True
        assert i.is_empty_set_complement is False
        assert tuple(i.items())== i.get_init_args()
        assert i.math_repr()== '{}'
        assert 1 not in i
        assert 2 not in i
        assert 3 not in i
        assert 4 not in i
        assert 0 not in i
        assert 1.5 not in i
        assert list(i.iter_in([2,3,4,1,5,0,1.5]))==[False,False,False,False,False,False,False]
        assert list(i.filter([2, 3, 4, 1, 5, 0, 1.5])) == []

        i = mSetRoster(True)
        assert i==mSetRoster(complement=True)
        assert i == mSetRoster('!{}')
        assert i.get_init_args() == (True,)
        assert i.has_vars is False
        assert i.vars == set()
        assert i.cardinality == float('inf')
        assert i.is_complement is True
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is True
        assert tuple(i.items()) == i.get_init_args()[:-1]
        assert i.math_repr() == '!{}'
        assert 1 in i
        assert 2 in i
        assert 3 in i
        assert 4 in i
        assert 0 in i
        assert 1.5 in i
        assert list(i.iter_in([2, 3, 4, 1, 5, 0, 1.5])) == [True,True,True,True,True,True,True]
        assert list(i.filter([2, 3, 4, 1, 5, 0, 1.5])) == [2, 3, 4, 1, 5, 0, 1.5]

        i = mSetRoster('var1')
        assert i == mSetRoster(items=['var1'])
        assert i.get_init_args() == (mSetItem('var1'),)
        assert i.has_vars is True
        assert i.vars == {'var1'}
        assert i.cardinality == 1
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert tuple(i.items()) == i.get_init_args()
        assert i.math_repr() == '{var1}'
        assert 1 not in i
        assert (1.5,{'var1':1.5}) in i
        assert list(i.iter_in([2, 3, 4, 1, 5, 0, 1.5],{'var1':1.5})) == [False,False,False,False,False,False,True]
        assert list(i.filter([2, 3, 4, 1, 5, 0, 1.5],{'var1':1.5})) == [1.5]

        i = mSetRoster('var1','var2',True)
        assert i == mSetRoster(items=['var1','var2'],complement=True)
        assert set(i.get_init_args()) == {mSetItem('var1'),mSetItem('var2'),True} # we use set because the order is not always the same
        assert i.has_vars is True
        assert i.vars == {'var1','var2'}
        assert i.cardinality == float('inf')
        assert i.is_complement is True
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert tuple(i.items()) == i.get_init_args()[:-1]
        assert i.math_repr() == '!{var1,var2}' or i.math_repr() == '!{var2,var1}'
        assert 1 in i
        assert (1.5,{'var1':1.5}) not in i
        assert (1.5, {'var2': 1.5}) not in i
        assert list(i.iter_in([2, 3, 4, 1, 5, 0, 1.5],{'var1':1.5,'var2':0})) == [True,True,True,True,True,False,False]
        assert list(i.filter([2, 3, 4, 1, 5, 0, 1.5],{'var1':1.5,'var2':0})) == [2, 3, 4, 1, 5]

        print('\nRESULT TEST: mSetRoster instance->PASS')

class Test4_MathSets_mSetMixed():

    def test1_math_set_instance(self):

        print('\nRUN TEST: mSetUnion instance')

        i=mSetCombine(mSetRoster(1,2,3),mSetInterval(100,200))
        assert i.has_vars is False
        assert i.vars == set()
        assert i.cardinality == float('inf')
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.get_init_args()==(mSetRoster(1,2,3),mSetInterval(100,200))
        assert tuple(i.items()) == tuple(i.get_init_args())

        assert 1 in i
        assert 2 in i
        assert 3 in i
        assert 100 in i
        assert 100.5 in i
        assert 200 in i
        assert 0 not in i
        assert 99.99999 not in i
        assert 200.00000001 not in i
        assert i.iter_in([0,1,100,200,200.001])==[False,True,True,True,False]
        assert i.filter([0,1,100,200,200.001])==[1,100,200]

        i=mSetCombine(mSetRoster(1,2,3),mSetInterval(100,200),[-1,-2,-100])
        assert i.has_vars is False
        assert i.vars == set()
        assert i.cardinality == float('inf')
        assert i.is_complement is False
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.get_init_args()==(mSetRoster(1,2,3),mSetInterval(100,200),[-1,-2,-100])
        assert tuple(i.items()) == tuple(i.get_init_args())

        assert 1 in i
        assert 2 in i
        assert 3 in i
        assert 100 in i
        assert 100.5 in i
        assert 200 in i
        assert 0 not in i
        assert 99.99999 not in i
        assert 200.00000001 not in i
        assert -1 in i

        assert i.iter_in([-100,0,1,100,200,200.001])==[True,False,True,True,True,False]
        assert i.filter([-100,0,1,100,200,200.001])==[-100,1,100,200]

        i=mSetCombine(mSetRoster(1,2,'var1'),mSetInterval(100,'var1'),[-1,-2,-100],complement=True)
        assert i.has_vars is True
        assert i.vars == {'var1'}
        assert i.cardinality == float('inf')
        assert i.is_complement is True
        assert i.is_empty_set is False
        assert i.is_empty_set_complement is False
        assert i.get_init_args()==(mSetRoster(1,2,'var1'),mSetInterval(100,'var1'),[-1,-2,-100],True,True)
        assert tuple(i.items()) == tuple(i.get_init_args()[:-2])

        assert (1,{'var1':200}) not in i
        assert (2,{'var1':200}) not in i
        assert (3,{'var1':200}) in i
        assert (100,{'var1':200}) not in i
        assert (100.5,{'var1':200}) not in i
        assert (200,{'var1':200}) not in i
        assert (0,{'var1':200}) in i
        assert (99.99999,{'var1':200}) in i
        assert (200.00000001,{'var1':200}) in i
        assert (-1,{'var1':200}) not in i

        assert i.iter_in([-100,0,1,100,200,200.001],{'var1':200})==[False,True,False,False,False,True]#[True,False,True,True,True,False]
        assert i.filter([-100,0,1,100,200,200.001],{'var1':200})==[0,200.001]

        i=mSetCombine('{1,2,3} u [100,200]')
        assert i.get_init_args()==(mSetRoster(1,2,3),mSetInterval(100,200))
        i = mSetCombine('!({1,2,3} u [100,200])')
        assert i.is_complement
        assert i.get_init_args() == (mSetRoster(1, 2, 3), mSetInterval(100, 200),True,True)
        i = mSetCombine('!({1,2,3} n [100,200])')
        assert i.is_complement
        assert i.get_init_args() == (mSetRoster(1, 2, 3), mSetInterval(100, 200), False,True)
        with pytest.raises(TypeError):
            i = mSetCombine('!({1,2,3} n [100,200] u  [900,100))')

        print('\nRESULT TEST: mSetUnion instance->PASS')
