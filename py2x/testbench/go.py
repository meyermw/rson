#!/usr/bin/env python

import sys

sys.path[0:0] = '..', 'simplejson'

import simplejson
import rson.ejson

simplejson.loads = rson.ejson.loads

import tests
tests.main()
