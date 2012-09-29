#!/usr/bin/env python

from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(
    name='rsonlite',
    version='0.1.0',
    description='rsonlite -- extremely lightweight version of rson',
    long_description=long_description,
    author='Patrick Maupin',
    author_email='pmaupin@gmail.com',
    platforms="Independent",
    url='http://code.google.com/p/rson/',
    py_modules=['rsonlite'],
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
    keywords='rson yaml configuration file',
)
