import pytest
import itertools
import pickle

from itertree.examples.performance_analysis.base_performance import BasePerformance
from itertree import iTLink,iTree


class TestiTreeSpecificL1(BasePerformance):


    def get_header(self):
        out = 'Here we test the perfomance of some iTree specific functions (most often not available in the other objects)'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        return out

    def get_callers(self):
        return {}

    #build
    def it_extend(self):
        tree=iTree('root',
                       subtree=[iTree('%i' % i) for i in range(self.max_items)])
        assert self.max_items == len(tree)

    def it_append(self):
        tree = iTree('root')
        # append itertree with items
        for i in range(self.max_items):
            tree.append(iTree('%i' % i,i))
        assert self.max_items == len(tree)
        self.trees['iTree']=tree

    def it_insert(self):
        tree = iTree('root')
        tree.append(iTree('-1',-1))
        for i in range(self.max_items):
            tree.insert(1,iTree('%i' % i))
        assert self.max_items == len(tree)-1

    def performance_it_load_links(self):
        # tag access
        tree=self.trees['iTree']
        cl=tree.__class__
        new = cl('new_root')
        # create link root:
        new.extend(tree)
        new.append(cl('link_root', link=iTLink(target_path=[0])))
        new.load_links()
        assert len(new)==len(tree)+1

    def it_get_idx_specific(self):
        tree=self.trees['iTree']
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

    def it_get_idx_common(self):
        tree=self.trees['iTree']
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



    def it_get_slice_specific(self):
        tree=self.trees['iTree']
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

    def it_get_slice_common(self):
        tree=self.trees['iTree']
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


    def it_get_key_specific(self):
        tree=self.trees['iTree']
        c=0
        last=None
        for i in range(self.max_items):
            item=tree.get.by_tag_idx(('%i' % i, 0))
            if item is not None:
                c+=1
            assert item is not last
            last=item

        assert self.max_items == c
        return c

    def it_get_by_key(self):
        tree=self.trees['iTree']
        c=0
        last=None
        for i in range(self.max_items):
            item=tree[('%i'%i,0)]
            if item is not None:
                c+=1
            assert item is not last
            last = item
        assert self.max_items == c
        return c

    def performance_it_get_tag_specific(self):
        # tag access
        tree=self.trees['iTree']
        # read itertree families per tag
        c = 0
        last=None
        for i in range(self.max_items):
            a = tree.get.by_tag('%i' % i)
            c += 1
            assert last!=a
            last=a
        assert c==len(tree)

    def performance_it_get_tag(self):
        # tag access
        tree=self.trees['iTree']
        # read itertree families per tag
        c = 0
        last=None
        for i in range(self.max_items):
            a = tree['%i' % i]
            c += 1
            assert last!=a
            last=a
        assert c==len(tree)

    def performance_it_get_tag_idx_slice(self):
        # tag access
        tree=self.trees['iTree']
        # read itertree families per tag
        c = 0
        for i in range(0, self.max_items - 1, self.slice_operation_factor):
            a = tree['1', slice(0, (i + 1))]
            c += 1
            assert a is not None


    def performance_it_get_tag_idx_slice_specific(self):
        tree=self.trees['iTree']
        # read itertree families per tag
        c = 0
        for i in range(0, self.max_items - 1, self.slice_operation_factor):
            a = tree.get.by_tag_idx(('1', slice(0, (i + 1))))
            c += 1
            assert a is not None

    def performance_it_dumps(self):
        tree=self.trees['iTree']
        a = tree.dumps()

    def performance_it_pickle(self):
        tree=self.trees['iTree']
        a = pickle.dumps(tree)


    def test_exec(self):
        t1 = self.calc_timeit(self.it_extend)
        self.print_time_meas_output(t1,
                                    ['tree=iTree("root",subtree=[...])'])
        t2 = self.calc_timeit(self.it_append)
        self.print_time_meas_output(t2,
                                    'tree=iTree(); tree.append()...',t1,post_text='{:.3f}x faster as extend()')
        try:
            import blist
            t = self.calc_timeit(self.it_insert)
            self.print_time_meas_output(t,
                                        'tree=iTree(); tree.insert()...',t2,post_text='{:.3f}x faster as append()')
        except:
            pass
        t = self.calc_timeit(self.performance_it_load_links)
        self.print_time_meas_output(t,
                                    'tree.load_links()            # %i linked-items loaded'%len(self.trees['iTree']))

        t3 = self.calc_timeit(self.it_get_idx_specific)
        self.print_time_meas_output(t3,
                                    'tree.get.by_idx(idx)         # specific absolute index access')
        t = self.calc_timeit(self.it_get_idx_common)
        self.print_time_meas_output(t,
                                    'tree[idx]                    # common absolute index access',
                                    t3,post_text='{:.3f}x faster as specific' )

        t1 = self.calc_timeit(self.it_get_slice_specific)
        self.print_time_meas_output(t1,
                                    'tree.get.by_idx_slice(slice) # specific absolute index slice access')
        t = self.calc_timeit(self.it_get_slice_common)
        self.print_time_meas_output(t,
                                    'tree[slice]                  # common absolute index slice access',
                                    t1,post_text='{:.3f}x faster as specific' )

        t2 = self.calc_timeit(self.it_get_key_specific)
        self.print_time_meas_output(t2,
                                    'tree.get.by_tag_idx(tag_idx) # specific tag-idx access',
                                    t3,post_text='{:.3f}x faster as get_by_idx()')
        t = self.calc_timeit(self.it_get_by_key)
        self.print_time_meas_output(t,
                                    'tree[tag_idx]                # common tag-idx access',
                                    t2,post_text='{:.3f}x faster as specific' )
        t1 = self.calc_timeit(self.performance_it_get_tag_idx_slice_specific)
        self.print_time_meas_output(t1,
                                    'tree.getitem_tag_idx_slice((tag,fam_idx_slice)) # specific tag_idx slice')
        t = self.calc_timeit(self.performance_it_get_tag_idx_slice)
        self.print_time_meas_output(t,
                                    'tree[(tag,fam_idx_slice]     # common tag_idx slice',
                                    t1,post_text='{:.3f}x faster as specific' )

        t1 = self.calc_timeit(self.performance_it_get_tag_specific)
        self.print_time_meas_output(t1,
                                    'tree.get.by_tag(tag)         # specific family-tag access')
        t = self.calc_timeit(self.performance_it_get_tag)
        self.print_time_meas_output(t,
                                    'tree[tag]                    # common family-tag access',
                                    t1, post_text = '{:.3f}x faster as specific' )

        t = self.calc_timeit(self.performance_it_dumps)
        self.print_time_meas_output(t,
                                    'tree.dumps()                 # serialize into string (json)')

        t = self.calc_timeit(self.performance_it_pickle)
        self.print_time_meas_output(t,
                                    'pickle.dumps(tree)           # serialize via pickle')


