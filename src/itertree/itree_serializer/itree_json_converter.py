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

This part of code contains the standard iTree serializers (JSON and rendering)
"""

from __future__ import absolute_import

import gzip
import hashlib
import os
from collections import OrderedDict,deque

# For serializing we (try) to import some modules:

IS_ORJSON=False
DECODE = False
try:
    import rapidjson
except:
    rapidjson = None

try:
    import orjson as JSON
    IS_ORJSON=True
    # orjson is much faster than standard json but might not be available
    import json

except:
    import json as JSON

    test=bytes(JSON.dumps({'test':'123','HASH':hashlib.sha1(b'asjhdahsdh').hexdigest()}).encode('utf8', errors='backslashreplace'))
    try:
        JSON.loads(test)
    except TypeError:
        DECODE=True

class np():
    class nparray():
        pass
try:
    import numpy as np
    # only needed in case of numpy arrays in data
    # for serializing the data
    np_loaded = True
except ImportError:
    np_loaded = False
    np=None

from itertree import *


def Converter_1_1_1_to_2_0_0(src_path,check_hash=True):
    return Converter_1_1_1_to_2_0_0_Cls().convert(src_path,check_hash)

class Converter_1_1_1_to_2_0_0_Cls(object):
    """
    This is the standard serializer for DataTree which translates the structure
    into the JSON format.
    Users might implement their own serializers using the interface methods defined
    in this serializer
    """
    ITREE_SERIALIZE_VERSION = "1.1.1"

    TREE = 'iT'
    DATA = 'DT'
    LINK = 'LK'
    TAG = 'TG'
    IDX = 'IDX'

    DATA_MODELL = 'DM'
    DTYPE = 'TP'
    DATA_CONTAINER = 'DC'

    ITREE_ITEMS_DECODE={'iT','iTRO','iTl','iTPH','iTI'}

    def convert(self,src_path,check_hash=True):
        source_str=None
        if type(src_path) is str:
            if not os.path.exists(src_path):
                raise FileNotFoundError('Error file "%s" not found' % src_path)
            with open(src_path, 'rb') as fh:
                source_str = fh.read()
        else:
            # file handle
            source_str = src_path.read()
        pack = False
        try:
            source_str = gzip.decompress(source_str)
            pack=True
        except OSError:
            # we might have an already unzipped file!
            pass
        if source_str is None:
            raise SyntaxError('File couldnot be loaded')

                
        header_str, dt_str = source_str.split(b'}***DT***')
        if DECODE:
            header_dict = JSON.loads((header_str + b'}').decode('utf-8'))
        else:
            header_dict = JSON.loads(header_str + b'}')
        if header_dict['VERSION'] != self.ITREE_SERIALIZE_VERSION:
            raise PermissionError('Wrong version of DataTree data please convert first!')
        if check_hash and ('HASH' in header_dict):
            if hashlib.sha1(dt_str).hexdigest() != header_dict['HASH']:
                raise PermissionError('Given DataTree data is corrupted (wrong hash)!')
        if DECODE:
            raw_o = JSON.loads(dt_str.decode('utf-8'))
        else:
            raw_o = JSON.loads(dt_str)
        new_tree=self.create_itree_from_raw(raw_o)
        return new_tree

    def create_itree_from_raw(self,raw_o):
        decode = self.create_itree_from_raw
        t = type(raw_o)
        if t is dict:
            o_type = raw_o.get(self.DTYPE)
            if o_type is None:
                return {decode(key): decode(v) for key, v in raw_o}
            elif o_type in self.ITREE_ITEMS_DECODE:
                tag = decode(raw_o.get(self.TAG))
                if o_type == 'iTPH':
                    return iTree(tag,flags=iTree._PLACEHOLDER)
                elif o_type == 'iTI':
                    return TagIdx(tag, raw_o.get(self.IDX))
                else:
                    data = raw_o.get(self.DATA)
                    if data is not None:
                        data = decode(data)
                    tree = raw_o.get(self.TREE)
                    link = raw_o.get(self.LINK)
                    if link is not None:
                        new_item = iTree(tag, value=data,
                                              subtree=[decode(i) for i in tree],
                                              link=iTLink(link[0],decode(link[1]))
                                         )
                    else:
                        if o_type == 'iT':
                            new_item = iTree(tag, value=data, subtree=[decode(i) for i in tree])
                        else:
                            new_item = iTree(tag, value=data,
                                                  subtree=[decode(i) for i in tree],
                                                  flags=iTree._READ_ONLY_TREE|iTree._READ_ONLY_VALUE)
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
                if not np_loaded:
                    raise ImportError(
                        'Numpy is needed for decoding of this data! It is not found in the python installation')
                return np.frombuffer(bytes(bytearray(raw_o.get(self.DATA_CONTAINER))), raw_o.get('np.dtype'))
        return raw_o

