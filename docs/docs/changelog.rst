.. _changelog:

Changelog
=============

************************************
Version 0.8.2
************************************

We reworked the itertree data module so that iData class behaves much better like a dict. All overloaded methods
are improved to match the dict interface. Also `iTDataModel` is changed and is now a class that must be overloaded.

The value `validator()` raises now an `iTDataValueError` or `iTDataTypeError` exception directly. This behavior match
from our point of view much better to the normal Python behavior compaired with the old style were we delivered a
tuple containing the error information.

->Please consider this interface change in your code.

Second we focused for this release on the extension of functionalities related to linked iTrees:

    * create internal links (reference to another tree part of the current tree)
    * `localize` and `cover` of linked elements
    * an example file related to the usage of links is available now

Beside this we started to extend the unit testing for the package and we fixed a lot of smaller bugs.

Because of some internal simplifications in `iTree` class the overall performance is again improved a bit.

The documentation was reviewed and improved.

No new features are planned at the moment and we just wait to complete the unit test suite, before we will do an
official 1.0.0 release.

Still Beta SW -> but release candidate!


************************************
Version 0.7.3
************************************

Bugfixes in repr() and render()

Extended examples

Still Beta SW -> but release candidate!

************************************
Version 0.7.2
************************************

Improved Interval class (dynamic limits in all levels)

Adapted some tests and the documentation

Still Beta SW -> but release candidate!

************************************
Version 0.7.1
************************************

Bigger bugfix on 0.7.0 which was really not well tested!

Still Beta SW -> but release candidate!

************************************
Version 0.7.0
************************************

Recursive functions are rewritten to use an iterative approach (recursion limit exception should be avoided)

Access to the deeper structures improved (find_all, new get_deep() and max_depth_down() method.

New `iTree` classes for Linked, Temporary or ReadOnly items

performance improved again

Examples regarding data models added

Still Beta SW -> but release candidate!

************************************
Version 0.6.0
************************************

Improved interface and performance

Documentation is setup

Testing is improved

Examples still missing

Beta SW!


************************************
Version 0.5.0
************************************

First released version

Contains just the base functionalities of itertree. Interface is is finished by 80%

Documentation and examples are missing

testing is not finished yet.

Beta SW!