class TestiTreeSpecificLn(BasePerformance):


    def get_header(self):
        out = 'Here we test the perfomance of some iTree specific functions (most often not available in the other objects)'
        out='\n\n--- {} {:-^{width}}\n'.format(out, '', width=110 - len(out))
        return out

    def get_callers(self):
        return {}

    #build

    def it_append(self):
        tree = iTree('root')
        # append itertree with items
        level_tree=tree
        c=0
        for i in range(self.max_items):
            for ii in range(self.items_per_level):
                subtree=level_tree.append(iTree('%i_%i' % (i,ii),(i,ii)))
                if ii==1:
                    next_level_tree=subtree
                c+=1
            level_tree=next_level_tree

        assert self.max_items*self.items_per_level ==c
        self.trees['iTree']=tree


    def performance_it_load_links(self):
        # tag access
        tree=self.trees['iTree']
        cl=tree.__class__
        new = cl('new_root')
        # create link root:
        new.extend(tree)
        new.append(cl('link_root', link=iTLink(target_path=[1])))
        new.load_links()
        #assert len(new)==len(tree)+1

    def it_get_idx_specific(self):
        tree=self.trees['iTree']
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

    def it_get_idx_common(self):
        tree=self.trees['iTree']
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

    def it_get_key_specific(self):
        tree=self.trees['iTree']
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]=('%i_%i'%(i,ii),0)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree.get.by_tag_idx(*key_list)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def it_get_by_key(self):
        tree=self.trees['iTree']
        c=0
        last=None
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]=('%i_%i'%(i,ii),0)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree.get(*key_list)
                assert item is not last
                last=item
                if item is not None:
                    c+=1
            key_list=new_key_list
        assert self.max_items*self.items_per_level == c,'Accessed item number: %i expect %i'%(c,self.max_items*self.items_per_level)
        return c

    def performance_it_get_tag_specific(self):
        tree=self.trees['iTree']
        c=0
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree.get.by_tag(*key_list)
                if item is not None:
                    c+=1
            key_list=new_key_list

    def performance_it_get_tag(self):
        tree=self.trees['iTree']
        c=0
        key_list=[]
        for i in range(self.max_items):
            key_list.append(None)
            for ii in range(self.items_per_level):
                key_list[-1]='%i_%i'%(i,ii)
                if ii==1:
                    new_key_list=key_list.copy()
                item=tree.get(*key_list)
                if item is not None:
                    c+=1
            key_list=new_key_list

    def performance_it_get_tag_idx_slice(self):
        # tag access
        tree=self.trees['iTree']
        # read itertree families per tag
        c = 0
        for i in range(0, self.max_items - 1, self.slice_operation_factor):
            a = tree['1', slice(0, (i + 1))]
            c += 1
            assert a is not None


    def performance_it_get_tag_idx_slice_specific(self):
        tree=self.trees['iTree']
        # read itertree families per tag
        c = 0
        for i in range(0, self.max_items - 1, self.slice_operation_factor):
            a = tree.get.by_tag_idx(('1', slice(0, (i + 1))))
            c += 1
            assert a is not None

    def performance_it_dumps(self):
        tree=self.trees['iTree']
        a = tree.dumps()



    def test_exec(self):
        t2 = self.calc_timeit(self.it_append)
        self.print_time_meas_output(t2,
                                    'tree=iTree(); tree.append()...')
        t = self.calc_timeit(self.performance_it_load_links)
        self.print_time_meas_output(t,
                                    'tree.load_links()            # %i linked-items loaded'%len(self.trees['iTree']))

        t3 = self.calc_timeit(self.it_get_idx_specific)
        self.print_time_meas_output(t3,
                                    'tree.get.by_idx(idx)         # specific absolute index access')
        t = self.calc_timeit(self.it_get_idx_common)
        self.print_time_meas_output(t,
                                    'tree[idx]                    # common absolute index access',
                                    t3,post_text='{:.3f}x faster as specific' )


        t2 = self.calc_timeit(self.it_get_key_specific)
        self.print_time_meas_output(t2,
                                    'tree.get.by_tag_idx(tag_idx) # specific tag-idx access',
                                    t3,post_text='{:.3f}x faster as get_by_idx()')
        t = self.calc_timeit(self.it_get_by_key)
        self.print_time_meas_output(t,
                                    'tree[tag_idx]                # common tag-idx access',
                                    t2,post_text='{:.3f}x faster as specific' )

        t1 = self.calc_timeit(self.performance_it_get_tag_specific)
        self.print_time_meas_output(t1,
                                    'tree.get.by_tag(tag)         # specific family-tag access')
        t = self.calc_timeit(self.performance_it_get_tag)
        self.print_time_meas_output(t,
                                    'tree[tag]                    # common family-tag access',
                                    t1, post_text = '{:.3f}x faster as specific' )

        t = self.calc_timeit(self.performance_it_dumps)
        self.print_time_meas_output(t,
                                    'tree.dumps()                 # serialize into string (json)')



