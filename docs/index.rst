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
   docs/API
   docs/examples
   docs/comparison
   docs/background

.. _intro:


itertree - Introduction 
========================

| Do you have to store data in a tree like structure?
| Do you need good performance and a reach feature set in the tree object?
| You like to serialize and store the structure in files?
| And is it helpful for you if you can link subtrees from other trees and add local items in this "inherited" parts?

Please give itertree package a try!

The main class for construction of the trees is the `iTree`-class. Here is a
simple representation of a itertree:

::

     iTree('root', value='xyz')
     > iTree('subitem', value='abc')
     > iTree(('tuple', 'tag'), value={'dict': 'value'})
     .  > iTree('subtag', value=1)
     .  > iTree('subtag', value=2)
     > iTree('tag', value=[1, 2, 3])


Every node in the itertree (`iTree`-object) contains two main parts:

    * First the related sub-structure (`iTree`-children)
    * Second the item related value attribute were any kind of object can be stored in

The itertree solution can be compared with nested lists or dicts. Other packages that targeting in the in the same
direction are `anytree`, `(l)xml.ElementTree`, `PyToolingTree`. In detail the feature-set and functional focus
of `iTree` is a bit different. An overview of the advantage and disadvantages related to the other packages is given
in the chapter :ref:`Comparison <Comparison_Chapter>`.

************************************
Status and compatibility information
************************************


.. admonition:: |release|_ has been released!
   :class: note

   Be sure to read the :ref:`changelog <changelog>` before upgrading!

   Please use the `github issues <https://github.com/BR1py/itertree/issues>`_
   to ask questions report problems.

.. |release| replace:: Version | 1.0.2|
.. _release: https://pypi.python.org/pypi/itertree/

The original implementation is done in Python 3.9 and it is tested under Python 3.5, 3.6 and 3.9. The package
should work for all Python >= 3.4 environments.

The actual development status is "*released*" and stable.

The Software and all related documents are published under MIT license extended by a human protect patch
(see :ref:`Background Licence <background_licence>`).

************************************
Feature Overview
************************************

The main features of the itertree package can be summarized with:

* trees can be structured in different levels (nested trees: parent - children - sub-children - ....)
* the identification tag (key) can be any kind of hashable object
* tags must not be unique (same tags are enumerated and collect in a tag-family)
* item access is possible via tag-index-pair, absolute index, slices, index-lists or filters
* the `iTree`-object keeps the order of the added children
* an `iTree`-object can contain linked/referenced items (linking to other internal tree parts or to an external itertree file is supported)
* in a linked iTree specific items can be *localized* and they can *cover* linked elements (overloading)
* supports standard serialization via export/import to JSON (incl. numpy and OrderedDict data serialization)
* designed for performance (huge trees with hundreds of levels and over a million of items)
* helper functions and data models which can be used to specify the valid values are delivered too
* it's a pure python package (should be easy usable in all environments)
* in general the `iTree`-class can be seen as a functional mix of lists and dicts with deeper levels and references

Here is very simple example of itertree usage:

.. start: index-code 1

::
  
  >>> from itertree import * # required for all examples shown in the documentation
  >>> # Create root item:
  >>> root = iTree('root', value={'mykey': 0})
  >>> # Append children:
  >>> root.append(iTree('sub', value={'mykey': 1}))
  iTree('sub', value={'mykey': 1})
  >>> root.append(iTree('sub', value={'mykey': 2}))
  iTree('sub', value={'mykey': 2})
  >>> root.append(iTree('sub', value={'mykey': 3}))
  iTree('sub', value={'mykey': 3})
  >>> # Show tree content:
  >>> root.render()
  iTree('root', value={'mykey': 0})
   > iTree('sub', value={'mykey': 1})
   > iTree('sub', value={'mykey': 2})
   > iTree('sub', value={'mykey': 3})
  >>> # Address item via tag-index-pair (key):
  >>> root['sub', 1]
  iTree('sub', value={'mykey': 2})
  >>> # Address item via absolute-index and check stored value:
  >>> root[1].value
  {'mykey': 2}
.. end - entry created: 2023-06-19T22:04:40

*****************************
Documentation Content
*****************************

* :ref:`Introduction <intro>` - Short introduction to the itertree package (this page)

* :ref:`Tutorial <tutorial>` - A detailed Tutorial including functional sorted reference description

* :ref:`API Reference <API_reference>` - API Description of all containing classes and methods of itertree

* :ref:`Usage Examples <examples>` - itertree usage examples

* :ref:`Comparison <Comparison_Chapter>` - Compare itertree with other packages

* :ref:`Background information <background>` - Some background information about itertree and the target of the development


*****************************
Getting started, first steps 
*****************************

Installation and dependencies
-----------------------------

