# itertree python package


## Welcome to itertree python package. 

0.7.2 --BETA-- -> but implementation is already a release candidate (all interfaces are fixed)!

Do you like to store your data some how in a tree like structure? Do you need good performance, a rich feature set and the possibility to store your data permanently in files?

Give the itertree package a try!

You might have a look into the feature list:

* trees can be structured in different levels (nested trees: parent->children->sub-children->sub-sub-....)
* identification tags can be strings or any hashable object
* identification tags must not be unique (same tags are enumerated and collect in a tag-family)
* keeps the order of the added children
* the data is stored in a protected data structure where data models can be used to evaluate the given data values
* Linking: An iTree item can be linked to another itertree file (that is loaded and integrated in the local itertree structure)
* Iterators and searches (find) can be filtered by a given query (item_filter)
* standard export/import to JSON (incl. numpy and OrderedDict data serialization)
* designed for performance, trees with over 100000 nodes are supported
* it's a pure python package (should be therefore usable in all embedded environments too)

The access to the items of the iTree object delivers two type of returns depending on the target:

*  address a single, unique target item (e.g. by giving the index) -> the single matching  iTree item will be returned
* addressed target was not unique (e.g. slice was given) -> an iterator over the selected  iTree items is delivered 

We deal here a lot with iterators and it's recommended to understand the powerful itertools package as a partner package to take full advantages of the itertree possibilities.  

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the itertree package.

```bash
pip install itertree
```

The package has no dependencies to other external packages. But some of the tests can only be performed if numpy is installed. Also the comparison tests with other packages are obviuosly only possible if the other packages are installed.

## Usage

```python
>>>from itertree import iTree
>>.
>>>root = iTree('root')
>>>root.append(iTree('child')
>>>root[0]+=iTree('sub-child')
>>>root+=iTree('child2',data='1. child2')
>>>root+=iTree('child2', data='2. child2')
>>>
>>>root.render()
iTree('root')  
└──iTree('child')  
   └──iTree('sub-child')  
└──iTree('child2', data='1. child2')   
└──iTree('child2', data='2. child2')  

```

Every iTree node in the itertree stores the related sub-structure (iTree children) and the related data in the internal data structure.

The itertree solution can be compaired with nested dicts or lists. Other packages that targeting in the in the same direction are anytree, xml.ElemetTree, sorted_dict, treenode. In detail the features set or the usage behavior of itertree is different and it focus on other features but in parts the functionality is comparable. An overview of the diffrences, advantage and disadvantages related to the other packages is given in the chapter Package Comparision in the main documentation.

The original implementation was realized with python 3.5 and it was tested with python 3.5 and 3.9. It should work in all python 3 environments.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Documentation

The detailed package documentation can be found here:
https://itertree.readthedocs.io/en/latest/#

## Package structure and files 

The structure of folder and files related to this package looks like this:

* itertree (main folder)

   * __ init __.py
   * itree_main.py
   * itree_helpers.py
   * itree_data.py
   * itree_serialize.py
   * _itree_internal.py

   * examples

      * itree_performance.py
      * itree_profiling.py
      * itree_data.py

## Getting started, first steps 

### Import and first itertree

All important classes of the package are puplished by the __ init__.py file so that the functionality of iterree in your code can be reached by simply importing:

```python
>>>from itertree import *
```
    
The itertrees are build by adding iTree node-objects to a iTree-parent-object (This means we do not have an external tree generator or factory).

The most efficient way to add single items in an itertree is to use the += operator (__ iadd__()) which adds the righthandside item to the lefthandside item.

```python
>>>root=iTree(tag='root') #first we create a root element
>>>root+=iTree(tag='child',data=0)
>>>root+=iTree(tag=(0,1,2)) #tuples can be used as tags because they are hashable objects
>>>root+=iTree(tag='child2')
```
    
It exists a huge set of methods to change the treestructure by appending, extending or inserting  items in an iTree object.

### Tags

