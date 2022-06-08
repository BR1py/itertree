.. _background:

Background information about itertree
=====================================

The itertree package is originally developed to be used in an internal test-system configuration and measurement
environment. In this environment we must handle a huge number of parameters and attributes which are configured
via a Graphical User Interface (GUI). The connection of the data and the GUI (editor) is realized via the coupled_object
function we have in `iTree`.
The so created configuration can be interpreted by test-systems and can be stored in version control systems.

But the idea of tree based configuration is nothing exceptionally new and of course trees can be used for many other
proposes. The itertree package is in Python a new approach to get
a very performant solution for these proposes even when the trees are very huge (many attributes in deep hierarchies).

In our case the package is also used in embedded environments and for this a pure Python implementation helps to
prevent us from different type of cross compilations for our targets. The package should run on
any Python 3.x interpreter.


****************
Architecture
****************

To find the best solution we made a lot of testing (check of the already available packages) and we checked other
implementation alternatives (like sorted or ordered dicts) but we came to the conclusion that it makes sense to
develop an own, new package to match all our requirements.

Based on the tests we created an architecture based on a list (blist) and a parallel managed dict that contains the
tag families again as lists (blist).

The `iTree` objects is build on these three base elements:

    * `iTree` (list) -> main list of items
    * _map (dict) -> dict containing the family list (key is tag)
    * _data (iTData) -> data object that stores all the data attributes related to the `iTree` item

Beside this structure the parent `iTree` object is stored in the `iTree` object by this we create the hierarchy.
An `iTree` object can only have one parent! When you feed an `iTree` object during instantiation as subtree parameter
then the `iTree` objects children will be copied and taken over in the new `iTree`. The extend function has the
same behavior.

A free to use couple_object can be used to combine an `iTree` object with any other python object
(e.g. an object in a related tree GUI element).


The profiling of the package done by running over 100000 base operations gives the following result based on blist:
::
    Running on itertree version: 0.6.1
    100003    0.161    0.000    0.342    0.000 itree_main.py:111(__init__)
    100000    0.044    0.000    0.059    0.000 itree_main.py:269(__getitem__)
    100000    0.090    0.000    0.383    0.000 itree_main.py:302(__delitem__)
    100000    0.239    0.000    0.258    0.000 itree_main.py:870(append)
    100000    0.269    0.000    0.286    0.000 itree_main.py:829(insert)
    100000    0.160    0.000    0.891    0.000 itree_main.py:725(__copy__)
    1         0.154    0.154    0.977    0.977 itree_main.py:919(extend)
    100000    0.067    0.000    0.089    0.000 itree_main.py:622(idx)
   
We can see that creating copies is the most time consuming operation and it is the reason why the one extend()
operation takes so long.

Running the same profiling actions without blist package (using normal list) we get:
::
    100003    0.161    0.000    0.320    0.000 itree_main.py:111(__init__)
    100000    0.052    0.000    0.060    0.000 itree_main.py:269(__getitem__)
    100000    0.094    0.000    1.266    0.000 itree_main.py:302(__delitem__)
    100000    0.140    0.000    0.161    0.000 itree_main.py:870(append)
    100000    0.228    0.000    1.895    0.000 itree_main.py:829(insert)
    100000    0.129    0.000    0.701    0.000 itree_main.py:725(__copy__)
    1         0.149    0.149    0.914    0.914 itree_main.py:919(extend)
    100000    0.082    0.000    0.097    0.000 itree_main.py:622(idx)
    
Especially the index based searches in the lists are take much longer. And especially the `insert()` take exceptionally
much longer but one may see this as a corner case only because the filling of a huge tree will normally always be done
by appending or even better by extending elements. Inserting a single item is absolutely no issue! Please consider we
talk here about a very huge number of `insert()` operations (100000). Same arguments can be made for the `__delitem__()`
operation nobody will delete all the items step by step it's much easier to delete or clear the parent instead.

We can summarize: Except from the told corner cases the itertree package runs with the same speed
(sometimes a bit faster) even that the blist package is not installed.

*********************
Special `iTree` objects
*********************

In an itertree person might need temporary items or they like to combine the tree from different sources (files).
Or they might like to protect specific items from writing (read only). For this proposes we can integrate special iTree
objects in the itertree.

