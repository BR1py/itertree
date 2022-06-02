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

"""
import fnmatch
from itertree import *


class IntegerModel(Data.iTDataModel):
    """'
    A data model for integer type numbers
    """

    BIN = 0
    HEX = 1
    DEC = 2
    KEYS={'BIN':BIN,'HEX':HEX,'DEC':DEC}

    def __init__(self, value=Data.__NOVALUE__, min=float('-inf') , max=float('+inf'),
                 representation=DEC):
        """
        A data model for integer type numbers

        :param value: a value that should be entered (default/start value) directly into the model

        :param range_interval: Interval object defining the valid range for the integer

        :param representation: on of DEC/HEX/BIN for the formatting of the string representation of the integer
        """
        self._min=min
        self._max=max
        self._range_interval = iTInterval(lower_limit=min,upper_limit=max,lower_open=False,upper_open=False)
        if type(representation) is str:
            representation=self.KEYS[representation]
        self._representation = representation

        super().__init__(value)

    def validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        if type(value) is not int:
            raise Data.iTDataTypeError('Given value of wrong type')
        if self._range_interval.check(value):
            return value
        raise Data.iTDataValueError('Value: %s not in expected range: %s' % (repr(value), self._range_interval.math_repr()))

    def formatter(self, value=None):
        """
        The formatter function the creates the string representation of the value
        Note:: If n value is defined "None" is returned
        :param value: give external value to be formatted (if None the internal value will be used)

        :return: string representing the value
        """
        if value is None:
            if self.is_empty:
                return 'None'
            value = self._value

        if self._representation == self.HEX:
            return hex(value)
        elif self._representation == self.BIN:
            return bin(value)
        else:  # self._representation == self.DEC:
            return '%i' % value

    def __repr__(self):
        """
        object representation
        :return: object representation string
        """
        if self.is_empty:
            value=''
        else:
            value=repr(self._value)
        return 'IntegerModel(%s, min=%s, max=%s, representation=%i)' % (value,
                                                                        repr(self._min),repr(self._max),
                                                                        self._representation)


class FloatModel(Data.iTDataModel):
    """
           A data model for float type numbers
    """


    def __init__(self, value=Data.__NOVALUE__, min=float('-inf') , max=float('+inf'), digits=3):
        """
        A data model for float type numbers

        :param value: a value that should be entered (default/start value) directly into the model

        :param range_interval: Interval object defining the valid range for the float

        :param digits: number of digits that should be printed in the string representation of the float
        """
        self._min=min
        self._max=max
        self._range_interval = iTInterval(lower_limit=min,upper_limit=max,lower_open=False,upper_open=False)
        self._digits = int(digits)
        super().__init__(value)

    def validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        if type(value) is not float:
            raise Data.iTDataTypeError('Given value of wrong type')
        if self._range_interval.check(value):
            return value
        raise Data.iTDataValueError('Value: %s not in range: %s' % (repr(value), self._range_interval.math_repr()))

    def formatter(self, value=None):
        """
        The formatter function the creates the string representation of the value
        Note:: If n value is defined "None" is returned
        :param value: give external value to be formatted (if None the internal value will be used)

        :return: string representing the value
        """
        if value is None:
            if self.is_empty:
                return 'None'
            value = self._value
        return '{v:.{digits}f}'.format(v=value, digits=self._digits)

    def __repr__(self):
        """
        object representation
        :return: object representation string
        """

        if self.is_empty:
            value=''
        else:
            value=repr(self._value)
        return 'FloatModel(value= %s, min=%s, max=%s, digits=%i)' % (value,
                                                                     repr(self._min),repr(self._max),
                                                                     self._digits)


class StringModel(Data.iTDataModel):
    """
    data model for strings
    """

    def __init__(self, value=Data.__NOVALUE__, match='', max_len=-1):
        """
        data model for strings
        :param value: default/start value
        :param match: match pattern (fnmatch standard) for the given string
        :param max_len: maximum length of the string
        """
        self.match = str(match)
        self.max_len = int(max_len)
        super().__init__(value)

    def validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        t = type(value)
        if t is not str:
            raise Data.iTDataTypeError('Given value of wrong type')
        if self.max_len>=0:
            if len(value) > self.max_len:
                raise Data.iTDataValueError('Given value contains to many characters (max_length=%i)' % self.max_len)
        if len(self.match)>0:
            if not fnmatch.fnmatch(value, self.match):
                raise Data.iTDataValueError('Given value does not match to given match pattern')
        return value

    def formatter(self, value=None):
        """
        The formatter function the creates the string representation of the value
        Note:: If n value is defined "None" is returned
        :param value: give external value to be formatted (if None the internal value will be used)

        :return: string representing the value
        """
        if value is None:
            if self.is_empty:
                return 'None'
            value = self._value
        return value

    def __repr__(self):
        """
        object representation
        :return: object representation string
        """

        if self.is_empty:
            value=''
        else:
            value=repr(self._value)

        return 'StringModel(%s, match=%s, max_length=%s)' % (value,
                                                                repr(self.match),
                                                                repr(self.max_len))

DATA_MODELS=[IntegerModel,FloatModel,StringModel]
