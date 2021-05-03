"""
This file contains some examples of data models
that might be modified or used for determine the data stored in the iTData object

The given data models are just examples and might be improved by the user for there specific use cases.

Different to the core code of the iTree object this code is not trimmed for performance
it was more important that the code can be understood very well

First we define a helper class for range intervals and afterwards a set of data model classes for different data types
"""

from __future__ import absolute_import
from fnmatch import fnmatch
import datetime
import time
from itertree import *

# define some helpers

class IntegerModel(Data.iTDataModel):
    '''
    A data model for integer type numbers
    '''
    BIN=0
    HEX=1
    DEC=2

    def __init__(self,value=Data.__NOVALUE__,range_interval=iTInterval(iTInterval.INF,iTInterval.INF),representation=DEC):
        """
        A data model for integer type numbers

        :param value: a value that should be entered (default/start value) directly into the model

        :param range_interval: Interval object defining the valid range for the integer

        :param representation: on of DEC/HEX/BIN for the formatting of the string representation of the integer
        """
        self._range_interval=range_interval
        self._representation=representation
        super().__init__(value)

    def _validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        t=type(value)
        if t is not int:
            if t is bool: # in case of boolean value we do type cast:
                value=int(value)
            else:
                return 1,'Given value of wrong type'
        if self._range_interval.check(value):
            return 0,'ok'
        return 2,'Value: %s not in range: %s'%(repr(value),self._range_interval.math_repr())


    def _formatter(self,value=None):
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

        if self._representation==self.HEX:
            return hex(value)
        elif self._representation == self.BIN:
            return bin(value)
        else: #self._representation == self.DEC:
            return '%i' % value

    def __repr__(self):
        """
        object representation
        :return: object representation string
        """
        if self.is_empty:
            return 'IntegerModel(range_interval=%s, representation=%i)' % (repr(self._range_interval),
                                                                           self._representation)

        return 'IntegerModel(value= %s, range_interval=%s, representation=%i)' % (repr(self._value),
                                                                                 repr(self._range_interval),
                                                                                 self._representation)


class FloatModel(Data.iTDataModel):
    """
           A data model for float type numbers
    """
    def __init__(self, value=Data.__NOVALUE__, range_interval=iTInterval(iTInterval.INF, iTInterval.INF), digits=3):
        """
        A data model for float type numbers

        :param value: a value that should be entered (default/start value) directly into the model

        :param range_interval: Interval object defining the valid range for the float

        :param digits: number of digits that should be printed in the string representation of the float
        """
        self._range_interval = range_interval
        self._digits = digits
        super().__init__(value)

    def _validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        t=type(value)
        if t is not float:
            if t is bool or t is int: # in case of boolean or integer value we do type cast:
                value=float(value)
            else:
                return 1,'Given value of wrong type'
        if self._range_interval.check(value):
            return 0, 'ok'
        return 2, 'Value: %s not in range: %s' % (repr(value), self._range_interval.math_repr())

    def _formatter(self, value=None):
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
            return 'FloatModel(range_interval=%s, digits=%i)' % (repr(self._range_interval),
                                                                 self._digits)

        return 'FloatModel(value= %s, range_interval=%s, digits=%i)' % (repr(self._value),
                                                                                  repr(self._range_interval),
                                                                                  self._digits)

class StringModel(Data.iTDataModel):
    """
    data model for strings
    """
    def __init__(self, value=Data.__NOVALUE__, match=None, max_len=None):
        """
        data model for strings
        :param value: default/start value
        :param match: match pattern (fnmatch standard) for the given string
        :param max_len: maximum length of the string
        """
        self._match = match
        self._max_len = max_len
        super().__init__(value)

    def _validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        t=type(value)
        if t is not str:
            return 1,'Given value of wrong type'
        if self._max_len is not None:
            if len(value)>self._max_len:
                return 2, 'Given value contains to many characters (max_length=%i)'%self._max_len
        if self._match is not None:
            if not fnmatch(value,self._match):
                return 3, 'Given value does not match to given match pattern'
        return 0,'ok'

    def _formatter(self,value=None):
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
            return 'StringModel(match=%s, max_length=%s)' % (repr(self._match),
                                                             repr(self._max_len))

        return 'StringModel(value= %s, match=%s, max_length=%s)' % (repr(self._value),
                                                                                  repr(self._match),
                                                                                  repr(self._max_len))

