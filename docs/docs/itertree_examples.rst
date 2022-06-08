.. _examples:

itertree examples package
================

**************
Usage examples
**************

In the example section you can find two example files itree_usage_example.py and itree_data_examples.py which explain how itertree package might be used.

In the file itree_usage_example.py a larger `iTree` is build ans manipulated and it is shown how the items in the tree can be reached. The example is in our opinion self explaining and we do not any more hints here.

In itree_data_examples.py we focus a bit on possible data models that might be used in `iTree`. We do not use any external packages in the examples but we recommend portion package for range definitions and also the Pydantic package might be a good option to define very powerful data models.

About the data models one can say that the data model can be used with the focus of checking and formatting of the stored data:
* check data type
* check value range (give intervals, limits)
* do we have an array of the data type and what is max length
* for strings we can use matches or regex checks of values
* for formatting think about numerical values (integer dec/hex/bin representation) or float number of digits to round to
* We can also define more abstract datatypes like keylists or enumerated keys.

In the file you can see some examples of how this data models can be defined and used.


Modules
----------

itertree usage example
----------------------
`itertree.examples.itree_usage_example1.py`

In this script we read in a part of the file system and we create an itertree which contains the some file information. Afterwards we filter on some conditions like filesize or modification times. Depending on the number of files found in the folder the first step (iTree creation) might need a short while.

After executing the script the output might look like this:
::
    We read a part of the filesystem ('c:/ProgramData') into an itertree
    Number of items read in 15633
    The load in tree has a depth of 15
    How many files are bigger then 1000000 Bytes?
    Number of Matches: 934
    How many files are in size 9000 ~ 10000 Bytes?
    Number of Matches: 170
    How many files are touched (modified) during the last day?
    Number of Matches: 297
    How many files are touched (modified) during the last minute?
    Number of Matches: 2
    iTree('root')
                 └──iTree('SelfElectController.log', data=iTData({'ACCESS': True, 'TYPE': 'FILE', 'EXT': 'log', 'CTIME': 1619959866.8760855, 'ATIME': 1620021514.1237395, 'FULL_PATH': 'c:/ProgramData\\LANDesk\\Log\\SelfElectController.log', 'MTIME': 1620021514.1237395, 'SIZE': 21081}))
                     └──iTree('macompatsvc_VSL9GMPW.log', data=iTData({'ACCESS': True, 'TYPE': 'FILE', 'EXT': 'log', 'CTIME': 1602947283.061818, 'ATIME': 1620021485.8823195, 'FULL_PATH': 'c:/ProgramData\\McAfee\\Agent\\logs\\macompatsvc_VSL9GMPW.log', 'MTIME': 1620021485.8823195, 'SIZE': 960698}))

itertree data models example
----------------------------

`itertree.examples.itree_data_models.py`

