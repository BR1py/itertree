.. _tutorial:

Tutorial
========

************************************
Status and compatibility information
************************************


The original implementation is done in python 3.5 and it is tested under python 3.5 and 3.9. It should work in all python 3 environments.

The actual development status is released.

***************************
Using the itertree package
***************************

To understand the full functionality of itertree the user should have a look on the related examples which can be found in the example folder of itertree.

In this chapter we try to dive in the functions of itertree in a clear structured way. The user might look in the class description of the modules too. But the huge number of methods in the `iTree` class might be very confusing. And we hope this chapter orders the things in a much better way.

***************************
Construction of an itertree
***************************


The first step in the construction of a itertree is to instance the :ref:`itertree `iTree` class`.


.. autoclass:: itertree.iTree
    :members: __init__

Instance the `iTree` object:
::

>>> item1=iTree('item1') # itertree item with the tag 'item1'
>>> item2=iTree('item2', data={'mykey':1}) # instance a iTree-object with data content (defined as a dict)
>>> item3=iTreeTemporary('temp_item') # instance a temporary iTree-object 
>>> # instance a iTree-object containing a link:
>>> item4=iTreeLink('linked_item', data={'mykey':2}, link_file_path='dt.itz', link_key_path=iTreeTagIdx('child',0), load_links=True) 


iTreeTemporary objects can be filtered out and when dumping the whole `iTree` into a file the iTreeTemporary items are ignored and not stored.

In case a link is set by using the iTreeLink class will integrate the childs of the linked iTree-objects as it's own childs into the tree. The `iTree` object can have own properties like temporary or own data. But it can also contain own, local children ( see `iTree linked sub-trees`_ ).


To add or manipulate the children of an item we have several possibilities. The following direct operations are recommended for structural manipulations in the tree:
::

>>> root=iTree('root')
>>> root.append(iTree('child')) # append a child
>>> root[0]=iTree('newchild') # replace the child with index 0
>>> del root[iTreeTagIdx('newchild',0)] # deletes the child with matching iTreeTagIdx


Additionally a huge set of methods is available for structural manipulations related to the children of a item.

.. autofunction:: itertree.iTree.append

.. autofunction:: itertree.iTree.__iadd__

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

Multiplication of a `iTree` is possible too the result is a list of `iTree` copies of the original one.
::

 >>> itree_list=iTree('a')*1000 # creates a list of 1000 copies of the original iTree
 >>> root=iTree('root')
 >>> root.extend(itree_list) # we can extend an existing `iTree` with the list (add 1000 identical children)
 True


***************************
item access
***************************

The items in the `iTree` can be accessed via __getitem__() method:

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

**************************************
iTree other structure related commands
**************************************

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


Because the __eq__() method (== operator) is internally used for same item object findings. We compare here based on the python object id. Therefore for the comparison of two non possibly not identical objects the equal() method should be used.

.. autofunction:: itertree.iTree.__contains__()

.. autofunction:: itertree.iTree.__hash__()

.. autofunction:: itertree.iTree.__len__()

Based on the `iTree` length the comparison operators <; <=; >; >= are available too.

.. autofunction:: itertree.iTree.count()

***************************
iTree properties
***************************

As we will see later on some properties of the `iTree` object can be modified by the related methods.
Warning:: The user should NEVER modify any of the given properties directly. Especially the not discussed private properties (marked with the beginning underline). Direct modifications will normally lead into inconsistencies of the `iTree` object!

The `iTree` object contains the following general properties:

.. autofunction:: itertree.iTree.root

.. autofunction:: itertree.iTree.is_root

.. autofunction:: itertree.iTree.parent

.. autofunction:: itertree.iTree.pre_item

.. autofunction:: itertree.iTree.post_item

.. autofunction:: itertree.iTree.depth_up

.. autofunction:: itertree.iTree.max_depth_down

.. autofunction:: itertree.iTree.is_temporary

.. autofunction:: itertree.iTree.is_read_only

.. autofunction:: itertree.iTree.is_linked

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

As shown in the last example hashable objects can be used as tags for the itertree items to be stored in the `iTree` object. Even for those kind of tag objects it is possible to store multiple items with the same tag. In the example the enumeration inside the tag family can be seen in the index enumeration in the TagIdx object.

Beside those structural properties the `iTree` objects contains some more properties that might be modified by the related methods.

.. autofunction:: itertree.iTree.coupled_object

