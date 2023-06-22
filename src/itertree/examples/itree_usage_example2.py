"""# -*- coding: utf-8 -*-#"""
from __future__ import absolute_import
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



This part of code contains the profiling of nested iTree structures
"""

import os
import sys
import time
from itertree import *
mSetInterval=Filters.mSetInterval

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
                        dir_etree = iTree(fd, value={'TYPE': 'DIR', 'ACCESS': True})
                        root_item.append(dir_etree)
                        self.get_items(fd_path, dir_etree)
                    else:
                        root_item.append(iTree(fd, value={'TYPE', 'UNKNOWN'}))
                except:
                    pass
        except PermissionError:
            root_item.d_set('ACCESS', False)

    def get_item_tree(self):
        return self.tree


if __name__ == '__main__':

    root_dir=os.path.dirname(sys.executable)

    print('We read a part of the filesystem (%s) into an itertree' % repr(root_dir))
    file_2_itree = FilesystemToItertree()
    file_2_itree.load_from_path(root_dir)
    filetree = file_2_itree.get_item_tree()
    # User might store the rendering into a file:
    # with open('d:/tmp/out.txt','wb') as fh:
    #    fh.write(filetree.renders().encode('utf8',errors='backslashreplace'))
    print('Number of items read in %i' % len(filetree.deep))
    print('The load in tree has a depth of %i' % filetree.max_depth)
    print('How many files are bigger then 1000000 Bytes?')
    interval=mSetInterval(1000000, 'inf')
    filter_method = lambda i: i.value.get('SIZE', 0) in interval if i.value != NoValue else False
    print('Number of Matches: %i' % filetree.deep.filtered_len(filter_method, True))
    print('How many files are in size 9000 ~ 10000 Bytes?')
    interval = mSetInterval(9000, 100000)
    filter_method = lambda i: i.value.get('SIZE', 0) in interval if i.value != NoValue else False
    print('Number of Matches: %i' % filetree.deep.filtered_len(filter_method, True))
    print('How many files are touched (modified) during the last day?')
    t = time.time()
    interval = mSetInterval(t - (60 * 60 * 24), t)
    filter_method = lambda i: i.value.get('MTIME', 0) in interval if i.value != NoValue else False
    print('Number of Matches: %i' % filetree.deep.filtered_len(filter_method, True))
    print('How many files are touched (modified) during the last minute?')
    t = time.time()
    interval = mSetInterval(t - 60, t)
    filter_method = lambda i: i.value.get('MTIME', 0) in interval if i.value != NoValue else False
    print('Number of Matches: %i' % filetree.deep.filtered_len(filter_method, True))
    # we render here the output (We do not expect to many matches)
    filetree.render(filter_method)
