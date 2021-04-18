.. _comparison:

Comparison
==========

In this chapter we compare the itertree package with other packages which are targeting in the same direction as itertree.

Each package is develop with a specific focus and therefore a comparison is always a bit misleading. Finally the comparison remarks you find in this chapter are no not at all a judgement of the other packages. Especially the performance tests can also be misleading be cause we may have utilized the other packages in the wrong way. 

In this comparison chapter we will compare iTree with the standard types like dict and lists. Additionally we have a look on xml.ElementTree, sorted_dict (from sorted containers) and the anytree package. 

In the design paradigms of the itertree package can be summarized by the following topics. They will be highlighted and compared:

1. We can add any type of tag in the iTree as long as it is hashable and we can add the same tag multiple times in the iTree. Some of the comparable package support only stringtype tags (like anytree or xml.ElementTree). Other allow only unique tags like the keys in dicts (using same key will overwrite the already existing tag in this case).

2. In iTree the item access via index and tag (or TagIdx) is possible. As you will see in the performance tests later many of the other packages are focus on one type of access and the second type is then much slower. In my opinion they are defined to have a specific access type in mind. (E.g. it's quite clear that index access on huge dicts or key access in huge list will be very slow). But even the search mechanisms in specialized packages are still very slow in my opinion.

3. The access of multiple items via index list is possible my_itree[[1,4,5,6,9]] will deliver the indexed items in an iterator (The access via indexlist is in most packages not supported).

4. The results when running filter queries in iTree will be delivered very quick because we delivering always iterators. But this might make the coding from the point of usage sometimes a bit complicate because if you need index access to a specific element you must have to cast the iterator in a list (by (list(my_iterator)) or use itertools.is_slice() operation. It's always recommended to addresse the target items via the available iTree methods (find(), find_all() or even iTree[]) directly. You can also use the item_filter and matches to reach your results as good as possible.

5. We can link multiple source files into one iTree object. Most of the packages do not support links and even the load and storage into files is not automatically supported (Users can always create serializers but this can be sometimes very difficult considering all datatypes stored in a tree). iTree delivers the possibility to store several datatypes into a JSON file and we allow to link subparts of a tree into diffrent files. So that you combine your trees from different file sources.

6. At least the data in the iTree objects can be combined with a data model that checks if the give data values matching with the ones expected by the data model. This means jmuch more then just a check of datatype one can also define ranges or intervals to which the given values must match. This functionality makes iTree objects very attractive for the storage of certain configuration data.

To summarize the iTree functions are focused on this given topics. The package is not focused on sorting values. For future extension the group building (e.g. building iTree intersections, etc.) might be realized by delivering the related group interators.

Under examples you can find the "itree_perfomance.py" file which contains a short performance test regarding other comparable packages. The following results are create with blist package installed and utilized by iTree. I didn't created a commmandline interface please feel free to adapt the first line regarding the tree size and the number of repetitions. The measured times are always relative to one iteration but it's a summary of the given number of operations.

Running the test on a tree with 5000 items delivers the following result on my PC under python 3.5.
::
    >>>python iter_performance.py
    We run for treesizes: 5000 with 4 repetitions
    itertree version: 0.6.1
    Exectime time itertree build (with insert): 0.01852375
    Exectime time itertree build: 0.01571845
    Exectime time itertree build: with subtree list comprehension: 0.014712800000000005
    Exectime time itertree tag access: 0.0028093999999999897
    Exectime time itertree tag index access: 0.006358150000000007
    Exectime time itertree tag index tuple access: 0.004354625000000001
    Exectime time itertree index access: 0.0029322250000000105
    Exectime time itertree convert iter_all iterator to list: 0.0035161499999999957
    Exectime time itertree save to file: 0.023204075000000005
    Exectime time itertree load from file: 0.03163832500000001
    Loaded iTree is equal: True
    -- Standard classes -----------------------------------
    Exectime time dict build: 0.002406100000000022
    Exectime time dict key access: 0.001221899999999998
    Exectime time dict index access: 0.29872780000000004
    Exectime time list build (via comprehension): 0.0007667500000000382
    Exectime time list build (via append): 0.0009924000000000044
    Exectime time list build (via insert): 0.004767324999999989
    Exectime time list index access: 0.00017365000000002517
    Exectime time list key access: 0.18101884999999995
    Exectime time OrderedDict build: 0.0016964999999999897
    Exectime time OrderedDict key access: 0.001065074999999971
    Exectime time deque build (append): 0.0014350250000000342
    Exectime time deque build (insert): 0.0017438749999999503
    Exectime time deque index access: 0.0002723000000000031
    Exectime time IndexedOrderedDict build: 0.003601199999999971
    Exectime time IndexedOrderedDict key access: 0.0012901249999999198
    Exectime time IndexedOrderedDict idx access: 0.0035858749999999606
    -- SortedDict ---------------------------------
    Exectime time SortedDict build: 0.04718642500000003
    Exectime time SortedDict key access: 0.0015281499999999504
    Exectime time SortedDict index access: 0.009181499999999954
    -- xml ElementTree ---------------------------------
    Exectime time xml ElementTree build: 0.0028383499999999895
    Exectime time xml ElementTree key access: 0.2222158500000001
    Exectime time xml ElementTree index access: 0.00018889999999993634
    -- anytree ---------------------------------
    Exectime time Anytree build: 0.6258656249999999
    Exectime time Anytree key access (no cache): 25.842957875
    Exectime time Anytree index access: 0.09278047500000142


I have following comments on the findings:

1. iTree objects behave ~ 10-20 times slower then the build in objects like dict, lists, etc. Reason is mainly that iTree is a pure python package which does not has the the speed advantage of an underlaying C-Layer. Anyway a 20 times slower execution is really not an issue if you consider the wide range of functionalities found in iTree objects.
2. For untypical access of dict per idx or list per key the buildin objects perform ~ 100 times slower then iTree.
3. The other tree like packages are on par or slower then iTree (in some cases incredible slower). An exception is the package xml-ElementTree which incredible fast in case of index access (quicker then buildin lists).

On a large tree of 500000 we have the following findings:
::
    >>>python iter_performance.py
    We run for treesizes: 500000 with 4 repetitions
    itertree version: 0.6.1
    Exectime time itertree build (with insert): 1.822058575
    Exectime time itertree build: 1.7976585249999997
    Exectime time itertree build: with subtree list comprehension: 1.7526210750000004
    Exectime time itertree tag access: 0.3406376249999994
    Exectime time itertree tag index access: 0.8212707750000003
    Exectime time itertree tag index tuple access: 0.5618178500000006
    Exectime time itertree index access: 0.3043280250000002
    Exectime time itertree convert iter_all iterator to list: 0.3584018750000002
    Exectime time itertree save to file: 2.775001025
    Exectime time itertree load from file: 3.4587883999999995
    Loaded iTree is equal: True
    -- Standard classes -----------------------------------
    Exectime time dict build: 0.5536466499999975
    Exectime time dict key access: 0.14499792499999842
    Exectime time dict index access: skipped incredible slow
    Exectime time list build (via comprehension): 0.10255107500000094
    Exectime time list build (via append): 0.11917187499999926
    Exectime time list build (via insert): Skipped very slow
    Exectime time list index access: 0.03232377500000183
    Exectime time list key access: Skipped incredible slow
    Exectime time OrderedDict build: 0.29996864999999673
    Exectime time OrderedDict key access: 0.1450631499999986
    Exectime time deque build (append): 0.17220544999999987
    Exectime time deque build (insert): 0.19610544999999746
    Exectime time deque index access: 7.205191400000004
    Exectime time IndexedOrderedDict build: 0.4442919250000017
    Exectime time IndexedOrderedDict key access: 0.1821846500000035
    Exectime time IndexedOrderedDict idx access: 0.4304988250000008
    -- SortedDict ---------------------------------
    Exectime time SortedDict build: 5.621732250000001
    Exectime time SortedDict key access: 0.19455682499999938
    Exectime time SortedDict index access: 1.6786233250000038
    -- xml ElementTree ---------------------------------
    Exectime time xml ElementTree build: 0.4656471249999967
    xml ElementTree key access skipped -> too slow
    Exectime time xml ElementTree index access: 0.020482749999999328
    -- anytree ---------------------------------
    Exectime time Anytree build: 0.6159421000000052
    Anytree key access skipped -> incredible slow
    Exectime time Anytree index access: not working

Some of the steps are skipped because bad performance (some functions need hours).

Maybe I made something wrong but I did not get the anytree package working for bigger treesizes (only building worked but access did not work).

Insertion of elements in lists is very slow. This might only be a minor cornercase because filling a list might always be done by append() or even better with a list comprehension. The iTree insertion mechanism (based on blist) works much quicker and is nearly on the speed of append(). But we also recommend list comprehension mechanism for quickest filling of itertrees too. The mayor time in filling an iTree goes into the instanciation and if need copy() of the list items.

***************************
iTree vs. dict / collections.OrderedDict
***************************

For the base functionality storing data paired with hashable objects as keys in a data structure where one can find the data by giving the key or iterate over the items the dict is 20 times quicker then iTree. But we have a lot of limitations. We cannot store one and the same hashable object (key) multiple times in the dict (item will always be overwritten). You can build nested dicts by putting sub dicts into dict keys. But the access to this nested structure is very limited no deep iterations are available out of the box. Also search queries must be programmed above the dict structure. The normal dict does not support ordered storage in older python versions, only the OrderedDict extension does this. At least we do not have access to the order by index we always must create an iterator that can be misused for index access. Summary: for the limited functional target the dict is a more effective way to store data then the iTree. But the overall functionality of iTree in all highlighted directions is much bigger then in standard dicts.

***************************
iTree vs. list / collections.deque
***************************

For lists and nested list we can found the same pros and cons we descripted for dicts in the last chapter except that the access in list is focused on index and not by keys. We can say that index access in iTrees is also the most performant way to access items (quicker then tag or TagIdx based access). Insert operations in lists can be also very slow. For huge trees we recommend to install blist package which outperformance lists in a lot of circumstances. Beside the tag based access itree objects can also be reached via index lists (not available in lists). The deque object behave in general as lists. We can quicker insert elements (linklist extension is easy) but get an items index() works much slower as in normal lists.

***************************
iTree vs. xml ElemenTree
***************************

The xml ElementTree package goes very much in the same direction as the iTree package. The performance regarding any list related action is very good and much better then iTree can deliver (C-Layer). But the handling of ElemntTrees is totally different. Trees are normally build by external factory functions an internal build interface is available too (list like behavior). The same tag can be stored multiple times in an ElemenTree (same as in itertree). As the naming tells the package is mainly build to provide all xml related data structures and fucntionalities. And the storage and loading into/from files is widely support. By the way serializing of none string objects in the tree must be managed and organized by the user. The data is stored under string tags one cannot use any hashable object here. Even the string usage is limited to the xml nameing convention (e.g. no spaces are allowed). For queries in the tree one can use the xpath syntax. iTree has comparible functionalities. Beside the index access iTree is quicker than the ElemenTree especially when searching for specific tags. Serialization and storage is more efficent than in ElemenTree. But iTree does not have all the xml powered higher level functionalities like schemata, etc. which are support by ElemenTree, which is not at all the target of iTree.

***************************
iTree vs. sorted_dict
***************************

The sorted_dict package from sorted_contains might be used for the same proposes iTree is build for. But the architecture for realization is a bit different. Sorted_dict supports key and index based access. But one cannot store same key multiple times (behavior is here the same as in normal dicts). The iTree object has not the target of sorting items in different ways. Furthermore iTree tries to relize filtered access to the items by keeping the original order. In one first approach the author tried to realize the iTree functionalities with an underlying sorted_dict. But the performance of the approach was worse and we changed the strategy. 
iTree does not yet support the grouping function supported by sorted-dicts. But building intersections, etc. of two or more iTrees might be supported in an upcoming version of iTree. The performance of sorted-dicts regarding the design paradigms of iTree is less good. Especially the instanciation of sorted-dict objects of a huge number is 2 times slower than for iTree objects.

***************************
iTree vs. anytree
***************************

The anytree packages gains mostly in the same direction as itertree. You can find nearly comparable serialization possibiliies. The rendering found in iTree is a simple "copy" of what you can get in anytree. As in iTree objects you can combine children of same name with a parent in anytree too. But you can only use string based tags. The way you can navigate in the tree is in anytree a bit more extended compared to iTree object. Before the itertree package was developed we thought anytree is the solution to go for and there is no need for a package like itertree. But the results of the anytree package tests we did where very ambigous. We found a very rich featureset but in some cases a very poor performance. But the real blocker is that the access to the children property on large trees (>10000 items) is not working at all (or we do something wrong).

At least we came to the conclusion that anytree seems not match to our requirements for tree structured storage and access. From description it should match, but in practice the package did not work for us as expected.
