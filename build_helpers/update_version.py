# -*- coding: utf-8 -*-
import os
VERSION='1.1.3'

def replacer(filename,pre_tag,post_tag):
    print('Update version in %s' % filepath)
    if type(pre_tag) is str:
        o1='r'
        o2='w'
        version=VERSION
    else:
        o1='rb'
        o2='wb'
        version=VERSION.encode()

    with open(filepath, o1) as fh:
        text = fh.read()
    i1 = text.find(pre_tag)
    if i1==-1:
        raise SyntaxError('pre_tag not found!')
    i1=i1 + len(pre_tag)
    i2 = text.find(post_tag, (i1 + 1))
    if i2==-1:
        raise SyntaxError('post_tag not found!')
    if i2-i1>len(version):
        raise SyntaxError('Extracted search string to large!')
    print('Old version found:', repr(text[i1:i2]), '(position: %i:%i)' % (i1, i2))
    text = text[:i1] + version + text[i2:]
    with open(filepath, o2) as fh:
        fh.write(text)
    print('%s version updated\n' % filepath)


#README.md

print('Write version: %s into the files\n'%VERSION)

filepath = 'src/itertree/__init__.py'
pre_tag=b'__version__ = \''
post_tag=b'\''
replacer(filepath,pre_tag,post_tag)


filepath = 'README.md'
pre_tag='Release '
post_tag=' '
replacer(filepath,pre_tag,post_tag)

#setup.cfg
filepath = 'setup.cfg'
pre_tag='version = '
post_tag='\n'
replacer(filepath,pre_tag,post_tag)

#setup.py
filepath = 'setup.py'
pre_tag='version=\''
post_tag='\''
replacer(filepath,pre_tag,post_tag)

filepath='docs/conf.py'
pre_tag='release = \''
post_tag='\''
replacer(filepath,pre_tag,post_tag)

filepath = 'docs/index.rst'
pre_tag='Version | '
post_tag='|'
replacer(filepath,pre_tag,post_tag)

print('HINT: Versions in docs/changelog.rst are not updated!\n')
