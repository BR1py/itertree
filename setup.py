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

setup.py for builds and installation
"""

from setuptools import setup

setup(
    name='itertree',
    version='1.2.0',
    packages=['itertree', 'itertree.examples', 'itertree.itree_serializer','itertree.itree_indepth_helpers'],
    package_dir={'': 'src'},
    url='https://github.com/BR1py/itertree',
    license='MIT',
    author='B_R',
    author_email='br_development@posteo.org',
    description='Python tree structure for data storage and iterations'
)