.. autofunction:: itertree.iTree.set_coupled_object()

Different than the data the coupled_obj is just a pointer to another python object. E.g. by this you might couple the `iTree` to a graphical user interface object e.g. an item in a hypertreelist or it can be used to couple the `iTree` object to an item in a mapping dictionary. The property couple_obj is not managed by the `iTree` object it's just a place to store a pointer. In file exports or string exports this information will not be considered.

***************************
iTree data related methods
***************************

.. autofunction:: itertree.iTree.data

This is the data property. The property contains the iData objects which behaves in general like a dict. But there are two excepetions that must be considered: 
* The (__NOKEY__) key is an implizit key that will be used in case the user gives only one value (no_key) to the d_set() method. Then the given parameter will be stored in the (__NOKEY__) item of the dict.
* In case a dict item contains a iDataModel object the given value in `iTree`.d_set() will be checked against the data model.

To manipulate data you can use the functions of the `iTree`.data object or can use the quick access functions in `iTree` object ( methods related to data access have all the prefix *d_* ):

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

Do not replace the `iTree`.data object with another object (iTree.data is just a property which is linking into the internal structure). You will destroy a part of the functionality, use `iTree`.data.clear() and `iTree`.data.update() instead.

***************************
iTree iterators and queries
***************************

The standard iterator for iTrees delivers all children of the opbject. Beside this we have some special iterators that contain specific filter possibilities.

.. autofunction:: itertree.iTree.__iter__()

.. autofunction:: itertree.iTree.iter_children()

.. autofunction:: itertree.iTree.iter_all()

.. autofunction:: itertree.iTree.iter_all_bottom_up()

.. autofunction:: itertree.iTree.iter_tag_idxs()

.. autofunction:: itertree.iTree.index()

Beside the classical iterators we have the more query related find methods:

.. autofunction:: itertree.iTree.find_all()

For filter creation we have some helper classes (itree_filter.py)

.. autofunction:: itertree.Filter.iTFilterTrue()

.. autofunction:: itertree.Filter.iTFilterItemType()

.. autofunction:: itertree.Filter.iTFilterItemTagMatch()

.. autofunction:: itertree.Filter.iTFilterData()

.. autofunction:: itertree.Filter.iTFilterDataKey()

.. autofunction:: itertree.Filter.iTFilterDataKeyMatch()

.. autofunction:: itertree.Filter.iTFilterDataValueMatch()

Depending on the data stored in the `iTree`.data object the user might create own filters. In general just a method must be created that takes the item as an argument and that delivers True in case of a match and False in case of no match. We have also a base class (super-class) of the given filters available which might be used for own filters too.

.. autofunction:: itertree.Filter.iTFilterBase()

The fitering in `iTree` is very effective and quick. As an example one might execute the example script itree_usage_example1.py where the itertree.Filter.iTFilterData object is used.

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

This method is implicit executed and set to the default serializing functions of itertree. The user might load his own functionalities explicit by using this method or he might overload the `iTree` class and the init_serializer() method with his own functionality (e.g. an xml export/import might be realized by this).

***************************
iTree linked sub-trees
***************************

The `iTree` objects can be merged to one main tree from different source files by using the iTreeLink class. The result is a merged `iTree` that contains all the linked subtrees. Beside the linking from different files links inside a `iTree` structure (internal links) can be defined too.

Additionally the user can manipulate the linked items by making them local (covering) or by appending local items. The functionalities given here are limited to operations that do not imply a reordering of the elements in the tree. The reason for this is that the linked items cannot be reordered furthermore they gave the tree a fixed, static structure.  E.g. mainly we have `append()` and `make_self_local()` functions and we cannot `appendleft()` or `insert()` because this would mean we have to reorder the other elements. A change of a linked structure can only be made by manipulating the original source structure. We allow only the localization of items that are a child of the linked root element, in deeper levels this is not possible.

The local items in a linked `iTree` are integrated in the tree during the load process of the linked elements. The identification is always made via the TagIdx of the item. The local storage of the tree contains iTreePlaceholder elements which will be replaced by the linked in elements during the load process. Those placeholders are needed to create the matching tag-idx combination for the real elements that should be kept after reload. In case the loaded structure is changed and and no matching item is found the iTreePlaceHolder items will remain in the `iTree`. All appended local items which are outside of the linked structure will be found at the end of the itertree.

