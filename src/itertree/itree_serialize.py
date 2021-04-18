# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import gzip
import hashlib
from collections import OrderedDict

# For serializing we (try) to import some modules:
IS_ORJSON=False
try:
    import orjson as JSON
    IS_ORJSON=True
    # orjson is much faster then standard json but might not be available
except:
    try:
        import ujson as JSON
        # ujson is much faster then standard json but might not be available
    except:
        import json as JSON
try:
    import numpy as np
    # only needed in case of numpy arrays in data
    # for serializing the data
except:
    np = None

from .itree_helpers import *
from .itree_filter import iTFilterItemType

from .itree_data import iTData, iTDataReadOnly
from .itree_main import iTree, iTreeReadOnly, iTreeLink, iTreeTemporary

DT_SERIALIZE_VERSION = "1.1.0"


class iTStdObjSerializer(object):
    """
    This class converts objects to raw objects (that can be converted by standard JSON serializer)
    and back conversion is also included
    """

    # JSON tags (We keep them very small)
    TREE = 'iT'
    DATA = 'DT'
    LINK = 'LK'
    TAG = 'TG'
    DATA_MODELL = 'DM'
    DTYPE = 'TP'
    DATA_CONTAINER = 'DC'

    def encode(self, o):
        """
        encode the given object to a list or dict (unordered objects)
        :param o: object
        :return: list
        """
        encode = self.encode
        t = type(o)
        dtype = None
        if t is iTree:
            dtype = 'iT'
        elif t is iTreeReadOnly:
            dtype = 'iTRO'
        elif t is iTreeLink:
            dtype = 'iTl'
        if dtype is not None:
            dt_dict = {self.DTYPE: dtype, self.TAG: encode(o._tag)}
            if t is iTreeLink:
                if o._link is not None:
                    dt_dict[self.LINK] = (o._link.file_path, o._link.key_path)
            data = o._data
            if not data.is_empty:
                dt_dict[self.DATA] = encode(data)
            dt_dict[self.TREE] = [encode(item) for item in
                                  o.iter_children(item_filter=iTFilterItemType(iTreeTemporary, invert=True))]
            return dt_dict
        if (t is str) or (t is int) or (t is float) or (t is bool):
            return o
        if t is dict:
            dtype = 'd'
        elif t is iTData:
            dtype = 'D'
        elif t is iTDataReadOnly:
            dtype = 'DR'
        elif t is OrderedDict:
            dtype = 'OD'
        if dtype is not None:
            return {self.DTYPE: dtype,
                    self.DATA_CONTAINER: [(encode(k), encode(v)) for k, v in o.items()]}
        if np is not None:
            if t is np.ndarray:
                return {self.DTYPE: 'npa', self.DATA_CONTAINER: [i for i in o.tobytes()], 'np.dtype': str(o.dtype)}
        try:
            # iterable?
            return {self.DTYPE: 'ITER:%s' % (str(t).split("'")[1]), self.DATA_CONTAINER: [encode(i) for i in o]}
        except:
            return o

    def decode(self, raw_o, load_links=True):
        """
        decode the given raw_object back to the original object
        :param raw_o: raw_object (dict or list)
        :param load_links: load the links of the linked iTree objects
        :return: constructed object
        """
        decode = self.decode
        t = type(raw_o)
        if t is dict:
            o_type = raw_o.get(self.DTYPE)
            if o_type is None:
                return {decode(key): decode(v) for key, v in raw_o}
            elif o_type == 'iT' or o_type == 'iTL' or o_type == 'iTRO':
                tag = decode(raw_o.get(self.TAG))
                data = raw_o.get(self.DATA)
                if data is not None:
                    data = decode(data)
                link = raw_o.get(self.LINK)
                if link is not None:
                    new_item = iTreeLink(tag, data=data, link_file_path=link[0], link_key_path=link[1])
                    if load_links:
                        new_item.load_links()
                else:
                    tree = raw_o.get(self.TREE)
                    if o_type == 'iT':
                        new_item = iTree(tag, data=data, subtree=[decode(i) for i in tree])
                    else:
                        new_item = iTreeReadOnly(tag, data=data, subtree=[decode(i) for i in tree])
                return new_item
            elif o_type == 'OD':
                return OrderedDict([(decode(i[0]), decode(i[1])) for i in raw_o[self.DATA_CONTAINER]])
            elif (o_type is 'D') or (o_type is 'd') or (o_type is 'DR'):
                return {decode(i[0]): decode(i[1]) for i in raw_o[self.DATA_CONTAINER]}
            elif o_type.startswith('ITER:'):
                new = [decode(i) for i in raw_o.get(self.DATA_CONTAINER)]
                return eval('%s(new)' % o_type[5:])
            elif o_type == 'npa':
                # here we will get an exception in case numpy is not available!
                if np is None:
                    raise ImportError(
                        'Numpy is needed for decoding of this data! It is not found in the python installation')
                return np.frombuffer(bytes(bytearray(raw_o.get(self.DATA_CONTAINER))), raw_o.get('np.dtype'))
        return raw_o


