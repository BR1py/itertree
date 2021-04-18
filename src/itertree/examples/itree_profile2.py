"""
profile a nested structure
"""
import cProfile
from itertree import *

max_items = 1000
root=None

def performance_dt():
    global root,max_items
    it = iTree('root')
    #append datatree with items
    for i in range(max_items):
        it += iTree('%i' % i,subtree=[iTree('%i' % ii) for ii in range(max_items)])
    #read datatree items per tag and index
    for i in range(max_items):
        a = it.find('%i' % i)
        b = it[i]
        for ii in range(max_items):
            a2 = a['%i' % ii] # get tag delivers an iterator (even if we have just one item!)
            b2 = b[ii]

    for i in range(max_items):
        for ii in range(max_items):
            del it[i][0]
    root=it

cProfile.run('performance_dt()')


