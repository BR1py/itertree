"""# -*- coding: utf-8 -*-#"""
from __future__ import absolute_import

"""
This file contains some examples for the usage of itertree module

"""

import os
import sys
import time
from itertree import *


class FilesystemToItertree:
    """
    In this example for huge deep tree of items we read in the filesystem into an itertree and
    put some file attributes in the data
    """

    def __init__(self):
        self.tree = iTree('root')

    def load_from_path(self, source_folder):
        self.tree = iTree('root')
        self.get_items(source_folder, self.tree)

    def get_items(self, source_dir, root_item):
        try:
            for fd in os.listdir(source_dir):
                try:
                    fd_path = os.path.join(source_dir, fd)
                    if os.path.isfile(fd_path):
                        data = {'SIZE': os.path.getsize(fd_path),
                                'ATIME': os.path.getatime(fd_path),
                                'CTIME': os.path.getctime(fd_path),
                                'MTIME': os.path.getmtime(fd_path),
                                'EXT': os.path.splitext(fd_path)[-1].replace('.', ''),
                                'FULL_PATH': fd_path,
                                'TYPE': 'FILE',
                                'ACCESS': True
                                }
                        root_item.append(iTree(fd, data))
                    elif os.path.isdir(fd_path):
                        dir_etree = iTree(fd, data={'TYPE': 'DIR', 'ACCESS': True})
                        root_item.append(dir_etree)
                        self.get_items(fd_path, dir_etree)
                    else:
                        root_item.append(iTree(fd, data={'TYPE', 'UNKNOWN'}))
                except:
                    pass
        except PermissionError:
            root_item.d_set('ACCESS', False)

    def get_item_tree(self):
        return self.tree


if __name__ == '__main__':
    """
    We run all the example (this will take a while and generate a huge print output!
    """
    # first we build a very simple tree:
    root = iTree('root')
    root.append(iTree('Africa', data={'surface': 30200000, 'inhabitants': 1257000000}))
    root.append(iTree('Asia', data={'surface': 44600000, 'inhabitants': 4000000000}))
    root.append(iTree('America', data={'surface': 42549000, 'inhabitants': 1009000000}))
    root.append(iTree('Australia&Oceania', data={'surface': 8600000, 'inhabitants': 36000000}))
    # you might add items also via __iadd__() (+=) operator
    root += iTree('Europe', data={'surface': 10523000, 'inhabitants': 746000000})
    root += iTree('Antarctica', data={'surface': 14000000, 'inhabitants': 1100})

    # for building next level here we select per index:
    root[0] += iTree('Ghana', data={'surface': 238537, 'inhabitants': 30950000})
    root[0] += iTree('Nigeria', data={'surface': 1267000, 'inhabitants': 23300000})
    root[1].append(iTree('China', data={'surface': 9596961, 'inhabitants': 1411780000}))
    root[1].append(iTree('India', data={'surface': 3287263, 'inhabitants': 1380004000}))
    root[2].append(iTree('Canada', data={'surface': 9984670, 'inhabitants': 38008005}))
    # here we select per TagIdx - remember in itertree you might put items with same tag multiple times:
    root[TagIdx('America', 0)].append(iTree('Mexico', data={'surface': 1972550, 'inhabitants': 127600000}))
    # add multiple items via extend:
    root[3].extend([iTree('Australia', data={'surface': 7688287, 'inhabitants': 25700000}),
                    iTree('New Zealand', data={'surface': 269652, 'inhabitants': 4900000})])
    root[4].append(iTree('France', data={'surface': 632733, 'inhabitants': 67400000}))
    # use TagIdx for item selection
    # remember itertree can have multiple items with same tag, we need here TagIdx object!
    root[TagIdx('Europe', 0)].append(iTree('Finland', data={'surface': 338465, 'inhabitants': 5536146}))

    root.render()

    # we might filter for data content:
    inhabitants_interval = iTInterval(0, 20000000)
    item_filter = Filter.iTFilterData(data_key='inhabitants', data_value=inhabitants_interval)
    iterator = root.iter_all(item_filter=item_filter)

    print('Filtered items; inhabitants in range: %s' % inhabitants_interval.math_repr())
    for i in iterator:
        print(i)

    # we do a mixed filtering:
    inhabitants_interval = iTInterval(0, 20000000)
    item_filter1 = Filter.iTFilterData(data_key='inhabitants', data_value=inhabitants_interval)
    surface_interval = iTInterval(0, 1000000)
    item_filter2 = Filter.iTFilterData(data_key='surface', data_value=surface_interval, pre_item_filter=item_filter1,
                                       use_and=True)
    iterator = root.iter_all(item_filter=item_filter2)

    print('Filter2 items (we expect Antarctica does not match anymore!):')
    for i in iterator:
        print(i)

    print('\nIt follows another example of a bigger tree:')

    if sys.platform == 'linux':
        root_dir = '/usr/lib'
    else:
        # Windows
        root_dir = "c:/ProgramData"
    print('We read a part of the filesystem (%s) into an itertree' % repr(root_dir))
    file_2_itree = FilesystemToItertree()
    file_2_itree.load_from_path(root_dir)
    filetree = file_2_itree.get_item_tree()
    # User might store the rendering into a file:
    # with open('d:/tmp/out.txt','wb') as fh:
    #    fh.write(filetree.renders().encode('utf8',errors='backslashreplace'))
    print('Number of items read in %i' % len(list(filetree.iter_all())))
    print('The load in tree has a depth of %i' % filetree.max_depth_down)
    print('How many files are bigger then 1000000 Bytes?')
    item_filter = Filter.iTFilterData(data_key='SIZE', data_value=iTInterval(1000000, 'inf'))
    print('Number of Matches: %i' % len(list(filetree.iter_all(item_filter))))
    print('How many files are in size 9000 ~ 10000 Bytes?')
    item_filter = Filter.iTFilterData(data_key='SIZE', data_value=iTInterval(9000, 10000))
    print('Number of Matches: %i' % len(list(filetree.iter_all(item_filter))))
    print('How many files are touched (modified) during the last day?')
    t = time.time()
    item_filter = Filter.iTFilterData(data_key='MTIME', data_value=iTInterval(t - (60 * 60 * 24), t))
    print('Number of Matches: %i' % len(list(filetree.iter_all(item_filter))))
    print('How many files are touched (modified) during the last minute?')
    t = time.time()
    item_filter = Filter.iTFilterData(data_key='MTIME', data_value=iTInterval(t - 60, t))
    print('Number of Matches: %i' % len(list(filetree.iter_all(item_filter))))
    # we render here the output (We do not expect to many matches)
    filetree.render(item_filter)
