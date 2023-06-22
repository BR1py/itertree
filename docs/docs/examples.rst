.. _examples:

itertree examples
=================

**************
Usage examples
**************

In the example section you can find two example files itree_usage_example.py and itree_data_examples.py which explain how itertree package might be used.

itree_usage_example1.py
+++++++++++++++++++++++

In this example we build a tree that contains the continents and the related countries insite.
Additionally we add some country related data. Finally we do some analysis and filter the tree for specific content.

After executing the script the output might look like this:

::

    iTree('root')
     > iTree('Africa', value={'surface': 30200000, 'inhabitants': 1257000000})
     .  > iTree('Ghana', value={'surface': 238537, 'inhabitants': 30950000})
     .  > iTree('Nigeria', value={'surface': 1267000, 'inhabitants': 23300000})
     > iTree('Asia', value={'surface': 44600000, 'inhabitants': 4000000000})
     .  > iTree('China', value={'surface': 9596961, 'inhabitants': 1411780000})
     .  > iTree('India', value={'surface': 3287263, 'inhabitants': 1380004000})
     > iTree('America', value={'surface': 42549000, 'inhabitants': 1009000000})
     .  > iTree('Canada', value={'surface': 9984670, 'inhabitants': 38008005})
     .  > iTree('Mexico', value={'surface': 1972550, 'inhabitants': 127600000})
     > iTree('Australia&Oceania', value={'surface': 8600000, 'inhabitants': 36000000})
     .  > iTree('Australia', value={'surface': 7688287, 'inhabitants': 25700000})
     .  > iTree('New Zealand', value={'surface': 269652, 'inhabitants': 4900000})
     > iTree('Europe', value={'surface': 10523000, 'inhabitants': 746000000})
     .  > iTree('France', value={'surface': 632733, 'inhabitants': 67400000})
     .  > iTree('Finland', value={'surface': 338465, 'inhabitants': 5536146})
     > iTree('Antarctica', value={'surface': 14000000, 'inhabitants': 1100})
    Filtered items; inhabitants in range: [0,20000000]
    iTree('New Zealand', value={'surface': 269652, 'inhabitants': 4900000})
    iTree('Finland', value={'surface': 338465, 'inhabitants': 5536146})
    iTree('Antarctica', value={'surface': 14000000, 'inhabitants': 1100})
    Filter2 items (we expect Antarctica does not match anymore!):
    iTree('New Zealand', value={'surface': 269652, 'inhabitants': 4900000})
    iTree('Finland', value={'surface': 338465, 'inhabitants': 5536146})


itree_usage_example2.py
+++++++++++++++++++++++

In this code we build a larger `iTree` by reading a part of the filesystem into a tree.
Again we do some analysis related to the read in files and folder.

After executing the script the output might look like this:

::

    We read a part of the filesystem ('C:\\Tools\\Python\\Python39') into an itertree
    Number of items read in 19878
    The load in tree has a depth of 11
    How many files are bigger then 1000000 Bytes?
    Number of Matches: 2
    How many files are in size 9000 ~ 10000 Bytes?
    Number of Matches: 6
    How many files are touched (modified) during the last day?
    Number of Matches: 0
    How many files are touched (modified) during the last minute?
    Number of Matches: 0

itree_data_models.py
+++++++++++++++++++++++

This examples focuses on the value stored in the `iTree`-object. We play with data-moddels and show how the user can
use the models to determine the values stored in the related `iTree`-object.

We do not use any external packages in the examples but the user may also use the more advanced Pydantic package
as a good option to define very powerful data models.

About the data models one can say that the data model can be used with the focus of checking and
formatting of the stored data:

* check data type
* check value range (give intervals, limits)
* do we have an array of the data type and what is max length
* for strings we can use matches or regex checks of values
* for formatting think about numerical values (integer dec/hex/bin representation) or float number of digits to round to
* We can also define more abstract datatypes like keylists or enumerated keys.

In the file you can see some examples of how this data models can be defined and used.

After executing the script the output might look like this:

