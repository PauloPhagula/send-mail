#!/usr/bin/env python
# coding: utf-8
"""
Setup script for package.
"""
from __future__ import unicode_literals, print_function
import os
import sys
import codecs
from email.utils import parseaddr
from setuptools import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py register')
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload --universal')
    sys.exit()


def file_get_contents(filename):
    """Reads an entire file into a string."""
    assert os.path.exists(filename) and os.path.isfile(filename), 'invalid filename: ' + filename
    return codecs.open(filename, 'r', 'utf-8').read()

SETUP_DIR = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION = '\n'.join([file_get_contents('README.md'), file_get_contents('CHANGELOG.md')])

setup(
    name='send_mail',
    version='0.1.0',
    description='Simple email sending module for use in ETL/reporting script.',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/dareenzo/send_mail',
    author='Paulo Phagula',
    author_email='pphagula@gmail.com',
    license='See LICENSE',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ),
    keywords=('mail', 'smtp'),
    py_modules=['send_mail'],
    install_requires=['six', 'html2text'],
    platforms=('any'),
    include_package_data=True,
    zip_safe=False
)
