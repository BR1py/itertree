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

Test insert() item performance.
"""

import pytest
import collections
from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestBuildByInsertL1(BasePerformance):

    def get_header(self):
        out = 'Build tree via insert operation'
        return '\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))

    def get_callers(self):
        try:
            import blist
            it_max=float('inf')
        except:
            it_max=5000
        return {
            'iTree':(self.it_build, 'tree=iTree(); tree.insert(1,iTree(key,value)',it_max),
            'list':(self.list_build, 'tree=%s(); tree.insert(1,(key,value,%s())',float('inf')),
            'deque': (self.list_build, 'tree=%s(); tree.insert(1,(key,value,%s())',float('inf')),
            'blist': (self.list_build, 'tree=%s(); tree.insert(1,(key,value,%s())',float('inf')),
            'dict': (self.dict_build, 'tree=%s();for .... tree2=%s();tree2.update(tree);tree=tree2',float('inf')),
            'odict': (self.dict_build, 'tree=%s();for .... tree2=%s();tree2.update(tree);tree=tree2', 50000),
            'iodict': (self.dict_build, 'tree=%s();for .... tree2=%s, ....', 5000),
            'idict': (self.dict_build, 'tree=%s();for .... tree2=%s();tree2.update(tree);tree=tree2', 5000),
            'XML.Element': (self.et_build, 'tree=%s(); tree.insert(1,(key,value,%s())', 50000),
            'LXML.Element': (self.et_build, 'tree=%s(); tree.insert(1,(key,value,%s())', 5000),
            #following classes have no counterpart (?)
            #'PT.Node': (self.pt_node_build, 'tree=%s(children=[%s(key,value) for ...])',float('inf')),
            #'llDict': (self.lldict_build, 'tree=%s(OrderedDict((key,%s(data=value)) for ....))',float('inf'))
            #'AT.Node': (self.at_build, 'tree=%s(children=[%s(key,value) for ...])',float('inf')),
        }

    def it_build(self, key, obj_class):
        tree = obj_class('root')
        tree.append(obj_class('-1',-1))
        for i in range(self.max_items):
            tree.insert(1,obj_class('%i' % i))
        assert self.max_items == len(tree)-1

    def list_build(self, key, obj_class):
        tree = obj_class()
        tree.append(('-1', -1, obj_class()))
        for i in range(self.max_items):
            tree.insert(1,('%i' % i, i, obj_class()))
        assert self.max_items == len(tree)-1

    def dict_build(self, key, obj_class):
        tree = obj_class()
        for i in range(self.max_items):
            tree2 = obj_class()
            tree2['%i' % i] = (i, obj_class())
            tree2.update(tree)
            tree = tree2
        assert self.max_items == len(tree)


    def et_build(self, key, obj_class):
        tree = obj_class('root')
        tree.append(obj_class('T-1',{'value':'-1'}))
        for i in range(self.max_items):
            tree.insert(1,obj_class('T%i' % i,{'value':'%i'%i})) # only strings supported for save to file
        assert self.max_items == len(tree)-1


    def pt_node_build(self, key, obj_class):
        tree = obj_class('root',children=[obj_class('%i' % i, i) for i in range(self.max_items)])
        assert self.max_items == len(tree)
        self.trees2[key]=tree

    def lldict_build(self, key, obj_class):
        tree = obj_class()
        for i in range(self.max_items):
            tree2 = obj_class()
            tree2['%i' % i] = obj_class(i)
            tree2.update(tree)
            tree = tree2
        assert self.max_items == len(tree)

    def at_build(self, key, obj_class):
        tree = obj_class('root',children=[obj_class('%i' % i,value= i) for i in range(self.max_items)])
        assert self.max_items == len(tree.children)
        self.trees2[key]=tree

    def test_exec(self):
        print(self.get_header())

        callers=self.get_callers()
        for key,obj_data in self.objects.items():
            cl=obj_data['class']
            caller=callers.get(key)
            if caller is None:
                # no action for this object
                continue
            else:
                method,op_str, max_items=caller
            if max_items<self.max_items:
                if key == 'iTree':
                    self.print_time_meas_output(None, ['%s (execution time set to inf):' % obj_data['str'],
                                                            op_str])
                    it_insert = float('inf')
                else:
                    init = obj_data.get('init', key)
                    op_str = op_str % (init, init)
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],
                                                 op_str])
                continue
            t=self.calc_timeit(method,key,cl)
            if key=='iTree':
                it_insert=t
                self.print_time_meas_output(it_insert, ['%s:'%obj_data['str'],
                                                        op_str])
            else:
                init=obj_data.get('init', key)
                op_str=op_str%(init,init)
                self.print_time_meas_output(t,
                                            ['%s:'%obj_data['str'],
                                            op_str],
                                            it_insert)

        return self.trees,self.trees2
