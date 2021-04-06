.. itertree documentation master file

Welcome to itertree python package
====================================

Do you like to store data some how in a tree like structure? Do you need good performance, a reach feature set and the possibility to store your data permanently in files?

Give itertree package a try!

The main class for construction of the itertrees is the iTree class. The class allows the construction of trees like this:

| iTree('root',data='xyz') 
| └──iTree('subitem1',data='abc') 
|       └──iTree('subsubitem1',data={'a':'b','b':'c'}) 
| └──iTree('subitem2',data={1:2}) 
| └──iTree('subitem2',data={2:3}) 

Every node in the itertree (iTree object) stores the related sub-structure (iTree-children) additinal the related node data can be stored in the internal data structure.

The itertree solution can be compared with nested dicts or lists. Other packages that targeting in the in the same direction are anytree, xml.ElemetTree, sorted_containers. In detail the feature-set and functional focus of iTree is a bit different. An overview of the advantage and disadvantages related to the other packages is given in the chapter Package Comparision.

************************************
Status and compatibility information
************************************


The original implementation is done in python 3.5 and it is tested under python 3.5 and 3.9. It should work in all python 3 environments.

The actual development status is Beta. The planned featureset is implemented. Work effort goes in the moment in testing, bugfixing and the creation of the documentation.

************************************
Feature Overview
************************************

The main features of the itertree can be summarized in:

* trees can be structured in different levels (nested trees: parent-children-sub-children-....)
* tags can be strings or any hashable objects
* tags must not be unique (same tags are enumerated and collect in a tag-family)
* keeps the order of the added children
* the data is stored in a protected data structure where data models can be used to evaluate the given data values
* a iTree can be linked into a itertree file (that is loaded and integrated in the itertree structure)
* standard export/import to JSON (incl. numpy and OrderedDict data serialisation)
* designed for performance (as good as it can be for a pure python implementation)
* it's a pure python package (should be therefore usable in all embedded environments)

Here is very simple example of itertree usage:
::
    >>>from itertree import *
    >>>root=iTree('root',data={'mykey':0})
    >>>root+=iTree('sub',data={'mykey':1})
    >>>root+=iTree('sub',data={'mykey':2})
    >>>root+=iTree('sub',data={'mykey':3})
    >>>root.append(iTree('sub',data={'mykey':4}))
    >>>root.render()
    iTree('root', data="{'mykey': 0}")
     └──iTree('sub', data="{'mykey': 1}")
     └──iTree('sub', data="{'mykey': 2}")
     └──iTree('sub', data="{'mykey': 3}")
     └──iTree('sub', data="{'mykey': 4}")

Getting started, first steps 
=============================

*****************************
Installation and dependencies
*****************************


The package does not have any dependencies, but we highly recommend the to install the blist package:  
https://pypi.org/project/blist/ ;Docu: http://stutzbachenterprises.com/blist/

This will speedup the iTree performance in huge trees especially for inserting and lefthandside operations (in case the package is not found normal list will be used instead).

To install the itertree package just run the command:
::
    pip install itertree

The structure of folder and files related to this package looks like this:

* itertree (main folder)

   * __init__.py
   * itree_main.py
   * itree_helpers.py
   * itree_data.py
   * itree_serialize.py

   * examples

      * itree_performance.py
      * itree_profiling.py

*****************************
The very first steps
*****************************


All important classes of the package are puplished by the __init__.py file so that the functionality of itertree can be reached by simply importing:
::
    >>>from itertree import *
    
.. note::  This line is needed if you want to rerun the given examples on this pages.


The datarees are build by adding iTree-objects to a iTree-parent-object. This means we do not have an external tree generator.