The package is a pure python package and does not have any dependencies. But we have two
recommendations which give the package additional performance:

    * blist  -  *Highly recommended!* This will speedup the iTree performance in huge trees especially for inserting and lefthand side operations

                    * package link: https://pypi.org/project/blist/
                    * documentation: http://stutzbachenterprises.com/blist/.

              -> in case the package is not found normal list object will be used instead
              -> depending on the size blist is especially better for `insert()` operations and slicing

              For Python 3.10 and 3.11 we created a package based on: https://github.com/stefanor/blist/tree/python3.11
              and some additional adaptions. The package can be found under:
              https://github.com/BR1py/itertree/tree/main/dist
              We did not test the package in detail but the itertree testsuite runs without issues.

              ..note :: We recommend to use it only for the newer Python versions. For older versions
                        Python <=3.9 use the original package from PyPI.


    * orjson - A quicker json parser that used to create the JSON structures during serializing/deserializing

              -> in case orjson is not found, standard json package will be used

To install the itertree package just run the command:
::

    pip install itertree

Inside the installed package the user can find a folder "examples" which might be a
good starting point to learn the functionalities.

First steps
------------

All important classes of the package are published by the package `__init__.py` file so that the functionality of
itertree can be reached by importing:

    >>> from itertree import *
    
.. note::  This import is a precondition for all shown code examples in this documentation.


The itertree trees are build by adding `iTree`-objects to a `iTree`-parent-object. This means we do not have an external
tree generator the tree is build by using the appending functionalities of the objects itself.

We start now building an itertree with the recommended method for adding items `append()`. The user might use the
lazy way via `+=` operator ( `__iadd__()` ) too. Both operations will add a child item at the end
of the parent sub-tree (like `append()` in lists).

.. start: index-code 2

::
  
  >>> root = iTree('root')  # first we create a root element (parent)
  >>> root.append(iTree(tag='child', value=0))  # add a child append method
  iTree('child', value=0)
  >>> root.append(iTree((1, 2, 3), 1))  # add next child (the given tag is tuple, any hashable object can be used as tag)
  iTree((1, 2, 3), value=1)
  >>> root += iTree(tag='child2', value=2)  # next child could be added via += operator too
  >>> root.render()  # show the created tree
  iTree('root')
   > iTree('child', value=0)
   > iTree((1, 2, 3), value=1)
   > iTree('child2', value=2)
  
.. end - entry created: 2023-06-19T22:04:40

Each `iTree`-object has a tag which is the main part of the identifier of the object. For tags you can use any
type of hashable objects.

Different than the keys in dictionaries the given tags must not be unique! The user should understand that in general
`iTree`-objects behave more like nested lists than nested dicts:

.. start: index-code 2_1

::
  
  >>> root.append(iTree('child', 5))
  iTree('child', value=5)
  >>> root.append(iTree('child', 6))
  iTree('child', value=6)
  >>> root.render()
  iTree('root')
   > iTree('child', value=0)
   > iTree((1, 2, 3), value=1)
   > iTree('child2', value=2)
   > iTree('child', value=5)
   > iTree('child', value=6)
  
.. end - entry created: 2023-06-19T22:04:40

In the `iTree` object equal tags are enumerated in a tag-family and they can be targeted
via a tag-index-pair (family-tag,family-index). In the "wording" of `ìTree` this pair is named
a **key** because it is unique like the keys in dicts. To summarize the items in an `iTree` can be accessed via
absolute index
(like in lists) or they can be reached by giving the key (tag-index-pair) which is comparable to the key in dicts
(both ways are very quick).

.. start: index-code 2_2

::
  
  >>> print(root['child', 1])  # target via key -> tag_idx pair
  iTree('child', value=5)
  >>> print(root[3])  # target via absolute index
  iTree('child', value=5)
  
.. end - entry created: 2023-06-19T22:04:40

E.g.: To add sub-items we can address the child item also by absolute index and add a sub-item.

.. start: index-code 2_3

::
  
  >>> root[0].append(iTree('subchild'))
  iTree('subchild')
  >>> print(root[0][0])
  iTree('subchild')
  
.. end - entry created: 2023-06-19T22:04:40

After the tree is generated we can iterate over the tree:

.. start: index-code 2_4

::
  
  >>> a = [i for i in root]
  >>> len(a)
  5
  >>> print(a)
  [iTree('child', value=0, subtree=[iTree('subchild')]), iTree((1, 2, 3), value=1), iTree('child2', value=2), iTree('child', value=5), iTree('child', value=6)]
  >>> b = list(root.deep)  # The list is build by iterating over all nested children
  >>> len(b)  # The item: root[0][0] is considered in this iteration too
  6
  >>> print(b)
  [iTree('child', value=0, subtree=[iTree('subchild')]), iTree('subchild'), iTree((1, 2, 3), value=1), iTree('child2', value=2), iTree('child', value=5), iTree('child', value=6)]
  
.. end - entry created: 2023-06-19T22:04:40

As shown in the example we have the possibility to iterate over the first level only (children) or we use the internal
class
absolute index
(like in lists) or they can be reached by giving the key (tag-index-pair) which is comparable to the key in dicts
(both ways are very quick).

.. start: index-code 2_5

::
  
  >>> print(root['child', 1])  # target via key -> tag_idx pair
  iTree('child', value=5)
  >>> print(root[3])  # target via absolute index
  iTree('child', value=5)
  
.. end - entry created: 2023-06-19T22:04:40

