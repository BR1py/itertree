import pytest

from itertree.examples.performance_analysis.base_performance import BasePerformance

class TestBuildByAppendL1(BasePerformance):

    def get_header(self):
        out = 'Build tree via append operation'
        return '\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))

    def get_callers(self):
        return {
            'iTree':(self.it_append,''),
            'list':(self.list_append,'tree.append((key,value,%s())'),
            'deque': (self.list_append, 'tree.append((key,value,%s())'),
            'blist': (self.list_append, 'tree.append((key,value,%s())'),
            'dict': (self.dict_append, 'tree[key]=(value,%s())'),
            'odict': (self.dict_append, 'tree[key]=(value,%s())'),
            'iodict': (self.dict_append, 'tree[key]=(value,%s())'),
            'idict': (self.dict_append, 'tree[key]=(value,%s())'),
            'bl_sorteddict': (self.dict_append, 'tree[key]=(value,%s())'),
            'SC.SortedDict': (self.dict_append, 'tree[key]=(value,%s())'),
            'XML.Element': (self.et_append, 'tree.append(%s(key,{"value":key}))'),
            'LXML.Element': (self.et_append, 'tree.append(%s(key,{"value":key}))'),
            'PT.Node': (self.pt_node_append, 'tree.AddChild(%s(key,value))'),
            'llDict': (self.lldict_append, 'tree[key] = %s(data=value)'),
            'TL.Tree': (self.tl_append, '%s.create_node(key,key, parent="root",value=value)'),
            'AT.Node': (self.at_append, '%s(key, parent=tree,value=value)',5000),
        }

    def it_append(self,key,obj_class):
        tree = obj_class('root')
        # append itertree with items
        for i in range(self.max_items):
            tree.append(obj_class('%i' % i,i))
        self.trees[key] = tree
        assert self.max_items == len(tree)

    def list_append(self,key,obj_class):
        tree = obj_class()
        for i in range(self.max_items):
            tree.append(('%i' % i, i, obj_class()))
        self.trees[key] = tree
        assert self.max_items == len(tree)

    def dict_append(self,key,obj_class):
        tree = obj_class()
        for i in range(self.max_items):
            tree['%i' % i] = (i, {})
        self.trees[key] = tree
        assert self.max_items == len(tree)

    def et_append(self,key,obj_class):
        tree = obj_class('root')
        for i in range(self.max_items):
            tree.append(obj_class('T%i' % i, {'value': '%i' % i}))  # only strings supported for save to file
        self.trees[key] = tree
        assert self.max_items == len(tree)

    def pt_node_append(self,key,obj_class):
        tree = obj_class()
        for i in range(self.max_items):
            tree.AddChild(obj_class('%i' % i, i))
        self.trees[key] = tree
        assert self.max_items == len(list(tree.GetChildren()))

    def lldict_append(self,key,obj_class):
        tree = obj_class()
        for i in range(self.max_items):
            tree['%i' % i] = obj_class(data=i)
        self.trees[key] = tree
        assert self.max_items == len(tree)

    def tl_append(self,key,obj_class):
        tree = obj_class()
        tree.create_node('root','root')
        for i in range(self.max_items):
            k='%i' % i
            tree.create_node(k,k,parent = 'root',data=i)
        assert self.max_items == len(tree)-1
        self.trees[key] = tree

    def at_append(self,key,obj_class):
        tree = obj_class('root')
        for i in range(self.max_items):
            obj_class('%i' % i, parent=tree,value=i)
        self.trees[key] = tree
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
                if len(caller) == 3:
                    method, op_str,max_items = caller
                else:
                    method, op_str = caller
                    max_items=float('inf')
            if key=='iTree':
                t = self.calc_timeit(method, key, cl)

                it_append=t
                self.print_time_meas_output(it_append, ['%s:'%obj_data['str'],
                                                        'tree=iTree(); tree.append(iTree(tag,value))'])
            else:
                if max_items>=self.max_items:
                    t = self.calc_timeit(method, key, cl)

                    init=obj_data.get('init', key)
                    op_str=op_str%init
                    self.print_time_meas_output(t,
                                                ['%s:'%obj_data['str'],
                                                'tree=%s(); %s'%(init,op_str)],
                                                it_append)
                else:
                    self.print_time_meas_output(None,
                                                [obj_data['str'],
                                                'tree=%s(); %s'%(init,op_str)])

        return self.trees,self.trees2