::

    Run itertree data_model.py example
    Each iTree item will contain different types of data models for the values
    Build the tree
    Append model items and enter values

    Enter a string in the string model, iTree nows that a model is in value and takes over the given value implicit into the model
    Appended item: iTree('str_len20_item', value=iTStrModel(<class 'itertree.itree_helpers.NoValue'>, None, (20,)))
    Content stored in item value: iTStrModel('Hello world', None, (20,))
    Content delivered via get_value(): Hello world
    Enter a string in the string model which is to long
    Exception raised (and handled):
    Given value shape=(55,) (position=0) too large for model (shape=(20))

    Enter a string in the string model, iTree nows that a model is in value and takes over the given value implicit into the model
    Appended item: iTree('ascii_str_len40_item', value=iTASCIIStrModel(<class 'itertree.itree_helpers.NoValue'>, None, (40,)))
    Content stored in item value: iTASCIIStrModel('Hello world', None, (40,))
    Content delivered via get_value(): Hello world
    Enter a string in the ASCII string model which is to long
    Exception raised (and handled):
    Given value shape=(440,) (position=0) too large for model (shape=(40))
    Enter a string in the ASCII string model which contains non ascii characters
    Exception raised (and handled):
    Non ASCII character '°' found in value (position=0) -> not accepted by model

    Enter len()=2 floats list
    Appended item: iTree('float_array2_item', value=iTFloatModel(<class 'itertree.itree_helpers.NoValue'>, None, (2,), None, '{:.2f}'))
    Content stored in item value: iTFloatModel([1.3, 6.4], None, (2,), None, '{:.2f}')
    Content delivered via get_value(): [1.3, 6.4]
    Enter a numeric string in the float model
    Content delivered via get_value(): [1.0, 3.0]
    Content delivered via get_value(): [1.3, 3.1]
    Enter a single item list in the float array model
    Content delivered via get_value(): [1.1]
    Enter a string in the float model
    Exception raised (and handled):
    could not convert string to float: 'ABC'
    Enter a single float in the float array model
    Exception raised (and handled):
    Given value shape=() too small for model (shape=(2)) ->expecting more dimensions
    Enter a triple item list in the float array model
    Exception raised (and handled):
    Given value shape=(3,) (position=0) too large for model (shape=(2))

    Enter single float with range
    Appended item: iTree('float_single_item', value=iTFloatModel(<class 'itertree.itree_helpers.NoValue'>, None, (), mSetInterval(mSetItem(-10, True), mSetItem(10, True)), '{:.4e}'))
    Content stored in item value: iTFloatModel(5.5, None, (), mSetInterval(mSetItem(-10, True), mSetItem(10, True)), '{:.4e}')
    Content delivered via get_value(): 5.5
    Enter a numeric string in the float model
    Content delivered via get_value(): -4.4
    Enter a string in the float model
    Exception raised (and handled):
    could not convert string to float: 'ABC'
    Enter a float list in the float model
    Exception raised (and handled):
    Given value shape=(2,) has more dimensions as model accepts (model-shape=()
    Enter a float out of range upper limit in the float model
    Exception raised (and handled):
    Given value does not match to given filter_method (out of range)
    Enter a float out of range lower limit in the float model
    Exception raised (and handled):
    Given value does not match to given filter_method (out of range)

    Enter timestamp
    Appended item: iTree('time_stamp_item', value=TimeModel(datetime.datetime(1970, 1, 1, 1, 0)))
    Content stored in item value: TimeModel(datetime.datetime(2023, 6, 15, 22, 33, 48, 451045))
    Content delivered via get_value(): 2023-06-15 22:33:48.451045
    Content stored in item value: TimeModel(datetime.datetime(2023, 6, 15, 22, 33, 48, 451045))
    Content delivered via get_value(): 2023-06-15 22:33:48.451045
    Enter a string in the time model
    Exception raised (and handled):
    Given value 'ABC' could not be converted in internal datetime object
    Enter a negative float in the time model
    Exception raised (and handled):
    Given value -100 could not be converted in internal datetime object


itree_link_example1.py
-------------------------------------

This example file should show the user how links can be used and how the links are stored. THe user can also
see how specific items are converted to local ones. Especially take a look on when the `load_links()` is
called and which effect it has if the method is not called or called.

Please compare the output with the code executed:

::

    iTree with linked element but no links loaded:
    iTree('root')
     > iTree('A')
     > iTree('B')
     > iTree('B')
     .  > iTree('Ba')
     .  > iTree('Bb')
     .  > iTree('Bb')
     .  > iTree('Bc')
     > iTree('internal_link', link=iTLink(None,[('B', 1)]), flags=0b100000)
    None
    iTree with linked element with links loaded
    iTree loaded links:

    iTree('root')
     > iTree('A')
     > iTree('B')
     > iTree('B')
     .  > iTree('Ba')
     .  > iTree('Bb')
     .  > iTree('Bb')
     .  > iTree('Bc')
     > iTree('internal_link', link=iTLink(None,[('B', 1)]), flags=0b100100)
     .  >>iTree('Ba')
     .  >>iTree('Bb')
     .  >>iTree('Bb')
     .  >>iTree('Bc')
    iTree with updated linked element but no reload of the links:

    iTree('root')
     > iTree('A')
     > iTree('B')
     > iTree('B')
     .  > iTree('Ba')
     .  > iTree('Bb')
     .  > iTree('Bb')
     .  > iTree('Bc')
     .  > iTree('B_post_append')
     > iTree('internal_link', link=iTLink(None,[('B', 1)]), flags=0b100100)
     .  >>iTree('Ba')
     .  >>iTree('Bb')
     .  >>iTree('Bb')
     .  >>iTree('Bc')
    iTree with linked element with links loaded
    iTree with updated linked element and with links reloaded:
    iTree('root')
     > iTree('A')
     > iTree('B')
     > iTree('B')
     .  > iTree('Ba')
     .  > iTree('Bb')
     .  > iTree('Bb')
     .  > iTree('Bc')
     .  > iTree('B_post_append')
     > iTree('internal_link', link=iTLink(None,[('B', 1)]), flags=0b100100)
     .  >>iTree('Ba')
     .  >>iTree('Bb')
     .  >>iTree('Bb')
     .  >>iTree('Bc')
     .  >>iTree('B_post_append')
    iTree with linked element and additional local items:
    iTree('root')
     > iTree('A')
     > iTree('B')
     > iTree('B')
     .  > iTree('Ba')
     .  > iTree('Bb')
     .  > iTree('Bb')
     .  > iTree('Bc')
     .  > iTree('B_post_append')
     > iTree('internal_link', link=iTLink(None,[('B', 1)]), flags=0b100100)
     .  >>iTree('Ba')
     .  >>iTree('Bb')
     .  > iTree('Bb', value='myvalue')
     .  .  > iTree('sublocal')
     .  >>iTree('Bc')
     .  >>iTree('B_post_append')
     .  > iTree('new')
    iTree with linked element and the overloading local item deleted:
    iTree('root')
     > iTree('A')
     > iTree('B')
     > iTree('B')
     .  > iTree('Ba')
     .  > iTree('Bb')
     .  > iTree('Bb')
     .  > iTree('Bc')
     .  > iTree('B_post_append')
     > iTree('internal_link', link=iTLink(None,[('B', 1)]), flags=0b100100)
     .  >>iTree('Ba')
     .  >>iTree('Bb')
     .  >>iTree('Bb')
     .  >>iTree('Bc')
     .  >>iTree('B_post_append')
     .  > iTree('new')
    iTree load from file with load_links parameter disabled (to make internal structure visible):
    -> See the placeholder element that was added to keep the key of the local item Bb[1] (flags==0b10000)
    iTree('root')
     > iTree('A')
     > iTree('B')
     > iTree('B')
     .  > iTree('Ba')
     .  > iTree('Bb')
     .  > iTree('Bb')
     .  > iTree('Bc')
     .  > iTree('B_post_append')
     > iTree('internal_link', link=iTLink(None,[('B', 1)]), flags=0b100000)
     .  >>iTree('Ba')
     .  > iTree('Bb', value=0, flags=0b10000)
     .  > iTree('Bb', value='myvalue')
     .  .  > iTree('sublocal')
     .  > iTree('Bc', value=0, flags=0b10000)
     .  >>iTree('B_post_append')
     .  > iTree('new')
    iTree load from file with load_links() executed:
    iTree('root')
     > iTree('A')
     > iTree('B')
     > iTree('B')
     .  > iTree('Ba')
     .  > iTree('Bb')
     .  > iTree('Bb')
     .  > iTree('Bc')
     .  > iTree('B_post_append')
     > iTree('internal_link', link=iTLink(None,[('B', 1)]), flags=0b100100)
     .  >>iTree('Ba')
     .  >>iTree('Bb')
     .  > iTree('Bb', value='myvalue')
     .  .  > iTree('sublocal')
     .  >>iTree('Bc')
     .  >>iTree('B_post_append')
     .  > iTree('new')

performance_analysis.exec_performance
--------------------------------------

In this example we run performance tests related different functionalities with diffrent types of packages targeting
tree functionalities.

For the results and output please have a look in the chapter
`Comparison of the iTree object with lists and dicts`_ .

If the user likes to run the performance test on his own maschine he must ensure that the targeted packeges installed.
The user may also change the setup related to the number of items or the depth of the tree
which is used for comparison. The parameters can be found in the `__init__()`-method of test classes defined.

