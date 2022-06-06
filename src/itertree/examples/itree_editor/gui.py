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
import datetime
import pickle
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, filedialog, commondialog
import tkinter.font as tkfont
from ast import literal_eval

from itertree import *
from data_models import DATA_MODELS

NOKEY = Data.__NOKEY__
NOVALUE = Data.__NOVALUE__
VERSION = "0.0.1"

class ModelDialog(commondialog.Dialog):

    def __init__(self, parent, current_model, selection):
        self._parent = parent
        self._tk_main = parent._tk_main
        self._controller = parent._controller
        self._selection = selection
        self._model_selection = self._controller.get_predefined_models()
        self._current_model = self._controller.get_data_model_data(current_model)
        choices = [item['name'] for item in self._model_selection]
        choices.insert(0, 'CURRENT MODEL')
        self._dialog_return = None

        global pop
        self._pop = pop = tk.Toplevel(self._tk_main)
        pop.title("iTDataModel Editor (select iTDataModel and set related properties)")
        pop.geometry("675x330")
        pop.config(bg="white")
        # Create a Label Text
        # Add a Frame
        frame = tk.Frame(pop, bg="white")
        frame.pack(fill=tk.BOTH)
        self.frame = frame
        # Create a Tkinter variable
        self._tkvar = tk.StringVar(frame)

        # Dictionary with options
        self._tkvar.set(self._current_model['name'])  # set the default option
        self._popupMenu = tk.OptionMenu(frame, self._tkvar, *choices, command=self.on_model_select)
        tk.Label(frame, text="Select iTDataModel:").grid(row=0, column=0, sticky='w', columnspan=5)
        self._popupMenu.grid(row=1, column=0, sticky='w', columnspan=5)
        tk.Label(frame, text="iTDataModel Properties:").grid(row=2, column=0, sticky='w', columnspan=5)
        self._proptree = tree = ttk.Treeview(frame, columns=['nr', 'name', 'value'], show='tree headings',
                                             selectmode='extended')
        # tree.column(column='tree', width=-1, minwidth=50, stretch=True)
        tree.column(column='nr', width=20, minwidth=50, stretch=True)
        tree.column(column='name', width=150, minwidth=50, stretch=True)
        tree.column(column='value', width=500, minwidth=300, stretch=True)
        tree.column(column='#0', width=0, minwidth=0, stretch=False)
        # tree.heading('#0', text='TREE ITEMS', anchor='w')
        tree.heading('nr', text='NR', anchor='w')
        tree.heading('name', text='NAME', anchor='w')
        tree.heading('value', text='VALUE', anchor='w')
        # tree.heading('value', text='VALUE',anchor='e')
        # add a scrollbar
        self._scrollbar_tree = scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.grid(row=3, column=0, sticky='news', columnspan=5)
        self._fill_tree(self._current_model)
        tree.bind("<Double-1>", self.OnDoubleClick)

        # Add Button for making selection
        ttk.Separator(frame, orient='horizontal').grid(row=4, column=1, sticky='ew', columnspan=5)
        tk.Label(frame, text="").grid(row=5, column=0, sticky='ew')
        button1 = tk.Button(frame, text="Cancel", command=self.on_close, bg="white", fg="black")
        button1.grid(row=5, column=1, sticky='ew')
        tk.Label(frame, text="").grid(row=5, column=2, sticky='ew')
        button2 = tk.Button(frame, text="OK", command=self.on_ok, bg="white", fg="black")
        button2.grid(row=5, column=3, sticky='ew')
        tk.Label(frame, text="").grid(row=5, column=4, sticky='ew')

    def _fill_tree(self, item):
        for child in self._proptree.get_children():
            self._proptree.delete(child)
        for i, (k, v) in enumerate(item['parameters'].items()):
            prop_str = repr(v)
            self._proptree.insert('', 'end', text='', value=['%i' % (i + 1), str(k), prop_str])
        self._proptree.update()
        self._pop.update()

    def OnDoubleClick(self, event):
        item = self._proptree.identify('item', event.x, event.y)
        i = None
        selection = self._tkvar.get()
        if selection == 'CURRENT MODEL':
            props = self._current_model
        else:
            for i, model in enumerate(self._model_selection):
                if model['name'] == selection:
                    break
        if i is None:
            return
        props = self._model_selection[i]
        for i, c in enumerate(self._proptree.get_children()):
            if c == item:
                prop_name = self._proptree.item(item).get('values')[1]
                value = repr(props['parameters'][prop_name])
                answer = simpledialog.askstring("Property value", "VALUE: ", parent=self._tk_main, initialvalue=value)
                if answer is not None:
                    try:
                        self._model_selection[i] = props = self._controller.update_data_model_data(props, prop_name,
                                                                                                   answer)
                        self._fill_tree(props)
                    except:
                        pass
                break
        self.frame.focus_set()

    def on_model_select(self, env=None):
        i = None
        selection = self._tkvar.get()
        if selection == 'CURRENT MODEL':
            props = self._current_model
        else:
            for i, model in enumerate(self._model_selection):
                if model['name'] == selection:
                    props = model
                    break
        if i is None:
            return
        self._fill_tree(props)

    def on_close(self):
        self._pop.destroy()

    def on_ok(self):
        i = None
        selection = self._tkvar.get()
        if selection == 'CURRENT MODEL':
            props = self._current_model
        else:
            for i, model in enumerate(self._model_selection):
                if model['name'] == selection:
                    props = model
                    break
        if i is None:
            return
        self._parent.set_data_model(self._selection[0], self._selection[1],self._selection[2], props['object'])
        self._pop.destroy()

    def get_result(self):
        return self._dialog_return


