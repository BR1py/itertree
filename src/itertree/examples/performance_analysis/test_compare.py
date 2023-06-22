import pytest
import itertools

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestCompareL1(BasePerformance):

    def get_header(self):
        out = 'Compare two trees (same trees compared)'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out = out + '-> For many objects the simple compare via == delivers not a real deep compare related to the subelements\n'
        out = out + '   therefore a compare iterating over the subitems was added\n'

        return out

    def get_callers(self):
        return {
            'iTree':[(self.tree_compare,'tree==tree2',float('inf')),
                     (self.tree_compare_iter, 'any(i==i2 for i,i2 in zip(tree,tree2)', float('inf'))],
            'list':[(self.tree_compare,'tree==tree2',float('inf')),
                     (self.tree_compare_iter, 'any(i==i2 for i,i2 in zip(tree,tree2)', float('inf'))],
            'deque': [(self.tree_compare, 'tree==tree2', float('inf')),
                     (self.tree_compare_iter, 'any(i==i2 for i,i2 in zip(tree,tree2)', float('inf'))],
            'blist': [(self.tree_compare, 'tree==tree2', float('inf')),
                     (self.tree_compare_iter, 'any(i==i2 for i,i2 in zip(tree,tree2)', float('inf'))],
            'dict': [(self.tree_compare, 'tree==tree2', float('inf')),
                     (self.dict_compare_iter, 'any(i==i2 for i,i2 in zip(tree.items(),tree2.items())', float('inf'))],
            'odict': [(self.tree_compare, 'tree==tree2', float('inf')),
                     (self.dict_compare_iter, 'any(i==i2 for i,i2 in zip(tree.items(),tree2.items())', float('inf'))],
            'iodict': [(self.tree_compare, 'tree==tree2', float('inf')),
                     (self.dict_compare_iter, 'any(i==i2 for i,i2 in zip(tree.items(),tree2.items())', float('inf'))],
            'idict': [(self.tree_compare, 'tree==tree2', float('inf')),
                     (self.dict_compare_iter, 'any(i==i2 for i,i2 in zip(tree.items(),tree2.items())', float('inf'))],
            'bl_sorteddict': [(self.tree_compare, 'tree==tree2', float('inf')),
                       (self.dict_compare_iter, 'any(i==i2 for i,i2 in zip(tree.items(),tree2.items())', float('inf'))],
            'SC.SortedDict': [(self.tree_compare, 'tree==tree2', float('inf')),
                      (self.dict_compare_iter, 'any(i==i2 for i,i2 in zip(tree.items(),tree2.items())', float('inf'))],
            'XML.Element': [(self.et_compare_iter, 'elements_equal(tree,tree2) # special method', float('inf')),
                            (None,None,float('inf'))],
            'LXML.Element': [(self.et_compare_iter, 'elements_equal(tree,tree2) # special method', float('inf')),
                            (None,None,float('inf'))],
            #'PT.Node': [(self.pt_compare, 'tree==tree2', float('inf')),
            #            (self.pt_compare_iter, 'any(i==i2 for i,i2 in zip(tree,tree2)', float('inf'))],
            'llDict': [(self.tree_compare, 'tree==tree2', float('inf')),
                              (self.dict_compare_iter, 'any(i==i2 for i,i2 in zip(tree.items(),tree2.items())',
                               float('inf'))],
            'AT.Node': [(self.at_compare, 'dir(tree)==dir(tree2)', float('inf')),
                              (self.at_compare_iter, 'any(dir(i)==dir(i2) for i,i2 in zip(tree.items(),tree2.items())',
                               float('inf'))],
            'PT.Node': [(self.at_compare, 'dir(tree)==dir(tree2)', float('inf')),
                        (self.pt_compare_iter, 'any(dir(i)==dir(i2) for i,i2 in zip(tree.items(),tree2.items())',
                         float('inf'))],

            #'AT.Node': (self.at_get_by_idx, 'tree.children[idx]',float('inf')),
        }

    def tree_compare(self,key):
        tree=self.trees[key]
        tree2 = self.trees2[key]
        assert tree==tree2

    def pt_compare(self,key):
        tree=self.trees[key]
        tree2 = self.trees2[key]
        assert tree==tree2

    def tree_compare_iter(self,key):
        tree=self.trees[key]
        tree2 = self.trees2[key]
        assert any(i==i2 for i,i2 in zip(tree,tree2))

    def dict_compare_iter(self,key):
        tree=self.trees[key]
        tree2 = self.trees2[key]
        assert any(i==i2 for i,i2 in zip(tree.items(),tree2.items()))

    def at_compare(self,key):
        tree=self.trees[key]
        tree2 = self.trees2[key]
        assert dir(tree)==dir(tree2)

    def at_compare_iter(self,key):
        tree=self.trees[key]
        tree2 = self.trees2[key]
        assert any(dir(i)==dir(i2) for i,i2 in zip(tree.children,tree2.children))

    def pt_compare_iter(self,key):
        tree=self.trees[key]
        tree2 = self.trees2[key]
        assert any(dir(i)==dir(i2) for i,i2 in zip(tree.GetChildren(),tree2.GetChildren()))

    def et_compare_iter(self, key):
        e1=self.trees[key]
        e2=self.trees2[key]
        return self.elements_equal(e1,e2)


    def elements_equal(self,e1,e2):
        if e1.tag != e2.tag: return False
        if e1.text != e2.text: return False
        if e1.tail != e2.tail: return False
        if e1.attrib != e2.attrib: return False
        if len(e1) != len(e2): return False
        return all(self.elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

    def test_exec(self,key,it_t1=None,it_t2=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2
        else:
            method1, op_str1,max_items1 = caller[0]
            method2, op_str2,max_items2 = caller[1]

        if key=='iTree':
            t = self.calc_timeit(caller[0][0], key)
            it_t1=t
            self.print_time_meas_output(t,
                                        ['%s:'%obj_data['str'],
                                        '%s'%(op_str1)])
            t = self.calc_timeit(caller[1][0], key)
            it_t2=t
            self.print_time_meas_output(t,'%s'%(op_str2))
        else:
            if key in self.trees2:
                if max_items1 >= self.max_items:
                    t = self.calc_timeit(method1, key)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],op_str1],
                                                it_t1)
                else:
                    self.print_time_meas_output(None,
                                                ['%s:' % obj_data['str'],op_str1])
                if max_items2 >= self.max_items:
                    if method2:
                        t = self.calc_timeit(method2, key)
                        self.print_time_meas_output(t,op_str2,
                                                    it_t2)
                else:
                    self.print_time_meas_output(None,op_str2)
            else:
                print('No comparison data found for %s (execute copy() test-case before this test-case)'%obj_data['str'])
        return self.trees,self.trees2,it_t1,it_t2

    def test_exec2(self):
        print(self.get_header())

        callers=self.get_callers()
        for key,obj_data in self.objects.items():
            cl=obj_data['class']
            caller=callers.get(key)
            if caller is None:
                # no action for this object
                continue
            elif type(caller) is not list:
                method,op_str=caller
            if key=='iTree':
                t = self.calc_timeit(caller[0][0], key)
                it_t1=t
                op_str=caller[0][1]
                self.print_time_meas_output(t,
                                            ['%s (index-specific access):'%obj_data['str'],
                                            '%s'%(op_str)])
                t = self.calc_timeit(caller[1][0], key)
                it_t2=t
                op_str=caller[1][1]
                self.print_time_meas_output(t,
                                            ['%s (common target access):'%obj_data['str'],
                                            '%s'%(op_str)])


            else:
                t = self.calc_timeit(method, key)
                self.print_time_meas_output(t,
                                            ['%s:'%obj_data['str'],
                                            '%s'%(op_str)],
                                            [it_t1,it_t2])

        return self.trees,self.trees2
