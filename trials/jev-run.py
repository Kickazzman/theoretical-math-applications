#!/usr/bin/env python3
"""JEV contract test runner (runs ON mrfloppy, CPU for tests).

Fast seats: quicklook :8203 (primary) and hammer :8201 (second
opinion), called DIRECTLY on their ports (not via the router),
SEQUENTIALLY, one call at a time. Strict-JSON decision contract:
typed decision + confidence 0-1, NO prose. Prose is a contract
failure (flagged, not silently cleaned). Unparseable after 1
retry -> decision null, confidence null, counts against
fast-alone accuracy, excluded from buckets.

Slow side: the CALCULATOR (tests) for (a)/(b). For (c) only,
slow = the other fast seat's opinion; ground truth for (c) is
perg's batched agreement (pending, null here).

Escalation (a)/(b): quicklook confidence < 0.8 OR the two fast
seats disagree. Escalated items' final decision = calculator
(ground truth). Non-escalated final = quicklook decision.
(c): high-stakes True -> always escalated, final = hammer.

Outputs: ~/jev-test/jev-decisions.json (one row per decision),
~/jev-test/jev-summary.json (buckets, verdicts, thresholds).
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import urllib.request

QUICKLOOK = 'http://127.0.0.1:8203/v1/chat/completions'
HAMMER = 'http://127.0.0.1:8201/v1/chat/completions'
TEST_DIR = '/home/joshua/jev-test'

SHIM = textwrap.dedent('''
    """Minimal pytest shim: approx + raises only."""
    class _Approx:
        def __init__(self, expected, rel=None, abs=None):
            self.expected = expected
            self.rel = 1e-6 if rel is None else rel
            self.abs = 1e-12 if abs is None else abs
        def __eq__(self, other):
            try:
                diff = abs(other - self.expected)
            except Exception:
                return False
            return diff <= max(self.rel * abs(self.expected), self.abs)
        def __ne__(self, other):
            return not self.__eq__(other)
        def __repr__(self):
            return f"approx({self.expected!r})"
    def approx(expected, rel=None, abs=None):
        return _Approx(expected, rel=rel, abs=abs)
    class _Raises:
        def __init__(self, exc):
            self.exc = exc
            self.value = None
        def __enter__(self):
            return self
        def __exit__(self, etype, evalue, tb):
            if etype is None:
                raise AssertionError(f"DID NOT RAISE {self.exc}")
            if not issubclass(etype, self.exc):
                return False
            self.value = evalue
            return True
    def raises(exc):
        return _Raises(exc)
''')

RUNNER = textwrap.dedent('''
    import sys, traceback, json
    sys.path.insert(0, '.')
    import test_impl
    passed, failed, errors = [], [], []
    for name in sorted(dir(test_impl)):
        if not name.startswith('test_'):
            continue
        fn = getattr(test_impl, name)
        if not callable(fn):
            continue
        try:
            fn()
            passed.append(name)
        except AssertionError as e:
            failed.append({"test": name, "error": str(e)[:300]})
        except Exception as e:
            errors.append({"test": name, "error": f"{type(e).__name__}: {e}"[:300]})
    print(json.dumps({"passed": passed, "failed": failed, "errors": errors}))
''')


def run_tests(code_text, tests_text):
    """Calculator: run tests against code. Returns (harness_ok,
    passes_all, n_pass, n_notpass)."""
    d = tempfile.mkdtemp(prefix='jev-run-')
    try:
        with open(os.path.join(d, 'impl.py'), 'w') as f:
            f.write(code_text)
        with open(os.path.join(d, 'test_impl.py'), 'w') as f:
            f.write(tests_text)
        with open(os.path.join(d, 'pytest.py'), 'w') as f:
            f.write(SHIM)
        with open(os.path.join(d, 'run_tests.py'), 'w') as f:
            f.write(RUNNER)
        p = subprocess.run([sys.executable, 'run_tests.py'], cwd=d,
                           capture_output=True, text=True, timeout=120)
        out = p.stdout.strip()
        try:
            res = json.loads(out.splitlines()[-1])
            notpass = len(res['failed']) + len(res['errors'])
            return (True, notpass == 0, len(res['passed']), notpass)
        except Exception:
            return (False, False, 0, 0)
    except Exception:
        return (False, False, 0, 0)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def call_seat(url, model, system, user):
    """One chat-completions call. Returns raw content string or
    None on transport/server error.

    Token budget 4096: at 300, Qwen3-4B on :8203 spent the whole
    budget thinking and returned EMPTY after think-stripping;
    at 1024 a LONG (a) prompt still truncated mid-think
    (finish=length, raw_len=0); at 4096 the same prompt returns
    clean JSON. chat_template_kwargs enable_thinking=false is
    passed but does NOT suppress thinking on the pinned build
    (the model still thinks; the budget is what saves it) --
    kept as harmless. If the budget ever truncates again, the
    symptom is empty=True, not prose."""
    body = json.dumps({
        'model': model,
        'messages': [{'role': 'system', 'content': system},
                     {'role': 'user', 'content': user}],
        'temperature': 0, 'max_tokens': 4096, 'stream': False,
        'chat_template_kwargs': {'enable_thinking': False}})
    req = urllib.request.Request(url, data=body.encode(),
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.load(r)
        return resp['choices'][0]['message']['content']
    except Exception as e:
        print(f"  !! seat call failed ({url}): {e}", flush=True)
        return None


def parse_decision(content, allowed):
    """Parse a strict-JSON decision. Returns (decision,
    confidence, prose, think, empty, ok).

    - Think blocks (<think>...</think>, including an unclosed
      trailing one) are stripped before parsing: they are a
      reasoning trace, not answer prose. think=True records
      their presence; it is NOT counted as prose.
    - The decision object is found by its "decision" key (not a
      greedy first-brace-to-last-brace span, which breaks if
      the trace contains braces).
    - prose = non-whitespace text outside the JSON object after
      think-stripping (markdown fences count as prose: the
      contract says JSON ONLY).
    - empty = content was empty/whitespace (a serving artifact,
      NOT prose)."""
    if content is None:
        return (None, None, False, False, False, False)
    think = '<think>' in content
    stripped = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    stripped = re.sub(r'<think>.*$', '', stripped, flags=re.DOTALL)
    if not stripped.strip():
        return (None, None, False, think, True, False)
    m = re.search(r'\{[^{}]*"decision"[^{}]*\}', stripped, re.DOTALL)
    if not m:
        return (None, None, True, think, False, False)
    obj_text = m.group(0)
    outside = (stripped[:m.start()] + stripped[m.end():]).strip()
    prose = bool(outside)
    try:
        obj = json.loads(obj_text)
    except Exception:
        return (None, None, prose, think, False, False)
    dec = obj.get('decision')
    conf = obj.get('confidence')
    if dec not in allowed:
        return (None, None, prose, think, False, False)
    try:
        conf = float(conf)
    except Exception:
        return (None, None, prose, think, False, False)
    if not (0.0 <= conf <= 1.0):
        return (None, None, prose, think, False, False)
    return (dec, conf, prose, think, False, True)


def ask(url, model, system, user, allowed):
    """Call with 1 retry on unparseable output. Returns
    (decision, confidence, prose, think, empty, contract_ok,
    raw)."""
    raw = call_seat(url, model, system, user)
    dec, conf, prose, think, empty, ok = parse_decision(raw, allowed)
    if not ok:
        raw2 = call_seat(url, model, system, user)
        dec2, conf2, prose2, think2, empty2, ok2 = parse_decision(
            raw2, allowed)
        if ok2:
            return (dec2, conf2, prose2, think2, empty2, True, raw2)
        return (None, None, prose or prose2, think or think2,
                empty or empty2, False, raw2 or raw)
    return (dec, conf, prose, think, empty, True, raw)


SYS_A = ("You are a code reviewer deciding whether a code change "
         "passes its tests. Reply with JSON ONLY: no prose, no "
         "explanation, no markdown fences, no extra text. The JSON "
         "must have exactly two fields: \"decision\" (\"pass\" if "
         "the NEW code passes ALL the given tests, \"fail\" "
         "otherwise) and \"confidence\" (a number from 0 to 1, "
         "your estimated probability that your decision is "
         "correct).")
SYS_B = ("You are a code reviewer choosing the better "
         "implementation. Reply with JSON ONLY: no prose, no "
         "explanation, no markdown fences, no extra text. The JSON "
         "must have exactly two fields: \"decision\" (\"A\" or "
         "\"B\", the implementation that better satisfies the "
         "spec and would pass hidden tests written from it) and "
         "\"confidence\" (a number from 0 to 1, your estimated "
         "probability that your decision is correct).")
SYS_C = ("You are a code reviewer deciding whether a change is "
         "safe to merge. Reply with JSON ONLY: no prose, no "
         "explanation, no markdown fences, no extra text. The JSON "
         "must have exactly two fields: \"decision\" (\"merge\" "
         "if the change is safe to merge, \"do_not_merge\" "
         "otherwise) and \"confidence\" (a number from 0 to 1, "
         "your estimated probability that your decision is "
         "correct).")


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


BUCKETS = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01)]


def bucket_tables(rows):
    """rows: decision rows with fast_confidence + fast_correct.
    Returns {combined, a, b} bucket lists."""
    out = {}
    for subset, name in [(rows, 'combined'),
                         ([r for r in rows if r['type'] == 'a'], 'a'),
                         ([r for r in rows if r['type'] == 'b'], 'b')]:
        table = []
        for lo, hi in BUCKETS:
            cell = [r for r in subset
                    if r['fast_confidence'] is not None
                    and lo <= r['fast_confidence'] < hi]
            k = len(cell)
            s = sum(1 for r in cell if r['fast_correct'])
            lo_i, hi_i = wilson(s, k)
            table.append({'bucket': f"{lo}-{hi if hi < 1.01 else 1.0}",
                          'k': k, 'success': s,
                          'rate': (s / k if k else None),
                          'wilson95': [lo_i, hi_i]})
        low = [r for r in subset
               if r['fast_confidence'] is not None
               and r['fast_confidence'] < 0.5]
        lk = len(low)
        ls = sum(1 for r in low if r['fast_correct'])
        lo_i, hi_i = wilson(ls, lk)
        table.append({'bucket': '<0.5', 'k': lk, 'success': ls,
                      'rate': (ls / lk if lk else None),
                      'wilson95': [lo_i, hi_i]})
        out[name] = table
    return out


def main():
    with open(os.path.join(TEST_DIR, 'jev-items.json')) as f:
        items = json.load(f)['items']
    rows = []
    for it in items:
        print(f"{it['decision_id']} {it['type']} {it['prompt_ref']} ...",
              flush=True)
        if it['type'] == 'a':
            user = (f"Function: {it['function']}\nSpec: {it['spec']}\n"
                    f"OLD code:\n```python\n{it['old_code']}\n```\n"
                    f"NEW code (after the change):\n```python\n{it['new_code']}\n```\n"
                    f"Diff (OLD -> NEW):\n```diff\n{it['diff']}\n```\n"
                    f"Tests (the NEW code must pass ALL of these):\n"
                    f"```python\n{it['tests']}\n```\n"
                    f"Decide: does the NEW code pass ALL the given "
                    f"tests? Reply with JSON only.")
            qd, qc, qp, qt, qe, qok, qraw = ask(
                QUICKLOOK, 'quicklook', SYS_A, user, ['pass', 'fail'])
            hd, hc, hp, ht, he, hok, hraw = ask(
                HAMMER, 'hammer', SYS_A, user, ['pass', 'fail'])
            ok_h, passes, _, _ = run_tests(it['new_code'], it['tests'])
            gt = 'pass' if (ok_h and passes) else ('fail' if ok_h else 'error')
        elif it['type'] == 'b':
            user = (f"Function: {it['function']}\nSpec: {it['spec']}\n"
                    f"Implementation A:\n```python\n{it['impl_a']}\n```\n"
                    f"Implementation B:\n```python\n{it['impl_b']}\n```\n"
                    f"Which implementation better satisfies the spec? "
                    f"Reply with JSON only.")
            qd, qc, qp, qt, qe, qok, qraw = ask(
                QUICKLOOK, 'quicklook', SYS_B, user, ['A', 'B'])
            hd, hc, hp, ht, he, hok, hraw = ask(
                HAMMER, 'hammer', SYS_B, user, ['A', 'B'])
            # Calculator: run the authored tests against both impls.
            # (The authored tests are the hidden tests here: the
            # fast seats never see them.)
            with open(os.path.join(TEST_DIR, 'materials', it['function'],
                                   'tests.py')) as f:
                tests = f.read()
            ok_a, pass_a, _, _ = run_tests(it['impl_a'], tests)
            ok_b, pass_b, _, _ = run_tests(it['impl_b'], tests)
            if ok_a and ok_b and pass_a and not pass_b:
                gt = 'A'
            elif ok_a and ok_b and pass_b and not pass_a:
                gt = 'B'
            else:
                gt = 'ambiguous'
        else:  # c
            status = ('all tests pass' if it['test_status'] == 'pass'
                      else 'some tests fail')
            user = (f"Function: {it['function']}\nSpec: {it['spec']}\n"
                    f"Change:\n```diff\n{it['diff']}\n```\n"
                    f"Test status after this change: {status}.\n"
                    f"Should this change be merged? Reply with JSON "
                    f"only.")
            qd, qc, qp, qt, qe, qok, qraw = ask(
                QUICKLOOK, 'quicklook', SYS_C, user,
                ['merge', 'do_not_merge'])
            hd, hc, hp, ht, he, hok, hraw = ask(
                HAMMER, 'hammer', SYS_C, user, ['merge', 'do_not_merge'])
            gt = None

        if it['type'] in ('a', 'b'):
            fast_correct = (qd == gt) if qd is not None else False
            hammer_correct = (hd == gt) if hd is not None else False
            escalated = (qd is None or qc is None or qc < 0.8
                         or (qd is not None and hd is not None
                             and hd != qd))
            final = gt if escalated else qd
            final_correct = (final == gt)
            slow = gt
        else:
            fast_correct = None
            hammer_correct = None
            escalated = True
            final = hd
            final_correct = None
            slow = hd

        rows.append({
            'decision_id': it['decision_id'], 'type': it['type'],
            'prompt_ref': it['prompt_ref'],
            'fast_decision': qd, 'fast_confidence': qc,
            'fast_prose': qp, 'fast_think': qt, 'fast_empty': qe,
            'fast_contract_ok': qok,
            'fast_raw': (qraw or '')[:1500],
            'hammer_decision': hd, 'hammer_confidence': hc,
            'hammer_prose': hp, 'hammer_think': ht,
            'hammer_empty': he, 'hammer_contract_ok': hok,
            'hammer_raw': (hraw or '')[:1500],
            'slow_decision': slow, 'escalated': escalated,
            'ground_truth': gt, 'fast_correct': fast_correct,
            'hammer_correct': hammer_correct,
            'final_decision': final, 'correct': final_correct})
        print(f"  fast={qd}@{qc} hammer={hd}@{hc} gt={gt} "
              f"esc={escalated} final_ok={final_correct}", flush=True)

    with open(os.path.join(TEST_DIR, 'jev-decisions.json'), 'w') as f:
        json.dump(rows, f, indent=2)

    ab = [r for r in rows if r['type'] in ('a', 'b')]
    n_ab = len(ab)
    fast_acc = sum(1 for r in ab if r['fast_correct']) / n_ab
    hammer_acc = sum(1 for r in ab if r['hammer_correct']) / n_ab
    final_acc = sum(1 for r in ab if r['correct']) / n_ab
    improvement = (final_acc - fast_acc) * 100
    esc = [r for r in ab if r['escalated']]
    esc_rate = len(esc) / n_ab
    esc_fast_acc = (sum(1 for r in esc if r['fast_correct']) / len(esc)
                    if esc else None)
    esc_improvement = ((1.0 - esc_fast_acc) * 100
                       if esc_fast_acc is not None else None)
    agree = sum(1 for r in ab
                if r['fast_decision'] is not None
                and r['fast_decision'] == r['hammer_decision']) / n_ab
    q_prose = sum(1 for r in rows if r['fast_prose']) / len(rows)
    q_fail = sum(1 for r in rows if not r['fast_contract_ok']) / len(rows)
    h_fail = sum(1 for r in rows if not r['hammer_contract_ok']) / len(rows)
    q_think = sum(1 for r in rows if r['fast_think']) / len(rows)
    h_think = sum(1 for r in rows if r['hammer_think']) / len(rows)
    q_empty = sum(1 for r in rows if r['fast_empty']) / len(rows)
    h_empty = sum(1 for r in rows if r['hammer_empty']) / len(rows)
    h_prose = sum(1 for r in rows if r['hammer_prose']) / len(rows)

    tables = bucket_tables(ab)
    # Monotone over non-empty buckets (combined), top bucket check.
    comb = tables['combined'][:5]
    seq = [(t['bucket'], t['rate']) for t in comb if t['k'] > 0]
    monotone = all(seq[i][1] <= seq[i + 1][1] + 1e-9
                   for i in range(len(seq) - 1))
    top = tables['combined'][4]
    top_ok = top['k'] >= 5 and top['rate'] is not None and top['rate'] >= 0.85

    # Recommended threshold: lowest boundary with pooled success
    # >= 85% at/above it (pooled k >= 5), else "no safe threshold".
    thresholds = []
    recommended = None
    for t in [0.5, 0.6, 0.7, 0.8, 0.9]:
        pool = [r for r in ab
                if r['fast_confidence'] is not None
                and r['fast_confidence'] >= t]
        k = len(pool)
        s = sum(1 for r in pool if r['fast_correct'])
        rate = s / k if k else None
        esc_t = (sum(1 for r in ab
                     if r['fast_confidence'] is None
                     or r['fast_confidence'] < t) / n_ab)
        thresholds.append({'threshold': t, 'pooled_k': k,
                           'pooled_success': s, 'pooled_rate': rate,
                           'escalation_rate_conf_only': esc_t})
        if (recommended is None and k >= 5 and rate is not None
                and rate >= 0.85):
            recommended = t
    if recommended is None:
        recommended = 'no safe threshold'

    if top['k'] < 5:
        kill, kill_reasons = 0, ['top bucket k<5: UNDECIDED-VOID '
                                 '(sparse-data rule)']
    else:
        reasons = []
        if not top_ok:
            reasons.append(f"top bucket {top['rate']:.3f} < 0.85")
        if improvement < 10:
            reasons.append(f"escalation improvement {improvement:.1f}pp "
                           f"< 10pp")
        if reasons:
            kill, kill_reasons = -1, reasons
        else:
            kill, kill_reasons = 1, []

    summary = {
        'n_ab': n_ab, 'n_c': len([r for r in rows if r['type'] == 'c']),
        'fast_alone_accuracy_quicklook': fast_acc,
        'hammer_standalone_accuracy': hammer_acc,
        'escalated_accuracy': final_acc,
        'escalation_improvement_pp': improvement,
        'escalation_rate': esc_rate,
        'escalated_subset_fast_accuracy': esc_fast_acc,
        'escalated_subset_improvement_pp': esc_improvement,
        'agreement_rate_quicklook_hammer': agree,
        'quicklook_prose_rate': q_prose,
        'quicklook_think_rate': q_think,
        'quicklook_empty_rate': q_empty,
        'quicklook_contract_failure_rate': q_fail,
        'hammer_prose_rate': h_prose,
        'hammer_think_rate': h_think,
        'hammer_empty_rate': h_empty,
        'hammer_contract_failure_rate': h_fail,
        'buckets': tables,
        'bucket_sequence_nonempty': seq,
        'monotone': monotone,
        'top_bucket': top,
        'top_bucket_ge_85': top_ok,
        'thresholds': thresholds,
        'recommended_threshold': recommended,
        'kill_verdict': kill,
        'kill_reasons': kill_reasons,
        'ceiling_max_improvement_pp': (1.0 - fast_acc) * 100,
    }
    with open(os.path.join(TEST_DIR, 'jev-summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
