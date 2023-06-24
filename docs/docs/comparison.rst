.. _Comparison_Chapter:

Comparison
==========

In this chapter we compare the itertree package with other packages which are targeting nested tree structures too or
that might be used for such an approach. We like to show that itertree package is on a comparable performance level
(or better) even that in most cases we have from the functional point much more features implemented.
In the final comparison with the other packages we will mark those functional differences too.

Each package is developed with a specific focus and therefore comparisons are always a bit misleading. Most often
there are good reasons for the different behavior (e.g. ElementTrees are build for xml representations
and therefore tags are limited to the "rules" of xml). We tried to use the packages as correct as possible but we may
missed a function and the performance shown might be worse. We apologize in tis case and ask
the autor to contact us via GIT Issue.

We compare `iTree` also with the standard types like `dict`, `list` and `deque`, `OrderedDict` from the
collections package. This is done to see how far away we are with itertree from the build-in classes
which are somehow the benchmark. In the comparison we must consider that some package are C-compiled
(like the build-in types or ElementTree). This leads automatically into a speed advantage against the packages
which are python based (like itertree)..

The code for this analysis is placed in itertree/examples/performance folder and the user can execute the analysis on
his own environment too. The user can easy adapt the parameters related to size and depth of the created trees. The
analysis can only be performed if the targeted packages are available in the local installation. Not found
modules are skipped automatically. The user can find some experimental not published packages
imported in the code, this should be ignored. In case no blist package is installed you may skip
the `insert()` operation of `iTree` for large trees, it s slowed
down a lot (standard `list` used).
**-> Actions which take 30 seconds or more are skipped and just marked as \"-> skipped too slow\".**

