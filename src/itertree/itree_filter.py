"""
filter classes

we use here lambda to create a method which is feed with an item and delivers then True/False depending on
the given condition so that it can be used in filter iterators
"""
import fnmatch

# List representation of the possible combinations of parameters (for quicker execution)
__FILTER_FACTORY__=[lambda result,item_filter: lambda item: item_filter(item) or result(item), # 0 item_filter=not None, invert=False, use_and=False
                    lambda result,item_filter: lambda item: item_filter(item) or not result(item), # 1 item_filter=not None, invert=True,  use_and=False
                    lambda result,item_filter: lambda item: item_filter(item) and result(item), # 2 item_filter=not None, invert=False, use_and=True
                    lambda result, item_filter: lambda item: item_filter(item) and not result(item), # 3 item_filter=not None, invert=True, use_and=True
                    lambda result,item_filter: lambda item: result(item),# 4 item_filter=None, invert=False, use_and=False
                    lambda result, item_filter: lambda item: not result(item), # 5 item_filter=None,invert=True, use_and=False
                    lambda result, item_filter: lambda item: result(item), # 6 item_filter=None, invert=False, use_and=True
                    lambda result, item_filter: lambda item: not result(item),# 7 item_filter=None, invert=True, use_and=True
                    ]

class iTFilterBase(object):
    def __new__(cls,filter_method,item_filter=None,invert=False,use_and=True):
        """
        Base/Super class for all itertree filter classes might be used for user defined filters too

        :param filter_method: method that is fet with an iTree item and that delivers True/False
        :param item_filter: Additional filter to combine with this filter (will always be calculated before this filter!
        :param invert: True - invert the result of the filter (not)
                       False (default) - result of filter is kept unchanged
        :param use_and: True (default) - combine this filter with item_filter via and operator
                        False - use or operator instead of and
        """
        index=int(item_filter is None)<<2 | int(invert) | int(use_and)<<1
        #print(index)
        return __FILTER_FACTORY__[index](filter_method,item_filter)

class iTFilterTrue(iTFilterBase):

    def __new__(cls,item_filter=None,invert=False,use_and=True):
        """
        This filter might be useless but it delivers True for all items (or False if inverted).

        :param item_filter: Additional filter to combine with this filter (will always be calculated before this filter!
        :param invert: True - invert the result of the filter (not)
                       False (default) - result of filter is kept unchanged
        :param use_and: True (default) - combine this filter with item_filter via and operator
                        False - use or operator instead of and
        """
        return super().__new__(cls,
                               lambda item: True,
                               item_filter,
                               invert,
                               use_and)


class iTFilterItemType(iTFilterBase):

    def __new__(cls,item_type,item_filter=None,invert=False,use_and=True):
        """
        Filter for iTree types (we have iTree,ITreeReadOnly,iTreeTemporary,iTreeLink types)
        :param item_type: target type class
        :param item_filter: Additional filter to combine with this filter (will always be calculated before this filter!
        :param invert: True - invert the result of the filter (not)
                       False (default) - result of filter is kept unchanged
        :param use_and: True (default) - combine this filter with item_filter via and operator
                        False - use or operator instead of and
        """
        return super().__new__(cls,
                               lambda item: type(item)==item_type,
                               item_filter,
                               invert,
                               use_and)

class iTFilterItemTagMatch(iTFilterBase):
    def __new__(cls,match,item_filter=None,invert=False,use_and=True):
        """
        Filter using the iTMatch object (have a look on th iTMatch for more details). In generalyou can
        use wild cards, etc. to find matching item tags
        :param match: iTMatch object that checks the item for a match
        :param item_filter: Additional filter to combine with this filter (will always be calculated before this filter!
        :param invert: True - invert the result of the filter (not)
                       False (default) - result of filter is kept unchanged
        :param use_and: True (default) - combine this filter with item_filter via and operator
                        False - use or operator instead of and
        """
        return super().__new__(cls,
                               lambda item: (match.check(item)),
                               item_filter,
                               invert,
                               use_and)


class iTFilterDataKey(iTFilterBase):

    def __new__(cls,data_key,item_filter=None,invert=False,use_and=True):
        """
        Filters in all items for the data key given. Delivers all items that have the given key in there data
        :param data_key: Checks if the given data key exists in item.data
        :param item_filter: Additional filter to combine with this filter (will always be calculated before this filter!
        :param invert: True - invert the result of the filter (not)
                       False (default) - result of filter is kept unchanged
        :param use_and: True (default) - combine this filter with item_filter via and operator
                        False - use or operator instead of and
        """
        return super().__new__(cls,
                               lambda item: (data_key in item.data),
                               item_filter,
                               invert,
                               use_and)

class iTFilterDataKeyMatch(iTFilterBase):

    def __new__(cls,match_pattern,item_filter=None,invert=False,use_and=True):
        """
        Filters in all items for the data key which matches to the given pattern (fnmatch search is used) you can
        use wildcards here.
        This filter works only on string or byte keys in the item.data (not on other objects)
        :param match_pattern: string/bytes that contains a match pattern
        :param invert: True - invert the result of the filter (not)
                       False (default) - result of filter is kept unchanged
        :param use_and: True (default) - combine this filter with item_filter via and operator
                        False - use or operator instead of and
        """
        return super().__new__(cls,
                               lambda item: fnmatch.filter(filter(lambda v: (type(v) is str) or (type(v) is bytes),
                                                           item.data.keys()),match_pattern),
                               item_filter,
                               invert,
                               use_and)

class iTFilterDataValue(iTFilterBase):

    def __new__(cls,data_value,item_filter=None,invert=False,use_and=True):
        """
        Filters in all items for containing the data value given. Delivers all items that have the given data value in
        there data
        :param data_value: value object to be searched in item.data
        :param item_filter: Additional filter to combine with this filter (will always be calculated before this filter!
        :param invert: True - invert the result of the filter (not)
                       False (default) - result of filter is kept unchanged
        :param use_and: True (default) - combine this filter with item_filter via and operator
                        False - use or operator instead of and
        """
        return super().__new__(cls,
                               lambda item: len(list(filter(lambda v: v == data_value , item.data.values())))>0,
                               item_filter,
                               invert,
                               use_and)

class iTFilterDataValueMatch(iTFilterBase):
    def __new__(cls,match_pattern,item_filter=None,invert=False,use_and=True):
        """
        Filters in all items for containing a matching data value to given pattern. (Works only on string and byte values
        :param match_pattern: pattern fnmatch will search for (you can use wildcards here)
        :param item_filter: Additional filter to combine with this filter (will always be calculated before this filter!
        :param invert: True - invert the result of the filter (not)
                       False (default) - result of filter is kept unchanged
        :param use_and: True (default) - combine this filter with item_filter via and operator
                        False - use or operator instead of and
        """
        return super().__new__(cls,
                               lambda item: fnmatch.filter(filter(lambda v: (type(v) is str) or (type(v) is bytes),
                                                           item.data.values()),match_pattern),
                           item_filter,
                           invert,
                           use_and)


