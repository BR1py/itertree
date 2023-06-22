# -*- coding: utf-8 -*-
"""
This code is taken from the itertree package:
https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license incl. human protect patch:

The MIT License (MIT) incl. human protect patch
Copyright © 2022 <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

Human protect patch:
The program and its derivative work will neither be modified or executed to harm any human being nor through
inaction permit any human being to be harmed.

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information see: https://en.wikipedia.org/wiki/MIT_License


This part of code contains the specific get methods for the iTree object

The specific getters are quicker compared with the common ones we have in iTree (__getitem__(); get(); get_single())
"""

from .itree_helpers import BLIST_ACTIVE,NoTarget,TagIdx
from .itree_private import _iTreePrivate

class _iTreeGetitem():
    __slots__ = ('_itree','getitem_by_idx','_getitem_fam','_get_fam')
    # To win some speed we set self._itree after init of the class in the main iTree object

    NoneSlice=slice(None)
    def __init__(self,itree):
        self._itree=itree

    @staticmethod
    def _get_child_ren(itree, target):
        """
        Main getter for items

        In case the given targets is a absolute index or a key (tag,family-index) pair the method will
        deliver a unique item back. This operation is prioritized over the other operations.

        For all other targets the method will deliver a list with the targeted items as result.

        In some cases an empty list might be delivered and no exception might be raised
        (e.g. filter query delivers no match).

        In case user likes to have other return behaviour he might check the other available get methods
        ( `get()`, `get_single()`) or he might also use the itertree helper method `getter_to_list()` to
        convert any of the possible results into a list.

        :except: In case of no match (even if a part is not matching (e.g. one index in an index-list) the
                 method will raise
                 a KeyError (no matching target given); IndexError (no matching index given) or
                 ValueError (no valid type of target given).


        :type target: Union[int,tuple,list,slice]
        :param target: target object targeting a child or multiple children in the ´iTree´.
                       Possible types are:
                           * *index* - absolute target index integer (fastest operation)
                           * *key* - key tuple (family_tag, family_index)
                           * *index-slice* - slice of absolute indexes
                           * *key-index-slice* - tuple of (family_tag, family_index_slice)
                           * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                           * *key-index-list* - tuple of (family_tag, family_index_list)
                           * *tag* - family_tag object targeting a whole family
                           * *tag-set* - a set of family-tags targeting the items of multiple families
                           * *itree_filter* - method (callable) for filtering the children of the object
                           * *all-children* - if build-in `iter` or ...(Ellipsis) is given a list
                                              of all children will be given (same like
                                              `list(itree.__iter__())`)

        :rtype: Union[iTree,list]
        :return: Target was *index* or *key* -> one `iTree` item will be given;
                 for all other targets a list will be delivered.
        """
        if itree:
            t = type(target)
            if t is tuple:
                try:
                    # check for key as quick as possible!
                    fam_tag, fam_idx = target  # unpack to be sure we have a tuple of two items
                    if fam_idx is ...:
                        return False,itree._getitem_fam(fam_tag)[:]
                    # key, family-index or  key, family-index-slice:
                    return True,itree._getitem_fam(fam_tag)[fam_idx]
                except TypeError:
                    try:
                        family = itree._getitem_fam(fam_tag)
                        return False,[family[i] for i in fam_idx]
                    except:
                        try:
                            return False, itree._getitem_fam(target)
                        except:
                            raise ValueError('Given target {} is invalid'.format(repr(target)))  # from e
                except IndexError:
                    try:
                        return False,itree._getitem_fam(target)
                    except:
                        raise IndexError(
                            'Given family-idx of target {} not found in iTree'.format(repr(target)))  # from e
                except:
                    try:
                        return False,itree._getitem_fam(target)
                    except:
                        if 'fam_idx' in locals():
                            raise KeyError(
                                'Given target {} invalid or not found in iTree'.format(repr(target)))  # from e
                        else:
                            raise ValueError('Given target {} is invalid'.format(repr(target)))  # from e
            elif t is int:
                # absolute index or absolute index-slice
                try:
                    return True,itree.getitem_by_idx(target)
                except IndexError:
                    try:
                        # Maybe we have a tag that matches?
                        return False,itree._getitem_fam(target)
                    except:
                        raise IndexError(
                            'Given abs-idx in target {} is out of range'.format(repr(target)))  # from e
            elif t is slice:
                # absolute index or absolute index-slice
                try:
                    return False,itree.getitem_by_idx(target)
                except IndexError:
                    try:
                        # Maybe we have a tag that matches?
                        return False,itree._getitem_fam(target)
                    except:
                        raise IndexError(
                            'Given abs-idx in target {} is out of range'.format(repr(target)))  # from e
            elif t is TagIdx:  # downward compatibility
                fam_tag, fam_idx = target  # unpack
                return True,itree._getitem_fam(fam_tag)[fam_idx]
            elif t is set:
                # tags-set
                result = []
                for tag in target:
                    result.extend(itree._families[tag])
                if result:
                    return False,result
                raise KeyError('No matching item found')
            elif t is list:
                # multiple targets given they will be combined in one list
                result = []
                for sub_target in target:
                    r = itree[sub_target]
                    if type(r) is list:
                        result.extend(r)
                    else:
                        result.append(r)
                if result:
                    return False,result
                raise KeyError('No matching item found')
            elif target is Ellipsis:
                return False,itree.getitem_by_idx(itree._NoneSlice)  # full slice is incredible fast on blists
            elif callable(target):
                if target is iter:
                    # give all items
                    return False,itree.getitem_by_idx(itree._NoneSlice)
                # filter given?
                try:
                    return False,filter(target, itree)
                except Exception:
                    if "<lambda>" in str(target):
                        # We try to identify in this case which child made the troubles
                        for c in itree:
                            try:
                                target(c)
                            except Exception:
                                raise TypeError('lambda: raised an exception in filter-calculation, the %i. child %s'
                                                ' is incompatible with the calculation' % (c.idx, str(c)))
            result=itree._get_fam(target)
            if result is not None:
                return False, result[:]
        raise KeyError('Given target: %s not found in iTree!' % repr(target))

    def __call__(self, target=NoTarget, *target_path, default=Exception,target_type=None):
        """
        Call via **iTree().get()**
        
        Main get method for items that supports in-depth level-wise access too.

        If only one parameter is given get behaves like `__getitem__()` except that a default parameter can be given
        so that it will be delivered (the normal method would raise an exception in this case).
        In case no default is given the exception will be raised too.

        .. warning::  The default parameter must be given as a keyword argument only e.g.:`get(1,default=None)`.
                       All
                       unnamed arguments given will always be interpreted as a target definitions!

        In case the method got more than one unnamed argument an in-depth target access will be performed. Each
        parameter will target in this case the next nested level of the tree.

        The method can be seen as a replacement of the operation
        `self[target_deep[0]][target_deep[1]]...[target_deep[-1]]`

        .. note::  But be aware that the results in the different levels might not be unique and therefore in detail
                   the
                   method will behave different as the simple direct targeting (which will raise
                   an exception in this case). This method will create an iterator of all (branched) findings in
                   the deepest targeted level instead.

        In this case the method will deliver an iterator of all the findings in the mostlowest level targeted.
        The iterator is always flatten even that in higher levels we might have multiple findings.

        E.g. the user might have build a tree like this:

        ::

            >>> root_tree.render()
            iTree('root', value=0)
             > iTree('sub', value=1)
             .  > iTree('subsub', value=5)
             > iTree('sub1', value=2)
             .  > iTree('subsub', value=6)
             > iTree('sub2', value=3)
             .  > iTree('subsub', value=7)
             > iTree('sub', value=4)
             .  > iTree('subsub', value=8)
             >>> get('sub','subsub')
             [iTree('subsub', value=5), iTree('subsub', value=8)]

        The reason for this result is that the first match is not unique and so the sub-items in the target
        levels are combined into on flatten result.

        The return of this method can be the following:

            1. Pure index and key list is given -> single target -> iTree object should be delivered
            2. list of all found items
            3. No match found an KeyError or IndexError will be raised

        :except: In case no matching item is found a KeyError or IndexError is raised. In case of invalid targets
                 TypeError or ValueError will be raised.

        :type target: Union[int,tuple,list,slice]
        :param target: level 0 target object targeting a child or multiple children in the ´iTree´.
                       Possible types are:

                           * *index* - absolute target index integer (fastest operation)
                           * *key* - key tuple (family_tag, family_index)
                           * *index-slice* - slice of absolute indexes
                           * *key-index-slice* - tuple of (family_tag, family_index_slice)
                           * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                           * *key-index-list* - tuple of (family_tag, family_index_list)
                           * *tag* - family_tag object targeting a whole family
                           * *tag-set* - a set of family-tags targeting the items of multiple families
                           * *itree_filter* - method (callable) for filtering the children of the object
                           * *all-children* - if build-in `iter()` or ... (Ellipsis) is given a list of all
                             children will be given (same result as `list(itree.__iter__())` )


        :type *target_path: Parameter pointer to iterable
        :param *target_path:  in-depth targets iterable of targets for the different levels 1-n
                                The supported targets in each level are (same like `__getitem__()`:

                                   * *index* - absolute target index integer (fastest operation)
                                   * *key* - key tuple (family_tag, family_index)
                                   * *index-slice* - slice of absolute indexes
                                   * *key-index-slice* - tuple of (family_tag, family_index_slice)
                                   * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                                   * *key-index-list* - tuple of (family_tag, family_index_list)
                                   * *tag* - family_tag object targeting a whole family
                                   * *tag-set* - a set of family-tags targeting the items of multiple families
                                   * *itree_filter* - method (callable) for filtering the children of the object
                                   * *all-children* - if build-in `iter()` or ... (Ellipsis) is given a list of all
                                     children will be given (same result as `list(itree.__iter__())` )


        :param default: The parameter must be given as keyword parameter! The object given will be
                        delievred in case of issues. If the parameter is not set (`==Exception`) exceptions will
                        be raised in case of issues.

        :rtype: Union[iTree,list]
        :return: iTree object or list of objects
        """
        try:
            if target_path:
                # create locals
                get_child_ren=self._get_child_ren
                cls = self._itree.__class__
                # access first item
                single,item_s = get_child_ren(self._itree,target)
                for t in target_path:
                    # in depth access
                    if single:
                        # if result is a list but we have just one item inside it is also unique
                        # and we reduce to the single item
                        single,item_s = get_child_ren(item_s,t)
                    else:
                        single = False
                        result = []
                        for item in item_s:
                            try:
                                is_single,r = get_child_ren(item,t)
                                result.append(r) if is_single else result.extend(r)
                            except:
                                pass
                        item_s = result
                if item_s.__class__ is cls:
                    return item_s if single else [item_s]
                elif item_s:
                    return list(item_s)
                else:
                    raise KeyError('No item found')
            elif target is NoTarget:
                return self._itree
            else:
                is_single,r=self._get_child_ren(self._itree,target)
                return r if is_single else list(r)
        except (ValueError, KeyError, IndexError,AttributeError) as e:
            if target is NoTarget:
                return self
            return _iTreePrivate._raise_exception(e) if (default is Exception) else default

    def single(self, target, *target_path, default=Exception):
        """
        Call via **iTree().get.single()**
        
        In general the methods does same like the "normal" `get()` but the method delivers only single (unique) results.
        In case `get()` delivers multiple items this method will raise an Exception or delivers
        the default value (if defined).

        .. note:: In case the match contains a list with only one element the result is unique too. The method will
                  unpack the unique item from the iterable and return it in this case.

        :except: If default parameter is not set an KeyError or IndexError will be raised. If result is not
                 unique a ValueError will be raised

        :type target: Union[int,tuple,list,slice]
        :param target: level 0 target object targeting a child or multiple children in the ´iTree´.
                       Possible types are:

                           * *index* - absolute target index integer (fastest operation)
                           * *key* - key tuple (family_tag, family_index)
                           * *index-slice* - slice of absolute indexes
                           * *key-index-slice* - tuple of (family_tag, family_index_slice)
                           * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                           * *key-index-list* - tuple of (family_tag, family_index_list)
                           * *tag* - family_tag object targeting a whole family
                           * *tag-set* - a set of family-tags targeting the items of multiple families
                           * *itree_filter* - method (callable) for filtering the children of the object
                           * *all-children* - if build-in `iter()` or ... (Ellipsis) is given a list of all
                             children will be given (same result as `list(itree.__iter__())` )

        :type *target_path: Parameter pointer to iterable
        :param *target_path:  in-depth targets iterable of targets for the different levels 1-n
                              The supported targets in each level are (same like `__getitem__()`:

                                   * *index* - absolute target index integer (fastest operation)
                                   * *key* - key tuple (family_tag, family_index)
                                   * *index-slice* - slice of absolute indexes
                                   * *key-index-slice* - tuple of (family_tag, family_index_slice)
                                   * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                                   * *key-index-list* - tuple of (family_tag, family_index_list)
                                   * *tag* - family_tag object targeting a whole family
                                   * *tag-set* - a set of family-tags targeting the items of multiple families
                                   * *itree_filter* - method (callable) for filtering the children of the object
                                   * *all-children* - if build-in `iter()` or ... (Ellipsis) is given a list of all
                                     children will be given (same result as `list(itree.__iter__())` )


        :type default: object
        :param default: If parameter is set in case of no match the default object will be delivered.
                        If parameter is not set an Exception will be raised

        :rtype: Union[iTree,object]
        :return: found single item or default (in case default is set)
        """
        try:
            if target_path:
                # create locals
                get_child_ren=self._get_child_ren
                cls = self._itree.__class__
                # access first item
                single,item_s = get_child_ren(self._itree,target)
                for t in target_path:
                    # in depth access
                    if single:
                        # if result is a list but we have just one item inside it is also unique
                        # and we reduce to the single item
                        single,item_s = get_child_ren(item_s,t)
                    else:
                        single = False
                        result = []
                        for item in item_s:
                            try:
                                is_single,r = get_child_ren(item,t)
                                result.append(r) if is_single else result.extend(r)
                            except:
                                pass
                        item_s = result
                if item_s.__class__ is cls:
                    return item_s
                elif item_s:
                    item_s=list(item_s)
                    if len(item_s)==1:
                        return item_s[0]
                    else:
                        raise ValueError('No single item found')
                else:
                    raise KeyError('No item found')
            elif target is NoTarget:
                return self._itree
            else:
                is_single,r=self._get_child_ren(self._itree,target)
                if is_single:
                    return r
                else:
                    r=list(r)
                    if len(r)==1:
                        return r[0]
                    else:
                        raise ValueError('No single item found')
        except (ValueError, KeyError, IndexError,AttributeError) as e:
            if target is NoTarget:
                return self
            return _iTreePrivate._raise_exception(e) if (default is Exception) else default

    def iter(self, target, *target_path, default=Exception):
        """
        Method call via **iTree().get.iter()**

        In general the methods does same like the "normal" `get()` but the method delivers an iterator results.
        In case `get()` delivers a single items this method will deliver [item].

        If no match is found  will be delivered the default value (if defined).

        If no target is given `[self]` will be delivered.

        .. warning:: It can be that an empty iterator is delivered and no Exception is raised in this case!

        .. note:: In case the target item should be iterated afterwards this method is recommended because
                  some operations are quicker then the standard `get()`.

        :except: If default parameter is not set an `KeyError` or `IndexError` will be raised. If result is not
                 unique a `ValueError` will be raised.

        :type target: Union[int,tuple,list,slice]
        :param target: level 0 target object targeting a child or multiple children in the ´iTree´.
                       Possible types are:

                           * *index* - absolute target index integer (fastest operation)
                           * *key* - key tuple (family_tag, family_index)
                           * *index-slice* - slice of absolute indexes
                           * *key-index-slice* - tuple of (family_tag, family_index_slice)
                           * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                           * *key-index-list* - tuple of (family_tag, family_index_list)
                           * *tag* - family_tag object targeting a whole family
                           * *tag-set* - a set of family-tags targeting the items of multiple families
                           * *itree_filter* - method (callable) for filtering the children of the object
                           * *all-children* - if build-in `iter()` or ... (Ellipsis) is given a list of all
                             children will be given (same result as `list(itree.__iter__())` )

        :type *target_path: Parameter pointer to iterable
        :param *target_path:  in-depth targets iterable of targets for the different levels 1-n
                              The supported targets in each level are (same like `__getitem__()`:

                                   * *index* - absolute target index integer (fastest operation)
                                   * *key* - key tuple (family_tag, family_index)
                                   * *index-slice* - slice of absolute indexes
                                   * *key-index-slice* - tuple of (family_tag, family_index_slice)
                                   * *target-list* - absolute indexes or keys to be replaced (indexes and keys can be mixed)
                                   * *key-index-list* - tuple of (family_tag, family_index_list)
                                   * *tag* - family_tag object targeting a whole family
                                   * *tag-set* - a set of family-tags targeting the items of multiple families
                                   * *itree_filter* - method (callable) for filtering the children of the object
                                   * *all-children* - if build-in `iter()` or ... (Ellipsis) is given a list of all
                                     children will be given (same result as `list(itree.__iter__())` )


        :type default: object
        :param default: If parameter is set in case of no match the default object will be delivered.
                        If parameter is not set an Exception will be raised

        :rtype: Union[list,blist,Iterator]
        :return: An iterator or a list with a single item will be delivered
        """
        try:
            if target_path:
                # create locals
                get_child_ren=self._get_child_ren
                cls = self._itree.__class__
                # access first item
                single,item_s = get_child_ren(self._itree,target)
                for t in target_path:
                    # in depth access
                    if single:
                        # if result is a list but we have just one item inside it is also unique
                        # and we reduce to the single item
                        single,item_s = get_child_ren(item_s,t)
                    else:
                        single = False
                        result = []
                        for item in item_s:
                            try:
                                is_single,r = get_child_ren(item,t)
                                result.append(r) if is_single else result.extend(r)
                            except:
                                pass
                        item_s = result
                if item_s.__class__ is cls:
                    return [item_s]
                elif item_s:
                    return iter(item_s)
                else:
                    raise KeyError('No item found')
            elif target is NoTarget:
                return [self._itree]
            else:
                is_single,r=self._get_child_ren(self._itree,target)
                if is_single:
                    return [r]
                else:
                    return iter(r)
        except (ValueError, KeyError, IndexError,AttributeError) as e:
            if target is NoTarget:
                return self
            return _iTreePrivate._raise_exception(e) if (default is Exception) else default

    # --- specific access ----------------------------------------------------------------------------------------------

    def by_idx(self, idx, *idx_path, default=Exception):
        """
        Call via **iTree().get.by_idx()**

        Get items by absolute index.

        This is the quickest getter function we have in `iTree` . As parameters the user can give just integers.

        For in-depth operations the user can give an index-path (pointer).

        :type idx: int
        :param idx: first item index

        :type *idx_path: tuple of int
        :param *idx_path: in case we have a in-depth operation we use index path and first given idx
                          will be integrated in the operation (give level 1- n index)

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised

        :rtype: iTree
        :return: target item
        """
        try:
            if idx_path:
                r = self.getitem_by_idx(idx)
                for i in idx_path:
                    r = r.getitem_by_idx(i)
                return r
            else:
                return self.getitem_by_idx(idx)
        except AttributeError:
            return self._raise_exception(IndexError('No child in iTree %s' % (self._itree))) if default is Exception else default
        except Exception as e:
            return self._raise_exception(e) if default is Exception else default

    def by_idx_slice(self, idx_slice, *idx_slice_path, default=Exception):
        """
        Call via **iTree().get.by_idx_slice()**

        Get items by absolute index slice.

        For in-depth operations the user can give multiple parameters (a slices per level). The findings
        are combined to a final flatten list.

        The operation can be mixed with normal indexes.

        .. note:: If the user likes to target all items in a level he can give the slice(None) object which will iterate
                  over all children of the level

                  To target a single item slice(n,n+1) must be given.

        :type idx_slice: slice
        :param idx_slice: absolute index slice for level 0 access (a slice object must be given!)

        :type *idx_slice_path: Parameter pointer
        :param *idx_path: Give multiple parameters  (one slice per level)

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised

        :rtype: list
        :return: list of target iTree-items
        """
        try:
            r = self.getitem_by_idx(idx_slice)
            if idx_slice_path:
                for i_s in idx_slice_path:
                    r2 = []
                    for item in r:
                        r2.extend(item.getitem_by_idx(i_s))
                    if not r2:
                        raise IndexError(' No matching items found in iTree')
                    r = r2
                return r
            else:
                return r if r else self._raise_exception(IndexError(' No matching items found in iTree'))
        except Exception as e:
             return self._raise_exception(e) if default is Exception else default

    def by_idx_list(self, idx_list, *idx_list_path, default=Exception):
        """
        Call via **iTree().get.by_idx_list()**

        Get items via  absolute index lists.

        For in-depth operations the user can multiple parameters (one parameter per level) each parameter must be
        an absolute index list.The findings are combined to a final flatten list.

        .. note:: The user can give ... (Ellipsis) to target all children in a specific level

        :type idx_list: list
        :param idx_list: list of absolute indexes targeting level 0

        :type *idx_list_path: Parameter pointer,
        :param *idx_list_path: Give multiple parameters  (one index list per level)

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised

        :rtype: list
        :return: list of targeted iTree-items
        """
        try:
            itree = self._itree
            if itree:
                getitem_super=self.getitem_by_idx
                if idx_list is ...:
                    r=self.getitem_by_idx(self.NoneSlice)
                else:
                    r = [getitem_super(i) for i in idx_list]
                if idx_list_path:
                    for i_l in idx_list_path:
                        r2 = []
                        if i_l is ...:
                            if BLIST_ACTIVE:
                                [r2.extend(list(item.getitem_by_idx(self.NoneSlice))) for item in r]
                            else:
                                [r2.extend(list(item)) for item in r]
                        else:
                            r2 = [item.getitem_by_idx(i) for item in r for i in i_l if i < len(item)]
                        if not r2:
                            raise KeyError(' No matching items found in iTree')
                        r = r2
                    return r
                else:
                    return r
            else:
                raise IndexError('No child in iTree %s' % (itree))
        except Exception as e:
            return self._raise_exception(e) if default is Exception else default

    def by_tag_idx(self, tag_idx, *tag_idx_path, default=Exception):
        """
        Call via **iTree().get.by_tag_idx()**

        Get items by tag-idx-key (tag,family-index) tuple.

        This is the quickest getter function available for tag-idx access (comparable to keys in dicts)
        we have in iTree. The parameters must be (tag, family-idx) tuples.

        For in-depth operations the user can give a tag_idx_path. In this case the methods dives into the tree and
        extracts the matching items in the different levels

        :type tag_idx: tuple
        :param tag_idx: level one tag-idx-key

        :type *idx_path: Parameter pointer
        :param *idx_path: In-depth parameters each additional parameter must be a tag-idx-key target the item in the
                          specific level

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised

        :rtype: iTree
        :return: targeted item
        """
        try:
            tag, fam_idx = tag_idx
            if tag_idx_path:
                r = self._getitem_fam(tag)[fam_idx]
                for t, i in tag_idx_path:
                    r = r._getitem_fam(t)[i]
                return r
            else:
                return self._getitem_fam(tag)[fam_idx]
        except AttributeError:
            if default is Exception:
                raise KeyError('No child in iTree %s' % (self._itree))
            else:
                return default
        except Exception as e:
            return self._raise_exception(e) if default is Exception else default

    def by_tag_idx_slice(self, tag_idx_slice, *tag_idx_slice_path, default=Exception):
        """
        Call via **iTree().get.by_tag_idx_slice()**

        Get items via tag_idx_key containing a slice in the family index tuple(tag,family-index-slice).
        The user must give here a slice object.

        For in-depth operation additional tag_idx_keys containing slices can be added. To target a whole family the
        user may give the slice(None). The results in the different levels are merged to a flatten list containing
        all matches in the highest targeted level.

        :type tag_idx_slice: tuple
        :param tag_idx_slice: tuple of tag and family-index-slice

        :type *tag_idx_slice_path: Parameter pointer
        :param *tag_idx_path: Give additional tag-idx-slices per target level in-depth of the iTree

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised

        :rtype: list
        :return: list of targeted iTree-items
        """
        try:
            tag, fam_idx_slice = tag_idx_slice
            r = self._getitem_fam(tag)[fam_idx_slice]
            if tag_idx_slice_path:
                for t, s in tag_idx_slice_path:
                    r2 = []
                    for item in r:
                        if item._contains_fam(t):
                            family = self._getitem_fam(t)
                            if len(family) > s:
                                result = family[s]
                                if hasattr(result, '_itree_prt_idx'):
                                    result = [result]
                                r2.extend(result)
                    if not r2:
                        raise KeyError(' No matching items found in iTree')
                    r = r2
                return r
            else:
                return r if r else self._raise_exception(KeyError(' No matching items found in iTree'))
        except Exception as e:
            return self._raise_exception(e) if default is Exception else default

    def by_tag_idx_list(self, tag_idx_list, *tag_idx_list_path, default=Exception):
        """
        Call via **iTree().get.by_tag_idx_list()**

        Get items by giving a tag-family-index-list tuple.

        For in-depth operation the user can add more tag-family-index-list tuples as additional parameters targeting
        the in-depth levels of the iTree object.

        To target all family items of a specific level the `,,,`-object`(Ellipsis) can be placed as parameter.

        :type tag_idx_list: tuple
        :param tag_idx_list: tuple of tag and a list of family-indexes (e.g. ('mytag',[1,2,3]))

        :type *tag_idx_list_path: Parameter pointer
        :param *tag_idx_list_path: Additional parameters each containing a tuple with tag and a list of indexes
                                   for each in-depth level of the iTree

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised

        :rtype: list
        :return: list of targeted iTree-items
        """
        try:
            tag, fam_idx_list = tag_idx_list
            family = self._getitem_fam(tag)
            if fam_idx_list is ...:
                r = family[:]
            else:
                r = [family[i] for i in fam_idx_list]
            if tag_idx_list_path:
                for t, il in tag_idx_list_path:
                    r2 = []
                    for item in r:
                        if item._contains_fam(t):
                            family = self._getitem_fam(t)
                            if il is ...:
                                r2.extend(family)
                            else:
                                if len(family) > il:
                                    r2.append(family[il])
                    if not r2:
                        raise KeyError(' No matching items found in iTree')
                    r = r2
                return r
            else:
                return r
        except Exception as e:
            return self._raise_exception(e) if default is Exception else default

    def by_tag(self, tag, *tag_path, default=Exception):
        """
        Call via **iTree().get.by_tag()**

        Get family items by given tag.

        This is the quickest getter function for families.

        For in-depth operation the user can give as additional parameters more tags (one tag per level). The findings
        are cumulated and delivered as a flattened item list.

        :type tag: hashable
        :param tag: Family tag targeting all items inside the family

        :type tag_path: Parameter pointer
        :param *tag_path: hashable tags targeting the deeper levels of iTree

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised

        :rtype: list
        :return: list of targeted iTree-items
        """
        try:
            if tag_path:
                r = self._getitem_fam(tag)
                r2 = []
                for t in tag_path:
                    for item in r:
                        if item._contains_fam(t):
                            r2.extend(item._getitem_fam(t))
                if not r2:
                    raise KeyError('Given tag_path %s has no match in iTree' % repr([tag] + tag_path))
                return r2
            else:
                return self._getitem_fam(tag)[:]
        except AttributeError:
            if default is Exception:
                raise KeyError('No child in targeted iTree?')
            else:
                return default
        except Exception as e:
            return self._raise_exception(e) if default is Exception else default

    def by_tags(self, tags, *tags_path, default=Exception):
        """
        Call via **iTree().get.by_tags()**

        Here the user gives an iterable of tags for the to be targeted families (multiple families). The targeted
        items are combined in one list.

        For in-depth operation the user can give additional parameters containing tag-iterables per target levels.
        The result is cumulated and delivers all found items in the deepest targeted level.

        The user might give also single tags (but it's recommended to put them in a list -> see the warning).

        .. warning:: Tuples are interpreted as iterables in this case! If the user likes to target a single tag which is
                     a tuple-object he must give an additional iteration level
                     (e.g. tag=(1,2) tags([(1,2)] must be given to target the tag-family (1,2)).

        :type tags: Iterable
        :param tags: Iterable of family tags

        :type *tags_path: Parameter pointer
        :param *tags_path: Additional family-tag iterables for deeper levels of teh iTree

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised

        :rtype: list
        :return: list of target items
        """
        try:
            itree = self._itree
            if itree:
                try:
                    iterator = iter(tags)
                except TypeError:
                    iterator = [tags]
                r = []
                for t in iterator:
                    r.extend(self._getitem_fam(t))
                if tags_path:
                    r2 = []
                    for tag in tags_path:
                        try:
                            iterator = iter(tag)
                        except TypeError:
                            iterator = [tag]
                        for t in iterator:
                            for item in r:
                                if item._contains_fam(t):
                                    r2.extend(item._getitem_fam(t))
                    if not r2:
                        raise KeyError('Given tag_path *%s has no match in iTree' % repr((tags,) + tuple(tags_path)))
                    return r2
                else:
                    return r
            else:
                raise KeyError('No child in iTree %s' % (itree))
        except Exception as e:
            return self._raise_exception(e) if default is Exception else default

    def by_level_filter(self, filter_method, *filter_method_path, default=Exception):
        """
        Call via **iTree().get.by_level_filters()**

        Get items by level-filters.

        For in-depth operation additional parameters can be given each is a level-filter for the next level.

        In case the build-in `iter`-method is given (without parameters) all items in the level
        will be considered (no filtering). The level filtering is always a hierarchical filtering.

        :type filter_method: Method
        :param filter_method: filter_method analysis the itree-items and delivers `True` for a match and
                              `False` for no match (filtered out)

        :type *filter_method_path: Parameter pointer
        :param *filter_method_path: Additional parameters for filter_methods for the deeper levels of the iTree.

        :type default: object
        :param default: This is a named parameter only!
                        If default is given the default objet will be returned in case of internal exceptions.
                        If default is Exception an exception is raised


        :rtype: list
        :return: list of filtered iTree-items found in the deepest targeted level
        """
        try:
            itree = self._itree
            if itree:
                r = filter(filter_method,itree)
                if filter_method_path:
                    r2 = []
                    for f in filter_method_path:
                        for item in r:
                            r2.extend(filter(f,item))
                    if not r2:
                        raise KeyError('Given filter_method_path has no match in iTree')
                    return r2
                else:
                    return list(r)
            else:
                raise KeyError('No child in iTree %s' % (itree))
        except Exception as e:
            return self._raise_exception(e) if default is Exception else default

    def _raise_exception(self,exception):
        raise exception
