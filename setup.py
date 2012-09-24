#!/usr/bin/env python

from distutils.core import setup

setup(
    name='rson',
    version='0.9',
    description='rson -- Readable Serial Objection Notation',
    long_description='''
The goal of the RSON project is to create file formats that are easy
to edit, diff, and version control.  The base RSON profile is a superset
of JSON and much smaller than YAML.
''',
    author='Patrick Maupin',
    author_email='pmaupin@gmail.com',
    platforms="Independent",
    url='http://code.google.com/p/rson/',
    packages=['rson', 'rson.base'],
    license="MIT",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='rson json yaml configuration file',
)
