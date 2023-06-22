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


This part of code contains the helper functions related to the `iTree` data attribute
"""

import copy
import itertools
import abc
import fnmatch
import re

from collections import deque, namedtuple
from itertree.itree_helpers import *
from itertree.itree_filters import *
from itertree.itree_mathsets import *

# special internal constant used for the item that is stored without giving a key

class iTValueModel(abc.ABC):
    """

    This is the replacement for the old `iTDataModel()`-class.

    This class can be used to define data models for the values that might be placed in the `iTree`.

    The model should define min more detail which value objects are accepted or not and it defines also how not
    matching objects are handled:

        * Deny the value and raise a ValueError exception
        * Cast the value into a valid value object

    But the definition of the data model allows limitations which goes far away from just data-type related topics.
    E.g. In the model the user can limit numerical values to a specific range (interval) or he might
    limit strings to specific characters.

    All definitions related to checks and type casts must be defined by the user by overwriting the method
    `check_and_cast_single_item(value_item)` . The return of the method must e the checked and cast value. if the value
    does not match the method should raise a `ValueError` .

    The method should always check and cast a single item, this is important. In case a list or an array like value
    should be stored in the model the base model will manage the required iteration over the sub-items and perform
    and utilize the single item check via the user defined method.

    .. note:: In case a value like `[1,2,3,45]` is given each item in the list will be checked and/or casted.

    This leads us to an important second definition functionality related to the model related to the size of
    dimensions (shape) of the value stored in the model. The definition
    of the shape is given as a parameter when the object is instanced. For the shape we expect a tuple with
    the dimension information. If a value object is given the maximum shape will be calculated and this will be
    compared with the expected one. The maximum is used because in nested lists the user can define
    sub-list with different length. Strings or bytes aare also seen as arrays in this case!

    We have the following possibilities to define shapes:

        * shape=Any -> accept any shape of the given value (no check performed)

        * shape=tuple() -> empty tuple given no dimension expected model will accept single values only!

        * shape=(Any,) -> tuple containing one element which is the Any helper class; We will accept single values or
          any 1 dimensional object here (e.g. values like: `1`; `'abc'`; `[1,2,3,4]` )

        * shape=(10,) -> tuple containing one element. We expect one dimensional values with a length lower
          or equal to the given integer number

        * shape=(INF,) -> tuple containing one element that is INF (infinite). We expect one dimensional values
          of any length

        * shape=(3,4) -> Two dimensions expected with fixed size (e.g. [[1],[2,3]] would match)

        * shape=(INF,4) -> Two dimensions expected with first length unlimited and second length limited to 3

        * shape=(4,ANY) -> Minimum one dimensions expected with first length limited to 4; here the user
          can also put infinite dimensions in (e.g [1]; [[1],[2]] ; [[[[888],[202,500]]]] would fit)

        * shape=(4,ANY,INF) -> 1 dimension or 3 dimensions accepted, 2 dimension will not be accepted

    .. note:: The model base object `iTValueModel()` contains two checking levels. First the user defined
              check via method definition for checks and casts of single items given. In second step the model also
              checks the dimension (shape) of the given value.

              In case a `str` or `bytes` objects are given the behavior related to the checks will be a bit different
              as for the other objects. The method `check_and_cast_single_item(value_item)` will target the whole string
              as a single item! But the shape check will be done also on the string as an object with a length.

              This means a string is a 1 dimensional object and the user might limit the size of the string via a shape.
              (E.g.: The object "Hello" has the shape: (5,); the object ['one', 'two','three'] has the shape: (3,5) )
              The user might use the method 'get_max_shape()' to measure the shape of objects that is considered
              in the model base class.

    During the instance of the object a formatter can be defined too. This might help the user e.g. do define if an
    integer value should be converted to a hex or binary representation during string conversion. The build-in command
    str() of this model class will deliver the formatted value only. The repr() will deliver the class definition.

    To use the model the user should put the instanced model object as value in the `iTree`. The real value objects
    can be placed during object instance via the parameter value or later on via the `set()` method of the model
    (value exchange too). In case the value is not matching to the model definition an ValueError exception
    will be raised.
    If the user like to test first if the value is matching he can use the `in` keyword to check this. In case of no
    match the exception content might be picked via the last_exception property of the model in this case (might give
    a hint why the value is not accepted).

    Standard Parameters:

    :param value: value object to be stored in the model (must match to the model). In case no value is stored
                  in the model (empty model) the value will be NoValue.

    :param description: Description string
    :param shape: Define the dimensions the object should have:

                   * None - shape is ignored object might have dimensions or not
                   * tuple() - empty tuple or iterable - value object will have no size/dimension
                   * (InfShape) - one dimensional value object with infinite size
                   * (100) - one dimensional value object with max size of 100 items
                   * (100,100) - two dimensional object with max size of 100 in each dimension
                   * (InfShape,InfShape,InfShape) - three-dimensional object with infinite size in each dimension
                   * ...

                   .. note:: For multi-dimensional objects it's recommended to use numpy arrays or objects which have
                             the attribute `shape` representing the size for each dimension available
                             instead of tuples or lists. If not the object
                             performance might be worse (internal iterations required to measure the shape).


    :param formatter: Formatter for the single item of the value object (see string formatting in python)
                      In case no formatter is given `str()` will be used for creation of the
                      item string representation.


    """
    __slots__ = ('_value', '_description', '_shape', '_formatter', '_last_exception','_contains')

    def __init__(self, value=NoValue, description=None, shape=Any, contains=None,formatter=str):
        """
    <    Base class for Value Type Model definitions to limit the usable objects that might be placed as values in the
        iTree objects (might be used for other proposes too).

        :type value: object
        :param value: value object to be stored in the model (must match to the model). In case no value is stored
                      in the model (empty model) the value will be NoValue.

        :type description: str
        :param description: Description string

        :type shape: Union[tuple,None]
        :param shape: Define the dimensions the object should have:
                       * None - shape is ignored object might have dimensions or not
                       * tuple() - empty tuple or iterable - value object will have no size/dimension
                       * (INFe,) - one dimensional value object with infinite size
                       * (100,) - one dimensional value object with max size of 100 items
                       * (100,100) - two dimensional object with max size of 100 in each dimension
                       * (INF,INF,INF) - three-dimensional object with infinite size in each dimension
                       * (Any) - single value or one dimensional object

                       * ...

                       ..note:
                               For multi-dimensional objects it's recommended to use numpy arrays or objects which have
                               the attribute `shape` representing the size for each dimension available
                               instead of tuples or lists. If not the object
                               performance might be worse (internal iterations required to measure the shape).

        :type contains: Union[iTSet,iTFilter,object,None]
        :param contains: This filter definition uses `__contains__()` to check if the given value is matching
                         If `None` is given filtering is inactive.

                         ..warning:: The filtering in `iTValueModel`-class differs from filtering we
                                     have in `iTree`-class which uses filters compatible with build-in `filter()`method..
                                     Here the containment is checked via `__contains__().

                                     The `itertree` objects under `Filters` do all have both checks available and
                                     can be used therefore in both cases.

        :param formatter: Formatter for the single item of the value object (see string formatting in python)
                          In case no formatter is given str() will be used for creation of the
                          item string representation.
        """
        if description:
            self._description = str(description)
        else:
            self._description = None
        if shape is not Any:
            shape = tuple(shape)
            for i in shape:
                t = type(i)
                if t is not int and i is not Any and i != INF:
                    raise ValueError('Parameter shape must be an iterable of integers or InfShape objects')
        self._shape = shape
        if formatter is None:
            formatter=str
        if callable(formatter):
            self._formatter = formatter
        else:
            self._formatter = str(formatter)
        self._contains=contains
        if value is NoValue:
            self._value=NoValue
        else:
            self._value = self.__contains__(value,True)
        self._last_exception = None

    def __eq__(self, other):
        if type(other)!=type(self):
            return False
        return self.get_init_args()==other.get_init_args()

    def check_and_cast_single_item(self, value_item):
        """
        method that should be overwritten in the user models

        Depending on the requirements the input value might be casted in a target type and he can be checked before
        or afterwards against check criteria for matches. In case of no match a
        ValueError  should be raised

        :except: Raise ValueError in case given value does not match

        :param value_item: The value given to the model

        :return: casted and checked value
        """
        return value_item

    def _recursive_check(self, value_iterable,raise_exception=False):
        """
        helper generator function used for iterable objects match checks

        :param value_iterable:  iterable value

        :param raise_exception: flag that will raise an exception if not set the not matching elements
         are not yielded back (ignored)
        """
        if self._contains is not None:
            contains=self._contains
            for v in value_iterable:
                if hasattr(v, '__iter__') or hasattr(v, '__next__'):
                    if hasattr(v, 'capitalize'):  # str or byte
                        v=self.check_and_cast_single_item(v)
                        if v in contains:
                            yield v
                        else:
                            if raise_exception:
                                raise ValueError('Given sub value does not match to given filter_method (out of range)')
                    else:
                        yield list(self._recursive_check(v,raise_exception))
                else:
                    v=self.check_and_cast_single_item(v)
                    if v in contains:
                        yield v
                    else:
                        if raise_exception:
                            raise ValueError('Given sub value does not match to given filter_method (out of range)')
        else:
            for v in value_iterable:
                if hasattr(v, '__iter__') or hasattr(v, '__next__'):
                    if hasattr(v, 'capitalize'):  # str or byte
                        yield self.check_and_cast_single_item(v)
                    else:
                        yield list(self._recursive_check(v))
                else:
                    yield self.check_and_cast_single_item(v)

    def _check_shape(self, value_shape):
        """
        helper function checking if the shape of the given value matches to the expected shape of the model

        :except: In case the shape does not match a ValueError will be raised

        :param value_shape: shape of the value

        :return: True
        """
        target_shape = self._shape
        if target_shape is Any:
            return True
        target_shape_size = len(target_shape)
        i = -1
        for i, v_s in enumerate(value_shape):
            if i > target_shape_size - 1:
                if len(target_shape) != 0 and target_shape[-1] is Any:
                    return True
                else:
                    raise ValueError('Given value shape=%s has more dimensions as model accepts '
                                     '(model-shape=%s)' % (repr(value_shape), self.__repr_shape(target_shape)))
            t_s = target_shape[i]
            if not (t_s is Any or t_s == INF) and v_s > t_s:
                raise ValueError('Given value shape=%s (position=%i) too large for model '
                                 '(shape=%s)' % (repr(value_shape), i, self.__repr_shape(target_shape)))
        if i == -1 and len(target_shape) != 0 and target_shape[0] is not Any:
            raise ValueError('Given value shape=%s too small for model (shape=%s) ->expecting more dimensions'
                             % (repr(value_shape), self.__repr_shape(target_shape)))
        if i < target_shape_size - 1:
            if target_shape[i + 1] is not Any:
                raise ValueError('Given value shape=%s too small for model (shape=%s) -> expecting more dimensions'
                                 % (repr(value_shape), self.__repr_shape(target_shape)))
        return True

    def _get_max_shape(self, value):
        """
        helper method that calculates the shape of the given value in case we have multiple dimensions the
        method must iterate over all items which might be slow

        :param value: value the shape should be calculated for

        :return:
        """
        if hasattr(value, '__len__'):
            s0 = len(value)
            if s0 == 0:
                return ()
            if s0 == 1 and hasattr(value, 'capitalize'):  # handle string like objects
                return ()
            if hasattr(value, 'capitalize'):
                return (len(value),)
            s1 = 0
            sub_shape = []
            # via zip_longest we iterate over the longest sub_list item
            for v2 in itertools.zip_longest(*(v if hasattr(v, '__len__') else tuple() for v in value), fillvalue=0):
                s1 += 1  # calc the length of second dimension
                for v3 in v2:
                    sub_shape_new = self._get_max_shape(v3)  # recursive measurement of lower dimensions
                    # compare new shapes with old shapes (find max)
                    for i, new in enumerate(sub_shape_new):
                        if i >= len(sub_shape):
                            # new items
                            sub_shape.extend(sub_shape_new[i:])
                        else:
                            # is max?
                            if sub_shape[i] < new:
                                sub_shape[i] = new
            if len(sub_shape):
                return (s0, s1) + tuple(sub_shape)
            elif s1:
                return (s0, s1)
            else:
                return (s0,)
        else:
            return ()

    def __contains__(self, value, _return_value=False):
        """
        Main checking function if a value matches in the model

        :param value: value to be checked

        :param _return_value: internal boolean parameter if we should give back the value itself

        :return: True/False or value
        """
        if value is NoValue:  # same as clear()
            if _return_value:
                return NoValue
            return True
        try:
            if hasattr(value, '__iter__') or hasattr(value, '__next__'):
                if hasattr(value, 'capitalize'):  # str or byte
                    value = self.check_and_cast_single_item(value)
                    if self._contains is not None:
                        if value not in self._contains:
                            raise ValueError('Given value does not match to given filter_method (out of range)')
                else:
                    value = list(self._recursive_check(value,True))
            else:
                value = self.check_and_cast_single_item(value)
                if self._contains is not None:
                    if value not in self._contains:
                        raise ValueError('Given value does not match to given filter_method (out of range)')
            if self._shape is not Any:
                self._check_shape(self._get_max_shape(value))
            self._last_exception = None
            if _return_value:
                return value
            else:
                return True
        except Exception as e:
            self._last_exception = e
            if _return_value:
                return self._value
            else:
                return False

    def set(self, value):
        """
        Set the value of the model in case the value does not match a ValueError exception will be raised

        :param value: value to be placed inside the model

        :return: old value stored in the model
        """
        value = self.__contains__(value, True)
        if self._last_exception:
            raise self._last_exception
        old, self._value = self._value, value
        return old

    def get(self):
        """
        get the value that is placed inside the model

        If no value is stored in the model the `NoValue`-object will be given back

        :return: value stored in the model
        """
        return self._value

    @property
    def value(self):
        """
        property delivering the value stored in the model

        :return: value stored in the model
        """
        return self._value

    @property
    def description(self):
        """
        optional description of the model

        :return: description related to the model
        """
        return self._description

    def set_description(self, description):
        """
        set/exchange  the description of the model

        :param description:

        :return: old description
        """
        old, self._description = self._description, str(description)
        return old

    @property
    def formatter(self):
        """
        get the formatter stored in the model

        :return: formatter object
        """
        return self._formatter

    def set_formatter(self, formatter):
        """
        set the formatter of the object

        :param formatter: The formatter can be a callable method that delivers a str object
                          or a string that contains teh formatting info

        :return: old formatter
        """
        if callable(formatter):
            old, self._formatter = self._formatter, formatter
        else:
            old, self._formatter = self._formatter, str(formatter)
        return old

    @property
    def contains(self):
        """
        contains object stored in the model
        :return:
        """
        return self._contains

    def clear(self):
        """
        deletes teh value store din the model and place the `NoValue`-object in
        """
        self._value = NoValue


    @property
    def last_except(self):
        """
        get the last exception

        :return: last exception raised by the model related the storage or check of a value
        """
        return self._last_exception

    @property
    def is_iTValueModel(self):
        """
        used for model identification

        :return: True
        """
        return True

    def get_init_args(self, full=False,clear=False):
        """
        deliver all initial arguments used to instance this model object

        :param full: True give always full list
                     False (default) list is shortened in case of default parameter values

        :param clear: True - use NoValue object as value (ignore stored value)
                      False - stored value is included in parameter tuple

        :return: Tuple of initial parameters
        """
        if clear:
            value=NoValue
        else:
            value=self._value
        if full or self._formatter is not str:
            return (value, self._description, self._shape, self._contains,self._formatter)
        elif self._contains is not None:
            return (value, self._description, self._shape, self._contains)
        elif self._shape is not Any:
            return (value, self._description, self._shape)
        elif self._description is not None and self._description!='':
            return (value, self._description)
        else:
            return (value,)

    def __repr_shape(self, shape):
        """
        helper function for the repr of the shape

        :param shape: shape to be converted into a string representation

        :return: string representation of given shape
        """
        if shape is Any:
            return 'Any'
        out = ['(']
        for i in self._shape:
            if i is Any:
                out.append('Any')
                out.append(',')
            elif i == INF:
                out.append('INF')
                out.append(',')
            else:
                out.append(repr(i))
                out.append(',')
            out[-1] = ')'
        return ''.join(out)

    def __repr__(self):
        """
        object representation

        :return: representation string
        """
        out = ['%s(' % self.__class__.__name__]
        #out.append(self.__str__())
        for item in self.get_init_args():
            if item is Any:
                out.append('Any')
            else:
                out.append(repr(item))
            out.append(', ')
        out[-1] = ')'
        return ''.join(out)

    def __create_item_str(self,value):
        """
        helper method for formatting of the given value

        :param value: value to be formatted

        :return: string of the formatted value
        """
        if hasattr(value, '__iter__') or hasattr(value, '__next__'):
            if hasattr(value, 'capitalize'):  # str or byte
                if callable(self._formatter):
                    return self._formatter(value)
                else:
                    try:
                        return self._formatter.format(value)
                    except:
                        return self._formatter%value
            else:
                out='['+''.join(self.__create_item_str(v)+', ' for v in value)
                return out[:-2]+']'
        else:
            if callable(self._formatter):
                return self._formatter(value)
            else:
                try:
                    return self._formatter.format(value)
                except:
                    return self._formatter % value

    def __str__(self):
        """
        string representation of the model value
        here we give just the representation of the stored value not the model object back

        :return: item string
        """
        if self._value == NoValue:
            return 'NoValue'
        return self.__create_item_str(self._value)

class iTAnyValueModel(iTValueModel):
    """
    Model that will take any python object without any restrictions
    """

    def check_and_cast_single_item(self, value_item):
        """
        required overload will allow any object to be stored in the model

        :param value_item: potential value to be stored in the model

        :return: confirmed value to be stored in the model
        """
        return value_item


class iTRoundIntModel(iTValueModel):
    """
    Model that would store integer values
    The model accepts any object that can be casted into a float and rounded to an integer
    to be stored as a int in the model
    """
    def check_and_cast_single_item(self, value_item):
        return round(float(value_item))


class iTIntModel(iTValueModel):
    """
    This integer model allows only integers or strings containing a decimal integer to be stored in the model
    as int value
    """
    def check_and_cast_single_item(self, value_item):
        if type(value_item) in {int, str}:
            return int(value_item)
        raise ValueError('Given value type is not matching to data model')


class iTInt8Model(iTValueModel):
    """
    Integer model that limits the given values to int8 values
    """
    interval = mSetInterval(-128, 127)

    def __init__(self,value=NoValue,description=None,shape=Any,contains=None,formatter=str):
        if contains:
            contains=mSetCombine(contains,self.interval,is_union=False)
        else:
            contains=self.interval
        super().__init__(value,description,shape,contains=contains,formatter=formatter)

    def check_and_cast_single_item(self, value_item):
        if type(value_item) not in {int, str}:
            raise ValueError('Given value type is not matching to data model')
        return int(value_item)

    def get_init_args(self, full=False,clear=False):
        if clear:
            value = NoValue
        else:
            value = self._value
        if full or self._formatter is not str:
            return super().get_init_args(full, clear)
        elif self._contains is not None and self._contains!=self.interval:
            return (value, self._description, self._shape, self._contains)
        elif self._shape is not Any:
            return (value, self._description, self._shape)
        elif self._description is not None and self._description != '':
            return (value, self._description)
        else:
            return (value,)

class iTUInt8Model(iTInt8Model):
    """
    Integer model that limits the given values to uint8 values
    """
    interval = mSetInterval(0,255)


class iTInt16Model(iTInt8Model):
    """
    Integer model that limits the given values to int16 values
    """

    interval = mSetInterval(-32768, 32767)


class iTUInt16Model(iTInt8Model):
    """
    Integer model that limits the given values to uint16 values
    """

    interval = mSetInterval(0, 65535)


class iTInt32Model(iTInt8Model):
    """
    Integer model that limits the given values to int32 values
    """

    interval = mSetInterval(-2147483648, 2147483647)


class iTUInt32Model(iTInt8Model):
    """
    Integer model that limits the given values to uint32 values
    """

    interval = mSetInterval(0, 2 ** 32 - 1)


class iTInt64Model(iTInt8Model):
    """
    Integer model that limits the given values to int64 values
    """

    interval = mSetInterval(-9223372036854775808, 9223372036854775807)


class iTUInt64Model(iTInt8Model):
    """
    Integer model that limits the given values to uint64 values
    """

    interval = mSetInterval(0, 18446744073709551615)


class iTFloatModel(iTValueModel):
    """
    Float model that allows any float or string that can be casted to float to be stored in the model as float value
    """

    def check_and_cast_single_item(self, value_item):
        return float(value_item)

class iTStrModel(iTValueModel):
    """
    A model to store a string
    """
    def check_and_cast_single_item(self, value_item):
        return str(value_item)

class iTStrFnPatternModel(iTStrModel):
    """
    A model to store a string that matches to the fnmatch pattern
    """
    def __init__(self,value=NoValue,description=None,shape=Any,contains=None,pattern=None,formatter=None):
        if pattern is not None:
            if contains:
                contains=iTFilterIntersection(contains,iTFilter(fnmatch.fnmatch,pattern))
            else:
                contains=iTFilter(fnmatch.fnmatch,pattern)
        self._pattern=pattern
        super().__init__(value,description,shape,contains=contains,formatter=formatter)

    @property
    def pattern(self):
        return self._pattern

    def get_init_args(self, full=False,clear=False):
        if full or self._formatter is not str:
            args = super().get_init_args(full=True, clear=clear)
            return args[:-1]+(self._pattern,args[-1])
        elif self._pattern is not None:
            args = super().get_init_args(full=True, clear=clear)
            return args[:-1] + (self._pattern,)
        else:
            return super().get_init_args(full=full, clear=clear)

class iTStrRegexPatternModel(iTStrModel):
    """
    A string model that matches to the regex pattern
    """
    def __init__(self, value=NoValue, description=None, shape=Any, contains=None, pattern=None, formatter=None):
        if pattern is not None:
            if contains:
                contains = iTFilterIntersection(contains, iTFilter(lambda i: re.fullmatch(pattern,i) is not None))
            else:
                contains = iTFilter(lambda i: re.fullmatch(pattern,i) is not None)
        self._pattern = pattern
        super().__init__(value, description, shape, contains=contains, formatter=formatter)

    @property
    def pattern(self):
        return self._pattern

    def get_init_args(self, full=False, clear=False):
        if full or self._formatter is not str:
            args = super().get_init_args(full=True, clear=clear)
            return args[:-1] + (self._pattern, args[-1])
        elif self._pattern is not None:
            args = super().get_init_args(full=True, clear=clear)
            return args[:-1] + (self._pattern,)
        else:
            return super().get_init_args(full=full, clear=clear)



class iTASCIIStrModel(iTValueModel):
    """
    A string model that accepts only ASCII characters
    """
    def check_and_cast_single_item(self, value_item):
        value = str(value_item)
        for i, c in enumerate(value):
            if ord(c) >= 128:
                raise ValueError('Non ASCII character %s found in value (position=%i) '
                                 '-> not accepted by model' % (repr(c), i))
        return value

class iTUTF8StrModel(iTValueModel):
    """
    A string model that accepts only  UTF-8 characters
    """

    def check_and_cast_single_item(self, value_item):
        value = str(value_item)
        try:
            value.encode('unicode-escape').decode('UTF-8')
        except:
            raise ValueError('Non UTF-8 character found in given value '
                             '-> not accepted by model')
        return value


class iTUTF16StrModel(iTStrModel):
    """
    A string model that accepts only UTF16 characters
    """
    def check_and_cast_single_item(self, value_item):
        value = str(value_item)
        try:
            value.encode('UTF-16').decode('UTF-16')
        except:
            raise ValueError('Non UTF-16 character found in given value '
                             '-> not accepted by model')
        return value

class iTEnumerateModel(iTValueModel):

    def __init__(self,value=NoValue,enumerate_dict={}):
        if NoValue not in enumerate_dict:
            enumerate_dict[NoValue]=NoValue
        self.cast_dict={v:k for k,v in enumerate_dict.items()}
        for k in enumerate_dict.keys():
            if k is not NoValue and k!=int(k):
                raise TypeError('Given enumerate_dict must have integer keys only!')
            self.cast_dict[k]=k
        self.enumerate_dict=enumerate_dict
        super().__init__(value,formatter=self.enumerate_dict.get)

    def check_and_cast_single_item(self, value_item):
        if value_item is NoValue:
            return NoValue
        try:
            value=self.cast_dict[value_item]
        except KeyError:
            raise ValueError('Given value does not match to enumeration definition of the model')
        return value

# ************************************************************************************************
# ******* The rest of the definitions are kept from older versions just to be downward compatible!
# Please do not use for new projects the classes are outdated
# ************************************************************************************************

__NOVALUE__=NoValue
__NOKEY__=NoKey
# return_types
VALUE = V = 0  # returns the stored value
STR = S = 1  # returns the string representation of the value (DTDataItems contains formatters for this)
FULL = F = 2  # In case DTDataItem objects are used for storage the full object is given back


class iTDataValueError(ValueError):
    """
    Exception to be raised in case a validator finds a non matching value related to the iDataModel
    """
    pass


class iTDataTypeError(ValueError):
    """
    Exception to be raised in case a validator finds a non matching value type related to the iDataModel
    """
    pass


class iTDataModel(abc.ABC):
    """
    The default iTree data model class
    This the interface definition for specific data model classes
    that might be created using this superclass

    The data model checks the given value for a specific data item.
    So that we can ensure that the given value matches to the expectations.
    We can check for types, shapes (length), limits, or matching patterns.

    Besides the check we can also define a default formatter for the value that is used when
    it is translated into a string.

    (see examples/itree_data_examples.py)
    """
    __slots__ = ('_value', '_formatter_cache')

    def __init__(self, value=NoValue):
        """
        :param value: value object to be stored in the data model
        """
        if not value == NoValue:
            value = self.validator(value)
        self._value = value
        self._formatter_cache = None

    def __contains__(self, item):
        """
        :param item: item to be checked if it is equal to the stored value
        :return: True/False
        """
        return self._value == item

    def __format__(self, format_spec=None):
        """
        If no format spec is given we format with the predefined internal formatter
        :param format_spec: None or format specification for the value
        :return: formatted string
        """
        if self.is_empty:
            # we might create an exception here when we have numerical values!
            # must be overloaded!
            return 'None'
        if format_spec is None or format_spec == '':
            # as long as the value is not changed we cache the result for quicker reuse:
            if self._formatter_cache is None:
                # run the formatter
                self._formatter_cache = self.formatter(self.value)
            return self._formatter_cache
        else:
            return self.value.__format__(format_spec)

    def __repr__(self):
        if self.is_empty:
            return '%s()' % self.__class__.__name__
        return '%s(value= %s)' % (self.__class__.__name__, self._value)

    def __eq__(self, other):
        if isinstance(other, iTDataModel):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def is_empty(self):
        """
        tells if the iTreeDataModel is empty or contains a value
        :return:
        """
        return self._value == NoValue

    @property
    def is_iTDataModel(self):
        return True

    def get(self):
        """
        the stored value
        :return: object stored in value
        """
        return self._value

    def set(self, value):
        """
        put a specific value into the data model

        :except: raises an iTreeValidationError in case a not matching object is given

        :param value: value object to be placed in the data model
        """
        if value is NoValue:
            old, self._value = self._value, NoValue
        else:
            old, self._value = self._value, self.validator(value)
            self._formatter_cache = None
        return old

    value = property(get, set)

    def check(self, value):
        """
        put a specific value into the data model

        :except: raises an iTreeValidationError in case a not matching object is given

        :param value: value object to be placed in the data model
        """
        try:
            self._value = self.validator(value)
            return True, ''
        except Exception as e:
            return False, str(e)

    def clear(self, ):
        """
        clears (deletes) the current value content and sets the state to "empty"

        :return: returns the value object that was stored in the iTreeDataModel
        """
        old, self._value = self._value, NoValue
        self._formatter_cache = None
        return old

    @abc.abstractmethod
    def validator(self, value):
        """
        This method should check the given value.

        It should raise an iDataValueError Exception with a failure explanation in case the value is not
        matching to the iDataModel.

        ..warning:: The validator in an explicit iDataModel class must always return the value itself and it must raise
                    the iDataValueError in case of a no matching value. It should also call the super().validator()
                    method or at least consider that `NoValue` is a no matching value.

        :except: iDataValueError in case value is not matching

        :param value: to be checked against the model

        :return: value (which might be casted)
        """
        # we actually accept here any value
        return value

    @abc.abstractmethod
    def formatter(self, value=None):
        """
        The formatter function allows us to create a specific string representation

        Especially in case of numerical values this is interesting.
        You can define here that an integer should be represented always as hex, bin, ...
        or for floats you can give digits.

        The formatter can be created by using the classical format options of string but
        for enumerations we can put here also a table, etc.

        :return: string representing the value
        """
        # place specific formatting here:
        if value is None:
            if self.is_empty:
                return 'None'
            value = self._value
        return str(value)

    @abc.abstractmethod
    def get_init_args(self):
        return (self._value,)


class iTDataModelAny(iTDataModel):
    """
    Example iDataModel class that accepts any kind of value
    """

    # we must overload the following mandatory abstract methods:

    def validator(self, value):
        return super().validator(value)

    def formatter(self, value=None):
        return super().formatter(value)

    def get_init_args(self):
        return tuple()


class iTData(dict):
    """
    Standard itertree Data management object might be overloaded or changed by the user
    """

    GET_LOOK_UP_METHOD = {STR: lambda item: format(item) if isinstance(item, iTDataModel) else str(item),
                          FULL: lambda item: item,
                          VALUE: lambda item: item.value if isinstance(item, iTDataModel) else item
                          }

    def __init__(self, seq=None, **kwargs):
        """
        Standard iTreeData object might be overloaded or changed by the user.
        Stores the data in a internal dict. For attribute like data it's recommended to store
        the data as iTreeDataItem. This object allows the definition of data type, sizes, limits and format definition
        of a string representation.

        :param data_items: single object or dict with key,value objects to be stored in the iTreeData object
        """
        if not kwargs:
            if seq is None:
                super().__init__()
            else:
                try:
                    super().__init__(seq)
                except:
                    super().__init__([(__NOKEY__, seq)])
        else:
            if seq is None:
                super().__init__(**kwargs)
            else:
                try:
                    super().__init__(seq, **kwargs)
                except TypeError:
                    super().__init__([(__NOKEY__, seq)], **kwargs)

    def __setitem__(self, *args,key=__NOKEY__, value=__NOVALUE__):
        """
        setter for the iTreeData object
        HINT: If no value is given the key item will be interpreted as value
              and it will be stored as __NOKEY__-object.
        :param key: key under which the given object is stored
        :param value: object that should be stored
        :return: None
        """
        l = len(args)
        if key==__NOKEY__:
            if value==__NOVALUE__:
                if l==1:
                    value=args[0]
                else:
                    try:
                        key,value=args
                    except:
                        raise AttributeError('Wrong number of positional arguments')
            else:
                if l==1:
                    key = args[0]
                elif l!=0:
                    raise AttributeError('Wrong arguments given')
        else:
            if l!=0:
                raise AttributeError('Wrong number of positional arguments')
        try:
            return super().__getitem__(key).set(value, _it_data_model_identifier=0)
        except (KeyError, AttributeError, TypeError):
            if key is __NOKEY__ and value is __NOVALUE__:
                if super().__contains__(key):
                    super().__delitem__(key)
            else:
                return super().__setitem__(key, value)

    def __getitem__(self, key=__NOKEY__, _return_type=VALUE):
        """
        get a specific data item by key

        :except: Will raise KeyError in case given key is unknown

        :param key: key of the data item (if not given __NOKEY__ is used!

        :param _return_type: We can deliver different returns
                            * VALUE - value object
                            * FULL - iTreeDataModel (only if used else same as VALUE)
                            * STR - formatted string representation of the data value

                            ..note :: The parameter is only used by the helper method `get()`
                                      and cannot be used by standard item access

        :return: requested value
        """
        item = super(iTData, self).__getitem__(key)
        return self.GET_LOOK_UP_METHOD[_return_type](item)

    def __delitem__(self, key=__NOKEY__, _value_only=True):
        """
        delete a item by key

        :except: KeyError is raised in case item key is unknown

        :param key: key of the data item (if not given __NOKEY__ is used!
        :param _value_only: Internal parameter cannot be reached by standard access
                            * True - (default) in case of iDataModel items we delete only the internal value
                                     not the model itself
                            * False - we delete the value independent from the type
        :return: deleted value

        """
        if _value_only:
            try:
                return super(iTData, self).__getitem__(key).clear(_it_data_model_identifier=0)
            except (AttributeError, TypeError):
                # AttributeError raised if clear() is not known
                # TypeError raised if _it_data_model_identifier is not accepted
                pass
        return super(iTData, self).__delitem__(key)

    def __copy__(self):
        return iTData(super().copy())

    def __deepcopy__(self):
        iTData(copy.deepcopy(super()))

    def __repr__(self):
        # we represent via dict because dict will automatically load in again as iTreeData object
        if self.is_empty:
            return '%s()' % (self.__class__.__name__)
        if self.is_no_key_only:
            return '%s(%s)' % (self.__class__.__name__, repr(super(iTData, self).__getitem__(__NOKEY__)))
        return '%s(%s)' % (self.__class__.__name__, super(iTData, self).__repr__())

    def __hash__(self):
        """
        Again hashing is quite slow here
        :return: hash integer
        """
        return hash((i for i in self.items()))

    def update(self, E=None, **F):
        """
        function update of multiple items
        if one item is invalid the whole update will be skipped and an iDataValueError exception will thrown!

        In case the replace_model flag is set the model will be exchanged.

        Parameters taken from builtin dict:

        Update D from dict/iterable E and F.
        If E is present and has a .keys() method, then does:
        If E is present and lacks a .keys() method, then does:
        In either case, this is followed by:

        :except: raises iDataValueError exception if a value in the given object is not matching to the data-model.
                 The iData object will not be updated in this case.

        :param E:
                  * with .keys() method: for k in E: D[k] = E[k]
                  * without .keys() method: for k, v in E: D[k] = v

        :param **F: we run: for k in F:  D[k] = F[k]

        :param replace_models:
                  * True - Will replace the whole key related value (also iTDataModels are replaced)
                  * False (default) - All values are replaced in case of iTDataModel object the internal value will
                                      be replaced
        """
        if F.get('replace_models') is True:
            del F['replace_models']
            helper = iTData(E, **F)
            return super(iTData, self).update(helper.items())
        # we first create a helper iTData object
        helper = iTData(E, **F)
        # check if we have just valid items will raise an exception if not matching!
        # pre-check and model identification:
        i = 0
        super_class = super(iTData, self)
        try:
            models = deque()
            for i, (k, v) in enumerate(helper.items()):
                m_flag = False
                if not isinstance(v, iTDataModel):
                    try:
                        super_class.__getitem__(k).validator(v)
                        m_flag = True
                    except (KeyError, AttributeError):
                        pass
                models.append(m_flag)
        except Exception as e:
            raise e.__class__('Input item %s raises: %s' % (str(list(helper.items())[i]), str(e)))
        # after pre check ran with success we finally fill in the data
        [m and super_class.__getitem__(k).set(v) or super_class.__setitem__(k, v) for (k, v), m in
         zip(helper.items(), models)]

    def copy(self):
        """
        create a new object with same items

        :return: new object copied from self
        """
        return self.__copy__()

    def clear(self, values_only=False) -> None:
        models = []
        if values_only:
            models = [((k, v), v.clear()) for k, v in super(iTData, self).items() if isinstance(v, iTDataModel)]
        super().clear()
        super().update([(k, v) for (k, v), _ in models])

    def pop(self, key=__NOKEY__, default=__NOKEY__, value_only=True):
        """
        delete a stored value

        :except: will case KeyError if key is not found and default is not set

        :param key: key where the item should be popped out

        :default: define the value given back in case key is not found else
                  KeyError will be raised

        :param value_only: True - only value will be deleted model will be kept in iTreeData
                           False - whole model will be popped out

        :return: deleted item or default
        """
        try:
            item = super(iTData, self).__getitem__(key).clear(_it_data_model_identifier=0)
        except KeyError:
            if default != __NOKEY__:
                return default
            raise
        except (AttributeError, TypeError):
            # AttributeError raised if clear() is not known
            # TypeError raised if _it_data_model_identifier is not accepted
            return super(iTData, self).pop(key)
        return item

    def get(self, key=__NOKEY__, default=None, return_type=VALUE):
        """
        get a specific data item by key


        :param key: key of the data item (if not given __NOKEY__ is used)

        :param default: default value that will be delivered in case of no match

        :param _return_type: We can deliver different returns
                            * VALUE - value object
                            * FULL - iTreeDataModel (only if used else same as VALUE)
                            * STR - formatted string representation of the data value

        :return: requested value
        """
        try:
            return self.__getitem__(key, _return_type=return_type)
        except KeyError:
            return default

    # not supported methods:
    def fromkeys(self, *args, **kwargs):
        """
        create a new iData object based on given keys and optional value

        - real signature unknown
        """
        return iTData(dict.fromkeys(self, *args, **kwargs))

    def __or__(*args, **kwargs):
        """
        method not supported

        :except: raises an Attribute error
        """
        raise AttributeError('__or__() method not supported by iData object')

    def __ior__(*args, **kwargs):
        """
        method not supported

        :except: raises an Attribute error
        """
        raise AttributeError('__ior__() method not supported by iData object')

    # additional methods (not available in normal dict)
    def delete_item(self, key, value_only=True):
        """
        delete a item by key

        :except: KeyError is raised in case item key is unknown

        :param key: key of the data item (if not given __NOKEY__ is used!
        :param value_only:
                            * True - (default) in case of iDataModel items we delete only the internal value
                                     not the model itself
                            * False - we delete the value independent from the type (also iDataModel objects)
        :return: deleted value
        """

        return self.__delitem__(key, value_only)

    def model_values(self):
        """
        iterator that takes in case of iDataModel values the value out of the model,
        in case of non iDataModel values the value is given directly as it is

        :return: iterator
        """
        for v in super(iTData, self).values():
            if isinstance(v, iTDataModel):
                yield v.value
            else:
                yield v

    def model_items(self):
        """
        iterator that takes in case of iDataModel values the value out of the model,
        in case of non iDataModel values the value is given directly as it is

        :return: iterator
        """
        for k, v in super(iTData, self).items():
            if isinstance(v, iTDataModel):
                yield k, v.value
            else:
                yield k, v

    @property
    def is_empty(self):
        """
        used for identification of this class
        :return: True
        """
        return not self


    @property
    def is_no_key_only(self):
        """
        used for identification of this class
        :return: True
        """
        return super(iTData, self).__len__() == 1 and super(iTData, self).__contains__(__NOKEY__)


    @property
    def is_iTData(self):
        return True

    def is_key_empty(self,key=__NOKEY__):
        '''
        Function delivers a key empty state (it delivers True in case key is absent or
        value is __NOVALUE__
        :param key: key to be check (delault is __NOKEY__
        :return: True/False
        '''
        try:
            return super(iTData, self).__getitem__(key) == __NOVALUE__
        except KeyError:
            return True

    def deepcopy(self):
        """
        create a deep copy of this object

        also all internal items will be copied!

        :return: new object deep copied from self
        """
        return self.__deepcopy__()

    def get_init_args(self):
        return [item for item in self.items()]

class iTDataReadOnly(iTData):
    """
    Standard itertree Data management object might be overloaded or changed by the user
    """

    def __setitem__(self, *arg, **kwargs):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def __delitem__(self, *arg, **kwargs):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def pop(self, *arg, **kwargs):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def update(self, *arg, **kwargs):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def clear(self, *arg, **kwargs):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def delete_item(self, key, value_only=True):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def __repr__(self):
        # we represent via dict because dict will automatically load in again as iTreeData object
        return 'iTDataReadOnly(%s)' % super(iTData, self).__repr__()

    def __copy__(self):
        return iTDataReadOnly(super(iTData, self).copy())

    def __deepcopy__(self):
        iTDataReadOnly(copy.deepcopy(super(iTData, self).copy()))

    def get_init_args(self):
        return [item for item in self.items()]