class EnumerationModel(Data.iTDataModel):
    """
    data model for an enumeration type of data
    """
    def __init__(self, value=Data.__NOVALUE__, enum_iterable_dict=()):
        """
        data model for an enumeration type of data
        :param value: default/starting value
        :param enum_iterable_dict: Here the enumeration is defined in a dict or just by a iterable (list/tuple,...)
                                   e.g.: {1:'FIRST',2:'SECOND'} ~ ('FIRST','SECOND') ~ ['FIRST','SECOND']
                                   Note: the dict allows gabs: {1:'FIRST',3:'THIRD'}
        """
        if type(enum_iterable_dict) is dict:
            for i in enum_iterable_dict.keys():
                if type(i) is not int:
                    raise TypeError('enum_iterable_dict: dict keys must be integers')
            self._enum = enum_iterable_dict
        else:# we build a dict to find the enum iterable
            self._enum = {i:enum for i,enum in enumerate(enum_iterable_dict)}

        self._v2i=None

        super().__init__(value)

    def _validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        t=type(value)
        if t is not int:
            if t is bool: # in case of boolean value we do type cast:
                value=int(value)
            else:
                return 1,'Given value of wrong type'
        if value not in self._enum:
            return 2, 'Value: %i not in enumeration definition'%value
        return 0,'ok'

    def _formatter(self,value=None):
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

        return self._enum[value]

    def enum_str_to_int(self,enum_string):
        """
        translates the enumeration string back to the int value
        :param enum_string: string to be translated back to int
        :return:
        """
        if self._v2i is None:
            self._v2i={value:key for key,value in self._enum}
        try:
            return self._v2i[enum_string]
        except KeyError:
            return None

    def __repr__(self):
        """
        object representation
        :return: object representation string
        """

        if self.is_empty:
            return 'EnumerationModel(enum_iterable_dict=%s)' % (repr(self._enum))

        return 'EnumerationModel(value= %s, enum_iterable_dict=%s)' % (repr(self._value), repr(self._enum))

class TimeModel(Data.iTDataModel):
    """
    A data model for timestamps (unix time) will be formatted into ISO time standard in string representation
    """
    def __init__(self, value=Data.__NOVALUE__,):
        """
        A data model for timestamps (unix time) will be formatted into ISO time standard in string representation
        :param value: float unix time (generated by time.time() command)
        """
        super().__init__(value)

    def _validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        # we validate for an float (unix-time) here
        t=type(value)
        if t is not float:
            return 1,'Given value of wrong type'
        if value < 0:
            return 2, 'Value out of range'
        return 0,'ok'

    def _formatter(self,value=None):
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
        t = datetime.datetime.fromtimestamp(value)
        return t.isoformat(' ')


    def __repr__(self):
        """
        object representation
        :return: object representation string
        """

        if self.is_empty:
            return 'TimeModel()'
        return 'TimeModel(value= %s)' % (repr(self._value))


class ArrayModel(Data.iTDataModel):
    def __init__(self, value=Data.__NOVALUE__, item_model=Data.iTDataModel(), max_len=None):
        """
        A data model for arrays of another type of data model
        e.g. a array of floats or integers
        :param value: default/initial value
        :param item_type: sub data model for the items
        :param max_len:
        """
        self._item_model=item_model
        self._max_len=max_len
        super().__init__(value)

    def _validator(self, value):
        """
        check if the given value matches

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        :return: tuple (return_code (int), hint string) - in case return code == 0 check was successful
        """
        # value must be an iterable
        if not hasattr(value,'__iter__'):
            return 1, 'Given value of wrong type (expecting an iterable)'
        if self._max_len is not None:
            if len(value)>self._max_len:
                return 3, 'Value array length bigger then max_len'
        for i,item in enumerate(value):
            back=self._item_model.check(item)
            if back[0]!=0:
                return  2, 'Given sub_value (index: %i)-> %s'%(i,back[1])
        return 0, 'ok'

    def _formatter(self,value=None):
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

        return repr([self._item_model._formatter(i) for i in value])

    def __repr__(self):
        """
        object representation
        :return: object representation string
        """

        if self.is_empty:
            return 'ArrayModel(item_type=%s, max_len=%s)' % (repr(self._item_model), str(self._max_len))
        else:
            return 'ArrayModel(value= %s, item_type=%s, max_len=%s)' % (repr(self._value), repr(self._item_model),str(self._max_len))

