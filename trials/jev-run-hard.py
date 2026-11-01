#!/usr/bin/env python3
"""JEV contract test, HARDER materials run (runs ON mrfloppy).

Fast seats: quicklook :8203 (primary) and hammer :8201 (second
opinion), called DIRECTLY on their ports (never the router),
SEQUENTIALLY, one call at a time. Strict-JSON decision contract,
same as the original run (jev-run.py): typed decision +
confidence 0-1, NO prose. Token budget 4096, temp 0, 1 retry on
unparseable output. Prompts carry the spec AS WRITTEN in the
items file -- nothing from any manifest's test-encoded readings.

Slow side: the CALCULATOR (local Python tests) for (a) and (b).
(a) ground truth = tests on NEW code (item's tests field).
(b) ground truth = authored tests (materials-hard/<fn>/tests.py)
run against both impls. No (c) items in this set.

Escalation: FULL rule (null OR confidence < 0.8 OR disagreement)
and LEANER rule (null OR confidence < 0.8, no disagreement).
Both final accuracies + escalation rates reported. Correction
path measured: did escalation fix any wrong confident call?

Outputs: ~/jev-test/jev-decisions-hard.json (40 rows, original
log template + lean fields + bare-word flags + gt-mismatch flags),
~/jev-test/jev-summary-hard.json.
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
    d = tempfile.mkdtemp(prefix='jev-hard-run-')
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
    """One chat-completions call. Token budget 4096 (see original
    runner: at 300/1024 Qwen3-4B truncated mid-think -> empty;
    at 4096 clean JSON). chat_template_kwargs enable_thinking
    passed but does NOT suppress thinking on the pinned build."""
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
    """Same parser as the original run. Returns (decision,
    confidence, prose, think, empty, ok)."""
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


def is_bare_word(raw, allowed):
    """Bare-word classification (analysis only, NOT part of the
    original parser): after think-strip and fence-strip, the
    whole response is exactly one allowed decision token and
    contains no JSON object."""
    if raw is None:
        return False
    s = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    s = re.sub(r'<think>.*$', '', s, flags=re.DOTALL)
    s = s.strip()
    s = re.sub(r'^```[a-zA-Z]*\s*', '', s)
    s = re.sub(r'\s*```$', '', s)
    s = s.strip()
    return s in allowed and '{' not in s


def ask(url, model, system, user, allowed):
    """Call with 1 retry on unparseable output. Returns
    (decision, confidence, prose, think, empty, contract_ok,
    bare_word, raw)."""
    raw = call_seat(url, model, system, user)
    dec, conf, prose, think, empty, ok = parse_decision(raw, allowed)
    if not ok:
        raw2 = call_seat(url, model, system, user)
        dec2, conf2, prose2, think2, empty2, ok2 = parse_decision(
            raw2, allowed)
        if ok2:
            return (dec2, conf2, prose2, think2, empty2, True,
                    is_bare_word(raw2, allowed), raw2)
        return (None, None, prose or prose2, think or think2,
                empty or empty2, False,
                is_bare_word(raw2, allowed) or is_bare_word(raw, allowed),
                raw2 or raw)
    return (dec, conf, prose, think, empty, True,
            is_bare_word(raw, allowed), raw)


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
    with open(os.path.join(TEST_DIR, 'jev-items-hard.json')) as f:
        items = json.load(f)['items']
    assert len(items) == 40, len(items)
    assert all(it['type'] in ('a', 'b') for it in items)
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
            qd, qc, qp, qt, qe, qok, qb, qraw = ask(
                QUICKLOOK, 'quicklook', SYS_A, user, ['pass', 'fail'])
            hd, hc, hp, ht, he, hok, hb, hraw = ask(
                HAMMER, 'hammer', SYS_A, user, ['pass', 'fail'])
            ok_h, passes, _, _ = run_tests(it['new_code'], it['tests'])
            gt = 'pass' if (ok_h and passes) else ('fail' if ok_h else 'error')
        else:  # b
            user = (f"Function: {it['function']}\nSpec: {it['spec']}\n"
                    f"Implementation A:\n```python\n{it['impl_a']}\n```\n"
                    f"Implementation B:\n```python\n{it['impl_b']}\n```\n"
                    f"Which implementation better satisfies the spec? "
                    f"Reply with JSON only.")
            qd, qc, qp, qt, qe, qok, qb, qraw = ask(
                QUICKLOOK, 'quicklook', SYS_B, user, ['A', 'B'])
            hd, hc, hp, ht, he, hok, hb, hraw = ask(
                HAMMER, 'hammer', SYS_B, user, ['A', 'B'])
            # Calculator: authored tests against both impls. The
            # fast seats never see these tests.
            with open(os.path.join(TEST_DIR, 'materials-hard',
                                   it['function'], 'tests.py')) as f:
                tests = f.read()
            ok_a, pass_a, _, _ = run_tests(it['impl_a'], tests)
            ok_b, pass_b, _, _ = run_tests(it['impl_b'], tests)
            if ok_a and ok_b and pass_a and not pass_b:
                gt = 'A'
            elif ok_a and ok_b and pass_b and not pass_a:
                gt = 'B'
            else:
                gt = 'ambiguous'

        item_expected = it['expected']
        gt_mismatch = (gt != item_expected)
        fast_correct = (qd == gt) if qd is not None else False
        hammer_correct = (hd == gt) if hd is not None else False
        # FULL rule: null OR <0.8 OR disagreement.
        escalated = (qd is None or qc is None or qc < 0.8
                     or (qd is not None and hd is not None
                         and hd != qd))
        final = gt if escalated else qd
        final_correct = (final == gt)
        # LEANER rule: null OR <0.8, no disagreement.
        escalated_lean = (qd is None or qc is None or qc < 0.8)
        final_lean = gt if escalated_lean else qd
        lean_correct = (final_lean == gt)

        rows.append({
            'decision_id': it['decision_id'], 'type': it['type'],
            'prompt_ref': it['prompt_ref'],
            'fast_decision': qd, 'fast_confidence': qc,
            'fast_prose': qp, 'fast_think': qt, 'fast_empty': qe,
            'fast_contract_ok': qok, 'fast_bare_word': qb,
            'fast_raw': (qraw or '')[:1500],
            'hammer_decision': hd, 'hammer_confidence': hc,
            'hammer_prose': hp, 'hammer_think': ht,
            'hammer_empty': he, 'hammer_contract_ok': hok,
            'hammer_bare_word': hb,
            'hammer_raw': (hraw or '')[:1500],
            'slow_decision': gt, 'escalated': escalated,
            'escalated_lean': escalated_lean,
            'ground_truth': gt, 'item_expected': item_expected,
            'gt_mismatch': gt_mismatch,
            'fast_correct': fast_correct,
            'hammer_correct': hammer_correct,
            'final_decision': final, 'correct': final_correct,
            'final_lean_decision': final_lean,
            'lean_correct': lean_correct})
        print(f"  fast={qd}@{qc} hammer={hd}@{hc} gt={gt} "
              f"item_exp={item_expected} mismatch={gt_mismatch} "
              f"esc={escalated} esc_lean={escalated_lean} "
              f"final_ok={final_correct} lean_ok={lean_correct}",
              flush=True)

    with open(os.path.join(TEST_DIR, 'jev-decisions-hard.json'), 'w') as f:
        json.dump(rows, f, indent=2)

    n = len(rows)
    fast_acc = sum(1 for r in rows if r['fast_correct']) / n
    hammer_acc = sum(1 for r in rows if r['hammer_correct']) / n
    final_acc = sum(1 for r in rows if r['correct']) / n
    lean_acc = sum(1 for r in rows if r['lean_correct']) / n
    improvement = (final_acc - fast_acc) * 100
    lean_improvement = (lean_acc - fast_acc) * 100
    esc = [r for r in rows if r['escalated']]
    esc_rate = len(esc) / n
    esc_lean = [r for r in rows if r['escalated_lean']]
    esc_lean_rate = len(esc_lean) / n
    esc_fast_acc = (sum(1 for r in esc if r['fast_correct']) / len(esc)
                    if esc else None)
    esc_lean_fast_acc = (sum(1 for r in esc_lean if r['fast_correct'])
                         / len(esc_lean) if esc_lean else None)
    agree = sum(1 for r in rows
                if r['fast_decision'] is not None
                and r['fast_decision'] == r['hammer_decision']) / n
    # Correction path: fast answered WRONG, escalation fixed it.
    full_corr = [r['decision_id'] for r in rows
                 if r['fast_decision'] is not None
                 and not r['fast_correct'] and r['escalated']
                 and r['correct']]
    lean_corr = [r['decision_id'] for r in rows
                 if r['fast_decision'] is not None
                 and not r['fast_correct'] and r['escalated_lean']
                 and r['lean_correct']]
    # Wrong confident answers corrected by NEITHER rule (hammer
    # agreed, confidence >= 0.8, answered).
    neither_corr = [r['decision_id'] for r in rows
                    if r['fast_decision'] is not None
                    and not r['fast_correct']
                    and not r['escalated'] and not r['escalated_lean']]
    # Escalation anatomy (full rule).
    n_null = sum(1 for r in rows if r['fast_decision'] is None)
    n_conf = sum(1 for r in rows
                 if r['fast_decision'] is not None
                 and r['fast_confidence'] is not None
                 and r['fast_confidence'] < 0.8)
    n_dis = sum(1 for r in rows
                if r['fast_decision'] is not None
                and r['hammer_decision'] is not None
                and r['hammer_decision'] != r['fast_decision'])
    # Confidence distribution (quicklook, answered only).
    confs = [r['fast_confidence'] for r in rows
             if r['fast_confidence'] is not None]
    conf_dist = {
        '<0.5': sum(1 for c in confs if c < 0.5),
        '0.5-0.6': sum(1 for c in confs if 0.5 <= c < 0.6),
        '0.6-0.7': sum(1 for c in confs if 0.6 <= c < 0.7),
        '0.7-0.8': sum(1 for c in confs if 0.7 <= c < 0.8),
        '0.8-0.9': sum(1 for c in confs if 0.8 <= c < 0.9),
        '0.9-1.0': sum(1 for c in confs if 0.9 <= c <= 1.0),
        'null': n - len(confs),
    }
    conf_lt_095 = sum(1 for c in confs if c < 0.95)

    def rate(pred):
        return sum(1 for r in rows if pred(r)) / n

    tables = bucket_tables(rows)
    comb = tables['combined'][:5]
    seq = [(t['bucket'], t['rate']) for t in comb if t['k'] > 0]
    monotone = all(seq[i][1] <= seq[i + 1][1] + 1e-9
                   for i in range(len(seq) - 1))
    top = tables['combined'][4]

    summary = {
        'n': n,
        'fast_alone_accuracy_quicklook': fast_acc,
        'hammer_standalone_accuracy': hammer_acc,
        'escalated_accuracy_full': final_acc,
        'escalation_improvement_pp_full': improvement,
        'escalation_rate_full': esc_rate,
        'escalated_subset_fast_accuracy_full': esc_fast_acc,
        'escalated_accuracy_lean': lean_acc,
        'escalation_improvement_pp_lean': lean_improvement,
        'escalation_rate_lean': esc_lean_rate,
        'escalated_subset_fast_accuracy_lean': esc_lean_fast_acc,
        'agreement_rate_quicklook_hammer': agree,
        'escalation_anatomy_full': {
            'null_fast': n_null, 'confidence_lt_0.8': n_conf,
            'disagreement': n_dis, 'total_escalated': len(esc)},
        'correction_full_ids': full_corr,
        'correction_lean_ids': lean_corr,
        'corrected_by_neither_ids': neither_corr,
        'confidence_distribution_quicklook': conf_dist,
        'confidence_lt_0.95_count': conf_lt_095,
        'quicklook_prose_rate': rate(lambda r: r['fast_prose']),
        'quicklook_think_rate': rate(lambda r: r['fast_think']),
        'quicklook_empty_rate': rate(lambda r: r['fast_empty']),
        'quicklook_contract_failure_rate':
            rate(lambda r: not r['fast_contract_ok']),
        'quicklook_bare_word_rate': rate(lambda r: r['fast_bare_word']),
        'hammer_prose_rate': rate(lambda r: r['hammer_prose']),
        'hammer_think_rate': rate(lambda r: r['hammer_think']),
        'hammer_empty_rate': rate(lambda r: r['hammer_empty']),
        'hammer_contract_failure_rate':
            rate(lambda r: not r['hammer_contract_ok']),
        'hammer_bare_word_rate': rate(lambda r: r['hammer_bare_word']),
        'buckets': tables,
        'bucket_sequence_nonempty': seq,
        'monotone': monotone,
        'top_bucket': top,
        'gt_mismatches': [r['decision_id'] for r in rows
                          if r['gt_mismatch']],
        'ceiling_max_improvement_pp': (1.0 - fast_acc) * 100,
    }
    with open(os.path.join(TEST_DIR, 'jev-summary-hard.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print('DONE')


if __name__ == '__main__':
    main()