class iTStdJSONSerializer(object):
    """
    This is the standard serializer for DataTree which translates the structure
    into the JSON format.
    Users might implement there own serializers using the interface methods defined
    in this serializer
    """

    def __init__(self, obj_serializer=None):
        self.json = JSON
        if obj_serializer is None:
            self.obj_serializer = iTStdObjSerializer()
        else:
            self.obj_serializer = obj_serializer

    def dumps(self, o, add_header=True, calc_hash=True):
        """
        In JSON the iTree object is represented in the following form
        Item-> dict with all properties (Special keys used)
        Tree structure is stored in list

        :param o: iTree object to be serialized
        :param add_header: True - the header information will be added (containing Version info and hash)
                           False - no header pure data
        :param calc_hash: True - A sha1 hash is calculated over the data section of iTree and added in the header
                          False - no hash will be calculated

        :return: string containing the serialized data
        """
        if IS_ORJSON:
            dt_str = JSON.dumps(self.obj_serializer.encode(o))
        else:
            dt_str = bytes(JSON.dumps(self.obj_serializer.encode(o), indent=1,
                                  ensure_ascii=False).encode('utf8', errors='backslashreplace'))
        if add_header:
            header_dict = {'TYPE': 'IterTree', 'VERSION': DT_SERIALIZE_VERSION}
            if calc_hash:
                data_hash = hashlib.sha1(dt_str).hexdigest()
                header_dict['HASH'] = data_hash
            if IS_ORJSON:
                header_str = JSON.dumps(header_dict)
            else:
                header_str = bytes(JSON.dumps(header_dict).encode('utf8', errors='backslashreplace'))
            dt_str = b''.join([header_str, b'***DT***', dt_str])
        return dt_str

    def dump(self, o, file_path, pack=True, calc_hash=True, overwrite=False):
        """
        Serialize iTree object into a file

        :param o: iTree object to be serialized
        :param file_path: target file path where to store the data in
        :param pack: True - gzip the data, False - do not zip
        :param overwrite: True - an existing fie will be overwritten
                          False (default) - in case the file exists an FileExistsError Exception will be raised
        :param calc_hash: True - A sha1 hash is calculated over the data section of iTree and added in the header
                          False - no hash will be calculated
        :return: None
        """
        is_hdl = True
        if type(file_path) is str:
            is_hdl = False
            if os.path.exists(file_path):
                if not overwrite:
                    raise FileExistsError('Error file "%s" exists already' % file_path)
                if os.path.isdir(file_path):
                    raise FileExistsError('Error dir with name "%s" exists already' % file_path)
        data = self.dumps(o, calc_hash=calc_hash)
        if pack:
            data = gzip.compress(data)
        if is_hdl:
            file_path.write(data)
        else:
            with open(file_path, 'wb') as fh:
                fh.write(data)

    def loads(self, source_str, check_hash=True, load_links=True):
        """
        create an iTree object by loading from a string.

        :param source_str: source string that contains the iTree information
        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash
        :param load_links: True - linked iTree objects will be loaded
        :return: iTree object loaded from file
        """
        header_str, dt_str = source_str.split(b'}***DT***')
        header_dict = JSON.loads(header_str + b'}')
        if header_dict['VERSION'] != DT_SERIALIZE_VERSION:
            raise PermissionError('Wrong version of DataTree data please convert first!')
        if check_hash and ('HASH' in header_dict):
            a = hashlib.sha1(dt_str).hexdigest()
            if hashlib.sha1(dt_str).hexdigest() != header_dict['HASH']:
                raise PermissionError('Given DataTree data is corrupted (wrong hash)!')
        raw_o = JSON.loads(dt_str)
        return self.obj_serializer.decode(raw_o, load_links=load_links)

    def load(self, file_path, check_hash=True, load_links=True):
        """
        create an iTree object by loading from a file

        :param file_path: file path to the file that contains the iTree information
        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash
        :param load_links: True - linked iTree objects will be loaded
        :return: iTree object loaded from file
        """
        if type(file_path) is str:
            if not os.path.exists(file_path):
                raise FileNotFoundError('Error file "%s" not found' % file_path)
            with open(file_path, 'rb') as fh:
                data = fh.read()
        else:
            # file handle
            data = file_path.read()
        try:
            data = gzip.decompress(data)
        except OSError:
            # we might have an already unzipped file!
            pass
        # data=data.decode(decode)
        return self.loads(data, check_hash=check_hash, load_links=load_links)


