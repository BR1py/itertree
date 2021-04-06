# -*- coding: iso-8859-1 -*-#
'''
start local unittest (pytest)
'''
import pytest
import os
import sys

if os.getenv('JOB_NAME') is None:
    # No execution in JenkinsJobs
    #pytest.main(['-v', '../..'])
    #pytest.main(['--pep8', '../..'])
    #pytest.main(['-pylint', '../..'])
    if 'LINUX_UNIT_TEST_ACTIVE' not in sys.path:
        sys.path.append('LINUX_UNIT_TEST_ACTIVE')
        pytest.main(['-s', '..'])