Finally we tried to make the testing as comparable as possible:

    * Because some tree-like-classes are limited to string-type
      keys/tags we always used string type keys (The string creation costs time
      so we create the strings for all objects).

    * For flat list-like objects (level one only objects we must create a nested structure to make it comparable
      and to test the in-depth access each item is in this case a tuple of (tag/key, value, subtree).

    * For flat dict-like objects we also had to extend a nested structure again a tuple of (value, subtree) is used.

    * We do not use the quickest possible functions to get a specific object we try to use the best comparable
      function (e.g. we do not compare a tree build via append() with a build via comprehension).

    * We used helper functions to realize comparable functionalities in case the object does not provide
      it out of the box. Sometimes this might be really meaning less (test a dict for index access
      or a list for key access). But this is done to really compare to the feature-set of itertree but we do not
      stress this comparison to much. But it shows very often that this object cannot be used
      out of the box as a nested tree representation.

      Sometimes we use helper functions also to overcome RecursionErrors in deep trees. In case of
      recursive definitions in the object we needed a iterative counter part. But it's not done in all cases
      (e.g. `deepcopy()` does not work on all other objects).


.. note:: IMPORTANT: Please consider that for the smaller trees the shown relative differences are less important
          because the absolute time for the operation is anyway very short. Normally nobody will have an issue
          with this the times are anyway extremely short and if the operation is not repeated the difference is
          neglect able even that the factor might be 10. If we compare the performance in between the objects
          we mainly look on the large scale analysis because some objects getting much slower if the
          size or the depth grows.


**We used for the here discussed analysis a setup with Python 3.9 incl. blist package installed on a Windows OS.**

The output is reduced by some spaces so it fits better on the html page.

##############################
Analysis Results
##############################


Building trees via item append
+++++++++++++++++++++++++++++++

Performance analysis related to level 1 only trees with a size of 5000; build via `append()` function:

::

    itertree.iTree:
    tree=iTree(); tree.append(iTree(tag,value))                          0.007014 s
    build-in list:
    tree=list(); tree.append((key,value,list())                          0.000890 s  -> 7.883x faster as iTree
    build-in dict:
    tree=dict(); tree[key]=(value,dict())                                0.000870 s  -> 8.065x faster as iTree
    collections.deque:
    tree=deque(); tree.append((key,value,deque())                        0.001786 s  -> 3.927x faster as iTree
    collections.OrderedDict:
    tree=odict(); tree[key]=(value,odict())                              0.001079 s  -> 6.500x faster as iTree
    blist.blist:
    tree=blist(); tree.append((key,value,blist())                        0.002133 s  -> 3.288x faster as iTree
    indexed.IndexedOrderedDict:
    tree=IndexedOrderedDict(); tree[key]=(value,IndexedOrderedDict())    0.004104 s  -> 1.709x faster as iTree
    indexed.Dict:
    tree=Dict(); tree[key]=(value,Dict())                                0.003955 s  -> 1.773x faster as iTree
    xml.etree.ElementTree.Element:
    tree=Element(); tree.append(Element(key,{"value":key}))              0.004201 s  -> 1.670x faster as iTree
    lxml.etree.Element:
    tree=Element(); tree.append(Element(key,{"value":key}))              0.020792 s  -> 0.337x faster as iTree
    pyTooling.Tree.Node:
    tree=Node(); tree.AddChild(Node(key,value))                          0.007428 s  -> 0.944x faster as iTree
    treelib.Node:
    tree=Tree(); Tree.create_node(key,key, parent="root",value=value)    0.023033 s  -> 0.305x faster as iTree
    anytree.Node:
    tree=Node(); Node(key, parent=tree,value=value)                      0.401775 s  -> 0.017x faster as iTree

Performance analysis related to level 1 only trees with a size of 500000; build via `append()` function:

::

    itertree.iTree:
    tree=iTree(); tree.append(iTree(tag,value))                         0.663867 s
    build-in list:
    tree=list(); tree.append((key,value,list())                         0.091123 s  -> 7.285x faster as iTree
    build-in dict:
    tree=dict(); tree[key]=(value,dict())                               0.115628 s  -> 5.741x faster as iTree
    collections.deque:
    tree=deque(); tree.append((key,value,deque())                       0.166790 s  -> 3.980x faster as iTree
    collections.OrderedDict:
    tree=odict(); tree[key]=(value,odict())                             0.148325 s  -> 4.476x faster as iTree
    blist.blist:
    tree=blist(); tree.append((key,value,blist())                       0.218836 s  -> 3.034x faster as iTree
    indexed.IndexedOrderedDict:
    tree=IndexedOrderedDict(); tree[key]=(value,IndexedOrderedDict())   0.232782 s  -> 2.852x faster as iTree
    indexed.Dict:
    tree=Dict(); tree[key]=(value,Dict())                               0.232265 s  -> 2.858x faster as iTree
    xml.etree.ElementTree.Element:
    tree=Element(); tree.append(Element(key,{"value":key}))             0.235984 s  -> 2.813x faster as iTree
    lxml.etree.Element:
    tree=Element(); tree.append(Element(key,{"value":key}))             1.775910 s  -> 0.374x faster as iTree
    pyTooling.Tree.Node:
    tree=Node(); tree.AddChild(Node(key,value))                         0.701030 s  -> 0.947x faster as iTree
    treelib.Node:
    tree=Tree(); Tree.create_node(key,key, parent="root",value=value)   1.945515 s  -> 0.341x faster as iTree
    anytree.Node
    tree=Tree(); %s(key, parent=tree,value=value)                         -> skipped too slow

Performance analysis related related to trees with depth 100 and a size of 1000; build via `append()` function:

::

    itertree.iTree:
    tree=iTree(); tree.append(iTree(tag,value))                        0.001502 s
    build-in list:
    tree=list(); tree.append((key,value,list())                        0.000279 s  -> 5.390x faster as iTree
    build-in dict:
    tree=dict(); tree[key]=(value,dict())                              0.000368 s  -> 4.081x faster as iTree
    collections.deque:
    tree=deque(); tree.append((key,value,deque())                      0.000480 s  -> 3.132x faster as iTree
    collections.OrderedDict:
    tree=odict(); tree[key]=(value,odict())                            0.000377 s  -> 3.986x faster as iTree
    blist.blist:
    tree=blist(); tree.append((key,value,blist())                      0.000581 s  -> 2.587x faster as iTree
    indexed.IndexedOrderedDict:
    tree=IndexedOrderedDict(); tree[key]=(value,IndexedOrderedDict())  0.001621 s  -> 0.927x faster as iTree
    indexed.Dict:
    tree=Dict(); tree[key]=(value,Dict())                              0.001446 s  -> 1.039x faster as iTree
    xml.etree.ElementTree.Element:
    tree=Element(); tree.append(Element(key,{"value":key}))            0.001595 s  -> 0.942x faster as iTree
    lxml.etree.Element:
    tree=Element(); tree.append(Element(key,{"value":key}))            0.004319 s  -> 0.348x faster as iTree
    pyTooling.Tree.Node:
    tree=Node(); tree.AddChild(Node(key,value))                        0.001427 s  -> 1.053x faster as iTree
    treelib.Node:
    tree=Tree(); Tree.create_node(key,key, parent="root",value=value)  0.005254 s  -> 0.286x faster as iTree
    anytree.Node:
    tree=Node(); Node(key, parent=tree,value=value)                    0.009790 s  -> 0.153x faster as iTree

Performance analysis related related to trees with depth 1000 and a size of 10000; build via `append()` function:

::

    itertree.iTree:
    tree=iTree(); tree.append(iTree(tag,value))                        0.013546 s
    build-in list:
    tree=list(); tree.append((key,value,list())                        0.003512 s  -> 3.857x faster as iTree
    build-in dict:
    tree=dict(); tree[key]=(value,dict())                              0.004493 s  -> 3.015x faster as iTree
    collections.deque:
    tree=deque(); tree.append((key,value,deque())                      0.005670 s  -> 2.389x faster as iTree
    collections.OrderedDict:
    tree=odict(); tree[key]=(value,odict())                            0.005158 s  -> 2.626x faster as iTree
    blist.blist:
    tree=blist(); tree.append((key,value,blist())                      0.007198 s  -> 1.882x faster as iTree
    indexed.IndexedOrderedDict:
    tree=IndexedOrderedDict(); tree[key]=(value,IndexedOrderedDict())  0.013275 s  -> 1.020x faster as iTree
    indexed.Dict:
    tree=Dict(); tree[key]=(value,Dict())                              0.013865 s  -> 0.977x faster as iTree
    xml.etree.ElementTree.Element:
    tree=Element(); tree.append(Element(key,{"value":key}))            0.006693 s  -> 2.024x faster as iTree
    lxml.etree.Element:
    tree=Element(); tree.append(Element(key,{"value":key}))            0.045103 s  -> 0.300x faster as iTree
    pyTooling.Tree.Node:
    tree=Node(); tree.AddChild(Node(key,value))                        0.013264 s  -> 1.021x faster as iTree
    treelib.Node:
    tree=Tree(); Tree.create_node(key,key, parent="root",value=value)  0.092746 s  -> 0.146x faster as iTree
    anytree.Node:
    tree=Node(); Node(key, parent=tree,value=value)                    0.587480 s  -> 0.023x faster as iTree

The `iTree`-object and the most other objects show here comparable performance.

    * `list`, `dict` : Both build-in object are the benchmark in this analysis. `list` is the clear winner of
      this comparison. The `dict`- object shows like all dict-like objects a relative drop in performance
      if the tree size grows.
      If we compare `iTree` with those objects we see that we are for level 1 trees round about 7-5 times slower and
      the really deep trees 3-4 times slower. This is not surprising considering the c-code base and the deep
      integration into the Python-Interpreter.

    * Other dicts and lists: We see that those objects are slower as the build-in counterparts We can
      say in mean `iTree` is round about two times slower. As standard dict the dict-like objects
      getting relative-slower for larger sized trees.

    * The two ElementTrees shows an ambivalent picture but all in all we would say they on large trees they are on same
      level like `iTree`.
      As we will see from design the ElementTree from xml is optimized for access where
      lxml seems to be optimized for build (instance). We see that lxml ElementTree is here a head
      the of xml counter-part and `iTree` too.

    * Indexed dicts and the PyTooling are on really comparable level as `iTree` in all `append()` cases executed.

    * The tree related objects treelib and anytree are clearly slower. As we will see for all other functions too
      anytree is a lot slower especially if the tree size crows. At one point the objects seems do block
      even after many minutes of execution we do not get a result.

Build tree via extend or comprehension
+++++++++++++++++++++++++++++++++++++++

The iTree object supports the build of an object via a comprehension like functionality which is the fastest way to
build the object. The operation is for nested structures not so much quicker compared
with `append()` (only 10-20% times quicker). We present here just the max-size results.

Performance analysis related to level 1 only trees with a size of 500000; build via comprehension or `extend()` function:

::

    itertree.iTree:
    tree=iTree(key,subtree=(iTree(key,value) for ....))                    0.610306 s
    build-in list:
    tree=list((key,value,list()) for ....))                                0.125169 s  -> 4.876x faster as iTree
    build-in dict:
    tree=dict((key,(value,dict())) for ....))                              0.215009 s  -> 2.839x faster as iTree
    collections.deque:
    tree=deque((key,value,deque()) for ....))                              0.207484 s  -> 2.941x faster as iTree
    collections.OrderedDict:
    tree=odict((key,(value,odict())) for ....))                            0.299324 s  -> 2.039x faster as iTree
    blist.blist:
    tree=blist((key,value,blist()) for ....))                              0.303959 s  -> 2.008x faster as iTree
    indexed.IndexedOrderedDict:
    tree=IndexedOrderedDict((key,(value,IndexedOrderedDict())) for ....))  0.782604 s  -> 0.780x faster as iTree
    indexed.Dict:
    tree=Dict((key,(value,Dict())) for ....))                              0.778467 s  -> 0.784x faster as iTree
    xml.etree.ElementTree.Element:
    tree.extend(Element(key,{"value":key}))                                0.301490 s  -> 2.024x faster as iTree
    lxml.etree.Element:
    tree.extend(Element(key,{"value":key}))                                1.804367 s  -> 0.338x faster as iTree
    pyTooling.Tree.Node:
    tree=Node(children=[Node(key,value) for ...])                          0.734321 s  -> 0.831x faster as iTree
    anytree.Node:
    tree=%s(children=[%s(key,value) for ...])                              -> skipped too slow

Performance analysis related related to trees with depth 1000 and a size of 10000; build via comprehension or `extend()` function:

::

    itertree.iTree:
    tree=iTree(key,subtree=(iTree(key,value) for ....))                    0.598814 s
    build-in list:
    tree=list((key,value,list()) for ....))                                0.112530 s  -> 5.321x faster as iTree
    build-in dict:
    tree=dict((key,(value,dict())) for ....))                              0.197339 s  -> 3.034x faster as iTree
    collections.deque:
    tree=deque((key,value,deque()) for ....))                              0.198221 s  -> 3.021x faster as iTree
    collections.OrderedDict:
    tree=odict((key,(value,odict())) for ....))                            0.275480 s  -> 2.174x faster as iTree
    blist.blist:
    tree=blist((key,value,blist()) for ....))                              0.271218 s  -> 2.208x faster as iTree
    indexed.IndexedOrderedDict:
    tree=IndexedOrderedDict((key,(value,IndexedOrderedDict())) for ....))  0.712246 s  -> 0.841x faster as iTree
    indexed.Dict:
    tree=Dict((key,(value,Dict())) for ....))                              0.710830 s  -> 0.842x faster as iTree
    xml.etree.ElementTree.Element:
    tree.extend(Element(key,{"value":key}))                                0.299102 s  -> 2.002x faster as iTree
    lxml.etree.Element:
    tree.extend(Element(key,{"value":key}))                                1.978916 s  -> 0.303x faster as iTree
    pyTooling.Tree.Node:
    tree=Node(children=[Node(key,value) for ...])                          0.691485 s  -> 0.866x faster as iTree
    anytree.Node:
    tree=%s(children=[%s(key,value) for ...])                              -> skipped too slow