E.g.: To add sub-items we can address the child item also by absolute index and add a sub-item.

.. start: index-code 2_6

::
  
  >>> root[0].append(iTree('subchild'))
  iTree('subchild')
  >>> print(root[0][0])
  iTree('subchild')
  
.. end - entry created: 2023-06-19T22:04:40

Many iterable methods have a `filter_method` parameter in which a filtering method can be placed that targets specific
properties of the items.

.. start: index-code 2_7

::
  
  >>> # ----> filtering method can be placed that targets specific properties of the items.
  >>> a = [i for i in root.deep.iter(filter_method=lambda i: type(i.value) is int and i.value % 2 == 0)]  # search even data items
  >>> print(a)
  [iTree('child', value=0, subtree=[iTree('subchild'), iTree('subchild')]), iTree('child2', value=2), iTree('child', value=6)]
  
.. end - entry created: 2023-06-19T22:04:40

In case no value is given the `iTree` will take automatically the `itertree.NoValue` object as value.
In case an `iTree` is instanced without tag the tag value `itertree.NoTag` will be used.

.. start: index-code 3

::
  
  >>> empty_item = iTree()
  >>> print(empty_item)
  iTree()
  >>> print(empty_item.tag)
  <class 'itertree.itree_helpers.NoTag'>
  >>> print(empty_item.value)
  <class 'itertree.itree_helpers.NoValue'>
.. end - entry created: 2023-06-19T22:04:40

At least the itertree can be stored and reconstructed from a file. We can also link an item to
a specific item in a file (external link) or create internal links.

.. start: index-code 2_8

::
  
  >>> root.dump('dt.itz',overwrite=True)  # itz is the recommended file ending for the zipped dataset file
  9cd3a9a644af51ea94c82f64ca4ccf745b4a1dd717958beec0cfeb9b0647ba73
  >>> root2 = iTree().load('dt.itz')  # loading a iTree from a file
  >>> print(root2 == root)
  True
  >>> root += iTree('link', link=iTLink('dt.itz',[('child', 0)]))  # The node item will integrate the children of the linked item.
  
.. end - entry created: 2023-06-19T22:04:40

***************************
iTree-Generators vs. lists
***************************

As the package name itertree suggests we have several possibilities to iterate over the tree items. The related
functions are realized internally via generators. We have generators targeting the children only (level 1)
and we have others which ran in-depth into the whole tree structure targeting all the internal items (children, sub-children,...).
The provided generators can be easily casted into real iterators via build-in `iter()`-method (most often the cast is not required,
if target method takes generators (uses `__iter__()`)).

If `mytree` is an `iTree`-object e.g. you can iterate via:

    * iter(mytree) - level 1 iterator over all children delivers the items
    * iter(mytree.keys()) - level 1 iterator over all children delivers the tag-idx of the items
    * iter(mytree.values()) - level 1 iterator over all children delivers the values of the items
    * iter(mytree.items()) - level 1 iterator over all children delivers the (tag_idx,item) pair of the items

    ..

    * iter(mytree.deep) - flatten iterator over all in-depth items in the tree delivers the items
    * iter(mytree.deep.tag_idx_path()) - flatten iterator over all in-depth items delivers the (tag-idx-path,item) pair
    * iter(mytree.deep.idx_path()) - flatten iterator over all in-depth items delivers the (abs. index,item) pair

..

    * mytree.get.iter(*target_path) - delivers an iterator over all items targeted via target_path (multi item target)

The usage of generators (iterators) give some big advantages over the usage of lists related to
performance and memory consumption. The main idea is to combine all the filtering and iterable
options together before you start the final iteration
(consume the iter-generator).
The instancing of generators/iterators is is very quick and
independent from the number of items the object wil iter over. E.g. if the user would casts the inbetween results of
multiple operations into
'list'-objects it would take relative long time and the memory consumption would be much more.
Therefore it is recommended to build (cascade) all required operations based on the given generator/iterator object.
And only at the very end we should consume the generator/iterator. If the code
is build like this it is very quick and needs less memory. So please avoid type casts to lists in between the operations.
It is very helpful if the user have a look at the powerful `itertools`-package which can be utilized for those proposes.

If the user really wants to to end-up in a `list`-object he can easy cast the generator by using the `list()` statement
(The cast might be needed for list related functionalities like `len()`):

Related to generators/iterators the user should know:

* The StopIteration exception must be handled in case of empty generators.

* An generator can be consumed only one time. To reuse an generator multiple times
  you may have a look at `itertools.tee()`.

Here are some possible usages of the iteration functions in itertree (imagine large trees
for small trees the example operations are equivalent):

.. start: index-code 2_9

::
  
  >>> myresultlist = list(root.deep)  # this is quick even for huge number of items
  >>> first_item = list(root.deep)[0]  # but this is slower (list-type-cast)  as:
  >>> first_item = next(iter(root.deep)) # create an iterator from the generator object
  >>> fifth_item = list(root.deep)[4]  # and this is slower as:
  >>> import itertools
  >>> fifth_item = next(itertools.islice(root.deep, 4, None))
  
.. end - entry created: 2023-06-19T22:04:40




