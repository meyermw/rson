#!/usr/bin/env python
'''
Test code for to run rson against simplejson testsuite.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/trunk/license.txt

'''


import sys
import re

sys.path[0:0] = '..', '../../../simplejson'

import simplejson
import simplejson.tests
import rson
import rson.pyjson


simplejson.loads = rson.pyjson.loads
simplejson.JSONDecodeError = rson.RSONDecodeError
simplejson.tests.main()
