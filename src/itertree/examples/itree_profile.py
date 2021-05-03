import cProfile
from itertree import *
import itertree

max_items = 100000
root=None
print('Running on itertree version:',itertree.__version__)

def performance_dt():
    global root,max_items
    it = iTree('root')
    #insert
    for i in range(max_items):
        it.insert(1,iTree('%i' % i))
    #append datatree with items
    for i in range(max_items):
        it += iTree('%i' % i)
    it=iTree('root',subtree=[iTree('%i' % i) for i in range(max_items)])
    #read datatree items per tag and index
    for i in range(max_items):
        a = it['%i' % i]
        b = it[i]
    for i in range(max_items):
        del it[0]
    new_it=it*max_items
    it.extend(new_it)
    if False:
        for i in range(max_items):
            for ii in range(10):
                it[i].append(iTree(str(ii)))
        it.count_all()
    root=it

cProfile.run('performance_dt()')


