"""
This code is taken from the itertree package:

  ___ _____ _____ ____ _____ ____  _____ _____
 |_ _|_   _| ____|  _ \_   _|  _ \| ____| ____|
  | |  | | |  _| | |_) || | | |_) |  _| |  _|
  | |  | | | |___|  _ < | | |  _ <| |___| |___
 |___| |_| |_____|_| \_\|_| |_| \_\_____|_____|


https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license
For more information see: https://en.wikipedia.org/wiki/MIT_License

CONTENT DESCRIPTION:

This is a class which translates an iTree in a dot graph

This part of code contains the standard iTree serializers (JSON and rendering)
"""

from __future__ import absolute_import

import os
import platform
import gzip
import hashlib
from collections import OrderedDict

from ..itree_helpers import *

class _iTreeRenderDot(object):
    """
    Standard renderer for the iTree object for creating a very simple pretty print output
    """

    def renders(self, itree_object,filter_method=None):
        """
         creates a pretty print string from iTree object and returns it in a string

         The rendered outputs can be filtered but only in hierarchical way.

         :param itree_object: iTree object to be converted

         :param filter_method: item filter method or filter-constant to filter specific items out
                             Note:: The root of the object is not filtered and always in the outputs first line

        :param enumerate: add enumeration before the items

         :return: string containing the pretty print output
         """
        output=['graph iTree {\n    node [shape=record, fillcolor=cadetblue3, style="rounded,filled"];\n']
        item,item_str=self._build_item(itree_object,0)
        output.append('\n')
        output.append(item_str[:-2]+', fillcolor=cadetblue];')
        number,output=self.render_children(output,item,itree_object,0,filter_method)
        output.append('\n}')
        return ''.join(output)

    def _build_item(self, itree_object,number):
        item='item%i'%number
        tag_idx=itree_object.tag_idx
        if tag_idx:
            if tag_idx[0] is NoTag:
                label = '(NoTag,%i)'%tag_idx[1]
            else:
                label = repr(tag_idx)
        else:
            tag=itree_object.tag
            if tag is NoTag:
                label = 'NoTag'
            else:
                label=repr(tag)
        value=itree_object.value
        if value is not NoValue:
            item_str=item+' [label="%s| value=%s"'%(label,repr(value))
            if itree_object.is_link_root:
                item_str = item + ' [label="%s| {value=%s|%s}"' % (label, repr(value,repr(itree_object._link)))
        else:
            if itree_object.is_link_root:
                item_str = item + ' [label="%s| %s"' % (label, repr(itree_object._link))
            else:
                item_str= item + ' [label="%s"'%label
        if itree_object.is_linked:
            item_str=item_str+', fillcolor=grey'
        elif itree_object.is_value_read_only:
            item_str = item_str + ', fillcolor=cadetblue1'
        elif itree_object.is_link_root:
            item_str = item_str + ', fillcolor=cornflowerblue'
        item_str = item_str.replace('{', '\\{').replace('}', '\\}')
        return item,item_str+'];'

    def render_children(self,out,parent,itree,number,filter_method=None):
        if filter_method:
            iterator=filter(filter_method,itree)
        else:
            iterator = itree
        for item in iterator:
            number=number  + 1
            out.append('\n')
            sitem,sitem_str=self._build_item(item,number)
            out.append(sitem_str)
            if item.is_linked:
                out.append('\n %s -- %s  [style=dotted];'%(parent,sitem))
            else:
                out.append('\n %s -- %s;' % (parent, sitem))
            if item:
                number,out=self.render_children(out,sitem,item,number,filter_method)
        return number,out