We start now building a itertree with the recommended method for adding items. Just use the += operator (__iadd__()) which adds the righthandside item to the lefthandside item.
::
    >>> root=iTree('root') # first we create a root element
    >>> root+=iTree(tag='child', data=0) # add a child via += operator
    >>> root+=iTree(tag=(1,2,3), data=1) # add next child (tag is tuple, a hashable object)
    >>> root+=iTree(tag='child2', data=2) # add next child
    >>> root.render() # show the current tree
    iTree('root')
     └──iTree('child', data=0)
     └──iTree((1, 2, 3), data=1)
     └──iTree('child2', data=2)

Each iTree-object must have a tag. For tags you can use any type of object that is hashable except integers and iTreeTagIdx objects (These objects are used for index access and they are therefore not allowed as tags).

Different than the keys in dictionairies the given tags must not be unique:
::
    >>>root+=iTree(tag='child', data=3)
    >>>root+=iTree(tag='child', data=4)
    >>>root.render()
    iTree('root')
     └──iTree('child', data=0)
     └──iTree((1, 2, 3), data=1)
     └──iTree('child2', data=2)
     └──iTree('child', data=3)
     └──iTree('child', data=4)

In the iTree object equal tags are enumerated in a tag_family and they can be reached with the helper object TagIdx.
::
    >>>print(root[TagIdx('child',1)])
    iTree(tag='child', data=3)

To add subitems we adress the child item by index and then add the sub-item.
::
    >>> print(root[2])
    iTree("'child2'", data=2)
    >>> root[0]+=iTree('subchild')
    >>> print(root[0][0])
    iTree("'subchild'")

.. note:: The addressing via index and via TagIdx objects are the quickest ways to reach an item in the itertree.

After the tree is generated we can iterate over the tree:
::
    >>> a=[i for i in root.iter_children()] # iter over the children and put result in list
    >>> print(a)
    [iTree("'child'", data=0, subtree=[iTree("'subchild'")]), iTree("(1, 2, 3)", data=1), iTree("'child2'", data=2), iTree("'child'", data=3), iTree("'child'", data=4)]
    >>> b=[i for i in root.iter_all()] # iter over all items and put them into a list
    >>> print(b)
    [iTree("'child'", data=0, subtree=[iTree("'subchild'")]), iTree("'subchild'"), iTree("(1, 2, 3)", data=1), iTree("'child2'", data=2), iTree("'child'", data=3), iTree("'child'", data=4)]

The iterators and find functions of itertree can use item_filters to search for specific properties. 
::
    >>>result=root.find_all(['**'],item_filter=root.create_data_value_filter(2)) # '**' is a wildcard for any item; result is an iterator 
    >>>print(list(result))
    [iTree(tag='child',data=2)]

The data handling can be done over set and get functions, if no specific key is given the ("__NOKEY__") element will be addressed. This is very helpful in case you want to store just one data object in the iTree-object.
::
    >>> root=iTree('root')
    >>> root.set(1)
    >>> root.get()
    1
    >>> root.set('mykey',2)
    >>> root.get() # the ("__NOKEY__") data item is untouched by the last operation
    1
    >>> root.get('mykey')
    2
    >>> item=iTree('root2',data={'A':'a','B':'b'})
    >>> item.data
    "{'A': 'a', 'B': 'b'}"

At least the itertree can be stored and reconstructed from a file. We can also link an item to a specific item in a file.
::
    >>>root.dump('dt.dtz') # dtz is the recommended file ending for the zipped dataset file
    >>>root2=root.load('dt.dtz') # for loading a itertree any available iTree object can be used
    >>>print(root2==root)
    True
    >>>root+=iTree('link',link=iTLink(dt.dtz',iTreeTagIdx(child',0))) # The node item will integrate the children of the linked item.
    

The itertree API - Reference
============================

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

.. automethod:: itertree.iTree.append

.. automethod:: itertree.iTree.appendleft

.. automethod:: itertree.itree_main.iTree.extend

.. automethod:: itertree.itree_main.iTree.extendleft

.. automethod:: itertree.itree_main.iTree.insert

.. automethod:: itertree.itree_main.iTree.move

.. automethod:: itertree.itree_main.iTree.rename

.. automethod:: itertree.itree_main.iTree.pop

