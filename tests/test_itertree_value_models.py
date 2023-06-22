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


class Test_iTValueModels():

    def test1_shape_helper_function(self):

        print('\nRUN TEST: iTValueModel shape helper function')

        a=Data.iTAnyValueModel()

        assert a._get_max_shape([[],[]])==(2,)
        assert a._get_max_shape([])==()
        assert a._get_max_shape([[1, 2, 3],[3,4,5,6]])==(2,4)
        assert a._get_max_shape([[[2,3,4,5],1,2], [3, [2,3,4], 5, 6]]) == (2, 4,4)
        assert a._get_max_shape([[[2, 3, 4, [4,[5,6]]], 1, 2], [3, [2, [3,4,5,6,7], 4], 5, 6]]) == (2,4,4,5,2)
        assert a._get_max_shape(['123456789', []]) == (2, 9)
        assert a._get_max_shape([b'123456789', []]) == (2, 9)
        assert a._get_max_shape('1234567890') == (10,)

        assert a._check_shape(1)
        assert a._check_shape('123')
        assert a._check_shape(())
        assert a._check_shape((1,))
        assert a._check_shape((1,2,3,4,56))
        assert a._check_shape((1, (2, 3, 4), 56))
        assert a._check_shape((1,'abcde'))

        # manipulate the model shape
        a._shape=(Any,)
        assert a._check_shape(tuple())
        assert a._check_shape((1,))
        assert a._check_shape((1,2,3,4,56))
        assert a._check_shape((1, (2, 3, 4), 56))

        # minimum one dimension first max. length=3
        a._shape = (3,Any)
        exc=None
        try:
            assert a._check_shape(tuple())
        except Exception as e:
            exc=e
        assert type(exc) is ValueError
        assert 'too small' in exc.args[0]
        assert a._check_shape((1,))
        assert a._check_shape((3,))
        assert a._check_shape((1, 2, 3, 4, 56))
        exc=None
        try:
            assert a._check_shape((4,))
        except Exception as e:
            exc=e
        assert type(exc) is ValueError
        assert 'too large' in exc.args[0]

        # infinity
        a._shape = (INF,Any)
        assert a._check_shape((4,))
        exc=None
        try:
            assert a._check_shape(tuple())
        except Exception as e:
            exc=e
        assert type(exc) is ValueError
        assert 'too small' in exc.args[0]

        # fixed one dimension only
        a._shape = (10,)
        assert a._check_shape((4,))
        exc = None
        try:
            assert a._check_shape(tuple())
        except Exception as e:
            exc = e
        assert type(exc) is ValueError
        assert 'too small' in exc.args[0]

        exc = None
        try:
            assert a._check_shape((20,))
        except Exception as e:
            exc = e
        assert type(exc) is ValueError
        assert 'too large' in exc.args[0]

        exc = None
        try:
            assert a._check_shape((1,1))
        except Exception as e:
            exc = e
        assert type(exc) is ValueError
        assert 'has more' in exc.args[0]

        # fixed two dimension only
        a._shape = (10,2)
        assert a._check_shape((4,1))
        exc = None
        try:
            assert a._check_shape(tuple())
        except Exception as e:
            exc = e
        assert type(exc) is ValueError
        assert 'too small' in exc.args[0]

        exc = None
        try:
            assert a._check_shape((20,))
        except Exception as e:
            exc = e
        assert type(exc) is ValueError
        assert 'too large' in exc.args[0]

        exc = None
        try:
            assert a._check_shape((4,))
        except Exception as e:
            exc = e
        assert type(exc) is ValueError
        assert 'too small' in exc.args[0]

        exc = None
        try:
            assert a._check_shape((1,1,3))
        except Exception as e:
            exc = e
        assert type(exc) is ValueError
        assert 'has more' in exc.args[0]

        # complex
        a._shape = (4,INF,30,Any,400)
        assert a._check_shape((1, 1000, 3,1000,100))
        assert a._check_shape((1, 1000, 3)) # ANY means also no item is allowed!
        with pytest.raises(ValueError):
            a._check_shape((5, 1000, 3))
        with pytest.raises(ValueError):
            a._check_shape((1, 1000))
        with pytest.raises(ValueError):
            a._check_shape((1, 1000,3,1,500))
        with pytest.raises(ValueError):
            a._check_shape((1, 1000,3,1,100,1))
        with pytest.raises(ValueError):
            assert a._check_shape((1, 1000, 3, 1000)) # if ANY item is used we expect always a following item

        print('\nRESULT TEST: iTValueModel shape helper function -> PASS')

    def test2_standard_iTValueObject(self):
        print('\nRUN TEST: iTValueModel base object')

        # We use the any model for this test
        model=Data.iTAnyValueModel(NoValue,'This is my model')
        #The base model contains only positive checks any value can be placed in
        #value checks
        assert 1 in model
        assert [1] in model
        assert [[1]] in model # as long as no shape is given nested iterables are allowed
        assert 'abc' in model
        assert ['abc'] in model
        assert b'abc' in model
        assert [b'abc'] in model
        assert 1 in model
        # value handling
        assert model.value is NoValue
        assert model.set('my_value') is NoValue # delivers last value
        assert model.value =='my_value'
        assert model.set(1) =='my_value'
        assert model.value == 1
        assert repr(model)=="iTAnyValueModel(1, 'This is my model')"

        model.clear()
        assert model.value is NoValue
        # description
        assert model.description=='This is my model'
        assert model.set_description('hello')=='This is my model' # delivers last value
        assert model.description == 'hello'
        # formatter
        assert model.formatter is str
        assert model.set_formatter('{:.2e}') is str # delivers last value
        assert model.formatter == '{:.2e}'
        model.set(1)
        assert str(model)=='1.00e+00'
        assert repr(model)=="iTAnyValueModel(1, 'hello', Any, None, '{:.2e}')"

        assert model.set_formatter('0x{:02x}') # hex representation
        model.set(18)
        assert str(model) == '0x12'
        assert model.set_formatter('0b{:08b}')  # bin representation
        assert str(model) == '0b00010010'
        assert model.set_formatter('{:d}')  # dec representation
        assert str(model) == '18'
        assert model.set_formatter('{:0.2f}')  # float representation
        assert str(model) == '18.00'

        print('\nRESULT TEST: iTValueModel base object -> PASS')

    def test3_standard_iTValueObject_checks_and_cast(self):
        print('\nRUN TEST: iTValueModel base object - checks_and_cast()')
        class check_model(Data.iTValueModel):
            def check_and_cast_single_item(self,value_item):
                value=int(value_item)
                if int(value_item)%2==0:
                    return value
                raise ValueError('Value must be an even number -> value not accepted by the model')
        model = check_model()
        assert  1 not in model
        assert type(model.last_except)==ValueError
        assert 'even number' in model.last_except.args[0]
        assert 2 in model
        assert  3.0 not in model
        assert 4.0 in model # this entry allowed is possible because we cast already in the pre_check
        assert 4.1 in model # this entry allowed is because we cast already in the pre_check
        assert 'a' not in model
        assert '2' in model # this entry allowed is because we cast already in the pre_check

        # stricter model example
        class check_model(Data.iTValueModel):
            def check_and_cast_single_item(self,value_item):
                if type(value_item) is not int:
                    raise ValueError('Value must be of type int -> value not accepted by the model')
                if value_item%2==0:
                    raise ValueError('Value must be an even number -> value not accepted by the model')
                return value_item

        model = check_model()
        assert 4.0 not in model # this model is stricter and allows only integer entries
        assert 4.1 not in model # this model is stricter and allows only integer entries

        # model include a post_check
        class check_model(Data.iTValueModel):
            def check_and_cast_single_item(self,value_item):
                t = type(value_item)
                if not t in {int, str}:
                    raise ValueError('Value must be int or string (cast to int); got different data type'
                                     ' -> value not accepted by model')
                try:
                    value=int(value_item)
                except:
                    raise ValueError('Value type cast to string failed -> value not accepted by model')
                if not (value<100 and value > 10):
                    raise ValueError('Value out of target range (10<value<100) -> value not accepted by model')
                if value % 2 != 0:
                    raise ValueError('Value must be an even number -> value not accepted by the model')
                return value

        model = check_model()
        assert 1.1 not in model
        assert 'int or str' in model.last_except.args[0]

        assert 1 not in model
        assert 'range' in model.last_except.args[0]
        assert 4 not in model
        assert 'range' in model.last_except.args[0]
        assert 12 in model
        assert 98 in model
        assert 99 not in model
        assert 'even' in model.last_except.args[0]
        assert 100 not in model
        assert 'range' in model.last_except.args[0]
        assert '98' in model
        assert ['98',96] in model

        # add no shape
        model = check_model(shape=tuple())
        assert ['98', 96] not in model
        assert 'more' in model.last_except.args[0]
        assert '98' in model
        assert model.last_except is None

        # add 1D infinite shape
        model = check_model(shape=(INF,))
        assert ['98', 96] in model
        assert ['98', [96]] not in model
        # add 1D limited shape
        model = check_model(shape=(3,))
        assert ['98', 96, 94]  in model
        assert ['98', 96,94,92] not in model
        assert 'position=0) too large' in model.last_except.args[0]

        assert ['98', [96], 94] not in model
        assert 'more' in model.last_except.args[0]

        # add 2D limited/unlimited shape
        model = check_model(shape=(3,INF))
        assert ['98', 96, 94]  not in model
        assert 'too small' in model.last_except.args[0]

        assert [['98'], [96], [94,92]] in model

        print('\nRESULT TEST: iTValueModel base object - checks_and_cast()-> PASS')

    def test4_standard_check_predefined_models(self):
        print('\nRUN TEST: check predefined model classes')
        # The AnyValueObject is already tested!
        model=Data.iTRoundIntModel()
        model.set(['123','456'])
        a=str(model)
        values=[1,2.2,-1,'2.34e-1','-2',['123','456']]
        for v in values:
            assert v in model
            model.set(v)
            if type(v) is not list:
                assert str(model)==repr(round(float(v)))
            else:
                assert str(model) =='[123, 456]'
        assert 'abc' not in model

        model = Data.iTIntModel()
        values = [1,  -1,  '-2', ['123', '456']]
        for v in values:
            assert v in model
            model.set(v)
            if type(v) is not list:
                assert str(model) == repr(round(float(v)))
            else:
                assert str(model) == '[123, 456]'
        values = ['abc', 2.2,  '2.34e-1', '-2.1', ['123', '456.3']]
        for v in values:
            assert v not in model
        model = Data.iTIntModel(contains={3,4})
        assert 1 not in model
        assert 3  in model
        assert 3.5 not in model
        assert 4 in model


        model = Data.iTInt8Model()
        values = [1,  -128,  '-2', ['123', '127']]
        for v in values:
            assert v in model
            model.set(v)
            if type(v) is not list:
                assert str(model) == repr(round(float(v)))
            else:
                assert str(model) == '[123, 127]'
        values = ['abc', 2.2,-129,  '2.34e-1', '-2.1', ['123', '128']]
        for v in values:
            assert v not in model

        model = Data.iTUInt8Model()
        values = [0,255,[[0],[255]]]
        for v in values:
            assert v in model
        values = [-1, 256, [[0], [256]],[[-1], [256]]]
        for v in values:
            assert v not in model

        model = Data.iTInt16Model()
        values = [-32768,32767]
        for v in values:
            assert v in model
        values = [-32768-1,32767+1]
        for v in values:
            assert v not in model

        model = Data.iTUInt16Model()
        values = [0,65535]
        for v in values:
            assert v in model
        values = [0-1,65535+1]
        for v in values:
            assert v not in model

        model = Data.iTInt32Model()
        values = [-2147483648, 2147483647]
        for v in values:
            assert v in model
        values = [-2147483648-1, 2147483647+1]
        for v in values:
            assert v not in model

        model = Data.iTUInt32Model()
        values = [0,4294967295]
        for v in values:
            assert v in model
        values = [0-1,4294967295+1]
        for v in values:
            assert v not in model

        model = Data.iTInt64Model()
        values = [-2**63, 2**63-1]
        for v in values:
            assert v in model
        values = [-2**63-1, 2**63]
        for v in values:
            assert v not in model

        model = Data.iTUInt64Model()
        values = [0,2**64-1]
        for v in values:
            assert v in model
        values = [0-1,2**64]
        for v in values:
            assert v not in model


        model = Data.iTFloatModel()
        values = [1,1.23,'1.2e-10','inf','NaN']
        for v in values:
            assert v in model
            model.set(v)
            assert type(model.value) is float
        values = ['abc']
        for v in values:
            assert v not in model
        model = Data.iTFloatModel(contains={1.3,4.5})
        assert 1 not in model
        assert 1.3  in model
        assert 3.5 not in model
        assert 4.5 in model

        model = Data.iTStrModel()
        values = [1,1.23,'1.2e-10','inf','NaN',b'asdl',None]
        for v in values:
            assert v in model
            model.set(v)
            assert type( model.value) is str

        model = Data.iTASCIIStrModel()
        values = [1,1.23,'1.2e-10','inf','NaN',b'asdl',None]
        for v in values:
            assert v in model
            model.set(v)
            assert type(model.value) is str
        values = ['ÖÄÜ'] # None Ascii characters
        for v in values:
            assert v not in model

        model = Data.iTUTF8StrModel()
        values = [1,1.23,'1.2e-10','inf','NaN',b'asdl','ÖÄÜ']
        for v in values:
            assert v in model
            model.set(v)
            assert type(model.value) is str

        model = Data.iTUTF16StrModel()
        values = [1,1.23,'1.2e-10','inf','NaN',b'asdl','ÖÄÜ']
        for v in values:
            assert v in model
            model.set(v)
            assert type(model.value) is str

        enum_dict={0:'left',1:'right',2:'up',3:'down',4:'forward',5:'backward'}
        check_set=set(enum_dict.values())
        check_set.add('NoValue')
        model=Data.iTEnumerateModel(enumerate_dict=enum_dict)
        values = [k for k in enum_dict.keys()]
        values.extend([v for v in enum_dict.values()])
        values.append(NoValue)
        for v in values:
            assert v in model
            model.set(v)
            assert type(model.value) is int or model.value is NoValue
            assert str(model) in check_set
        print('\nRESULT TEST: check predefined model classes-> PASS')

    def test5_models_in_itree(self):
        print('\nRUN TEST: models in iTrees')
        model = Data.iTUInt8Model()
        root=iTree(value=model)
        # in value property we find the model
        assert root.value is model
        # enter values into the model
        assert root.get_value() is NoValue
        assert root.set_value(1) is NoValue # old value returned
        assert root.get_value()==1
        assert root.set_value(3) ==1 # old value returned
        assert root.get_value()==3
        # enter invalid value into the model
        with pytest.raises(ValueError):
            root.set_value(-1)
        # old value resists
        assert root.get_value()==3
        # clear the model
        root.value.clear()
        assert root.get_value() is NoValue
        # recheck model still in iTree value
        assert root.value is model
        assert root.set_value(1) is NoValue  # old value returned
        # now we delete the model:
        assert root.del_value()
        assert root.get_value() is NoValue
        # model is no more in!
        assert root.value is NoValue

        print('\nRESULT TEST: models in iTrees -> PASS')
