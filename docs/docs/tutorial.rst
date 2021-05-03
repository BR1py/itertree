.. _tutorial:

Tutorial
========

************************************
Status and compatibility information
************************************


The original implementation is done in python 3.5 and it is tested under python 3.5 and 3.9. It should work in all python 3 environments.

The actual development status is Beta. The planned featureset is implemented. Work effort goes in the moment in testing, bugfixing and the creation of the documentation.

***************************
Using the itertree package
***************************

To understand the full functionality of itertree the user should have a look on the related examples which can be found in the example folder of itertree.

In this chapter we try to dive in the functions of itertree in a clear structured way. The user might look in the class description of the modules too. But the huge number of methods in the iTree class might be very confusing. And we hope this chapter orders the things in a much better way.

***************************
Construction of an itertree
***************************


The first step in the construction of a itertree is to instance the :ref:`itertree iTree class`.


.. autoclass:: itertree.iTree
    :members: __init__

Instance the iTree object:
::
   >>>item1=iTree('item1') # itertree item with the tag 'item1'
   >>>item2=iTree('item2', data={'mykey':1}) # instance a iTree-object with data content (defined as a dict)
   >>>item3=iTree('temp_item', is_temp=True) # instance a temporary iTree-object 
   >>>item4=iTree('link_item', data={'mykey':2}, is_temp=True, link=DiTLink(dt.dtz',iTreeTagIdx(child',0)) # instance a iTree-object containing a link
   

iTree objects can be marked as temporary. One can filter for this property and in the dump into a file temporary iTrees will be ignored.

In case a link is set the iTree object will integrate the childs of the linked iTree-objects as it's own childs into the tree. The iTree object can have own properties like temporary or own data. But it cannot contain own children. Operations that try to manipulate the children structure will fail in this case.


To add or manipulate the children of an item we have several possibilities. The following direct operations are recommended for structural manipulations in the tree:
::
   >>>root=iTree('root')
   >>>root+=iTree('child') # append a child
   >>>root[0]=iTree('newchild') # replace the child with index 0
   >>>del root[iTreeTagIdx('newchild',0)] # deletes the child with matching iTreeTagIdx
    

Additionally a huge set of methods is available for structural manipulations related to the children of a item.

.. autofunction:: itertree.iTree.append

.. autofunction:: itertree.iTree.appendleft

.. autofunction:: itertree.itree_main.iTree.extend

.. autofunction:: itertree.itree_main.iTree.extendleft

.. autofunction:: itertree.itree_main.iTree.insert

.. autofunction:: itertree.itree_main.iTree.move

.. autofunction:: itertree.itree_main.iTree.rename

.. autofunction:: itertree.itree_main.iTree.pop

.. autofunction:: itertree.itree_main.iTree.popleft

.. autofunction:: itertree.iTree.clear

The addition of iTrees is possible the result contains always the properties of the first added item and the children of the second added item are appended by creating a copy. 
::
    >>> a=iTree('a',data={'mykey':1},subtree=[iTree('a1'),iTree('a2')])
    >>> b=iTree('b',subtree=[iTree('b1'),iTree('b2')])
    >>> c=a+b
    >>> c
    iTree("'a'", data="{'mykey': 1}", subtree=[iTree("'a1'"), iTree("'a2'"), iTree("'b1'"), iTree("'b2'")])

Multiplication of a iTree is possible too the result is a list of iTree copies of the original one.
::
    itree_list=iTree('a')*1000 # creates a list of 1000 copies of the original iTree
    >>> root=iTree('root')
    >>> root.extend(itree_list) # we can extend an existing iTree with the list (add 1000 identical children)
    True


***************************
item access
***************************

The items in the iTree can be accessed via __getitem__() method:

.. autofunction:: itertree.iTree.__getitem__()

    >>> root=iTree('root')
    >>> root+=iTree('child',data=0)
    >>> root+=iTree('child',data=1)
    >>> root+=iTree('child',data=2)
    >>> root+=iTree('child',data=3)
    >>> root+=iTree('child',data=4)
    >>> root[1] # index access
    iTree("'child'", data=1)
    >>> root[TagIdx('child',1)] # TagIdx access (index targets the index in the tag family!)
    iTree("'child'", data=1)
    >>> root[TagIdx('child',-1)] # TagIdx access with negative index
    iTree("'child'", data=4)
    >>> root[TagIdx('child',[0,2])] # TagIdx give index list -> result is an iterator!
    <list_iterator object at 0x0000029E12F69B00>
    >>> list(root[TagIdx('child',[0,2])]) # make ietartor content visible by casting into a list
    [iTree("'child'", data=0), iTree("'child'", data=2)]
    >>> list(root[[0,2]]) # index list access (absolute indexes)
    [iTree("'child'", data=0), iTree("'child'", data=2)]
    >>> list(root[1:3]) # slices are allowed too
    [iTree("'child'", data=1), iTree("'child'", data=2)]
    
The TagIdx class is used to address items that contains the same tag. The second argument of the TagIdx is the index that the item has in the related tag-family. But we can also give multiple indexes or a slice. As the given example shows is the result of not unique targets always an iterator object. 

.. autofunction:: itertree.iTree.get_deep()

.. autofunction:: itertree.iTree.find()

***************************
iTree other structure related commands
***************************

.. autofunction:: itertree.iTree.__setitem__()

.. autofunction:: itertree.iTree.__delitem__()

.. autofunction:: itertree.iTree.clear()

.. autofunction:: itertree.iTree.copy()

.. autofunction:: itertree.iTree.reverse()

.. autofunction:: itertree.iTree.rotate()


***************************
iTree compare items
***************************

.. autofunction:: itertree.iTree.__eq__()

.. autofunction:: itertree.iTree.__neq__()

.. autofunction:: itertree.iTree.equal()


Because the __eq__() method (== opertor) is internally used for same item object findings we really compare here based on the python object id. Therefore for the comparison of two non identical objects the equal() method should be used.

.. autofunction:: itertree.iTree.__contains__()

.. autofunction:: itertree.iTree.__hash__()

.. autofunction:: itertree.iTree.__len__()

Based on the iTree length the comparison operators <; <=; >; >= are available too.

.. autofunction:: itertree.iTree.count()

***************************
iTree properties
***************************

As we will see later on some properties of the iTree object can be modified by teh related methods. 
Warning:: The user should NEVER modify any of the given properties directly. Especially the not discussed private properties (marked with the beginning underline). Direct modifications will normally lead into inconsistencies of the iTree object!

The iTree object contains the following general properties:

.. autofunction:: itertree.iTree.root

.. autofunction:: itertree.iTree.is_root

.. autofunction:: itertree.iTree.parent

.. autofunction:: itertree.iTree.pre_item

.. autofunction:: itertree.iTree.post_item

.. autofunction:: itertree.iTree.depth_up

.. autofunction:: itertree.iTree.max_depth_down

Item identification properties:

.. autofunction:: itertree.iTree.idx

.. autofunction:: itertree.iTree.tag_idx

.. autofunction:: itertree.iTree.idx_path

.. autofunction:: itertree.iTree.tag_idx_path

    >>> root=iTree('root')
    >>> root+=iTree('child',data=0)
    >>> root+=iTree((1,2),data='tuple_child0')
    >>> root+=iTree('child',data=1)
    >>> root+=iTree('child',data=2)
    >>> root+=iTree((1,2),data='tuple_child1')
    >>> root[0]+=iTree('subchild')
    >>> root.render()
    iTree('root')
     └──iTree('child', data=0)
        └──iTree('subchild')
     └──iTree((1, 2), data='tuple_child0')
     └──iTree('child', data=1)
     └──iTree('child', data=2)
     └──iTree((1, 2), data='tuple_child1')
    >>> root[0][0].root
    iTree("'root'", subtree=[iTree("'child'", data=0, subtree=[iTree("'subchild'")]), iTree("(1, 2)", data='tuple_child0'), iTree("'child'", data=1), iTree("'child'", data=2), iTree("(1, 2)", data='tuple_child1')])
    >>> root[0][0].idx
    0
    >>> root[0][0].tag_idx
    TagIdx('subchild', 0)
    >>> root[0][0].idx_path
    [0, 0]
    >>> root[0][0].tag_idx_path
    [TagIdx('child', 0), TagIdx('subchild', 0)]
    >>> root[1].tag_idx
    TagIdx((1, 2), 0)
    >>> root[-1].tag_idx
    TagIdx((1, 2), 1)

