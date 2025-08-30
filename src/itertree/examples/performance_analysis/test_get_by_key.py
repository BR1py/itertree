# -*- coding: utf-8 -*-
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

Test get items by key (or tag) performance.
"""

import pytest
import itertools

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestGetByKeyL1(BasePerformance):

    def get_header(self):
        out = 'Get tree-item via key access'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        return out

    def get_callers(self):
        return {
            'iTree':[(self.it_get_key_specific,'tree.get.by_tag_idx(key)',float('inf')),
                     (self.it_get_by_key,'tree[key]',float('inf'))],
            'list':(self.list_get_by_key1,'tree[tree.index(key)]',5000),
            'deque': (self.list_get_by_key1,'tree[tree.index(key)]',5000),
            'blist': (self.list_get_by_key1,'tree[tree.index(key)]',5000),
            'dict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'odict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'iodict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'idict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'bl_sorteddict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'SC.SortedDict':(self.dict_get_by_key, 'tree[key]',float('inf')),
            'XML.Element': (self.et_get_by_key1,'tree.find(key)',5000),
            'LXML.Element': (self.et_get_by_key1,'tree.find(key)',5000),
            'PT.Node': (self.pt_node_get_by_key, 'tree.GetNodeByID(key))',float('inf')),
            'TL.Tree': (self.tl_get_by_key, 'tree.get_node(key)',float('inf')),
            'lldict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'AT.Node': [(self.at_get_by_key, 'search.find(tree, lambda node: node.name == key)',5000),
                        (self.at_get_by_key2, 'next(dropwhile(lambda item: item.name != key, tree.children)',5000) ],
        }

    def it_get_key_specific(self,key):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.get.by_tag_idx(('%i' % i, 0))
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def it_get_by_key(self,key):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree[('%i'%i,0)]
            if item is not None:
                c+=1
            assert item is not last
            last = item
        assert self.max_items == c
        return c

    def dict_get_by_key(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree['%i'%i]
            if item is not None:
                c+=1
            assert item is not last
            last = item
        assert self.max_items == c
        return c

    def list_get_by_key1(self,key,module):
        tree=self.trees[key]
        cl=tree.__class__
        c=0
        last=None
        for i in range(self.max_items):
            item=tree[tree.index(('%i'%i,i,cl()))]
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def list_get_by_key2(self,key,module):
        dropwhile=itertools.dropwhile
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=next(dropwhile(lambda item: item[0]!='%i'%i,tree))
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def tl_get_by_key(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.get_node('%i' % i)
            if item is not None:
                c+=1
            assert item is not last
            last=item
        assert self.max_items == c
        return c

    def et_get_by_key1(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.find('T%i' % i)
            if item is not None:
                c+=1
            assert item is not last
            last=item
        assert self.max_items == c
        return c



    def et_get_by_key2(self,key,module):
        dropwhile=itertools.dropwhile
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=next(dropwhile(lambda item: item.tag!='T%i'%i,tree))
            if item is not None:
                c+=1
            assert item is not last
            last=item
        assert self.max_items == c
        return c

    def pt_node_get_by_key(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.GetNodeByID('%i' % i)
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def at_get_by_key(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item = module.search.find(tree, lambda node: node.name == "%i" % i)
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def at_get_by_key2(self,key,module):
        dropwhile = itertools.dropwhile
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item = next(dropwhile(lambda item: item.name != '%i' % i, tree.children))
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def test_exec(self,key,it_t1=None,it_t2=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2
        elif type(caller) is not list:
            method,op_str,max_items=caller
            single=True
        else:
            method1, op_str1,max_items1 = caller[0]
            method2, op_str2,max_items2 = caller[1]
            single = False

        if key=='iTree':
            t = self.calc_timeit(caller[1][0], key)
            it_t2=t
            op_str=caller[1][1]
            self.print_time_meas_output(t,
                                        ['%s (common target access):'%obj_data['str'],
                                        '%s'%(op_str)])
            t = self.calc_timeit(caller[0][0], key)
            it_t1=t
            op_str=caller[0][1]
            self.print_time_meas_output(t,
                                        ['%s (tag_idx-specific access):'%obj_data['str'],
                                        '%s'%(op_str)],it_t2,post_text='{:.3f}x faster as common access')
        else:
            if single:
                if max_items>=self.max_items:
                    t = self.calc_timeit(method, key,module)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                '%s'%(op_str)],
                                                [it_t1,it_t2])
                else:
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],
                                                 '%s' % (op_str)],
                                                )


            else:
                if max_items1 >= self.max_items:
                    t = self.calc_timeit(method1, key,module)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                '%s'%(op_str1)],
                                                [it_t1,it_t2])
                else:
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],
                                                 '%s' % (op_str1)])
                if max_items2 >= self.max_items:

                    t = self.calc_timeit(method2, key,module)
                    self.print_time_meas_output(t,
                                                '%s'%(op_str2),
                                                [it_t1,it_t2])
                else:
                    self.print_time_meas_output(None,op_str2)

        return self.trees,self.trees2,it_t1,it_t2


class TestGetByKeyLn(BasePerformance):

    def get_header(self):
        out = 'Get tree-item via key access'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out=out+'-> for list-like objects with no key related access we use itertools.dropwhile()'
        out = out + '\n   item = next(dropwhile(lambda item: item[0] != key, tree))'

        return out

    def get_callers(self):
        return {
            'iTree':[(self.it_get_key_specific,'tree.get.by_tag_idx(key)',float('inf')),
                     (self.it_get_by_key,'tree[key]',float('inf'))],
            'list':(self.list_get_by_key,'tree[tree.index(key)]',float('inf')),
            'deque': (self.list_get_by_key,'tree[tree.index(key)]',float('inf')),
            'blist': (self.list_get_by_key,'tree[tree.index(key)]',float('inf')),
            'dict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'odict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'iodict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'idict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'bl_sorteddict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'SC.SortedDict':(self.dict_get_by_key, 'tree[key]',float('inf')),
            'XML.Element': (self.et_get_by_key1,'tree.find(key)',float('inf')),
            'LXML.Element': (self.et_get_by_key1,'tree.find(key)',float('inf')),
            'PT.Node': (self.pt_node_get_by_key, 'tree.GetNodeByID(key))',float('inf')),
            'TL.Tree': (self.tl_get_by_key, 'tree.get_node(key)',float('inf')),
            'lldict': (self.dict_get_by_key, 'tree[key]',float('inf')),
            'AT.Node': [(self.at_get_by_key, 'search.find(tree, lambda node: node.name == key)',100),
                        (self.at_get_by_key2, 'next(dropwhile(lambda item: item.name != key, tree.children)',float('inf')) ],
        }

    def it_get_key_specific(self,key):
        tree=self.trees[key]
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]=('%i_%i'%(i,ii),0)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree.get.by_tag_idx(*key_list)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def it_get_by_key(self,key):
        tree=self.trees[key]
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]=('%i_%i'%(i,ii),0)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree.get(*key_list)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def dict_get_by_key(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree
                for key in key_list:
                    item=item[key][-1]
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def list_get_by_key(self,key,module):
        dropwhile=itertools.dropwhile
        tree=self.trees[key]
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree
                for key in key_list:
                    item = next(dropwhile(lambda i: i[0] != key, item))[-1]
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c


    def et_get_by_key1(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='T%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree
                for key in key_list:
                    item=item.find(key)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def pt_node_get_by_key(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                item = tree
                for k in key_list:
                    item = tree.GetNodeByID(k)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def tl_get_by_key(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        key_list=['root']
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                k='/'.join(key_list)
                item = tree.get_node(k)
                assert item is not last,'Issue finding item %s found %s'%(k,repr(item))
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def at_get_by_key(self,key,module):
        tree=self.trees[key]
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                item = tree
                for k in key_list:
                    item = module.search.find(item, lambda node: node.name == k)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def at_get_by_key2(self,key,module):
        dropwhile=itertools.dropwhile
        tree=self.trees[key]
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree
                for key in key_list:
                    item = next(dropwhile(lambda i: i.name != key, item.children))
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def test_exec(self,key,it_t1=None,it_t2=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2
        elif type(caller) is not list:
            method,op_str,max_items=caller
            single=True
        else:
            method1, op_str1,max_items1 = caller[0]
            method2, op_str2,max_items2 = caller[1]
            single = False

        if key=='iTree':
            t = self.calc_timeit(caller[1][0], key)
            it_t2=t
            op_str=caller[1][1]
            self.print_time_meas_output(t,
                                        ['%s (common target access):'%obj_data['str'],
                                        '%s'%(op_str)])
            t = self.calc_timeit(caller[0][0], key)
            it_t1=t
            op_str=caller[0][1]
            self.print_time_meas_output(t,
                                        ['%s (tag_idx-specific access):'%obj_data['str'],
                                        '%s'%(op_str)],it_t2,post_text='{:.3f}x faster as common access')
        else:
            if single:
                if max_items>=self.max_items:
                    t = self.calc_timeit(method, key,module)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                '%s'%(op_str)],
                                                [it_t1,it_t2])
                else:
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],
                                                 '%s' % (op_str)],
                                                )


            else:
                if max_items1 >= self.max_items:
                    t = self.calc_timeit(method1, key,module)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                '%s'%(op_str1)],
                                                [it_t1,it_t2])
                else:
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],
                                                 '%s' % (op_str1)])
                if max_items2 >= self.max_items:

                    t = self.calc_timeit(method2, key,module)
                    self.print_time_meas_output(t,
                                                '%s'%(op_str2),
                                                [it_t1,it_t2])
                else:
                    self.print_time_meas_output(None,op_str2)

        return self.trees,self.trees2,it_t1,it_t2
