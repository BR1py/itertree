# -*- coding: utf-8 -*-
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


This part of code contains the standard iTree serializers (JSON and rendering)
"""

from __future__ import absolute_import

import os
import platform
import gzip
import hashlib
from collections import OrderedDict

# For serializing we (try) to import some modules:

IS_ORJSON=False
DECODE = False

try:
    import orjson as JSON
    IS_ORJSON=True
    # orjson is much faster then standard json but might not be available
except:
    import json as JSON

    test=bytes(JSON.dumps({'test':'123','HASH':hashlib.sha1(b'asjhdahsdh').hexdigest()}).encode('utf8', errors='backslashreplace'))
    try:
        JSON.loads(test)
    except TypeError:
        DECODE=True

try:
    import numpy as np
    # only needed in case of numpy arrays in data
    # for serializing the data
except:
    np = None

from .itree_helpers import *
from .itree_filter import iTFilterItemType

from .itree_data import iTData, iTDataReadOnly
from .itree_main import iTree, iTreeReadOnly, iTreeLink, iTreeTemporary,iTreePlaceHolder

DT_SERIALIZE_VERSION = "1.1.1"


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
    IDX = 'IDX'

    DATA_MODELL = 'DM'
    DTYPE = 'TP'
    DATA_CONTAINER = 'DC'
    ITREE_ITEMS_DECODE={'iT':iTree,'iTRO':iTreeReadOnly,'iTl':iTreeLink,'iTPH':iTreePlaceHolder,'iTI':TagIdx}
    ITREE_ITEMS_ENCODE = {iTree:'iT', iTreeReadOnly:'iTRO', iTreeLink:'iTl' , iTreePlaceHolder:'iTPH',TagIdx:'iTI' }
    OTHER_ITEMS_DECODE = {'d':dict ,'D': iTData , 'DR':iTDataReadOnly , 'OD':OrderedDict }
    OTHER_ITEMS_ENCODE={dict:'d',iTData:'D',iTDataReadOnly:'DR',OrderedDict:'OD'}

    def encode(self, o):
        """
        encode the given object to a list or dict (unordered objects)
        :param o: object
        :return: list
        """
        encode = self.encode
        t = type(o)
        dtype = self.ITREE_ITEMS_ENCODE.get(t)
        if dtype is not None:
            if t is TagIdx:
                return {self.DTYPE: dtype, self.TAG: encode(o.tag),self.IDX:o.idx}
            dt_dict = {self.DTYPE: dtype, self.TAG: encode(o.tag)}
            if t is not iTreePlaceHolder:
                data = o._data
                if not data.is_empty:
                    dt_dict[self.DATA] = encode(data)
                if t is iTreeLink:
                    if o._link is not None:
                        dt_dict[self.LINK] = (o._link.file_path, encode(o._link.key_path))
                    result_list=[encode(item) for item in o.iter_locals(add_placeholders=True)]
                else:
                    result_list =[encode(item) for item in
                                      o.iter_children(item_filter=iTFilterItemType(iTreeTemporary, invert=True))]
                dt_dict[self.TREE] = result_list
            return dt_dict
        if (t is str) or (t is int) or (t is float) or (t is bool):
            return o
        dtype=self.OTHER_ITEMS_ENCODE.get(t)
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

    def decode(self, raw_o):
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
            elif o_type in self.ITREE_ITEMS_DECODE:
                tag = decode(raw_o.get(self.TAG))
                if o_type == 'iTPH':
                    return iTreePlaceHolder(tag)
                elif o_type == 'iTI':
                    return TagIdx(tag,raw_o.get(self.IDX))
                else:
                    data = raw_o.get(self.DATA)
                    if data is not None:
                        data = decode(data)
                    tree = raw_o.get(self.TREE)
                    link = raw_o.get(self.LINK)
                    if link is not None:
                        new_item = iTreeLink(tag, data=data,
                                             link_file_path=link[0],
                                             link_key_path=decode(link[1]),
                                             load_links=False,
                                             subtree=[decode(i) for i in tree])
                    else:
                        if o_type == 'iT':
                            new_item = iTree(tag, data=data, subtree=[decode(i) for i in tree])
                        else:
                            new_item = iTreeReadOnly(tag, data=data, subtree=[decode(i) for i in tree])
                return new_item
            elif o_type == 'OD':
                return OrderedDict([(decode(i[0]), decode(i[1])) for i in raw_o[self.DATA_CONTAINER]])
            elif (o_type == 'D') or (o_type == 'd') or (o_type == 'DR'):
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

    def dumps2(self, o, add_header=True, calc_hash=True):
        """
        new dump not yet working still in development!
        should be iterative and only one iteration over all items should be done (not two like in the current solution)
        :param o:
        :param add_header:
        :param calc_hash:
        :return:
        """
        return_items=b''
        iterator=o.iter_all_bottom_up(item_filter=iTFilterItemType(iTreeTemporary,invert=True))
        parents = [o]

        for item in iterator:
            p=item._parent
            if p not in parents:
                i=len(parents)
                parents.append(p)
            else:
                i=parents.index(p)
                diff=len(parents)-i
                if diff!=1:
                    parents=parents[:(i+1)]
            return_items=b'  '*i+JSON.dumps(self.obj_serializer.encode(item))+b'\n'+return_items
        return JSON.dumps(self.obj_serializer.encode(o))+b'\n'+return_items

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

    def loads(self, source_str, check_hash=True, load_links=True,_source=None):
        """
        create an iTree object by loading from a string.

        :param source_str: source string that contains the iTree information
        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash
        :param load_links: True - linked iTree objects will be loaded
        :param _source: Path of a loaded source file (for internal use)

        :return: iTree object loaded from file
        """
        header_str, dt_str = source_str.split(b'}***DT***')
        if DECODE:
            header_dict = JSON.loads((header_str + b'}').decode('utf-8'))
        else:
            header_dict = JSON.loads(header_str + b'}')
        if header_dict['VERSION'] != DT_SERIALIZE_VERSION:
            raise PermissionError('Wrong version of DataTree data please convert first!')
        if check_hash and ('HASH' in header_dict):
            a = hashlib.sha1(dt_str).hexdigest()
            if hashlib.sha1(dt_str).hexdigest() != header_dict['HASH']:
                raise PermissionError('Given DataTree data is corrupted (wrong hash)!')
        if DECODE:
            raw_o = JSON.loads(dt_str.decode('utf-8'))
        else:
            raw_o = JSON.loads(dt_str)
        new_tree=self.obj_serializer.decode(raw_o)
        if _source is not None:
            if new_tree._link is None:
                link_obj=iTLink()
                link_obj._source_path=_source
                new_tree._link = link_obj
            else:
                new_tree._link._source_path=_source
        if load_links:
            new_tree.load_links()
        return new_tree

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
        try:
            file_path=os.path.abspath(file_path)
        except:
            pass
        return self.loads(data, check_hash=check_hash, load_links=load_links,_source=file_path)


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
        link_str = u''
        class_name = u'iTree'
        if t is iTreeReadOnly:
            class_name = u'iTreeReadOnly'
        elif t is iTreeLink:
            class_name = u'iTreeLink'
            if item._link is not None:
                link_str = u', link=%s' % repr(item._link)
        elif t is iTreePlaceHolder:
            class_name = u'iTreePlaceHolder'
        elif t is iTreeTemporary:
            class_name = u'iTreeTemporary'
        data = item._data
        out=u''
        if data.is_empty:
            out= u'%s(%s%s)' % (class_name, repr(item.tag), link_str)
        if data.is_no_key_only:
            out= u'%s(%s%s, data=%s)' % (class_name, repr(item.tag), link_str, repr(item.d_get()))
        else:
            out= u'%s(%s%s, data=%s)' % (class_name, repr(item.tag), link_str, repr(item._data))
        return out

    def render2(self, itree_object, item_filter=None, _level=0):
        """
        prints a pretty output of the iTree object

        :param itree_object: iTree object to be converted
        :param item_filter: item filter method or filter-constant to filter specific items out
        :param _level: internal parameter for recursive calls (do not use)
        :return: string containing the pretty print aoutput
        """
        if not isinstance(itree_object, iTree):
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
            print(u''.join([u' ' * (self._identation * _level), header, self.__create_item_string(item)]))
            self.render(item, item_filter=item_filter, _level=_level + 1)

    def renders2(self, itree_object, item_filter=None, _level=0):
        """
        creates a pretty print string from iTree object
        This is the recursive version which might be a bit quicker

        :param itree_object: iTree object to be converted
        :param item_filter: item filter method or filter-constant to filter specific items out
        :param _level: internal parameter for recursive calls (do not use)
        :return: string containing the pretty print aoutput
        """
        if not isinstance(itree_object, iTree):
            raise TypeError('Can only render iTree objects, got %s instead' % (type(itree_object)))
        if _level == 0:
            output = self.__create_item_string(itree_object)
        else:
            output = u''
        if (item_filter is not None) and (not item_filter(itree_object)):
            return ''
        sub_tree = None
        for item in itree_object.iter_children(item_filter=item_filter):
            output = u''.join(
                [output, u'\n', u' ' * (self._identation * _level), self._heading, self.__create_item_string(item),
                 self.renders(item, item_filter=item_filter, _level=_level + 1)])
        return output

    def render(self, itree_object, item_filter=None):
        """
         creates a pretty print from iTree object and prints it stdout

         Note:: Filtered renderings contains always the root object and the added children might have
               confusing indentation levels because the parent elements might be filtered out

         :param itree_object: iTree object to be converted
         :param item_filter: item filter method or filter-constant to filter specific items out
                             Note:: The root of the object is not filtered and always in the outputs first line
         :return:
         """
        return self._render_main(itree_object,item_filter,True)

    def renders(self, itree_object, item_filter=None):
        """
         creates a pretty print string from iTree object ad returns it in a string

         Note:: Filtered renderings contains always the root object and the added children might have
               confusing indentation levels because the parent elements might be filtered out

         :param itree_object: iTree object to be converted

         :param item_filter: item filter method or filter-constant to filter specific items out
                             Note:: The root of the object is not filtered and always in the outputs first line
         :return: string containing the pretty print output
         """
        return self._render_main(itree_object,item_filter,False)

    def _render_main(self, itree_object, item_filter=None,_only_print_tree=False):
        """
        internal function for rendering the itertree

        :param itree_object: iTree object to be converted
        :param item_filter: item filter method or filter-constant to filter specific items out
        :param _only_print_tree: True/False print or create return string
        :return: string containing the pretty print a output
        """
        if not isinstance(itree_object, iTree):
            raise TypeError('Can only render iTree objects, got %s instead' % (type(itree_object)))
        output=[]
        items=[itree_object]
        if item_filter is not None:
            if _only_print_tree:
                out=u''.join([self.__create_item_string(itree_object)])
                try:
                    print(out)
                except UnicodeEncodeError:
                    print(out.encode().decode('cp1252'))
            else:
                output.append(
                    u''.join([self.__create_item_string(itree_object), '\n']))
        heading = u''
        while 1:
            if len(items)==0:
                break
            item=items[0]
            parent_list=items
            if (type(item) is list) and len(item) == 0:
                break
            level = 0
            while (type(item) is list):
                parent_list=item
                item=item[0]
                if (type(item) is list) and len(item) == 0:
                    del parent_list[0]
                    level=-1
                    break
                level+=1
            if level==-1:
                continue
            if item_filter is None or item_filter(item):
                if _only_print_tree:
                    out=u''.join([u' ' * (self._identation * level), heading, self.__create_item_string(item)])
                    try:
                        print(out)
                    except UnicodeEncodeError:
                        print(out.encode().decode('cp1252'))
                else:
                    output.append(u''.join([u' ' * (self._identation * level), heading, self.__create_item_string(item),'\n']))
            if level==0:
                heading = self._heading
            new_items=list(item.iter_children())
            if parent_list is None:
                items=new_items
            else:
                # replace the original item with the children
                parent_list[0]=new_items
        return u''.join(output)

