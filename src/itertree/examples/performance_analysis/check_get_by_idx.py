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

Test get item by index performance.
"""

import pytest
import itertools

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestGetByIdxL1(BasePerformance):

    def get_header(self):
        out = 'Get tree-item via absolute index (position) access'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out=out+'-> dict-like objects index access is realized via itertools.islice(tree,idx)\n'
        return out

    def get_callers(self):
        return {
            'iTree':[(self.it_get_idx_specific,'tree.get.by_idx(idx)',float('inf')),
                     (self.list_get_by_idx,'tree[idx]',float('inf'))],
            'list':(self.list_get_by_idx,'tree[idx]',float('inf')),
            'deque': (self.list_get_by_idx, 'tree[idx]',float('inf')),
            'blist': (self.list_get_by_idx, 'tree[idx]',float('inf')),
            'dict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',50000),
            'odict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',5000),
            'iodict': (self.idict_get_by_idx, 'tree.values()[idx]',float('inf')),
            'idict': (self.idict_get_by_idx, 'tree.values()[idx]',float('inf')),
            'bl_sorteddict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',5000),
            'SC.SortedDict':(self.dict_get_by_idx, 'next(islice(tree.values(),idx))',float('inf')),
            'XML.Element': (self.list_get_by_idx, 'tree[idx]',float('inf')),
            'LXML.Element': (self.list_get_by_idx, 'tree[idx]',50000),
            'PT.Node': (self.pt_node_get_by_idx, 'next(islice(tree.GetChildren(),idx))',50000),
            'llDict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',5000),
            'TL.Tree': (self.tl_get_by_idx, 'tree.children[idx]',5000),
            'AT.Node': (self.at_get_by_idx, 'tree.children[idx]',float('inf')),
        }

    def it_get_idx_specific(self,key):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.get.by_idx(i)
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def list_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree[i]
            if item is not None:
                c+=1
            assert item is not last
            last = item

        assert self.max_items == c
        return c

    def dict_get_by_idx(self,key):
        islice=itertools.islice # make local
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            #item = list(tree.values())[i]
            item=next(islice(tree.values(),i,None)) # this solution is quicker
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def idict_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.values()[i]
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c


    def pt_node_get_by_idx(self,key):
        islice=itertools.islice # make local
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=next(islice(tree.GetChildren(),i,None))
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def tl_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.children('root')[i]
            if item is not None:
                c+=1
            assert item is not last
            last = item
        assert self.max_items == c
        return c

    def at_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.children[i]
            if item is not None:
                c+=1
            assert item is not last
            last = item
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
                                        ['%s (index-specific access):'%obj_data['str'],
                                        '%s'%(op_str)],it_t2,post_text='{:.3f}x faster as common access')
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

