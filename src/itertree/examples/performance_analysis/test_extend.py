import pytest
import collections
from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestBuildByExtendL1(BasePerformance):

    def get_header(self):
        out = 'Build tree via extend/comprehension operation'
        return '\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))

    def get_callers(self):
        return {
            'iTree':(self.it_build, 'tree=iTree(key,subtree=(iTree(key,value) for ....))'),
            'list':(self.list_build, 'tree=%s((key,value,%s()) for ....))'),
            'deque': (self.list_build, 'tree=%s((key,value,%s()) for ....))'),
            'blist': (self.list_build, 'tree=%s((key,value,%s()) for ....))'),
            'dict': (self.dict_build, 'tree=%s((key,(value,%s())) for ....))'),
            'odict': (self.dict_build, 'tree=%s((key,(value,%s())) for ....))'),
            'iodict': (self.dict_build, 'tree=%s((key,(value,%s())) for ....))'),
            'idict': (self.dict_build, 'tree=%s((key,(value,%s())) for ....))'),
            'bl_sorteddict': (self.dict_build, 'tree=%s((key,(value,%s())) for ....))'),
            'SC.SortedDict': (self.dict_build, 'tree=%s((key,(value,%s())) for ....))'),
            'XML.Element': (self.et_build, 'tree.extend(%s(key,{"value":key}))'),
            'LXML.Element': (self.et_build, 'tree.extend(%s(key,{"value":key}))'),
            'PT.Node': (self.pt_node_build, 'tree=%s(children=[%s(key,value) for ...])'),
            #'llDict': (self.lldict_build, 'tree=%s(OrderedDict((key,%s(data=value)) for ....))'), #has no extend!
            'AT.Node': (self.at_build, 'tree=%s(children=[%s(key,value) for ...])',5000),
        }

    def it_build(self, key, obj_class):
        tree=obj_class('root',
                       subtree=list(obj_class('%i' % i) for i in range(self.max_items)))
        assert self.max_items == len(tree)

    def list_build(self, key, obj_class):
        tree = obj_class((('%i' % i, i, obj_class()) for i in range(self.max_items)))
        assert self.max_items == len(tree)

    def dict_build(self, key, obj_class):
        tree = obj_class((('%i' % i,(i, obj_class())) for i in range(self.max_items)))
        assert self.max_items == len(tree)

    def et_build(self, key, obj_class):
        tree = obj_class('root')
        tree.extend(obj_class('T%i'%i,{'value': '%i' % i}) for i in range(self.max_items))
        assert self.max_items == len(tree)

    def pt_node_build(self, key, obj_class):
        tree = obj_class('root',children=[obj_class('%i' % i, i) for i in range(self.max_items)])
        assert self.max_items == len(tree)

    def lldict_build(self, key, obj_class):
        od=collections.OrderedDict
        tree = obj_class(od(('%i' % i,obj_class(data=i)) for i in range(self.max_items)))
        assert self.max_items == len(tree)

    def at_build(self, key, obj_class):
        tree = obj_class('root',children=[obj_class('%i' % i,value= i) for i in range(self.max_items)])
        assert self.max_items == len(tree.children)

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
                method,op_str=caller[0],caller[1]
                if len(caller)==3:
                    max_items=caller[2]
                else:
                    max_items=float('inf')

            if key=='iTree':
                t = self.calc_timeit(method, key, cl)
                it_extend=t
                self.print_time_meas_output(it_extend, ['%s:'%obj_data['str'],
                                                        op_str])
            elif key in {'XML.Element','LXML.Element'}:
                t = self.calc_timeit(method, key, cl)
                init = obj_data.get('init', key)
                op_str = op_str % (init)
                self.print_time_meas_output(t,
                                            ['%s:' % obj_data['str'],
                                             op_str],
                                            it_extend)
            else:
                if max_items>=self.max_items:
                    t = self.calc_timeit(method, key, cl)
                    init=obj_data.get('init', key)
                    op_str=op_str%(init,init)
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                op_str],
                                                it_extend)
                else:
                    self.print_time_meas_output(None,
                                                ['%s:'%obj_data['str'],
                                                op_str],
                                                )


        return self.trees,self.trees2
