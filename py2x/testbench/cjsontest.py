#!/usr/bin/env python

import sys
import cProfile

sys.path[0:0] = '..', 'simplejson'

import simplejson
import simplejson.tests
import rson.cjson
import rson.tokenizer

simplejson.loads = rson.cjson.loads
simplejson.JSONDecodeError = rson.tokenizer.RSONDecodeError

simplejson.tests.main()

#cProfile.run('simplejson.tests.main()')
