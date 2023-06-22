.. _changelog:

Changelog
=============

************************************
Version 1.0.0
************************************

Full released

After the whole functionality was implemented in the previous versions we made a review of the interfaces
of the `iTree` class and we came to the decision that we should align it more with the standard interfaces in python
(especially related to list and dict standard methods).
Finally we updated a lot of methods to a more clearer naming and a more standardized behavior.
We apologize that the changes leads into adaptions of already existing implementations of the users. But we hope that
you understand after some tries that the new interface is much clearer and easier to use.

The functionalities related to the nested (in-depth) structure are now moved in an internal helper-class which is
reachable via `itree.deep`.

Furthermore we saw in practice that item access is most often made via absolute index or tag,index pair (key).
Therefore we changed the paradigm of targeting those kind of targets easier and with higher priority. In case of
conflicts with the index or tag-index pair the user must give the lower prioritized family-tags in a specific way.
The number of possible targets is increased especially a level-filter is now available too.
As a side effect the limitation related to integer keys we had is no more there. Integers can now be used as tags too.
In general with this release any hashable object can be used as tag.

In case the user instance an `iTree`-object without a tag or without a value. We have new default values
( `NoTag` and `NoValue`) which are used automatically in this case. This is made implicit and allows the
build of very simple trees without any overhead anymore. The append of values to a tree with implicit
instancing the related `iTree`-object is made based on the `NoTag` definition available.

The equal check `==` operator is now checking for same content and no more on the identical instance
(as it is in `list`s too).
For identical instance checks the user must use the `is` build-in statement. But please check
on the side effects of this change (read here the changed behavior of the `index()` command which is now the
same like in lists (first match is delivered).

We deleted the find-functions from the object because we first thought they were too confusing and second the filter
possibilities in all the methods are largely extended. We do not see any case (from old find functions)
that can not be covered by the
method-parameter-set we have. The filter functions are also simplified in a way that any filter-method can be
used now, we do not need any more a special filter-object to be used.

Finally we uncoupled a lot of functionalities, especially the usage of the data property is changed here.
`iTree` can now be used without any limitations related to the stored data. We do not expect here any more a
`dict`-like-object. The provided data models can still be used if required but there is no more coupling anymore. To
align with the standard  `dict`-class we renamed the related attribute from `data` to `value`.

As a side effect the performance of the `ìTree` could be improved again. We eliminated the different classes of
`ìTree` related to read_only behavior. We now use a set of methods and flags. The advantage is that the
objects can now change their behavior without changing the instance of the original object (in-place-operation).

`iTree` objects can now be pickled (if the trees are deeper than 200 levels RecursionError will be raised
(std. recursion-limit)). The serializers and rendering is updated too.

The MIT licence was extended by a "human protect patch".

To symbolize the stability and also the final fix of the interface we decided to create the first full released version.
The testsuite is largely expanded for this step.

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

Access to the deeper structures improved (find_all, new getitem_deep() and max_depth_down() method.

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