Local items can be manipuplated as normal `iTree` items with one exception. In case a local item is deleted and a matching linked item is available (was covered by the local item) the linked item will replace the local element after deletion. This means in this case a delete of an item will not reduce the numbers of the elements. If the local item has no corresponding linked item the number of children will decrease as usual.

The linked items must be loaded by an explizit operation. They are not loaded automatically. The links must be loaded via the `load_links()` method which can be executed at any level of the tree and it will start loading all links in the subtree (use `load_links()` on the `iTree` root to be sure to load all links). The behavior in case of load erros can be switched between Exceptions or deleting invalid elements (delete_invalid_items parameter). In case of exceptions the `iTree` is in an incomplete load state and if the exception is kept this must be handled (e.g. copy original tree before loading and replace back). The commands for loading `iTree` files can be influenced by the `load_links` parameter (to activate or deactivate the link loading) during file load.

.. warning:: The user must be aware that changing the source structure and local items in parallel might lead to unexpected results. **The identification of local items is always done via the TagIdx.** If we miss items during load placeholders are used to keep the TagIdx of the "real" local items. Normally those artefacts will be replaced during the load with linked items (if found) but in case of missmatches they will stay in the tree. Using wild linking in between different `iTree` elements can lead into very confusing situations especially if the user removes local items. We recommend to use the feature only in special cases where the source architecture is clearly defined and remains structural relative stable. For stability reasons we have also functional limitations in iTreeLink objects (e.g. we do allow only linking on not already linked elements (protection for circular definitions); local items cannot be linked items or temporary items).

.. autofunction:: itertree.iTreeLink

.. autofunction:: itertree.iTreeLink.load_links()

Beside this the following specific functions are available on linked items:

.. autofunction:: itertree.iTreeLink.make_self_local()

.. autofunction:: itertree.iTreeLink.make_child_local()

.. autofunction:: itertree.iTreeLink.iter_locals()


For a better understanding please have a look in the example file examples/itree_link_example1.py in the package. That contains the following examples too.

Special functionalities related to linking of iTrees:

To link a subtree in the current tree the iTreeLinked class is used.
::

    >>> #We create a small iTree:
    >>> root = iTree('root')
    >>> root += iTree('A')
    >>> root += iTree('B') 
    >>> # we add "B" tag two times to get an enumerated tag family
    >>> B=iTree('B')
    >>> B +=iTree('Ba')
    >>> #we create multiple 'Bb' elements to show how the placeholders are used during save and load
    >>> B +=iTree('Bb')
    >>> B +=iTree('Bb')
    >>> B +=iTree('Bc')
    >>> root += B
    >>> #Now we create a internal link (but we disable the loading -> load_links=False):
    >>> linked_element=iTreeLink('internal_link',link_key_path='/B',load_links=False)
    >>> root.append(linked_element)
    >>> print(root.render())
    iTree('root')
         └──iTree('A')
         └──iTree('B')
         └──iTree('B')
             └──iTree('Ba')
             └──iTree('Bb')
             └──iTree('Bb')
             └──iTree('Bc')
        └──iTreeLink('internal_link', link=iTreeLink(file_path=None, key_path=['/', TagIdx(tag='B', idx=1)]))
    >>> # now we load the links:
    >>> root.load_links()
    >>> print(root.render())
    iTree('root')
         └──iTree('A')
         └──iTree('B')
         └──iTree('B')
             └──iTree('Ba')
             └──iTree('Bb')
             └──iTree('Bb')
             └──iTree('Bc')
         └──iTreeLink('internal_link', link=iTreeLink(file_path=None, key_path=['/', TagIdx(tag='B', idx=1)]))
             └──iTreeLink('Ba')
             └──iTreeLink('Bb')
             └──iTreeLink('Bb')
             └──iTreeLink('Bc')

