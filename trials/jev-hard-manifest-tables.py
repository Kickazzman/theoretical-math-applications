#!/usr/bin/env python3
"""Generate the manifest's item tables from jev-items-hard.json + verify report.

Reads local copies (scp'd from mrfloppy) and prints markdown rows:
- Table A: per function, gate results (correct pass, buggy_a/b fails).
- Table B: per item (40 rows), decision_id, type, function, prompt_ref,
  expected, and the gate basis.
Run AFTER the build step; paste output into jev-hard-materials.md.
"""
import json
import sys

ITEMS = json.load(open(sys.argv[1] if len(sys.argv) > 1 else
                        '/home/hatch/workspace/jev-items-hard.json'))
REPORT = json.load(open(sys.argv[2] if len(sys.argv) > 2 else
                         '/home/hatch/workspace/jev-verify-hard-report.json'))

print("## Table A — test-gate results per function\n")
print("| function | correct | buggy_a | buggy_b | AB_VALID |")
print("|---|---|---|---|---|")
for name, e in REPORT.items():
    c = e.get('correct', {})
    ba = e.get('buggy_a', {})
    bb = e.get('buggy_b', {})
    c_s = f"PASS {c.get('passed', '?')}/{c.get('passed', 0) + len(c.get('failed', [])) + len(c.get('errors', []))}"
    ba_s = f"FAIL {len(ba.get('failed', []))}F+{len(ba.get('errors', []))}E"
    bb_s = f"FAIL {len(bb.get('failed', []))}F+{len(bb.get('errors', []))}E"
    print(f"| {name} | {c_s} | {ba_s} | {bb_s} | {e.get('AB_VALID')} |")

print("\n## Table B — items (40)\n")
print("| id | type | function | prompt_ref | expected | gate basis |")
print("|---|---|---|---|---|---|")
for it in ITEMS['items']:
    fn = it['function']
    if it['type'] == 'a':
        basis = ("buggy_a fails gate; correct passes"
                 if it['expected'] == 'fail'
                 else "correct passes gate; buggy_b fails gate")
    else:
        basis = "better impl passes gate; worse impl fails gate"
    print(f"| {it['decision_id']} | {it['type']} | {fn} | {it['prompt_ref']} | "
          f"{it['expected']} | {basis} |")
print(f"\nSeed: {ITEMS['seed']}; counts: {ITEMS['counts']}")
