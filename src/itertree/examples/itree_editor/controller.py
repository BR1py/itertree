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

"""
from __future__ import absolute_import

from threading import Lock
from collections import deque,OrderedDict
from ast import literal_eval
import tempfile
import inspect
import copy
from tkinter import Tk
from itertree import *
from data_models import *

NOKEY=Data.__NOKEY__
NOVALUE=Data.__NOVALUE__

class ActionItem():
    def __init__(self,cmd_str,*args,**kwargs):
        self._cmd_str=cmd_str
        self._args=args
        self._kwargs=kwargs

    def exec(self,target_object):
        caller=target_object.__getattribute__(self._cmd_str)
        return caller(*self._args,**self._kwargs)

    def get_data_tuple(self):
        return (self._cmd_str,self._args,self._kwargs)

class PopupMenuBuilder():

    ITREE=1
    ITREELINK = 2
    ITREEREADONLY = 3

    DATA=4
    DATA_KEY=5
    LINK=6
    LINK_KEY=7


    def __init__(self,controller):
        self._controller=controller
        self._creater_by_source={self.DATA:self._create_data_popup,
                                 self.DATA_KEY:self._create_data_key_popup,
                                 self.ITREE:self._create_itree_popup,
                                 self.ITREELINK: self._create_itreelink_popup,
                                 self.ITREEREADONLY: self._create_itreereadonly_popup,

                                 self.LINK: self._create_link_popup,
                                 self.LINK_KEY: self._create_link_key_popup,
                                 }

    def _valid_clipboard_object(self,clp_data):
        if clp_data is None:
            return False
        else:
            try:
                it_items = iTree('tmp').load(self._controller._clp_file_path)
                l=len(it_items)
                if l==0:
                    return False
            except:
                return False
        return True

    def get_source_item_type(self,item,detail):
        if detail.get('is_data'):
            if detail.get('key'):
                return self.DATA_KEY
            return self.DATA
        if detail.get('is_link'):
            if detail.get('key'):
                return self.LINK_KEY
            return self.LINK
        if isinstance(item,iTreeLink):
            return self.ITREELINK
        if isinstance(item, iTreeReadOnly):
            return self.ITREEREADONLY
        return self.ITREE

    def _create_data_popup(self,context_menu,item,detail,clp_data):
        if item.is_linked:
            if not item.link_root:
                return context_menu
        if item.is_read_only:
            return context_menu
        # data dialog
        data_item = iTree('item', data={'name': 'data manipulations:'})
        context_menu.append(data_item)
        context_menu.append(iTree('separator'))
        data_item = iTree('item', data={'name': 'set data value',
                                        'tooltip': 'enter a data value directly (no model)',
                                        'action': 'set_data_value'})
        context_menu.append(data_item)
        data_item = iTree('item', data={'name': 'add new data key',
                                        'tooltip': 'add a data key where a value can be added afterwards',
                                        'action': 'add_empty_data_key'})
        context_menu.append(data_item)
        data_item = iTree('item', data={'name': 'edit data model',
                                        'tooltip': 'edit the specific data-model',
                                        'action': 'edit_data_model'})
        context_menu.append(data_item)
        context_menu.d_set('data_key', NOKEY)
        return context_menu


    def _create_data_key_popup(self, context_menu, item, detail,clp_data):
        if item.is_linked:
            if not item.link_root:
                return context_menu
        if item.is_read_only:
            return context_menu
        key = detail['text']
        try:
            key = literal_eval(key)
        except:
            pass
        context_menu.d_set('data_key', key)
        m_item = iTree('item', data={'name': 'data-key related data manipulations:'})
        context_menu.append(m_item)
        context_menu.append(iTree('separator'))
        m_item = iTree('item', data={'name': 'set data value',
                                        'tooltip': 'enter a data value directly (no model)',
                                        'action': 'set_data_value'})
        context_menu.append(m_item)
        m_item = iTree('item', data={'name': 'delete data key',
                                     'tooltip': 'remove the key from the data structure',
                                     'action': 'remove_data_key'})
        context_menu.append(m_item)

        m_item = iTree('item', data={'name': 'edit data model',
                                        'tooltip': 'edit/define the specific data-model',
                                        'action': 'edit_data_model'})
        context_menu.append(m_item)
        return context_menu

    def _create_link_popup(self,context_menu,item,detail,clp_data):
        return context_menu

    def _create_link_key_popup(self, context_menu, item, detail, clp_data):
        if isinstance(item,iTreeLink) and item.is_link_root:
            key = detail['text']
            try:
                key = literal_eval(key)
            except:
                pass
            context_menu.d_set('data_key', key)
            m_item = iTree('item', data={'name': 'set link value',
                                         'action': 'set_link_value'})
            context_menu.append(m_item)
        return context_menu


    def _create_itree_popup(self, context_menu, item, detail,clp_data):
        if item.is_root:
            title = iTree('item', data={'name': 'Tag: ' + item.tag})
        else:
            name = ['TagIdx(%s,%i)' % (t[0], t[1]) for t in item.tag_idx_path]
            title = iTree('item', data={'name': 'Tag-Idx-Path: ' + str(name)})
        context_menu.append(title)

        title.append(iTree('item', data={'name': 'Show item representations:'}))
        title+=iTree('separator')
        title.append(iTree('item', data={'name': 'Short repr() (no subtree)',
                                         'tooltip': 'print item repr in the log',
                                         'action': 'log_item_repr_short'}))
        title.append(iTree('item', data={'name': 'Full repr() (with subtree)',
                                         'tooltip': 'print item repr in the log',
                                         'action': 'log_item_repr'}))
        title.append(iTree('item', data={'name': 'Render Tree',
                                         'tooltip': 'Give the rendered item tree in the log',
                                         'action': 'log_item_render'}))

        context_menu.append(iTree('separator'))
        item_edit=iTree('item', data={'name': 'edit item'})
        context_menu.append(item_edit)
        item_edit.append(iTree('item', data={'name': 'edit item tag',
                                                'tooltip': 'change the tag of the item',
                                                'key': 'Ctrl-t',
                                                'action': 'edit_tag'}))
        if item.data.is_empty:
            item_edit.append(iTree('item', data={'name': 'set data value (no model)',
                                                'tooltip': 'enter a data value directly (no model)',
                                                'action': 'set_data_value'}))
            item_edit.append(iTree('item', data={'name': 'add new data key',
                                                'tooltip': 'add a data key where a value can be added afterwards',
                                                'action': 'add_empty_data_key'}))
            item_edit.append(iTree('item', data={'name': 'edit data model',
                                                'tooltip': 'edit/define the specific data-model',
                                                'action': 'edit_data_model'}))
        new_menu=iTree('item', data={'name': 'Create new iTree'})
        if not item.is_root:
            new_menu.append(
                iTree('item', data={'name': 'insert sibling before','action': 'insert_new_sibling_before'}))
            new_menu.append(
                iTree('item', data={'name': 'insert sibling after','action': 'insert_new_sibling_after'}))
            new_menu.append(
                iTree('item', data={'name': 'append sibling', 'action': 'append_new_sibling_after'}))
        new_menu.append(
                iTree('item', data={'name': 'append child',
                                'tooltip': 'append new child to selected item',
                                'action': 'append_new_child'}))
        context_menu.append(new_menu)

        new2_menu=iTree('item', data={'name': 'Create new iTreeLink'})
        if not item.is_root:
            new2_menu.append(
                iTree('item', data={'name': 'insert sibling before','action': 'insert_new_link_sibling_before'}))
            new2_menu.append(
                iTree('item', data={'name': 'insert sibling after','action': 'insert_new_link_sibling_after'}))
            new2_menu.append(
                iTree('item', data={'name': 'append sibling', 'action': 'append_new_link_sibling_after'}))
        new2_menu.append(
                iTree('item', data={'name': 'append child link',
                                'action': 'append_new_child_link'}))
        context_menu.append(new2_menu)

        if not item.is_root:
            context_menu.append(
                iTree('item', data={'name': 'make item read-only',
                                    'action': 'make_read_only_item'}))

            context_menu.append(
                iTree('item', data={'name': 'delete selected item',
                                    'tooltip': 'delete the selected item',
                                    'action': 'delete_item'}))
        context_menu.append(iTree('separator'))
        if not item.is_root:
            move_item = iTree('item',
                              data={'name': 'Move selected item:'})
            set=False
            if item.idx != 0:
                set=True
                move_item.append(
                    iTree('item',
                          data={'name': 'move up', 'action': 'move_up'}))
            if item.idx < len(item.parent) - 1:
                set = True

                move_item.append(
                    iTree('item',
                          data={'name': 'move down', 'action': 'move_down'}))
            if item.idx != 0:
                set = True
                move_item.append(
                    iTree('item',
                          data={'name': 'move inside first (make child)',
                                'action': 'move_inside_first'}))
            move_item.append(
                iTree('item',
                      data={'name': 'move inside last (make child)',
                            'action': 'move_inside_last'}))
            if not item.parent.is_root:
                set=True
                move_item.append(
                    iTree('item',
                          data={'name': 'move outside (make parents sibling)',
                                'tooltip': 'move selected item inside previous item (append as child)'}))
            if set:
                context_menu.append(move_item)

            context_menu.append(iTree('separator'))
        context_menu.append(
            iTree('item',
                  data={'name': 'Cut item',
                        'action': 'cut_to_clp'}))
        context_menu.append(
            iTree('item',
                  data={'name': 'Copy',
                        'action': 'copy_to_clp'}))
        context_menu.append(
            iTree('item',
                  data={'name': 'Copy item key-path',
                        'action': 'copy_key_path_to_clp'}))

        if self._valid_clipboard_object(clp_data):
            context_menu.append(
                iTree('item',
                      data={'name': 'Paste',
                            'action': 'paste_from_clp_after_item'}))
            context_menu.append(
                iTree('item',
                      data={'name': 'Paste inside',
                            'action': 'paste_from_clp_inside_item'}))

        context_menu.append(iTree('separator'))
        v_menu=iTree('item',
              data={'name': 'Tree visibility'})
        context_menu.append(v_menu)
        v_menu.append(
            iTree('item',
                  data={'name': 'collapse item',
                        'action': 'collapse_item'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'expand item',
                        'action': 'expand_item'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'collapse item and children',
                        'action': 'collapse_all_sub_items'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'expand item and children',
                        'action': 'expand_all_sub_items'}))
        #context_menu.render()
        context_menu.d_set('data_key', NOKEY)
        return context_menu

    def _create_itreereadonly_popup(self, context_menu, item, detail,clp_data):
        parent_read_only=item.parent.is_read_only

        name = ['TagIdx(%s,%i)' % (t[0], t[1]) for t in item.tag_idx_path]
        title = iTree('item', data={'name': 'Tag-Idx-Path: ' + str(name)})
        context_menu.append(title)

        title.append(iTree('item', data={'name': 'Show item representations:'}))
        title.append(iTree('separator'))
        title.append(iTree('item', data={'name': 'Short repr() (no subtree)',
                                         'tooltip': 'print item repr in the log',
                                         'action': 'log_item_repr_short'}))
        title.append(iTree('item', data={'name': 'Full repr() (with subtree)',
                                         'tooltip': 'print item repr in the log',
                                         'action': 'log_item_repr'}))
        title.append(iTree('item', data={'name': 'Render Tree',
                                         'tooltip': 'Give the rendered item tree in the log',
                                         'action': 'log_item_render'}))

        context_menu.append(iTree('separator'))
        if not parent_read_only:
            new_menu=iTree('item', data={'name': 'Create new iTree'})
            if not item.is_root:
                new_menu.append(
                    iTree('item', data={'name': 'insert sibling before','action': 'insert_new_sibling_before'}))
                new_menu.append(
                    iTree('item', data={'name': 'insert sibling after','action': 'insert_new_sibling_after'}))
                new_menu.append(
                    iTree('item', data={'name': 'append sibling', 'action': 'append_new_sibling_after'}))
            context_menu.append(new_menu)

            new2_menu=iTree('item', data={'name': 'Create new iTreeLink'})
            if not item.is_root:
                new2_menu.append(
                    iTree('item', data={'name': 'insert sibling before','action': 'insert_new_link_sibling_before'}))
                new2_menu.append(
                    iTree('item', data={'name': 'insert sibling after','action': 'insert_new_link_sibling_after'}))
                new2_menu.append(
                    iTree('item', data={'name': 'append sibling', 'action': 'append_new_link_sibling_after'}))
            context_menu.append(new2_menu)

            context_menu.append(
                iTree('item', data={'name': 'make item writeable',
                                    'action': 'make_writeable_item'}))

            context_menu.append(
                iTree('item', data={'name': 'make item and all sub children writeable',
                                    'action': 'make_writeable_item_all'}))

            context_menu.append(
                iTree('item', data={'name': 'delete selected item',
                                    'tooltip': 'delete the selected item',
                                    'action': 'delete_item'}))
            context_menu+=iTree('separator')
            move_item = iTree('item',
                              data={'name': 'Move selected item:'})
            set=False
            if item.idx != 0:
                set=True
                move_item.append(
                    iTree('item',
                          data={'name': 'move up', 'action': 'move_up'}))
            if item.idx < len(item.parent) - 1:
                set = True

                move_item.append(
                    iTree('item',
                          data={'name': 'move down', 'action': 'move_down'}))
            if not item.parent.is_root:
                set=True
                move_item.append(
                    iTree('item',
                          data={'name': 'move outside (make parents sibling)',
                                'tooltip': 'move selected item inside previous item (append as child)'}))
            if set:
                context_menu.append(move_item)

            context_menu.append(iTree('separator'))
            context_menu.append(
                iTree('item',
                      data={'name': 'Cut item',
                            'action': 'cut_to_clp'}))
        context_menu.append(
            iTree('item',
                  data={'name': 'Copy',
                        'action': 'copy_to_clp'}))
        context_menu.append(
            iTree('item',
                  data={'name': 'Copy item key-path',
                        'action': 'copy_key_path_to_clp'}))

        if not parent_read_only:
            if self._valid_clipboard_object(clp_data):
                context_menu.append(
                    iTree('item',
                          data={'name': 'Paste',
                                'action': 'paste_from_clp_after_item'}))

        context_menu.append(iTree('separator'))
        v_menu=iTree('item',
              data={'name': 'Tree visibility'})
        context_menu.append(v_menu)
        v_menu.append(
            iTree('item',
                  data={'name': 'collapse item',
                        'action': 'collapse_item'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'expand item',
                        'action': 'expand_item'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'collapse item and children',
                        'action': 'collapse_all_sub_items'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'expand item and children',
                        'action': 'expand_all_sub_items'}))
        #context_menu.render()
        context_menu.d_set('data_key', NOKEY)
        return context_menu


    def _create_itreelink_popup(self, context_menu, item, detail,clp_data):
        is_link_root=item.link_root==item
        if item.is_root:
            title = iTree('item', data={'name': 'Tag: ' + item.tag})
        else:
            name = ['TagIdx(%s,%i)' % (t[0], t[1]) for t in item.tag_idx_path]
            title = iTree('item', data={'name': 'Tag-Idx-Path: ' + str(name)})
        context_menu.append(title)

        title.append(iTree('item', data={'name': 'Show item representations:'}))
        title.append(iTree('separator'))
        title.append(iTree('item', data={'name': 'Short repr() (no subtree)',
                                         'tooltip': 'print item repr in the log',
                                         'action': 'log_item_repr_short'}))
        title.append(iTree('item', data={'name': 'Full repr() (with subtree)',
                                         'tooltip': 'print item repr in the log',
                                         'action': 'log_item_repr'}))
        title.append(iTree('item', data={'name': 'Render Tree',
                                         'tooltip': 'Give the rendered item tree in the log',
                                         'action': 'log_item_render'}))

        context_menu.append(iTree('separator'))
        if is_link_root:
            item_edit=iTree('item', data={'name': 'edit item'})
            context_menu.append(item_edit)
            item_edit.append(iTree('item', data={'name': 'edit item tag',
                                                    'tooltip': 'change the tag of the item',
                                                    'key': 'Ctrl-t',
                                                    'action': 'edit_tag'}))
            item_edit.append(iTree('item', data={'name': 'edit file link',
                                                 'action': 'edit_file_link'}))

            item_edit.append(iTree('item', data={'name': 'edit key link',
                                                 'action': 'edit_key_link'}))

            if item.data.is_empty:
                item_edit.append(iTree('item', data={'name': 'set data value (no model)',
                                                    'tooltip': 'enter a data value directly (no model)',
                                                    'action': 'set_data_value'}))
                item_edit.append(iTree('item', data={'name': 'add new data key',
                                                    'tooltip': 'add a data key where a value can be added afterwards',
                                                    'action': 'add_empty_data_key'}))
                item_edit.append(iTree('item', data={'name': 'edit data model',
                                                    'tooltip': 'edit/define the specific data-model',
                                                    'action': 'edit_data_model'}))
        new_menu=iTree('item', data={'name': 'Create new iTree'})
        if not item.is_root:
            new_menu.append(
                iTree('item', data={'name': 'insert sibling before','action': 'insert_new_sibling_before'}))
            new_menu.append(
                iTree('item', data={'name': 'insert sibling after','action': 'insert_new_sibling_after'}))
            new_menu.append(
                iTree('item', data={'name': 'append sibling', 'action': 'append_new_sibling_after'}))
        context_menu.append(new_menu)

        new2_menu=iTree('item', data={'name': 'Create new iTreeLink'})
        if not item.is_root:
            new2_menu.append(
                iTree('item', data={'name': 'insert sibling before','action': 'insert_new_link_sibling_before'}))
            new2_menu.append(
                iTree('item', data={'name': 'insert sibling after','action': 'insert_new_link_sibling_after'}))
            new2_menu.append(
                iTree('item', data={'name': 'append sibling', 'action': 'append_new_link_sibling_after'}))
        context_menu.append(new2_menu)
        context_menu.append(
            iTree('item', data={'name': 'load/relaod reference', 'action': 'load_links'}))
        if not is_link_root:
            context_menu.append(
                    iTree('item', data={'name': 'make local', 'action': 'make_item_local'}))
            if is_link_root:
                context_menu.append(
                    iTree('item', data={'name': 'delete selected item',
                                        'tooltip': 'delete the selected item',
                                        'action': 'delete_item'}))

        if is_link_root:

            new2_menu = iTree('item', data={'name': 'Load/Reload Links',
                                            'action': 'load_links'})
            context_menu.append(new2_menu)


            context_menu.append(iTree('separator'))
            if not item.is_root:
                move_item = iTree('item',
                                  data={'name': 'Move selected item:'})
                set=False
                if item.idx != 0:
                    set=True
                    move_item.append(
                        iTree('item',
                              data={'name': 'move up', 'action': 'move_up'}))
                if item.idx < len(item.parent) - 1:
                    set = True

                    move_item.append(
                        iTree('item',
                              data={'name': 'move down', 'action': 'move_down'}))
                if set:
                    context_menu.append(move_item)

                context_menu.append(iTree('separator'))
            context_menu.append(
                iTree('item',
                      data={'name': 'Cut item',
                            'action': 'cut_to_clp'}))
            context_menu.append(
                iTree('item',
                      data={'name': 'Copy',
                            'action': 'copy_to_clp'}))
        context_menu.append(
        iTree('item',
              data={'name': 'Copy item key-path',
                    'action': 'copy_key_path_to_clp'}))

        if self._valid_clipboard_object(clp_data):
            context_menu.append(
                iTree('item',
                      data={'name': 'Paste',
                            'action': 'paste_from_clp_after_item'}))

        context_menu.append(iTree('separator'))
        v_menu=iTree('item',
              data={'name': 'Tree visibility'})
        context_menu.append(v_menu)
        v_menu.append(
            iTree('item',
                  data={'name': 'collapse item',
                        'action': 'collapse_item'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'expand item',
                        'action': 'expand_item'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'collapse item and children',
                        'action': 'collapse_all_sub_items'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'expand item and children',
                        'action': 'expand_all_sub_items'}))
        #context_menu.render()
        context_menu.d_set('data_key', NOKEY)
        return context_menu

    def build_data_item_popup(self,data_item_root,data_item):
        data_item_root.append(
                            iTree('item', data={'name': 'edit value',
                                                'tooltip': 'change the data content'
                                ,'action':'edit_data_item'}))
        data_item_root.append(iTree('separator'))
        if isinstance(data_item,Data.iTDataModel):
            if data_item.__class__ in DATA_MODELS:
                data_item_root.append(
                    iTree('item', data={'name': data_item.__class__.__name__,
                                        'tooltip': 'edit data-model properties',
                                        'action':'edit_data_item_model'}))
            else:
                data_item_root.append(
                    iTree('item', data={'name': data_item.__class__.__name__, 'tooltip': 'unknown data model (no model properties editable)'}))
        else:
            data_item_root.append(
                iTree('item', data={'name': 'No data-model',
                                    'tooltip': 'No data-model value only type (no model properties editable)'}))
        data_item_root.append(iTree('separator'))
        data_models=iTree('item', data={'name': 'change data-model to:',
                                'tooltip': 'change data-model'})
        data_item_root.append(data_models)
        data_models.append(
            iTree('item', data={'name': 'NO data model/ value only',
                                'tooltip': 'change remove data model and switch to value only mode'}))
        for m in DATA_MODELS:
            data_models.append(
                iTree('item', data={'name': m.__class__.__name__,
                                    'tooltip': m.Description}))


    def _create_list_popup(self, context_menu, items,clp_data):

        title = iTree('item', data={'Multi-Selection'})
        context_menu.append(title)
        context_menu.append(iTree('separator'))
        context_menu.append(
        iTree('item', data={'name': 'Delete',
                                'tooltip': 'delete the selected item',
                                'action': 'delete_item'}))
        context_menu.append(
            iTree('item',
                  data={'name': 'Cut items',
                        'action': 'cut_to_clp'}))
        context_menu.append(
            iTree('item',
                  data={'name': 'Copy items',
                        'action': 'copy_to_clp'}))
        context_menu.append(iTree('separator'))
        v_menu=iTree('item',
              data={'name': 'Tree visibility'})
        context_menu.append(v_menu)
        v_menu.append(
            iTree('item',
                  data={'name': 'collapse item',
                        'action': 'collapse_item'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'expand item',
                        'action': 'expand_item'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'collapse item and children',
                        'action': 'collapse_all_sub_items'}))
        v_menu.append(
            iTree('item',
                  data={'name': 'expand item and children',
                        'action': 'expand_all_sub_items'}))

        context_menu.d_set('data_key', NOKEY)
        return context_menu

    def create_popup_menu_tree_items(self,sel_items,sel_details,x,y,clp_data):
        '''
        create an itree containing the related popup menu entries
        the context menu depends on the type of selection made

        :param item: selects items
        :return:
        '''

        context_menu = iTree('root', data={'x': x, 'y': y, 'sel_items': sel_items, 'sel_details': sel_details})
        l=len(sel_items)
        if l==0:
            return context_menu
        elif l==1:
            item=sel_items[0]
            if item is None:
                return context_menu
            detail = sel_details[0]
            source_type=self.get_source_item_type(item,detail)
            return self._creater_by_source[source_type](context_menu,item,detail,clp_data)
        else:
            remove=[]
            for i, (ii,d) in enumerate(zip(sel_items, sel_details)):
                if ii.is_root:
                    remove.append(i)
            for i in remove:
                del sel_items[i]
                del sel_details[i]
            return self._create_list_popup(context_menu,sel_items,clp_data)


class iTreeEditorController():
    def __init__(self):
        self._subscribers={}
        self.popup_menu_builder=PopupMenuBuilder(self)
        self._lock=Lock()
        self._temp_dir= tempfile.TemporaryDirectory()
        self._clp_file_path=self._temp_dir.name+'/copy.item'

    def subscribe(self,name):
        if name in self._subscribers:
            raise KeyError('Given subscriber is already subscribed!')
        buffer=deque()
        self._subscribers[name]=buffer
        return buffer

    def distribute(self,action_item):
        for b in self._subscribers.values():
            b.append(action_item)

    def create_new_tree(self):
        tree=iTree('root')
        action=ActionItem('update_tree',tree)
        self.distribute(action)
        action=ActionItem('log','new empty tree created')
        self.distribute(action)

    def get_popup_menu_items(self, sel_items, sel_details, x, y, clp_data):
        '''
        create an itree containing the related popup menu entries
        the context menu depends on the type of selection made
        '''
        popup_menu=self.popup_menu_builder.create_popup_menu_tree_items(sel_items,sel_details,x,y,clp_data)
        action=ActionItem('create_popup',popup_menu)
        self.distribute(action)

    #tree operations
    def item_rename(self,item,new_tag):
        old_tag=repr(item.tag)
        try:
            new_tag = literal_eval(new_tag)
        except:
            pass
        item.rename(new_tag)
        action = ActionItem('update_tree',item )
        self.distribute(action)
        action = ActionItem('log', 'Item renamed from %s to %s'%(old_tag,repr(new_tag)))
        self.distribute(action)

    def item_set_data_value(self,item,key,raw_value):
        try:
            value = eval(raw_value)
        except:
            value=raw_value
        try:
            item.d_set(key,value)
            action = ActionItem('update_tree',item )
            self.distribute(action)
            action = ActionItem('make_visible_itree_item', item,True,key)
            self.distribute(action)
        except Exception as e:
            action = ActionItem('log', '%s'%str(e))
            self.distribute(action)

    def item_set_link_value(self,item,key,raw_value):
        try:
            value = eval(raw_value)
        except:
            value=raw_value
        try:
            if key=='linked_file_path':
                new_item=iTreeLink(item.tag,
                                   link_file_path=value,
                                   link_key_path=item._link.key_path,
                                   subtree=item.iter_locals(add_placeholders=True),
                                   load_links=False)
            elif key=='linked_key_path':
                new_item=iTreeLink(item.tag,
                                   link_file_path=item._link.file_path,
                                   link_key_path=value,
                                   subtree=item.iter_locals(add_placeholders=True),
                                   load_links=False)
            else:
                return
            item.parent[item.idx]=new_item
            action = ActionItem('update_tree',new_item )
            self.distribute(action)
            action = ActionItem('make_visible_itree_item', new_item,True,key)
            self.distribute(action)
        except Exception as e:
            action = ActionItem('log', '%s'%str(e))
            self.distribute(action)

    def item_add_data_key(self,item,raw_key):
        try:
            key = literal_eval(raw_key)
        except:
            key=raw_key
        #We set no value first
        item.d_set(key=key)
        action = ActionItem('update_tree',item )
        self.distribute(action)
        action = ActionItem('make_visible_itree_item', item,True,key)
        self.distribute(action)


    def item_append_child(self,item,new_tag,itreelink=False):
        try:
            new_tag = literal_eval(new_tag)
        except:
            pass
        if itreelink:
            new_item = iTreeLink(new_tag,link_key_path='TPD',load_links=False)
        else:
            new_item = iTree(new_tag)
        item.append(new_item)
        action = ActionItem('update_tree', new_item)
        self.distribute(action)
        action = ActionItem('make_visible_itree_item', new_item,True)
        self.distribute(action)
        action = ActionItem('log', 'New child %s appended to item %s' % (repr(new_tag), repr(item.tag)))
        self.distribute(action)

    def item_insert_new(self,item, new_tag, before=False,itreelink=False):
        try:
            new_tag = literal_eval(new_tag)
        except:
            pass
        if itreelink:
            new_item = iTreeLink(new_tag,link_key_path='TPD',load_links=False)
        else:
            new_item = iTree(new_tag)
        idx = item.idx
        if not before:
            idx=idx+1
        if idx<0:
            idx=0
        item.parent.insert(idx,new_item)
        action = ActionItem('update_tree', new_item)
        self.distribute(action)
        action = ActionItem('make_visible_itree_item', new_item,True)
        self.distribute(action)
        if before:
            action = ActionItem('log', 'New child %s appended before item %s' % (repr(new_tag), repr(item.tag)))
        else:
            action = ActionItem('log', 'New child %s appended after item %s' % (repr(new_tag), repr(item.tag)))
        self.distribute(action)

    def item_insert_clp(self,target_item,clp_item_data, inside=False):
        try:
            it_items=iTree('tmp').load(self._clp_file_path)
            l=len(it_items)
            if l==0:
                return
            new_items=[i.__copy__() for i in it_items]
        except:
            action = ActionItem('log', 'No iTree item found in clipboard')
            self.distribute(action)
            return
        idx = target_item.idx
        if inside:
            for new_item in new_items:
                target_item.append(new_item)
        else:
            for new_item in new_items:
                idx+=1
                if len(target_item.parent) <= idx:
                    target_item.parent.append(new_item)
                else:
                    target_item.parent.insert(idx, new_item)
        action = ActionItem('update_tree', target_item)
        self.distribute(action)
        action = ActionItem('make_visible_itree_item', new_items[-1],True)
        self.distribute(action)
        if inside:
            action = ActionItem('log', 'New child(s) appended inside item %s' % (repr(target_item.tag)))
        else:
            action = ActionItem('log', 'New child(s) appended after item %s' % (repr(target_item.tag)))
        self.distribute(action)

    def cut_items(self,items):

        removed = iTree('COPY')
        try:
            root = items[0].root
        except:
            return
        for item in items:
            if item == root:
                continue
            try:
                removed.append(item.parent.remove(item))
            except:
                pass
        removed.dump(self._clp_file_path,pack=True,overwrite=True)
        action = ActionItem('update_tree',root)
        self.distribute(action)
        action = ActionItem('log', '%i items cut from tree (might be pasted in again)' % (len(removed)))
        self.distribute(action)

    def copy_items(self,items):
        copy=iTree('COPY')
        for item in items:
            if item.is_root:
                continue
            try:
                copy.append(item.__copy__())
            except:
                pass
        copy.dump(self._clp_file_path,pack=True,overwrite=True)

    def items_load_links(self,items):
        if len(items)==0:
            return
        for item in items:
            item.load_links(force=True, delete_invalid_items=True)
        action = ActionItem('update_tree')
        self.distribute(action)
        action = ActionItem('log', 'References loaded')
        self.distribute(action)

    def items_make_local(self, items):
        for item in items:
            if isinstance(item, iTreeLink) and not item.is_link_root:
                coupled_object=item.coupled_object
                old_items=item.iter_all()
                item=item.make_self_local()
        action = ActionItem('update_tree')
        self.distribute(action)
        action = ActionItem('make_visible_itree_item', item,True)
        self.distribute(action)

    def items_make_read_only(self, items):
        for item in items:
            if isinstance(item, iTree) and not item.is_read_only and not item.is_linked:
                idx=item.idx
                new_item=iTreeReadOnly(item.tag,subtree=item)
                item.parent[idx]=new_item
        action = ActionItem('update_tree')
        self.distribute(action)
        action = ActionItem('make_visible_itree_item', items,True)
        self.distribute(action)

    def _get_writeable_sub_items(self,parent):
        return [iTree(item.tag,data=item.data, subtree=self._get_writeable_sub_items(item)) for item in parent.iter_children()]

    def items_make_writeable(self, items,all=False):
        for item in items:
            if isinstance(item, iTree) and item.is_read_only and not item.is_linked:
                if all:
                    new_item = iTree(item.tag, data=item.data,subtree=self._get_writeable_sub_items(item))
                else:
                    new_item=iTree(item.tag,data=item.data,subtree=item)
                item.parent[item.idx]=new_item
        action = ActionItem('update_tree')
        self.distribute(action)
        action = ActionItem('make_visible_itree_item', items,True)
        self.distribute(action)

    def items_delete(self,items):
        removed=[]
        try:
            root=items[0].root
        except:
            return
        for item in items:
            if item.is_root:
                action = ActionItem('log', 'Remove of tree root ignored')
                self.distribute(action)
                continue
            try:
                removed.append(item.parent.remove(item))
            except:
                pass
        if len(removed)>0:
            action = ActionItem('update_tree', root)
            self.distribute(action)
            action = ActionItem('log', 'The following items are removed from tree: %s' % (str([i.tag for i in removed])))
            self.distribute(action)
        return removed

    def move(self,item,up=True):
        if up:
            idx=item.pre_item.idx
        else:
            idx=item.post_item.idx
        item.move(idx)
        action = ActionItem('update_tree', item)
        self.distribute(action)
        action = ActionItem('make_visible_itree_item', item,True)
        self.distribute(action)

    def move_inside(self,items,first=False):
        i=None
        for i in items:
            parent=i.parent
            idx=i.pre_item.idx
            item=i.parent.pop(i.idx)
            if first:
                parent[idx].insert(0,item)
            else:
                parent[idx].append(item)
        if i is not None:
            action = ActionItem('update_tree',parent.root) #we update whole tree!
            self.distribute(action)
            action = ActionItem('make_visible_itree_item', item, True)
            self.distribute(action)

    def open_with_ref(self,filename,load_links=True):
        new_tree=iTree('root').load(filename,load_links=True)
        action = ActionItem('update_tree',new_tree) #we update whole tree!
        self.distribute(action)
        action = ActionItem('log', 'ITree loaded from  %s' % (str(filename)))
        self.distribute(action)

    def save(self,filename,item,zip=True):
        if zip:
            if filename[:-3]!='itz':
                filename=filename+'.itz'
        else:
            if filename[:-3] != 'itr':
                filename = filename + '.itr'
        item.dump(filename,pack=zip)

    def get_data_model_data(self,data_model=None):
        if data_model is None: #empty model
            return {'name': "None", 'class': None, 'parameters': {},'parameter_types': {}, 'object': None}
        model_class=data_model.__class__
        parameters= inspect.signature(model_class).parameters
        para_dict=OrderedDict()
        para_types=OrderedDict()
        for k in parameters.keys():
            if k=='value':
                continue
            try:
                pd=data_model.__getattribute__(k)
            except:
                try:
                    pd = data_model.__getattribute__('_'+k)
                except:
                    pd=parameters[k]
            para_dict[k]=pd
            para_types[k] = type(pd)

        return {'name':model_class.__name__,'class':model_class,'parameters':para_dict,'parameter_types':para_types,'object':data_model}

    def get_predefined_models(self):
        models=[self.get_data_model_data(None)]
        for model in DATA_MODELS:
            models.append(self.get_data_model_data(model()))
        return models

    def update_data_model_data(self,model_data,key,value):
        paras=copy.copy(model_data['parameters'])
        try:
            paras[key]=literal_eval(value)
        except:
            paras[key] =value
        model_class=model_data['class']
        value=model_data['object']._value
        new_object=model_class(value, **paras)
        return self.get_data_model_data(new_object)

    def copy_to_os_clp(self,value):
        tmp=Tk()
        tmp.hidden = 0
        tmp.clipboard_clear()
        tmp.clipboard_append(value)
        tmp.destroy()

    def paste_from_os_clp(self):
        tmp = Tk()
        return tmp.clipboard_get()

    def __del__(self):
        self._temp_dir.cleanup()