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


This part of code contains the helper functions related to the iTree data attribute
"""

import copy
import itertools
import abc
from collections import deque

# special internal constant used for the item that is stored without giving a key
__NOKEY__=('__iTree_NOKEY__',)
__NOVALUE__ = ('__iTree_NOVALUE__',)

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

    def __init__(self, value=__NOVALUE__):
        """
        :param value: value object to be stored in the data model
        """
        if not value == __NOVALUE__:
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
                self._formatter_cache = self.formatter()
            return self._formatter_cache
        else:
            return super(iTDataModel, self).__format__(format_spec)

    def __repr__(self):
        if self.is_empty:
            return '%s()'%self.__class__.__name__
        return '%s(value= %s)' % (self.__class__.__name__,self._value)

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    @property
    def is_empty(self):
        """
        tells if the iTreeDataModel is empty or contains a value
        :return:
        """
        return self._value == __NOVALUE__

    def get(self):
        """
        the stored value
        :return: object stored in value
        """
        if self._value == __NOVALUE__:
            return None
        return self._value

    def set(self, value, _it_data_model_identifier=None):
        """
        put a specific value into the data model

        :except: raises an iTreeValidationError in case a not matching object is given

        :param value: value object to be placed in the data model
        :param _it_data_model_identifier: internal parameter used for identification
                                         of the set method in special cases, no functional impact

        """
        self._value = self.validator(value)
        self._formatter_cache = None

    value = property(get, set)

    def clear(self,_it_data_model_identifier=None):
        """
        clears (deletes) the current value content and sets the state to "empty"

        :param _it_data_model_identifier: internal parameter used for identification
                                         of the set method in special cases, no functional impact

        :return: returns the value object that was stored in the iTreeDataModel
        """
        v = self.value
        self._value = __NOVALUE__
        self._formatter_cache = None
        return v

    @abc.abstractmethod
    def validator(self, value):
        """
        This method should check the given value.

        It should raise an iDataValueError Exception with a failure explanation in case the value is not
        matching to the iDataModel.

        ..warning:: The validator in an explicit iDataModel class must always return the value itself and it must raise
                    the iDataValueError in case of a no matching value. It should also call the super().validator()
                    method or at least consider that `__NOVALUE__` is a no matching value.

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



class iTDataModelAny(iTDataModel):
    """
    Example iDataModel class that accepts any kind of value
    """

    # we must overload the following mandatory abstract methods:

    def validator(self, value):
        return super().validator(value)

    def formatter(self, value=None):
        return super().formatter(value)


class iTData(dict):
    """
    Standard itertree Data management object might be overloaded or changed by the user
    """

    GET_LOOK_UP_METHOD={STR: lambda item: isinstance(item,iTDataModel) and format(item) or str(item),
                        FULL: lambda item: item,
                        VALUE:lambda item: isinstance(item,iTDataModel) and item.value or item
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
                    super().__init__(seq,**kwargs)
                except TypeError:
                    super().__init__([(__NOKEY__, seq)], **kwargs)

    def __setitem__(self, key, value=__NOKEY__):
        """
        setter for the iTreeData object
        HINT: If no value is given the key item will be interpreted as value
              and it will be stored as __NOKEY__-object.
        :param key: key under which the given object is stored
        :param value: object that should be stored
        :return: None
        """
        if value == __NOKEY__:
            value = key
            key = __NOKEY__
        try:
            return super().__getitem__(key).set(value, _it_data_model_identifier=0)
        except (KeyError, AttributeError, TypeError):
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

                            ..note :: The parameter is only used by the helper method `getitem()`
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
            except (AttributeError,TypeError):
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
        return '%s(%s)' % (self.__class__.__name__,super(iTData, self).__repr__())

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

        :return: None
        """
        if hasattr(E, 'keys'):
            # we iter two times over the items  (but we can consume iterator only one time)
            # and deque is quicker then list in this case!
            items = deque(itertools.chain(E.items(), F.items()))
        elif E is None:
            items = deque(F.items())
        else:
            # we iter two times over the items  (but we can consume iterator only one time)
            # and deque is quicker then list in this case!
            items = deque(itertools.chain(E, F.items()))
        # check if we have just valid items will raise an exception if not matching!
        # precheck:
        i=0
        super_class=super(iTData,self)
        try:
            models=deque()
            for i, (k, v) in enumerate(items):
                append=False
                try:
                    super_class.__getitem__(k).validator(v)
                    append = True
                except (KeyError,AttributeError):
                    pass
                models.append(append)
        except Exception as e:
            raise e.__class__('Input item %s raises: %s'%(str(items[i]),str(e)))
        #finally fill the data
        for (k, v), m in zip(items, models):
            if m:
                super_class.__getitem__(k).set(v)
            else:
                super_class.__setitem__(k, v)

    def copy(self):
        """
        create a new object with same items

        :return: new object copied from self
        """
        return self.__copy__()

    def clear(self, values_only=False) -> None:
        models=[]
        if values_only:
            models=[((k,v),v.clear()) for k, v in super(iTData,self).items() if isinstance(v,iTDataModel)]
        super().clear()
        super().update([(k,v) for (k,v),_ in models])

    def pop(self, key=__NOKEY__, default=__NOKEY__,value_only=True):
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
            if default!=__NOKEY__:
                return default
            raise
        except (AttributeError,TypeError):
            # AttributeError raised if clear() is not known
            # TypeError raised if _it_data_model_identifier is not accepted
            return super(iTData, self).pop(key)
        return item


    def get(self,key=__NOKEY__,default=None,return_type=VALUE):
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
            return self.__getitem__(key,_return_type=return_type)
        except KeyError:
            return default

    # not supported methods:
    def fromkeys(self, *args,**kwargs):
        """
        create a new iData object based on given keys and optional value

        - real signature unknown
        """
        return iTData(dict.fromkeys(self,*args,**kwargs))

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
    def delete_item(self,key,value_only=True):
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

        return self.__delitem__(key,value_only)

    def model_values(self):
        """
        iterator that takes in case of iDataModel values the value out of the model,
        in case of non iDataModel values the value is given directly as it is

        :return: iterator
        """
        for v in super(iTData,self).values():
            if isinstance(v,iTDataModel):
                yield v.value
            else:
                yield v

    def model_items(self):
        """
        iterator that takes in case of iDataModel values the value out of the model,
        in case of non iDataModel values the value is given directly as it is

        :return: iterator
        """
        for k,v in super(iTData,self).items():
            if isinstance(v,iTDataModel):
                yield k,v.value
            else:
                yield k,v

    @property
    def is_empty(self):
        """
        used for identification of this class
        :return: True
        """
        return not self
        #return super(iTData, self).__len__()==0

    @property
    def is_no_key_only(self):
        """
        used for identification of this class
        :return: True
        """
        return super(iTData, self).__len__() == 1 and super(iTData, self).__contains__(__NOKEY__)

    def deepcopy(self):
        """
        create a deep copy of this object

        also all internal items will be copied!

        :return: new object deep copied from self
        """
        return self.__deepcopy__()



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

    def delete_item(self,key,value_only=True):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def __repr__(self):
        # we represent via dict because dict will automatically load in again as iTreeData object
        return 'iTDataReadOnly(%s)' % super(iTData, self).__repr__()

    def __copy__(self):
        return iTDataReadOnly(super(iTData, self).copy())

    def __deepcopy__(self):
        iTDataReadOnly(copy.deepcopy(super(iTData, self).copy()))
