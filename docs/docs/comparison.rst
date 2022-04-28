.. _Comparison_Chapter:


Comparison
==========

In this chapter we compare the itertree package with other packages which are targeting in the same direction.

Each package is develop with a specific focus and therefore a comparison is always a bit misleading. Finally the
comparison remarks you find in this chapter are no not at all a judgement of the other packages. Especially the
performance tests can also be misleading because we may not have utilized the other packages in the right way.

In this chapter we compare `iTree` also with the standard types like dict and lists. Additionally we have a
look on xml.ElementTree, sorted_dict (from sorted containers) and the anytree package.

In the design paradigms of the itertree package can be summarized by the following topics. They will be highlighted
and compared:

1. We can add any type of tag in the `iTree` as long as it is hashable and we can add the same tag multiple times in
the `iTree`. Some of the comparable package support only string-type tags (like anytree or xml.ElementTree). Other
allow only unique tags like the keys in dicts (using same key will overwrite the already existing tag in this case).

2. In `iTree` the item access via index and tag (or TagIdx) is possible. As you will see in the performance tests
later many of the other packages are focus on one type of access only and the second type is then much slower
(optimized for key or optimized index access only). It is part of the design paradigm related to the classes
(E.g. it's quite clear that index access on huge dicts or key access in huge list will be very slow).
But even the search mechanisms in specialized packages are very often really slow (compared to iTree).

3. The access of multiple items via index list is possible `my_itree[[1,4,5,6,9]]` will deliver the indexed items
in an iterator (The access via index-list is in most packages not supported).

4. As in the introduction already explained the results when running filter queries in `iTree` will be delivered
very quick because we delivering always iterators. But this might make the coding from the point of usage sometimes
a bit more complicate because if you need index access to a specific element you must cast the iterator
in a list (by `list(my_iterator)`) or you use
or use `itertools.is_slice()` operation. It's always recommended to address the target items via the available iTree
methods (`find()`, `find_all()` or even `iTree[my_identifier]`) directly. You can also use the item_filter and
matches to reach your results as good as possible.

5. We can link multiple source files into one `iTree` object or even create link inside the tree itself, also we can
cover linked items by local items. Most of the packages do not support links and we do not know any other package
supporting item covering (overloading). Even the load and storage into files is most often not supported especially
considering the data object stored in the item must be serialized in this case too.
(Users can always create serializers but this can be sometimes very difficult considering all data-types
stored in a tree). `iTree` delivers out of the box the possibility to store several data-types into a JSON file
(e.g. also numpy arrays if needed).

6. At least the data in the `iTree` objects can be combined with a data model that checks that the give data values
matching with the ones expected by the data model. The defined data models allows much more then just a check of the
data type. E.g. one can also define ranges or intervals in which an integer value must fit in. This functionality
makes `iTree` objects very attractive for the storage of certain configuration data.

Finally we must also mention that sorting of items is not in focus of this package.

Under examples you can find the "itree_performance.py" file which contains a short performance test regarding other
comparable packages. The following results are create under Python 3.9 and blist package installed. Please feel
free to adapt the first line regarding the tree size and the number of repetitions when you run your own tests.
In case no blist package is installed you may skip the insert operation of `iTree` which is slowed down a lot.

The measured times given are always relative to one operation.

The tests are only performed in case the needed package is available in the local installation
if the module is not found the test is skipped. The user can find some experimental not published packages
imported in the code, this should be ignored.

Running the test on a tree with 5000 items delivers the following result on my PC under python 3.9.
::
    >>>python iter_performance.py
    We run for treesizes: 5000 with 4 repetitions
    Python:  3.9.2 (tags/v3.9.2:1a79785, Feb 19 2021, 13:44:55) [MSC v.1928 64 bit (AMD64)]
    blist package is available and used
    itertree version: 0.8.0
    A relative values >1 related to `iTree` means the other object is faster
    (relative values <1 means `iTree` is faster)
    Exectime time itertree build: 0.014122499999999996
    Exectime time itertree build: with subtree list comprehension: 0.011322650000000004
    Exectime time itertree build (with insert): 0.014225149999999992
    Exectime time itertree tag access: 0.0018194249999999995
    Exectime time itertree tag index access: 0.0037113499999999883
    Exectime time itertree tag index tuple access: 0.0025402999999999953
    Exectime time itertree index access: 0.0018937750000000003
    Exectime time itertree convert iter_all iterator to list: 0.0024619749999999913
    Exectime time itertree save to file: 0.018669550000000007
    Exectime time itertree load from file: 0.030752224999999994
    Loaded `iTree` is equal: True
    -- Standard classes -----------------------------------
    Exectime time dict build: 0.0013473249999997883 ~ 10.482x faster as iTree
    Exectime time dict key access: 0.0010821000000000858 ~ 1.681x faster as iTree
    Exectime time dict index access: 0.1515084499999999 ~ 0.012x faster as iTree
    Exectime time list build (via comprehension): 0.0007731250000000411 ~ 14.645x faster as iTree
    Exectime time list build (via append): 0.0010298500000001098 ~ 13.713x faster as iTree
    Exectime time list build (via insert): 0.007580025000000212 ~ 1.877x faster as iTree
    Exectime time list index access: 0.00014650000000004937 ~ 12.927x faster as iTree
    Exectime time list key access: 0.15582805 ~ 0.012x faster as iTree
    Exectime time OrderedDict build: 0.0010928749999998821 ~ 12.922x faster as iTree
    Exectime time OrderedDict key access: 0.0007975499999999247 ~ 0.002x faster as iTree
    Exectime time deque build (append): 0.0009357999999999311 ~ 15.091x faster as iTree
    Exectime time deque build (insert): 0.0012067749999999933 ~ 11.788x faster as iTree
    Exectime time deque index access: 0.00027527499999990823 ~ 6.880x faster as iTree
    -- SortedDict ---------------------------------
    Exectime time SortedDict build: 0.03194094999999986 ~ 0.442x faster as iTree
    Exectime time SortedDict key access: 0.0011537749999999125 ~ 1.577x faster as iTree
    Exectime time SortedDict index access: 0.005190625000000004 ~ 0.365x faster as iTree
    -- xml ElementTree ---------------------------------
    Exectime time xml ElementTree build: 0.0017907750000001332 ~ 7.886x faster as iTree
    Exectime time xml ElementTree key access: 0.16554792499999982 ~ 0.011x faster as iTree
    Exectime time xml ElementTree index access: 0.00016492499999998245 ~ 11.032x faster as iTree
    -- anytree ---------------------------------
    Exectime time Anytree build: 0.6392311500000001 ~ 0.022x faster as iTree
    Exectime time Anytree key access (no cache): 20.658143574999997 ~ 0.000088x faster as iTree
    Exectime time Anytree index access: 0.06119849999999971 ~ 0.031x faster as iTree


Running the test on a tree with a depth of 150 levels and 22500 items delivers the following result on my PC under python 3.5.
::
    >>>python iter_performance2.py
    We run for deep tree sizes: depth of 150 with 22500 items and 4 repetitions
    Python:  3.9.2 (tags/v3.9.2:1a79785, Feb 19 2021, 13:44:55) [MSC v.1928 64 bit (AMD64)]
    blist package is available and used
    itertree version: 0.8.0
    A relative values >1 related to `iTree` means the other object is faster
    (relative values <1 means `iTree` is faster)
    Exectime time itertree build append: 0.053359225
    Exectime time itertree build (with insert): 0.06587992499999999
    Max tree depth 150
    Exectime time itertree get max_depth_down~iter_all(): 0.0105537
    Exectime time itertree get deep indexes access (all items iterated): 0.5943447749999999
    Exectime time itertree get find_all by indexes access (all items iterated): 4.701620525
    Exectime time itertree find all by deep tag list (one deep search last item): 0.08802357500000024
    -- Standard classes -----------------------------------
    Exectime time dict build: 0.007973800000000253 ~ 6.692x faster as iTree
    Exectime time dict key access: 0.11559847499999965 ~ 0.761x faster as iTree
    Exectime time list build (via comprehension): 0.006427750000000287 ~ 8.301x faster as iTree
    Exectime time list index access: 0.04177927499999967 ~ 14.226x faster as iTree
    -- SortedDict ---------------------------------
    Exectime time SortedDict build: 0.1408219500000003 ~ 0.379x faster as iTree
    Exectime time SortedDict key access: 0.13243777499999965 ~ 0.665x faster as iTree
    -- xml ElementTree ---------------------------------
    Exectime time xml ElementTree build: 0.00898362499999994 ~ 5.940x faster as iTree
    Exectime time xml ElementTree key access: 2.8548865250000004 ~ 0.031x faster as iTree
    Exectime time xml ElementTree index access: 0.05549647499999999 ~ 10.710x faster as iTree
    -- anytree ---------------------------------
    Exectime time Anytree build: 0.3895624249999994 ~ 0.137x faster as iTree
    Anytree key access skipped -> slow
    Exectime time Anytree index access: 1.0371582999999998 ~ 0.573x faster as iTree

I have following comments on the findings:

1. `iTree` objects behave ~ 8-16 times slower then the build in objects like dict, lists, etc. Reason is mainly that `iTree` is a pure python package which does not has the the speed advantage of an underlying C-Layer. Anyway a 20 times slower execution is really not an issue from our point of view. Please consider the wide range of functionalities found in `iTree` objects.
2. For untypical access of dict per idx or list per key the builtin objects perform ~ 100 times slower than `iTree`.
3. The other tree like packages are on par or slower then `iTree` (in some cases incredible slower). An exception is the package xml-ElementTree which incredible fast in case of index access (quicker then builtin lists).

On a large tree of 500000 we have the following findings:
::
    We run for treesizes: 500000 with 4 repetitions
    Python:  3.9.2 (tags/v3.9.2:1a79785, Feb 19 2021, 13:44:55) [MSC v.1928 64 bit (AMD64)]
    blist package is available and used
    itertree version: 0.8.0
    A relative values >1 related to `iTree` means the other object is faster
    (relative values <1 means `iTree` is faster)
    Exectime time itertree build: 1.4585138
    Exectime time itertree build: with subtree list comprehension: 1.317420325
    Exectime time itertree build (with insert): 1.5535431249999996
    Exectime time itertree tag access: 0.23381625000000028
    Exectime time itertree tag index access: 0.5307640249999999
    Exectime time itertree tag index tuple access: 0.4094945000000001
    Exectime time itertree index access: 0.21780237500000066
    Exectime time itertree convert iter_all iterator to list: 0.27708437500000027
    Exectime time itertree save to file: 2.1980745499999994
    Exectime time itertree load from file: 2.7010892500000008
    Loaded `iTree` is equal: True
    -- Standard classes -----------------------------------
    Exectime time dict build: 0.15743670000000165 ~ 9.264x faster as iTree
    Exectime time dict key access: 0.11920657499999976 ~ 1.961x faster as iTree
    Exectime time dict index access: skipped incredible slow
    Exectime time list build (via comprehension): 0.07432719999999904 ~ 17.725x faster as iTree
    Exectime time list build (via append): 0.09793205000000071 ~ 14.893x faster as iTree
    Exectime time list build (via insert): Skipped very slow
    Exectime time list index access: 0.025543875000000327 ~ 8.527x faster as iTree
    Exectime time list key access: Skipped incredible slow
    Exectime time OrderedDict build: 0.17470362499999936 ~ 8.349x faster as iTree
    Exectime time OrderedDict key access: 0.11788422500000095 ~ 0.234x faster as iTree
    Exectime time deque build (append): 0.10968872499999804 ~ 13.297x faster as iTree
    Exectime time deque build (insert): 0.1312096000000018 ~ 11.840x faster as iTree
    Exectime time deque index access: 7.638674499999997 ~ 0.029x faster as iTree
    -- SortedDict ---------------------------------
    Exectime time SortedDict build: 3.445377900000004 ~ 0.423x faster as iTree
    Exectime time SortedDict key access: 0.1740121499999958 ~ 1.344x faster as iTree
    Exectime time SortedDict index access: 1.105328924999995 ~ 0.197x faster as iTree
    -- xml ElementTree ---------------------------------
    Exectime time xml ElementTree build: 0.20869660000000323 ~ 6.989x faster as iTree
    xml ElementTree key access skipped -> too slow
    Exectime time xml ElementTree index access: 0.019160849999998675 ~ 12.203x faster as iTree
    -- anytree ---------------------------------
    Exectime time Anytree build: 5641.44443335 ~ 0.000x faster as iTree
    Anytree key access skipped -> incredible slow
    Exectime time Anytree index access: not working

Some of the steps are skipped because very bad performance (some functions need hours).

Insertion of elements in lists is very slow. This might only be a minor corner case because filling a list might
always be done by append() or even better with a list comprehension. The `iTree` insertion mechanism (based on blist)
works much quicker and is nearly on the speed of append(). But we also recommend list comprehension mechanism for
quickest filling of `iTree` objects too. The mayor time in filling an `iTree` goes into instance the object (`__init__`) and
if needed in the internal `copy()` of `iTree` items (e.g. see `extend()` method).

*****************************************
iTree vs. dict / collections.OrderedDict
*****************************************

For the base functionality storing data paired with hashable objects as keys in a data structure where one can
find the data by giving the key the dict is quicker then iTree
(10x quicker for the building of the structure and 2x quicker for the item access).
But we have a lot of limitations. We cannot store one and the same hashable object (key) multiple times in the dict
(item will always be overwritten). You can build nested dicts by putting sub dicts into dict keys
(building nested structures is only 7x quicker). But the access to this
nested structure is very limited no deep iterations are available out of the box. Also search queries must
be programmed outside the dict structure. The normal dict does not support ordered storage in older python
versions, only the OrderedDict extension does this. At least we do not have access to the order by index we always
must create an iterator that can be misused for index access.

Summary: It's not surprising that the main functional target (key based operations) of the build-in dict object are
quicker compared with the key (tag) based operations we have on `iTree`.
But the a dict is a flat unordered structure and there is no build-in functionality
related to trees. Considering the overall functionality of `iTree` in all highlighted directions the speed difference
even compared with the "core" functions of a dict are still more than acceptable from our point of view.

**********************************
iTree vs. list / collections.deque
**********************************

For lists and nested list we can found the same pros and cons we described for dicts in the last chapter
except that the access in list is focused on index and not by keys. We can say that index access in
iTrees is also the most performant way to access items (quicker then tag or TagIdx based access). Insert operations
in lists can be also very slow. For huge trees we recommend to install blist package which out-performances lists
in a lot of circumstances (We still don't understand why the blist implementation is not used as standard list
in python as proposed by the author). Beside the tag based access `iTree` objects can also be reached via index
lists (not available in lists). The deque object behave in general as lists. We can quicker insert elements
(link-list extension is easy) but get an items index() works much slower as in normal lists.

Summary: For the core functions lists and deque are 10-18 times quicker than `iTree`. But key access is very limited.

***************************
iTree vs. xml ElementTree
***************************

The xml ElementTree package goes very much in the same direction as the `iTree` package. The performance regarding
any list related action is very good and much better than `iTree` can deliver (C-Layer).

But the handling of ElementTrees is totally different. Trees are normally build by external factory functions even
that an internal build interface is available too (list like behavior). The same tag can be stored multiple times
in an ElementTree (same as in itertree). As the naming tells the package is mainly build to provide all xml related
data structures and functionalities. And the storage and loading into/from files is widely support. By the way serializing of none
string objects in the tree must be managed and organized by the user. The item identification is made via string only
tags and you can't use hashable object as tags (like in iTree).
Even the string usage is limited to the xml naming convention (e.g. no spaces are allowed). For queries in the tree
one can use the powerful xpath syntax. But we think the `iTree` filter functions are comparable and because we use
filter objects we are more flexible especially very special filter conditions.

Beside the pure index access `iTree` is for any operation quicker than the ElementTree
(which is surprising because ElementTree is a c-based implementation). Especially when searching for
specific tags and filtering we see bigger advantages for `iTree` (not all seen in the performance test).
Serialization and storage in `iTree` is more efficient than in ElementTree. But `iTree` does not have all
the xml powered higher level functionalities like schemata, etc. which are support by ElementTree
(which is really not the target of iTree). As last remark we can say an xml-serialization of `iTree` objects might
be easy implemented if needed.

***************************
iTree vs. sorted_dict
***************************

The sorted_dict package from sorted_containers might be used for the same proposes `iTree` is build for. But the
architecture for realization is a bit different. Sorted_dict supports key and index based access. But one cannot
store same key multiple times (behavior is here the same as in normal dicts). The `iTree` object has not the target
of sorting items in different ways. Furthermore `iTree` tries to realize filtered access to the items by keeping
the original order. In one first approach the author tried to realize the `iTree` functionalities with an underlying
sorted_dict. But the performance of the approach was worse and we changed the strategy.
iTree does not support the grouping function (union, intersection, etc.) supported by sorted-dicts. The performance
of sorted-dicts regarding the design paradigms of `iTree` is less good. Especially building a instance of sorted-dict
objects of a huge number is 2 times slower than for `iTree` objects. Key access is on par with normal dicts and 2
time quicker than in `iTree`.

***************************
iTree vs. anytree
***************************

The anytree packages gains mostly in the same direction as itertree. You can find nearly comparable serialization
possibilities. The rendering found in `iTree` is a simple "copy" of what you can get in anytree. As in `iTree` objects
you can combine children of same name with a parent in anytree too. But there are limitations in anytree:

    * You can only use string based tags (not hashable objects like in itertree). 
    * functional properties of a specific item do not exists (iTree.idx, `iTree`.idx_path, ....)
    * But the main issue from our point of view is the really bad performance in case of huge trees
      (Especially search for item.name is very slow)
    * filtering is very slow and not as powerful as in itertree

Before the itertree package was developed we thought anytree is the solution to go for and there is no need for a
new package like itertree. But the results of the anytree package tests we did where very ambiguous. Anytree has a
very huge feature-set but also really poor performance.
This was also shortly discussed with the author: https://github.com/c0fec0de/anytree/issues/169.

At least we came to the conclusion that anytree seems not match to our requirements for tree structured storage and
access. From description it should match, but in practice the package did not work for us as expected.

Summary: For small trees anytree might be an alternative to `iTree` but when getting to bigger structures (more elements
deeper levels) or when effective filtering is needed `iTree` has very huge advantages.

