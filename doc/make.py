#!/usr/bin/env python

import sys
import subprocess
sys.path.insert(0, '../py2x')
from rson import loads
from simplejson import dumps

data = iter(open('manual.txt', 'rb').read().splitlines())

result = []
for line in data:
    result.append(line)
    while line.endswith('::') and '..' not in line:
        result[-1] = line.replace(' (break)', '')
        pagebreak = line != result[-1]
        indent = line[:len(line) - len(line.lstrip())] + ' '
        index = len(result)
        for line in data:
            if line.strip() and not line.startswith(indent):
                break
            result.append(line)
        code = '\n'.join(result[index:])
        code = loads(code)
        code = dumps(code, indent=2)
        code = '\n'.join(indent + '   ' + x for x in code.splitlines())
        if pagebreak:
            result.append('.. page::')
            result.append('')
        result.append(indent[:-1] + 'Results in the following equivalent JSON::')
        result.append('')
        result.append(code)
        result.append('')
        result.append(line)

result.append('')
result = '\n'.join(result)

f = open('manual2.txt', 'wb')
f.write(result)
f.close()

subprocess.call('../../rst2pdf/bin/rst2pdf manual2.txt -e preprocess -e dotted_toc -o manual.pdf'.split())

lines = result.splitlines()
result = []
for line in lines:
    if 'page::' not in line and 'space::' not in line:
        result.append(line)

result.append('')
result = '\n'.join(result)

f = open('manual3.txt', 'wb')
f.write(result)
f.close()