We see that in this case the differences in between the objects are less compared to `append()`.
The build-in `list` is again the fastest object it is 5 times quicker than `iTree`.

The results we have seen in `append()` are somehow reproduced. The indexed dicts and the pyToolingTree
are here a bit behind `ìTree`.

Index based item access
++++++++++++++++++++++++

Beside the build of the nested structure the access of items in the diffrent levels is the second important
core-function we see for trees. We can here differentiate in between the index and the key/tag based access.

In `iTree` the user has the choice in between the "lazy" get item access with flexible targets or a specific access.
The flexible (common) access is slower because the given target must be identified. Because this feature does
not exist in the other objects we mainly compare with the specific access (even that
common access comparison is given in brackets too).

We know that list-like object are designed for index-access only and dict-like objects (except indexed dict)
are designed for key-based-access. We had to use helper functions for the missing function and we will see
that they are comparable slow.

Let's first have a look on index based access. Dict-like objects access via `next(itertools.islice(tree,idx))` which
is much slower for the last items in the stored order but we show here the mean access time.

Performance analysis related to level 1 only trees with a size of 5000; access via  `__getitem__(index)` function:

::

    itertree.iTree (common target access):
    tree[idx]                                                0.001344 s
    itertree.iTree (index-specific access):
    tree.get.by_idx(idx)                                     0.000857 s ->  1.568x faster as common access
    build-in list:
    tree[idx]                                                0.000274 s  -> 3.124x (4.898x) faster as iTree
    build-in dict:
    next(islice(tree.values(),idx))                          0.046756 s  -> 0.018x (0.029x) faster as iTree
    collections.deque:
    tree[idx]                                                0.000458 s  -> 1.872x (2.935x) faster as iTree
    collections.OrderedDict:
    next(islice(tree.values(),idx))                          0.274780 s  -> 0.003x (0.005x) faster as iTree
    blist.blist:
    tree[idx]                                                0.000271 s  -> 3.169x (4.969x) faster as iTree
    indexed.IndexedOrderedDict:
    tree.values()[idx]                                       0.001780 s  -> 0.482x (0.755x) faster as iTree
    indexed.Dict:
    tree.values()[idx]                                       0.001685 s  -> 0.509x (0.798x) faster as iTree
    xml.etree.ElementTree.Element:
    tree[idx]                                                0.000245 s  -> 3.494x (5.479x) faster as iTree
    lxml.etree.Element:
    tree[idx]                                                0.044648 s  -> 0.019x (0.030x) faster as iTree
    pyTooling.Tree.Node:
    next(islice(tree.GetChildren(),idx))                     0.263845 s  -> 0.003x (0.005x) faster as iTree
    treelib.Node:
    tree.children[idx]                                       2.032886 s  -> 0.000x (0.001x) faster as iTree
    anytree.Node:
    tree.children[idx]                                       0.038357 s  -> 0.022x (0.035x) faster as iTree

Performance analysis related to level 1 only trees with a size of 500000; access via  `__getitem__(index)` function:

::

    itertree.iTree (common target access):
    tree[idx]                                                0.142918 s
    itertree.iTree (index-specific access):
    tree.get.by_idx(idx)                                     0.097269 s ->  1.469x faster as common access
    build-in list:
    tree[idx]                                                0.028292 s  -> 3.438x (5.052x) faster as iTree
    build-in dict:
    next(islice(tree.values(),idx))                            -> skipped too slow
    collections.deque:
    tree[idx]                                                6.575242 s  -> 0.015x (0.022x) faster as iTree
    collections.OrderedDict:
    next(islice(tree.values(),idx))                            -> skipped too slow
    blist.blist:
    tree[idx]                                                0.029997 s  -> 3.243x (4.764x) faster as iTree
    indexed.IndexedOrderedDict:
    tree.values()[idx]                                       0.187038 s  -> 0.520x (0.764x) faster as iTree
    indexed.Dict:
    tree.values()[idx]                                       0.190313 s  -> 0.511x (0.751x) faster as iTree
    xml.etree.ElementTree.Element:
    tree[idx]                                                0.029029 s  -> 3.351x (4.923x) faster as iTree
    lxml.etree.Element:
    tree[idx]                                                  -> skipped too slow
    pyTooling.Tree.Node:
    next(islice(tree.GetChildren(),idx))                       -> skipped too slow
    treelib.Node:
    tree.children[idx]                                         -> skipped too slow
    anytree.Node no test source was build (append())           -> operation skipped

The `iTree`-class supports the in-depth access of items out of the box (via `itree.deep.` ). For most other
objects an in-depth helper access function was created. For treelib we couldn't create a comparable
function so that the object is not considered in the followoing analysis.

Performance analysis related related to trees with depth 100 and a size of 1000; access via  `__getitem__(index)` function:

::

    itertree.iTree (common target access):
    tree.get(*idxs)                                           0.010597 s
    itertree.iTree (index-specific access):
    tree.get.by_idx(*idxs)                                    0.002180 s ->  4.862x faster as common access
    build-in list:
    tree[idx]                                                 0.001252 s  -> 1.741x (8.463x) faster as iTree
    build-in dict:
    next(islice(tree.values(),idx))                           0.006946 s  -> 0.314x (1.526x) faster as iTree
    collections.deque:
    tree[idx]                                                 0.001490 s  -> 1.463x (7.114x) faster as iTree
    collections.OrderedDict:
    next(islice(tree.values(),idx))                           0.009487 s  -> 0.230x (1.117x) faster as iTree
    blist.blist:
    tree[idx]                                                 0.001353 s  -> 1.611x (7.832x) faster as iTree
    indexed.IndexedOrderedDict:
    tree.values()[idx]                                        0.016197 s  -> 0.135x (0.654x) faster as iTree
    indexed.Dict:
    tree.values()[idx]                                        0.016333 s  -> 0.133x (0.649x) faster as iTree
    xml.etree.ElementTree.Element:
    tree[idx]                                                 0.001144 s  -> 1.905x (9.262x) faster as iTree
    lxml.etree.Element:
    tree[idx]                                                 0.006120 s  -> 0.356x (1.732x) faster as iTree
    pyTooling.Tree.Node:
    next(islice(tree.GetChildren(),idx))                      0.014973 s  -> 0.146x (0.708x) faster as iTree
    anytree.Node:
    tree.children[idx]                                        0.007702 s  -> 0.283x (1.376x) faster as iTree

Performance analysis related related to trees with depth 1000 and a size of 10000; access via  `__getitem__(index)` function:

::

    itertree.iTree (common target access):
    tree.get(*idxs)                                           1.049203 s
    itertree.iTree (index-specific access):
    tree.get.by_idx(*idxs)                                    0.197017 s ->  5.325x faster as common access
    build-in list:
    tree[idx]                                                 0.117011 s  -> 1.684x (8.967x) faster as iTree
    build-in dict:
    next(islice(tree.values(),idx))                           0.679821 s  -> 0.290x (1.543x) faster as iTree
    collections.deque:
    tree[idx]                                                 0.149676 s  -> 1.316x (7.010x) faster as iTree
    collections.OrderedDict:
    next(islice(tree.values(),idx))                           0.938039 s  -> 0.210x (1.119x) faster as iTree
    blist.blist:
    tree[idx]                                                 0.130424 s  -> 1.511x (8.045x) faster as iTree
    indexed.IndexedOrderedDict:
    tree.values()[idx]                                        1.543223 s  -> 0.128x (0.680x) faster as iTree
    indexed.Dict:
    tree.values()[idx]                                        1.548948 s  -> 0.127x (0.677x) faster as iTree
    xml.etree.ElementTree.Element:
    tree[idx]                                                 0.098422 s  -> 2.002x (10.660x) faster as iTree
    lxml.etree.Element:
    tree[idx]                                                 6.198828 s  -> 0.032x (0.169x) faster as iTree
    pyTooling.Tree.Node:
    next(islice(tree.GetChildren(),idx))                      1.437700 s  -> 0.137x (0.730x) faster as iTree
    anytree.Node:
    tree.children[idx]                                        0.747130 s  -> 0.264x (1.404x) faster as iTree

First we like to remark that for small trees the common access function in `iTree` is only 1-1.5 times slower as
the specific one. Only for larger trees the difference get obvoius up two 5 times slower in our examples. What we
can also see that `iTree` supports it's nested structure quite well and it has even more advantages for in-depth access.

    * dict-like objects: We do not want to stress this point here they are obviously not made for this kind of
      access and therefore slower.

    * `list` - is again the fastest object. Of course it is designed for index access. But the difference to `iTree`
      is not much in deeper trees `list` is less then two times quicker (only).

    * Indexed dicts - do not perform as good as the name and functions let us expect. The index access is better
      then for normal dicts for sure but it is clearly behind `iTree`.

    * ElementTrees - Getting slower for lager number of children. For the deep structures `iTree`
      outperforms those objects. For this function lxml ElementTree is clearly slower as the xml ElementTree.

    * All other tree objects - People may say index access is less important in trees this might be the reason why
      index access is for all of them slower as in `iTree`.


Key based item access
++++++++++++++++++++++

As mentioned in the sentence before for some users this access type might be for trees more important then
the index access. This means at the end trees are more seen as nested dicts.

The list-like are not designed for this kind of access and for those objects we end up in a search functionality
which is based on an interation and comparison (we used `tree[tree.index((key,value,subtree))]`). The operation 
is not 100% accurate normally we should just search for the key with something like 
`next(dropwhile(lambda item: item[0] != key,tree))` but this would be even slower but it
is used where `index()`-method was not avaiable.

Performance analysis related to level 1 only trees with a size of 5000; access via  `__getitem__(key)` function:

::

    itertree.iTree (common target access):
    tree[key]                                                 0.002031 s
    itertree.iTree (tag_idx-specific access):
    tree.get.by_tag_idx(key)                                  0.001589 s ->  1.278x faster as common access
    build-in list:
    tree[tree.index(key)]                                     0.172946 s  -> 0.009x (0.012x) faster as iTree
    build-in dict:
    tree[key]                                                 0.000844 s  -> 1.882x (2.406x) faster as iTree
    collections.deque:
    tree[tree.index(key)]                                     0.180119 s  -> 0.009x (0.011x) faster as iTree
    collections.OrderedDict:
    tree[key]                                                 0.000852 s  -> 1.865x (2.384x) faster as iTree
    blist.blist:,
    tree[tree.index(key)]                                     0.205660 s  -> 0.008x (0.010x) faster as iTree
    indexed.IndexedOrderedDict:
    tree[key]                                                 0.000984 s  -> 1.616x (2.065x) faster as iTree
    indexed.Dict:
    tree[key]                                                 0.000958 s  -> 1.659x (2.120x) faster as iTree
    xml.etree.ElementTree.Element:
    tree.find(key)                                            0.122876 s  -> 0.013x (0.017x) faster as iTree
    lxml.etree.Element:
    tree.find(key)                                            0.114247 s  -> 0.014x (0.018x) faster as iTree
    pyTooling.Tree.Node:
    tree.GetNodeByID(key))                                    0.001260 s  -> 1.261x (1.612x) faster as iTree
    treelib.Node:
    tree.get_node(key)                                        0.001685 s  -> 0.943x (1.206x) faster as iTree
    anytree.Node:
    search.find(tree, lambda node: node.name == key)                           14.093013 s  -> 0.000x (0.000x) faster as iTree
    next(dropwhile(lambda item: item.name != key, tree.children)               1.835935 s  -> 0.001x (0.001x) faster as iTree

Performance analysis related to level 1 only trees with a size of 500000; access via  `__getitem__(key)` function:

::

    itertree.iTree (common target access):
    tree[key]                                                 0.266813 s
    itertree.iTree (tag_idx-specific access):
    tree.get.by_tag_idx(key)                                  0.215222 s ->  1.240x faster as common access
    build-in list:
    tree[tree.index(key)]                                       -> skipped too slow
    build-in dict:
    tree[key]                                                 0.103994 s  -> 2.070x (2.566x) faster as iTree
    collections.deque:
    tree[tree.index(key)]                                       -> skipped too slow
    collections.OrderedDict:
    tree[key]                                                 0.103348 s  -> 2.082x (2.582x) faster as iTree
    blist.blist:
    tree[tree.index(key)]                                       -> skipped too slow
    indexed.IndexedOrderedDict:
    tree[key]                                                 0.119337 s  -> 1.803x (2.236x) faster as iTree
    indexed.Dict:
    tree[key]                                                 0.117257 s  -> 1.835x (2.275x) faster as iTree
    xml.etree.ElementTree.Element:
    tree.find(key)                                              -> skipped too slow
    lxml.etree.Element:
    tree.find(key)                                              -> skipped too slow
    pyTooling.Tree.Node:
    tree.GetNodeByID(key))                                    0.158424 s  -> 1.359x (1.684x) faster as iTree
    treelib.Node:
    tree.get_node(key)                                        0.196832 s  -> 1.093x (1.356x) faster as iTree
    anytree.Node no test source was build (append())                             -> operation skipped


Performance analysis related related to trees with depth 100 and a size of 1000; access via  `__getitem__(key)` function:

::

    itertree.iTree (common target access):
    tree[key]                                                 0.012834 s
    itertree.iTree (tag_idx-specific access):
    tree.get.by_tag_idx(key)                                  0.003589 s ->  3.575x faster as common access
    build-in list:
    tree[tree.index(key)]                                     0.014637 s  -> 0.245x (0.877x) faster as iTree
    build-in dict:
    tree[key]                                                 0.001911 s  -> 1.878x (6.715x) faster as iTree
    collections.deque:
    tree[tree.index(key)]                                     0.014943 s  -> 0.240x (0.859x) faster as iTree
    collections.OrderedDict:
    tree[key]                                                 0.001984 s  -> 1.809x (6.468x) faster as iTree
    blist.blist:
    tree[tree.index(key)]                                     0.014691 s  -> 0.244x (0.874x) faster as iTree
    indexed.IndexedOrderedDict:
    tree[key]                                                 0.002619 s  -> 1.371x (4.900x) faster as iTree
    indexed.Dict:
    tree[key]                                                 0.002598 s  -> 1.382x (4.940x) faster as iTree
    xml.etree.ElementTree.Element:
    tree.find(key)                                            0.004508 s  -> 0.796x (2.847x) faster as iTree
    lxml.etree.Element:
    tree.find(key)                                            0.152578 s  -> 0.024x (0.084x) faster as iTree
    pyTooling.Tree.Node:
    tree.GetNodeByID(key))                                    0.004712 s  -> 0.762x (2.724x) faster as iTree
    treelib.Node:
    tree.get_node(key)                                        0.001022 s  -> 3.513x (12.559x) faster as iTree
    anytree.Node:
    search.find(tree, lambda node: node.name == key)                           17.558134 s  -> 0.000x (0.001x) faster as iTree
    next(dropwhile(lambda item: item.name != key, tree.children)               0.021549 s  -> 0.167x (0.596x) faster as iTree

Performance analysis related related to trees with depth 1000 and a size of 10000; access via  `__getitem__(key)` function:

::

    itertree.iTree (common target access):
    tree[key]                                                 1.230146 s
    itertree.iTree (tag_idx-specific access):
    tree.get.by_tag_idx(key)                                  0.327140 s ->  3.760x faster as common access
    build-in list:
    tree[tree.index(key)]                                     1.392063 s  -> 0.235x (0.884x) faster as iTree
    build-in dict:
    tree[key]                                                 0.169229 s  -> 1.933x (7.269x) faster as iTree
    collections.deque:
    tree[tree.index(key)]                                     1.410674 s  -> 0.232x (0.872x) faster as iTree
    collections.OrderedDict:
    tree[key]                                                 0.165853 s  -> 1.972x (7.417x) faster as iTree
    blist.blist:
    tree[tree.index(key)]                                     1.353723 s  -> 0.242x (0.909x) faster as iTree
    indexed.IndexedOrderedDict:
    tree[key]                                                 0.223637 s  -> 1.463x (5.501x) faster as iTree
    indexed.Dict:
    tree[key]                                                 0.222354 s  -> 1.471x (5.532x) faster as iTree
    xml.etree.ElementTree.Element:
    tree.find(key)                                            0.419544 s  -> 0.780x (2.932x) faster as iTree
    lxml.etree.Element:
    tree.find(key)                                            33.371158 s  -> 0.010x (0.037x) faster as iTree
    pyTooling.Tree.Node:
    tree.GetNodeByID(key))                                    0.497697 s  -> 0.657x (2.472x) faster as iTree
    treelib.Node:
    tree.get_node(key)                                        0.054741 s  -> 5.976x (22.472x) faster as iTree
    anytree.Node:
    search.find(tree, lambda node: node.name == key)                             -> skipped too slow
    next(dropwhile(lambda item: item.name != key, tree.children)               2.157126 s  -> 0.152x (0.570x) faster as iTree

Even that `iTree` is in base more related to a list we can see that the key access is on a very high level.


    * `dict` and all dict-like objects (inkl. indexed) - This build-in object is for sure the benchmark for al key
      related access objects. Suprsingly `iTree` is not far away it is less as two times slower.

    * treelib - the flatten storage structure of treelib allows very quick key access over the different levels of the
      tree. This structure is for in-depth access the clear winner.

    * other tree objects except treelib - all other tree objects are slower as `iTree` especially anytree
      is again incredible slow.

    * ElementTree - those objects are list-like and the search for tags is clearly slower then in `iTree`. For in-depth
      access the difference get less and the performance is comparable. The bottleneck is here clearly
      a level with a lot of items.


copy the tree
+++++++++++++

The copy function is the most difficult function related to the `iTree` architecture. The challenge is that in
`iTree`-objects the *one parent only principle is mandatory*. And therefore we cannot just copy the toplevel item we
must copy all the
items inside the tree too. The `itree.copy()` operation copies in fact all containing items and it copies
in the item the values too. But the values are copied just first level. Which makes the main difference to the
deepcopy() operation were we do a deepcopy() of the whole value objects too.

To make the comparison comparable we ensured in the first analysis (against `itree.copy()`) a comparable operation
in the objects. We copied the main object and additional we copied all children via:

    new_tree=tree.copy()
    new_tree.clear()
    new_tree.extend(((i[0],copy(i[1]),copy(i[2]) for i in tree))

We think this kind of copy of all items is the expected behavior in a nested tree.

Second we run the command `copy.copy()` here we do not consider if in this case children are copied or not.
For most of the other objects this in fact a top level copy only, we can see this in the huge speed difference.
In `iTree`  we use for comparison the command `itree.copy_keep_value()` which does not copy the values
and is a bit faster as `copy.copy() ~ itree.copy()`.


Performance analysis related to level 1 only trees with a size of 5000; for `copy()` functions:

::

    itertree.iTree:
    tree.copy()                                                                0.006894 s
    tree.copy_keep_value()                                                     0.006740 s
    copy.deepcopy(tree)                                                        0.008287 s
    build-in list:
    n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))  0.001564 s  -> 4.407x faster as iTree
    copy.copy(tree)                                                            0.000011 s  -> 618.330x faster as iTree
    copy.deepcopy(tree)                                                        0.010031 s  -> 0.826x faster as iTree
    build-in dict:
    n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items())) 0.009887 s  -> 0.697x faster as iTree
    copy.copy(tree)                                                            0.000024 s  -> 282.000x faster as iTree
    copy.deepcopy(tree)                                                        0.010486 s  -> 0.790x faster as iTree
    collections.deque:
    n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))  0.002446 s  -> 2.818x faster as iTree
    copy.copy(tree)                                                            0.000025 s  -> 268.518x faster as iTree
    copy.deepcopy(tree)                                                        0.014278 s  -> 0.580x faster as iTree
    collections.OrderedDict:
    n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items())) 0.011029 s  -> 0.625x faster as iTree
    copy.copy(tree)                                                            0.000483 s  -> 13.960x faster as iTree
    copy.deepcopy(tree)                                                        0.011297 s  -> 0.734x faster as iTree
    blist.blist:
    n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))  0.005918 s  -> 1.165x faster as iTree
    copy.copy(tree)                                                            0.000003 s  -> 2106.188x faster as iTree
    copy.deepcopy(tree)                                                        0.018452 s  -> 0.449x faster as iTree
    indexed.IndexedOrderedDict:
    n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items())) 0.013091 s  -> 0.527x faster as iTree
    copy.copy(tree)                                                            0.001601 s  -> 4.209x faster as iTree
    copy.deepcopy(tree)                                                        0.012605 s  -> 0.657x faster as iTree
    indexed.Dict:
    n=tree.copy();n.update((k,(copy(i[0]),copy(i[1])) for k,i in tree.items()))0.013222 s  -> 0.521x faster as iTree
    copy.copy(tree)                                                            0.001580 s  -> 4.265x faster as iTree
    copy.deepcopy(tree)                                                        0.012263 s  -> 0.676x faster as iTree
    xml.etree.ElementTree.Element:
    n=tree.copy();n.clear();n.extend((copy(i) for i in tree))                  0.001259 s  -> 5.476x faster as iTree
    copy.copy(tree)                                                            0.000013 s  -> 518.446x faster as iTree
    copy.deepcopy(tree)                                                        0.000878 s  -> 9.438x faster as iTree
    lxml.etree.Element:
    n=tree.copy();n.clear();n.extend((copy(i) for i in tree))                  0.006082 s  -> 1.133x faster as iTree
    copy.copy(tree)                                                            0.001318 s  -> 5.114x faster as iTree
    copy.deepcopy(tree)                                                        0.000973 s  -> 8.515x faster as iTree
    pyTooling.Tree.Node:
    copy.copy(tree)                                                            0.000004 s  -> 1604.714x faster as iTree
    copy.deepcopy(tree)                                                        0.055884 s  -> 0.148x faster as iTree
    anytree.Node:
    copy.copy(tree)                                                            0.000020 s  -> 333.653x faster as iTree
    copy.deepcopy(tree)                                                        0.021417 s  -> 0.387x faster as iTree