Besides the normal `iTree` object we have three other types of `iTree` objects available:

    * `iTreeLink` - Link to another `iTree` file/key so that an itertree can be created from different source files. Also
      internal linking to other branches of the root object supported. The children and sub children of these linked
      objects are read only. But they can be localized and by this you can cover the orignal linked items by a
      new structure.

    * `iTreeReadOnly` - An read_only object that allows no changes in the `iTree` structure
      (properties (like data or coupled_object) can be changed)

    * `iTreeTemporary` - a temporary `iTree` item (These items behave like normal `iTree` items except that
      they are not stored in a file. If `dump()` is called these items are filtered out.

    * `iTreePlaceHolder` - an internally used object that is used to keep the indexing of localized items during storage.


For data protection a `iTDataReadOnly` class is available too.

*********************
Iterators and filters
*********************

An investigation in other packages showed that search algorithms for specific items are sometimes very slow.
Even xml.ElementTree which shows overall a very good performance is not very fast when using the `find_all()`
method. Beside this the string based xpath syntax is sometimes also a bit difficult and not as powerful and flexible
as it might be needed for complex data structures and data objects different from strings.

In itertree we have the possibility to define filter functionalities for all the iterators delivered by the
`iter_children()`, `iter_all()` or `find()` and `find_all()` methods. These methods contain a `item_filter` parameter
where the user can give a filter method or class. Those objects can be cascaded to create complex filters
(and/or logic supported).

The filter method is fed by the item and must deliver a True/False after the analysis of the item is done.

The itertree package contains predefined filters in the `itree_filter.py` file and they can be reached via
`Filter.iTFilter****` in the code.

Because we are using iterators the filtering is very effective. The filters can be combined and so the user can create
queries like in a database to catch all information out of the tree and selected the matching items.

The resulting iterator is delivered very quick totally independent from the tree size. After all filtering is combined
the iterator can be consumed and in maximum we will iterate only one time over the whole tree.

****************************
File storage and serializing
****************************

At the moment we serialize to JSON and the speed (with `orjson` module) is comparable with `pickle`. But we see that there
is still room for improvements and we might get quicker results in the future. Also we might consider other output
formats like `MessagePack` or `xml`.

Anyway we allow already the packing and hashing of the data before we store it onto a file. Packing helps to keep the
files small but the cost of calculation time must be considered and sometimes it's better to use the unpacked files
and combine same into an archive afterwards (independent from itertree). Therefore all these options (packing, hashing)
are optional and can switch off if required.

*******************************
Data Structure and Data Models
*******************************

The data structure of a `iTree` is not ordered (do not confuse data with the tree structure). It behaves like a
normal dict (We do not see why we should create a second ordered structure here). If the user really needs this he can
add any type of object into the data structure (e.g. also `OrderedDict`s). And for newer Python versions the `dict`
is ordered anyway.
But to be honest in this case it might be better to create a deeper `iTree` containing all the items of the `OrderedDict`
in an `iTree` branch instead.

To create a better usability the data structure can be fed directly with only one data object. Alternatively the user
can store also multiple objects by giving key,value pairs. Internally the `iTData` object is an overloaded dictionary.

The itertree package contains a concept for data models for the attributes stored in the data structure of the `iTree`.
By this the user can determine what kind of data can be stored in a specific attribute. The `iTDataModel` is just a
basic structure which can be used to create more advanced models. You might have a look in the
examples/itree_data_models.py file to get a better idea.

In general the data model allows to define the target data type but furthermore also the dimension, the range, etc.
Also the formatting of the data when casted into a string can be defined.
E.g. we can define the following data models:

    * We can define an integer in the range 0-255 in a 1 dimensional array (`list`) of maximum length 8. Additionally
      we like to have a hex representation when converted into a string.

    * We define a float value in the range in between -250 and 250 and we like to have a string representation
      of maximum 3 digits and added by a unit string "V" ("%.3f V").

If a data model is stored in the data structure we can put only values into the related attribute that are matching
to the model. In case of no matching values the set command will raise an `iDataValueError` exception.

.. note:: If define your own data_models and or `iData`classes ensure that you create a matching interface! E.g. the
           `check()`and `_validator()`methods must deliver the value as return (needed for recursive operations).

