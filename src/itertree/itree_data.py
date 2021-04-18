import copy
from collections import OrderedDict

# special internal constant used for the item that is stored without giving a key
__NOKEY__ = ('__iTree_NOKEY__',)
__NOVALUE__ = ('__iTree_NOVALUE__',)

# return_types
VALUE = V = 0  # returns the stored value
STR = S = 1  # returns the string representation of the value (DTDataItems contains formatters for this)
FULL = F = 2  # In case DTDataItem objects are used for storage the full object is given back


class iTreeValidationError(Exception):
    """
    Special data validation exception with validation traceback function

    """

    def __init__(self, *args, **kwargs):
        try:
            self._validation_traceback = kwargs.pop('validation_traceback')
        except KeyError:
            self._validation_traceback = {'text': 'Value validation failed (unknown reason)'}
        super(iTreeValidationError, self).__init__(*args, *kwargs)

    @property
    def validation_traceback(self):
        """
        delivers the related validation traceback
        :return:
        """
        return self._validation_traceback

    @property
    def text(self):
        """
        delivers the related validation traceback text
        :return:
        """
        return self._validation_traceback.get('text')


class iTDataModel(object):
    """
    The default iTree data model class
    It's more the interface definition for specific data model classes that might be created using this superclass

    The data model checks the given value for a specific data item.
    So that we can ensure that the given value matches to the expectations.
    We can check for types, shapes (length), limits, or matching patterns.

    Besides the check we can also define a default formatting for the value when
    it is translated into a string.

    (see examples/itree_data_examples.py)
    """
    __slots__ = ('_value', '_formatter_cache')

    def __init__(self, value=__NOVALUE__):
        """
        :param value: value object to be stored in the data model
        """
        if not value == __NOVALUE__:
            self.__validator(value)
        self._value = value
        self._formatter_cache = None

    @property
    def is_iTDataModel(self):
        """
        class identifier used in hasattr() method
        :return: True
        """
        return True

    @property
    def is_empty(self):
        """
        tells if the iTreeDataModel is empty or contains a value
        :return:
        """
        return self.value == __NOVALUE__

    @property
    def value(self):
        """
        the stored value
        :return: object stored in value
        """
        if self.is_empty:
            return None
        return self._value

    def clear_value(self):
        """
        clears (deletes) the current value content and sets the state to "empty"
        :return: returns the value object that was stored in the iTreeDataModel
        """
        v = self._value
        self._value = __NOVALUE__
        return v

    def __validator(self, value):
        """
        Here we check the value

        In case check fails an iTreeValidationError is raised

        :param value: to be checked against the model

        """
        # we actually accept here any value
        pass

    def __formatter(self):
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
        if self.is_empty:
            return 'None'
        return str(self._value)

    def set(self, value):
        """
        put a specific value into the data model
        :except: raises an iTreeValidationError in case a not matching object is given
        :param value: value object to be placed in the data model
        :return:
        """
        self.__validator(value)
        self._value = value
        self._formatter_cache = None

    def check(self, value):
        """
        check a specific value if it is matching to the data model
        :param value: value object to be checked
        :return: tuple (True/False, checking text string)
        """
        try:
            self.__validator(value)
            return True, 'ok'
        except iTreeValidationError as e:
            return False, e.text

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
        if format_spec is None:
            # as long as the value is not changed we cache the result for quicker reuse:
            if self._formatter_cache is None:
                # run the formatter
                self._formatter_cache = self.__formatter()
            return self._formatter_cache
        else:
            return super(iTDataModel, self).__format__(format_spec)

    def __repr__(self):
        return 'iTreeDataModel(value= %s)' % self._value


