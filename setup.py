from setuptools import setup

setup(
    name='itertree',
    version='1.0.1',
    packages=['itertree', 'itertree.examples', 'itertree.itree_serializer'],
    package_dir={'': 'src'},
    url='https://github.com/BR1py/itertree',
    license='MIT',
    author='B_R',
    author_email='br_development@posteo.org',
    description='Python tree structure for data storage and iterations'
)
