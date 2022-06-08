# itertree python package


## Welcome to itertree python package. 

0.8.1 --BETA-- -> this is already final release candidate (all interfaces are fixed), 
                  we do just some more unit-testing to get the last bugs out!

Do you have to store data in a tree like structure? Do you need good performance, a reach feature set especially in 
case of filtered access to all data and the possibility to serialize and store the structure in files? Or do you like to use 
links to sub-trees and to cover items from a linked structure with new data?

Give itertree package a try!

The main class for construction of the itertree trees is the iTree class. The class allows the construction of trees like this:

    | iTree('root',data='xyz') 
    | └──iTree('subitem1',data='abc') 
    |       └──iTree('subsubitem1',data={'a':'b','b':'c'}) 
    | └──iTree('subitem2',data={1:2}) 
    | └──iTree('subitem2',data={2:3}) 

Every node in the itertree (iTree object) contains two parts of stored information:

* First the related sub-structure (iTree-children)
* Second the item related data attribute were any kind of object can be stored in

The itertree solution can be compared with nested dicts or lists. Other packages that targeting in the in the same direction
are anytree, xml.ElementTree, sorted_containers. In detail the feature-set and functional focus of iTree is a bit different. An overview of the advantage and disadvantages related to the other packages is given in the chapter Package :ref:`Comparison <comparison>`.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the itertree package.

```bash
pip install itertree
```

The package has no dependencies to other external packages. But the comparison tests with other packages 
are obviously only possible if the other packages are available.

But we have two recommendations which give the package additional performance:

* blist  -  *Highly recommended!* This will speedup the iTree performance in huge trees especially for inserting and lefthandside operations

    * package link: https://pypi.org/project/blist/
    * documentation: http://stutzbachenterprises.com/blist/.

-> in case the package is not found normal list object will be used instead

* orjson - A quicker json parser that used to create the JSON structures during serializing/deserializing

  -> in case orjson is not found, ujson package is checked too
  
  -> in case both not found normal json package will be used

##Feature Overview

The main features of the iTree object in itertree can be summarized in:

* trees can be structured in different levels (nested trees: parent - children - sub-children - ....)
* the identification tag can be a string or any kind of object that is hashable
* tags must not be unique (same tags are enumerated and collect in a tag-family)
* item access is possible via tag, tag-index, index, slices
* iTree keeps the order of the added children
* the item related data is stored in a protected data structure where data models can be used to evaluate the given data values
* a iTree can contain linked/referenced items (linking to other internal tree parts or to an external itertree file is supported)
* in a linked iTree specific items can be *localized* and they can *cover* linked elements
* standard export/import to JSON (incl. numpy and OrderedDict data serialization)
* designed for performance (huge trees with hundreds of levels)
* it's a pure python package (should be therefore usable in all embedded environments)

Here is very simple example of itertree usage:

    >>> from itertree import *
    >>> root=iTree('root',data={'mykey':0})
    >>> root+=iTree('sub',data={'mykey':1})
    >>> root+=iTree('sub',data={'mykey':2})
    >>> root+=iTree('sub',data={'mykey':3})
    >>> root.append(iTree('sub',data={'mykey':4}))
    >>> root.render()
    iTree('root', data="{'mykey': 0}")
     └──iTree('sub', data="{'mykey': 1}")
     └──iTree('sub', data="{'mykey': 2}")
     └──iTree('sub', data="{'mykey': 3}")
     └──iTree('sub', data="{'mykey': 4}")


##First steps


All important classes of the package are published by the __init__.py file so that the functionality of itertree can be reached by simply importing:

    >>> from itertree import *

The itertree trees are build by adding iTree-objects to a iTree-parent-object. This means we do not have an external tree generator.

We start now building a itertree with the recommended method for adding items.
You can just use the `+=` operator ( `__iadd__()` ) which adds a child item to the parent item
left of `=+` operator. The classical append() method is available too.

    >>> root=iTree('root') # first we create a root element
    >>> root+=iTree(tag='child', data=0) # add a child via += operator
    >>> root+=iTree(tag=(1,2,3), data=1) # add next child (tag is tuple, a hashable object)
    >>> root+=iTree(tag='child2', data=2) # add next child
    >>> root.render() # show the current tree
    iTree('root')
     └──iTree('child', data=0)
     └──iTree((1, 2, 3), data=1)
     └──iTree('child2', data=2)

Each iTree-object must have a tag which is the main part of the identifier of the object. For tags you can use any type of hashable objects
except integers and `TagIdx` objects (these objects are used for index access and they are
therefore not allowed as tags).

