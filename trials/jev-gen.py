#!/usr/bin/env python3
"""JEV test materials generator (runs ON mrfloppy).

Generator = magicoder :8202 (resident code seat). Judge (later) =
hammer/quicklook. Calculator (later + here for verification) =
pytest. Generator != judge != calculator.

For each function spec: ask magicoder for CORRECT impl + pytest
TESTS + BUGGY_A + BUGGY_B (subtle bugs, each failing >=1 test),
then (for c_diff functions) a REFACTOR or OPTIMIZE variant.
Writes materials/<name>/*.py. A separate verify step runs
pytest and reports which materials are valid; nothing here
asserts ground truth, it only collects candidates.
"""
import json, re, subprocess, sys, tempfile, os, urllib.request

BASE = '/home/joshua/jev-test/materials'
URL = 'http://127.0.0.1:8202/v1/chat/completions'
SPECS = json.load(open('/home/joshua/jev-test/jev-specs.json'))['functions']

SYS = ("You are a code generator. Output ONLY fenced python code "
       "blocks with the exact first-line labels requested. No prose "
       "outside code blocks. No explanations.")

def call_model(user_prompt, max_tokens=1600):
    body = json.dumps({
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": user_prompt}],
        "temperature": 0, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        out = json.load(r)
    msg = out["choices"][0]["message"]["content"]
    return msg

def parse_blocks(text, wanted):
    """Return dict label -> code for fenced python blocks whose
    first non-empty line is '# LABEL'."""
    found = {}
    for m in re.finditer(r"```python\s*\n(.*?)```", text, re.DOTALL):
        code = m.group(1)
        lines = [l for l in code.splitlines() if l.strip()]
        if not lines:
            continue
        first = lines[0].strip()
        for w in wanted:
            if first == "#" + w:
                found[w] = code
    return found

def gen_main(fn):
    prompt = (
        f"Function: {fn['name']}\nSpec: {fn['spec']}\n\n"
        "Output EXACTLY these 4 fenced python blocks, in this order, "
        "each starting with its label line and nothing else before it:\n"
        "```python\n# CORRECT\n<correct implementation>\n```\n"
        "```python\n# TESTS\n<pytest tests, importing the function with "
        f"\"from impl import {fn['name']}\">\n```\n"
        "```python\n# BUGGY_A\n<same function with ONE subtle bug; first line "
        "after the label must be a comment '# BUG: <what the bug is>'>\n```\n"
        "```python\n# BUGGY_B\n<same function with a DIFFERENT subtle bug; "
        "first line after the label must be '# BUG: <what the bug is>'>\n```\n"
        "Rules: CORRECT must satisfy the spec exactly. TESTS must cover "
        "every case listed in the spec. BUGGY_A and BUGGY_B must each fail "
        "at least one TEST. No prose outside the blocks.")
    for attempt in range(3):
        try:
            text = call_model(prompt)
        except Exception as e:
            print(f"  call failed (attempt {attempt+1}): {e}", flush=True)
            continue
        got = parse_blocks(text, ["CORRECT", "TESTS", "BUGGY_A", "BUGGY_B"])
        if len(got) == 4 and f"def {fn['name']}" in got["CORRECT"]:
            return got
        print(f"  parse incomplete (attempt {attempt+1}): got {sorted(got)}",
              flush=True)
    return None

def gen_cdiff(fn, correct_code):
    kind = fn['c_diff']  # 'refactor' or 'optimize'
    if kind == 'refactor':
        ask = ("a REFACTOR of the implementation that preserves behavior "
               "EXACTLY (same outputs on all inputs, only structure/style "
               "changes). It must pass all TESTS.")
    else:
        ask = ("an OPTIMIZATION of the implementation that passes all "
               "TESTS but changes implementation approach (faster or "
               "simpler code, same results on the tested cases).")
    label = kind.upper()
    prompt = (
        f"Function: {fn['name']}\nSpec: {fn['spec']}\n\n"
        f"Correct implementation:\n```python\n{correct_code}\n```\n\n"
        f"Output EXACTLY one fenced python block starting with '# {label}' "
        f"containing {ask} No prose outside the block.")
    for attempt in range(3):
        try:
            text = call_model(prompt)
        except Exception as e:
            print(f"  c_diff call failed (attempt {attempt+1}): {e}", flush=True)
            continue
        got = parse_blocks(text, [label])
        if label in got and f"def {fn['name']}" in got[label]:
            return got[label]
        print(f"  c_diff parse incomplete (attempt {attempt+1})", flush=True)
    return None

def main():
    os.makedirs(BASE, exist_ok=True)
    report = {}
    for fn in SPECS:
        name = fn['name']
        print(f"=== {name} (c_diff={fn['c_diff']}) ===", flush=True)
        got = gen_main(fn)
        d = os.path.join(BASE, name)
        os.makedirs(d, exist_ok=True)
        if got is None:
            report[name] = {"generated": False}
            print("  FAILED to generate main bundle", flush=True)
            continue
        for key, fname in [("CORRECT", "correct.py"), ("TESTS", "tests.py"),
                           ("BUGGY_A", "buggy_a.py"), ("BUGGY_B", "buggy_b.py")]:
            with open(os.path.join(d, fname), "w") as f:
                f.write(got[key])
        entry = {"generated": True, "c_diff": fn['c_diff']}
        if fn['c_diff'] in ("refactor", "optimize"):
            code = gen_cdiff(fn, got["CORRECT"])
            if code is None:
                entry["c_diff_generated"] = False
                print("  FAILED to generate c_diff", flush=True)
            else:
                with open(os.path.join(d, "c_diff.py"), "w") as f:
                    f.write(code)
                entry["c_diff_generated"] = True
        report[name] = entry
    with open('/home/joshua/jev-test/gen-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
