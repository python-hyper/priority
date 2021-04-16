#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='priority',
    version='1.3.0',
    description='A pure-Python implementation of the HTTP/2 priority tree',
    long_description=open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
    author='Cory Benfield',
    author_email='cory@lukasa.co.uk',
    url='https://github.com/python-hyper/priority/',
    project_urls={
        'Documentation': 'https://python-hyper.org/projects/priority/',
        'Source': 'https://github.com/python-hyper/priority/',
        'Tracker': 'https://github.com/python-hyper/priority/issues',
        'Changelog': 'https://github.com/python-hyper/priority/blob/master/HISTORY.rst',
    },
    packages=find_packages(where='src'),
    package_data={'': ['LICENSE', 'README.rst', 'CONTRIBUTORS.rst', 'HISTORY.rst']},
    package_dir={'': 'src'},
    include_package_data=True,
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
