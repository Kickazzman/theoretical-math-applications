#!/usr/bin/env python3
"""JEV HARD variant generator: MUTATION-SPECIFIED variants via magicoder :8202 direct.

Same method as jev-gen-mutations.py: each prompt specifies EXACTLY one
mechanical edit; the parser keeps the first fenced block defining the
function that differs substantively from correct; 3 attempts; raw
saved on failure. Mutations loaded from jev-hard-mutations.json.
No router calls; :8202 direct only. No quicklook/hammer calls.
"""
import json
import os
import re
import urllib.request

BASE = '/home/joshua/jev-test/materials-hard'
URL = 'http://127.0.0.1:8202/v1/chat/completions'
MUTS = json.load(open('/home/joshua/jev-test/jev-hard-mutations.json'))

SYS = ("You are a code editor. Apply exactly the requested edit and "
       "output the full modified function in one fenced python code "
       "block. No prose outside the block.")


def call_model(user_prompt, max_tokens=1200):
    body = json.dumps({
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": user_prompt}],
        "temperature": 0, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def normalize(code):
    out = []
    for line in code.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        out.append(re.sub(r'\s+', ' ', s))
    return '\n'.join(out)


def pick_block(text, name, correct_code):
    want = normalize(correct_code)
    for m in re.finditer(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL):
        code = m.group(1)
        if f"def {name}" not in code:
            continue
        if normalize(code) == want:
            continue
        return code
    return None


def gen_variant(name, kind, edit, correct_code):
    prompt = (
        f"Here is a correct Python function:\n```python\n{correct_code}\n```\n\n"
        f"Apply EXACTLY this edit and nothing else: {edit}\n\n"
        "Output the full modified function in one fenced python code "
        "block. No prose outside the block.")
    raw_path = f"{BASE}/{name}/{kind.lower()}.raw.txt"
    for attempt in range(3):
        try:
            text = call_model(prompt)
        except Exception as e:
            print(f"  {kind} call failed (attempt {attempt+1}): {e}", flush=True)
            continue
        code = pick_block(text, name, correct_code)
        if code is not None:
            return code
        with open(raw_path, "w") as f:
            f.write(text)
        print(f"  {kind} no differing block (attempt {attempt+1}), raw saved",
              flush=True)
    return None


def main():
    report = {}
    for name in sorted(MUTS):
        d = os.path.join(BASE, name)
        correct_p = os.path.join(d, 'correct.py')
        if not os.path.exists(correct_p):
            print(f"=== {name}: NO correct.py, skipped ===", flush=True)
            report[name] = {"skipped": True}
            continue
        correct = open(correct_p).read()
        print(f"=== {name} ===", flush=True)
        entry = {}
        for kind, edit in MUTS[name].items():
            fname = {"BUGGY_A": "buggy_a.py", "BUGGY_B": "buggy_b.py"}[kind]
            code = gen_variant(name, kind, edit, correct)
            if code is None:
                entry[kind] = False
                print(f"  {kind}: FAILED", flush=True)
            else:
                with open(os.path.join(d, fname), "w") as f:
                    f.write(code)
                entry[kind] = True
                print(f"  {kind}: ok", flush=True)
        report[name] = entry
    with open('/home/joshua/jev-test/jev-hard-gen-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