During the execution of the module we build an itertree and we fill the `iTree` objects with the data
module and in a second step with the data values. Some exceptions are generated for non matching values
and the formatted string representation of the data model is printed out. The script delivers the following
output:
::
    Run itertree data_model.py example
    We build a tree for the following information:
    signal_catalog
     - signal_category
       - signal
    Each level in the tree contains several attributes that are stored in the data model
    Build iTData structure for signal_catalog:
    iTData({'creation_time': TimeModel(), 'name': StringModel(match=None, max_length=20)})
    Build iTData structure for signal_category
    iTData({'description': StringModel(match=None, max_length=200)})
    Build iTData structure for signal
    iTData({'type': StringModel(match=None, max_length=20), 'raw_data': ArrayModel(item_type=FloatModel(range_interval=iTInterval(lower_limit=-10, upper_limit=10, lower_open=False, upper_open=False), digits=2), max_len=None), 'gain': FloatModel(range_interval=iTInterval(lower_limit=inf, upper_limit=inf, lower_open=True, upper_open=True), digits=4), 'offset': FloatModel(range_interval=iTInterval(lower_limit=inf, upper_limit=inf, lower_open=True, upper_open=True), digits=4), 'io_type': EnumerationModel(enum_iterable_dict={1: 'INPUT', 2: 'OUTPUT'}), 'buffer_size': IntegerModel(range_interval=iTInterval(lower_limit=0, upper_limit=1024, lower_open=False, upper_open=False), representation=2), 'address': IntegerModel(range_interval=iTInterval(lower_limit=0, upper_limit=inf, lower_open=False, upper_open=False), representation=1)})
    Build the tree
    Type check example
    Enter int as name and catch exception
    Exception caught: iDataValueError('Given value of wrong type')
    Enter creation time
    Creation time value: 1649524264.1243489
    Creation time string representation: 2022-04-09 19:11:04.124349
    Create a category
    Enter a to long description and catch exception
    Exception caught: iDataValueError('Given value contains to many characters (max_length=200)')
    Enter a array item out of range
    Exception caught: iDataValueError('Given sub_value (index: 8)-> Value: 10.1 not in range: [-10,10]')
    raw_data_string ['1.00', '2.00', '3.00', '4.00', '5.00', '6.00', '7.00', '8.00', '9.90']
    gain (see number of digits=4!) 1.0230
    Enter invalid enumerate number
    Exception caught: iDataValueError('Value: 3 not in enumeration definition')
    io_type enum string INPUT
    address as hex representation 0xff1234
    Enter invalid buffer_size in update()
    Exception caught: iDataValueError("Item ('buffer_size',-1): Value: -1 not in range: [0,1024]")
    CONSTRUCTED TREE:
    iTree('signal_catalog', data=iTData({'creation_time': TimeModel(value= 1649524264.1243489), 'name': StringModel(value= 'my signal catalog', match=None, max_length=20)}))
         └──iTree('analog signals', data=iTData({'description': StringModel(value= 'Digital signals (switches and state inputs)', match=None, max_length=200)}))
             └──iTree('power voltage', data=iTData({'type': StringModel(value= 'analog input', match=None, max_length=20), 'raw_data': ArrayModel(value= [1, 2, 3, 4, 5, 6, 7, 8, 9.9], item_type=FloatModel(range_interval=iTInterval(lower_limit=-10, upper_limit=10, lower_open=False, upper_open=False), digits=2), max_len=None), 'gain': FloatModel(value= 1.023, range_interval=iTInterval(lower_limit=inf, upper_limit=inf, lower_open=True, upper_open=True), digits=4), 'offset': FloatModel(value= 0.0183, range_interval=iTInterval(lower_limit=inf, upper_limit=inf, lower_open=True, upper_open=True), digits=4), 'io_type': EnumerationModel(value= 1, enum_iterable_dict={1: 'INPUT', 2: 'OUTPUT'}), 'buffer_size': IntegerModel(value= 256, range_interval=iTInterval(lower_limit=0, upper_limit=1024, lower_open=False, upper_open=False), representation=2), 'address': IntegerModel(value= 16716340, range_interval=iTInterval(lower_limit=0, upper_limit=inf, lower_open=False, upper_open=False), representation=1)}))
             └──iTree('power current', data=iTData({'type': 'analog input', 'raw_data': [1, 2, 3, 4], 'gain': 1, 'offset': 0, 'io_type': 1, 'buffer_size': 100, 'address': 123}))
             └──iTree('power control', data=iTData({'type': 'analog output', 'raw_data': ArrayModel(value= [1, 2, 3, 4, 5, 6, 7, 8, 9.9], item_type=FloatModel(range_interval=iTInterval(lower_limit=-10, upper_limit=10, lower_open=False, upper_open=False), digits=2), max_len=None), 'gain': 1.0, 'offset': 0, 'io_type': 2, 'buffer_size': IntegerModel(value= 256, range_interval=iTInterval(lower_limit=0, upper_limit=1024, lower_open=False, upper_open=False), representation=2), 'address': 456}))
         └──iTree('digital signals', data=iTData({'description': StringModel(value= 'Digital signals (switches and state inputs)', match=None, max_length=200)}))
             └──iTree('power switch', data=iTData({'type': 'digital output', 'raw_data': ArrayModel(value= [1, 2, 3, 4, 5, 6, 7, 8, 9.9], item_type=FloatModel(range_interval=iTInterval(lower_limit=-10, upper_limit=10, lower_open=False, upper_open=False), digits=2), max_len=None), 'gain': FloatModel(value= 1.023, range_interval=iTInterval(lower_limit=inf, upper_limit=inf, lower_open=True, upper_open=True), digits=4), 'offset': FloatModel(value= 0.0183, range_interval=iTInterval(lower_limit=inf, upper_limit=inf, lower_open=True, upper_open=True), digits=4), 'io_type': 2, 'buffer_size': IntegerModel(value= 256, range_interval=iTInterval(lower_limit=0, upper_limit=1024, lower_open=False, upper_open=False), representation=2), 'address': 789}))

