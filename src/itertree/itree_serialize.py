# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import gzip
import hashlib
from collections import OrderedDict

# For serializing we (try) to import some modules:
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
from .itree_data import iTData
from .itree_main import iTree

DT_SERIALIZE_VERSION="1.0.0"

class iTStdObjSerializer(object):
    '''
    This class converts objects to raw objects (that can be converted by standard JSON serializer)
    and back conversion is also included
    '''

    #JSON tags (We keep them small)
    TREE = 'iT'
    DATA = 'iTData'
    LINK = 'iTLink'
    TAG = 'Tag'
    DATA_MODELL='iTDM'
    DTYPE='DTYPE'
    DATA_CONTAINER='DataContainer'


    def encode(self, o):
        '''
        encode the given object to a list or dict (unordered objects)
        :param o: object
        :return: list
        '''
        t=type(o)
        if t is iTree:
            if o._flags&T:
                #we skip temporary items
                return
            dt_dict = {self.DTYPE: 'iTree',self.TAG: self.encode(o._tag)}
            data = o._data
            if data is not None:
                dt_dict[self.DATA] = self.encode(data)
            if o._flags&LINKED:
                dt_dict[self.LINK] = (o._link.file_path,o._link.key_path)
            item_list = []
            for item in o.iter_children(item_filter=N|L):
                item_list.append(self.encode(item))
            dt_dict[self.TREE] = item_list
            return dt_dict
        if t in {str,int,float,bool}:
            return o
        if t in {dict,OrderedDict,iTData}:
            dict_list=[]
            for k, v in o.items():
                dict_list.append((self.encode(k),self.encode(v)))
            if t is dict:
                return {self.DTYPE: 'dict', self.DATA_CONTAINER: dict_list}
            elif t is iTData:
                return {self.DTYPE: 'iTreeData', self.DATA_CONTAINER: dict_list}
            else:
                return {self.DTYPE: 'OrderedDict', self.DATA_CONTAINER: dict_list}
        if np is not None:
            if t is np.ndarray:
                return {self.DTYPE: 'np.array', self.DATA_CONTAINER: [i for i in o.tobytes()],'np.dtype':str(o.dtype)}
        try:
            object_list = []
            for i in o:
                object_list.append(self.encode(i))
            return {self.DTYPE: 'ITER:%s'%(str(t).split("'")[1]), self.DATA_CONTAINER: object_list}
        except:
            return o

    def decode(self, raw_o,load_links=True):
        '''
        decode the given raw_object back to the original object
        :param raw_o: raw_object (dict or list)
        :param load_links: load the links of the linked iTree objects
        :return: constructed object
        '''
        t=type(raw_o)
        if t is dict:
            o_type=raw_o.get(self.DTYPE)
            if o_type is None:
                new_dict={}
                for key,v in raw_o:
                    new_dict[self.decode(key)]=self.decode(v)
                return new_dict
            elif o_type == 'iTree':
                tag=self.decode(raw_o.get(self.TAG))
                data=raw_o.get(self.DATA)
                if data is not None:
                    data=self.decode(data)
                link=raw_o.get(self.LINK)
                if link is not None:
                    link=iTLink(link[0],link[1])
                    new_item=iTree(tag,data=data,link=link)
                    if load_links:
                        new_item.load_links()
                else:
                    tree=raw_o.get(self.TREE)
                    new_item = iTree(tag, data=data, subtree=[self.decode(i) for i in tree])
                return new_item
            elif o_type in {'iTreeData','dict','OrderedDict'}:
                if o_type=='OrderedDict':
                    new_dict=OrderedDict()
                else:
                    new_dict={}
                for i in raw_o.get(self.DATA_CONTAINER):
                    new_dict[self.decode(i[0])]=self.decode(i[1])
                return new_dict
            elif o_type.startswith('ITER:'):
                new=[self.decode(i) for i in raw_o.get(self.DATA_CONTAINER)]
                return eval('%s(new)'%o_type[5:])
            elif o_type=='np.array':
                #here we will get an exception in case numpy is not available!
                if np is None:
                    raise ImportError('Numpy is needed for decoding of this data! It is not found in the python installation')
                return np.frombuffer(bytes(bytearray(raw_o.get(self.DATA_CONTAINER))),raw_o.get('np.dtype'))
        return raw_o


