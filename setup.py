# coding: utf-8

import os
import sys
from setuptools import setup, find_packages
from pip.req import parse_requirements

setup(
    name='hikidashi',
    version='0.0.1',
    url='https://github.com/pistatium/hikidashi',
    author='pistatium',
    description='Key-Value store over http protcol.',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'hikidashi=hikidashi.cmd:main'
        ]
    },
)