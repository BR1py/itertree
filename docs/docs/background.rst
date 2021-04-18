.. _background:

Background information about itertree
=====================================

The itertree package is originaly developed to be used in an internal test-system configuration and measurement environment. In this environment we must handle a huge number of parameters and attributes which are configured via a Graphical user Interface. The connection of the data and the GUI is realized via the coupled_obj function we have in iTree.

To find the best solution we made a lot of testing (check of the already available packages and we checked other implementation alternatives (like sorted or ordered dicts) but we came to the conclusion that it makes sense to develop an own, new package to match all our requirements.

Based on the tests we made the architecture is finally done on a list based implementation with a parallel managed dict that contains the TagIdx based information like tag-families and the related indexes. To speed up large lists we recommend to use blist package. When the itree package is imported we test if the package is available.

To speed up the instanciating process some information is only generated later on and only in case it is really needed.

When profiling the different core methods the time consumption can be seen in more detail:
::
    100000    0.220    0.000    0.473    0.000 itree_main.py:100(__init__)
    100000    0.053    0.000    0.076    0.000 itree_main.py:266(__getitem__)
    100000    0.080    0.000    0.110    0.000 itree_main.py:318(__delitem__)
    100000    0.178    0.000    0.186    0.000 itree_main.py:436(__iadd__)
    100000    0.223    0.000    1.379    0.000 itree_main.py:866(copy)
    100002    0.234    0.000    0.263    0.000 itree_main.py:995(extend)
   

During this profiling run we see that copy() is the most costly operation, next is __init__().

We do not use much caching in iTree objects only the index values iTree.idx and the tag related index are cached for quicker finding of the item in the list.