As shown in the example the internal linked element contains now the same subtree as the element "B". But they are integrated as iTreeLink objects which protects the items from changes (readonly). If we change the elements in the "B" item the changes are only considered if we reload the links in the tree!


    >>> B +=iTree('B_post_append')
    >>> print(root.render())
    iTree('root')
         └──iTree('A')
         └──iTree('B')
         └──iTree('B')
             └──iTree('Ba')
             └──iTree('Bb')
             └──iTree('Bb')
             └──iTree('Bc')
             └──iTree('B_post_append')
         └──iTreeLink('internal_link', link=iTreeLink(file_path=None, key_path=['/', TagIdx(tag='B', idx=1)]))
             └──iTreeLink('Ba')
             └──iTreeLink('Bb')
             └──iTreeLink('Bb')
             └──iTreeLink('Bc')
    >>> root.load_links(force=True) # we must force the reloading, if not forced already loaded trees will not be updated
    >>> print(root.render())
    iTree('root')
         └──iTree('A')
         └──iTree('B')
         └──iTree('B')
             └──iTree('Ba')
             └──iTree('Bb')
             └──iTree('Bb')
             └──iTree('Bc')
             └──iTree('B_post_append')
         └──iTreeLink('internal_link', link=iTreeLink(file_path=None, key_path=['/', TagIdx(tag='B', idx=1)]))
             └──iTreeLink('Ba')
             └──iTreeLink('Bb')
             └──iTreeLink('Bb')
             └──iTreeLink('Bc')
             └──iTreeLink('B_post_append')

The toplevel iTreeLink object allows manipulations of the subtree. We can append elements and we can change existing subitems to a local item taht covers the linked item and that can contain diffrent data and different children. 

    >>> #get the linked element
    >>> il=root[TagIdx('internal_link',0)]
    >>> #append an item
    >>> il.append(iTree('new'))
    >>> #we make second element local and append a item in the subtree
    >>> local=il.make_child_local(2)
    >>> local+=iTree('sublocal')
    >>> print(root.render())
    iTree('root')
         └──iTree('A')
         └──iTree('B')
         └──iTree('B')
             └──iTree('Ba')
             └──iTree('Bb')
             └──iTree('Bb')
             └──iTree('Bc')
             └──iTree('B_post_append')
         └──iTreeLink('internal_link', link=iTreeLink(file_path=None, key_path=['/', TagIdx(tag='B', idx=1)]))
             └──iTreeLink('Ba')
             └──iTreeLink('Bb')
             └──iTree('Bb')
                 └──iTree('sublocal')
             └──iTreeLink('Bc')
             └──iTreeLink('B_post_append')
             └──iTree('new')

The element 'Bb' in the linked subtree is now no more an iTreeLink object, its a normal `iTree` object. The identification of the covering item is internally always done via the TagIdx of the item. We can do all `iTree` related operations on this object. But there is one exception: if we delete the object the linked object will come back into the tree!

    >>> del il[TagIdx('Bb',1)]
    >>> print(root.render())
    iTree('root')
         └──iTree('A')
         └──iTree('B')
         └──iTree('B')
             └──iTree('Ba')
             └──iTree('Bb')
             └──iTree('Bb')
             └──iTree('Bc')
             └──iTree('B_post_append')
         └──iTreeLink('internal_link', link=iTreeLink(file_path=None, key_path=['/', TagIdx(tag='B', idx=1)]))
             └──iTreeLink('Ba')
             └──iTreeLink('Bb')
             └──iTreeLink('Bb')
             └──iTreeLink('Bc')
             └──iTreeLink('B_post_append')
             └──iTree('new')

The link functionality in iTrees can be understood like the overloading mechanism of classes. By linking a subtree in the tree this is like defining a superclass for a specific tree section. By making a subitem local this part of the linked `iTree` is covered (overloaded). But we should not stress this analogy to much because the functionalities in this covered data structures are much less then we have it for the class concept.

***************************
iTree helpers classes
***************************

In the itertree helper module we have some helper classes that can be used to construct specific `iTree` objects.

We have the following helper classes available:

.. autofunction:: itertree.itree_helpers.iTInterval()
.. autofunction:: itertree.itree_helpers.iTInterval.__init__()

.. autofunction:: itertree.itree_helpers.iTMatch()
.. autofunction:: itertree.itree_helpers.iTMatch.__init__()

.. autofunction:: itertree.itree_helpers.TagIdx()

.. autofunction:: itertree.itree_helpers.TagIdxStr()

.. autofunction:: itertree.itree_helpers.TagIdxBytes()

The other classes in itree_helpers are used internally in the `iTree` object and might be less interesting for the user.

Addinionally the user might have also a look in the other itertree modules like itertree_data.py or itertree_filter.py. Especially the class iTDataModel might be a good starting point for own data model definitions as it is also shown in  examples/itertree_data_model.py.

.. autofunction:: itertree.itree_data.iTDataModel()