Performance analysis related to level 1 only trees with a size of 500000; for `copy()` functions:


::

    itertree.iTree:
    tree.copy()                                                                0.835458 s
    tree.copy_keep_value()                                                     0.796100 s
    copy.deepcopy(tree)                                                        0.952877 s
    build-in list:
    n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))  0.211637 s  -> 3.948x faster as iTree
    copy.copy(tree)                                                            0.012144 s  -> 65.553x faster as iTree
    copy.deepcopy(tree)                                                        1.215360 s  -> 0.784x faster as iTree
    build-in dict:
    n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items())) 1.120784 s  -> 0.745x faster as iTree
    copy.copy(tree)                                                            0.020014 s  -> 39.776x faster as iTree
    copy.deepcopy(tree)                                                        1.290939 s  -> 0.738x faster as iTree
    collections.deque:
    n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))  0.306400 s  -> 2.727x faster as iTree
    copy.copy(tree)                                                            0.012119 s  -> 65.691x faster as iTree
    copy.deepcopy(tree)                                                        1.625661 s  -> 0.586x faster as iTree
    collections.OrderedDict:
    n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items())) 1.347654 s  -> 0.620x faster as iTree
    copy.copy(tree)                                                            0.172031 s  -> 4.628x faster as iTree
    copy.deepcopy(tree)                                                        1.505746 s  -> 0.633x faster as iTree
    blist.blist:
    n=tree.copy();n.clear();n.extend(((i[0],copy(i[1]),copy(i[2])) for ....))  0.699678 s  -> 1.194x faster as iTree
    copy.copy(tree)                                                            0.000093 s  -> 8532.692x faster as iTree
    copy.deepcopy(tree)                                                        2.336833 s  -> 0.408x faster as iTree
    indexed.IndexedOrderedDict:
    n=tree.copy();n.update(k:(copy(i[0]),copy(i[1])) for k,i in tree.items())) 1.617339 s  -> 0.517x faster as iTree
    copy.copy(tree)                                                            0.294597 s  -> 2.702x faster as iTree
    copy.deepcopy(tree)                                                        1.535705 s  -> 0.620x faster as iTree
    indexed.Dict:
    n=tree.copy();n.update((k,(copy(i[0]),copy(i[1])) for k,i in tree.items()))1.549998 s  -> 0.539x faster as iTree
    copy.copy(tree)                                                            0.265445 s  -> 2.999x faster as iTree
    copy.deepcopy(tree)                                                        1.579321 s  -> 0.603x faster as iTree
    xml.etree.ElementTree.Element:
    n=tree.copy();n.clear();n.extend((copy(i) for i in tree))                  0.169371 s  -> 4.933x faster as iTree
    copy.copy(tree)                                                            0.008154 s  -> 97.634x faster as iTree
    copy.deepcopy(tree)                                                        0.132343 s  -> 7.200x faster as iTree
    lxml.etree.Element:
    n=tree.copy();n.clear();n.extend((copy(i) for i in tree))                  2.620617 s  -> 0.319x faster as iTree
    copy.copy(tree)                                                            1.134328 s  -> 0.702x faster as iTree
    copy.deepcopy(tree)                                                        1.031247 s  -> 0.924x faster as iTree
    pyTooling.Tree.Node:
    copy.copy(tree)                                                            0.000004 s  -> 204128.257x faster as iTree
    copy.deepcopy(tree)                                                        6.419806 s  -> 0.148x faster as iTree
    anytree.Node no test source was build (append())                             -> operation skipped

For in-depth copies over multiple levels we use just `deepcopy()`. But fo tre depth above 500 all othetr objects
except `iTree` raise RecursionError.

Performance analysis related to trees with depth 100 and a size of 1000; for `deepcopy()` function:

::

    itertree.iTree:
    tree.copy()                                               0.001347 s
    copy.deepcopy(tree)                                       0.002609 s
    build-in list:
    copy.deepcopy(tree)                                       0.003200 s  -> 0.815x (0.421x) faster as iTree
    build-in dict:
    copy.deepcopy(tree)                                       0.003270 s  -> 0.798x (0.412x) faster as iTree
    collections.deque:
    copy.deepcopy(tree)                                       0.003990 s  -> 0.654x (0.338x) faster as iTree
    collections.OrderedDict:
    copy.deepcopy(tree)                                       0.003983 s  -> 0.655x (0.338x) faster as iTree
    blist.blist:
    copy.deepcopy(tree)                                       0.005017 s  -> 0.520x (0.269x) faster as iTree
    indexed.IndexedOrderedDict:
    copy.deepcopy(tree)                                       0.006796 s  -> 0.384x (0.198x) faster as iTree
    indexed.Dict:
    copy.deepcopy(tree)                                       0.006855 s  -> 0.381x (0.197x) faster as iTree
    xml.etree.ElementTree.Element:
    copy.deepcopy(tree)                                       0.000184 s  -> 14.173x (7.318x) faster as iTree
    lxml.etree.Element:
    copy.deepcopy(tree)                                       0.008311 s  -> 0.314x (0.162x) faster as iTree
    pyTooling.Tree.Node:
    copy.deepcopy(tree)                                       0.012250 s  -> 0.213x (0.110x) faster as iTree
    treelib.Node:
    copy.deepcopy(tree)                                       0.011016 s  -> 0.237x (0.122x) faster as iTree
    anytree.Node:
    copy.deepcopy(tree)                                                        0.005676 s  -> 0.460x (0.237x) faster as iTree
    anytree.Node no test source was build (append())                             -> operation skipped


Performance analysis related to trees with depth 100 and a size of 1000; for `deepcopy()` function:

::

    itertree.iTree:
    tree.copy()                                                                0.014717 s
    copy.deepcopy(tree)                                                        0.027662 s
    build-in list:
    copy.deepcopy(tree)                                                          skipped -> RecursionError
    build-in dict:
    copy.deepcopy(tree)                                                          skipped -> RecursionError
    ...

We see that copying is a bit tricky for trees and when ever we really copy the tree in depth the performance of
`iTree` is quite good. But of course for top level copies `iTree` has disadvantages.

But even for `deepcopy()` operation outperforms `iTree` all the other objects (except xml.ElementTree which is quicker)
Because of the iterative copy implementation in `iTree` this even works for very deep trees
where all other objects fails (if the user does not increase the recursion limit).

Delete items
+++++++++++++++++++


Performance analysis related to level 1 only trees with a size of 50000; delete items:

