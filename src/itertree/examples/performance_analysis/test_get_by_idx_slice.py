import pytest
import itertools

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestGetByIdxSliceL1(BasePerformance):

    def get_header(self):
        out = 'Get tree-item via absolute index-slice (position) access'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out=out+'-> dict-like objects index access is realized via itertools.islice(tree,idx)\n'
        return out

    def get_callers(self):
        return {
            'iTree':[(self.it_get_idx_specific,'tree.get.by_idx_slice(slice)',float('inf')),
                     (self.list_get_by_idx,'tree[slice]',float('inf'))],
            'list':(self.list_get_by_idx,'tree[slice]',float('inf')),
            'deque': (self.deque_get_by_idx, 'tree[slice]',float('inf')),
            'blist': (self.list_get_by_idx, 'tree[slice]',float('inf')),
            'dict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',float('inf')),
            'odict': (self.dict_get_by_idx, 'list(islice(tree.values(),slice))',float('inf')),
            'iodict': (self.dict_get_by_idx, 'list(islice(tree.values(),slice))',50000),
            'idict': (self.dict_get_by_idx, 'list(islice(tree.values(),slice))',50000),
            'bl_sorteddict': (self.dict_get_by_idx, 'list(islice(tree.values(),slice))',5000),
            'SC.SortedDict':(self.dict_get_by_idx, 'list(islice(tree.values(),slice))',50000),
            'XML.Element': (self.list_get_by_idx, 'tree[slice]',float('inf')),
            'LXML.Element': (self.list_get_by_idx, 'tree[slice]',float('inf')),
            'PT.Node': (self.pt_node_get_by_idx, 'list(islice(tree.GetChildren(),slice))',float('inf')),
            'llDict': (self.dict_get_by_idx, 'list(islice(tree.values(),slice))',5000),
            'TL.Tree': (self.tl_get_by_idx, 'tree.children("root")[slice]',5000),
            'AT.Node': (self.at_get_by_idx, 'tree.children[slice]',float('inf')),
        }

    def it_get_idx_specific(self,key):
        tree=self.trees[key]
        c=0
        last=[]
        for i in range(0, (self.max_items - 1),self.slice_operation_factor):
            item=tree.get.by_idx_slice(slice(0, (i + 1)))
            if item is not None:
                c+=1
            assert len(item) > len(last)
            last=item
        nr=self.max_items/self.slice_operation_factor
        assert nr in [c+1, c]
        return c

    def list_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=[]
        for i in range(0,(self.max_items-1),self.slice_operation_factor):
            item=tree[slice(0,(i+1))]
            if item is not None:
                c+=1
            assert len(item) > len(last)
            last = item

        nr=self.max_items/self.slice_operation_factor
        assert nr in [c+1, c]
        return c

    def deque_get_by_idx(self,key):
        islice=itertools.islice # make local
        tree=self.trees[key]
        c=0
        last=[]
        for i in range(0,(self.max_items-1),self.slice_operation_factor):
            item=list(islice(tree,0,(i+1)))
            if item is not None:
                c+=1
            assert len(item) > len(last)
            last = item

        nr=self.max_items/self.slice_operation_factor
        assert nr in [c+1, c]
        return c

    def dict_get_by_idx(self,key):
        islice=itertools.islice # make local
        tree=self.trees[key]
        c=0
        last=[]
        for i in range(0,(self.max_items-1),self.slice_operation_factor):
            #item = list(tree.values())[i]
            item=list(islice(tree.values(),0,(i+1))) # this solution is quicker
            if item is not None:
                c+=1
            assert len(item)>len(last)
            last=item
        nr=self.max_items/self.slice_operation_factor
        assert nr in [c+1, c]
        return c


    def pt_node_get_by_idx(self,key):
        islice=itertools.islice # make local
        tree=self.trees[key]
        c=0
        last=[]
        for i in range(0,(self.max_items-1),self.slice_operation_factor):
            item=list(islice(tree.GetChildren(),0,(i+1)))
            if item is not None:
                c+=1
            assert len(item) > len(last)
            last=item

        nr=self.max_items/self.slice_operation_factor
        assert nr in [c+1, c]
        return c

    def tl_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=[]
        for i in range(self.max_items):
            item=tree.children('root')[slice(0,(i+1))]
            if item is not None:
                c+=1
            assert len(item) > len(last)
            last = item
        nr = self.max_items / self.slice_operation_factor
        assert nr in [c + 1, c]
        return c

    def at_get_by_idx(self,key):
        tree=self.trees[key]
        c=0
        last=[]
        for i in range(0,(self.max_items-1),self.slice_operation_factor):
            item=tree.children[slice(0,(i+1))]
            if item is not None:
                c+=1
            assert len(item) > len(last)
            last = item
        nr=self.max_items/self.slice_operation_factor
        assert nr in [c+1, c]
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
