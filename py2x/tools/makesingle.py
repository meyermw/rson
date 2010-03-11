#!/usr/bin/env python

import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rson'))

imports = set()

def splitfile(s):
    top, bottom = s.split('\nclass ',1)
    bottom = '\nclass ' + bottom
    for line in top.splitlines():
        if line.startswith('import'):
            mod, = line.split()[1:]
            imports.add(mod)
    return bottom

def split_init(s):
    top, bottom = s.split('\n# RSON is developed')
    bottom = '\n'.join(x[4:] for x in bottom.splitlines())
    return top, splitfile(bottom)

files = 'tokenizer baseobjects dispatcher doublequoted unquoted parser __init__'
files = files.split()
files = [open(os.path.join(root, x+'.py'), 'rb').read() for x in files]
init_top, init_bottom = split_init(files.pop())
files = [splitfile(x) for x in files]

result = [init_top]
result.extend('import %s' % x for x in sorted(imports))
result.extend(files)
result.append(init_bottom)
result.append('')
result = '\n'.join(result)
f = open(os.path.join(root, 'rson_single.py'), 'wb')
f.write(result)
f.close()
print
print "rson_single.py written"
print
