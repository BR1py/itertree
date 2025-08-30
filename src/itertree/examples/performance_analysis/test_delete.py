# -*- coding: utf-8 -*-
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

Test delete() performance.
"""

import pytest
import itertools
import copy

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestDeleteL1(BasePerformance):

    def get_header(self):
        out = 'Delete tree items'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out=out+'-> list-like objects we do deletes first and last item delete (compared with same operations in iTree)\n'
        out=out+'-> dict-like objects we do delete via key (comppared with same operation in iTree)\n'
        return out

    def prepare_test_trees(self):
        print()
        print('Create tree copies for deletion this will take some time...')

        self.test_tree ={}

        for k,t in self.trees.items():
            if k=='TL.Tree':
                self.test_tree[k] = [copy.deepcopy(t) for i in range(3 * self.repeat)]
            else:
                self.test_tree[k] = [copy.copy(t) for i in range(3 * self.repeat)]
        print('Tree copies created for deletion')
        print()

    def get_callers(self):
        return {
            'iTree':[(self.list_del_by_idx,'del tree[0] for  ...',float('inf')),
                     (self.list_del_by_idx2, 'del tree[-1] for ...', float('inf')),
                     (self.it_del_by_key,'del tree[tag_idx] for ...',float('inf'))],
            'list':[(self.list_del_by_idx,'del tree[0]',50000),
                    (self.list_del_by_idx2,'del tree[-1]',float('inf')),],
            'deque': [(self.list_del_by_idx,'del tree[0]',float('inf')),
                    (self.list_del_by_idx2,'del tree[-1]',float('inf')),],
            'blist': [(self.list_del_by_idx,'del tree[0]',float('inf')),
                    (self.list_del_by_idx2,'del tree[-1]',float('inf')),],
            'dict': (self.dict_del_by_key, 'del tree[key]',float('inf')),
            'odict': (self.dict_del_by_key, 'del tree[key]',50000),
            'iodict': (self.dict_del_by_key, 'del tree[key]',50000),
            'idict': (self.dict_del_by_key, 'del tree[key]',500000),
            'bl_sorteddict': (self.dict_del_by_key, 'del tree[key]',float('inf')),
            'SC.SortedDict':(self.dict_del_by_key, 'del tree[key]',float('inf')),
            'XML.Element': [(self.list_del_by_idx,'del tree[0]',50000),
                    (self.list_del_by_idx2,'del tree[-1]',50000)],
            'LXML.Element': [(self.list_del_by_idx,'del tree[0]',float('inf')),
                    (self.list_del_by_idx2,'del tree[-1]',float('inf')),],
            #'PT.Node': (self.dict_del_by_key, 'del tree[key]',float('inf')), # No delete?
            'llDict': (self.dict_del_by_key, 'del tree[key]',float('inf')),
            'TL.Tree': (self.tl_del_by_key,'tree.remove_node(key)',50000),
            # 'AT.Node': (self.at_del_by_key, 'tree.children[idx]',float('inf')), # No delete?
        }

    def list_del_by_idx(self,key):
        # first is deleted
        tree=self.test_tree[key].pop()
        for i in range(self.max_items):
            if i==4999:
                a=0
            del tree[0]
        assert len(tree)==0

    def list_del_by_idx2(self,key):
        # last is deleted
        tree=self.test_tree[key].pop()
        for i in range(self.max_items):
            if i==4999:
                a=0
            del tree[-1]
        assert len(tree)==0

    def it_del_by_key(self,key):
        tree = self.test_tree[key].pop()
        for i in range(self.max_items):
            del tree[('%i'%i,0)]
        assert len(tree)==0

    def dict_del_by_key(self,key):
        tree=self.test_tree[key].pop()
        for i in range(self.max_items):
            del tree['%i'%i]
        assert len(tree)==0

    def pt_node_del_by_key(self,key):
        tree=self.test_tree[key].pop()
        for i in range(self.max_items):
            tree.GetNodeByID('%i'%i)
        assert len(tree)==0


    def tl_del_by_key(self,key):
        tree=self.test_tree[key].pop()
        for i in range(self.max_items):
            tree.remove_node('%i'%i)
        assert len(tree)==1

    def at_del_by_key(self,key):
        tree=self.test_tree[key].pop()
        for i in range(self.max_items):
            tree.remove_node('%i'%i)
        assert len(tree)==1



    def test_exec(self,key, it_t1=None, it_t2=None, it_t3=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2,it_t3
        elif type(caller) is not list:
            method,op_str,max_items=caller
            single=True
        elif len(caller)==3:
            method1, op_str1, max_items1 = caller[0]
            method2, op_str2, max_items2 = caller[1]
            method3, op_str3, max_items3 = caller[2]
            single = False

        else:
            method1, op_str1,max_items1 = caller[0]
            method2, op_str2,max_items2 = caller[1]
            single = False

        if key=='iTree':
            t = self.calc_timeit(method1, key)
            it_t2=t
            op_str=op_str1
            self.print_time_meas_output(t,
                                        ['%s (del by idx):'%obj_data['str'],
                                        '%s'%(op_str)])
            t = self.calc_timeit(method2, key)
            it_t3=t
            op_str=op_str2
            self.print_time_meas_output(t,
                                        ['%s (del by idx):'%obj_data['str'],
                                        '%s'%(op_str)])
            t = self.calc_timeit(method3, key)
            it_t1=t
            op_str=op_str3
            self.print_time_meas_output(t,
                                        ['%s (self by key):'%obj_data['str'],
                                        '%s'%(op_str)],it_t2,post_text='{:.3f}x faster as idx access')
        else:
            if single:
                if max_items>=self.max_items:
                    t = self.calc_timeit(method, key)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                '%s'%(op_str)],
                                                it_t1)
                else:
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],
                                                 '%s' % (op_str)],
                                                )


            else:
                if method1 is self.list_del_by_idx:
                    compare_time=it_t2
                else:
                    compare_time=it_t1
                if max_items1 >= self.max_items:
                    t = self.calc_timeit(method1, key)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                '%s'%(op_str1)],
                                                compare_time)
                else:
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],
                                                 '%s' % (op_str1)])
                if max_items2 >= self.max_items:

                    t = self.calc_timeit(method2, key)
                    self.print_time_meas_output(t,
                                                '%s'%(op_str2),
                                                 it_t3)
        return self.trees,self.trees2,it_t1,it_t2,it_t3


class TestGetByIdxLn(BasePerformance):

    def get_header(self):
        out = 'Get tree-item via absolute index (position) access'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out=out+'-> dict-like objects index access is realized via itertools.islice(tree,idx)\n'
        return out

    def get_callers(self):
        return {
            'iTree':[(self.it_get_idx_specific,'tree.get.by_idx(*idxs)',float('inf')),
                     (self.it_get_idx_common,'tree.get(*idxs)',float('inf'))],
            'list':(self.list_get_by_idx,'tree[idx]',float('inf')),
            'deque': (self.list_get_by_idx, 'tree[idx]',float('inf')),
            'blist': (self.list_get_by_idx, 'tree[idx]',float('inf')),
            'dict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',float('inf')),
            'odict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',float('inf')),
            'iodict': (self.idict_get_by_idx, 'tree.values()[idx]',float('inf')),
            'idict': (self.idict_get_by_idx, 'tree.values()[idx]',float('inf')),
            'bl_sorteddict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',5000),
            'SC.SortedDict':(self.dict_get_by_idx, 'next(islice(tree.values(),idx))',float('inf')),
            'XML.Element': (self.et_get_by_idx, 'tree[idx]',float('inf')),
            'LXML.Element': (self.et_get_by_idx, 'tree[idx]',float('inf')),
            'PT.Node': (self.pt_node_get_by_idx, 'next(islice(tree.GetChildren(),idx))',float('inf')),
            #'llDict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',50000),
            #'TL.Tree': (self.tl_get_by_idx, 'tree.children[idx]',50000), # no in depth index access possible
            'AT.Node': (self.at_get_by_idx, 'tree.children[idx]',float('inf')),
        }

    def it_get_idx_specific(self,key):
        tree=self.trees[key]
        c=0
        last=None
        index_list=[]
        for i in range(self.max_items):
            index_list.append(0)
            for ii in range(self.items_per_level):
                index_list[-1]=ii
                #item=tree.get.by_idx(*index_list)
                item = tree.get.by_idx(*index_list)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            index_list[-1]=1 # next level item
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def it_get_idx_common(self,key):
        tree=self.trees[key]
        c=0
        last=None
        index_list=[]
        for i in range(self.max_items):
            index_list.append(0)
            for ii in range(self.items_per_level):
                index_list[-1]=ii
                item=tree.get(*index_list)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            index_list[-1]=1 # next level item
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def list_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=None
        index_list=[]
        for i in range(self.max_items):
            index_list.append(0)
            for ii in range(self.items_per_level):
                index_list[-1]=ii
                # In depth access:
                item=tree
                for iii in index_list:
                    item=item[iii][2]
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            index_list[-1]=1 # next level item
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def dict_get_by_idx(self,key):
        islice=itertools.islice # make local
        tree=self.trees[key]
        c=0
        last=None
        index_list=[]
        for i in range(self.max_items):
            index_list.append(0)
            for ii in range(self.items_per_level):
                index_list[-1]=ii
                # In depth access:
                item=tree
                for iii in index_list:
                    item=next(islice(item.values(),iii,None))[1]
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            index_list[-1]=1 # next level item
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c


    def idict_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=None
        index_list=[]
        for i in range(self.max_items):
            index_list.append(0)
            for ii in range(self.items_per_level):
                index_list[-1]=ii
                # In depth access:
                item=tree
                for iii in index_list:
                    item=item.values()[iii][1]
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            index_list[-1]=1 # next level item
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def et_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=None
        index_list=[]
        for i in range(self.max_items):
            index_list.append(0)
            for ii in range(self.items_per_level):
                index_list[-1]=ii
                # In depth access:
                item=tree
                for iii in index_list:
                    item=item[iii]
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            index_list[-1]=1 # next level item
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c


    def pt_node_get_by_idx(self,key):
        islice=itertools.islice # make local
        tree=self.trees[key]
        c=0
        last=None
        index_list=[]
        for i in range(self.max_items):
            index_list.append(0)
            for ii in range(self.items_per_level):
                index_list[-1]=ii
                # In depth access:
                item=tree
                for iii in index_list:
                    item=next(islice(tree.GetChildren(),iii,None))
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            index_list[-1]=1 # next level item
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def at_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=None
        index_list=[]
        for i in range(self.max_items):
            index_list.append(0)
            for ii in range(self.items_per_level):
                index_list[-1]=ii
                # In depth access:
                item=tree
                for iii in index_list:
                    item=item.children[iii]
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            index_list[-1]=1 # next level item
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
                                        ['%s (index-specific access):'%obj_data['str'],
                                        '%s'%(op_str)],
                                        it_t2,post_text='{:.3f}x faster as common access')
        else:
            if single:
                if max_items>=self.max_items:
                    t = self.calc_timeit(method, key)
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
                    t = self.calc_timeit(method1, key)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                '%s'%(op_str1)],
                                                [it_t1,it_t2])
                else:
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],
                                                 '%s' % (op_str1)])
                if max_items2 >= self.max_items:

                    t = self.calc_timeit(method2, key)
                    self.print_time_meas_output(t,
                                                '%s'%(op_str2),
                                                [it_t1,it_t2])
        return self.trees,self.trees2,it_t1,it_t2