Different than the keys in dictionaries the given tags must not be unique:

    >>> root+=iTree(tag='child', data=3)
    >>> root+=iTree(tag='child', data=4)
    >>> root.render()
    iTree('root')
     └──iTree('child', data=0)
     └──iTree((1, 2, 3), data=1)
     └──iTree('child2', data=2)
     └──iTree('child', data=3)
     └──iTree('child', data=4)

In the iTree object equal tags are enumerated in a tag-family and they can be reached/identified
via the helper object `TagIdx`.

    >>> print(root[TagIdx('child',1)])
    iTree(tag='child', data=3)
    >>> print(root[3])
    iTree(tag='child', data=3)

To add subitems we can address the child item also by index (or `TagIdx`) and add a sub-item.

    >>> root[0]+=iTree('subchild')
    >>> print(root[0][0])
    iTree("'subchild'")

After the tree is generated we can iterate over the tree:

    >>> a=[i for i in root.iter_children()] # iter over the children and put result in list
    >>> print(a)
    [iTree("'child'", data=0, subtree=[iTree("'subchild'")]), iTree("(1, 2, 3)", data=1), iTree("'child2'", data=2), iTree("'child'", data=3), iTree("'child'", data=4)]
    >>> b=[i for i in root.iter_all()] # iter over all items (all levels) and put them into a list
    >>> print(b)
    [iTree("'child'", data=0, subtree=[iTree("'subchild'")]), iTree("'subchild'"), iTree("(1, 2, 3)", data=1), iTree("'child2'", data=2), iTree("'child'", data=3), iTree("'child'", data=4)]

The iterators and find functions of itertree have a `item_filters` parameter in which filter
functions/objects can be placed in to search for specific properties. The provided filter objects can also
be cascaded.

    >>> result=root.find_all(['**'],item_filter=Filter.iTFilterDataValue(2)) # '**' is a wildcard for any item; result is an iterator
    >>> print(list(result))
    [iTree(tag='child',data=2)]

The data handling can be done over set and get functions, if no specific key is given the
`__NOKEY__` element will be addressed automatically. This is very helpful in case you want to store just
one data object in the iTree-object.

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

At least the itertree can be stored and reconstructed from a file. We can also link an item to
a specific item in a file (external link) or create internal links.

    >>> root.dump('dt.dtz') # dtz is the recommended file ending for the zipped dataset file
    >>> root2=root.load('dt.dtz') # for loading a itertree any available iTree object can be used
    >>> print(root2==root)
    True
    >>> root+=iTree('link',link=iTLink(dt.dtz',iTreeTagIdx(child',0))) # The node item will integrate the children of the linked item.
    
##iterators vs. lists

We named the package itertree because when ever a iTree operation delivers multiple items the result will be an
iterator (and not a list what the user might expect).

Iterators are very powerful objects especially if you have a huge number of items to be iterated over.
Iterators can be created very fast and they can be combined. So you can create very effective filter functions. It's
recommended to have a look in the powerful itertools and more_itertools packages to combine it with itertree

The main idea is to combine all the filtering and iterator options together before you start the final iteration
(consume the iterator), which might at least end up in the expected list. By this mechanism we do at least only one
unique iteration over the items and we must not do multiple typecasts and re-iterations in between even when we
combine multiple filters.

If the user really wants to create a list he can easy cast the iterator by using the `list()` statement:

    >>> myresultlist=list(root.iter_all()) #  this is quick even for huge number of items
    >>> first_item=list(root.iter_all())[0] # Anyway this is much slower than:
    >>> first_item=next(root.iter_all())
    >>> fifth_item=list(root.iter_all())[4] # and this is much slower than:
    >>> import itertools
    >>> fifth_item=next(itertools.isslice(root.iter_all(),4,None))
    

As it is shown in the performance test the operation `list()` is very quick (less then 0.5 s on 1 million items
(depending on you PC)). And using the index access afterwards is a very good readable code. But as shown here there
are quicker solutions available on iterators only.

But we see also two downsides related to iterators:

* The StopIteration exception must be handled in case of empty iterators. To make the handling a bit easier iTree
  delivers in most cases an empty list if we have no match. But in some cases (e.g. filter operations) the user
  will get an empty iterator and not the empty list. In itree_helpers the user can find a check
  function for empty iterators that might help in this case: `is_iterator_empty(my_iterator)`.

* The user must also consider that an iterator can be consumed only one time. To reuse an iterator multiple times
  you may have a look on `itertools.tee()`.

To summarize this chapter: 

We decided that the iTree methods should deliver only iterators (and not lists). This is made to give the user
the possibility to utilize the whole iterator power afterwards. If he really needs a list (in most cases for
index access) he can cast the iterator easy and quick via the `list()` statement. But if iTree would directly
deliver lists by default we would have a performance drop in all itertree filter functions which is not
acceptable from our point of view.