class iTStdJSONSerializer(object):
    '''
    This is the standard serializer for DataTree which translates the structure
    into the JSON format.
    Users might implement there own serializers using the interface methods defined
    in this serializer
    '''


    def __init__(self, obj_serializer=None):
        self.json = JSON
        if obj_serializer is None:
            self.obj_serializer = iTStdObjSerializer()
        else:
            self.obj_serializer = obj_serializer

    def dumps(self, o, add_header=True):
        '''
        In JSON the iTree object is represented in the following form
        Item-> dict with all properties (Special keys used)
        Tree structure is stored in list

        :param o: iTree object to be serialized
        :param add_header: True - the header information will be added (containing Version info and hash)
                           False - no header pure data
        :return: string containing the serialized data
        '''
        raw_obj=self.obj_serializer.encode(o)
        dt_str = JSON.dumps(raw_obj, indent=1)
        if add_header:
            header_dict = {}
            data_hash = hashlib.sha1(bytes(dt_str.encode('utf16'))).hexdigest()
            header_dict['HASH'] = data_hash
            header_dict['TYPE'] = 'DataTree'
            header_dict['VERSION'] = DT_SERIALIZE_VERSION
            header_str = JSON.dumps(header_dict, indent=4)
            dt_str = header_str + '***DT***' + dt_str
        return dt_str

    def dump(self, o, file_path, pack=True, overwrite=False,encode='utf16'):
        '''
        Serialize iTree object into a file

        :param o: iTree object to be serialized
        :param file_path: target file path where to store the data in
        :param pack: True - gzip the data, False - do not zip
        :param overwrite: True - an existing fie will be overwritten
                          False (default) - in case the file exists an FileExistsError Exception will be raised
        :param encode: encoding that should be used (default is UTF-16)
                       ::Note: You must know the used encoding for loading the file!
        :return: None
        '''
        if os.path.exists(file_path):
            if not overwrite:
                raise FileExistsError('Error file "%s" exists already' % file_path)
            if os.path.isdir(file_path):
                raise FileExistsError('Error dir with name "%s" exists already' % file_path)
        data=bytes(self.dumps(o).encode(encode))

        if pack:
            data=gzip.compress(data)
        with open(file_path, 'wb') as fh:
            fh.write(data)

    def loads(self, source_str, check_hash=True,load_links=True):
        '''
        create an iTree object by loading from a string.

        :param source_str: source string that contains the iTree information
        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash
        :param load_links: True - linked iTree objects will be loaded
        :param decode: Give the decoding of the file (actually the decoding can't be detected automatically
        :return: iTree object loaded from file
        '''
        header_str, dt_str = source_str.split('}***DT***')
        header_dict = JSON.loads(header_str + '}')
        if header_dict['VERSION'] != DT_SERIALIZE_VERSION:
            raise PermissionError('Wrong version of DataTree data please convert first!')
        if check_hash:
            a = hashlib.sha1(bytes(dt_str.encode('utf16'))).hexdigest()
            if hashlib.sha1(bytes(dt_str.encode('utf16'))).hexdigest() != header_dict['HASH']:
                raise PermissionError('Given DataTree data is corrupted (wrong hash)!')
        raw_o = JSON.loads(dt_str)
        return self.obj_serializer.decode(raw_o,load_links=load_links)

    def load(self, file_path, check_hash=True,load_links=True,decode='utf16'):
        '''
        create an iTree object by loading from a file

        :param file_path: file path to the file that contains the iTree information
        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash
        :param load_links: True - linked iTree objects will be loaded
        :param decode: Give the decoding of the file (actually the decoding can't be detected automatically
        :return: iTree object loaded from file
        '''
        if not os.path.exists(file_path):
            raise FileNotFoundError('Error file "%s" not found' % file_path)
        with open(file_path, 'rb') as fh:
            data = fh.read()
        try:
            data = gzip.decompress(data)
        except OSError:
            #we might have an already unzipped file!
            pass
        data=data.decode(decode)
        return self.loads(data, check_hash=check_hash,load_links=load_links)

class iTStdRenderer(object):
    '''
    Standard renderer fr the iTree object for creating a very simple pretty print output
    '''
    def __init__(self):
        self._identation=4
        self._heading=u' \u2514\u2500\u2500'
        self._link_heading=u' \u2514\u2500>'

    def __create_item_string(self,item):
        '''
        internal method creating the item string
        (We do not use repr() here because we do not want to see the subtree parameter here)

        :param item: item to be printed
        :return: string containing the item information
        '''
        link_str=''
        if item._link is not None:
            link_str=', link=%s'%repr(item._link)
        data=item._data
        if data.is_empty:
            return 'iTree(%s%s)' % (repr(item.tag),link_str)
        if data.is_no_key_only:
            return 'iTree(%s%s, data=%s)'%(repr(item.tag),link_str,repr(item.get()))
        else:
            return 'iTree(%s%s, data=%s)' % (repr(item.tag),link_str, repr(item._data))

    def render(self,itree_object,item_filter=ALL,_level=0):
        '''
        prints a pretty output of the iTree object

        :param itree_object: iTree object to be converted
        :param item_filter: item filter method or filter-constant to filter specific items out
        :param _level: internal parameter for recursive calls (do not use)
        :return: string containing the pretty print aoutput
        '''
        if not hasattr(itree_object,'is_iTree'):
            raise TypeError('Can only render iTree objects, got %s instead'%(type(itree_object)))
        if _level == 0:
            print(self.__create_item_string(itree_object))
        else:
            output=[]
        sub_tree = None
        header=self._heading
        if itree_object._link is not None:
            header=self._link_heading
        for item in itree_object.iter_children(item_filter=item_filter):
            print(''.join([' '*(self._identation*_level),header,self.__create_item_string(item)]))
            self.render(item,item_filter=item_filter,_level=_level+1)

    def renders(self,itree_object,item_filter=ALL,_level=0):
        '''
        creates a pretty print string from iTree object

        :param itree_object: iTree object to be converted
        :param item_filter: item filter method or filter-constant to filter specific items out
        :param _level: internal parameter for recursive calls (do not use)
        :return: string containing the pretty print aoutput
        '''
        if not hasattr(itree_object,'is_iTree'):
            raise TypeError('Can only render iTree objects, got %s instead'%(type(itree_object)))
        if _level == 0:
            output=self.__create_item_string(itree_object)
        else:
            output=''
        sub_tree = None
        for item in itree_object.iter_children(item_filter=item_filter):
            output=''.join([output,'\n', ' '*(self._identation*_level),self._heading,self.__create_item_string(item),
            self.renders(item,item_filter=item_filter,_level=_level+1)])
        return output