class PopupMenuCommands():
    def __init__(self, parent):
        self._parent = parent
        self._controller = parent._controller
        self._tk_main = parent._tk_main
        self.log = parent.log

        self._active_popup = None

    def set_active_popup(self, active_popup):
        self._active_popup = active_popup

    def log_item_repr_short(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        out = repr(items[0])
        tmp = out.split(', subtree')
        if len(tmp) > 1:
            out = tmp[0] + ')'
        self.log(out)

    def log_item_repr(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        self.log(repr(items[0]))

    def log_item_render(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        self.log('\n' + items[0].renders())

    def edit_tag(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        tag = items[0].tag
        if type(tag) is not str:
            tag = repr(tag)
        answer = simpledialog.askstring("Change Item Tag", "TAG: ", initialvalue=tag,
                                        parent=self._tk_main)
        if answer is not None or answer != tag:
            self._controller.item_rename(items[0], answer)

    def edit_data_model(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        item = items[0]
        key = self._active_popup.data.get('data_key')
        try:
            data_item = item.d_get(key, return_type=Data.FULL)
            data = item.d_get(key)
        except KeyError:
            data_item = None
            data = Data.__NOVALUE__
        if isinstance(data_item, Data.iTDataModel):
            current_model = data_item
        else:
            current_model = None
        ModelDialog(self, current_model, (item, key,data))

    def set_data_model(self, item, key,data, model):
        if model is None:
            # no model selected
            item.d_set(key, data)
        else:
            try:
                model.set(data)
            except:
                self.log('Old value does not match to new model, old data value is not filled in')

            else:
                self.log('Old value put in new model')
            item.data.update([(key,model)],replace_models=True)
            self._parent.update_tree(item)

    def set_data_value(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Data Value Input", "VALUE: ", parent=self._tk_main)
        if answer is not None:
            self._controller.item_set_data_value(items[0], key=self._active_popup.data.get('data_key'),
                                                 raw_value=answer)

    def set_link_value(self):
        items = self._active_popup.data.get('sel_items')
        key=self._active_popup.data.get('data_key')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Link Value Input", "%s: "%key, parent=self._tk_main)
        if answer is not None:
            self._controller.item_set_link_value(items[0], key=key,
                                                 raw_value=answer)

    def add_empty_data_key(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Data Key Input", "KEY: ", parent=self._tk_main)
        if answer is not None:
            self._controller.item_add_data_key(items[0], answer)

    def append_new_child(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Give tag of new child to be appended", "TAG: ",
                                        parent=self._tk_main)
        if answer is not None:
            self._controller.item_append_child(items[0], answer)

    def insert_new_sibling_before(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Give tag of new item", "TAG: ",
                                        parent=self._tk_main)
        if answer is not None:
            self._controller.item_insert_new(items[0], answer, before=True)

    def insert_new_sibling_after(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Give tag of new item", "TAG: ",
                                        parent=self._tk_main)
        if answer is not None:
            self._controller.item_insert_new(items[0], answer, before=False)

    def append_new_sibling_after(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Give tag of new item", "TAG: ",
                                        parent=self._tk_main)
        if answer is not None:
            self._controller.item_append_child(items[0].parent, answer)

    def append_new_child_link(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Give tag of new child to be appended", "TAG: ",
                                        parent=self._tk_main)
        if answer is not None:
            self._controller.item_append_child(items[0], answer,itreelink=True)

    def insert_new_link_sibling_before(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Give tag of new link-item", "TAG: ",
                                        parent=self._tk_main)
        if answer is not None:
            self._controller.item_insert_new(items[0], answer, before=True,itreelink=True)

    def insert_new_link_sibling_after(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Give tag of new link-item", "TAG: ",
                                        parent=self._tk_main)
        if answer is not None:
            self._controller.item_insert_new(items[0], answer, before=False,itreelink=True)

    def append_new_link_sibling_after(self):
        items = self._active_popup.data.get('sel_items')
        if len(items) != 1:
            return
        answer = simpledialog.askstring("Give tag of new link-item", "TAG: ",
                                        parent=self._tk_main)
        if answer is not None:
            self._controller.item_append_child(items[0].parent, answer,itreelink=True)

    def load_links(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.items_load_links(items)

    def make_item_local(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.items_make_local(items)

    def make_writeable_item(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.items_make_writeable(items)

    def make_writeable_item_all(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.items_make_writeable(items,all=True)

    def make_read_only_item(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.items_make_read_only(items)

    def delete_item(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.items_delete(items)

    def move_up(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.move(items[0], up=True)

    def move_down(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.move(items[0], up=False)

    def move_inside_first(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.move_inside(items, first=True)

    def move_inside_last(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.move_inside(items, first=False)

    def cut_to_clp(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.cut_items(items)

    def copy_to_clp(self):
        items = self._active_popup.data.get('sel_items')
        self._controller.copy_items(items)

    def copy_key_path_to_clp(self):
        items = self._active_popup.data.get('sel_items')
        if len(items)!=1:
            return
        path=items[0].tag_idx_path
        self._controller.copy_to_os_clp(repr(path))

    def paste_from_clp_after_item(self):
        items = self._active_popup.data.get('sel_items')
        clp_raw = self._tk_main.clipboard_get()
        for item in items:
            self._controller.item_insert_clp(item, clp_raw, inside=False)

    def paste_from_clp_inside_item(self):
        items = self._active_popup.data.get('sel_items')
        clp_raw = self._tk_main.clipboard_get()
        for item in items:
            self._controller.item_insert_clp(item, clp_raw, inside=True)

    def expand_item(self, item=None):
        tree = self._parent._tree
        items = self._active_popup.data.get('sel_items')
        for itree_item in items:
            item = itree_item.coupled_object
            tree.item(item, open=True)
            for child in self._parent._tree.get_children(item):
                if tree.item(child).get('text') == 'data':
                    tree.item(child, open=True)
                    for key in self._parent._tree.get_children(child):
                        tree.item(key, open=True)
            tree.see(item)

    def collapse_item(self):
        tree = self._parent._tree
        items = self._active_popup.data.get('sel_items')
        for itree_item in items:
            item = itree_item.coupled_object
            tree.item(item, open=False)
            for child in self._parent._tree.get_children(item):
                if tree.item(child).get('text') == 'data':
                    tree.item(child, open=False)
                    for key in self._parent._tree.get_children(child):
                        tree.item(key, open=False)

    def expand_all_sub_items(self, item=None):
        tree = self._parent._tree
        if item is None:
            items = self._active_popup.data.get('sel_items')
        else:
            items = [item]
        for itree_item in items:
            if type(itree_item) is str:
                item = itree_item
            else:
                item = itree_item.coupled_object
            tree.item(item, open=True)
            for child in tree.get_children(item):
                self.expand_all_sub_items(child)
        tree.see(item)

    def collapse_all_sub_items(self, item=None):
        tree = self._parent._tree
        if item is None:
            items = self._active_popup.data.get('sel_items')
        else:
            items = [item]
        for itree_item in items:
            if type(itree_item) is str:
                item = itree_item
            else:
                item = itree_item.coupled_object
            tree.item(item, open=False)
            for child in self._parent._tree.get_children(item):
                self.collapse_all_sub_items(child)


class iTreeEditorGUI():
    FILETYPES = (
        ('iTree files', '*.it*'),
        ('All files', '*.*')
    )
    FILETYPES_SAVE1 = (
        ('iTree file', '*.itr'),
        ('All files', '*.*')
    )
    FILETYPES_SAVE2 = (
        ('iTree file', '*.itz'),
        ('All files', '*.*')
    )

    def __init__(self, controller):
        self._controller = controller
        self._action_buffer = self._controller.subscribe(self.__class__.__name__)
        self._tree_to_item_dict = {}
        self._active_popup = None


        self._tk_main = root = tk.Tk()

        root.title('iTreeEditor')
        root.geometry('800x600')
        mb = simpledialog.messagebox.showwarning('DISCLAIMER:',
                                                 'This is just a demo program please do not report issues found in this application')

        baseFont = tkfont.nametofont("TkDefaultFont")
        size = baseFont.cget("size")  # -ve is pixels +ve is points
        bold_font = tkfont.Font(family=baseFont.cget("family"), size=size, weight=tkfont.BOLD)
        italic_font = tkfont.Font(family=baseFont.cget("family"), size=size, slant=tkfont.ITALIC)

        # Tree
        # define columns
        self._tree = tree = ttk.Treeview(root, columns=['value'], show='tree headings', selectmode='extended')
        # tree.column(column='tree', width=-1, minwidth=50, stretch=True)
        tree.column(column='value', width=100, minwidth=50, stretch=True)
        tree.column(column='#0', width=-1, minwidth=50, stretch=True)
        tree.heading('#0', text='TREE ITEMS', anchor='w')
        tree.heading('value', text='DATA VALUE', anchor='w')

        # tree.heading('value', text='VALUE',anchor='e')
        # add a scrollbar
        self._scrollbar_tree = scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
        tree.tag_configure('BoldItem', font=bold_font)
        tree.tag_configure('ItalicItem', font=italic_font)

        tree.configure(yscroll=scrollbar.set)
        # Log
        self._log_box = text_box = tk.Text(root, height=10)
        text_box.config(state='disable')
        self._scrollbar_log = scrollbar_log = ttk.Scrollbar(root, orient=tk.VERTICAL, command=text_box.yview)
        text_box.configure(yscroll=scrollbar_log.set)
        self.__init_menubar()
        self.popup_commands = PopupMenuCommands(self)

        # position items
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky='news')
        scrollbar.grid(row=0, column=1, sticky='ns')
        text_box.grid(row=1, column=0, sticky='ew')
        scrollbar_log.grid(row=1, column=1, sticky='ns')
        # events
        root.bind("<Button-3>", self.on_popup)

        self.log('iTreeEditor initialized')

    def __init_menubar(self):
        root = self._tk_main
        # Menu
        self._menubar = menubar = tk.Menu(root)
        root.config(menu=menubar)
        self._file_menu = file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label='New itertree', command=self._controller.create_new_tree, )
        file_menu.add_separator()
        file_menu.add_command(label='Open itertree file (load references)', command=self.on_open_load_ref, )
        file_menu.add_command(label='Open itertree file (do not load references)', command=self.on_open_no_load_ref, )
        file_menu.add_command(label='Save to itertree file', command=self.on_save, )
        file_menu.add_command(label='Save to itertree file (zipped)', command=self.on_save_zip, )
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.on_close, )
        menubar.add_cascade(label="File", menu=file_menu)

        # create the Help menu
        help_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        help_menu.add_command(label='About...', command=self.on_about)

        # add the Help menu to the menubar
        menubar.add_cascade(
            label="Help",
            menu=help_menu
        )

    def create_popup(self, popup_itree, parent=None):
        if parent is None:
            menu = tk.Menu(self._tk_main, tearoff=0)
            self.popup_commands.set_active_popup(popup_itree)
        else:
            menu = parent
        for c in popup_itree:
            if c.tag == 'separator':
                menu.add_separator()
                continue
            if len(c) != 0:
                sub_menu = tk.Menu(self._tk_main, tearoff=0)
                self.create_popup(c, sub_menu)
                menu.add_cascade(label=c.data.get('name'), menu=sub_menu)
            else:
                caller = None
                action = c.data.get('action')
                if action is not None:
                    try:
                        caller = self.popup_commands.__getattribute__(action)
                    except:
                        pass
                if caller is None:
                    menu.add_command(label=c.data.get('name'))
                else:
                    menu.add_command(label=c.data.get('name'), command=caller)
        if parent is None:
            try:
                menu.tk_popup(popup_itree.data.get('x'), popup_itree.data.get('y'), 0)
            except:
                pass

    def __update_from_controller(self):
        # Timer function that takes the actions from the controller to be done
        while 1:
            if len(self._action_buffer) == 0:
                break
            action = self._action_buffer.popleft()
            action.exec(self)
        self._tk_main.after(200, self.__update_from_controller)

    def _get_related_itree_item(self, item):
        search_item = item
        itree_item = None
        while itree_item is None:
            itree_item = self._tree_to_item_dict.get(search_item)
            search_item = self._tree.parent(search_item)
            if search_item is None:
                break
        return itree_item

    def run(self):
        # run the app
        self.__update_from_controller()
        self.log('iTreeEditor start mainloop')
        self._tk_main.mainloop()

    def log(self, log_str, new_line=True, addtime=True):
        if addtime:
            t = datetime.datetime.isoformat(datetime.datetime.now())[:-3]
        else:
            t = ''
        if new_line:
            n = '\n'
        else:
            n = ''
        self._log_box.config(state='normal')
        self._log_box.insert('end', '%s %s%s' % (t, str(log_str), n))
        self._log_box.update()
        self._log_box.see(tk.END)
        self._log_box.config(state='disable')

    def _add_link(self,it_item,item):
        root = self._tree
        link_obj = it_item._link
        if link_obj  is None:
            return
        link_item = root.insert('', 'end', text='link',  tag='ItalicItem')
        root.move(link_item, item, 'end')
        if link_obj.source_path is not None:
            sub_item = root.insert('', 'end', text='source_path',value=[str(link_obj.source_path)])
            root.move(sub_item, link_item, 'end')
        link_added=False
        if link_obj.file_path is not None:
            sub_item = root.insert('', 'end', text='linked_file_path', value=[str(link_obj.file_path)], tag='ItalicItem')
            root.move(sub_item, link_item, 'end')
            link_added = True

        if link_obj.key_path is not None:
            if not link_added:
                sub_item = root.insert('', 'end', text='linked_file_path', value=[str(None)],
                                       tag='ItalicItem')
                root.move(sub_item, link_item, 'end')
            sub_item = root.insert('', 'end', text='linked_key_path', value=[str(link_obj.key_path)], tag='ItalicItem')
            root.move(sub_item, link_item, 'end')

    def _add_data(self, it_item, item):
        root = self._tree
        v = ''
        if not it_item.data.is_empty:
            if not it_item.data.is_key_empty():
                v = it_item.d_get()
                if isinstance(v, Data.iTDataModel):
                    v = v.value
                v_str = repr(v)
                data_item = root.insert('', 'end', text='data', value=[v_str], tag='ItalicItem')
            else:
                data_item = root.insert('', 'end', text='data', tag='ItalicItem')
            root.move(data_item, item, 'end')
            for k, v in it_item.data.items():
                if k == NOKEY:
                    continue
                if isinstance(v, Data.iTData):
                    v = v.value
                v_str = repr(v)
                if v is NOVALUE:
                    sub_data_item = root.insert('', 'end', text=repr(k), tag='ItalicItem')
                else:
                    sub_data_item = root.insert('', 'end', text=repr(k), value=[v_str], tag='ItalicItem')
                root.move(sub_data_item, data_item, 'end')

    def update_tree(self, it_item=None, clean=True):
        root = self._tree
        if it_item is None:
            for v in self._tree_to_item_dict.values():
                it_item=v.root
                break
        if it_item.is_root:
            self.clear_tree()
            tag = 'iTree(%s)' % it_item.tag
            t_item = root.insert('', 'end', text=str(tag), tag='BoldItem')
            self._add_link(it_item, t_item)
            self._add_data(it_item, t_item)
            it_item.set_coupled_object(t_item)
            self._tree_to_item_dict[t_item] = it_item
        else:
            if clean:
                self.clear_tree(it_item.parent)
                it_item = it_item.parent
        t_parent = it_item.coupled_object
        for child in it_item:
            text = '%s(%s)' % (child.__class__.__name__, child.tag)
            if isinstance(child,iTree) and (child.is_linked or child.is_read_only or child.is_placeholder):
                t_item = root.insert('', 'end', text=text)
            else:
                t_item = root.insert('', 'end', text=text, tag='BoldItem')
            root.move(t_item, t_parent, tk.END)
            child.set_coupled_object(t_item)
            self._tree_to_item_dict[t_item] = child
            self._add_link(child,t_item)
            self._add_data(child, t_item)
            self.update_tree(child, clean=False)
        root.update()

    def clear_tree(self, it_item=None):
        if it_item is None:
            for child in self._tree.get_children():
                self._tree.delete(child)
                it_item=self._tree_to_item_dict.get(child)
                if it_item is not None:
                    it_item.set_coupled_object(None)
            self._tree_to_item_dict = {}
        else:
            if type(it_item) is str:
                item = it_item
            else:
                item = it_item.coupled_object
            for child in self._tree.get_children(item):
                self._tree.delete(child)
                try:
                    itree_item = self._tree_to_item_dict.pop(child)
                    itree_item.set_coupled_object(None)
                except KeyError:
                    pass

    def make_visible_itree_item(self, items, select=False, data_key=None):
        if not type(items) is list:
            items=[items]
        for itree in items:
            t_item=None
            if data_key is None:
                t_item = itree.coupled_object
            else:
                if data_key == NOKEY:
                    t_item = list(self._tree.get_children(itree.coupled_object))[0]
                else:
                    t_data = list(self._tree.get_children(itree.coupled_object))[0]
                    for i in self._tree.get_children(t_data):
                        try:
                            k = literal_eval(self._tree.item(i).get('text'))
                        except:
                            k=self._tree.item(i).get('text')
                        if k == data_key:
                            t_item = i
                            break
            try:
                self._tree.see(t_item)
                if select:
                    self._tree.selection_set([t_item])
            except:
                pass

    def edit_data_item(self, item, key):
        pass

    def edit_data_item_model(self, item, key):
        pass

    # Events:
    def on_close(self, evt=None):
        self._tk_main.destroy()

    def on_about(self, evt=None):
        message = 'itertree iTreeEditor (Version %s)\n\n' % VERSION + \
                  'The editor is an example implementation showing how the iTree ' \
                  'object might be used in interaction with a GUI.\n' \
                  'Beside the example the editor might also be used to create/modify and debug iTree ' \
                  'objects. The editor is in an early implementation state and might have issues when ' \
                  'reaching specific corner cases.'
        simpledialog.messagebox.showinfo("About", message, parent=self._tk_main)

    def on_open_load_ref(self, evt=None):
        filename = filedialog.askopenfilename(title='Open a iTree File',
                                              filetypes=self.FILETYPES)
        if filename is not None:
            self._controller.open_with_ref(filename)

    def on_open_no_load_ref(self, evt=None):
        filename = filedialog.askopenfilename(title='Open a iTree File',
                                              filetypes=self.FILETYPES)
        if filename is not None:
            self._controller.open_with_ref(filename, False)

    def on_save(self, evt=None):
        filename = filedialog.asksaveasfilename(title='Save a iTree File',
                                                filetypes=self.FILETYPES_SAVE1)
        if filename is not None:
            if len(self._tree_to_item_dict) > 0:
                root = list(self._tree_to_item_dict.values())[0].root
                self._controller.save(filename, root, zip=False)

    def on_save_zip(self, evt=None):
        filename = filedialog.asksaveasfilename(title='Save a iTree File',
                                                filetypes=self.FILETYPES_SAVE2)
        if filename is not None:
            if len(self._tree_to_item_dict) > 0:
                root = list(self._tree_to_item_dict.values())[0].root
                self._controller.save(filename, root)

    def on_save_selection(self, evt=None):
        pass

    def on_popup(self, evt):
        sel = self._tree.selection()
        if type(sel) is str:
            sel = [sel]
            pass
        items = [self._get_related_itree_item(ti) for ti in sel]
        details = []
        for i, ti in enumerate(sel):
            detail = self._tree.item(ti)
            if self._tree_to_item_dict.get(self._tree.parent(ti)) == items[i]:
                if detail.get('text')=='data':
                    detail['is_data'] = True
                elif detail.get('text') == 'link':
                    detail['is_link'] = True
            elif self._tree_to_item_dict.get(self._tree.parent(self._tree.parent(ti))) == items[i]:
                detail2=self._tree.item(self._tree.parent(ti))
                if detail2.get('text')=='data':
                    detail['is_data'] = True
                elif detail2.get('text') == 'link':
                    detail['is_link'] = True
                detail['key'] = True
            details.append(detail)
        try:
            clp_data = self._tk_main.clipboard_get()
        except:
            clp_data = None
        self._controller.get_popup_menu_items(items, details, evt.x_root, evt.y_root, clp_data)
