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

Test performance of iterations (iter()).
"""

import pytest
import itertools

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestIterL1(BasePerformance):

    def get_header(self):
        out = 'Iter over all level 1 children'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        return out

    def get_callers(self):
        return {
            'iTree':(self.tree_iter,'for i in tree: ....',float('inf')),

            'list':(self.tree_iter,'for i in tree: ....',float('inf')),
            'deque': (self.tree_iter,'for i in tree: ....',float('inf')),
            'blist': (self.tree_iter,'for i in tree: ....',float('inf')),
            'dict': (self.tree_iter,'for i in tree.items(): ....',float('inf')),
            'odict': (self.tree_iter,'for i in tree.items(): ....',float('inf')),
            'iodict': (self.tree_iter,'for i in tree.items(): ....',float('inf')),
            'idict': (self.tree_iter,'for i in tree.items(): ....',float('inf')),
            'bl_sorteddict': (self.tree_iter,'for i in tree.items(): ....',float('inf')),
            'SC.SortedDict': (self.tree_iter, 'for i in tree.items(): ....', float('inf')),
            'XML.Element': (self.tree_iter,'for i in tree: ....',float('inf')),
            'LXML.Element': (self.tree_iter,'for i in tree: ....',float('inf')),
            'PT.Node': (self.pt_iter, 'for i in tree.GetChildren(): ....',float('inf')),
            'llDict': (self.tree_iter, 'for i in tree.items(): ....', float('inf')),
            'TL.Tree': (self.tl_iter, 'for i in tree.children("root"): ....',float('inf')),
            'AT.Node': (self.at_iter, 'for i in tree.children: ....',float('inf')),
        }

    def tree_iter(self,key):
        tree=self.trees[key]
        for i in tree:
            assert i is not None

    def dict_iter(self,key):
        tree=self.trees[key]
        for i in tree.items():
            assert i is not None

    def pt_iter(self,key):
        tree=self.trees[key]
        for i in tree.GetChildren():
            assert i is not None

    def tl_iter(self,key):
        tree=self.trees[key]
        for i in tree.children('root'):
            assert i is not None

    def at_iter(self,key):
        tree=self.trees[key]
        for i in tree.children:
            assert i is not None

    def test_exec(self,key,it_t1=None,it_t2=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2
        method,op_str,max_items=caller

        if key=='iTree':
            t = self.calc_timeit(caller[0],key)
            it_t1=t
            op_str=caller[1]
            self.print_time_meas_output(t,
                                        ['%s:'%obj_data['str'],
                                        op_str])
        else:
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

        return self.trees,self.trees2,it_t1,it_t2



class TestIterLn(BasePerformance):

    def get_header(self):
        out = 'Iter over all in-depth children'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        return out

    def get_callers(self):
        return {
            'iTree':(self.it_iter,'for i in tree.deep: ....',float('inf')),

            'list':(self.list_iter,'for i in tree: for ii in i ....',float('inf')),
            'deque': (self.list_iter,'for i in tree: for ii in i ....',float('inf')),
            'blist': (self.list_iter,'for i in tree: for ii in i ....',float('inf')),
            'dict': (self.dict_iter,'for i in tree.values(): for ii in i.values(): ....',float('inf')),
            'odict': (self.dict_iter,'for i in tree.values(): for ii in i.values(): ....',float('inf')),
            'iodict': (self.dict_iter,'for i in tree.values(): for ii in i.values(): ....',float('inf')),
            'idict': (self.dict_iter,'for i in tree.values(): for ii in i.values(): ....',float('inf')),
            'bl_sorteddict': (self.dict_iter,'for i in tree.values(): for ii in i.values(): ....',float('inf')),
            'SC.SortedDict': (self.dict_iter,'for i in tree.values(): for ii in i.values(): ....',float('inf')),
            'XML.Element': (self.et_iter,'for i in tree: for ii in i ....',float('inf')),
            'LXML.Element': (self.et_iter,'for i in tree: for ii in i ....',float('inf')),
            'PT.Node': (self.pt_iter, 'for i in tree.GetChildren(): for ii in i.GetChildren(): ....',float('inf')),
            'llDict': (self.lldict_iter, 'for i in tree.values(): for ii in i.values(): ....',float('inf')),
            'TL.Tree': (self.tl_iter, 'for i in tree.children("root"): .... ',float('inf')),
            'AT.Node': (self.at_iter, 'for i in tree.children: for ii in i.children: ....',float('inf')),
        }

    def it_iter(self,key):
        tree=self.trees[key]
        c=0
        for i in tree.deep:
            assert i is not None
            c+=1
        assert c==self.max_items*self.items_per_level

    # in depth iter helper we cannot use recursive solutions here!

    def _iter_dict(self,tree):
        iterators = [iter(tree.values())]
        while iterators:
            for item in iterators[-1]:
                yield item
                if item[-1]:
                    iterators.append(iter(item[-1].values()))
                    break
            else:  # for loop is finished and not broken
                del iterators[-1]

    def dict_iter(self,key):
        tree=self.trees[key]
        c=0
        for i in self._iter_dict(tree):
            assert i is not None
            c += 1
        assert c==self.max_items*self.items_per_level

    # in depth iter helper we cannot use recursive solutions here!

    def _iter_list(self,tree):
        iterators = [iter(tree)]
        while iterators:
            for item in iterators[-1]:
                yield item
                if item[-1]:
                    iterators.append(iter(item[-1]))
                    break
            else:  # for loop is finished and not broken
                del iterators[-1]

    def list_iter(self,key):
        tree=self.trees[key]
        c=0
        for i in self._iter_list(tree):
            assert i is not None
            c += 1
        assert c==self.max_items*self.items_per_level

    def _iter_lldict(self,tree):
        iterators = [iter(tree.values())]
        while iterators:
            for item in iterators[-1]:
                yield item
                if item:
                    iterators.append(iter(item.values()))
                    break
            else:  # for loop is finished and not broken
                del iterators[-1]

    def lldict_iter(self,key):
        tree=self.trees[key]
        c=0
        for i in self._iter_lldict(tree):
            assert i is not None
            c += 1
        assert c==self.max_items*self.items_per_level

    def _iter_et(self,tree):
        iterators = [iter(tree)]
        while iterators:
            for item in iterators[-1]:
                yield item
                if len(item):
                    iterators.append(iter(item))
                    break
            else:  # for loop is finished and not broken
                del iterators[-1]

    def et_iter(self,key):
        tree=self.trees[key]
        c=0
        for i in self._iter_et(tree):
            assert i is not None
            c += 1
        assert c==self.max_items*self.items_per_level

    def _iter_pt(self,tree):
        iterators = [tree.GetChildren()]
        while iterators:
            for item in iterators[-1]:
                yield item
                if item:
                    iterators.append(item.GetChildren())
                    break
            else:  # for loop is finished and not broken
                del iterators[-1]

    def pt_iter(self,key):
        tree=self.trees[key]
        c=0
        for i in self._iter_pt(tree):
            assert i is not None
            c += 1
        assert c==self.max_items*self.items_per_level


    def tl_iter(self,key):
        tree=self.trees[key]
        for i in tree.children('root'):
            assert i is not None

    def _iter_at(self,tree):
        iterators = [iter(tree.children)]
        while iterators:
            for item in iterators[-1]:
                yield item
                if item.children:
                    iterators.append(iter(item.children))
                    break
            else:  # for loop is finished and not broken
                del iterators[-1]

    def at_iter(self,key):
        tree=self.trees[key]
        c=0
        for i in self._iter_at(tree):
            assert i is not None
            c += 1
        assert c==self.max_items*self.items_per_level


    def test_exec(self,key,it_t1=None,it_t2=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2
        method,op_str,max_items=caller

        if key=='iTree':
            t = self.calc_timeit(caller[0],key)
            it_t1=t
            op_str=caller[1]
            self.print_time_meas_output(t,
                                        ['%s:'%obj_data['str'],
                                        op_str])
        else:
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

        return self.trees,self.trees2,it_t1,it_t2

