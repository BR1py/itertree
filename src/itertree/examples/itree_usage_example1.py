"""
This file contains some examples for the usage of itertree module

"""

from __future__ import absolute_import
import os
import sys
import time
from itertree import *


class FilesystemToItertree():
    """
    In this example for huge deep tree of items we read in the filesystem into an itertree and
    put some file attributes in the data
    """

    def __init__(self):
        self.tree = iTree('root')

    def load_from_path(self,source_folder):
        self.tree=iTree('root')
        self.get_items(source_folder,self.tree)

    def get_items(self,source_dir,root_item):
        try:
            for fd in os.listdir(source_dir):
                fd_path=os.path.join(source_dir,fd)
                if os.path.isfile(fd_path):
                    data={'SIZE': os.path.getsize(fd_path),
                          'ATIME':os.path.getatime(fd_path),
                          'CTIME': os.path.getctime(fd_path),
                          'MTIME': os.path.getmtime(fd_path),
                          'EXT': os.path.splitext(fd_path)[-1].replace('.',''),
                          'FULL_PATH': fd_path,
                          'TYPE': 'FILE',
                          'ACCESS': True
                          }
                    root_item.append(iTree(fd,data))
                elif os.path.isdir(fd_path):
                    dir_etree=iTree(fd, data={'TYPE': 'DIR','ACCESS':True})
                    root_item.append(dir_etree)
                    self.get_items(fd_path,dir_etree)
                else:
                    root_item.append(iTree(fd, data={'TYPE','UNKNOWN'}))
        except PermissionError:
            root_item.d_set('ACCESS',False)
    def get_item_tree(self):
        return self.tree

if __name__ == '__main__':
    """
    We run all the example (this will take a while and generate a huge print output!
    """
    if sys.platform == 'linux':
        root_dir='/usr/lib'
    else:
        # Windows
        root_dir="c:/ProgramData"
    print('We read a part of the filesystem (%s) into an itertree'%repr(root_dir))
    file_2_itree=FilesystemToItertree()
    file_2_itree.load_from_path(root_dir)
    filetree=file_2_itree.get_item_tree()
    # User might store the rendering into a file:
    #with open('d:/tmp/out.txt','wb') as fh:
    #    fh.write(filetree.renders().encode('utf8',errors='backslashreplace'))
    print('Number of items read in %i' % len(list(filetree.iter_all())))
    print('The load in tree has a depth of %i' % filetree.max_depth_down)
    print('How many files are bigger then 1000000 Bytes?')
    item_filter=Filter.iTFilterData(data_key='SIZE',data_value=iTInterval(1000000,'inf'))
    print('Number of Matches: %i'%len(list(filetree.iter_all(item_filter))))
    print('How many files are in size 9000 ~ 10000 Bytes?')
    item_filter=Filter.iTFilterData(data_key='SIZE',data_value=iTInterval(9000,10000))
    print('Number of Matches: %i'%len(list(filetree.iter_all(item_filter))))
    print('How many files are touched (modified) during the last day?')
    t=time.time()
    item_filter=Filter.iTFilterData(data_key='MTIME',data_value=iTInterval(t-(60*60*24),t))
    print('Number of Matches: %i'%len(list(filetree.iter_all(item_filter))))
    print('How many files are touched (modified) during the last minute?')
    t=time.time()
    item_filter=Filter.iTFilterData(data_key='MTIME',data_value=iTInterval(t-(60),t))
    print('Number of Matches: %i'%len(list(filetree.iter_all(item_filter))))
    # we render here the output (We do not expect to many matches)
    filetree.render(item_filter)

