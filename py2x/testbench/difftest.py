#!/usr/bin/env python

import sys
import os

sys.path.insert(0, '..')

from json import loads as sysloads
from rson import loads as newloads

strings = [open(os.path.join('styles', x), 'rb').read() for x in os.listdir('styles') if x.endswith('json')]

expected = [sysloads(x) for x in strings]
actual = [newloads(x) for x in strings]

print expected == actual

result = []
for fname in 'styles/styles.json styles.rson'.split():
    text = open(fname, 'rb').read()
    data = newloads(text)
    data['styles'] = dict(data['styles'])
    result.append(data)

print result[0] == result[1]
