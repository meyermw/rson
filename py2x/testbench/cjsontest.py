#!/usr/bin/env python

import sys

sys.path[0:0] = '..', 'simplejson'

import simplejson
import simplejson.tests
import rson.cjson

simplejson.loads = rson.cjson.loads
simplejson.JSONDecodeError = rson.cjson.ParseError

simplejson.tests.main()
