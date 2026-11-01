#!/usr/bin/env python3
"""JEV variant generator, v2: MUTATION-SPECIFIED variants.

Lesson from v1 (documented): free-form "invent a subtle bug"
failed completely -- magicoder echoed the correct code verbatim
under bug-name headers (no bug implemented) and ignored the
label format. Mechanical edits are a task it can do: each prompt
specifies EXACTLY one change to apply to the given correct code
and nothing else. Verification (jev-verify.py) remains the gate:
buggy must fail >= 1 test with zero errors; c_diff must pass
all tests AND differ substantively from correct.

Parser is robust to format games: it collects every fenced
block, keeps the first that defines the function AND differs
substantively from correct (comment/blank lines ignored).
Copies are rejected at generation time, not passed along.
Raw output is saved on failure.
"""
import json, os, re, urllib.request

BASE = '/home/joshua/jev-test/materials'
URL = 'http://127.0.0.1:8202/v1/chat/completions'
SPECS = {f['name']: f for f in
         json.load(open('/home/joshua/jev-test/jev-specs.json'))['functions']}

MUTATIONS = {
    'wilson_lower': {
        'BUGGY_A': "In the delta line, remove the math.sqrt call, so delta = z * (p * (1 - p) / n + z * z / (4 * n * n)) / denom. Change nothing else.",
        'BUGGY_B': "In the centre line, use z * z / n instead of z * z / (2 * n). Change nothing else.",
        'REFACTOR': "Rewrite so the denominator is computed once into a variable d, centre and delta both use d, and the clamp uses an if/else instead of max/min. Same outputs on all inputs.",
    },
    'median_of': {
        'BUGGY_A': "In the even-count case, return s[mid] instead of the mean of the two middle values. Change nothing else.",
        'BUGGY_B': "Sort the input list in place (values.sort()) and use it directly instead of working on a sorted copy. Change nothing else.",
        'REFACTOR': "Rewrite using indices lo = (n - 1) // 2 and hi = n // 2, returning (s[lo] + s[hi]) / 2 in all cases. Same outputs on all inputs.",
    },
    'format_duration': {
        'BUGGY_A': "Remove the `if days:`, `if hours:`, `if minutes:`, `if secs:` guards so all units are always emitted (keep the 0 -> '0s' early return). Change nothing else.",
        'BUGGY_B': "Remove the days computation entirely: compute hours as seconds // 3600 with no days unit. Change nothing else.",
        'REFACTOR': "Rewrite using a loop over (label, seconds) pairs [(d, 86400), (h, 3600), (m, 60), (s, 1)] building the parts list. Same outputs on all inputs.",
    },
    'parse_size': {
        'BUGGY_A': "Use 1000-based units (KB=1000, MB=1000**2, GB=1000**3, TB=1000**4) instead of 1024-based. Change nothing else.",
        'BUGGY_B': "Do not uppercase the unit part (remove the .upper() call), so units are case-sensitive. Change nothing else.",
        'REFACTOR': "Rewrite the numeric/unit split using a regex match instead of the while loop. Same outputs on all inputs.",
    },
    'backoff_delay': {
        'BUGGY_A': "Remove the cap: return base * (2 ** attempt) without min(). Change nothing else.",
        'BUGGY_B': "Use linear growth base * attempt instead of exponential base * (2 ** attempt). Change nothing else.",
        'OPTIMIZE': "Compute the power with a bit shift: base * (1 << attempt) instead of base * (2 ** attempt). Same outputs on all inputs.",
    },
    'sliding_average': {
        'BUGGY_A': "Use values[i:i + window + 1] and divide by window + 1 instead of window. Change nothing else.",
        'BUGGY_B': "Use integer division // instead of / when computing each mean. Change nothing else.",
        'OPTIMIZE': "Use a running-sum implementation: maintain a window sum, subtract the leaving element and add the entering one, instead of re-summing each window. Same outputs on all inputs.",
    },
    'chunk_list': {
        'BUGGY_A': "Only yield full chunks: iterate range(0, len(items) - size + 1, size) so a trailing partial chunk is dropped. Change nothing else.",
        'BUGGY_B': "Use size + 1 as both the chunk length and the step. Change nothing else.",
        'OPTIMIZE': "Use an iterator-based implementation with iter() and itertools.islice instead of range slicing. Same outputs on all inputs.",
    },
    'merge_intervals': {
        'BUGGY_A': "Do not sort the intervals first; process them in input order. Change nothing else.",
        'BUGGY_B': "Merge only when next.start < current.end (strict), so touching intervals are NOT merged. Change nothing else.",
    },
    'top_k': {
        'BUGGY_A': "Sort by count descending only (key=lambda kv: -kv[1]), so ties keep insertion order instead of key ascending. Change nothing else.",
        'BUGGY_B': "Sort by key descending first, then stable-sort by count descending, so ties come out key-descending instead of key-ascending. Change nothing else.",
    },
    'clamp': {
        'BUGGY_A': "Do not raise ValueError when lo > hi; just return value. Change nothing else.",
        'BUGGY_B': "Swap the clamp directions: return hi when value < lo, and lo when value > hi. Change nothing else.",
    },
    'slugify': {
        'BUGGY_A': "Replace each non-alphanumeric character with '-' individually (use [^a-z0-9] without the + quantifier), so runs are NOT collapsed. Change nothing else.",
        'BUGGY_B': "Do not strip leading/trailing hyphens (omit the .strip('-') call). Change nothing else.",
    },
    'dedupe_preserve_order': {
        'BUGGY_A': "Keep the LAST occurrence of each value instead of the first (keep x only if it does not appear later in the list). Change nothing else.",
        'BUGGY_B': "Only remove ADJACENT duplicates (keep x if it differs from the previous element). Change nothing else.",
    },
}

SYS = ("You are a code editor. Apply exactly the requested edit and "
       "output the full modified function in one fenced python code "
       "block. No prose outside the block.")

def call_model(user_prompt, max_tokens=700):
    body = json.dumps({
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": user_prompt}],
        "temperature": 0, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["choices"][0]["message"]["content"]

def normalize(code):
    """Substantive content: drop pure-comment and blank lines,
    collapse whitespace. Used to detect verbatim copies."""
    out = []
    for line in code.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        out.append(re.sub(r'\s+', ' ', s))
    return '\n'.join(out)

def pick_block(text, name, correct_code):
    """First fenced block defining the function that differs
    substantively from correct. Returns None if no such block."""
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
    raw_path = f"/home/joshua/jev-test/materials/{name}/{kind.lower()}.raw.txt"
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
    for name, fn in SPECS.items():
        d = os.path.join(BASE, name)
        correct_p = os.path.join(d, 'correct.py')
        if not os.path.exists(correct_p):
            continue
        correct = open(correct_p).read()
        muts = MUTATIONS.get(name, {})
        print(f"=== {name} ===", flush=True)
        entry = {}
        for kind, edit in muts.items():
            fname = {"BUGGY_A": "buggy_a.py", "BUGGY_B": "buggy_b.py",
                     "REFACTOR": "c_diff.py",
                     "OPTIMIZE": "c_diff.py"}[kind]
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
    with open('/home/joshua/jev-test/gen-mutations-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
