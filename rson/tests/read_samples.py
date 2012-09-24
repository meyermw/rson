import os

f = open(os.path.join(os.path.dirname(__file__), 'samples.txt'))
data = f.read()
f.close()

data = data.split('\n---\n')
data = [x.replace('--', '\t').replace('-', '') for x in data]
