import sys
from collections import deque
from ..itree_helpers import ITER
from .itree_indepth_siblings import _iTreeIndepthSiblings

DOWN = ITER.DOWN
UP = ITER.UP
REVERSE = ITER.REVERSE
SELF = ITER.SELF
FILTER_ANY = ITER.FILTER_ANY
MULTIPLE=ITER.MULTIPLE

iter_list = list if sys.version_info >= (3, 8) else deque  # from Python 3.8 on lists are quicker then deque

class _iTreeIndepthIter(_iTreeIndepthSiblings):

    _SIBLINGS_PLUS_HELPERS = {
        0: _iTreeIndepthSiblings._siblings_plus,
        MULTIPLE: _iTreeIndepthSiblings._siblings_plus,
        REVERSE: _iTreeIndepthSiblings._siblings_plus_reverse,
        MULTIPLE | REVERSE: _iTreeIndepthSiblings._siblings_plus_reverse,
    }

    _SIBLINGS_MINUS_HELPERS = {
        0: _iTreeIndepthSiblings._siblings_minus,
        MULTIPLE: _iTreeIndepthSiblings._siblings_minus_multi,
        REVERSE: _iTreeIndepthSiblings._siblings_minus_reverse,
        MULTIPLE | REVERSE: _iTreeIndepthSiblings._siblings_minus_multi_reverse,
    }

    @staticmethod
    def _iter_normal(self, filter_method, options=0):
        """
        helper iteration generator

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        if filter_method:
            if options & SELF:
                if filter_method(itree):
                    yield itree
                else:
                    return
            if itree:
                iterators = iter_list((filter(filter_method, itree.__iter__()),))
                while iterators:
                    for item in iterators[-1]:
                        yield item
                        if item:
                            iterators.append(filter(filter_method, item.__iter__()))
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
        else:
            if options & SELF:
                yield itree
            # from here on same as __iter__()
            if itree:
                iterators = iter_list((itree.__iter__(),))
                while iterators:
                    for item in iterators[-1]:
                        yield item
                        if item:
                            iterators.append(item.__iter__())
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]

    @staticmethod
    def _iter_normal_idxpath(self, filter_method, options=0):
        """
        helper iteration generator yields (idx_path,item) tuples

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        idx_path=itree.idx_path
        if filter_method:
            if options & SELF:
                if filter_method(itree):
                    yield idx_path,itree
                else:
                    return
            if itree:
                iterators = iter_list((itree.__iter__(),))
                indexes = [-1]
                while iterators:
                    for item in iterators[-1]:
                        item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                        if filter_method(item):
                            yield idx_path+tuple(indexes),item
                            if item:
                                iterators.append(item.__iter__())
                                indexes.append(-1)
                                break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
                        del indexes[-1]
        else:
            if options & SELF:
                yield idx_path,itree
            # from here on same as __iter__()
            if itree:
                iterators = iter_list((itree.__iter__(),))
                indexes = [-1]
                while iterators:
                    for item in iterators[-1]:
                        item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                        yield idx_path+tuple(indexes),item
                        if item:
                            iterators.append(item.__iter__())
                            indexes.append(-1)
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
                        del indexes[-1]

    @staticmethod
    def _iter_normal_tagidxpath(self, filter_method, options=0):
        """
        helper iteration generator yields (tag_idx_path,item) tuples

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        tag_idx_path=itree.tag_idx_path
        if filter_method:
            if options & SELF:
                if filter_method(itree):
                    yield tag_idx_path,itree
                else:
                    return
            # from here on same as __iter__()
            if itree:
                iterators = iter_list((itree.__iter__(),))
                tag_idx_dicts = [dict.fromkeys(itree._families.keys(), -1)]
                tag_idxs=[None]
                while iterators:
                    for item in iterators[-1]:
                        tag=item.tag
                        tag_dict=tag_idx_dicts[-1]
                        item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                        tag_idxs[-1]=(tag,idx)
                        if filter_method(item):
                            yield tag_idx_path+tuple(tag_idxs),item
                        if item and filter_method(item):
                            iterators.append(item.__iter__())
                            tag_idx_dicts.append(dict.fromkeys(item._families.keys(), -1))
                            tag_idxs.append(None)
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
                        del tag_idx_dicts[-1]
                        del tag_idxs[-1]
            if options & SELF:
                if filter_method(itree):
                    yield tag_idx_path,itree
                else:
                    return
        else:
            if options & SELF:
                yield tag_idx_path,itree
            # from here on same as __iter__()
            if itree:
                iterators = iter_list((itree.__iter__(),))
                tag_idx_dicts = [dict.fromkeys(itree._families.keys(), -1)]
                tag_idxs=[None]
                while iterators:
                    for item in iterators[-1]:
                        tag=item.tag
                        tag_dict=tag_idx_dicts[-1]
                        item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                        tag_idxs[-1]=(tag,idx)
                        yield tag_idx_path+tuple(tag_idxs),item
                        if item:
                            iterators.append(item.__iter__())
                            tag_idx_dicts.append(dict.fromkeys(item._families.keys(), -1))
                            tag_idxs.append(None)
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
                        del tag_idx_dicts[-1]
                        del tag_idxs[-1]

    @staticmethod
    def _iter_reverse(self, filter_method=None, options=0):
        """
        helper iteration generator

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((filter(filter_method, reversed(itree)),))
                while iterators:
                    for item in iterators[-1]:
                        yield item
                        if item:
                            iterators.append(filter(filter_method, reversed(item)))
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield itree
        else:
            if itree:
                iterators = iter_list((iter(reversed(itree)),))
                while iterators:
                    for item in iterators[-1]:
                        yield item
                        if item:
                            iterators.append(iter(reversed(item)))
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield itree

    @staticmethod
    def _iter_reverse_idxpath(self, filter_method=None, options=0):
        """
        helper iteration generator yields (idx_path,item) tuples

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        idx_path=itree.idx_path
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((iter(reversed(itree)),))
                indexes = [len(itree)]
                while iterators:
                    for item in iterators[-1]:
                        item._itree_prt_idx[1] =indexes[-1] = indexes[-1] - 1
                        if filter_method(item):
                            yield idx_path+tuple(indexes),item
                            if item:
                                iterators.append(iter(reversed(item)))
                                indexes.append(len(item))
                                break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
                        del indexes[-1]
            if options & SELF and filter_method(itree):
                yield idx_path,itree
        else:
            if itree:
                iterators = iter_list((iter(reversed(itree)),))
                indexes = [len(itree)]
                while iterators:
                    for item in iterators[-1]:
                        item._itree_prt_idx[1] =indexes[-1] = indexes[-1] - 1
                        yield idx_path + tuple(indexes), item
                        if item:
                            iterators.append(iter(reversed(item)))
                            indexes.append(len(item))
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
                        del indexes[-1]
            if options & SELF:
                yield idx_path,itree


    @staticmethod
    def _iter_reverse_tagidxpath(self, filter_method=None, options=0):
        """
        helper iteration generator yields (tag_idx_path,item) tuples

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        tag_idx_path=itree.tag_idx_path
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((iter(reversed(itree)),))
                tag_idx_dicts = [{key:len(itree._families[key]) for key in itree._families.keys()}]
                tag_idxs=[None]
                while iterators:
                    for item in iterators[-1]:
                        tag=item.tag
                        tag_dict=tag_idx_dicts[-1]
                        item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] - 1
                        tag_idxs[-1]=(tag,idx)
                        if filter_method(item):
                            yield tag_idx_path + tuple(tag_idxs), item
                            if item:
                                iterators.append(iter(reversed(item)))
                                tag_idx_dicts.append({key:len(item._families[key]) for key in item._families.keys()})
                                tag_idxs.append(None)
                                break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
                        del tag_idx_dicts[-1]
                        del tag_idxs[-1]
            if options & SELF:
                yield tag_idx_path,itree
        else:
            if itree:
                iterators = iter_list((iter(reversed(itree)),))
                tag_idx_dicts = [{key:len(itree._families[key]) for key in itree._families.keys()}]
                tag_idxs=[None]
                while iterators:
                    for item in iterators[-1]:
                        tag=item.tag
                        tag_dict=tag_idx_dicts[-1]
                        item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] - 1
                        tag_idxs[-1]=(tag,idx)
                        yield tag_idx_path + tuple(tag_idxs), item
                        if item:
                            iterators.append(iter(reversed(item)))
                            tag_idx_dicts.append({key:len(item._families[key]) for key in item._families.keys()})
                            tag_idxs.append(None)
                            break
                    else:  # for loop is finished and not broken
                        del iterators[-1]
                        del tag_idx_dicts[-1]
                        del tag_idxs[-1]
            if options & SELF:
                yield tag_idx_path,itree



    @staticmethod
    def _iter_up(self, filter_method=None, options=0):
        """
        helper iteration generator bottom -> up direction

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((filter(filter_method, itree.__iter__()),))
                while iterators:
                    for item in iterators[-1]:
                        if item:
                            iterators.extend(((None, item), filter(filter_method, item.__iter__())))
                            break
                        elif item is None:
                            yield iterators.pop()[-1]
                            break
                        else:
                            yield item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF and filter_method(itree):
                yield itree
        else:
            if itree:
                iterators = iter_list((itree.__iter__(),))
                while iterators:
                    for item in iterators[-1]:
                        if item:
                            iterators.extend(((None, item), item.__iter__()))
                            break
                        elif item is None:
                            yield iterators.pop()[-1]
                            break
                        else:
                            yield item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield itree

    @staticmethod
    def _iter_up_idxpath(self, filter_method=None, options=0):
        """
        helper iteration generator bottom->up direction, yields (idx_path,item) tuples

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        idx_path=itree.idx_path
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((itree.__iter__(),))
                indexes=[-1]
                while iterators:
                    for item in iterators[-1]:
                        if item and filter_method(item):
                            item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                            iterators.extend(((None, item), item.__iter__()))
                            indexes.append(-1)
                            break
                        elif item is None:
                            item=iterators.pop()[-1]
                            indexes.pop()
                            if filter_method(item):
                                yield idx_path+tuple(indexes),item
                            break
                        else:
                            item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                            if filter_method(item):
                                yield idx_path+tuple(indexes),item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield idx_path,itree
        else:
            if itree:
                iterators = iter_list((itree.__iter__(),))
                indexes=[-1]
                while iterators:
                    for item in iterators[-1]:
                        if item:
                            item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                            iterators.extend(((None, item), item.__iter__()))
                            indexes.append(-1)
                            break
                        elif item is None:
                            item=iterators.pop()[-1]
                            del indexes[-1]
                            yield idx_path+tuple(indexes),item
                            break
                        else:
                            item._itree_prt_idx[1] = indexes[-1] = indexes[-1] + 1
                            yield idx_path+tuple(indexes), item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield idx_path, itree

    @staticmethod
    def _iter_up_tagidxpath(self, filter_method=None, options=0):
        """
        helper iteration generator bottom-> up direction, yields (tag_idx_path,item) tuples

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        tag_idx_path=itree.tag_idx_path
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((itree.__iter__(),))
                tag_idx_dicts = [dict.fromkeys(itree._families.keys(), -1)]
                tag_idxs=[None]
                while iterators:
                    for item in iterators[-1]:
                        if item and filter_method(item):
                            tag = item.tag
                            tag_dict = tag_idx_dicts[-1]
                            item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                            tag_idxs[-1]=(tag,idx)
                            iterators.extend(((None,item),item.__iter__()))
                            tag_idx_dicts.append(dict.fromkeys(item._families.keys(), -1))
                            tag_idxs.append(None)
                            break
                        elif item is None:
                            item=iterators.pop()[-1]
                            del tag_idx_dicts[-1]
                            del tag_idxs[-1]
                            yield tag_idx_path+tuple(tag_idxs),item
                            break
                        else:
                            tag = item.tag
                            tag_dict = tag_idx_dicts[-1]
                            item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                            tag_idxs[-1]=(tag,idx)
                            if filter_method(item):
                                yield tag_idx_path+tuple(tag_idxs),item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield tag_idx_path,itree
        else:
            if itree:
                iterators = iter_list((itree.__iter__(),))
                tag_idx_dicts = [dict.fromkeys(itree._families.keys(), -1)]
                tag_idxs=[None]
                while iterators:
                    for item in iterators[-1]:
                        if item:
                            tag = item.tag
                            tag_dict = tag_idx_dicts[-1]
                            item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                            tag_idxs[-1]=(tag,idx)
                            iterators.extend(((None,item),item.__iter__()))
                            tag_idx_dicts.append(dict.fromkeys(item._families.keys(), -1))
                            tag_idxs.append(None)
                            break
                        elif item is None:
                            item=iterators.pop()[-1]
                            del tag_idx_dicts[-1]
                            del tag_idxs[-1]
                            yield tag_idx_path+tuple(tag_idxs),item
                            break
                        else:
                            tag = item.tag
                            tag_dict = tag_idx_dicts[-1]
                            item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] + 1
                            tag_idxs[-1]=(tag,idx)
                            yield tag_idx_path+tuple(tag_idxs),item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield tag_idx_path,itree

    @staticmethod
    def _iter_up_reverse(self, filter_method=None, options=0):
        """
        helper iteration generator bottom->up directions and reversed item order

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((filter(filter_method, reversed(itree)),))
                while iterators:
                    for item in iterators[-1]:
                        if item:
                            iterators.extend(((None, item), filter(filter_method, reversed(item))))
                            break
                        elif item is None:
                            yield iterators.pop()[-1]
                            break
                        else:
                            yield item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield itree
        else:
            if itree:
                iterators = iter_list((reversed(itree),))
                while iterators:
                    for item in iterators[-1]:
                        if item:
                            iterators.extend(((None, item), reversed(item)))
                            break
                        elif item is None:
                            yield iterators.pop()[-1]
                            break
                        else:
                            yield item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield itree


    @staticmethod
    def _iter_up_reverse_idxpath(self, filter_method=None, options=0):
        """
        helper iteration generator bottom->up directions and reversed item order, yields (idx_path,item) tuples

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        idx_path=itree.idx_path
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((reversed(itree),))
                indexes=[len(itree)]
                while iterators:
                    for item in iterators[-1]:
                        if item and filter_method(item):
                            item._itree_prt_idx[1] = indexes[-1] = indexes[-1] - 1
                            iterators.extend(((None, item), reversed(item)))
                            indexes.append(len(item))
                            break
                        elif item is None:
                            item=iterators.pop()[-1]
                            indexes.pop()
                            if filter_method(item):
                                yield idx_path+tuple(indexes),item
                            break
                        else:
                            item._itree_prt_idx[1] = indexes[-1] = indexes[-1] - 1
                            if filter_method(item):
                                yield idx_path+tuple(indexes),item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield idx_path,itree
        else:
            if itree:
                iterators = iter_list((reversed(itree),))
                indexes=[len(itree)]
                while iterators:
                    for item in iterators[-1]:
                        if item:
                            item._itree_prt_idx[1] = indexes[-1] = indexes[-1] - 1
                            iterators.extend(((None, item), reversed(item)))
                            indexes.append(len(item))
                            break
                        elif item is None:
                            item=iterators.pop()[-1]
                            indexes.pop()
                            yield idx_path+tuple(indexes),item
                            break
                        else:
                            item._itree_prt_idx[1] = indexes[-1] = indexes[-1] - 1
                            yield idx_path+tuple(indexes), item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield idx_path, itree

    @staticmethod
    def _iter_up_reverse_tagidxpath(self, filter_method=None, options=0):
        """
        helper iteration generator bottom->up directions and reversed item order, yields (tag_idx_path,item) tuples

        :param filter_method: filter_method parameter from parent method
        :param options: only SELF is considered here
        """
        itree = self._itree
        tag_idx_path=itree.tag_idx_path
        if filter_method:
            if options & SELF:
                if not filter_method(itree):
                    return
            if itree:
                iterators = iter_list((reversed(itree),))
                tag_idx_dicts = [{key:len(itree._families[key]) for key in itree._families.keys()}]
                tag_idxs=[None]
                while iterators:
                    for item in iterators[-1]:
                        if item and filter_method(item):
                            tag = item.tag
                            tag_dict = tag_idx_dicts[-1]
                            item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] - 1
                            tag_idxs[-1] = (tag, idx)
                            tag_idx_dicts.append({key:len(item._families[key]) for key in item._families.keys()})
                            tag_idxs.append(None)
                            iterators.extend(((None, item), reversed(item)))
                            break
                        elif item is None:
                            item=iterators.pop()[-1]
                            del tag_idx_dicts[-1]
                            del tag_idxs[-1]
                            if filter_method(item):
                                yield tag_idx_path+tuple(tag_idxs),item
                            break
                        else:
                            tag = item.tag
                            tag_dict = tag_idx_dicts[-1]
                            item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] - 1
                            tag_idxs[-1] = (tag, idx)
                            if filter_method(item):
                                yield tag_idx_path + tuple(tag_idxs), item
                    else:  # for loop is finished and not broken
                        del iterators[-1]

            if options & SELF:
                yield tag_idx_path,itree
        else:
            if itree:
                iterators = iter_list((reversed(itree),))
                tag_idx_dicts = [{key:len(itree._families[key]) for key in itree._families.keys()}]
                tag_idxs=[None]
                while iterators:
                    for item in iterators[-1]:
                        if item:
                            tag = item.tag
                            tag_dict = tag_idx_dicts[-1]
                            item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] - 1
                            tag_idxs[-1] = (tag, idx)
                            tag_idx_dicts.append({key:len(item._families[key]) for key in item._families.keys()})
                            tag_idxs.append(None)
                            iterators.extend(((None, item), reversed(item)))
                            break
                        elif item is None:
                            item=iterators.pop()[-1]
                            del tag_idx_dicts[-1]
                            del tag_idxs[-1]
                            yield tag_idx_path+tuple(tag_idxs),item
                            break
                        else:
                            tag = item.tag
                            tag_dict = tag_idx_dicts[-1]
                            item._itree_prt_idx[2] = tag_dict[tag] = idx = tag_dict[tag] - 1
                            tag_idxs[-1] = (tag, idx)
                            yield tag_idx_path + tuple(tag_idxs), item
                    else:  # for loop is finished and not broken
                        del iterators[-1]
            if options & SELF:
                yield tag_idx_path,itree