Each iTree-object must have a tag. For tags you can use any hashable object except integers and iTreeTagIdx objects (These objects are used for adressing in access operations and can therefore not be used as tags). When using string tags more search functionalities are available.

Different than the keys in dictionairies the given tags must not be unique:

```python
>>>root+=iTree(tag='child',data=1)
>>>root+=iTree(tag='child',data=2)
```
    
Internally the equal tags are enumerated and collected in a tag-family. They can be reached and addressed by the iTreeTagIdx-object.

```python
>>>print(root[iTreeTagIdx('child',1)])
iTree(tag='child', data=1)
```

Beside the iTreeTagIdx the items can be reached also by index. In the next example we add a sub-item to the index addressed item:

```python
>>>print(root[2])
iTree(tag='child2', data={})
>>>root[0]+=ITree(tag='subchild')
>>>print(root[0][0])
ITree(tag='subchild')
```

HINT: The addressing via index and via iTreeTagIdx objects are the quickest ways to reach a single item in the itertree.

### Iterators

In itertrees iterators used in a very wide range. When ever a set of items are the result of an operation itertree will deliver an iterator over the set. We never deliver a list or an iterable object. The user ist free to create those objects (e.g.a list) when needed from the iterator (use list()). Also the methods can be feeded by iterators (where ever an iterable makes sense). 

After the tree is generated we can iterate over the tree:

```python 
>>>a=[item for i in root] # iter over the children
>>>print(a)
[iTree(tag='child',data= 0, subtree=[iTree(tag='subchild')]), iTree()tag=(1,2,3)), .....
>>>b=[item for i in root.iter_all()] # iter over all items in the tree (deep iter)
>>>print(b)
[iTree(tag='child',data=0, subtree=[iTree(tag='subchild')]), iTree(tag='subchild'), .....
```

The iterators and find functions of itertree can use item_filters to search for specific properties (create queries).
 
```python
>>># '**' is a wildcard for any item; c is an iterator
>>>c=root.find_all(['**'],item_filter=root.create_data_value_filter(2))  
>>>print(list(s)) # to print iterator content we must create a list
[iTree(tag='child',data=2)]
```

HINT: In case a function returns multiple elements (multi target) itertree delivers always an iterator. The advantage is that we can create very quick results even when the item number is very high. For efficent usage the user should continue use iterators (e.g. see itertools package) to reach the final result. Normally only at the end of the whole operation the iterator should be "realized" by looping over the items or casting into a list. Even single item acces can be best realized via itertools.isslice() operation.

### Data

The data handling can be done over set and get functions, if no specific key is given the "__ NOKEY__" element in the internal data structure will be adressed. This is very helpful in case you want to store just one data object in the iTree object. By adding explicit keys multiple data elements can be stored in the internal dict structure of one iTree object (attributes). Additionally  a data-model can be defined so that only matching data values will be accepted in the data structure. The data access is possible via direct methods (get(),set(),check(), pop()) in the iTree.

```python
>>>root.set(1) # implicit key
>>>print(root.d_get())
1
>>>root.d_set('mykey':2) # explicit key
>>>print(root.d_get()) # the "__NOKEY__" data item is untouched by the last operation
1
>>>print(root.d_get('mykey'))
2
```
    
### Storage and Serialization

At least the itertree can be stored in a file and reconstructed from a file. We can also link an item to a specific item in an other file.

```python
>>>root.dump('data.dtz') # itz is the recommended file ending for the zipped itertree file
>>>root2=root.load('data.itz') # any available iTree object can be used for creating a new iTree containing the loaded file data
>>>print(rrot2==root)
True
>>>root+=iTree('link',link=iTreeLink(data.itz',iTreeTagIdx(child',0))) # From the given target node all children will be integrated
```

The standard serialization is done into a zipped JSON format and can handle an extended  set of datatypes that might be stored in the data structure of iTree (e.g. numpy.ndarray objects can be serialized too). The serializer can be additionally extended by the user by overloading the standard classes. Also the output format can be modified by same mechanism. The default files created are zipped and secured by a checksum (default ending is ".itz").
      
