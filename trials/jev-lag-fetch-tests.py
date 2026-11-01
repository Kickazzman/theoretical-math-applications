#!/usr/bin/env python3
"""Runs ON mrfloppy. Dump tests.py for every function in both materials
dirs as JSON {function: tests_text} on stdout. Read-only."""
import json
import os

out = {}
for base in ('/home/joshua/jev-test/materials',
             '/home/joshua/jev-test/materials-hard'):
    for fn in sorted(os.listdir(base)):
        p = os.path.join(base, fn, 'tests.py')
        if os.path.isfile(p):
            with open(p) as f:
                out[fn] = f.read()
print(json.dumps(out))