.. automethod:: itertree.itree_main.iTree.popleft

.. automethod:: itertree.iTree.clear

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

.. automethod:: itertree.iTree.__getitem__()

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

***************************
iTree other structure related commands
***************************

.. automethod:: itertree.iTree.__setitem__()

.. automethod:: itertree.iTree.__delitem__()

.. automethod:: itertree.iTree.clear()

.. automethod:: itertree.iTree.copy()

.. automethod:: itertree.iTree.reverse()

.. automethod:: itertree.iTree.rotate()


***************************
iTree compare items
***************************

.. automethod:: itertree.iTree.__eq__()

.. automethod:: itertree.iTree.__neq__()

.. automethod:: itertree.iTree.equal()


Because the __eq__() method (== opertor) is internally used for same item object findings we really compare here based on the python object id. Therefore for the comparison of two non identical objects the equal() method should be used.

.. automethod:: itertree.iTree.__contains__()

.. automethod:: itertree.iTree.__hash__()

.. automethod:: itertree.iTree.__len__()

Based on the iTree length the comparison operators <; <=; >; >= are available too.

.. automethod:: itertree.iTree.count()

***************************
iTree properties
***************************

As we will see later on some properties of the iTree object can be modified by teh related methods. 
Warning:: The user should NEVER modify any of the given properties directly. Especially the not discussed private properties (marked with the beginning underline). Direct modifications will normally lead into inconsistencies of the iTree object!

The iTree object contains the following general properties:

.. automethod:: itertree.iTree.root

.. automethod:: itertree.iTree.is_root

.. automethod:: itertree.iTree.parent

.. automethod:: itertree.iTree.pre_item

.. automethod:: itertree.iTree.post_item

.. automethod:: itertree.iTree.depth

Item identification properties:

.. automethod:: itertree.iTree.idx

.. automethod:: itertree.iTree.tag_idx

.. automethod:: itertree.iTree.idx_path

.. automethod:: itertree.iTree.tag_idx_path

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

.. automethod:: itertree.iTree.is_temporary

.. automethod:: itertree.iTree.set_temporary()

.. automethod:: itertree.iTree.unset_temporary()

.. automethod:: itertree.iTree.coupled_obj

.. automethod:: itertree.iTree.set_coupled_obj()

Diffrent then the data the coupled_obj is just a pointer to another python object. By this you might couple the iTree to a graphical user interface object e.g. an item in a hypertreelist or it can be used to couple the itree object to an item in a mapping dictionary. The property couple_obj is not managed by the iTree object it's just a place to stroe the informations. for file exports or string exports this information will not be stored.

***************************
iTree data related methods
***************************

.. automethod:: itertree.iTree.data