class iTStdRenderer(object):
    """
    Standard renderer fr the iTree object for creating a very simple pretty print output
    """

    def __init__(self):
        self._identation = 4
        self._heading = u' \u2514\u2500\u2500'
        self._link_heading = u' \u2514\u2500>'

    def __create_item_string(self, item):
        """
        internal method creating the item string
        (We do not use repr() here because we do not want to see the subtree parameter here)

        :param item: item to be printed
        :return: string containing the item information
        """
        t = type(item)
        link_str = ''
        class_name = 'iTree'
        if t is iTreeReadOnly:
            class_name = 'iTreeReadOnly'
        elif t is iTreeLink:
            class_name = 'iTreeLink'
            if item._link is not None:
                link_str = ', link=%s' % repr(item._link)
        elif t is iTreeTemporary:
            class_name = 'iTreeTemporary'
        data = item._data
        if data.is_empty:
            return '%s(%s%s)' % (class_name, repr(item.tag), link_str)
        if data.is_no_key_only:
            return '%s(%s%s, data=%s)' % (class_name, repr(item.tag), link_str, repr(item.get()))
        else:
            return '%s(%s%s, data=%s)' % (class_name, repr(item.tag), link_str, repr(item._data))

    def render(self, itree_object, item_filter=None, _level=0):
        """
        prints a pretty output of the iTree object

        :param itree_object: iTree object to be converted
        :param item_filter: item filter method or filter-constant to filter specific items out
        :param _level: internal parameter for recursive calls (do not use)
        :return: string containing the pretty print aoutput
        """
        if not hasattr(itree_object, 'is_iTree'):
            raise TypeError('Can only render iTree objects, got %s instead' % (type(itree_object)))
        if _level == 0:
            print(self.__create_item_string(itree_object))
        else:
            output = []
        sub_tree = None
        header = self._heading
        if type(itree_object) is iTreeLink:
            header = self._link_heading
        for item in itree_object.iter_children(item_filter=item_filter):
            print(''.join([' ' * (self._identation * _level), header, self.__create_item_string(item)]))
            self.render(item, item_filter=item_filter, _level=_level + 1)

    def renders(self, itree_object, item_filter=None, _level=0):
        """
        creates a pretty print string from iTree object

        :param itree_object: iTree object to be converted
        :param item_filter: item filter method or filter-constant to filter specific items out
        :param _level: internal parameter for recursive calls (do not use)
        :return: string containing the pretty print aoutput
        """
        if not hasattr(itree_object, 'is_iTree'):
            raise TypeError('Can only render iTree objects, got %s instead' % (type(itree_object)))
        if _level == 0:
            output = self.__create_item_string(itree_object)
        else:
            output = ''
        sub_tree = None
        for item in itree_object.iter_children(item_filter=item_filter):
            output = ''.join(
                [output, '\n', ' ' * (self._identation * _level), self._heading, self.__create_item_string(item),
                 self.renders(item, item_filter=item_filter, _level=_level + 1)])
        return output