::

    itertree.iTree (del by idx):
    del tree[0] for  ...                       0.039939 s
    itertree.iTree (del by idx):
    del tree[-1] for ...                       0.035988 s
    itertree.iTree (self by key):
    del tree[tag_idx] for ...                  0.345494 s ->  0.116x faster as idx access
    build-in list:
    del tree[0]                                2.156652 s  -> 0.160x faster as iTree
    del tree[-1]                               0.003988 s  -> 9.024x faster as iTree
    build-in dict:
    del tree[key]                              0.008149 s  -> 42.397x faster as iTree
    collections.deque:
    del tree[0]                                0.008281 s  -> 41.722x faster as iTree
    del tree[-1]                               0.009760 s  -> 3.687x faster as iTree
    collections.OrderedDict:
    del tree[key]                              0.010482 s  -> 32.959x faster as iTree
    blist.blist:
    del tree[0]                                0.019203 s  -> 17.992x faster as iTree
    del tree[-1]                               0.016717 s  -> 2.153x faster as iTree
    indexed.IndexedOrderedDict:
    del tree[key]                              2.171378 s  -> 0.159x faster as iTree
    indexed.Dict:
    del tree[key]                              2.175590 s  -> 0.159x faster as iTree
    xml.etree.ElementTree.Element:
    del tree[0]                                0.742840 s  -> 0.465x faster as iTree
    del tree[-1]                               0.006250 s  -> 5.758x faster as iTree
    lxml.etree.Element:
    del tree[0]                                0.011022 s  -> 31.346x faster as iTree
    del tree[-1]                               0.011105 s  -> 3.241x faster as iTree
    treelib.Node:
    tree.remove_node(key)                      2.356795 s  -> 0.147x faster as iTree

