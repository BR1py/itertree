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

import os
import platform
import gzip
import hashlib
from collections import OrderedDict

from ..itree_helpers import *

class iTreeRender(object):
    """
    Standard renderer fr the iTree object for creating a very simple pretty print output
    """

    def __init__(self):
        self._identation = 3
        self._heading = '> '
        self._link_heading='>>'

    def renders(self, itree_object, filter_method=None,enumerate=False):
        """
         creates a pretty print string from iTree object and returns it in a string

         The rendered outputs can be filtered but only in hierarchical way.

         :param itree_object: iTree object to be converted

         :param filter_method: item filter method or filter-constant to filter specific items out
                             Note:: The root of the object is not filtered and always in the outputs first line

        :param enumerate: add enumeration before the items

         :return: string containing the pretty print output
         """
        return self._render_main(itree_object,filter_method,enumerate,False)

    def _build_item_str(self,itree_object,enum_cnt=None):
        out = ['%s('%itree_object.__class__.__name__]
        if itree_object._tag != NoTag:
            out.append(repr(itree_object._tag))
            out.append(', ')
        if itree_object._value != NoValue:
            out.append('value=')
            out.append(repr(itree_object._value))
            out.append(', ')
        is_links_loaded=False
        if hasattr(itree_object,'_link') and itree_object._link:
            link = itree_object._link
            if link.file_path or link.target_path:
                out.append('link=iTLink(%s,%s)' % (repr(link.file_path),repr(link.target_path)))
                out.append(', ')
            is_links_loaded=link.is_loaded
        if itree_object._flags or is_links_loaded:
            flags = itree_object._flags& (~itree_object._LINKED) #  we mask the linked out, is shown in header
            if flags!=0:
                flags = itree_object._flags
            if is_links_loaded and itree_object.is_link_root:
                flags=flags|iTFLAG.LOAD_LINKS
            if flags!=0:
                out.append('flags=%s' % (bin(flags)))
        if out[-1] == ', ':
            out = out[:-1]
        if out[-1] == ',':
            out = out[:-1]
        out.append(')\n')
        if enum_cnt is not None:
            out=['%i. '%enum_cnt]+out
        return ''.join(out)

    def _render_main(self, itree_object, filter_method=None,enumerate=False,level=0):
        """
        internal function for rendering the itertree

        :param itree_object: iTree object to be converted
        :param filter_method: item filter method or filter-constant to filter specific items out
        :param enumerate: add enumeration before the items
        :param level: helper parameter for indentation-level
        :return: rendered tree output string
        """
        output=[]
        if level==0:
            if filter_method:
                if filter_method(itree_object):
                    if enumerate:
                        output.append(self._build_item_str(itree_object,0))
                    else:
                        output.append(self._build_item_str(itree_object))
            else:
                if enumerate:
                    output.append(self._build_item_str(itree_object, 0))
                else:
                    output.append(self._build_item_str(itree_object))
        if filter_method:
            cnt=0
            for item in filter(filter_method,itree_object):
                if item.is_linked:
                    out = [' ', '.  ' * (level), self._link_heading]
                else:
                    out=[' ','.  '*(level),self._heading]
                if enumerate:
                    out.append(self._build_item_str(item, cnt))
                    cnt = cnt + 1
                else:
                    out.append(self._build_item_str(item))
                output.append(''.join(out))
                output.extend(self._render_main(item,filter_method,enumerate=enumerate,level=level+1))

        else:
            for item in itree_object:
                if item.is_linked:
                    out = [' ', '.  ' * (level), self._link_heading]
                else:
                    out = [' ', '.  ' * (level), self._heading]
                if enumerate:
                    out.append(self._build_item_str(item, cnt))
                    cnt = cnt + 1
                else:
                    out.append(self._build_item_str(item))
                output.append(''.join(out))
                output.extend(self._render_main(item, filter_method, enumerate=enumerate, level=level + 1))
        return ''.join(output)

