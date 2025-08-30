# -*- coding: utf-8 -*-
'''
start local unittest (pytest)
'''
import pytest
import os
import sys

if os.getenv('JOB_NAME') is None:
    #pytest.main(['-v', '../..'])
    #pytest.main(['--pep8', '../..'])
    #pytest.main(['-pylint', '../..'])
    pytest.main(['-s', '..'])
