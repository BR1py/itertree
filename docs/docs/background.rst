.. _background:

Background information about itertree
=====================================

The itertree package is originally developed to be used in an internal test-system configuration and measurement
environment. In this environment we must handle a huge number of parameters and attributes which are configured
via a Graphical User Interface (GUI). The connection of the data and the GUI (editor) is realized via the coupled_object
function we have in `iTree`.
The so created configuration can be interpreted by test-systems and can be stored in version control systems.

But the idea of tree based configuration is nothing exceptionally new and of course trees can be used for many other
proposes. The itertree package for Python is a new approach to get
a very performant solution for these proposes even when the trees are very huge (many attributes in deep hierarchies).

In our case the package is also used in embedded environments and for this a pure Python implementation helps to
prevent us from different type of cross compilations for our targets. The package should run on
any Python >=3.4 interpreter.


****************
Architecture
****************

To find the best solution we made a lot of testing (check of the already available packages) and we checked other
implementation alternatives (like sorted or ordered dicts) but we came to the conclusion that it makes sense to
develop an own, new package to match all our requirements.

Based on the pre tests we created an architecture based on a list (blist) and a parallel managed dict that
contains the tag families again as lists (blist).

The `iTree` objects is build on these three base elements:

    * _items (list/blist) -> main list of items
    * _families (dict) -> dict containing the family list (key is tag)
    * _value -> place to store the data content of the item

Beside this structure the parent `iTree`-object is stored in the `iTree`-object by this we create the hierarchy.
An `iTree`-object can only have one parent! When you feed an `iTree` object during instantiation as subtree parameter
then the `iTree` objects children will be copied and taken over in the new `iTree`. The extend function has the
same behavior.

A free to use couple_object can be used to combine an `iTree` object with any other python object
(e.g. an object in a related tree GUI element) Or for other temporary data. It is not permanent in meaning that it
will not be stored in a file (if tree is saved) and it will not be considered in any comparisons
(except `equal()` where tit can be included).


The profiling of the package done by running over 100000 base operations gives the following result based on blist:

::

    Running on itertree version: 1.0.1
    Profiling is done based on 100000 single operations (some clas might be even used more often)
             5000038 function calls (4900039 primitive calls) in 3.334 seconds

       Ordered by: standard name

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000    3.334    3.334 <string>:1(<module>)
            1    0.000    0.000    0.000    0.000 copy.py:107(_copy_immutable)
            1    0.000    0.000    0.000    0.000 copy.py:66(copy)
       500005    0.033    0.000    0.033    0.000 itree_getitem.py:48(__init__)
       100002    0.078    0.000    0.130    0.000 itree_main.py:1041(append)
    500005/400006    1.440    0.000    1.999    0.000 itree_main.py:108(__init__)
       100000    0.128    0.000    0.159    0.000 itree_main.py:1187(insert)
            1    0.000    0.000    0.588    0.588 itree_main.py:1279(extend)
       100000    0.074    0.000    0.118    0.000 itree_main.py:1840(__delitem__)
       200000    0.067    0.000    0.094    0.000 itree_main.py:2018(__getitem__)
            1    0.000    0.000    0.803    0.803 itree_main.py:2160(__mul__)
       199999    0.050    0.000    1.051    0.000 itree_main.py:2261(__copy__)
            1    0.000    0.000    0.000    0.000 itree_main.py:2290(copy)
            2    0.000    0.000    0.000    0.000 itree_main.py:316(parent)
       200000    0.032    0.000    0.032    0.000 itree_main.py:3194(is_link_root)
            2    0.000    0.000    0.000    0.000 itree_main.py:340(root)
       300003    0.532    0.000    1.646    0.000 itree_private.py:223(_iter_extend)
       200000    0.068    0.000    0.113    0.000 itree_private.py:452(_get_copy_args)
       200000    0.193    0.000    1.001    0.000 itree_private.py:555(_iter_copy)
            1    0.356    0.356    3.334    3.334 itree_profile.py:54(performance_dt)
            1    0.038    0.038    0.271    0.271 itree_profile.py:67(<listcomp>)
       300000    0.017    0.000    0.017    0.000 {built-in method builtins.callable}
            1    0.000    0.000    3.334    3.334 {built-in method builtins.exec}
       400002    0.030    0.000    0.030    0.000 {built-in method builtins.hasattr}
       200003    0.015    0.000    0.015    0.000 {built-in method builtins.len}
       100000    0.006    0.000    0.006    0.000 {method '__getitem__' of 'blist.blist' objects}
       100000    0.008    0.000    0.008    0.000 {method '__getitem__' of 'dict' objects}
       299800    0.023    0.000    0.023    0.000 {method 'append' of 'blist.blist' objects}
       100200    0.007    0.000    0.007    0.000 {method 'append' of 'list' objects}
            2    0.000    0.000    0.000    0.000 {method 'copy' of 'blist.blist' objects}
       100000    0.005    0.000    0.005    0.000 {method 'copy' of 'list' objects}
            1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
            1    0.010    0.010    0.588    0.588 {method 'extend' of 'blist.blist' objects}
       600002    0.087    0.000    0.087    0.000 {method 'get' of 'dict' objects}
       100000    0.015    0.000    0.015    0.000 {method 'insert' of 'blist.blist' objects}
       100000    0.021    0.000    0.021    0.000 {method 'pop' of 'blist.blist' objects}


