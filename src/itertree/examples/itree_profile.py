import cProfile
from itertree import *

max_items = 100000
root=None

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
    root=it

cProfile.run('performance_dt()')


