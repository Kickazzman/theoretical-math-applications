#!/usr/bin/env python3
"""JEV variant generator: magicoder supplies ONLY variants.

Given the authored correct implementation + tests, ask magicoder
for ONE variant per call (single fenced block, robust parsing):
- BUGGY_A, BUGGY_B: same function with ONE subtle bug, failing
  >= 1 test. First line after the label: '# BUG: <what it is>'.
- REFACTOR / OPTIMIZE (c_diff functions): behavior-preserving
  refactor, or an optimization passing all tests.
Raw output is saved on parse failure (the earlier 4-block run
failed parsing on all 12 with no raw saved -- never again).
Verification (jev-verify.py) decides VALID/INVALID afterwards.
"""
import json, os, re, urllib.request

BASE = '/home/joshua/jev-test/materials'
URL = 'http://127.0.0.1:8202/v1/chat/completions'
SPECS = {f['name']: f for f in
         json.load(open('/home/joshua/jev-test/jev-specs.json'))['functions']}

SYS = ("You are a code generator. Output EXACTLY one fenced python "
       "code block with the requested first-line label. No prose "
       "outside the block.")

def call_model(user_prompt, max_tokens=900):
    body = json.dumps({
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": user_prompt}],
        "temperature": 0, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def parse_one(text, label):
    for m in re.finditer(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL):
        code = m.group(1)
        lines = [l for l in code.splitlines() if l.strip()]
        if lines and lines[0].strip() == "#" + label:
            return code
    return None

def gen_variant(name, kind, correct_code, tests_code):
    """kind: BUGGY_A, BUGGY_B, REFACTOR, OPTIMIZE."""
    if kind.startswith("BUGGY"):
        ask = ("Rewrite the function with ONE subtle bug (for example an "
               "off-by-one, a wrong operator, a missed edge check, or a "
               "wrong tie-break). The buggy version MUST fail at least one "
               "of the given tests. First line after the label must be a "
               "comment '# BUG: <what the bug is>'.")
    elif kind == "REFACTOR":
        ask = ("Rewrite the function as a behavior-preserving refactor: "
               "same outputs on ALL inputs, only structure/style changes. "
               "It must pass all given tests.")
    else:  # OPTIMIZE
        ask = ("Rewrite the function as an optimization or simplification "
               "that passes all given tests but changes implementation "
               "approach (faster or simpler code, same results on the "
               "tested cases).")
    prompt = (
        f"Function: {name}\nCorrect implementation:\n```python\n"
        f"{correct_code}\n```\nTests it must relate to:\n```python\n"
        f"{tests_code}\n```\n\nOutput EXACTLY one fenced python block "
        f"starting with '# {kind}' containing {ask} No prose outside "
        "the block.")
    raw_path = f"/home/joshua/jev-test/materials/{name}/{kind.lower()}.raw.txt"
    for attempt in range(3):
        try:
            text = call_model(prompt)
        except Exception as e:
            print(f"  {kind} call failed (attempt {attempt+1}): {e}", flush=True)
            continue
        code = parse_one(text, kind)
        if code and f"def {name}" in code:
            return code
        with open(raw_path, "w") as f:
            f.write(text)
        print(f"  {kind} parse failed (attempt {attempt+1}), raw saved",
              flush=True)
    return None

def main():
    report = {}
    for name, fn in SPECS.items():
        d = os.path.join(BASE, name)
        correct_p = os.path.join(d, 'correct.py')
        tests_p = os.path.join(d, 'tests.py')
        if not (os.path.exists(correct_p) and os.path.exists(tests_p)):
            print(f"=== {name}: SKIP (no authored correct/tests) ===", flush=True)
            continue
        correct = open(correct_p).read()
        tests = open(tests_p).read()
        print(f"=== {name} ===", flush=True)
        entry = {}
        for kind, fname in [("BUGGY_A", "buggy_a.py"),
                            ("BUGGY_B", "buggy_b.py")]:
            code = gen_variant(name, kind, correct, tests)
            if code is None:
                entry[kind] = False
                print(f"  {kind}: FAILED", flush=True)
            else:
                with open(os.path.join(d, fname), "w") as f:
                    f.write(code)
                entry[kind] = True
                print(f"  {kind}: ok", flush=True)
        cd = fn['c_diff']
        if cd in ("refactor", "optimize"):
            kind = cd.upper()
            code = gen_variant(name, kind, correct, tests)
            if code is None:
                entry[kind] = False
                print(f"  {kind}: FAILED", flush=True)
            else:
                with open(os.path.join(d, "c_diff.py"), "w") as f:
                    f.write(code)
                entry[kind] = True
                print(f"  {kind}: ok", flush=True)
        report[name] = entry
    with open('/home/joshua/jev-test/gen-variants-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
