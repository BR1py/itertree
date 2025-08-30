# -*- coding: utf-8 -*-
"""
This code is taken from the itertree package:

  ___ _____ _____ ____ _____ ____  _____ _____
 |_ _|_   _| ____|  _ \_   _|  _ \| ____| ____|
  | |  | | |  _| | |_) || | | |_) |  _| |  _|
  | |  | | | |___|  _ < | | |  _ <| |___| |___
 |___| |_| |_____|_| \_\|_| |_| \_\_____|_____|


https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license
For more information see: https://en.wikipedia.org/wiki/MIT_License

CONTENT DESCRIPTION:

This part of code contains
THe test of the functions in itree_helpers.py
"""
import timeit
import os

from itertree import *
from itertree.itree_helpers import itree_list, BLIST_ACTIVE

if BLIST_ACTIVE:
    from blist import blist

root_path = os.path.dirname(__file__)
print('ROOT_PATH', root_path)


print('Test start: itertree  helpers test')
if BLIST_ACTIVE: print('blist module imported for the test')

def get_relpath_to_root(item_path):
    new_path = item_path.replace(root_path, '')
    if new_path.startswith('\\'):
        new_path = new_path[1:]
    if new_path.startswith('/'):
        new_path = new_path[1:]
    return root_path + '/' + new_path


def calc_timeit(check_method, number):
    min_time = float('inf')
    for i in range(number):
        t = timeit.timeit(check_method, number=1)
        if t < min_time:
            min_time = t
    return min_time


class Test1_Helpers:


    def test1_ITER_options(self):
        ''''
        we build a tree with some entries and then we try to access the items
        '''
        print('\nOUTPUT HELPERS-TEST: ITER_options')
        option=ITER.UP
        assert ITER.get_option_str(option)=='UP', 'Value was %s'%bin(option)
        option = ITER.REVERSE
        assert ITER.get_option_str(option) == 'REVERSE', 'Value was %s'%bin(option)
        option = ITER.SELF
        assert ITER.get_option_str(option) == 'SELF', 'Value was %s'%bin(option)
        option=ITER.UP|ITER.REVERSE
        assert ITER.get_option_str(option) == 'UP | REVERSE', 'Value was %s'%bin(option)
        option = ITER.UP | ITER.SELF
        assert ITER.get_option_str(option) == 'UP | SELF', 'Value was %s'%bin(option)
        option = ITER.REVERSE | ITER.SELF
        assert ITER.get_option_str(option) == 'REVERSE | SELF', 'Value was %s'%bin(option)
        option = ITER.UP | ITER.SELF |ITER.REVERSE
        assert ITER.get_option_str(option) == 'UP | REVERSE | SELF', 'Value was %s'%bin(option)
        option = ITER.UP | ITER.SELF |ITER.REVERSE|ITER.MULTIPLE
        assert ITER.get_option_str(option) == 'UP | REVERSE | SELF | MULTIPLE', 'Value was %s'%bin(option)
        option=ITER.FILTER_ANY
        assert ITER.get_option_str(option) == 'FILTER_ANY', 'Value was %s' % bin(option)
        option = ITER.FILTER_ANY | ITER.UP | ITER.SELF |ITER.REVERSE
        assert ITER.get_option_str(option) == 'UP | REVERSE | SELF | FILTER_ANY', 'Value was %s'%bin(option)
        invalid_option = 0b1100000|ITER.FILTER_ANY | ITER.UP | ITER.SELF |ITER.REVERSE # unknown option
        assert ITER.get_option_str(invalid_option) == 'UP | REVERSE | SELF | FILTER_ANY | MULTIPLE | %s'%bin(0b1000000), 'Value was %s'%bin(option)
        assert ITER.valid_option(option) is None
        assert bin(0b1000000) in ITER.valid_option(invalid_option)



