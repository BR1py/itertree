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
helper classes used in DataTree object
"""

from __future__ import absolute_import

import abc
import math
import re
from decimal import Decimal
from operator import le, lt, gt, ge
from itertree.itree_helpers import *

UNION = 0
INTERSECT = 1

_VAR_START_CHARACTERS = {i for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'}
_VAR_CHARACTERS = {i for i in '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'}
_NUMBER_START_CHARACTERS = {i for i in '-+1234567890i'}
_CALL = 0
_FORMAT = 1
_OLD = 2


def _get_formatter_type(formatter):
    """
    helper function to identify the formatter type

    In case of str type formatters the formatter stripped from spaces is given back
    :type formatter: Union[str,Callable]
    :param formatter: to be identified object
    :rtype: tuple
    :return: formatter, formatter-types
    """
    if callable(formatter):
        if type(formatter(0)) is not str:
            raise TypeError('Given formatter must deliver a str')
        return formatter, _CALL
    elif type(formatter) is str:
        formatter = formatter.strip(' ')
        if formatter[0] == '{':
            return formatter, _FORMAT
        return formatter, _OLD
    raise TypeError('Given formatter is no string or Callable')


class mSetItem():
    """
    item object to used in the different mSet objects
    Depending on the object it is a "normal" item (`mSetRoster`) or it is the lower or upper limit
    of the `mSetInterval` object.
    In first case complemented items will be ignored.

    The object contains a formatting option to define how the string representation of the item should look like.
    Especially integer formatting is used to to create representations of the other base like hex or octal.

    :type value: object
    :param value: numerical value to be stored in object or definition str the user can give also a variable-name here
    :type complement: bool
    :param complement: complement type item (only required for interval limits
    :type fromatter: Union[Callable,str]
    :param formatter: explicit formatter user can give as formatter
                      1. formatter method (callable)
                      2. escape string for `format()` method
                      3 escape string for classical "%" replacement

    """

    def __init__(self, value, complement=False, formatter=str):
        """
        :type value: object
        :param value: numerical value to be stored in object or definition str the user can give also a variable-name here
        :type complement: bool
        :param complement: complement type item (only required for interval limits
        :type fromatter: Union[Callable,str]
        :param formatter: explicit formatter user can give as formatter
                          1. formatter method (callable)
                          2. escape string for `format()` method
                          3 escape string for classical "%" replacement
        """
        self._complement = bool(complement)
        self._is_var = False
        formatter = _get_formatter_type(formatter)
        if type(value) is str:
            value = value.strip(' ')
            if value[0] in _VAR_START_CHARACTERS and value != 'inf':
                var_chars = _VAR_CHARACTERS
                for c in value:
                    if c not in var_chars:
                        raise TypeError('Given variable name contains invalid characters (%s)' % repr(c))
                self._is_var = True
            elif value[0] in _NUMBER_START_CHARACTERS:
                if value[0] == '-':
                    factor = -1
                    value = value[1:].strip(' ')
                elif value[0] == '+':
                    factor = 1
                    value = value[1:].strip(' ')
                else:
                    factor = 1
                # we try to extract a number from the input string
                if value == 'inf':
                    value = float('inf')
                else:
                    i = value.find('.')
                    try:
                        if i == -1:
                            if value[0] == '0':
                                if value[1].lower() == 'x':
                                    value = int(value, 16)
                                    formatter = hex, 0
                                elif value[1].lower() == 'o':
                                    value = int(value, 8)
                                    formatter = oct, 0
                                elif value[1].lower() == 'b':
                                    value = int(value, 2)
                                    formatter = bin, 0
                                else:
                                    value = int(value)
                            else:
                                value = int(value)
                        else:
                            if formatter[0] is str:
                                i2 = -1
                                if 'e' in value:
                                    i2 = value.find('e')
                                elif 'E' in value:
                                    i2 = value.find('E')
                                if i2 != -1:
                                    formatter = '{:%i.%ie}' % (i, i2 - i - 1), _FORMAT
                                else:
                                    formatter = '{:%i.%if}' % (i, len(value) - i - 1), _FORMAT
                            value = float(value)
                    except:
                        raise TypeError(
                            'Given str value cannot be interpreted as an %s object' % self.__class__.__name__)
                value = value * factor
            else:
                raise TypeError('Given str value cannot be interpreted as an %s object' % self.__class__.__name__)

        else:
            # we check if the given value is a number by casting it to float
            try:
                float(value)
            except TypeError:
                raise TypeError('Give value is not a numeric type that is supported by this class')
        self._formatter = formatter
        self._value = value

    @property
    def is_mSetItem(self):
        """
        Property used for identification of the object

        :rtype: bool
        :return: True
        """
        return True

    @property
    def is_complement(self):
        """
        property tells if the object is complement

        :rtype: bool
        :return: True/False
        """
        return self._complement

    @property
    def value(self):
        """
        property contains the value of the item
        :return: value of the object
        """
        return self._value

    @property
    def formatter(self):
        """
        property delivers the formatter of the object

        :rtype: Union[Callable,str]
        :return: formatter object (Callable or string)
        """
        return self._formatter[0]

    @property
    def formatter_type(self):
        """
        property delivers the formatter type integer constant of the object formatter

        :rtype: int
        :return: formatter type integer ( `_CALL`~0;,`_FORMAT`~1; ,`_OLD`~2 )
        """
        return self._formatter[1]

    @property
    def is_var(self):
        """
        property returns if the value is a variable name or a normal numerical value

        :rtype: bool
        :return: True - is variable; False - normal numerical value
        """
        return self._is_var

    def get_init_args(self, full=False):
        """
        get the initial arguments for instance the object

        :type full: bool
        :param full: do not shorten even that we have default values

        :rtype: tuple
        :return: tuple of init arguments
        """
        if full or self._formatter[0] is not str:
            return (self._value, self._complement, self._formatter[0])
        elif self._complement:
            return (self._value, self._complement)
        else:
            return (self._value,)

    def math_repr(self, formatter=None):
        """
        delivers the formatted value
        :rtype formatter: Union[Callable,str,None][
        :param formatter: optionally an explicit formatter can be given

        :rtype: str
        :return: Formatted value stored in the `mSetItem`-object
        """
        if self.is_var:
            return self._value
        if formatter:
            formatter = _get_formatter_type(formatter)
        else:
            formatter = self._formatter
        if formatter[1] == _CALL:
            return formatter[0](self._value)
        elif formatter[1] == _FORMAT:
            return formatter[0].format(self._value)
        else:
            return formatter[0] % (self._value)

    def __gt__(self, other):
        """
        greater than given other object
        :param other: object self is compared to
        :return: True self is larger or False other is larger
        """
        if self.is_var or hasattr(other, 'is_var') and other.is_var:
            return None
        if hasattr(other, 'value'):
            return self._value > other.value
        else:
            return self._value > other

    def __lt__(self, other):
        """
        smaller than given other object
        :param other: object self is compared to
        :return: True self is smaller or False other is smaller
        """
        if self.is_var or hasattr(other, 'is_var') and other.is_var:
            return None
        if hasattr(other, 'value'):
            return self._value < other.value
        else:
            return self._value < other

    def __ge__(self, other):
        """
        greater or equal than given other object
        :param other: object self is compared to
        :return: True self is larger or equal; or False other is larger
        """

        if self.is_var or hasattr(other, 'is_var') and other.is_var:
            return None
        if hasattr(other, 'value'):
            return self._value >= other.value
        else:
            return self._value >= other

    def __le__(self, other):
        """
        smaller or equal than given other object
        :param other: object self is compared to
        :return: True self is smaller or equal; or False other is smaller
        """
        if self.is_var or hasattr(other, 'is_var') and other.is_var:
            return None
        if hasattr(other, 'value'):
            return self._value <= other.value
        else:
            return self._value <= other

    def __eq__(self, other):
        """
        other is same object from the content?
        :param other: other object
        :return: True ~ other has equal content; False ~ other has different content
        """
        if hasattr(other, 'is_mSetItem'):
            if (self.is_complement + other.is_complement) & 0b1:  # XOR for complements
                return self._value != other.value
            else:
                return self._value == other.value
        else:
            if self._complement:
                return self._value != other
            else:
                return self._value == other

    def __float__(self):
        """
        converts (casts) stored value in a float

        In case conversion is not possible (variable) float('NaN') is returned

        :rtype: float
        :return: float conversion result
        """
        if self.is_var:
            return float('NaN')
        return float(self._value)

    def __repr__(self):
        """
        string representation
        :rtype: str
        :return: representation string of the object
        """
        out = [self.__class__.__name__, '(']
        value = self._value
        if value == float('inf') or value == float('-inf') or self.is_var:
            v = "'%s'" % str(value)
        else:
            v = repr(self._value)
        out.append(v)
        out.append(', ')
        args = self.get_init_args()[1:]
        for arg in args:
            out.append(repr(arg))
            out.append(', ')
        out[-1] = ')'
        return ''.join(out)

    def __str__(self):
        """
        string representation using math_repr() as parameter
        :rtype: str
        :return: representation string
        """
        out = [self.__class__.__name__, '(']
        if self.is_var:
            out.append(repr(self._value))
        else:
            out.append(self.math_repr())
        out.append(', ')
        args = self.get_init_args()[1:]
        for arg in args:
            out.append(repr(arg))
            out.append(', ')
        out[-1] = ')'
        return ''.join(out)

    def __hash__(self):
        if self._complement:
            return hash((self._value, self._complement))
        return hash(self._value)


class _mSetBase(abc.ABC):
    """
    super class for all mSet objects

    handles two parameters
    :param vars: variable names set
    :param complement: complement flag


    """

    def __init__(self, vars, complement=False):
        """
        handles two parameters
        :param vars: variable names set
        :param complement: complement flag
        """
        self._complement = bool(complement)
        self._vars = vars

    def __len__(self):
        """
        The cardinality is somehow the size of the set it delivers how many items the set contains.
        The result is not in all cases correct furthermore it is just an estimation!

        In many cases in float intervals the user will find infinite as the result of the operation.
        :return: number of items integer or float('inf') for infinite results
        """
        return self.cardinality()

    def __sub__(self, other):
        # intersection
        return mSetCombine(self, other, False)

    def __add__(self, other):
        # union
        return mSetCombine(self, other, True)

    @property
    def is_mSet(self):
        """
        used for object identification

        :rtype: bool
        :return: True
        """
        return True

    @property
    def is_complement(self):
        """
        is this a complemented set?

        :rtype: bool
        :return: True is complemented; False is normal
        """
        return self._complement

    def switch_complement(self):
        """
        switch the complement flag

        :rtype: bool
        :return: current complement flag (after switching)
        """
        self._complement = complement = not self._complement
        return complement

    @property
    def has_vars(self):
        """
        do we  have variables in the object?

        :rtype: bool
        :return: True we have variables; False we don't have variables
        """
        return bool(len(self._vars))

    @property
    def vars(self):
        """
        deliver set of variable names
a       :rtype: set
        :return: set of variable names
        """
        return self._vars

    @abc.abstractmethod
    def cardinality(self):
        """
        The cardinality is somehow the size of the set it delivers how many items the set contains.
        The result is not in all cases correct furthermore it is just an estimation!

        In many cases in float intervals the user will find infinite as the result of the operation.
        :return: number of items integer or float('inf') for infinite results
        """
        pass

    @abc.abstractmethod
    def is_empty_set(self):
        """
        For some set definition no matching item can be found! Then the set is equal to the empty set and this property
        will deliver True

        :rtype: bool
        :return: True is empty set; False set contains items
        """
        pass

    @abc.abstractmethod
    def is_empty_set_complement(self):
        """
        For some set definition no matching item can be found! Then the set is equal to the empty set. Here we do
        not check the set itself, we check if the complement of the set is empty. Somehow if this property
        delivers True we can say that the set is the universal set.
        :rtype: bool
        :return: True is full/universal set (complement is empty);
                 False is not full/universal set (complement is not empty)
        """
        pass

    @abc.abstractmethod
    def __contains__(self, value, vars_dict=None):
        """
        checks if given value is inside the set (This is the main function of the whole object!)

        :type value: Union[iterable,Numeric,tuple]
        :param value: value to be checked if it is in. Because "in" supports no parameters the vars_dict
                      can be given as a tuple in the form: (value, vars_dict) in this_object

        :type vars_dict: dict
        :param vars_dict: optional replacement dict for variable items

        :rtype: bool
        :return: True is in; False is not in the set
        """
        pass

    @abc.abstractmethod
    def __repr__(self):
        """
        create representation string

        :rtype: str
        :return: representation string
        """
        pass

    @abc.abstractmethod
    def __str__(self):
        """
        create representation string us math_repr as parameter

        :rtype: str
        :return:representation str
        """
        pass

    def __call__(self, value, vars_dict=None):
        """
        Use method like call to check if the given value is in this object.
        Same as __contains__()

        :param value: value to be checked
        :param vars_dict: variables replacement dict
        :return: True/False
        """
        return self.__contains__(value, vars_dict)

    @abc.abstractmethod
    def iter_in(self, value, vars_dict=None):
        """
        For each item in the given iterable value we check if the item is in this mSet object the
        result is a iterable over the single results
        :param value: to be checked iterable value (single item check)
        :param vars_dict: variable replacement dict
        :return: iterable True\False
        """
        pass

    @abc.abstractmethod
    def filter(self, value, vars_dict=None):
        """
        For each item in the given iterable value we check if the item is in this mSet object or not in case it is in
        the item will be delivered back if not it is skipped

        :param value: iterable value which items will be checked
        :param vars_dict: variable replacement dict
        :return: iterable of matching items
        """
        pass

    @abc.abstractmethod
    def get_init_args(self, full=False):
        """
        delivers tuple of all initial arguments given to instance the mSet object
        :param full: True all arguments given also defaults
        :return: tuple of initial arguments
        """
        pass

    @abc.abstractmethod
    def math_repr(self):
        """
        mathematical representation of the object (we try to match as good as possible to the
        mathematical standards here but we avoid exotic characters!
        :return: mathematical representation string
        """
        pass


class mSetInterval(_mSetBase):
    """
    Mathematical interval set object. Here the user can define a mathematical interval with closed or open boarders.

    For more details related to mathematical intervals you may have a look here:
    https://en.wikipedia.org/wiki/Interval_(mathematics)


    """

    _REGEX_MATH_REP_DEF = r'(\!\(|\!\[|\(|\[)(.+)+(,|\.\.)(.+)+(\)\'|\]\'|\)|\])'
    _REGEX_MATH_REP = re.compile(_REGEX_MATH_REP_DEF)
    # group 1: ( or { or !( or !{
    # group 2: lower value
    # group 3 , or ..
    # group 4 upper value
    # group 5 ) or } or )' or }'
    # pre-condition: all spaces are eliminated!
    _REGEX_BUILDER_DEF = r'(\!\{|\{)([a-zA-Z])(\|)' \
                         r'(((?P<lv1>[a-zA-Z\d\.\_\+\-]*)' \
                         r'(((?P<lo12>\<\=|\>\=|\<|\>)\2(?P<uo12>\<\=|\<|\>\=|\>))|' \
                         r'((?<=\|)\2(?P<uo1>\!\=\=|\!\=|\=\=|\=|\<\=|\<|\>\=|\>|E|e))|' \
                         r'((?P<lo1>\!\=\=|\!\=|\=\=|\<\=|\>\=|\=|\<|\>)\2(?=\,)))' \
                         r'(?P<uv1>[a-zA-Z\d\.\_\+\-]*)\,)?' \
                         r'((?P<lv2>[a-zA-Z\d\.\_\+\-]*)' \
                         r'(((?P<lo22>\<\=|\>\=|\<|\>)\2(?P<uo22>\<\=|\<|\>\=|\>))|' \
                         r'((?<=(\,|\|))\2(?P<uo2>\!\=\=|\!\=|\=\=|\=|\<\=|\<|\>\=|\>|E|e))|' \
                         r'((?P<lo2>\!\=\=|\!\=|\=\=|\<\=|\>\=|\=|\<|\>)\2(?=\})))' \
                         r'(?P<uv2>[a-zA-Z\d\.\_\+\-]*)))' \
                         r'(\}\'|\})'
    _REGEX_BUILDER = re.compile(_REGEX_BUILDER_DEF)

    # group 1 { or !{
    # group2 varname
    # group 3 |
    # group4 full content
    # we allow here maximum 2 more sub-groups (comma separated)
    # first part exists only in case a comma separator is used
    # group 6 lower_value 1 (2 operator definition)
    # group 9 lower_operator 1 (2 operator definition)
    # group 10 upper_operator 1 (2 operator definition)
    # group 12 upper_operator 1 (1 operator)
    # group 14 lower_operator 1 (1 operator definition)
    # group 15 upper_value 1 (or set type)
    # These groups should always exists somehow:
    # group 17 lower_value 2
    # group 20 lower value operator 2 (2 operator definition)
    # group 26 lower value operator 2 (1 operator definition variable left)
    # group 21 upper value operator 2 (2 operator definition) (can be also e or E for element)
    # group 24 upper value operator 2 (1 operator) (can be also e or E for element)
    # group 27 upper_value 2 (or set type)
    # number of sub-sub-groups depend on the content
    # last group contains the ending } or }'

    def __init__(self, *definition, lower=None, upper=None, int_only=False, complement=False):
        """

        :param definition: pointer to all unnamed parameters given
                           If only one is given and the one is a string the parsers try to extract/construct the
                           interval object from the given mathematical interval definition given.
                           We support direct definitions like "[1,2]" (closed) or "(1,2)" (open) but also
                           most type builder definitions are supported like {x| 2<=x<1} ~ (1,2]
                           To define integer based intervals the user must use ".." instead of "," as seperator:
                           [1,2] ~ float and [1..2] ~ int
                           For builder definitions the user can use numerical set domains to define the number type:
                           {x|x e Z, 2<=x<1} ~[(1..2] ~ int definition
                           The numerical set domain can be in most cases extended by 0+- to limit the valid range:
                           e.g: Z,Z+,Z0+,Z-,Z0-
                           Finally we have also a simplified builder definition available with the fixed variable name x
                           for floats and n for integers:
                           2>=x>1 ~ (1,2] or 2>=n>1 ~ (1..2]
                           If one limit is not given it will be set to the maximum
                           (lower ~ float('-inf') and upper ~ float('inf')
        :param lower: lower limit value (Give tuple (value,True) for open definitions
                            or mSetItem(value,complement=True, formatter='%e') (with formatter example)
        :param upper: upper limit value (Give tuple (value,True) for open definitions
                            or mSetItem(value,complement=True, formatter='%e') (formatter example)
        :param int_only: Flag for integer only intervals True ~ int; Flase ~ float
        :param complement: Interval complement
        """
        self._int_only = bool(int_only)
        s = len(definition)
        paras = None
        if s > 0:
            if lower is not None:
                raise TypeError('Unnamed and named parameters are in conflict')
            t = type(definition[0])
            if t is mSetItem:
                lower = definition[0]
            elif definition[0] is None:
                lower = mSetItem(float('-inf'))
            elif t is tuple:
                lower = mSetItem(*definition[0])
            elif t is str:
                def_str = definition[0].strip(' ')
                if def_str[0] == '!':
                    pre_complement_found = True
                    def_str = def_str[1:].strip(' ')
                else:
                    pre_complement_found = False
                if def_str[0] == '[' or def_str[0] == '(':
                    paras = self._parse_math_definition_str(def_str, pre_complement_found)
                elif def_str[0] == '{':
                    paras = self._parse_builder_definition_str(def_str, pre_complement_found)
                else:
                    try:
                        lower = mSetItem(definition[0])
                    except:
                        if 'x' in def_str:  # simplified definition using "x" given?
                            try:
                                paras = self._parse_builder_definition_str('{x|' + def_str + '}', pre_complement_found)
                            except:
                                raise TypeError('Issue with first parameter given, argument parsing failed')
                        elif 'n' in def_str:  # simplified definition using "x" given?
                            try:
                                paras = self._parse_builder_definition_str('{n|neZ,' + def_str + '}',
                                                                           pre_complement_found)
                            except:
                                raise TypeError('Issue with first parameter given, argument parsing failed')

                        else:
                            raise
            else:
                lower = mSetItem(definition[0])
        if paras:
            if upper is not None:
                raise TypeError('Unnamed and named parameters are in conflict')
            lower = paras[0]
            upper = paras[1]
            if s > 1:
                self._int_only = definition[1] or self._int_only
            self._int_only = paras[2] or self._int_only

            if s > 2:
                complement = definition[2] or complement
            complement = paras[3] or complement
            if s > 3:
                raise TypeError('Too many unnamed parameters given')
        else:
            if s > 1:
                if upper is not None:
                    raise TypeError('Unnamed and named parameters are in conflict')
                t = type(definition[1])
                if t is mSetItem:
                    upper = definition[1]
                elif definition[1] is None:
                    upper = mSetItem(float('inf'))
                elif t is tuple:
                    upper = mSetItem(*definition[1])
                else:
                    upper = mSetItem(definition[1])
            if s > 2:
                self._int_only = definition[2] or self._int_only
            if s > 3:
                complement = definition[3] or complement
            if s > 4:
                raise TypeError('Too many unnamed parameters given')
        t = type(lower)
        if t is not mSetItem:
            if lower is None:
                lower = mSetItem(float('-inf'))
            elif t is tuple:
                lower = mSetItem(*lower)
            else:
                lower = mSetItem(lower)
        t = type(upper)
        if t is not mSetItem:
            if upper is None:
                upper = mSetItem(float('inf'))
            elif t is tuple:
                upper = mSetItem(*upper)
            else:
                upper = mSetItem(upper)
        vars = set()
        if lower.is_var:
            vars.add(lower._value)
        if upper.is_var:
            vars.add(upper._value)
        super().__init__(vars, complement)
        if not vars:
            if lower > upper:
                # switch order
                lower, upper = upper, lower
        self._lower_op = lt if lower.is_complement else le
        self._upper_op = gt if upper.is_complement else ge
        if upper.value == lower.value and (self._lower_op == le or self._upper_op == ge):
            self._lower_op = le
            self._upper_op = ge
        self._upper = upper
        self._lower = lower

    @property
    def is_lower_closed(self):
        """
        do we have a closed lower limit "("
        :return: True is closed, False is open
        """
        return not self._lower.is_complement

    @property
    def is_lower_open(self):
        """
        do we have a open lower limit "("
        :return: True is open, False is closed
        """
        return self._lower.is_complement

    @property
    def lower_value(self):
        """
        Property delivers the lower limit value
        :return: value of the lower limit
        """

        return self._lower.value

    @property
    def is_upper_closed(self):
        """
        do we have a closed upper limit "("
        :return: True is closed, False is open
        """
        return not self._upper.is_complement

    @property
    def is_upper_open(self):
        """
        do we have a open upper limit "("
        :return: True is open, False is closed
        """
        return self._upper.is_complement

    @property
    def upper_value(self):
        """
        Property delivers the upper limit value
        :return: value of the upper limit
        """
        return self._upper.value

    @property
    def is_int_only(self):
        """
        Is this an integer number only interval?
        :return:
        """
        return self._int_only

    def _cardinality_without_complement(self):
        """
        Helper function to calculate the cardinality (size/number of items)
        :return: integer or float('inf')
        """
        if self._vars:
            if self._upper.value == self._lower.value:
                if self._lower._complement and self._upper._complement:
                    return 0
                else:
                    return 1
            else:
                return float('inf')
        elif self._int_only:
            if self._lower.is_complement:
                lower = self._lower.value + 1
            else:
                lower = self._lower.value
            if self._upper.is_complement:
                upper = self._upper.value - 1
            else:
                upper = self._upper.value
            diff = (upper - lower) + 1
            if diff < 0:
                return 0
            elif diff == 0 and not (self._upper.is_complement and self._lower.is_complement):
                return 1
            return diff
        else:
            if self._upper.value == self._lower.value:
                if self._lower._complement and self._upper._complement:
                    return 0
                else:
                    return 1
            else:
                return float('inf')

    @property
    def cardinality(self):
        """
        The cardinality is somehow the size of the set it delivers how many items the set contains.
        The result is not in all cases correct furthermore it is just an estimation!

        In many cases in float intervals the user will find infinite as the result of the operation.
        :return: number of items integer or float('inf') for infinite results
        """
        c = self._cardinality_without_complement()
        if self._complement:
            if c == float('inf') and self._lower.value == float('-inf') and self._upper.value == float('inf'):
                return 0
            else:
                return float('inf')
        else:
            return c

    @property
    def is_empty_set(self):
        """
        Is the interval same as an empty set (no item inside)
        :return: True is empty; False is not empty
        """

        if self.is_complement:
            return False
        return self._cardinality_without_complement() == 0

    @property
    def is_empty_set_complement(self):
        """
        Is the complement interval same as an empty set (no item inside). If this is the case the set is the universal
        set (any item inside). But this is a relative definition to the "universe". E.g. strings will never be found
        inside a numerical set they are not in the "universe".

        :return: True complement is empty; False complement is not empty
        """
        if not self.is_complement:
            return False
        return self._cardinality_without_complement() == 0

    def _get_lower_upper(self, vars_dict=None):
        """
        helper method to replace variable boarders with real values
        :param vars_dict: dict containing the replacement values for the variables
        :return: replaced values of the limits
        """
        lower = self._lower.value
        upper = self._upper.value
        if vars_dict is None or not self._vars:
            return lower, upper
        for key in self._vars:
            if key in vars_dict:
                if key == lower:
                    lower = vars_dict[key]
                if key == upper:
                    upper = vars_dict[key]
        return lower, upper

    def _parse_math_definition_str(self, definition, pre_complement=False):
        """
        parser for math_rper strings given to instance the object
        :param definition: definition string
        :param pre_complement: complement flag that is pre parsed
        :return: parameter set for the instance
        """
        def_str = definition.replace(' ', '')
        match = self._REGEX_MATH_REP.match(def_str)
        if match:
            if match.end() != len(def_str):
                raise TypeError('After parsing additional characters found in the definition, somethings wrong')
            groups = match.groups()
            # how many main groups we have?
            try:
                lower = mSetItem(groups[1], groups[0] == '(')
                if lower.is_var:
                    if groups[1] not in definition:
                        raise TypeError('Spaces found in variable name (lower), this is not supported')
            except:
                raise TypeError('Something is wrong with the lower value, not interpretable')
            try:
                upper = mSetItem(groups[3], groups[4][0] == ')')
                if upper.is_var:
                    if groups[3] not in definition:
                        raise TypeError('Spaces found in variable name (upper), this is not supported')
            except:
                raise TypeError('Something is wrong with the upper value, not  interpretable')
            is_int = groups[2] == '..'
            complement = (pre_complement + int(groups[4][-1] == "'")) & 0b1
            return lower, upper, is_int, complement
        else:
            raise TypeError('Parsing error given interval definition')

    def _get_set_data(self, set_def_str):
        """
        helper function for numerical domians
        :param set_def_str: definition string for the numerical domain
        :return: tuple with (integer True/False,lower_limit,upper_limit)
        """
        set_def_str = set_def_str.replace('Integer', 'Z').replace('integer', 'Z').replace('int', 'Z')
        set_def_str = set_def_str.replace('Float', 'R').replace('float', 'R').replace('Double', 'R').replace('double',
                                                                                                             'R')
        if set_def_str in {'bool', 'boolean', 'Boolean', 'N01', 'N10'}:
            return True, 0, 1
        s = len(set_def_str)
        if s == 0:
            raise TypeError('Missing numerical set definition')
        if set_def_str[0] == 'N':
            if s == 1:
                return True, 0, float('inf')
            elif s == 2:
                if set_def_str[1] == '+':
                    return True, 1, float('inf')
                elif set_def_str[1] == '0':
                    return True, 0, float('inf')
            elif s == 3:
                if set_def_str[1] == '+':
                    if set_def_str[2] == '0':
                        return True, 0, float('inf')
                elif set_def_str[1] == '0':
                    if set_def_str[2] == '+':
                        return True, 0, float('inf')
        else:  # the rest has same limits!
            is_int = False
            if set_def_str[0] == 'Z':
                is_int = True
            if s == 1:
                return is_int, float('-inf'), float('inf')
            elif s == 2:
                if set_def_str[1] == '+':
                    return is_int, (0, True), float('inf')
                elif set_def_str[1] == '0':
                    return is_int, float('-inf'), float('inf')
                elif set_def_str[1] == '-':
                    return is_int, float('-inf'), (0, True)
            elif s == 3:
                if set_def_str[1] == '+':
                    if set_def_str[2] == '0':
                        return is_int, 0, float('inf')
                        # We don't support R+- user should use x!=1 instead
                elif set_def_str[1] == '-':
                    if set_def_str[2] == '0':
                        return is_int, float('-inf'), 0
                elif set_def_str[1] == '0':
                    if set_def_str[2] == '-':
                        return is_int, float('-inf'), 0
                    elif set_def_str[2] == '+':
                        return is_int, 0, float('inf')
        raise TypeError('Unsupported set definition %s' % (repr(set_def_str)))

    def _replace_lower_limit(self, old, new_limit, is_equal):
        """
        helper function to replaced lower limits with later parsed limit?
        :param old: old value
        :param new_limit: new_value
        :param is_equal: is equal already detected (limits possibilities)
        :return: mSetItem of the current lower limit
        """
        if old is None:
            return mSetItem(new_limit)
        if is_equal:
            raise TypeError('Definition mixes a equal limits with range limits on the lower side')
        if old.has_vars:
            raise TypeError('Definition mixes a variable limit with a fixed limit on the lower side')
        t = type(new_limit)
        if t is tuple:
            # open boarder!
            if old < new_limit[0]:
                return mSetItem(new_limit)
        elif t is mSetItem:
            if new_limit.has_vars:
                raise TypeError('Definition mixes a variable limit with a fixed limit on the lower side')
            if new_limit.is_complement:
                if old < new_limit:
                    return mSetItem(new_limit)
            elif old <= new_limit:
                return mSetItem(new_limit)
        elif old <= new_limit:
            return mSetItem(new_limit)
        return old

    def _replace_upper_limit(self, old, new_limit, is_equal):
        """
        helper function to replaced upper limits with later parsed limit?
        :param old: old value
        :param new_limit: new_value
        :param is_equal: is equal already detected (limits possibilities)
        :return: mSetItem of the current lower limit
        """

        if old is None:
            if type(new_limit) is tuple:
                return mSetItem(*new_limit)
            return mSetItem(new_limit)
        if is_equal:
            raise TypeError('Definition mixes a equal limits with range limits on the upper side')
        if old.is_var:
            raise TypeError('Definition mixes a variable limit with a fixed limit on the upper side')
        t = type(new_limit)
        if t is tuple:
            # open boarder!
            if old > new_limit[0]:
                return mSetItem(new_limit)
        elif t is mSetItem:
            if new_limit.is_var:
                raise TypeError('Definition mixes a variable limit with a fixed limit on the upper side')
            if new_limit.is_complement:
                if old > new_limit:
                    return mSetItem(new_limit)
            elif old >= new_limit:
                return mSetItem(new_limit)
        elif old >= new_limit:
            return mSetItem(new_limit)
        return old

    def _parse_builder_definition_str(self, definition, pre_complement=False):
        """
        Parser and mapper for interval definitions in builder style

        The parser is very complex and the mapping of the results to the parameters is even more complex.

        For details see:
        https://en.wikipedia.org/wiki/Interval_(mathematics)
        https://en.wikipedia.org/wiki/Set-builder_notation

        Our parser has the following general limits:
            1. Only one "|" is supported
            2. left of the "|" the user must place the notification variable (e.g. x)
            3. just one unique notification variable is supported
            4. right of the "|" the user can place one or two statements which must be separated by a comma ","
            5. A numerical domain can be given via "e" or "E" which stands for "element of"
            6. Equal statements {x|x=1} cannot be combined with other statements but the complement
               is supported in the operator too ("!=")
            7. Complement can be given as leading "!" or as post "'" (must be escaped in python string definitions)
            8. Multiple complements wil neutralize each other finally a even number of complements will
               lead into a not complemented interval

        In general the following numerical sets are supported as domains:
            * N -> [0..inf] natural numbers incl. zero
            * N+ -> [1..inf] natural numbers without zero
            * N0+ -> [0..inf] natural numbers incl. zero (explicit)
            * Z -> [-inf..inf] integers (following names can be used as replacement (only without extensions): int,integer,Integer)
            * Z+ -> [1..inf]
            * Z0+ -> [0..inf]
            * Z- -> [-inf..-1]
            * Z0- -> [-inf..0]
            * Q -> [-inf..inf] rational numbers and real numbers are internally handled as the same (floats)
                               (Following replacements accepted: R (with extensions), float, Float, double, Double)
            * Q+ -> (0)..inf]
            * Q0+ -> [0..inf]
            * Q- -> [-inf..0)
            * Q0- -> [-inf..0]
        Additionally we support:
            * bool or Boolean [0..1] but it's very highly recommended not to mix such a definition with other statements
            in this case the user should just place an x on the right hand side.


        As explained we support a logical subset of possibilities but we did not extend the already very complex
        parser to cover more corner cases. The user should try to find the easiest logical notification.
        E.g:
        "{x| x e N0+- , x>10}"  will raise a TypeError because of N0+- (what should be the minus in this case?) is not supported
        "{x| x e N0+ , x>10}" -> (10..inf]  will work but the interpretation will take a lot of time
        Recommended would be : {x| x e Z, x> 10}  -> (10..inf]
        The set N makes only sense for definitions targeting in the other direction:
        {x| x e N+, x><10} -> (0..10)

        We give here some examples which should be logically clear and simple formed:
            * {b| b e bool} -> [0..1]
            * {n| n e N , n<256 } -> [0..256)
            * {z|  -128<=z<128, z e Z } -> [-128..128)
            * {x| -70000.555<=x<=,80000.555} -> [-70000.555,80000.555]
            * {x| x=0}} -> [0,0]
            * {x| x!=0}} -> ![0,0]
        Less good but still possible definitions are:
            * {x| -70000.555<=x ,80000.555>=x} -> [-70000.555,80000.555] it's always better to use statements like 1<=x<=2
            * !{x| x!=0}}' -> ![0,0] (triple complement)
            * !{x| x!=0}} -> [0,0] (dual complement)
            * {n| n e Z0+ , n>256 } -> (256)..inf] Z0+ is not required just put Z
            * {x| x>10 , x>256 } -> (256,inf] avoid duplicated limits in same direction
        And this will crash
            * {x| x==10 , x>256 } -> TypeError (equal mixed with other operation)
            * {x| x==10 , x e N } -> TypeError (equal mixed with other operation) we deny this because there are to many cornercases that must be covered!
            * {n| n e Z0+- , n>256 } -> TypeError (Z0+- not supported)
            * {x| x==10 , x e N } -> TypeError (equal mixed with other operation)


        :param definition: definition string
        :param pre_complement: is pre complement already detected (leading "!"
        :return: New parameter set for mSetInterval
        """
        def_str = definition.replace(' ', '')
        match = self._REGEX_BUILDER.match(def_str)
        if match:
            if match.end() != len(def_str):
                raise TypeError('After parsing additional characters found in the definition, somethings wrong')
            groups = match.groupdict()
            if groups['lv1'] or groups['uv1']:
                # two main groups
                upper = None
                lower = None
                is_int = False
                is_equal = False
                lo = groups['lo1']
                uo = groups['uo1']
                lo2 = groups['lo12']
                uo2 = groups['uo12']
                if lo2:
                    lo = lo2
                if uo2:
                    uo = uo2
                if lo is None:
                    pass
                elif lo == '>=':  # upper limit
                    upper = self._replace_upper_limit(upper, mSetItem(groups['lv1']), is_equal)
                elif lo == '>':  # upper limit
                    upper = self._replace_upper_limit(upper, mSetItem(groups['lv1'], True), is_equal)
                elif lo == '<=':
                    lower = self._replace_lower_limit(lower, mSetItem(groups['lv1']), is_equal)
                elif lo == '<':
                    lower = self._replace_lower_limit(lower, mSetItem(groups['lv1'], True), is_equal)
                elif lo[-1] == '=':
                    raise TypeError('Equal operator definitions cannot be mixed with other operators')
                elif lo == 'e' or lo == 'E':
                    numerical_set = groups['uv1']
                    is_int, lower_limit, upper_limit = self._get_set_data(numerical_set)
                    # here we have a very special case of equal definition afterwards which would lead into issues:
                    # therefore we will return already here in this case
                    lo = groups['lo2']
                    uo = groups['uo2']
                    lo2 = groups['lo22']
                    uo2 = groups['uo22']
                    if lo2:
                        lo = lo2
                    if uo2:
                        uo = uo2
                    if lo in {'!=', '!==', '==', '='}:
                        raise TypeError('Equal operator definitions cannot be mixed with other operators')
                    if uo in {'!=', '!==', '==', '='}:
                        raise TypeError('Equal operator definitions cannot be mixed with other operators')
                    lower = self._replace_upper_limit(lower, lower_limit, False)  # ignore equal flag
                    upper = self._replace_upper_limit(upper, upper_limit, False)
                else:
                    raise TypeError('Parsed operator %s invalid' % repr(lo2))
                if uo is None:
                    pass
                elif uo == '>=':  # lower limit
                    lower = self._replace_lower_limit(lower, mSetItem(groups['uv1']), is_equal)
                elif uo == '>':  # lower limit
                    lower = self._replace_lower_limit(lower, mSetItem(groups['uv1'], True), is_equal)
                elif uo == '<=':
                    upper = self._replace_upper_limit(upper, mSetItem(groups['uv1']), is_equal)
                elif uo == '<':
                    upper = self._replace_upper_limit(upper, mSetItem(groups['uv1'], True), is_equal)
                elif uo[-1] == '=':
                    raise TypeError('Equal operator definitions cannot be mixed with other operators')
                elif uo == 'e' or uo == 'E':
                    numerical_set = groups['uv1']
                    is_int, lower_limit, upper_limit = self._get_set_data(numerical_set)
                    # here we have a very special case of equal definition afterwards which would lead into issues:
                    # therefore we will return already here in this case
                    lo = groups['lo2']
                    uo = groups['uo2']
                    lo2 = groups['lo22']
                    uo2 = groups['uo22']
                    if lo2:
                        lo = lo2
                    if uo2:
                        uo = uo2
                    if lo in {'!=', '!==', '==', '='}:
                        raise TypeError('Equal operator definitions cannot be mixed with other operators')
                    if uo in {'!=', '!==', '==', '='}:
                        raise TypeError('Equal operator definitions cannot be mixed with other operators')
                    lower = self._replace_upper_limit(lower, lower_limit, False)  # ignore equal flag
                    upper = self._replace_upper_limit(upper, upper_limit, False)

                else:
                    raise TypeError('Parsed operator %s invalid' % repr(uo2))

            else:
                # one main group only
                upper = None
                lower = None
                is_int = False
                is_equal = False
            lo = groups['lo2']
            uo = groups['uo2']
            lo2 = groups['lo22']
            uo2 = groups['uo22']
            if lo2:
                lo = lo2
            if uo2:
                uo = uo2
            if lo is None:
                pass
            elif lo == '>=':  # upper limit
                upper = self._replace_upper_limit(upper, mSetItem(groups['lv2']), is_equal)
            elif lo == '>':  # upper limit
                upper = self._replace_upper_limit(upper, mSetItem(groups['lv2'], True), is_equal)
            elif lo == '<=':
                lower = self._replace_lower_limit(lower, mSetItem(groups['lv2']), is_equal)
            elif lo == '<':
                lower = self._replace_lower_limit(lower, mSetItem(groups['lv2'], True), is_equal)
            elif lo == '==' or lo == '=':
                if lower or upper:
                    raise TypeError('Equal operator definitions cannot be mixed with other operators')
                is_equal = True
                lower = mSetItem(groups['lv2'])
                upper = lower
            elif lo == '!==' or lo == '!=':
                is_equal = True
                if lower or upper:
                    raise TypeError('Equal operator definitions cannot be mixed with other operators')
                lower = mSetItem(groups['lv2'])
                upper = lower
                pre_complement = (pre_complement + 1) & 0b1
            else:
                raise TypeError('Parsed operator %s invalid' % repr(lo2))
            if uo is None:
                pass
            elif uo == '>=':  # lower limit
                lower = self._replace_lower_limit(lower, mSetItem(groups['uv2']), is_equal)
            elif uo == '>':  # lower limit
                lower = self._replace_lower_limit(lower, mSetItem(groups['uv2'], True), is_equal)
            elif uo == '<=':
                upper = self._replace_upper_limit(upper, mSetItem(groups['uv2']), is_equal)
            elif uo == '<':
                upper = self._replace_upper_limit(upper, mSetItem(groups['uv2'], True), is_equal)
            elif uo == '==' or uo == '=':
                if lower or upper:
                    raise TypeError('Equal operator definitions cannot be mixed with other operators')
                is_equal = True
                lower = mSetItem(groups['uv2'])
                upper = lower
            elif uo == '!==' or uo == '!=':
                if lower or upper:
                    raise TypeError('Equal operator definitions cannot be mixed with other operators')
                is_equal = True
                lower = mSetItem(groups['uv2'])
                upper = lower
                pre_complement = (pre_complement + 1) & 0b1
            elif uo == 'e' or uo == 'E':
                numerical_set = groups['uv2']
                is_int, lower_limit, upper_limit = self._get_set_data(numerical_set)
                lower = self._replace_upper_limit(lower, lower_limit, is_equal)  # ignore equal flag
                upper = self._replace_upper_limit(upper, upper_limit, is_equal)
            else:
                raise TypeError('Parsed operator %s invalid' % repr(uo2))
            complement = (pre_complement + int(match.groups()[27][-1] == "'")) & 0b1
            return lower, upper, is_int, complement
        else:
            raise TypeError('Parsing error given interval definition')

    def __contains__(self, value, vars_dict=None, _limits=None):
        """
        checks if given value is inside the set (This is the main function of the whole object!)

        :type value: Union[iterable,Numeric,tuple]
        :param value: value to be checked if it is in. Because "in" supports no parameters the vars_dict
                      can be given as a tuple in the form: (value, vars_dict) in this_object

        :type vars_dict: dict
        :param vars_dict: optional replacement dict for variable items

        :rtype: bool
        :return: True is in; False is not in the set
        """
        if not vars_dict and type(value) is tuple and len(value) == 2 and type(value[1]) is dict:
            value, vars_dict = value
        if _limits:
            lower, upper = _limits
        else:
            lower, upper = _limits = self._get_lower_upper(vars_dict)
        if hasattr(value, 'capitalize'):
            if self._complement:
                return True
            else:
                return False
        if hasattr(value, '__iter__') or hasattr(value, '__next__'):
            # iterable
            return all(self.__contains__(v, _limits=_limits) for v in value)
        try:
            if self.is_int_only:
                if int(value) != value:
                    result = False
                else:
                    result = self._lower_op(lower, value) and self._upper_op(upper, value)
            else:
                result = self._lower_op(lower, value) and self._upper_op(upper, value)
        except TypeError:
            if self.has_vars:
                if vars_dict is None:
                    raise TypeError('Set contains variables but no vars_dict given')
                not_set_vars = []
                for var in self.vars:
                    if var not in vars_dict:
                        not_set_vars.append(var)
                raise TypeError('Not all required variables set for comparison (%s) ' % repr(not_set_vars)[1:-1])
            else:
                raise

        if self._complement:
            return not result
        else:
            return result

    def __repr__(self):
        """
        string representation
        :rtype: str
        :return: representation string of the object
        """

        out = [self.__class__.__name__, '(', repr(self._lower), ', ', repr(self._upper)]
        if self.is_complement:
            if self.is_int_only:
                out.append(', True')
            else:
                out.append(', False')
            out.append(', True)')
        else:
            if self.is_int_only:
                out.append(', True)')
            else:
                out.append(')')
        return ''.join(out)

    def __str__(self):
        """
        string representation using math_repr() as parameter
        :rtype: str
        :return: representation string
        """

        return ''.join([self.__class__.__name__, '(', repr(self.math_repr()), ')'])

    def __eq__(self, other):
        if type(other) is not mSetInterval:
            return False
        return self.get_init_args() == other.get_init_args()

    def __iter__(self):
        if not self.is_complement and self.is_int_only and not self.has_vars \
                and self._upper.value != float('inf') and self._lower.value != float('-inf'):
            if self._lower.is_complement:
                start = self._lower.value + 1
            else:
                start = self._lower.value
            if self._upper.is_complement:
                end = self._upper.value - 1
            else:
                end = self._upper.value
            if start is None or end is None:
                return
            if start > end:
                return
            elif start == end:
                yield start
            else:
                for i in range(start, end + 1):
                    yield i
        return

    def iter_in(self, value, vars_dict=None):
        """
        For each item in the given iterable value we check if the item is in this mSet object the
        result is a iterable over the single results
        :param value: to be checked iterable value (single item check)
        :param vars_dict: variable replacement dict
        :return: iterable True\False
        """

        limits = self._get_lower_upper(vars_dict)
        for v in value:
            yield self.__contains__(v, _limits=limits)

    def filter(self, value, vars_dict=None):
        """
        For each item in the given iterable value we check if the item is in this mSet object or not in case it is in
        the item will be delivered back if not it is skipped

        :param value: iterable value which items will be checked
        :param vars_dict: variable replacement dict
        :return: iterable of matching items
        """

        limits = self._get_lower_upper(vars_dict)
        for v in value:
            if self.__contains__(v, _limits=limits):
                yield v

    def get_init_args(self, full=False):
        """
        delivers tuple of all initial arguments given to instance the mSet object
        :param full: True all arguments given also defaults
        :return: tuple of initial arguments
        """

        if full or self.is_complement:
            return (self._lower, self._upper, self.is_int_only, True)
        elif self.is_int_only:
            return (self._lower, self._upper, True)
        else:
            return (self._lower, self._upper)

    def math_repr(self, formatters=None):
        """
        mathematical representation of the object (we try to match as good as possible to the
        mathematical standards here but we avoid exotic characters!
        :return: mathematical representation string
        """

        if self.is_complement:
            out = ['!']
        else:
            out = []
        lower = self._lower
        if lower.is_complement:
            out.append('(')
        else:
            out.append('[')
        if formatters:
            out.append(lower.math_repr(formatters[0]))
        else:
            out.append(lower.math_repr())
        if self.is_int_only:
            out.append('..')
        else:
            out.append(',')
        upper = self._upper
        if formatters:
            out.append(upper.math_repr(formatters[1]))
        else:
            out.append(upper.math_repr())
        if upper.is_complement:
            out.append(')')
        else:
            out.append(']')
        return ''.join(out)


class mSetRoster(_mSetBase):

    def __init__(self, *definition, items=None, complement=False):
        item_set = set()
        if items is not None:
            for item in items:
                t = type(item)
                if t is mSetItem:
                    pass
                elif t is tuple():
                    item = mSetItem(*item)
                else:
                    item = mSetItem(item)
                if not item.is_complement:
                    item_set.add(item)
        s = len(definition)
        if s != 0:
            if type(definition[-1]) is bool:
                complement = (int(complement) + int(definition[-1])) & 0b1
                definition = definition[:-1]
                s = len(definition)
        if s == 0:
            pass
        elif s == 1:
            not_parsed = True
            if type(definition[0]) is str:
                def_str = definition[0].replace(' ', '')
                try:
                    new_items, n_complement = self._math_def_parser(def_str)
                    item_set.update(new_items)
                    complement = (int(complement) + int(n_complement)) & 0b1
                    not_parsed = False
                except:
                    pass
            if not_parsed:
                t = type(definition[0])
                if t is mSetItem:
                    item = definition[0]
                elif t is tuple:
                    item = mSetItem(*definition[0])
                else:
                    item = mSetItem(definition[0])
                if not item.is_complement:
                    item_set.add(item)
        else:
            for item in definition:
                t = type(item)
                if t is mSetItem:
                    pass
                elif t is tuple():
                    item = mSetItem(*item)
                else:
                    item = mSetItem(item)
                if not item.is_complement:
                    item_set.add(item)
            t = type(definition[-1])
            if t is mSetItem:
                item = definition[-1]
            elif t is tuple:
                item = mSetItem(*definition[-1])
            elif t is bool:
                complement = (int(complement) + int(item)) & 0b1
                item = None
            else:
                item = mSetItem(definition[-1])
            if item is not None and not item.is_complement:
                item_set.add(item)
        vars = set()
        for item in item_set:
            if item.is_var:
                vars.add(item.value)
        super().__init__(vars, complement)
        self._item_set = item_set

    def _math_def_parser(self, def_str):
        def_str = def_str.replace(' ', '')
        complement = False
        if def_str[0] == '!':
            complement = not complement
            def_str = def_str[1:]
        if def_str[-1] == "'":
            complement = not complement
            def_str = def_str[:-1]
        if def_str[0] != '{' and def_str[-1] != '}':
            raise TypeError('Given RosterSet definition is invalid (no open/close) bracket pair found')
        items = {mSetItem(item) for item in def_str[1:-1].split(',') if item != ''}
        return items, complement

    @property
    def cardinality(self):
        """
        The cardinality is somehow the size of the set it delivers how many items the set contains.
        The result is not in all cases correct furthermore it is just an estimation!

        In many cases in float intervals the user will find infinite as the result of the operation.
        :return: number of items integer or float('inf') for infinite results
        """

        if self.is_complement:
            return float('inf')
        return len(self._item_set)

    @property
    def is_empty_set(self):
        """
        For some set definition no matching item can be found! Then the set is equal to the empty set and this property
        will deliver True

        :rtype: bool
        :return: True is empty set; False set contains items
        """
        return not bool(self.cardinality)

    @property
    def is_empty_set_complement(self):
        """
        Is the complement interval same as an empty set (no item inside). If this is the case the set is the universal
        set (any item inside). But this is a relative definition to the "universe". E.g. strings will never be found
        inside a numerical set they are not in the "universe".

        :return: True complement is empty; False complement is not empty
        """
        if self.is_complement:
            return not bool(len(self._item_set))
        else:
            return False

    def items(self):
        return self._item_set.__iter__()

    def __contains__(self, value, vars_dict=None, _replacement_vars=set()):
        """
        checks if given value is inside the set (This is the main function of the whole object!)

        :type value: Union[iterable,Numeric,tuple]
        :param value: value to be checked if it is in. Because "in" supports no parameters the vars_dict
                      can be given as a tuple in the form: (value, vars_dict) in this_object

        :type vars_dict: dict
        :param vars_dict: optional replacement dict for variable items

        :rtype: bool
        :return: True is in; False is not in the set
        """

        if not vars_dict and type(value) is tuple and len(value) == 2 and type(value[1]) is dict:
            value, vars_dict = value
        if not _replacement_vars and vars_dict is not None and self._vars:
            _replacement_vars = set()
            for var in self._vars:
                if var in vars_dict:
                    _replacement_vars.add(mSetItem(vars_dict[var]))
        if not hasattr(value, 'capitalize') and hasattr(value, '__iter__') or hasattr(value, '__next__'):
            # iterable
            return all(self.__contains__(v, _replacement_vars=_replacement_vars) for v in value)
        result = value in self._item_set or value in _replacement_vars
        if self._complement:
            return not result
        else:
            return result

    def __repr__(self):
        """
        string representation
        :rtype: str
        :return: representation string of the object
        """

        if len(self._item_set):
            out = [self.__class__.__name__, '(', repr(self._item_set)[1:-1]]
        else:
            out = [self.__class__.__name__, '(']
        if self.is_complement:
            out.append(', True)')
        else:
            out.append(')')
        return ''.join(out)

    def __str__(self):
        """
        string representation using math_repr() as parameter
        :rtype: str
        :return: representation string
        """

        return ''.join([self.__class__.__name__, '(', self.math_repr(), ')'])

    def __iter__(self):
        return self._item_set.__iter__()

    def __eq__(self, other):
        if type(other) is mSetRoster:
            return self._item_set == other._item_set and self._complement == other._complement
        else:
            if self.is_complement:
                if hasattr(other, 'is_complement'):
                    if not other.is_complement:
                        return False
                else:
                    return False
            try:
                for item, other_item in zip(self._item_set, other.items):
                    if item != other_item:
                        return False
                return True
            except:
                return False

    def iter_in(self, value, vars_dict=None):
        """
        For each item in the given iterable value we check if the item is in this mSet object the
        result is a iterable over the single results
        :param value: to be checked iterable value (single item check)
        :param vars_dict: variable replacement dict
        :return: iterable True\False
        """
        _replacement_vars = set()
        if vars_dict is not None and self._vars:
            for var in self._vars:
                if var in vars_dict:
                    _replacement_vars.add(mSetItem(vars_dict[var]))
        for v in value:
            yield self.__contains__(v, _replacement_vars=_replacement_vars)

    def filter(self, value, vars_dict=None):
        _replacement_vars = set()
        if vars_dict is not None and self._vars:
            for var in self._vars:
                if var in vars_dict:
                    _replacement_vars.add(mSetItem(vars_dict[var]))
        for v in value:
            if self.__contains__(v, _replacement_vars=_replacement_vars):
                yield v

    def get_init_args(self, full=False):
        """
        delivers tuple of all initial arguments given to instance the mSet object
        :param full: True all arguments given also defaults
        :return: tuple of initial arguments
        """

        if full or self.is_complement:
            return tuple(self._item_set) + (self.is_complement,)
        else:
            return tuple(self._item_set)

    def math_repr(self, formatters=None):

        if self.is_complement:
            out = ['!{']
        else:
            out = ['{']
        if formatters is None:
            s = -1
        else:
            s = len(formatters)
        for i, item in enumerate(self._item_set):
            if i < s:
                out.append(item.math_repr(formatters[i]))
            else:
                out.append(item.math_repr())
            out.append(',')
        if out[-1] == ',':
            out[-1] = '}'
        else:
            out.append('}')
        return ''.join(out)


class mSetCombine(_mSetBase):
    """
    class where the user can combine different sets to unions

    In this class the user can combine different types of sets (all objects with `__contains__()` and a length are
    allowed to be added.

    If the object is used to check if a value is in it is sufficient if the value is in one of the subsets to
    create a positive response for a match
    """

    def __init__(self, *definition, is_union=True, complement=False):
        """

        :param definition: pointer parameter containing all unnamed arguments we expect here somehow one item
                           for each set that should be integrated into the union.
        :param complement: complement flag
        """
        if len(definition) == 0:
            raise TypeError('Minimum one sub-item must be given!')
        if type(definition[-1]) is bool:
            is_union = definition[-1]
            definition = definition[:-1]
        if len(definition) == 0:
            raise TypeError('Minimum one sub-item must be given!')
        if type(definition[-1]) is bool:
            complement = (int(complement) + int(is_union)) & 0b1
            is_union = definition[-1]
            definition = definition[:-1]
        s = len(definition)
        if s == 0:
            raise TypeError('Minimum one sub-item must be given!')
        elif s == 1 and type(definition[0]) is str:
            items, is_union, complement = self._parse_math_repr(definition[0], complement)
        else:
            items = definition
        vars = set()
        for item in items:
            if hasattr(item, 'vars'):
                vars.update(item.vars)
        self._is_union = is_union
        self._items = items
        super().__init__(vars, complement)

    def __eq__(self, other):
        if type(other) is not mSetCombine:
            return False
        try:
            for i, ii in zip(self.items(), other.items()):
                if i != ii:
                    return False
        except:
            return False
        if self.is_complement != other.is_complement:
            return False
        if self.is_union != other.is_union:
            return False
        return True

    def _parse_math_repr(self, def_str, complement=False):
        """
        parser for given math_repr to instance the object
        :param def_str:
        :return:
        """
        items = []
        vars = set()
        def_str = def_str.strip(' ')
        if def_str[0] == '!':
            complement = not complement
            def_str = def_str[1:].strip(' ')
        if def_str[-1] == "'":
            complement = not complement
            def_str = def_str[:-1].strip(' ')
        if def_str[0] == '(' and def_str[-1] == ')':
            try:
                def_str = def_str[1:-1].strip(' ')
                return self._parse_math_repr(def_str, complement)
            except:
                def_str = '(' + def_str + ')'
        is_union = True
        tmp = def_str.split(' u ')
        tmp2 = def_str.split(' n ')
        if len(tmp) > 1 and len(tmp2) > 1:
            raise TypeError('mSetCombines supports just one type of combinations " u "~unions or " n "~intersections ')
        items = []
        if len(tmp) > 1:
            for sub_def in tmp:
                try:
                    item = mSetInterval(sub_def)
                except TypeError:
                    try:
                        item = mSetRoster(sub_def)
                    except TypeError:
                        item = mSetCombine(sub_def)
                items.append(item)
        elif len(tmp2) > 1:
            is_union = False
            for sub_def in tmp2:
                try:
                    item = mSetInterval(sub_def)
                except TypeError:
                    try:
                        item = mSetRoster(sub_def)
                    except TypeError:
                        item = mSetCombine(sub_def)
                items.append(item)
        else:  # single item only
            try:
                item = mSetInterval(def_str)
            except TypeError:
                try:
                    item = mSetRoster(def_str)
                except TypeError:
                    item = mSetCombine(def_str)
            items.append(item)
        return items, is_union, complement

    @property
    def is_union(self):
        return self._is_union

    @property
    def is_intersection(self):
        return not self._is_union

    def items(self):
        for item in self._items:
            yield item

    def _get_cardinality_without_complement(self):
        """
        Helper function to estimate the cardinality
        :return:
        """
        if self._is_union:
            c = 0
            for i in self._items:
                if hasattr(i, 'cardinality'):
                    c = c + i.cardinality
                else:
                    c = c + len(i)
            return c
        else:
            c = float('inf')
            for i in self._items:
                if hasattr(i, 'cardinality'):
                    c2 = i.cardinality
                    if c2 < c:
                        c = c2
            return c

    @property
    def cardinality(self):
        """
        The cardinality is somehow the size of the set it delivers how many items the set contains.
        The result is not in all cases correct furthermore it is just an estimation!

        Especially in this case the cardinally is really an estimation only. It's not teh case that
        we check here for overlapping intervals which might reduce the cardinality. We create just an
        estimation based the cardinalities of the subitems

        In many cases in float intervals the user will find infinite as the result of the operation.
        :return: number of items integer or float('inf') for infinite results
        """
        return self._get_cardinality_without_complement()

    @property
    def is_empty_set(self):
        """
        For some set definition no matching item can be found! Then the set is equal to the empty set and this property
        will deliver True

        :rtype: bool
        :return: True is empty set; False set contains items
        """
        return self.cardinality == 0

    @property
    def is_empty_set_complement(self):
        """
        Is the complement interval same as an empty set (no item inside). If this is the case the set is the universal
        set (any item inside). But this is a relative definition to the "universe". E.g. strings will never be found
        inside a numerical set they are not in the "universe".

        :return: True complement is empty; False complement is not empty
        """
        if self.is_complement:
            return self._get_cardinality_without_complement() == 0
        else:
            return False

    def __contains__(self, value, vars_dict=None):
        """
        checks if given value is inside the set (This is the main function of the whole object!)

        :type value: Union[iterable,Numeric,tuple]
        :param value: value to be checked if it is in. Because "in" supports no parameters the vars_dict
                      can be given as a tuple in the form: (value, vars_dict) in this_object

        :type vars_dict: dict
        :param vars_dict: optional replacement dict for variable items

        :rtype: bool
        :return: True is in; False is not in the set
        """

        return_value = not self.is_complement
        if type(value) is tuple and len(value) == 2 and type(value[1]) is dict:
            value, vars_dict = value
        raise_exception = None
        if self._is_union:
            for item in self._items:
                if hasattr(item, 'is_mSet'):
                    try:
                        if item(value, vars_dict=vars_dict):
                            return return_value
                    except Exception as e:
                        raise_exception = e
                else:
                    if value in item:
                        return return_value
            if raise_exception:
                raise raise_exception
            return not return_value
        else:
            return_value = self.is_complement
            for item in self._items:
                if hasattr(item, 'is_mSet'):
                    try:
                        if not item.__contains__(value, vars_dict=vars_dict):
                            return return_value
                    except Exception as e:
                        raise_exception = e
                else:
                    if value not in item:
                        return return_value
            if raise_exception:
                raise raise_exception
            return not return_value

    def __repr__(self):
        """
        string representation
        :rtype: str
        :return: representation string of the object
        """

        out = [self.__class__.__name__, '(']
        for a in self.get_init_args():
            out.append(repr(a))
            out.append(', ')
        if out[-1] == ', ':
            out[-1] = ')'
        else:
            out.append(')')
        return ''.join(out)

    def __str__(self):
        """
        string representation using math_repr() as parameter
        :rtype: str
        :return: representation string
        """

        out = [self.__class__.__name__, '("', self.math_repr(), '")']
        return ''.join(out)

    def math_repr(self):
        """
        mathematical representation of the object (we try to match as good as possible to the
        mathematical standards here but we avoid exotic characters!
        :return: mathematical representation string
        """
        if self._complement:
            out = ['!(']
        else:
            out = ['']
        for item in self._items:
            if hasattr(item, 'math_repr'):
                out.append(item.math_repr())
            else:
                out.append(repr(item))
            if self._is_union:
                out.append(' u ')
            else:
                out.append(' n ')
        if len(self._items) > 0:
            out = out[:-1]
        if self._complement:
            out.append(')')
        return ''.join(out)

    def iter_in(self, value, vars_dict=None):
        """
        For each item in the given iterable value we check if the item is in this mSet object the
        result is a iterable over the single results
        :param value: to be checked iterable value (single item check)
        :param vars_dict: variable replacement dict
        :return: iterable True\False
        """

        return [self.__contains__(v, vars_dict) for v in value]

    def filter(self, value, vars_dict=None):
        """
        For each item in the given iterable value we check if the item is in this mSet object or not in case it is in
        the item will be delivered back if not it is skipped

        :param value: iterable value which items will be checked
        :param vars_dict: variable replacement dict
        :return: iterable of matching items
        """

        return [v for v in value if self.__contains__(v, vars_dict)]

    def get_init_args(self, full=False):
        """
        delivers tuple of all initial arguments given to instance the mSet object
        :param full: True all arguments given also defaults
        :return: tuple of initial arguments
        """
        if len(self._items) == 1:
            items = (self._items[0], None)
        else:
            items = tuple(self._items)

        if self._complement or full:
            return items + (self._is_union, self._complement)
        if not self._is_union:
            return items + (self._is_union,)
        return items

    def __simplify(self):
        """
        This method tries to reduce the items and sets in the union
        """
        # this can be improved
        del_full_items = []
        for i, item in enumerate(self._items):
            t = type(item)
            if type(item) is mSetRoster:
                if not item.is_complement:
                    del_items = set()
                    for i3, v in enumerate(item.items()):
                        for i2, item2 in enumerate(self._items):
                            if i2 == i:
                                continue
                            if v in item2:
                                del_items.add(v)
                                break
                    if len(del_items) > 0:
                        if len(del_items) == (i3 + 1):
                            del_full_items.append(item)
                        else:
                            for i3 in del_items:
                                del item._items[i3]
                            if len(item._items) == 0:
                                del_full_items.append(item)
            if type(item) is mSetInterval:
                if not item.is_complement:
                    for i2, item2 in enumerate(self._items):
                        if i2 == i:
                            continue
                        if type(item2) is mSetInterval:
                            if not item2.is_complement:
                                if item.lower.value in item2 and item.lower.value in item2:
                                    del_full_items.append(item)
                                    break
        for item in del_full_items:
            self._items.pop(item)
