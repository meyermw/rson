#!/usr/bin/env python

import sys
import os

sys.path.insert(0, '..')

from json import loads as sysloads
from rson.ejson import loads as newloads

strings = [open(os.path.join('styles', x), 'rb').read() for x in os.listdir('styles') if x.endswith('json')]

expected = [sysloads(x) for x in strings]
actual = [newloads(x) for x in strings]

print expected == actual
