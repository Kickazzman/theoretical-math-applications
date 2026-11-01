#!/usr/bin/env python3
"""Probe magicoder raw output format for one function."""
import json, urllib.request
URL = 'http://127.0.0.1:8202/v1/chat/completions'
SYS = ("You are a code generator. Output ONLY fenced python code "
       "blocks with the exact first-line labels requested. No prose "
       "outside code blocks. No explanations.")
prompt = (
    "Function: wilson_lower\n"
    "Spec: Wilson score interval lower bound for a proportion. "
    "wilson_lower(k, n, z=1.96): k successes out of n trials. n==0 "
    "returns 0.0. k<0 or k>n or n<0 raises ValueError.\n\n"
    "Output EXACTLY these 4 fenced python blocks, in this order, "
    "each starting with its label line and nothing else before it:\n"
    "```python\n# CORRECT\n<correct implementation>\n```\n"
    "```python\n# TESTS\n<pytest tests, importing the function with "
    "\"from impl import wilson_lower\">\n```\n"
    "```python\n# BUGGY_A\n<same function with ONE subtle bug>\n```\n"
    "```python\n# BUGGY_B\n<same function with a DIFFERENT subtle bug>\n```\n"
    "Rules: CORRECT must satisfy the spec exactly. No prose outside "
    "the blocks.")
body = json.dumps({
    "messages": [{"role": "system", "content": SYS},
                 {"role": "user", "content": prompt}],
    "temperature": 0, "max_tokens": 1600}).encode()
req = urllib.request.Request(URL, data=body,
                             headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=180) as r:
    out = json.load(r)
msg = out["choices"][0]["message"]["content"]
open('/home/joshua/jev-test/probe-raw.txt', 'w').write(msg)
print(f"RAW LENGTH: {len(msg)}")
print(msg[:3000])
