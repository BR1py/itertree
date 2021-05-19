.. raw:: html

    <div style="float:right; margin:1em 0em 1em 1em; padding: 0em 1em 1em 1em;">
    <span style="color:transparent;position: absolute;font-size:5px;width: 0px;height: 0px;">B.R.</span></a>
    <br/>
    </div>
 
   


.. toctree::
   :maxdepth: 1
   :hidden: 

   docs/docs
   docs/changelog
   docs/tutorial
   docs/itertree_api
   docs/itertree_examples
   docs/comparison
   docs/background

.. _intro:


itertree - Introduction 
========================

Do you like to store data some how in a tree like structure? Do you need good performance, a reach feature set especially in case of filtered access to all data and the possibility to serialize and store the structure in files?

Give itertree package a try!

The main class for construction of the itertrees is the iTree class. The class allows the construction of trees like this:

| iTree('root',data='xyz') 
| └──iTree('subitem1',data='abc') 
|       └──iTree('subsubitem1',data={'a':'b','b':'c'}) 
| └──iTree('subitem2',data={1:2}) 
| └──iTree('subitem2',data={2:3}) 

Every node in the itertree (iTree object) stores the related sub-structure (iTree-children) additional the related node data can be stored in the internal data structure of the object.

The itertree solution can be compared with nested dicts or lists. Other packages that targeting in the in the same direction are anytree, xml.ElemetTree, sorted_containers. In detail the feature-set and functional focus of iTree is a bit different. An overview of the advantage and disadvantages related to the other packages is given in the chapter Package :ref:`Comparison <comparison>`.

************************************
Status and compatibility information
************************************


.. admonition:: |release|_ has been released!
   :class: note

   Be sure to read the :ref:`changelog <changelog>` before upgrading!

   Please use the `github issues <https://github.com/BR1py/itertree/issues>`_
   to ask questions report problems. **Please do not email me directly**

.. |release| replace:: Version | 0.7.3|
.. _release: https://pypi.python.org/pypi/itertree/

The original implementation is done in python 3.5 and it is tested under python 3.5 and 3.9. It should work in all python 3 environments.

The actual development status is Beta. The planned featureset is implemented. Work effort goes in the moment in testing, bugfixing and the creation of the documentation and examples.

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

*****************************
Documentation
*****************************

* :ref:`Introduction <intro>` - Short introduction to the itertree package

* :ref:`Tutorial and Reference <tutorial>` - Detailed Tutorial about the usage of the itertree

* :ref:`API Reference <API_reference>` - API Description of all containing classes and methods of itertree

* :ref:`Usage Examples <examples>` - itertree usage examples

* :ref:`Comparison <comparison>` - Compare itertree with other packages

* :ref:`Background information <background>` - Some background information about itertree and the target of the development


*****************************
Getting started, first steps 
*****************************

Installation and dependencies
-----------------------------

The package is a pure python package abd does not have any dependencies. But we have some high recommandations to give the package additional performance:

* blist - This will speedup the iTree performance in huge trees especially for inserting and lefthandside operations (see https://pypi.org/project/blist/ ;Docu: http://stutzbachenterprises.com/blist/). -> in case the package is not found normal list will be used instead

* orjson - quicker json parser used to create the JSON structures during serializing/deserializing (an installed ujson will be  considered too, but it's a bit slower then orjson in our case)) -> in case orjson is not found and ujson is not found the standard json module will be used.

To install the itertree package just run the command:
::
    pip install itertree

The structure of folder and files related to this package looks like this:

* itertree (main folder)

   * __init__.py
   * itree_main.py

   * itree_data.py
   * itree_filter.py
   * itree_helpers.py
   * itree_serialize.py

   * examples

      * itree_performance.py
      * itree_profiling.py
      * itree_profiling2.py
      * itree_data_models.py
      * itree_usage.py

First steps
------------


All important classes of the package are puplished by the __init__.py file so that the functionality of itertree can be reached by simply importing:
::
    >>>from itertree import *
    
.. note::  This line is needed if you want to rerun all the given examples on this pages.


The datarees are build by adding iTree-objects to a iTree-parent-object. This means we do not have an external tree generator.

We start now building a itertree with the recommended method for adding items. You can just use the += operator (__iadd__()) which adds the righthandside item to the lefthandside item or you use the append() method.
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

In the iTree object equal tags are enumerated in a tag_family and they can be reached via the helper object TagIdx.
::
    >>>print(root[TagIdx('child',1)])
    iTree(tag='child', data=3)

To add subitems we address the child item by index and then add the sub-item.
::
    >>> print(root[2])
    iTree("'child2'", data=2)
    >>> root[0]+=iTree('subchild')
    >>> print(root[0][0])
    iTree("'subchild'")

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
    >>>result=root.find_all(['**'],item_filter=Filter.iTFilterDataValue(2)) # '**' is a wildcard for any item; result is an iterator
    >>>print(list(result))
    [iTree(tag='child',data=2)]

The data handling can be done over set and get functions, if no specific key is given the ("__NOKEY__") element will be addressed. This is very helpful in case you want to store just one data object in the iTree-object.
::
    >>> root=iTree('root')
    >>> root.d_set(1)
    >>> root.d_get()
    1
    >>> root.d_set('mykey',2)
    >>> root.d_get() # the ("__NOKEY__") data item is untouched by the last operation
    1
    >>> root.d_get('mykey')
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
    
*******************
iterators vs. lists
*******************

We named the package itertree because when ever a operation delivers multiple items as result the iTree object delivers an iterator (not a list what the user might expect). 

Iterators are very powerful instruments. The creation of the iterator can be done very fast. They can be combined and you can create very effective filters. It's recommended to have a look in the powerful itertools and more_itertools packages to combine it with itertree (functions are realized on c-level they are incredible fast). 
The main idea is to combine all the filtering and iterator options together before you start the final iteration (consume the iterator), which might end up in a list. By this we do at least only one iteration over the items and we must not do multiple typecasts in between even when we combine multiple filters.

If the user wants to have the expected list he can easy cast the iterator:
::
    >>>myresultlist=list(root.iter_all()) #  this is quick even for huge number of items
    >>>first_item=list(root.iter_all())[0] # Anyway this is much slower than:
    >>>first_item=next(root.iter_all())
    >>>fifth_item=list(root.iter_all())[4] # and this is much slower than:
    >>>fifth_item=next(itertools.isslice(root.iter_all(),4,None))
    

As it is shown in the performance test this operation list() is very quick (less then 0.5 s on 1 million items (depending on you PC)). And using the index access afterwards is a very good readable code. But as shown here there are quicker solutions available on iterators.

But there might be two downsides:

* The StopIteration exception must be handled in case of empty iterators. To make the handling a bit easier iTree delivers in most cases an empty list if we have not match. But in some cases (e.g. filter operations) the user will get an iterator even when the iterator is empty. In helpers the user can find an iterator empty check function (is_iterator_empty(iterator)).

* The user must also consider that an iterator can only consumed one time. To reuse an interator multiple times you may have a look on itertools.tee().

To summarize this chapter: 

We decided to deliver only iterators (and not lists) to give the user the possibility to utilize the whole iterator power. If he really needs a list (in most cases for index access) he can convert to a list very easy and quick. But giving lists directly would slowdown the performance of the whole itertree filter functions a lot.