itertree link example
-------------------------------------
`itertree.examples.itree_link_example1.py`

This example file should show the user how links can be used and how the links are stored.

Please compare the output with the code executed:
::
    `iTree` with linked element but no links loaded:
    iTree('root')
         └──iTree('A')
         └──iTree('B')
         └──iTree('B')
             └──iTree('Ba')
             └──iTree('Bb')
             └──iTree('Bb')
             └──iTree('Bc')
         └──iTreeLink('internal_link', link=iTreeLink(file_path=None, key_path=['/', TagIdx(tag='B', idx=1)]))

    `iTree` with linked element with links loaded:
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
    `iTree` with updated linked element but no reload of the links:

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

    `iTree` with updated linked element and with links reloaded:
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

    `iTree` with linked element and additional local items:
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

    `iTree` with linked element and the overloading local item deleted:
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

    `iTree` load from file with load_links parameter disabled (to make internal structure visible):
    -> See the placeholder element that was added to keep the TagIdx of the local item Bb[1]
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
             └──iTreePlaceHolder('Bb')
             └──iTree('Bb')
                 └──iTree('sublocal')
             └──iTree('new')

    `iTree` load from file with load_links() executed:
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

itertree editor example
-------------------------------------

This program is using Tkinter to create a GUI to create and manipulate `itertree` objects. The program should show
how an 'iTree'-item can be coupled with an item in a tree structure of the GUI (use the coupled_object
functionality of `iTree`). THe editor allows diffrent manipulations on the tree structure from renaming and ordering to
manipulations of the data (add some models, etc) and the creation of additional items ( `iTree` / `iTreeLink` ,
`iTreeReadOnly` ).
The context menus are also created via a defintions based on `iTree` objects.
The GUI code example is splittet in an controller and the GUI itself. This allows better testing of the
functionalities if required and brings a lot more advantages. But we should not dive in the discussions of GUI
related architecture here, as long we have here just another example for the usage of itertree.

.. note:: Please do not report issues related to the editor on GIT. We know that a lot of corner-cases are not covered
and that the editor functionalities are incomplete. It's just an example and not an application we provide here.


itertree performance example
-------------------------------------

There are two performance tests found under examples. They are not created for learning proposes furthermore the user
can see how we have run some performance test against other solutions that
targeting in same direction as the itertree package. For more details have a look on the
:ref:`Comparison_Chapter` of the documentation.

itertree profiler example
-------------------------------------

The example contains one of the profiling we did to optimize the `iTree` class for the main operations.