Form our point of view we see a well balanced behavior. Copy is relative costly because it is always an in-depth copy.
Deletion is slower then append but still relative quick.

Running the same profiling actions without blist package (using normal list) we get:
::

    Running on itertree version: 1.0.1
    Profiling is done based on 100000 single operations (some clas might be even used more often)
             5000038 function calls (4900039 primitive calls) in 12.823 seconds

       Ordered by: standard name

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000   12.823   12.823 <string>:1(<module>)
            1    0.000    0.000    0.000    0.000 copy.py:107(_copy_immutable)
            1    0.000    0.000    0.000    0.000 copy.py:66(copy)
       500005    0.034    0.000    0.034    0.000 itree_getitem.py:48(__init__)
       100002    0.315    0.000    0.361    0.000 itree_main.py:1041(append)
    500005/400006    0.615    0.000    1.463    0.000 itree_main.py:108(__init__)
       100000    0.171    0.000    1.515    0.000 itree_main.py:1187(insert)
            1    0.000    0.000    0.533    0.533 itree_main.py:1279(extend)
       100000    0.081    0.000    8.687    0.000 itree_main.py:1840(__delitem__)
       200000    0.066    0.000    0.091    0.000 itree_main.py:2018(__getitem__)
            1    0.000    0.000    0.685    0.685 itree_main.py:2160(__mul__)
       199999    0.049    0.000    0.386    0.000 itree_main.py:2261(__copy__)
            1    0.000    0.000    0.000    0.000 itree_main.py:2290(copy)
            2    0.000    0.000    0.000    0.000 itree_main.py:316(parent)
       200000    0.030    0.000    0.030    0.000 itree_main.py:3194(is_link_root)
            2    0.000    0.000    0.000    0.000 itree_main.py:340(root)
       300003    0.959    0.000    1.399    0.000 itree_private.py:223(_iter_extend)
       200000    0.067    0.000    0.108    0.000 itree_private.py:452(_get_copy_args)
       200000    0.103    0.000    0.337    0.000 itree_private.py:555(_iter_copy)
            1    0.194    0.194   12.823   12.823 itree_profile.py:54(performance_dt)
            1    0.038    0.038    0.238    0.238 itree_profile.py:67(<listcomp>)
       300000    0.016    0.000    0.016    0.000 {built-in method builtins.callable}
            1    0.000    0.000   12.823   12.823 {built-in method builtins.exec}
       400002    0.030    0.000    0.030    0.000 {built-in method builtins.hasattr}
       200003    0.014    0.000    0.014    0.000 {built-in method builtins.len}
       100000    0.033    0.000    0.033    0.000 {method '__getitem__' of 'dict' objects}
       100000    0.005    0.000    0.005    0.000 {method '__getitem__' of 'list' objects}
       400000    0.024    0.000    0.024    0.000 {method 'append' of 'list' objects}
       100002    0.005    0.000    0.005    0.000 {method 'copy' of 'list' objects}
            1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
            1    0.010    0.010    0.533    0.533 {method 'extend' of 'list' objects}
       600002    0.096    0.000    0.096    0.000 {method 'get' of 'dict' objects}
       100000    1.310    0.000    1.310    0.000 {method 'insert' of 'list' objects}
       100000    8.559    0.000    8.559    0.000 {method 'pop' of 'list' objects}

