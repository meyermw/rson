#!/usr/bin/env python

import sys
import time
import os

sys.path.insert(0, '..')
sys.path.insert(0, 'simplejson')

from rson import loads
#from simplejson import loads
#from json import loads

strings = [open(os.path.join('styles', x), 'rb').read() for x in os.listdir('styles') if x.endswith('json')]

endtime = time.time() + 10.0

i = 0
while time.time() < endtime:
    z = [loads(x) for x in strings]
    i += 1

print i
