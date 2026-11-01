#!/usr/bin/env python3
"""Derive jev-hard-verify.py from the original jev-verify.py by path swaps only.

Original is untouched; the derived copy reads materials-hard /
jev-specs-hard.json and writes jev-verify-hard-report.json. No logic
changes: AB_VALID still requires correct all-pass + both buggy failing
>= 1 test with the harness intact.
"""
src = open('/home/joshua/jev-test/jev-verify.py').read()
src = src.replace("'/home/joshua/jev-test/materials'",
                  "'/home/joshua/jev-test/materials-hard'")
src = src.replace("'/home/joshua/jev-test/jev-specs.json'",
                  "'/home/joshua/jev-test/jev-specs-hard.json'")
src = src.replace("'/home/joshua/jev-test/verify-report.json'",
                  "'/home/joshua/jev-test/jev-verify-hard-report.json'")
open('/home/joshua/jev-test/jev-hard-verify.py', 'w').write(src)
print('patched verify: materials-hard + jev-specs-hard.json + jev-verify-hard-report.json')
