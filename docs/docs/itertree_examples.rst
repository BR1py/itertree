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

iterree profiler example
-------------------------------------

.. automodule::     itertree.examples.dt_profile
    :members:
    :undoc-members:
    :show-inheritance:
