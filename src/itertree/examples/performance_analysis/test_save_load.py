import os.path

import pytest
import itertools

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestSaveLoadL1(BasePerformance):

    def get_header(self):
        out = 'Save and load the tree structures'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        out=out+'\n-> for most objects we did not found an internal way to store them in a file'
        return out

    def get_callers(self):
        return {
            'iTree':[(self.it_save,'tree.dump(target_file1,pack=False)',float('inf')),
                     (self.it_load,'tree.load(target_file1)',float('inf')),
                     (self.it_save_pack, 'tree.dump(target_file1,pack=True)', float('inf')),
                     (self.it_load_pack, 'tree.load(target_file1)',float('inf')),
                     ],
            #'list':(self.list_get_by_idx,'tree[idx]',float('inf')),
            #'deque': (self.list_get_by_idx, 'tree[idx]',float('inf')),
            #'blist': (self.list_get_by_idx, 'tree[idx]',float('inf')),
            #'dict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',float('inf')),
            #'odict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',float('inf')),
            #'iodict': (self.idict_get_by_idx, 'tree.values()[idx]',float('inf')),
            #'idict': (self.idict_get_by_idx, 'tree.values()[idx]',float('inf')),
            #'bl_sorteddict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',5000),
            #'SC.SortedDict':(self.dict_get_by_idx, 'next(islice(tree.values(),idx))',float('inf')),
            'XML.Element': [(self.et_save,'fh.write(etree.tostring(tree))',float('inf')),
                            (self.et_load,'etree.parse(source_file))',float('inf'))],
            'LXML.Element': [(self.et_save,'fh.write(etree.tostring(tree))',float('inf')),
                            (self.et_load,'etree.parse(source_file))',float('inf'))],
            'llDict': [(self.lldict_save, 'fh.write(etree.tostring(tree))', float('inf')),
                             (self.lldict_load, 'etree.parse(source_file))', float('inf'))],

            #'PT.Node': (self.pt_node_get_by_idx, 'next(islice(tree.GetChildren(),idx))',float('inf')),
            #'llDict': (self.dict_get_by_idx, 'next(islice(tree.values(),idx))',50000),
            #'TL.Tree': (self.tl_get_by_idx, 'tree.children[idx]',50000),
            #'AT.Node': (self.at_get_by_idx, 'tree.children[idx]',float('inf')),
        }



    def it_save(self, key):
        tree = self.trees[key]
        file_path = os.path.join(self.tmp_folder, 'out.itr')
        if os.path.exists(file_path):
            os.remove(file_path)
        tree.dump(file_path, pack=False)
        assert os.path.exists(file_path)

    def it_load(self,key):
        tree=self.trees[key]
        file_path = os.path.join(self.tmp_folder, 'out.itr')
        new=tree.load(file_path)
        assert len(tree)==len(new)

    def it_save_pack(self, key):
        tree = self.trees[key]
        file_path = os.path.join(self.tmp_folder, 'out.itz')
        if os.path.exists(file_path):
            os.remove(file_path)
        tree.dump(file_path, pack=True)
        assert os.path.exists(file_path)

    def it_load_pack(self, key):
        tree = self.trees[key]
        file_path = os.path.join(self.tmp_folder, 'out.itz')
        new = tree.load(file_path)
        assert len(tree) == len(new)

    def et_save(self, key,module):
        tree = self.trees[key]
        data=module.tostring(tree)
        file_path = os.path.join(self.tmp_folder, 'out.xml')
        with open(file_path,'wb') as fh:
            fh.write(data)
        assert os.path.exists(file_path)

    def et_load(self, key,module):
        tree = self.trees[key]
        file_path = os.path.join(self.tmp_folder, 'out.xml')
        new=module.parse(file_path).getroot()
        assert len(tree) == len(new)


    def lldict_save(self, key,module):
        tree = self.trees[key]
        file_path = os.path.join(self.tmp_folder, 'out.lldict')
        if os.path.exists(file_path):
            os.remove(file_path)
        tree.dump(file_path)
        assert os.path.exists(file_path)

    def lldict_load(self,key,module):
        tree=self.trees[key]
        file_path = os.path.join(self.tmp_folder, 'out.lldict')
        new=tree.create_from_file(file_path)
        assert len(tree)==len(new)

    def test_exec(self,key,it_t1=None,it_t2=None,it_t3=None,it_t4=None):
        obj_data=self.objects[key]
        module=obj_data.get('module')
        caller = self.get_callers().get(key)
        if caller is None:
            # no action for this object
            return self.trees,self.trees2,it_t1,it_t2,it_t3,it_t4
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
                                        ['%s:'%obj_data['str'],
                                        op_str])
            t = self.calc_timeit(caller[1][0], key)
            it_t2=t
            op_str=caller[1][1]
            self.print_time_meas_output(t,
                                        op_str)
            t = self.calc_timeit(caller[2][0], key)
            it_t3 = t
            op_str=caller[0][1]
            self.print_time_meas_output(t,op_str)
            t = self.calc_timeit(caller[3][0], key)
            it_t4 = t
            op_str=caller[1][1]
            self.print_time_meas_output(t,op_str)

        else:
            if max_items1 >= self.max_items:
                t = self.calc_timeit(method1, key,obj_data['module'])
                self.print_time_meas_output(t,
                                            ['%s:'%obj_data['str'],
                                            '%s'%(op_str1)],
                                            [it_t1,it_t2])
            else:
                self.print_time_meas_output(None,
                                            ['%s:' % obj_data['str'],
                                             '%s' % (op_str1)])
            if max_items2 >= self.max_items:
                t = self.calc_timeit(method2, key,obj_data['module'])
                self.print_time_meas_output(t,
                                            '%s'%(op_str2),
                                            [it_t1,it_t2])
            else:
                self.print_time_meas_output(None,op_str2)

        return self.trees,self.trees2,it_t1,it_t2,it_t3,it_t4

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
