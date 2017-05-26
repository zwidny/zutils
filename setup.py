# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from setuptools import setup, find_packages
from codecs import open
from os import path

REPO = path.dirname(path.abspath(__file__))

# Get the long description from the README file
with open(path.join(REPO, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='zutils',
    version='0.1.0',
    description='Some utils for python dev',
    long_description=long_description,
    url='https://github.com/zwidny/zutils',
    author='zwidny',
    author_email='649038269@qq.com',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
    ],
    keywords='python dev utils',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['django'],

)