class iTData(dict):
    """
    Standard itertree Data management object might be overloaded or changed by the user
    """
    __slots__=()

    def __init__(self, data_items=None):
        """
        Standard iTreeData object might be overloaded or changed by the user.
        Stores the data in a internal dict. For attribute like data it's recommended to store
        the data as iTreeDataItem. This object allows the definition of data type, sizes, limits and format definition
        of a string representation.

        :param data_items: single object or dict with key,value objects to be stored in the iTreeData object
        """
        if data_items is None:
            super().__init__()
        else:
            t = type(data_items)
            if (t is dict) or (t is OrderedDict) or (t is list):  # we can instance the whole data set via these types
                super().__init__(data_items)
            else:
                super().__init__([(__NOKEY__, data_items)])

    def __copy__(self):
        return iTData(super().copy())

    def __deepcopy__(self):
        iTData(copy.deepcopy(super().copy()))

    def set(self, key, value=__NOKEY__):
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
        if hasattr(value, 'is_iTDataModel'):
            super(iTData, self).__setitem__(key, value)
            return
        else:
            try:
                old_item = super(iTData, self).pop(key)
            except KeyError:
                super(iTData, self).__setitem__(key, value)
                return
            if hasattr(old_item, 'is_iTreeDataModel'):
                old_item.set(value)
                super(iTData, self).__setitem__(key, old_item)
            else:
                super(iTData, self).__setitem__(key, value)

    @property
    def data(self):
        """
        delivers a copy of the super dict of this class (do not use for manipulations directly)!
        :return: dict
        """
        return super(iTData, self).copy()

    @property
    def is_iTData(self):
        """
        used for identification of this class
        :return: True
        """
        return True

    @property
    def is_empty(self):
        """
        used for identification of this class
        :return: True
        """
        return super(iTData, self).__len__() == 0

    @property
    def is_no_key_only(self):
        """
        used for identification of this class
        :return: True
        """
        return super(iTData, self).__len__() == 1 and super(iTData, self).__contains__(__NOKEY__)

    def get(self, key=__NOKEY__, default_value=None, return_type=VALUE):
        """
        get a specific data item by key
        :param key: key of the data item (if not given __NOKEY__ is used!
        :param default_value: value is delivered in case key is not found
        :param return_type: We can deliver different returns
                            VALUE - value object
                            FULL - iTreeDataModel (only if used else same as VALUE)
                            STR - formatted string representation of the data value
        :return: requested value
        """
        try:
            item = super(iTData, self).__getitem__(key)
        except KeyError:
            return default_value
        if return_type == FULL:
            return item
        if hasattr(item, 'is_iTreeDataModel'):
            if return_type == STR:
                return format(item)
            return item.value
        if return_type == STR:
            return str(item)
        return item

    def check(self, value, key=__NOKEY__):
        """
        check if given value can be stored in the key related itreeDataModel
        :param value: to be checked value
        :param key: key to be stored in
        :return: tuple (True/False,'check text')
        """
        try:
            item = super(iTData, self).__getitem__(key)
        except KeyError:
            # nothing to check item does not exist
            return True, 'ok'
        if hasattr(item, 'is_iTreeDataModel'):
            return item.check(value)
        return True, 'ok'

    def pop(self, key=__NOKEY__, value_only=True):
        """
        delete a stored value
        :param key: key where the item should be popped out
        :param value_only: True - only value will be deleted model will be kept in iTreeData
                           False - whole model will be popped out
        :return:
        """
        if value_only:
            item = super(iTData, self).__getitem__(key)
            if hasattr(item, 'is_iTreeDataModel'):
                return item.clear_value()
        return super(iTData, self).pop(key)

    def __repr__(self):
        # we represent via dict because dict will automatically load in again as iTreeData object
        return repr([i for i in self.items()])

    def __hash__(self):
        """
        Again hashing is quite slow here
        :return: hash integer
        """
        return hash((i for i in self.items()))


class iTDataReadOnly(iTData):
    """
    Standard itertree Data management object might be overloaded or changed by the user
    """

    def __init__(self, data_items=None):
        """
        Standard iTreeData object might be overloaded or changed by the user.
        Stores the data in a internal dict. For attribute like data it's recommended to store
        the data as iTreeDataItem. This object allows the definition of data type, sizes, limits and format definition
        of a string representation.

        :param data_items: single object or dict with key,value objects to be stored in the iTreeData object
        """
        super(iTData, self).__init__(data_items)

    def __setitem__(self, *arg, **kwargs):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def pop(self, *arg, **kwargs):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def set(self, *arg, **kwargs):
        raise PermissionError('The iTDataReadOnly() object data can not be changed')

    def __repr__(self):
        # we represent via dict because dict will automatically load in again as iTreeData object
        return 'iTDataReadOnly(' + repr([i for i in self.items()]) + ')'

    @property
    def is_iTDataReadOnly(self):
        """
        used for identification of this class
        :return: True
        """
        return True

    @property
    def data(self):
        """
        delivers a copy of the super dict of this class (do not use for manipulations directly)!

        :return: dict
        """
        return super(iTDataReadOnly, self).data

