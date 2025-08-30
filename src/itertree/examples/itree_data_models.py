# -*- coding: utf-8 -*-
"""
This code is taken from the itertree package:
  _ _____ _____ _____ _____ _____ _____ _____
 | |_   _|   __| __  |_   _| __  |   __|   __|
 |-| | | |   __|    -| | | |    -|   __|   __|
 |_| |_| |_____|__|__| |_| |__|__|_____|_____|

https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license
For more information see: https://en.wikipedia.org/wiki/MIT_License

CONTENT DESCRIPTION:

This file contains some examples of data models
that might be modified or used for determine the data stored in the iTData object

The data models validators are designed as very strong (user might change them so that as float input we might
also accept integers or boolean types).

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


# define some extra models



class TimeModel(Data.iTValueModel):
    """
    A data model for timestamps (unix time) will be formatted into ISO time standard in string representation
    """
    def __init__(self,value=NoValue):
        super().__init__(value,
                         shape=tuple(), # single_value
                         )

    def check_and_cast_single_item(self, value_item):
        t=type(value_item)
        if t is not datetime.datetime:
            try:
                value=float(value_item)
                value_item=datetime.datetime.fromtimestamp(value)
            except:
                raise ValueError('Given value %s could not be converted in internal datetime object'%repr(value_item))
        return value_item

    def get_init_args(self):
        return (self._value,)

    def __str__(self):
        if self._value is NoValue:
            return 'NoValue'
        return self._value.isoformat(' ')



if __name__ == '__main__':
    """
    During the execution of the module we build an itertree and we fill the iTree objects with the data module and in a 
    second step with the data values. Some exceptions are generated for non matching values and the formatted string 
    representation of the data model is printed out
    """
    print('Run itertree data_model.py example')
    print('Each iTree item will contain different types of data models for the values')
    print('Build the tree')

    root=iTree('root')

    print('Append model items and enter values')


    print('\nEnter a string in the string model, iTree nows that a model is in value and takes over the given value implicit into the model')
    item=root.append(iTree('str_len20_item', value=Data.iTStrModel(shape=(20,))))
    print('Appended item: %s'%repr(item))
    item.set_value('Hello world')
    print('Content stored in item value: %s'%repr(item.value))
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    try:
        print('Enter a string in the string model which is to long')
        item.set_value('Hello world this string is more then 20 characters long')
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])

    print(
        '\nEnter a string in the string model, iTree nows that a model is in value and takes over the given value implicit into the model')
    item=root.append(iTree('ascii_str_len40_item', value=Data.iTASCIIStrModel(shape=(40,))))
    print('Appended item: %s'%repr(item))
    item.set_value('Hello world')
    print('Content stored in item value: %s'%repr(item.value))
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    try:
        print('Enter a string in the ASCII string model which is to long')
        item.set_value('Hello world'*40)
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])
    try:
        print('Enter a string in the ASCII string model which contains non ascii characters')
        item.set_value('°C')
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])

    print('\nEnter len()=2 floats list')
    item=root.append(iTree('float_array2_item', value=Data.iTFloatModel(shape=(2,),formatter='{:.2f}')))
    print('Appended item: %s'%repr(item))
    item.set_value([1.3,6.4])
    print('Content stored in item value: %s'%repr(item.value))
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    print('Enter a numeric string in the float model')
    item.set_value(['1','3'])
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    item.set_value(['1.3','3.1'])
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    print('Enter a single item list in the float array model')
    item.set_value([1.1])
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    try:
        print('Enter a string in the float model')
        item.set_value(['1.3','ABC'])
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])
    try:
        print('Enter a single float in the float array model')
        item.set_value(1.1)
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])
    try:
        print('Enter a triple item list in the float array model')
        item.set_value([1.1,2.2,4.4])
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])

    print('\nEnter single float with range')
    item=root.append(iTree('float_single_item', value=Data.iTFloatModel(shape=tuple(),
                                                                   contains=Filters.mSetInterval((-10,True),(10,True)),
                                                                   formatter='{:.4e}')))
    print('Appended item: %s'%repr(item))
    item.set_value(5.5)
    print('Content stored in item value: %s'%repr(item.value))
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    print('Enter a numeric string in the float model')
    item.set_value('-4.4')
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    try:
        print('Enter a string in the float model')
        item.set_value('ABC')
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])
    try:
        print('Enter a float list in the float model')
        item.set_value([1.2,3.4])
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])
    try:
        print('Enter a float out of range upper limit in the float model')
        item.set_value(11)
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])
    try:
        print('Enter a float out of range lower limit in the float model')
        item.set_value(-11)
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])

    print('\nEnter timestamp')
    item=    root.append(iTree('time_stamp_item', value=TimeModel(0)))
    print('Appended item: %s'%repr(item))
    item.set_value(time.time())
    print('Content stored in item value: %s'%repr(item.value))
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    item.set_value(datetime.datetime.fromtimestamp(time.time()))
    print('Content stored in item value: %s' % repr(item.value))
    print('Content delivered via get_value(): %s' % str(item.get_value()))
    try:
        print('Enter a string in the time model')
        item.set_value('ABC')
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])
    try:
        print('Enter a negative float in the time model')
        item.set_value(-100)
    except ValueError as e:
        print('Exception raised (and handled):')
        print(e.args[0])
