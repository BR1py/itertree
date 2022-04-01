.. _examples:

itertree examples package
================

**************
Usage examples
**************

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


Modules
----------

itertree usage example
----------------------
.. automodule::     itertree.examples.itree_usage_example1
    :members:
    :undoc-members:
    :show-inheritance:

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

.. automodule::     itertree.examples.itree_data_models
    :members:
    :undoc-members:
    :show-inheritance:

During the execution of the module we build an itertree and we fill the iTree objects with the data module and in a second step with the data values. Some exceptions are generated for non matching values and the formatted string representation of the data model is printed out. The script delivers the fllwing output:
::
    Run itertree data_model.py example
    We build a tree for the following information:
    signal_catalog
     - signal_category
       - signal
    Each level in the tree contains several attributes that are stored in the data model
    Build iTData structure for signal_catalog:
    iTData({'name': StringModel(match=None, max_length=20), 'creation_time': TimeModel()})
    Build iTData structure for signal_category
    iTData({'description': StringModel(match=None, max_length=200)})
    Build iTData structure for signal
    iTData({'buffer_size': IntegerModel(range_interval=Interval().from_string([0.000,1024.000]), representation=2), 'offset': FloatModel(range_interval=Interval().from_string((-inf,+inf)), digits=4), 'io_type': EnumerationModel(enum_iterable_dict={1: 'INPUT', 2: 'OUTPUT'}), 'gain': FloatModel(range_interval=Interval().from_string((-inf,+inf)), digits=4), 'addresse': IntegerModel(range_interval=Interval().from_string([0.000,+inf]), representation=1), 'type': StringModel(match=None, max_length=20), 'raw_data': ArrayModel(item_type=FloatModel(range_interval=Interval().from_string([-10.000,10.000]), digits=2), max_len=None)})
    Build the tree
    Type check example
    Enter int as name and catch exception
    Exception catched: TypeError('Given value of wrong type',)
    Enter creation time
    Creation time value: 1619033584.3464892
    Creation time string representation: 2021-04-21 21:33:04.346489
    Create a category
    Enter a to long description and catch exception
    Exception catched: TypeError('Given value contains to many characters (max_length=200)',)
    Enter a array item out of range
    Exception catched: TypeError('Given sub_value (index: 8)-> Value: 10.1 not in range: [-10.000,10.000]',)
    raw_data_string ['1.00', '2.00', '3.00', '4.00', '5.00', '6.00', '7.00', '8.00', '9.90']
    gain (see number of digits=4!) 1.0230
    Enter invalid enumerate number
    Exception catched: TypeError('Value: 3 not in enumeration definition',)
    io_type enum string INPUT
    addresse as hex represenation 0xff1234
    Enter invalid buffersize in update()
    Exception catched: TypeError("Item ('buffer_size',-1): Value: -1 not in range: [0.000,1024.000]",)
    CONSTRUCTED TREE:
    iTree('signal_catalog', data=iTData({'name': StringModel(value= 'my signal catalog', match=None, max_length=20), 'creation_time': TimeModel(value= 1619033584.3464892)}))
     └──iTree('analog signals', data=iTData({'description': StringModel(value= 'Digital signals (switches and state inputs)', match=None, max_length=200)}))
         └──iTree('power voltage', data=iTData({'buffer_size': IntegerModel(value= 100, range_interval=Interval().from_string([0.000,1024.000]), representation=2), 'offset': FloatModel(value= 0, range_interval=Interval().from_string((-inf,+inf)), digits=4), 'io_type': EnumerationModel(value= 1, enum_iterable_dict={1: 'INPUT', 2: 'OUTPUT'}), 'gain': FloatModel(value= 1, range_interval=Interval().from_string((-inf,+inf)), digits=4), 'addresse': IntegerModel(value= 2020963, range_interval=Interval().from_string([0.000,+inf]), representation=1), 'type': StringModel(value= 'digital input', match=None, max_length=20), 'raw_data': ArrayModel(value= [1, 2, 3, 4], item_type=FloatModel(range_interval=Interval().from_string([-10.000,10.000]), digits=2), max_len=None)}))
         └──iTree('power current', data=iTData({'buffer_size': IntegerModel(value= 100, range_interval=Interval().from_string([0.000,1024.000]), representation=2), 'offset': FloatModel(value= 0, range_interval=Interval().from_string((-inf,+inf)), digits=4), 'io_type': EnumerationModel(value= 1, enum_iterable_dict={1: 'INPUT', 2: 'OUTPUT'}), 'gain': FloatModel(value= 1, range_interval=Interval().from_string((-inf,+inf)), digits=4), 'addresse': IntegerModel(value= 2020963, range_interval=Interval().from_string([0.000,+inf]), representation=1), 'type': StringModel(value= 'digital input', match=None, max_length=20), 'raw_data': ArrayModel(value= [1, 2, 3, 4], item_type=FloatModel(range_interval=Interval().from_string([-10.000,10.000]), digits=2), max_len=None)}))
         └──iTree('power control', data=iTData({'buffer_size': IntegerModel(value= 100, range_interval=Interval().from_string([0.000,1024.000]), representation=2), 'offset': FloatModel(value= 0, range_interval=Interval().from_string((-inf,+inf)), digits=4), 'io_type': EnumerationModel(value= 1, enum_iterable_dict={1: 'INPUT', 2: 'OUTPUT'}), 'gain': FloatModel(value= 1, range_interval=Interval().from_string((-inf,+inf)), digits=4), 'addresse': IntegerModel(value= 2020963, range_interval=Interval().from_string([0.000,+inf]), representation=1), 'type': StringModel(value= 'digital input', match=None, max_length=20), 'raw_data': ArrayModel(value= [1, 2, 3, 4], item_type=FloatModel(range_interval=Interval().from_string([-10.000,10.000]), digits=2), max_len=None)}))
     └──iTree('digital signals', data=iTData({'description': StringModel(value= 'Digital signals (switches and state inputs)', match=None, max_length=200)}))
         └──iTree('power switch', data=iTData({'buffer_size': IntegerModel(value= 100, range_interval=Interval().from_string([0.000,1024.000]), representation=2), 'offset': FloatModel(value= 0, range_interval=Interval().from_string((-inf,+inf)), digits=4), 'io_type': EnumerationModel(value= 1, enum_iterable_dict={1: 'INPUT', 2: 'OUTPUT'}), 'gain': FloatModel(value= 1, range_interval=Interval().from_string((-inf,+inf)), digits=4), 'addresse': IntegerModel(value= 2020963, range_interval=Interval().from_string([0.000,+inf]), representation=1), 'type': StringModel(value= 'digital input', match=None, max_length=20), 'raw_data': ArrayModel(value= [1, 2, 3, 4], item_type=FloatModel(range_interval=Interval().from_string([-10.000,10.000]), digits=2), max_len=None)}))

itertree performance example
-------------------------------------

There are two performance tests found under examples. They are not created for learning proposes furthermore the user can see how we have run some performance test against other solutions that targeting in same direction as the itertree package.

itertree profiler example
-------------------------------------

The example contains one of the profiling we did to optimize the iTree class for the main operations.