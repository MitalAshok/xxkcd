#!/usr/bin/env python

import sys
import os
import codecs

from setuptools import setup, find_packages


__dir__ = os.path.abspath(os.path.dirname(__file__))

# To prevent a redundant __version__, import it from the packages
sys.path.insert(0, os.path.join(__dir__, 'xxkcd'))

try:
    from metadata import __version__, __author__, __email__
finally:
    sys.path.pop(0)

with codecs.open(os.path.join(__dir__, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup_args = dict(
    name='xxkcd',

    version=__version__,

    description='An (unofficial) Python wrapper around xkcd APIs',
    long_description=long_description,

    url='https://github.com/MitalAshok/xxkcd',

    author=__author__,
    author_email=__email__,

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    ],
    platforms=['any'],

    keywords=['xkcd', 'api', 'wrapper', 'what-if'],

    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),

    install_requires=[
        'objecttools>=0.0.4'
    ],
    extras_require={},
    entry_points={},

    test_suite='tests'
)


setup(**setup_args)
