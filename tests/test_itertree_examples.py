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



The main goal of this test is that the examples run without any exception
"""

import os
import sys
import shutil
import collections
# import timeit
import pytest

from itertree import *

root_path = os.path.dirname(os.path.dirname(__file__))
print('ROOT_PATH', root_path)


print('Test start')

@pytest.fixture(scope="session")
def out_file(tmpdir_factory):
    i=0
    while 1:
        fn = str(tmpdir_factory.mktemp("data").join("test_%i.out"%i))
        if not os.path.exists(fn):
            break
        i+=1
    return fn


class Test_iTree_Examples:
    EXAMPLE_FILES=['itree_usage_example1.py','itree_link_example1.py','itree_data_models.py',
                   'itree_docu_examples.py','calendar_example.py']
    PERFORMANCE_FILES = [('itree_performance.py', '10'), ('itree_performance2.py', '2'),
                     ('itree_profile.py', '10'), ('itree_profile2.py', '1')]

    def _examples_base(self,index,out_file):
        file=self.EXAMPLE_FILES[index]
        print('\n<- RESULT OF TEST: %s'%file)
        rel_example_dir=os.path.join(root_path,'src','itertree','examples')
        temp_file_path=out_file
        target_file=os.path.join(rel_example_dir,file)
        print('We ran: %s'%target_file)
        assert os.path.exists(target_file)
        error_code=os.system(sys.executable+' '+target_file+' > %s'%temp_file_path)
        if error_code!=0:
            with open(temp_file_path,'r') as fh:
                output=fh.read()
        assert error_code==0,'Example file: %s was not executed with success!\n\n%s'%(file,output)
        #clean up delete the temp_file
        os.remove(temp_file_path)

    def _performance_base(self,index,out_file):
        file, max_len=self.PERFORMANCE_FILES[index]
        print('\n<- RESULT OF TEST: %s'%file)
        rel_example_dir=os.path.join(root_path,'src','itertree','examples')
        temp_file_path=out_file
        target_file=os.path.join(rel_example_dir,file)
        print('We ran: %s'%target_file)
        assert os.path.exists(target_file)
        error_code=os.system(sys.executable+' '+target_file+' %s'%max_len+'2>> %s'%temp_file_path)
        assert error_code==0,'Example file: %s was not executed with success!'%file


    def test_example0(self,out_file):
        self._examples_base(0,out_file)

    def test_example1(self,out_file):
        self._examples_base(1,out_file)

    def test_example2(self,out_file):
        self._examples_base(2,out_file)

    def test_example3(self,out_file):
        self._examples_base(3,out_file)

    def test_example4(self,out_file):
        self._examples_base(4,out_file)