class TestBuildByAppendLn(BasePerformance):

    def get_header(self):
        out = 'Build tree via append operation'
        return '\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))

    def get_callers(self):
        return {
            'iTree':(self.it_append,''),
            'list':(self.list_append,'tree.append((key,value,%s())'),
            'deque': (self.list_append, 'tree.append((key,value,%s())'),
            'blist': (self.list_append, 'tree.append((key,value,%s())'),
            'dict': (self.dict_append, 'tree[key]=(value,%s())'),
            'odict': (self.dict_append, 'tree[key]=(value,%s())'),
            'iodict': (self.dict_append, 'tree[key]=(value,%s())'),
            'idict': (self.dict_append, 'tree[key]=(value,%s())'),
            'bl_sorteddict': (self.dict_append, 'tree[key]=(value,%s())'),
            'SC.SortedDict': (self.dict_append, 'tree[key]=(value,%s())'),
            'XML.Element': (self.et_append, 'tree.append(%s(key,{"value":key}))'),
            'LXML.Element': (self.et_append, 'tree.append(%s(key,{"value":key}))'),
            'PT.Node': (self.pt_node_append, 'tree.AddChild(%s(key,value))'),
            'llDict': (self.lldict_append, 'tree[key] = %s(data=value)'),
            'TL.Tree': (self.tl_append, '%s.create_node(key,key, parent="root",value=value)'),
            'AT.Node': (self.at_append, '%s(key, parent=tree,value=value)'),
        }

    def it_append(self,key,obj_class):
        tree = obj_class('root')
        # append itertree with items
        level_tree=tree
        c=0
        for i in range(self.max_items):
            for ii in range(self.items_per_level):
                subtree=level_tree.append(obj_class('%i_%i' % (i,ii),(i,ii)))
                if ii==1:
                    next_level_tree=subtree
                c+=1
            level_tree=next_level_tree
        self.trees[key] = tree
        assert self.max_items*self.items_per_level ==c

    def list_append(self,key,obj_class):
        tree = obj_class()
        level_tree=tree
        c=0
        for i in range(self.max_items):
            for ii in range(self.items_per_level):
                subsubtree=obj_class()
                level_tree.append(('%i_%i' % (i,ii),(i,ii),subsubtree))
                if ii==1:
                    next_level_tree=subsubtree
                c+=1
            level_tree=next_level_tree
        self.trees[key] = tree
        assert self.max_items*self.items_per_level ==c

    def dict_append(self,key,obj_class):
        tree = obj_class()
        level_tree=tree
        c=0
        for i in range(self.max_items):
            for ii in range(self.items_per_level):
                subsubtree=obj_class()
                level_tree['%i_%i' % (i,ii)]=((i,ii),subsubtree)
                if ii==1:
                    next_level_tree=subsubtree
                c+=1
            level_tree=next_level_tree
        self.trees[key] = tree
        assert self.max_items*self.items_per_level ==c

    def et_append(self,key,obj_class):
        tree = obj_class('root')
        level_tree=tree
        c=0
        for i in range(self.max_items):
            for ii in range(self.items_per_level):
                subsubtree=obj_class('T%i_%i' % (i,ii), {'value': '%i_%i' % (i,ii)})
                level_tree.append(subsubtree)
                if ii==1:
                    next_level_tree=subsubtree
                c+=1
            level_tree=next_level_tree
        self.trees[key] = tree
        assert self.max_items*self.items_per_level ==c

    def pt_node_append(self,key,obj_class):
        tree = obj_class('root')
        level_tree=tree
        c=0
        for i in range(self.max_items):
            for ii in range(self.items_per_level):
                subsubtree=obj_class('%i_%i' % (i,ii), (i,ii))
                level_tree.AddChild(subsubtree)
                if ii==1:
                    next_level_tree=subsubtree
                c+=1
            level_tree=next_level_tree
        self.trees[key] = tree
        assert self.max_items*self.items_per_level ==c

    def lldict_append(self,key,obj_class):
        tree = obj_class()
        level_tree=tree
        c=0
        for i in range(self.max_items):
            for ii in range(self.items_per_level):
                subsubtree=obj_class(data= (i,ii))
                level_tree['%i_%i' % (i,ii)]=subsubtree
                if ii==1:
                    next_level_tree=subsubtree
                c+=1
            level_tree=next_level_tree
        self.trees[key] = tree
        assert self.max_items*self.items_per_level ==c

    def tl_append(self,key,obj_class):
        tree = obj_class()
        tree.create_node('root','root')
        level_tree_key='root'
        c=0
        key_list=['root']
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]=  '%i_%i' % (i,ii)
                k='/'.join(key_list)
                tree.create_node(k, k, parent=level_tree_key, data=(i,ii))
                if ii==1:
                    next_level_key_list=key_list.copy()
                c+=1
            key_list=next_level_key_list
        self.trees[key] = tree
        assert self.max_items*self.items_per_level ==c

    def at_append(self,key,obj_class):
        tree = obj_class('root')
        level_tree=tree
        c=0
        for i in range(self.max_items):
            for ii in range(self.items_per_level):
                subsubtree=obj_class('%i_%i' % (i,ii),parent=level_tree,value=(i,ii))
                if ii==1:
                    next_level_tree=subsubtree
                c+=1
            level_tree=next_level_tree
        self.trees[key] = tree
        assert self.max_items*self.items_per_level ==c

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
                if len(caller) == 3:
                    max_items =caller[-1]
                else:
                    max_items=float('inf')

            t=self.calc_timeit(method,key,cl)
            if key=='iTree':
                it_append=t
                self.print_time_meas_output(it_append, ['%s:'%obj_data['str'],
                                                        'tree=iTree(); tree.append(iTree(tag,value))'])
            else:
                if max_items>=self.max_items:
                    init = obj_data.get('init', key)
                    op_str = op_str % init
                    self.print_time_meas_output(t,
                                                    ['%s:'%obj_data['str'],
                                                    'tree=%s(); %s'%(init,op_str)],
                                                    it_append)
                else:
                    self.print_time_meas_output(None,
                                                    ['%s:'%obj_data['str'],
                                                    'tree=%s(); %s'%(init,op_str)])

        return self.trees,self.trees2