We see that blist package is really recommended because the general performnce is much better (3 times quicker).
But we have to look in the details:

    * `__init__()` - instancing is quicker with normal `list`
    * `copy()` - is much quicker with `list`
    * `insert()` - is much slower with `list`
    * `__delitem__()`- is extremely slow with `list`

And for item acces the classes are on same level but even that it is not checked in this analysis we must mention that
slicing is much quicker in `blist`. We found that slicing `[:]`is even quicker then `copy()` in `blist`-objects.

We can summarize: It's highly recommended to istnall `blist`package if itertree is used. With `list` only the object
still runs smooth (in some cases quicker) as long as the user avoids mass-opertion related to deletion or
insertion of items.

*********************************
Iteration-Generators and filters
*********************************

An investigation in other packages showed that search algorithms for specific items are sometimes very slow.
Even xml.ElementTree which shows overall a very good performance but it is not very fast when using the `find_all()`
method. The xpath syntax is relative powerful but sometimes difficult to use (e.g. try to target the text property). But
we found that using iterators and build-in `filter()` function might be quicker and easier to use.

In itertree we have the possibility to define filter functionalities for nearly all the in-depth iteration-generators.
We support here the  `filter_method` parameter for hierarchical filterings. This means in case the parent does not match
we will not iter over the children too.
Via external filtering (build-in `filter()`-method) the user can still filter inside the parents if required. But
hierarchical filtering is much easier to realize if supported inside the generator itself.

The filter method is fed by the `iTree`-item and must deliver a True/False after the analysis of the item is done.

The itertree package contains predefined filters in the `itree_filter.py` file and they can be reached via
`Filter.***` in the code.

Because we are using generators the filtering is very effective. The filters can be combined and so the user can create
queries like in a database to catch all information out of the tree and selected the matching items.

The resulting filtered-iterator-object is instanced very quick and it is totally independent from the tree size.
After all filtering is combined the iterator can be consumed and in maximum we will iterate only one time over the
whole tree. We do not waised any time in typecasts to lists inbetween. This is very memory effective and we
avoid unnecessary iterations.

To avoid RecursionErrors all internal and external iterations an done in an iterative and not recursive way. We made
tests and most often recursive algorithms will raise the RecursionError exceptions at tree depth >200 levels. The user
can extend this by changing Pythons recursion-limit. But it is not required for `iTree`. We also tested the iterative
implementation against the recursive ones and we did not find large differences.


****************************
File storage and serializing
****************************

The standard format for serializing and storage is a JSON format. It contains a header with environmental
information like file (interface) version and the checksum.
The data content is represented by a flatten list of items. We store the depth information for each item which
allows us to reconstruct the whole tree if the file is read in. If we would store here a nested list we risk that the
json-parser may raise RecursionError for deep trees.

The standard serializer can handle a large number of objects and serialize them into the JSON format
(numpy.arrays supported too). If the user has additional objects that should be serialized he may extend the serialize
or use his own serializer. The serializer is independent from `iTree` itself and another serializer can be
defined easily. Please use the `itree_serializer` parameter in the related methods
(the used serializer is stored after first usage and will be reused for future operations).

If the user likes to have other output formats (e.g. xml or MessagePack) he must also create his own serializer.

We allow already the packing and hashing of the data before we store it onto a file. Packing helps to keep the
files small but the cost of calculation time must be considered and sometimes it's better to use the unpacked files
and combine many of those files into an archive afterwards (independent from itertree). Therefore all these options
(packing, hashing)vare optional and can switch off if required.

*******************************
Data Structure and Data Models
*******************************

The structure the user store data in the `iTree.value` is totally free any object can be used.
In case of list or dict like objects (all objects with a `__getitem__()` method) the user can also use a
key or index based access to the items in the structure.

If the user likes to determine which data can be stored in the `ìTree.value`he can store a data model first.
If the provided data-model from itertree is used the `set_value()` method will set the value inside the model
automatically.

This works also for the key related setter `set_key_value()` in this case the user can store multiple data models
related to the given key or index in the `iTree.value` and again the method will exchange the value inside the model.

You might have a look in the examples/itree_data_models.py file to get a better idea what a data-model
is in this contents.