As shown in the last example hashable objects can be used as tags for the itertree items to be stored in the iTree object. Even for those kind of tag objects it is possible to store multiple items with the same tag. In the example the enumartion inside the tag family can be seen in the index enumeration in the TagIdx object.

Beside those structural properties the iTree objects contains some more properties that might be modified by the related methods.

.. autofunction:: itertree.iTree.is_temporary

.. autofunction:: itertree.iTree.is_read_only

.. autofunction:: itertree.iTree.is_linked

.. autofunction:: itertree.iTree.coupled_object

.. autofunction:: itertree.iTree.set_coupled_object()

Diffrent then the data the coupled_obj is just a pointer to another python object. By this you might couple the iTree to a graphical user interface object e.g. an item in a hypertreelist or it can be used to couple the itree object to an item in a mapping dictionary. The property couple_obj is not managed by the iTree object it's just a place to stroe the informations. for file exports or string exports this information will not be stored.

***************************
iTree data related methods
***************************

.. autofunction:: itertree.iTree.data

This is the data property. The property contains the iData objects which behaves in genral like a dict. There are two execpetions that must be considered: 
* The (__NOKEY__) key is an implizit key that will be used in case the user gives only one value (no_key) to the d_set() method. Then the given parameter will be stored in the (__NOKEY__) item of the dict.
* In case a dict item contains a iDataModel object the given value in iTree.d_set() will be checked against the data model.

To manipulate data you can use the functions of the iTree.data object or can use the quick access functions form iTree related to data access which have all the prefix "d_":

.. autofunction:: itertree.iTree.d_get

.. autofunction:: itertree.Data.iTData.__getitem__()

.. autofunction:: itertree.iTree.d_set

.. autofunction:: itertree.Data.iTData.__setitem__()

.. autofunction:: itertree.iTree.d_del

.. autofunction:: itertree.Data.iTData.__delitem__()

.. autofunction:: itertree.iTree.d_pop

.. autofunction:: itertree.Data.iTData.pop()

.. autofunction:: itertree.iTree.d_update

.. autofunction:: itertree.Data.iTData.update()

.. autofunction:: itertree.iTree.d_chk

.. autofunction:: itertree.Data.iTData.check()

Do not replace the iTree.data object with another object (iTree.data is just a property which is linking into the internal structure). You will destroy a part of the functionality, use iTree.data.clear() and iTree.data.update() instead.

***************************
iTree iterators and queries
***************************
The standard iterator for iTrees delivers all chidlren beside this we have same special iterators that contain filter possibilities.

.. autofunction:: itertree.iTree.__iter__()

.. autofunction:: itertree.iTree.iter_children()

.. autofunction:: itertree.iTree.iter_all()

.. autofunction:: itertree.iTree.iter_tag_idxs()

.. autofunction:: itertree.iTree.index()

Beside the classical ietartors we have the more query related find methods:

.. autofunction:: itertree.iTree.find_all()

For filter creation we have some helper classes (itree_filter.py)

.. autofunction:: itertree.Filter.iTFilterDataKey()


In each iTree object the user can store data objects. For this the data items are stored in the internal iTData class. It is possible to store just one data item or you can store multiple items by giving key/item pairs to the set function.

***************************
iTree formatted output
***************************
.. autofunction:: itertree.iTree.__repr__()

.. autofunction:: itertree.iTree.renders()

.. autofunction:: itertree.iTree.render()

***************************
iTree file storage
***************************

.. autofunction:: itertree.iTree.dump()

.. autofunction:: itertree.iTree.dumps()

.. autofunction:: itertree.iTree.load()

.. autofunction:: itertree.iTree.loads()

The file storage methods and the rendering methods are initialized by:

.. autofunction:: itertree.iTree.init_serializer()

This method is implizit executed and set to the default serializing functions of itertree. The user might load his own functionalities explicit by using this method or he might overload the iTree class and the init_serializer() method with his own functionality.

