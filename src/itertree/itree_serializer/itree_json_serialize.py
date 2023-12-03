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


This part of code contains the standard iTree serializers (JSON and rendering)
"""

from __future__ import absolute_import

import gzip
import hashlib
from collections import OrderedDict, deque

# For serializing we (try) to import some modules:

IS_ORJSON = False
DECODE = False
try:
    import rapidjson
except:
    rapidjson = None

try:
    import orjson as JSON

    IS_ORJSON = True
    # orjson is much faster than standard json but might not be available
    import json

except:
    import json as JSON

    test = bytes(JSON.dumps({'test': '123', 'HASH': hashlib.sha1(b'asjhdahsdh').hexdigest()}).encode('utf8',
                                                                                                     errors='backslashreplace'))
    try:
        JSON.loads(test)
    except TypeError:
        DECODE = True


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

from ..itree_helpers import *

DT_SERIALIZE_VERSION = "2.0.0"
DT_SERIALIZE_MAJOR_VERSION = "2.0"


class iTStdJSONSerializer2(object):
    """
    This is the standard serializer for DataTree which translates the structure
    into the JSON format.
    Users might implement their own serializers using the interface methods defined
    in this serializer
    """
    not_linked_filter = lambda i: not i.is_linked

    ALL_TYPE = 0
    BYTE_TYPE = 1
    STR_TYPE = 2
    DICT_TYPE = 3
    ITER_TYPE = 4
    NP_TYPE = 5
    IT_TYPE = 6
    IT_LINK_TYPE = 7
    IT_CONST_TYPE = 8

    NO_VALUE = 0
    NO_TAG = 1
    ANY = 2
    NO_KEY = 3

    TRANSLATE_OBJ2KEY = {NoKey: NO_KEY,
                         Any: ANY,
                         NoTag: NO_TAG,
                         NoValue: NO_VALUE}

    TRANSLATE_KEY2OBJ = {NO_KEY: NoKey,
                         ANY: Any,
                         NO_TAG: NoTag,
                         NO_VALUE: NoValue}

    CONVERT_MAP = {
        float: lambda self, o: [o, self.ALL_TYPE],
        int: lambda self, o: [o, self.ALL_TYPE],
        str: lambda self, o: [o, self.ALL_TYPE],
        tuple: lambda self, o: [[self.convert_to_json_item(i) for i in o],
                                self.ITER_TYPE,
                                o.__class__.__name__],
        type: lambda self, o: [self.TRANSLATE_OBJ2KEY[o], self.IT_CONST_TYPE],
        bytes: lambda self, o: [list(o), self.BYTE_TYPE],
        list: lambda self, o: [[self.convert_to_json_item(i) for i in o],
                               self.ITER_TYPE,
                               o.__class__.__name__],
        deque: lambda self, o: [[self.convert_to_json_item(i) for i in o],
                                self.ITER_TYPE,
                                o.__class__.__name__],
        set: lambda self, o: [[self.convert_to_json_item(i) for i in o],
                              self.ITER_TYPE,
                              o.__class__.__name__],
        dict: lambda self, o: [[(self.convert_to_json_item(k),
                                 self.convert_to_json_item(v)) for k, v in o.items()],
                               self.DICT_TYPE, o.__class__.__name__],
        OrderedDict: lambda self, o: [[(self.convert_to_json_item(k),
                                        self.convert_to_json_item(v)) for k, v in o.items()],
                                      self.DICT_TYPE, o.__class__.__name__],
    }

    CONVERT_FROM_JSON_MAP = {
        ALL_TYPE: lambda self, o: o[0],
        BYTE_TYPE: lambda self, o: b''.join([i.to_bytes(1, 'little') for i in o[0]]),
        DICT_TYPE: lambda self, o: eval(o[2])(
            [(self.convert_from_json_obj(k), self.convert_from_json_obj(v)) for k, v in o[0]]),
        ITER_TYPE: lambda self, o: eval(o[2])([self.convert_from_json_obj(v) for v in o[0]]),
        NP_TYPE: lambda self, o: self.convert_numpy(o[0], o[3], o[4]),
        IT_CONST_TYPE: lambda self, o: self.TRANSLATE_KEY2OBJ[o[0]],
        IT_TYPE: lambda self, o: self.convert_it_type(o)
    }

    if np_loaded:
        CONVERT_MAP[np.ndarray] = lambda self, o: [[int(i) for i in o.tobytes()],
                                                   self.NP_TYPE,
                                                   o.__class__.__name__,
                                                   str(o.dtype),
                                                   list(o.shape)]

    def __init__(self, itree_class):
        self.itree_class = itree_class
        self.json = JSON

    def convert_to_json_item(self, o):
        try:
            t = type(o)
            cm = self.CONVERT_MAP
            if t in cm:
                return cm[t](self, o)
            elif hasattr(o, 'get_init_args'):
                return [self.convert_to_json_item(o.get_init_args()), self.IT_TYPE,
                        o.__class__.__name__,
                        o.__class__.__module__]
            elif hasattr(o, '__iter__') or hasattr(o, '__next__'):  # This is an iterable
                convert_to_json_item = self.convert_to_json_item
                if hasattr(o, 'items') and callable(o.items):  # dict indication
                    return [[(convert_to_json_item(k), convert_to_json_item(v)) for k, v in o.items()],
                            self.DICT_TYPE, o.__class__.__name__]
                else:
                    return [[convert_to_json_item(i) for i in o], self.ITER_TYPE, o.__class__.__name__]
            else:
                return [o, self.ALL_TYPE]
        except:
            print('Issue in converting item {}'.format(o))
            raise

    def convert_numpy(self, data, dtype, shape):
        raw_bytes = np.array(data, dtype=np.uint8)
        flat_array = np.frombuffer(raw_bytes, dtype)
        return flat_array.reshape(shape)

    def convert_it_type(self, o):
        class_name = o[2]
        object_class = None
        try:
            object_class = eval(class_name)
        except:
            pass
        if object_class is None:
            module_name = o[3]
            if module_name.endswith('itree_data'):
                try:
                    object_class = eval('Data.%s' % class_name)
                except:
                    pass
            elif module_name.endswith('itree_filter'):
                try:
                    object_class = eval('Filters.%s' % class_name)
                except:
                    pass
            if object_class is None:
                try:
                    object_class = eval('%s.%s' % (module_name, class_name))
                except:
                    try:
                        exec('import %s' % module_name)
                        object_class = eval('%s.%s' % (module_name, class_name))
                    except:
                        pass
        if object_class is None:
            raise TypeError('Target-Object: %s.%s could not be created, '
                            'ensure related import (from xxx import yyy is available' % (module_name, class_name))
        return object_class(*self.convert_from_json_obj(o[0]))

    def convert_from_json_obj(self, json_obj):

        try:
            try:
                t = json_obj[1]
            except:
                return json_obj
            return self.CONVERT_FROM_JSON_MAP[t](self, json_obj)
        except Exception as e:
            args = list(e.args)
            args[0] = 'Issue in object %s; \n%s' % (repr(json_obj), args[0])
            e.args = tuple(args)
            raise

    def convert_single_itree_to_json_obj(self, depth, itree, fidx):
        convert_to_json_item = self.convert_to_json_item
        data = [depth, fidx]
        data.extend(convert_to_json_item(arg) for arg in itree.__class__._get_args_skip_subtree(itree))
        try:
            return b' ' * 2 * depth + JSON.dumps(data)
        except TypeError as e:
            raise TypeError('%s -> %s' % (str(e), str((itree))))

    def convert_single_itree_to_json_obj2(self, depth, itree, fidx):
        convert_to_json_item = self.convert_to_json_item
        data = [depth, fidx]
        data.extend(convert_to_json_item(arg) for arg in itree.__class__._get_args_skip_subtree(itree))
        try:
            return b' ' * 2 * depth + bytes(JSON.dumps(data, indent=2).encode('utf8', errors='backslashreplace'))
        except TypeError as e:
            raise TypeError('%s -> %s' % (str(e), str((itree))))

    def dumps(self, o, add_header=False, calc_hash=False, filter_method=None):
        """
        In JSON the iTree object is represented in the following form
        Item-> dict with all properties (Special keys used)
        Tree structure is stored in list

        :param o: iTree object to be serialized
        :param add_header: True - the header information will be added (containing Version info and hash)
                           False - no header pure data
        :param calc_hash: True - A sha1 hash is calculated over the data section of iTree and added in the header
                          False - no hash will be calculated

        :rtype: tuple
        :return: hash,string containing the serialized data -> if no hash calculation requested hash will be None
        """
        if IS_ORJSON:
            convert = self.convert_single_itree_to_json_obj
        else:
            convert = self.convert_single_itree_to_json_obj2

        if filter_method:
            tree_json = [convert(d, i, fidx) for d, fidx, i in
                         o.__class__._iter_deep_locals_add_placeholders_filtered(o, filter_method)]
        else:
            tree_json = [convert(d, i, fidx) for d, fidx, i in o.__class__._iter_deep_locals_add_placeholders(o)]
        dt_str = b'[\n' + convert(0, o, 0) + b',\n' + b',\n'.join(tree_json) + b'\n]'
        if calc_hash:
            data_hash = hashlib.sha256(dt_str).hexdigest()
        if add_header:
            class_name = self.itree_class.__name__
            if class_name == 'iTree':
                full_name = 'itertree.iTree'
            else:
                module = self.itree_class.__module__
                full_name = module + '.' + class_name
            header_dict = {'TYPE': full_name, 'VERSION': DT_SERIALIZE_VERSION}
            if calc_hash:
                header_dict['HASH'] = data_hash
            if IS_ORJSON:
                header_str = JSON.dumps(header_dict)
            else:
                header_str = bytes(JSON.dumps(header_dict, indent=2).encode('utf8', errors='backslashreplace'))
            dt_str = b'[\n' + header_str + b',\n' + dt_str + b']'
        if calc_hash:
            return data_hash, dt_str
        return dt_str

    def dump(self, o, file_path, pack=True, calc_hash=True, overwrite=False, filter_method=None):
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
        if calc_hash:
            data_hash, data = self.dumps(o, add_header=True, calc_hash=calc_hash, filter_method=filter_method)
        else:
            data = self.dumps(o, add_header=True, calc_hash=calc_hash, filter_method=filter_method)
        if pack:
            data = gzip.compress(data)
        if is_hdl:
            file_path.write(data)
        else:
            with open(file_path, 'wb') as fh:
                fh.write(data)
        return data_hash if calc_hash else True

    def create_itree_from_raw(self, raw_o):
        convert_from_json_obj = self.convert_from_json_obj
        itree_class = self.itree_class
        # root=itree_class(*[convert_from_json_obj(arg)  for arg in raw_o[2:]])
        level_datas = [[]]
        for item_data in raw_o:
            try:
                depth = item_data[0]
                s = len(level_datas) - 1
                if depth == s:
                    level_datas[depth].append(item_data)
                elif depth == s + 1:
                    level_datas.append([item_data])
                elif depth < s:
                    for _ in range(s - depth):
                        main_args = level_datas[-2][-1]
                        if len(main_args) > 2:
                            a = 1
                        if type(main_args) is not list:
                            raise SyntaxError(
                                'Something wrong in structure in between {} and {}'.format(main_args, item_data))
                        it = itree_class(convert_from_json_obj(main_args[2]),  # tag
                                         convert_from_json_obj(main_args[3]),  # value
                                         # subtree:
                                         (itree_class(*[convert_from_json_obj(arg)
                                                        for arg in args[2:]])
                                          if type(args) is list else args for args in level_datas[-1]),
                                         # additional arguments
                                         *[convert_from_json_obj(arg) for arg in main_args[5:]])
                        del level_datas[-1]
                        level_datas[-1][-1] = it
                    level_datas[-1].append(item_data)
                else:
                    raise SyntaxError('During build of {} from serialized data '
                                      'an implausible depth step upwards was found in item: {}'.format(
                                       self.itree_class.__name__, str(item_data)))
            except:
                print('Issue in {}'.format(item_data))
                raise
        for _ in range(len(level_datas) - 1):
            main_args = level_datas[-2][-1]
            if type(main_args) is not list:
                raise SyntaxError('Something wrong in structure in {}'.format(main_args))
            it = itree_class(convert_from_json_obj(main_args[2]),  # tag
                             convert_from_json_obj(main_args[3]),  # value
                             # subtree:
                             (itree_class(*[convert_from_json_obj(arg)
                                            for arg in args[2:]])
                              if type(args) is list else args for args in level_datas[-1]),
                             # additional arguments
                             *[convert_from_json_obj(arg) for arg in main_args[5:]])
            del level_datas[-1]
            level_datas[-1][-1] = it

        return it

    def create_itree_from_raw2(self, raw_o):
        convert_from_json_obj = self.obj_serializer.convert_from_json_obj
        itree_class = self.itree_class
        _, args = raw_o.pop(-1)
        new_itree = itree_class(*[convert_from_json_obj(arg) for arg in args])
        last_kp = 1
        last_item = new_itree
        for kp, args in raw_o:
            if kp != last_kp:
                last_kp = kp
                new_index = [-1] * (kp - 1)
                last_item = new_itree.getitem_deep(new_index)
                # for _ in range((kp-1)):
                #    last_item=last_item[-1]
            last_item._append(itree_class(*[convert_from_json_obj(arg) for arg in args]))
        return new_itree

    def loads(self, source_str, check_hash=True, load_links=True, _source=None):
        """
        create an iTree object by loading from a string.

        :param source_str: source string that contains the iTree information
        :param check_hash: True the hash of the file will be checked and the loading will be stopped if it doesn't match
                           False - do not check the iTree hash
        :param load_links: True - linked iTree objects will be loaded
        :param _source: Path of a loaded source file (for internal use)

        :return: iTree object loaded from file
        """
        if DECODE:
            raw_o = JSON.loads(source_str.decode('utf-8'))
        else:
            raw_o = JSON.loads(source_str)
        if type(raw_o) is not list:
            raise SyntaxError('Unknown input file format')
        if len(raw_o) == 2 and type(raw_o[0]) is dict:
            # header found
            header_dict, tree_data = raw_o
            version = header_dict['VERSION']
            i = version.rindex('.')
            if version[:i] != DT_SERIALIZE_MAJOR_VERSION:
                raise SyntaxError('Wrong version of serialization file please convert first!')
            if check_hash and ('HASH' in header_dict):
                i = source_str.find(b'},\n') + 3
                if hashlib.sha256(source_str[i:-1]).hexdigest() != header_dict['HASH']:
                    raise PermissionError('Given tree data is corrupted (wrong hash)!')
        else:
            tree_data = raw_o
        new_tree = self.create_itree_from_raw(tree_data)
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
            file_path = os.path.abspath(file_path)
        except:
            pass
        return self.loads(data, check_hash, load_links, file_path)