The data property should never be modified directly (like all other properties too. This will lead into inconstiéncies of the iTree object.

Use the related methods instead. Those methods are linked to the related methods in the internal iTData object.

.. automethod:: itertree.iTree.get

.. automethod:: itertree.iTData.get()

.. automethod:: itertree.iTree.set

.. automethod:: itertree.iTData.set()

.. automethod:: itertree.iTree.pop_data

.. automethod:: itertree.iTData.pop()

.. automethod:: itertree.iTree.check

.. automethod:: itertree.iTData.check()

The iTData objects contains a special functionality so that the user can store easy any related data objects into the iTree internal iTData object. If set() function is used with out giving a key the object will be stored in the (__NOKEY__) item. For more complex data the user can combine the data with a key and it is stored in the internal dict like structure.


***************************
iTree iterators and queries
***************************
The standard iterator for iTrees delivers all chidlren beside this we have same special iterators that contain filter possibilities.

.. automethod:: itertree.iTree.__iter__()

.. automethod:: itertree.iTree.iter_children()

.. automethod:: itertree.iTree.iter_all()

.. automethod:: itertree.iTree.iter_tag_idxs()

.. automethod:: itertree.iTree.index()

Beside the classical ietartors we have the more query related find methods:

.. automethod:: itertree.iTree.find()

.. automethod:: itertree.iTree.findall()

For filter creation we have some helper methods in the iTree object:

.. automethod:: itertree.iTree.create_data_key_filter()

.. automethod:: itertree.iTree.create_data_value_filter()

.. automethod:: itertree.iTree.create_data_item_filter()

In each iTree object the user can store data objects. For this the data items are stored in the internal iTData class. It is possible to store just one data item or you can store multiple items by giving key/item pairs to the set function.

***************************
iTree formatted output
***************************
.. automethod:: itertree.iTree.__repr__()

.. automethod:: itertree.iTree.renders()

.. automethod:: itertree.iTree.render()

***************************
iTree file storage
***************************

.. automethod:: itertree.iTree.dump()

.. automethod:: itertree.iTree.dumps()

.. automethod:: itertree.iTree.load()

.. automethod:: itertree.iTree.loads()

The file storage methods and the rendering methods are initialized by:

.. automethod:: itertree.iTree.init_serializer()

This method is implizit executed and set to the default serializing functions of itertree. The user might load his own functionalities explicit by using this method or he might overload the iTree class and the init_serializer() method with his own functionality.

Some background informations regarding itertree
===============================================

The itertree package is originaly developed to be used in an internal test-system configuration and measurement environment. In this environment we must handle a huge number of parameters and attributes which are configured via a Graphical user Interface. The connection of the data and the GUI is realized via the coupled_obj function we have in iTree.

To find the best solution we made a lot of testing (check of the already available packages and we checked other implementation alternatives (like sorted or ordered dicts) but we came to the conclusion that it makes sense to develop an own, new package to match all our requirements.

Based on the tests we made the architecture is finally done on a list based implementation with a parallel managed dict that contains the TagIdx based information like tag-families and the related indexes. To speed up large lists we recommend to use blist package. When the itree package is imported we test if the package is available.

To speed up the instanciating process some information is only generated later on and only in case it is really needed.

When profiling the different core methods the time consumption can be seen in more detail:
::
    100000    0.220    0.000    0.473    0.000 itree_main.py:100(__init__)
    100000    0.053    0.000    0.076    0.000 itree_main.py:266(__getitem__)
    100000    0.080    0.000    0.110    0.000 itree_main.py:318(__delitem__)
    100000    0.178    0.000    0.186    0.000 itree_main.py:436(__iadd__)
    100000    0.223    0.000    1.379    0.000 itree_main.py:866(copy)
    100002    0.234    0.000    0.263    0.000 itree_main.py:995(extend)
   

During this profiling run we see that copy() is the most costly operation, next is __init__().

We do not use much caching in iTree objects only the index values iTree.idx and the tag related index are cached for quicker finding of the item in the list.

Usage examples
============================

In the example section you can find two example files itree_usage_example.py and itree_data_examples.py which explain how itertree package might be used.

In the file itree_usage_example.py a larger iTree is build ans manipulated and it is shown how the items in the tree can be reached. The example is in our opinion self explaining and we do not any more hints here.

In itree_data_examples.py we focus a bit on possible data models that might be used in iTree. We do not use any external packages in the examples but we recommend portion package for range definitions and also the Pydantic package might be a good option to define very powerful data models.

About the data models one can say that the data model can be used with the focus of checking and formatting of the stored data:
* check data type
* check value range (give intervals, limits)
* do we have an array of the data type and what is max length
* for strings we can use matches or regex checks of values
* for formatting think about numerical values (integer dec/hex/bin representation) or float number of digits to round to
* We can also define more abstract datatypes like keylists or enumerated keys.

In the file you can see some examples of how this data models can be defiend and used.

Comparison with other packages
==============================

Each package is develop with a specific focus and therefore a comparison is always a bit misleading. Finally the comparison remarks you find in this chapter are no not at all a judgement of the other packages. Especially the performance tests can also be misleading be cause we may have utilized the other packages in the wrong way. 

In this comparison chapter we will compare iTree with the standard types like dict and lists. Additionally we have a look on xml.ElementTree, sorted_dict (from sorted containers) and the anytree package. 

In the design paradigms of the itertree package can be summarized by the following topics. They will be highlighted and compared:

1. We can add any type of tag in the iTree as long as it is hashable and we can add the same tag multiple times in the iTree. Some of the comparable package support only stringtype tags (like anytree or xml.ElementTree). Other allow only unique tags like the keys in dicts (using same key will overwrite the already existing tag in this case).

2. In iTree the item access via index and tag (or TagIdx) is possible. As you will see in the performance tests later many of the other packages are focus on one type of access and the second type is then much slower. In my opinion they are defined to have a specific access type in mind. (E.g. it's quite clear that index access on huge dicts or key access in huge list will be very slow). But even the search mechanisms in specialized packages are still very slow in my opinion.

3. The access of multiple items via index list is possible my_itree[[1,4,5,6,9]] will deliver the indexed items in an iterator (The access via indexlist is in most packages not supported).

4. The results when running filter queries in iTree will be delivered very quick because we delivering always iterators. But this might make the coding from the point of usage sometimes a bit complicate because if you need index access to a specific element you must have to cast the iterator in a list (by (list(my_iterator)) or use itertools.is_slice() operation. It's always recommended to addresse the target items via the available iTree methods (find(), find_all() or even iTree[]) directly. You can also use the item_filter and matches to reach your results as good as possible.

5. We can link multiple source files into one iTree object. Most of the packages do not support links and even the load and storage into files is not automatically supported (Users can always create serializers but this can be sometimes very difficult considering all datatypes stored in a tree). iTree delivers the possibility to store several datatypes into a JSON file and we allow to link subparts of a tree into diffrent files. So that you combine your trees from different file sources.

6. At least the data in the iTree objects can be combined with a data model that checks if the give data values matching with the ones expected by the data model. This means jmuch more then just a check of datatype one can also define ranges or intervals to which the given values must match. This functionality makes iTree objects very attractive for the storage of certain configuration data.

To summarize the iTree functions are focused on this given topics. The package is not focused on sorting values. For future extension the group building (e.g. building iTree intersections, etc.) might be realized by delivering the related group interators.

Under examples you can find the "itree_perfomance.py" file which contains a short performance test regarding other comparable packages. The following results are create with blist package installed and utilized by iTree. I didn't created a commmandline interface please feel free to adapt the first line regarding the tree size and the number of repetitions. The measured times are always relative to one iteration but it's a summary of the given number of operations.

Running the test on a tree with 5000 items delivers the following result on my PC under python 3.5.
::
    >>>python iter_performance.py
    We run for treesizes: 5000 with 4 repetitions
    Exectime time itertree build (with insert): 0.026015675
    Exectime time itertree build: 0.024330450000000003
    Exectime time itertree build: with subtree list comprehension: 0.020939399999999997
    Exectime time itertree tag access: 0.0059641
    Exectime time itertree tag index access: 0.009975650000000003
    Exectime time itertree index access: 0.002971674999999993
    Exectime time itertree save to file: 0.06322012500000002
    Exectime time itertree load from file: 0.049249350000000025
    -- Standard classes -----------------------------------
    Exectime time dict build: 0.0012350749999999744
    Exectime time dict key access: 0.0009292250000000057
    Exectime time dict index access: 0.28833085
    Exectime time list build (via comprehension): 0.0007910749999999744
    Exectime time list build (via append): 0.0010759750000000068
    Exectime time list build (via insert): 0.004880924999999925
    Exectime time list index access: 0.00018914999999997129
    Exectime time list key access: 0.19022565000000002
    Exectime time OrderedDict build: 0.0017937999999999565
    Exectime time OrderedDict key access: 0.00098937500000007
    Exectime time deque build (append): 0.0014920750000000371
    Exectime time deque build (insert): 0.0017849250000000483
    Exectime time deque index access: 0.00027615000000003054
    -- SortedDict ---------------------------------
    Exectime time SortedDict build: 0.052125974999999936
    Exectime time SortedDict key access: 0.0020535250000000005
    Exectime time SortedDict index access: 0.015410475000000035
    -- xml ElementTree ---------------------------------
    Exectime time xml ElementTree build: 0.002996099999999946
    Exectime time xml ElementTree key access: 0.2468151249999999
    Exectime time xml ElementTree index access: 0.00019949999999990808
    -- anytree ---------------------------------
    Exectime time Anytree build: 0.6590694500000001
    Exectime time Anytree key access (no cache): 28.046290425000002
    Exectime time Anytree index access: 0.09262174999999928

I have following comments on the findings:

1. iTree objects behave ~ 20 times slower then the build in objects like dict, lists, etc. Reason is mainly that iTree is a pure python package which does not has the the speed advantage of an underlaying C-Layer. Anyway a 20 times slower execution is really not an issue if you consider the wide range of functionalities found in iTree objects.
2. For untypical access of dict per idx or list per key the buildin objects perform ~ 100 times slower then iTree.
3. The other tree like packages are on par or slower then iTree (in some cases incredible slower). An exception is the package xml-ElementTree which incredible fast in case of index access (quicker then buildin lists).

On a large tree of 500000 we have the following findings:
::
    >>>python iter_performance.py
    We run for treesizes: 500000 with 4 repetitions
    Exectime time itertree build (with insert): 2.6232671499999998
    Exectime time itertree build: 2.7199797
    Exectime time itertree build: with subtree list comprehension: 2.31382715
    Exectime time itertree tag access: 0.6250698000000003
    Exectime time itertree tag index access: 1.0864297
    Exectime time itertree index access: 0.286127350000001
    Exectime time itertree save to file: 6.571910975
    Exectime time itertree load from file: 5.457168599999999
    -- Standard classes -----------------------------------
    Exectime time dict build: 0.20076107499999907
    Exectime time dict key access: 0.14599812499999842
    Exectime time dict index access: skipped incredible slow
    Exectime time list build (via comprehension): 0.10968072500000048
    Exectime time list build (via append): 0.12277327499999657
    Exectime time list build (via insert): 48.27888635
    Exectime time list index access: 0.021388675000011403
    Exectime time list key access: Skipped incredible slow
    Exectime time OrderedDict build: 0.30613169999999457
    Exectime time OrderedDict key access: 0.14227942499999813
    Exectime time deque build (append): 0.17697375000000193
    Exectime time deque build (insert): 0.20823397499999885
    Exectime time deque index access: 7.319813974999988
    -- SortedDict ---------------------------------
    Exectime time SortedDict build: 5.629920824999999
    Exectime time SortedDict key access: 0.18590682500000355
    Exectime time SortedDict index access: 1.7704129499999937
    -- xml ElementTree ---------------------------------
    Exectime time xml ElementTree build: 0.487862475
    xml ElementTree key access skipped -> too slow
    Exectime time xml ElementTree index access: 0.02187282500000265
    -- anytree ---------------------------------
    Exectime time Anytree build: 0.6846071249999994
    Anytree key access skipped -> incredible slow
    Exectime time Anytree index access: not working


Some of the steps are skipped because bad performance (some functions need hours).

Maybe I made something wrong but I did not get the anytree package working for bigger treesizes (only building worked but access did not work).

Insertion of elements in lists is very slow. This might only be a minor cornercase because filling a list might always be done by append() or even better with a list comprehension. The iTree insertion mechanism (based on blist) works much quicker and is nearly on the speed of append(). But we also recommend list comprehension mechanism for quickest filling of itertrees too. The mayor time in filling an iTree goes into the instanciation and if need copy() of the list items.

***************************
iTree vs. dict / collections.OrderedDict
***************************
For the base functionality storing data paired with hashable objects as keys in a data structure where one can find the data by giving the key or iterate over the items the dict is 20 times quicker then iTree. But we have a lot of limitations. We cannot store one and the same hashable object (key) multiple times in the dict (item will always be overwritten). You can build nested dicts by putting sub dicts into dict keys. But the access to this nested structure is very limited no deep iterations are available out of the boy. Also search queries must be programmed above the dict structure. The normal dict does not support ordered storage only the OerderedDict axtension does this. At least we do not have acces to the order by index we always must create an iterator that can be misused for index access. Summary for the limited functional target the dict is a more effective way to store data then the iTree. But the overall functionality of iTree in all highlighted directions is much bigger then in dicts.

***************************
iTree vs. list / collections.deque
***************************

For lists and nested list we can found the same pros and cons we had for dicts in the last chapter except that the access in list is focused on index and not keywise access. We can say that index access in iTrees is also the most performent way to access items (quicker then tag or TagIdx based access). Insert operations in lists can be also very slow. For huge trees we recommend to install blist package which outperformnce lists in a lot of circumstances. Beside the the tag based access itree objects can also be reached via index lists (not available in lists). Deque objects behave in general as lists. We can quicker insert elements (linklist extension is easy) but get an items index() works much slower as in normal lists.

***************************
iTree vs. xml ElemenTree
***************************

The xml ElementTree package goes very much in the same direction as the iTree package. The performance regarding any list related action is very good and much better then iTree can deliver (C-Layer). But the handling of ElemntTrees is totally different. Trees are normally build by external factory functions an internal build interface is available too (list like behavior). The same tag can be stored multiple times in an ElemenTree. As the naming tells the package is mainly build to provide all xml related data structures and fucntionalities. And the storage and loading into/from files is widely support. By the way serializing of none string objects in the tree must be managed and organized by the user. The data is stored under string tags one cannot use any hashable object here. Even the string usage is limited to the xml nameing convention (e.g. no spaces are allowed). For queries in the tree one can use the xpath syntax. iTree has comparible functionalities. Beside the index access iTree is quicker the ElemenTree especially when searching for specific tags. Serialization and storage is more efficeant then in ElemenTree. But iTree does not have all the xml powered higher level functionalities like schemata, etc. which are support by ElemenTree, this is no not at all the target of iTree.

***************************
iTree vs. sorted_dict
***************************

The sorted_dict package from sorted_contains might be used for the same proposes iTree is build for. But the architecture for realization is a bit different. Sorted_dict supports key and index based access. But one cannot store same key multiple times (behavior is here the same as in normal dicts). The iTree object has not the target of sorting items in different ways. Furthermore iTree tries to relize filtered access to the items by keeping the original order. In one first approach the author tried to realize the iTree functionalities with an underlying sorted_dict. But the performance of the approach was worse and we changed the strategy. 
iTree does not yet support the grouping function supported by sorted-dicts. But building intersections, etc. of two or more iTrees might be supported in an upcoming version of iTree. The performance of sorted-dicts regarding the design paradigms of iTree is less good. Especially the instanciation of sorted-dict objects of a huge number is 2 times slower than for iTree objects.

***************************
iTree vs. anytree
***************************
The anytree packages gains mostly in the same direction as itertree. You can find nearly comparable serialization possibiliies. The rendering found in iTree is a simple "copy" of what you can get in anytree. As in iTree objects you can combine children of same name with a parent in anytree too. But you can only use string based tags. The way you can navigate in the tree is in anytree a bit more extended compared to iTree object. Before the itertree package was developed we thought anytree is the solution to go for and there is no need for a package like itertree. But the results of the anytree package tests we did where very ambigous. We found a very rich featureset but in some cases a very poor performance. But the real blocker is that the access to the children property on large trees (>10000 items) is not working at all (or we do something wrong).

At least we came to the conclusion that anytree seems not match to our requirements for tree structured storage and access. From description it should match, but in practice the package did not work for us as expected.

.. toctree::
   :maxdepth: 10
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