if __name__ == '__main__':
    """
    During the execution of the module we build an itertree and we fill the iTree objects with the data module and in a 
    second step with the data values. Some exceptions are generated for non matching values and the formatted string 
    representation of the data model is printed out
    """
    print('Run itertree data_model.py example')
    print('We build a tree for the following information:')
    print('signal_catalog')
    print(' - signal_category')
    print('   - signal')
    print('Each level in the tree contains several attributes that are stored in the data model')
    print('Build iTData structure for signal_catalog:')
    catalog_data=Data.iTData({'creation_time':TimeModel(),'name':StringModel(max_len=20)})
    print(catalog_data)
    print('Build iTData structure for signal_category')
    category_data = Data.iTData({'description': StringModel(max_len=200)})
    print(category_data)
    print('Build iTData structure for signal')
    signal_data = Data.iTData({'type': StringModel(max_len=20),
                               'raw_data':ArrayModel(item_model=FloatModel(range_interval=iTInterval(-10,
                                                                                                  10,
                                                                                                  False,
                                                                                                  False),
                                                     digits=2)),
                               'gain': FloatModel(digits=4),
                               'offset': FloatModel(digits=4),
                               'io_type': EnumerationModel(enum_iterable_dict={1:'INPUT',2:'OUTPUT'}),
                               'buffer_size':IntegerModel(range_interval=iTInterval(0,1024,False,False)),
                               'addresse': IntegerModel(
                                   range_interval=iTInterval(0, iTInterval.INF, False, False),
                                   representation=IntegerModel.HEX),

                               })
    print(signal_data)

    print('Build the tree')
    root=iTree('signal_catalog',data=catalog_data)
    print('Type check example')
    print('Enter int as name and catch exception')
    try:
        root.d_set('name', 1)
    except TypeError as e:
        print('Exception catched: %s'%repr(e))
    root.d_set('name', 'my signal catalog')
    print('Enter creation time')
    root.d_set('creation_time',time.time())
    print('Creation time value:', root.d_get('creation_time'))
    print('Creation time string representation:',root.d_get('creation_time',return_type=Data.STR))

    print('Create a category')
    child=iTree('analog signals',data=category_data)
    print('Enter a to long description and catch exception')
    try:
        child.d_set('description', 'Signals responsible for analog inputs and outputs' + '.' * 300)
    except TypeError as e:
        print('Exception catched: %s' % repr(e))
    #enter valid description
    child.d_set('description', 'Signals responsible for analog inputs and outputs')
    #append to root
    root.append(child)
    #create some signals for the category
    sub_child=iTree('power voltage',data=signal_data)
    sub_child.d_set('type','analog input')
    print('Enter a array item out of range')
    try:
        sub_child.d_set('raw_data', [1.1, 2.2, 3.1, 4.2, 5.3, 6.4, 7.5, 8.6, 10.1])
    except TypeError as e:
        print('Exception catched: %s' % repr(e))
    #Enter valid entry
    sub_child.d_set('raw_data', [1, 2, 3, 4, 5, 6, 7, 8, 9.9])
    print('raw_data_string',sub_child.d_get('raw_data',return_type=Data.STR))
    sub_child.d_set('gain', 1.023)
    print('gain (see number of digits=4!)', sub_child.d_get('gain', return_type=Data.STR))
    sub_child.d_set('offset', 0.0183)
    print('Enter invalid enumerate number')
    try:
        sub_child.d_set('io_type', 3)
    except TypeError as e:
        print('Exception catched: %s' % repr(e))
    #enter valid io_type
    sub_child.d_set('io_type', 1)
    print('io_type enum string', sub_child.d_get('io_type', return_type=Data.STR))
    sub_child.d_set('buffer_size', 256)
    sub_child.d_set('addresse', 0xFF1234)
    print('addresse as hex represenation', sub_child.d_get('addresse', return_type=Data.STR))
    child.append(sub_child)
    #create some more childs to complete the tree
    sub_child = iTree('power current', data=signal_data)
    print('Enter invalid buffersize in update()')
    try:
        sub_child.d_update({'type': 'analog input',
                               'raw_data': [1,2,3,4],
                               'gain': 1,
                               'offset': 0,
                               'io_type': 1,
                               'buffer_size': -1, #issue!
                               'addresse': 0xFED123,
                               })
    except TypeError as e:
        print('Exception catched: %s' % repr(e))
    #valid update
    sub_child.d_update({'type': 'analog input',
                           'raw_data': [1,2,3,4],
                           'gain': 1,
                           'offset': 0,
                           'io_type': 1,
                           'buffer_size': 100,
                           'addresse': 0xFED123,
                           })
    child.append(sub_child)
    sub_child = iTree('power control', data=signal_data)
    sub_child.d_update({'type': 'analog output',
                           'gain': 1,
                           'offset': 0,
                           'io_type': 2,
                           'addresse': 0xFED663,
                           })
    child.append(sub_child)
    child=iTree('digital signals',data=category_data)
    child.d_set('description', 'Digital signals (switches and state inputs)')
    #append to root
    root.append(child)
    sub_child = iTree('power switch', data=signal_data)
    sub_child.d_update({'type': 'digital output',
                           'io_type': 2,
                           'addresse': 0x87D663,
                           })
    child.append(sub_child)
    sub_child = iTree('power state', data=signal_data)
    sub_child.d_update({'type': 'digital input',
                           'io_type': 1,
                           'addresse': 0x1ED663,
                           })

    print('CONSTRUCTED TREE:')
    root.render()




