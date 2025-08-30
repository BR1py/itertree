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

Test copy() performace.
"""

import pytest
import itertools
import copy

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestCopyL1(BasePerformance):

    def get_header(self):
        out = 'Tree copy/deepcopy operations'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out=out+'-> In the copy operations of iTree the one parent only principle is important\n'
        out = out + '   In tree.copy() old children are copied too (more or less a deepcopy is required) '
        out = out + '-> The copy.copy(tree) method is not considered because in many objects this is just first level copy\n'
        out = out + '-> The deepcopy(tree) result is kept for the comparision check\n'
        return out

    def get_callers(self):
        return {
            'iTree':[(self.it_copy,'tree.copy()',float('inf')),
                     (self.it_copycopy,'tree.copy_keep_value()',float('inf')),
                     (self.it_deepcopy,'copy.deepcopy(tree)',float('inf'))],
            'list':[(self.list_copy,'n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))',float('inf')),
                     (self.tree_copycopy,'copy.copy(tree)',float('inf')),
                     (self.list_deepcopy,'copy.deepcopy(tree)',float('inf'))],
            'deque':[(self.list_copy,'n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))',float('inf')),
                     (self.tree_copycopy,'copy.copy(tree)',float('inf')),
                     (self.list_deepcopy,'copy.deepcopy(tree)',float('inf'))],
            'blist':[(self.list_copy,'n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))',float('inf')),
                     (self.tree_copycopy,'copy.copy(tree)',float('inf')),
                     (self.list_deepcopy,'copy.deepcopy(tree)',float('inf'))],
            'dict': [(self.dict_copy, 'n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items()))',
                       float('inf')),
                      (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                      (self.dict_deepcopy, 'copy.deepcopy(tree)', float('inf'))],
            'odict': [(self.dict_copy, 'n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items()))',
                      float('inf')),
                     (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                     (self.dict_deepcopy, 'copy.deepcopy(tree)', float('inf'))],
            'iodict': [(self.dict_copy, 'n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items()))',
                       float('inf')),
                      (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                      (self.dict_deepcopy, 'copy.deepcopy(tree)', float('inf'))],
            'idict': [(self.dict_copy, 'n=tree.copy();n.update((k,(copy(i[0]),copy(i[1])) for k,i in tree.items()))',
                        float('inf')),
                       (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                       (self.dict_deepcopy, 'copy.deepcopy(tree)', float('inf'))],
            'bl_sorteddict': [(self.dict_copy, 'n=tree.copy();n.update((k,(copy(i[0]),copy(i[1])) for k,i in tree.items()))',
                       float('inf')),
                      (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                      (self.dict_deepcopy, 'copy.deepcopy(tree)', float('inf'))],
            'SC.SortedDict': [(self.dict_copy, 'n=tree.copy();n.update((k,(copy(i[0]),copy(i[1])) for k,i in tree.items()))',
                       float('inf')),
                      (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                      (self.dict_deepcopy, 'copy.deepcopy(tree)', float('inf'))],
            'XML.Element': [
                (self.et_copy, 'n=tree.copy();n.clear();n.extend((copy(i) for i in tree))',
                 float('inf')),
                (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                (self.list_deepcopy, 'copy.deepcopy(tree)', float('inf'))],
            'LXML.Element': [
                (self.et_copy, 'n=tree.copy();n.clear();n.extend((copy(i) for i in tree))',
                 float('inf')),
                (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                (self.list_deepcopy, 'copy.deepcopy(tree)', float('inf'))],
            'PT.Node': [
                (None, None, float('inf')),
                (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                (self.pt_deepcopy, 'copy.deepcopy(tree)', float('inf'))
                ],
            'llDict': [
                (None, None, float('inf')),
                (self.tree_copycopy, 'copy.copy(tree)', float('inf')),
                (self.dict_deepcopy, 'copy.deepcopy(tree)', float('inf'))
                ],
            'AT.Node': [
                (None, None, float('inf')),
                (self.at_copycopy, 'copy.copy(tree)', float('inf')),
                (self.at_deepcopy, 'copy.deepcopy(tree)', float('inf'))
                ],
        }

    def it_copy(self,key):
        tree=self.trees[key]
        new=tree.copy()
        assert len(new)==len(tree)
        assert new.get.by_idx(0) is not tree.get.by_idx(0)

    def it_copycopy(self,key):
        tree=self.trees[key]
        #new=tree.copy(levels=0)
        new=tree.copy_keep_value()
        assert len(new)==len(tree)

    def it_deepcopy(self,key):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        assert new.get.by_idx(0) is not tree.get.by_idx(0)
        self.trees2[key]=new

    def list_copy(self,key,module):
        cp = copy.copy
        tree=self.trees[key]
        new=cp(tree)
        new.clear()
        new.extend(((i[0],cp(i[1]),cp(i[2])) for i in tree))
        assert len(new)==len(tree)
        assert new[0] is not tree[0]

    def tree_copycopy(self,key,module):
        tree=self.trees[key]
        new=copy.copy(tree)
        assert len(new)==len(tree)
        assert tree is tree  # we compare to make the loop as quick as other loops
        return new

    def list_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        assert new[0] is not tree[0]
        self.trees2[key] = new

    def dict_copy(self,key,module):
        cp=copy.deepcopy
        tree=self.trees[key]
        new=copy.copy(tree)
        new.update(((k,cp(v)) for k,v in tree.items()))
        assert len(new)==len(tree)
        assert tree['0'] is tree['0'] #we compare to make the loop as quick as other loops


    def dict_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        assert new['0'] is not tree['0']
        self.trees2[key] = new

    def et_copy(self,key,module):
        cp = copy.copy
        tree=self.trees[key]
        new=cp(tree)
        new.clear()
        new.extend((cp(i) for i in tree))
        assert len(new)==len(tree)
        assert new[0] is not tree[0]

    def pt_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        assert list(new.GetChildren())[0] is not list(tree.GetChildren())[0]
        self.trees2[key] = new

    def at_copycopy(self,key,module):
        tree=self.trees[key]
        new=copy.copy(tree)
        assert len(new.children)==len(tree.children)
        assert new  is not tree  # we compare to make the loop as quick as other loops
        return new

    def at_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new.children)==len(tree.children)
        assert new.children[0] is not tree.children[0]
        self.trees2[key] = new

    def test_exec(self,key,it_t1=None,it_t2=None,it_t3=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2,it_t3

        method1, op_str1,max_items1 = caller[0]
        method2, op_str2,max_items2 = caller[1]
        method3, op_str3, max_items3 = caller[2]

        if key=='iTree':
            if max_items1>=self.max_items:
                t = self.calc_timeit(method1, key)
                it_t1=t
                self.print_time_meas_output(t,
                                            ['%s:'%obj_data['str'],
                                            '%s'%(op_str1)])
            else:
                it_t1 = float('inf')
                self.print_time_meas_output(None,
                                            ['%s:' % obj_data['str'],
                                             '%s' % (op_str1)])
            if max_items2 >= self.max_items:
                t = self.calc_timeit(method2, key)
                it_t2=t
                self.print_time_meas_output(t,'%s'%(op_str2))
            else:
                it_t2=float('inf')
                self.print_time_meas_output(None,'%s'%(op_str2))

            if max_items3 >= self.max_items:
                t = self.calc_timeit(method3, key)
                it_t3=t
                self.print_time_meas_output(t,'%s'%(op_str3))
            else:
                it_t3=float('inf')
                self.print_time_meas_output(None,'%s'%(op_str3))
        else:

            entry = False
            if max_items1 >= self.max_items:
                if method1:
                    t = self.calc_timeit(method1, key,module)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                '%s'%(op_str1)],
                                                it_t1)
                    entry=True

            else:
                self.print_time_meas_output(None,
                                            ['%s:' % obj_data['str'],
                                             '%s' % (op_str1)])
            if entry:
                if max_items2 >= self.max_items:
                    t = self.calc_timeit(method2, key,module)
                    self.print_time_meas_output(t,
                                                '%s'%(op_str2),
                                                it_t2)
                else:
                    self.print_time_meas_output(None,'%s'%(op_str2))
            else:
                if max_items2 >= self.max_items:
                    t = self.calc_timeit(method2, key,module)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],'%s'%(op_str2)],
                                                it_t2)
                else:
                    self.print_time_meas_output(None,['%s:'%obj_data['str'],'%s'%(op_str2)])


            if max_items3 >= self.max_items:
                t = self.calc_timeit(method3, key,module)
                self.print_time_meas_output(t,
                                            '%s'%(op_str3),
                                            it_t3)
            else:
               self.print_time_meas_output(None,'%s'%(op_str3))
               #for poststeps we need an input in trees2
               self.trees2[key]= method2(key,module)

        return self.trees,self.trees2,it_t1,it_t2,it_t3


class TestCopyLn(BasePerformance):

    def get_header(self):
        out = 'Tree deepcopy operations'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out=out+'-> For this nested tree we can run just deepcopy() on the other objects\n'
        out = out + '-> The comparison in brackets is with iTree.copy() function (which is infact also a deepcopy())\n'
        out = out + '-> deepcopy on other objects is limited because of RecursionError\n'
        return out

    def get_callers(self):
        return {
            'iTree':[(self.it_copy,'tree.copy()',float('inf')),
                     (self.it_deepcopy,'copy.deepcopy(tree)',float('inf'))],
            'list':(self.list_deepcopy,'copy.deepcopy(tree)',100),
            'deque':(self.list_deepcopy,'copy.deepcopy(tree)',100),
            'blist':(self.list_deepcopy,'copy.deepcopy(tree)',100),
            'dict': (self.dict_deepcopy, 'copy.deepcopy(tree)',100),
            'odict': (self.dict_deepcopy, 'copy.deepcopy(tree)',100),
            'iodict': (self.dict_deepcopy, 'copy.deepcopy(tree)',100),
            'idict': (self.dict_deepcopy, 'copy.deepcopy(tree)',100),
            'bl_sorteddict': (self.dict_deepcopy, 'copy.deepcopy(tree)',100),
            'SC.SortedDict': (self.dict_deepcopy, 'copy.deepcopy(tree)',100),
            'XML.Element': (self.list_deepcopy, 'copy.deepcopy(tree)',100),
            'LXML.Element': (self.list_deepcopy, 'copy.deepcopy(tree)',100),
            'PT.Node': (self.pt_deepcopy, 'copy.deepcopy(tree)',100),
            'TL.Tree': (self.tl_deepcopy, 'copy.deepcopy(tree)',100),
            'llDict': (self.dict_deepcopy, 'copy.deepcopy(tree)',100),
            'AT.Node': (self.at_deepcopy, 'copy.deepcopy(tree)',100),
        }

    def it_copy(self,key):
        tree=self.trees[key]
        new=tree.copy()
        assert len(new)==len(tree)
        assert new.get.by_idx(0) is not tree.get.by_idx(0)


    def it_deepcopy(self,key):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        assert new.get.by_idx(0) is not tree.get.by_idx(0)
        self.trees2[key]=new


    def list_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        assert new[0] is not tree[0]
        self.trees2[key] = new

    def dict_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        assert new['0_0'] is not tree['0_0']
        self.trees2[key] = new


    def pt_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        assert list(new.GetChildren())[0] is not list(tree.GetChildren())[0]
        self.trees2[key] = new

    def tl_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new)==len(tree)
        # looks like that deepcopy is not working on this object
        #assert new.get_node('0_0') is not tree.get_node('0_0')
        self.trees2[key] = new

    def at_deepcopy(self,key,module):
        tree=self.trees[key]
        new=copy.deepcopy(tree)
        assert len(new.children)==len(tree.children)
        assert new.children[0] is not tree.children[0]
        self.trees2[key] = new

    def test_exec(self,key,it_t1=None,it_t2=None,it_t3=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2,it_t3


        if key=='iTree':
            method1, op_str1, max_items1 = caller[0]
            method2, op_str2, max_items2 = caller[1]

            if max_items1>=self.max_items:
                t = self.calc_timeit(method1, key)
                it_t1=t
                self.print_time_meas_output(t,
                                            ['%s:'%obj_data['str'],
                                            '%s'%(op_str1)])
            else:
                it_t1 = float('inf')
                self.print_time_meas_output(None,
                                            ['%s:' % obj_data['str'],
                                             '%s' % (op_str1)])
            if max_items2 >= self.max_items:
                t = self.calc_timeit(method2, key)
                it_t2=t
                self.print_time_meas_output(t,'%s'%(op_str2))
            else:
                it_t2=float('inf')
                self.print_time_meas_output(None,'%s'%(op_str2))

        else:
            method1, op_str1, max_items1 = caller
            if max_items1 >= self.max_items:
                if method1:
                    t = self.calc_timeit(method1, key,module)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                op_str1],
                                                [it_t2,it_t1])
            else:
                self.print_time_meas_output(None,
                                            ['%s:' % obj_data['str'],
                                             '%s' % (op_str1)],post_text=' skipped -> RecursionError')

        return self.trees,self.trees2,it_t1,it_t2,it_t3