The comparison related to item delete operation is really difficult. And we see very different behavior for
the executed cases. The results are very wide variance (e.g. dict is 40 times quicker as ìTree`and indexed dicts
are 6 times slower).

We must also say that for a size of 50000 items for some classes the time gets already critical (more then 2 seconds)
and surprisingly `list` is also in this category for first item delete. We do not show the results for 500000 items
here,
because many classes would have bin skipped because of the time limit. The situation is here that the operation for
those classes gets a lot more difficult if the size grows.

 We ran the following cases:

* list-like delete first element (index 0) -> compared with same operation in `iTree`
* list-like delete last element (index -1) -> compared with same operation in `iTree`
* dict-like delete per key -> compared with same operation in `iTree`


For PyToolingTree and anytree we did not found a delete function for items.

For the `iTree`-class the `__delitem__()` method is very difficult. We must delete the item in the main list
and in the family. We must consider different cases and in case of local items which overload linked items we must
replace in stead of delete. But even though the speed of the operation (in the level 1 example is good. But we must say
that the class take big advantages of the good delete performance of the blist class (if package is not installed
this operation will be much worse).

* `list` - "our all time winner" performance for this operation not very well. We see that especially the delete of
  the first items is very costy (all items must be reindexed). For the last items the list is quicker then `iTree`.

* `dict` and `OrderedDict` - are clearly much quicker then `iTree` (more then 40-30 times) and
  round about 5 times quicker then delete per index in `iTree`.

* `deque` - performance very well and much quicker then `iTree`. Suprisingly the delete from the end is slower
  then the delete from the beginning.

* Indexed Dicts - The indexed dicts are much slower then `iTree`

* xml-ElementTree -  behaves like list

* lxml ElementTree -  is clearly quicker then `iTree`

* treelib  - is much slower then `iTree` but we must say we didn't find here a way for indexed based deletes,
  we used a deleted targeted key

Tree` operations
+++++++++++++++++++

Finally we just ran an analysis of the `iTree` object itself so that we have an overview of the main functionalities.

We target a lot of functions which are only available in `iTree` and where we found no counterpart in the other objects.

Performance analysis related to level 1 only trees with a size of 500000:

::

    tree=iTree("root",subtree=[...])                                           0.574042 s
    tree=iTree(); tree.append()...                                             0.683904 s ->  0.839x faster as extend()
    tree=iTree(); tree.insert()...                                             0.831075 s ->  0.823x faster as append()
    tree.load_links()            # 500000 linked-items loaded                  0.919389 s
    tree.get.by_idx(idx)         # specific absolute index access              0.097410 s
    tree[idx]                    # common absolute index access                0.145026 s ->  0.672x faster as specific
    tree.get.by_idx_slice(slice) # specific absolute index slice access        0.012604 s
    tree[slice]                  # common absolute index slice access          0.012821 s ->  0.983x faster as specific
    tree.get.by_tag_idx(tag_idx) # specific tag-idx access                     0.206083 s ->  0.473x faster as get_by_idx()
    tree[tag_idx]                # common tag-idx access                       0.256707 s ->  0.803x faster as specific
    tree.getitem_tag_idx_slice((tag,fam_idx_slice)) # specific tag_idx slice   0.001470 s
    tree[(tag,fam_idx_slice]     # common tag_idx slice                        0.001866 s ->  0.788x faster as specific
    tree.get.by_tag(tag)         # specific family-tag access                  0.263708 s
    tree[tag]                    # common family-tag access                    0.350820 s ->  0.752x faster as specific
    tree.dumps()                 # serialize into string (json)                0.996655 s
    pickle.dumps(tree)           # serialize via pickle                        0.647319 s

Performance analysis related to trees with depth 100 and a size of 1000:

::

    tree=iTree(); tree.append()...                                             0.013060 s
    tree.load_links()            # 10 linked-items loaded                      0.033486 s
    tree.get.by_idx(idx)         # specific absolute index access              0.193028 s
    tree[idx]                    # common absolute index access                1.039325 s ->  0.186x faster as specific
    tree.get.by_tag_idx(tag_idx) # specific tag-idx access                     0.344499 s ->  0.560x faster as get_by_idx()
    tree[tag_idx]                # common tag-idx access                       1.247241 s ->  0.276x faster as specific
    tree.get.by_tag(tag)         # specific family-tag access                  0.307431 s
    tree[tag]                    # common family-tag access                    2.242912 s ->  0.137x faster as specific
    tree.dumps()                 # serialize into string (json)                0.039315 s

The `insert()` operation based on the internal usage of the blist-package is impressive
only 20% slower compared to `append()`.

This analysis shows on first level the common access can be up to two times slower as the specific item access. For
in-depth access the difference grows.

Serialization via pickle is quicker compared to the json-serialization used by `iTree().dumps()` but for deep trees
RecursionErrors will appear.

#################
Final summary
#################

From the functional point `iTree` ,has the following functions that are not found in most of the other objects:

* linking of branches and overwrite local items
* store the structure in a file by serializing all value objects too (we do not consider here something like pickle)
* in-depth access and iterators

If the objects have such solutions too it will be mentioned.

iTree vs. list like objects
++++++++++++++++++++++++++++

Related to performance we can see that the
internal structure of `iTree` is also list like. But we have some overhead to handle
(tag family related management) so we are for most operations a bit slower than the list like objects. And we must
consider here that most of this objects are implemented on c-level which gives an additional boost.

For the un-typic operations like key-access (were lists must do at least a search by iterating over all elements)
we see that `iTree` behaves much quicker. We think that such operations are mandatory for trees. As we see in the
other tree like objects the targeting related to keys is much more important than index access. For us this is the main
reason why list-like objects are not fitting to the requirements of tree structures.

We must also remark here that in the comparison we had to find a way to use the list-like objects as nested objects.
We stored in each item a tuple of (key,value,subtree). A pure flat list of values and not containing such tuples
would be much quicker. But this is not the use-case of a tree were you need the possibility of subtrees.

Focusing on functional limitations we must first see that list are not made for nested, in-depth structures. In our
comparison we had to use a helper by putting tuples in the values in which as last item again a list for the
deeper sub-structure was placed. So with out such a help object and with addtional methods for in-depth
functions lists can not be used for trees out of the box.

And as already said the in our opinion mandatory key/item access is very slow in lists.

In lists any object-type can be used as key if stored in the helper structure (tuple).

iTree vs. dict like objects
++++++++++++++++++++++++++++

Talking about performance the speed of the standard dict is not so far ahead from `iTree` as we can see it in lists.
Especially for structures with a large number of items dicts getting relatively slower.

The other non-standard dicts are only in some cases a bit quicker as `iTree`.

The non typic access via index is slow except for the indexed dicts. But even those are slower
in index access as `iTree`. And we must they that index acces in dicts is quicker as key-access in lists
(for larger number of items).

Dict objects contains normally only level 1 children and as in lists an additional helper object is
required to store sub-dicts. And we can see that for in-depth access most of the dicts are slower then `iTree`.

The indexed dicts of the indexed module are an interesting alternative to `iTree`. We can imagine
that those those objects would be a good
base for tree structures. But in practice we can see that those objects behave slower then `iTree` in most cases
and therefore there we see no reason to use those objects for trees.

When we talk about functional limits of dicts compared to `iTree` we see as explained that they are not
out of the box nested.

Second they are not capable to store an item with same key multiple times as you can do
it in `iTree` but also in most of the other tree structures (like xml ElementTree).

The order of the items is not always kept (depends also on the python version) but even if the order is kept the change
of the order is not possible or difficult.

In dicts any hashable type can be used as key (as it is for tags in `iTree`.

iTree vs. ElementTree
++++++++++++++++++++++

The ElementTrees gave a very ambivalent picture in general we sse that the object from the xml package is designed
for quicker instancing and longer access times compared to the one from the package lxml.

If we look just on the performance we can say that index related functions are very quick better or on same level
as `iTree` depending which variant you are looking on. In mean we must say we are on same level.  The key related
access (tag search) is slower as we have it in `iTree`.

It's not shown here but the storage into files (save/load to/from xml) is quicker then the related functions we have
in `iTree` (json files). But as we will see we have normally just strings stored in the object (tag,value).

In general we must say that in those objects we have a real tree functionality realized we have also a larger range
of functionalities available then we have it in `iTree`. Especially we have in-depth operations like iterators
or access. We have also the very powerful xpath search function. And as in `iTree`the user can store the tag
mutliple times in `ElementTree`.

But those trees are made for xml storage and this means they normally handle just strings.
If other objects stored in the values a special serializing must be adapted
(which will decrease the performance).
Especially in the tags the limits are even higher, no special characters can be
used there (e.g. spaces are not allowed in xml-tags).
The possibility of `iTrees` related to the usage any hashable object as a tag can not be realized
in those objects (out of the box).

In the value (in case of ElementTree attrib) we have a dict like structure and the user must use it he
cannot exchange the dict-like behavior of the value object.

Finally we can say those alternatives are only good as long as the user just tags/stores string like objects.

iTree vs. PyToolingTree
++++++++++++++++++++++++

Related to performance we can say that the two objects are on same level. (On PytToolingTree docu they
mention 2 times quicker performance but this was related to older version of `iTree`).

In our opinion the focus related access in PyToolingTree is more in the direction of key-access as
index access (in last topic the object is slower).

The overall functionality of this object (Version 4.0.1) is very limited compared to `iTree`. We did not checked
all details here but we see the following differences. The item used IDs and those IDs must be unique this means
you cannot store same key multiple times (like in `iTree`). We do not see any special in-depth functions all
this access must be programmed outside of the object.

The storage into files (serializing) does not exists.

Summary for specific implementations we see this as an alternative. But we see a much bigger
functionality in `iTree` with same or even better performance.

iTree vs. treelib
++++++++++++++++++

Treelib was integrated relative late in the comparison and some analysis are missing. The structural
setup is completely different (nested items are stored in a flat list) and some functions cannot be realized
(in our opinion e.g. nested index access).

On performance side we can see that the object is slower for nearly any access type and most of the other functions.
Because of the structure we see that the whole tree iteration is very quick but we do not see that the order is really
kept here.

In general we found that the object is very difficult to be used. And because of the architecture
we see functional limitations (e.g. in-depth index access). also we do not see real in-depth functionalities.

From our point of few there is no reason to take this alternative. The object has functional limits, it's slower and
from our experience difficult to use. The documentation is even incomplete from our point of view.

iTree vs. anytree
++++++++++++++++++

The recommended object for trees for many users is anytree. And before we started with itertree implementation we
thought this object might match to our requirements. But as you can see in the performance analysis the behavior is
really disappointing.

The object behaves in all directions very slow. And even in flat trees with more then 5000 elements
the objects gets unusable slow.
The bad performance was shortly discussed with the author: https://github.com/c0fec0de/anytree/issues/169.

Some case could not work at all the objects seems to block (even for very
simple operations e.g. index access on flat trees with 50000 items (I had to wait some minutes to create such trees)).

Additionally we see limitations in anytree:

    * You can only use string based tags (not hashable objects like in itertree).
    * functional properties of a specific item do not exists (iTree.idx, `iTree`.idx_path, ....)
    * But the main issue from our point of view is the really bad performance in case of huge trees
      (Especially search for item.name is very slow)
    * filtering is very slow and not as powerful as in itertree

In general the functionality in anytree is much less and not comparable with `iTree`.

Finally we must say this is the only package which we found not usable at all. It is very slow and
blocks in some operations. We cannot recommend to use this package.


Other arguments for `iTree`
++++++++++++++++++++++++++++

One main functionality in `iTree` that is not found in any of the other objects is the possibility to link from one tree
to the other tree. This "inheritance" of subtrees seams to be a unique feature.

Also the possibility of marking elements as read-only for specific functions (value read-only, subtree read-only)
is unique.

Another thing we do not find one to one in the other objects ís the possibility to store out of the box the trees
in files. Especially if we consider that in `iTree` the value objects are serialized too even if they are complex
types like (lists, dicts, data-models or even numpy arrays).

The original requirement to develop itertree was the target to store configurations in a more efficient way
compared with ini-files, xml-files, json-files, yaml-files. We wanted to extend a tree like data structure
with the possibility of linking sub-trees in a main-tree by linking from different sources. Additionally we like
to overload in the linked tree some items if required.
We can say itertree contains those functionalities and we do not know any other object supporting this.

But beside the orignal starting point we extended the object to a generic python object for trees. It contains a very
pythonic standard interface (lists/dict). And can be used for many other proposes too.

As you can see from the naming iterations are supported in a wide range. Especially filtering is important. Here we can
find another unique feature for nested trees we did not found in the other objects this is the possibility of
hierarchical filtering. The filter will not consider the subtree if the parent does not match. In general for most
objects such a filter can be programmed from the outside too. But this has disadvantages if this is not done inside
the iterator and it makes additional effort that is not needed in ìtertree.

If the user knows to use the iterators (see e.g. itertools) very efficient code can be created especially if you want
to dive inside the tree. The iterators can be cascaded and instanced extremely quick. The iteration runs only
finally in the moment you consume the iterator. This is much quicker then instances lists in many steps in between
which you iterate multiple times. Those iterators are widely used in itertree and can be used from the outside too. In
many of the other objects the delivered objects are lists or tuples and not iterators which is a big disadvantage
from our point of view.


