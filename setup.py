import os
import sys

from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='jira-term',
    version='0.1.0',
    py_modules=['jira_term'],
    install_requires=[
        'click',
        'jira',
    ],
    extras_require={
        'tables': ['tabulate==0.7.5'],
    },
    entry_points='''
        [console_scripts]
        jira-term=jira_term.cli:cli
    '''
)
