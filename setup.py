"""
This code is taken from the itertree package:
 _ _____ _____ _____ _____ _____ _____ _____
 | |_   _|   __| __  |_   _| __  |   __|   __|
 |-| | | |   __|    -| | | |    -|   __|   __|
 |_| |_| |_____|__|__| |_| |__|__|_____|_____|

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