Based on those analysis you can see which operations needs the most calculation time. The output looks like:
::
    Running on itertree version: 0.8.0
             5400015 function calls (5300015 primitive calls) in 4.132 seconds

       Ordered by: standard name

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000    4.132    4.132 <string>:1(<module>)
       700003    0.520    0.000    0.520    0.000 itree_data.py:203(__init__)
       400001    0.280    0.000    0.456    0.000 itree_data.py:220(__copy__)
       100000    0.180    0.000    0.228    0.000 itree_main.py:1087(insert)
       100000    0.130    0.000    0.187    0.000 itree_main.py:1127(append)
            1    0.000    0.000    0.897    0.897 itree_main.py:1178(extend)
            1    0.000    0.000    0.000    0.000 itree_main.py:1434(iter_children)
       500003    0.766    0.000    1.780    0.000 itree_main.py:148(__init__)
    200003/100003    0.463    0.000    1.237    0.000 itree_main.py:2073(_load_subtree)
       200000    0.088    0.000    0.121    0.000 itree_main.py:255(__getitem__)
       100000    0.084    0.000    0.124    0.000 itree_main.py:288(__delitem__)
            1    0.001    0.001    1.062    1.062 itree_main.py:373(__mul__)
            1    0.028    0.028    0.916    0.916 itree_main.py:385(<listcomp>)
            1    0.000    0.000    0.000    0.000 itree_main.py:409(__iter__)
       200000    0.760    0.000    1.607    0.000 itree_main.py:957(__copy__)
       200000    0.024    0.000    0.024    0.000 itree_main.py:972(<listcomp>)
            1    0.393    0.393    4.132    4.132 itree_profile.py:41(performance_dt)
            1    0.086    0.086    0.402    0.402 itree_profile.py:51(<listcomp>)
            1    0.000    0.000    4.132    4.132 {built-in method builtins.exec}
       200001    0.017    0.000    0.017    0.000 {built-in method builtins.isinstance}
       100000    0.009    0.000    0.009    0.000 {built-in method builtins.iter}
       100000    0.008    0.000    0.008    0.000 {built-in method builtins.len}
       400001    0.036    0.000    0.036    0.000 {function iTData.copy at 0x000001F206B4DA60}
       100000    0.013    0.000    0.013    0.000 {function `iTree`.__getitem__ at 0x000001F206BBC940}
       699998    0.069    0.000    0.069    0.000 {function `iTree`.append at 0x000001F206BC9CA0}
       100000    0.026    0.000    0.026    0.000 {function `iTree`.insert at 0x000001F206BC9C10}
       100000    0.032    0.000    0.032    0.000 {function `iTree`.pop at 0x000001F206BC9EE0}
       499997    0.077    0.000    0.077    0.000 {method '__contains__' of 'dict' objects}
       399998    0.040    0.000    0.040    0.000 {method '__getitem__' of 'dict' objects}
            1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}

and for second profiling script:
::
             6934372 function calls in 3.239 seconds

       Ordered by: standard name

       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000    3.239    3.239 <string>:1(<module>)
      1050804    0.215    0.000    2.915    0.000 itree_helpers.py:56(accu_iterator)
       535806    1.338    0.000    2.520    0.000 itree_main.py:1504(find_all)
       525402    0.229    0.000    2.700    0.000 itree_main.py:1688(<lambda>)
       535806    0.312    0.000    0.446    0.000 itree_main.py:2133(__extract_first_iter_items)
       535806    0.212    0.000    0.323    0.000 itree_main.py:2163(__build_find_all_result)
       535806    0.290    0.000    0.349    0.000 itree_main.py:255(__getitem__)
            1    0.206    0.206    3.239    3.239 itree_profile2.py:77(performance_it_find_all_by_idx)
            1    0.000    0.000    3.239    3.239 {built-in method builtins.exec}
       535806    0.081    0.000    0.081    0.000 {built-in method builtins.hasattr}
       535806    0.052    0.000    0.052    0.000 {built-in method builtins.isinstance}
       535806    0.060    0.000    0.060    0.000 {built-in method builtins.iter}
       535806    0.053    0.000    0.053    0.000 {built-in method builtins.len}
        10404    0.068    0.000    2.937    0.000 {built-in method builtins.next}
       525402    0.064    0.000    0.064    0.000 {built-in method from_iterable}
       535806    0.059    0.000    0.059    0.000 {function `iTree`.__getitem__ at 0x0000029A579A2AF0}
          102    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
            1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}

