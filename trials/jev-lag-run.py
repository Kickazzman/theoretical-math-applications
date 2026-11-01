#!/usr/bin/env python3
"""JEV lag run: 100 problems, fast (quicklook :8203) + hammer (:8201).

Runs ON mrfloppy. Same CONTRACT as the valid JEV runs (report
jev-contract-test-report.md, jev-hard-run-report.md): strict JSON
(typed decision + confidence 0-1, no prose), temp 0, 4096-token
budget, 1 retry on unparseable output, same parser, DIRECT ports
only (never the router), sequential, one call at a time. No seat
pauses, no frank, no browser.

NEW vs the JEV runners: latency logging. For EVERY problem and
EVERY seat this records answer, confidence, t_start and t_end
(wall-clock time.time() + monotonic time.monotonic()), per-seat
duration, and attempt count. Seats are called SEQUENTIALLY (fast
first, then hammer), so the end-time gap is NOT a parallel latency
gap: end_gap ~= hammer duration + inter-call gap. The interpretable
lag is the duration difference (hammer_duration - fast_duration);
the analysis reports both, never the end gap alone as if the seats
ran in parallel.

Ground truth: the CALCULATOR (local Python tests) per item --
(a) tests on new_code, (b) embedded tests on both impls. Never a
seat's answer. Items file is self-contained (prompts + tests).

Checkpointing: after EVERY problem the row is appended to
jev-lag-decisions.jsonl and the full jev-lag-decisions.json is
rewritten. Resume: problems already in the checkpoint are skipped
(by problem_id), so an interrupted run loses nothing. Env
LAG_LIMIT=N runs only the first N problems (smoke test).

Outputs (~/jev-test/lag-run/): jev-lag-decisions.json (100 rows),
jev-lag-decisions.jsonl (checkpoint), jev-lag-run.log,
jev-lag-done (marker written at clean completion).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import urllib.request

QUICKLOOK = 'http://127.0.0.1:8203/v1/chat/completions'
HAMMER = 'http://127.0.0.1:8201/v1/chat/completions'
RUN_DIR = '/home/joshua/jev-test/lag-run'
ITEMS_FILE = os.path.join(RUN_DIR, 'jev-lag-items.json')
OUT_JSON = os.path.join(RUN_DIR, 'jev-lag-decisions.json')
OUT_JSONL = os.path.join(RUN_DIR, 'jev-lag-decisions.jsonl')
DONE_FILE = os.path.join(RUN_DIR, 'jev-lag-done')

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
    import sys, json
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
    d = tempfile.mkdtemp(prefix='jev-lag-run-')
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
    if raw is None:
        return False
    s = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
    s = re.sub(r'<think>.*$', '', s, flags=re.DOTALL)
    s = s.strip()
    s = re.sub(r'^```[a-zA-Z]*\s*', '', s)
    s = re.sub(r'\s*```$', '', s)
    s = s.strip()
    return s in allowed and '{' not in s


def ask_timed(url, model, system, user, allowed):
    """Call with 1 retry on unparseable output, timed. Returns dict
    with decision/confidence/flags + t_start/t_end (wall + mono),
    duration_s (mono), n_attempts. t_start is the FIRST attempt's
    start; t_end is the LAST attempt's end (total seat latency
    including any retry)."""
    t_start_wall = time.time()
    t_start_mono = time.monotonic()
    raw = call_seat(url, model, system, user)
    dec, conf, prose, think, empty, ok = parse_decision(raw, allowed)
    n_attempts = 1
    if not ok:
        raw2 = call_seat(url, model, system, user)
        n_attempts = 2
        dec2, conf2, prose2, think2, empty2, ok2 = parse_decision(
            raw2, allowed)
        if ok2:
            dec, conf, prose, think, empty = dec2, conf2, prose2, think2, empty2
            ok = True
            raw = raw2
        else:
            prose = prose or prose2
            think = think or think2
            empty = empty or empty2
            raw = raw2 or raw
    t_end_wall = time.time()
    t_end_mono = time.monotonic()
    return {
        'decision': dec, 'confidence': conf, 'prose': prose,
        'think': think, 'empty': empty, 'contract_ok': ok,
        'bare_word': is_bare_word(raw, allowed),
        'raw': (raw or '')[:1500],
        't_start_wall': t_start_wall, 't_end_wall': t_end_wall,
        't_start_mono': t_start_mono, 't_end_mono': t_end_mono,
        'duration_s': t_end_mono - t_start_mono,
        'n_attempts': n_attempts,
    }


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


def main():
    os.makedirs(RUN_DIR, exist_ok=True)
    with open(ITEMS_FILE) as f:
        items = json.load(f)['items']
    limit = os.environ.get('LAG_LIMIT')
    if limit:
        items = items[:int(limit)]
    print(f'lag run: {len(items)} problems (limit={limit})', flush=True)

    # Resume: load existing checkpoint rows.
    rows = []
    done_ids = set()
    if os.path.exists(OUT_JSONL):
        with open(OUT_JSONL) as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    rows.append(r)
                    done_ids.add(r['problem_id'])
        print(f'resuming: {len(rows)} rows already done', flush=True)

    for it in items:
        pid = it['problem_id']
        if pid in done_ids:
            continue
        print(f"{pid} {it['type']} {it['prompt_ref']} ...", flush=True)
        if it['type'] == 'a':
            user = (f"Function: {it['function']}\nSpec: {it['spec']}\n"
                    f"OLD code:\n```python\n{it['old_code']}\n```\n"
                    f"NEW code (after the change):\n```python\n{it['new_code']}\n```\n"
                    f"Diff (OLD -> NEW):\n```diff\n{it['diff']}\n```\n"
                    f"Tests (the NEW code must pass ALL of these):\n"
                    f"```python\n{it['tests']}\n```\n"
                    f"Decide: does the NEW code pass ALL the given "
                    f"tests? Reply with JSON only.")
            fast = ask_timed(QUICKLOOK, 'quicklook', SYS_A, user,
                             ['pass', 'fail'])
            hammer = ask_timed(HAMMER, 'hammer', SYS_A, user,
                               ['pass', 'fail'])
            ok_h, passes, _, _ = run_tests(it['new_code'], it['tests'])
            gt = 'pass' if (ok_h and passes) else ('fail' if ok_h else 'error')
        else:  # b
            user = (f"Function: {it['function']}\nSpec: {it['spec']}\n"
                    f"Implementation A:\n```python\n{it['impl_a']}\n```\n"
                    f"Implementation B:\n```python\n{it['impl_b']}\n```\n"
                    f"Which implementation better satisfies the spec? "
                    f"Reply with JSON only.")
            fast = ask_timed(QUICKLOOK, 'quicklook', SYS_B, user, ['A', 'B'])
            hammer = ask_timed(HAMMER, 'hammer', SYS_B, user, ['A', 'B'])
            ok_a, pass_a, _, _ = run_tests(it['impl_a'], it['tests'])
            ok_b, pass_b, _, _ = run_tests(it['impl_b'], it['tests'])
            if ok_a and ok_b and pass_a and not pass_b:
                gt = 'A'
            elif ok_a and ok_b and pass_b and not pass_a:
                gt = 'B'
            else:
                gt = 'ambiguous'

        fd, hd = fast['decision'], hammer['decision']
        fast_correct = (fd == gt) if fd is not None else False
        hammer_correct = (hd == gt) if hd is not None else False
        both_answered = (fd is not None and hd is not None)
        change_all = (fd != hd)  # None counts as a value
        change_both = (both_answered and fd != hd)
        agree = (both_answered and fd == hd)
        both_wrong = (both_answered and not fast_correct
                      and not hammer_correct)
        row = {
            'problem_id': pid, 'source': it['source'],
            'type': it['type'], 'function': it['function'],
            'prompt_ref': it['prompt_ref'],
            'ground_truth': gt, 'item_expected': it['expected'],
            'gt_mismatch': (gt != it['expected']),
            'fast_decision': fd, 'fast_confidence': fast['confidence'],
            'fast_prose': fast['prose'], 'fast_think': fast['think'],
            'fast_empty': fast['empty'],
            'fast_contract_ok': fast['contract_ok'],
            'fast_bare_word': fast['bare_word'],
            'fast_raw': fast['raw'],
            'fast_t_start_wall': fast['t_start_wall'],
            'fast_t_end_wall': fast['t_end_wall'],
            'fast_t_start_mono': fast['t_start_mono'],
            'fast_t_end_mono': fast['t_end_mono'],
            'fast_duration_s': fast['duration_s'],
            'fast_n_attempts': fast['n_attempts'],
            'hammer_decision': hd,
            'hammer_confidence': hammer['confidence'],
            'hammer_prose': hammer['prose'],
            'hammer_think': hammer['think'],
            'hammer_empty': hammer['empty'],
            'hammer_contract_ok': hammer['contract_ok'],
            'hammer_bare_word': hammer['bare_word'],
            'hammer_raw': hammer['raw'],
            'hammer_t_start_wall': hammer['t_start_wall'],
            'hammer_t_end_wall': hammer['t_end_wall'],
            'hammer_t_start_mono': hammer['t_start_mono'],
            'hammer_t_end_mono': hammer['t_end_mono'],
            'hammer_duration_s': hammer['duration_s'],
            'hammer_n_attempts': hammer['n_attempts'],
            # Derived gap/lag fields (sequential calls: see header).
            'duration_gap_s': hammer['duration_s'] - fast['duration_s'],
            'end_gap_s': hammer['t_end_wall'] - fast['t_end_wall'],
            'start_gap_s': hammer['t_start_wall'] - fast['t_start_wall'],
            'inter_call_gap_s': hammer['t_start_wall'] - fast['t_end_wall'],
            'fast_correct': fast_correct,
            'hammer_correct': hammer_correct,
            'both_answered': both_answered,
            'change_all': change_all,
            'change_both_answered': change_both,
            'agree': agree,
            'both_wrong': both_wrong,
        }
        rows.append(row)
        with open(OUT_JSONL, 'a') as f:
            f.write(json.dumps(row) + '\n')
        with open(OUT_JSON, 'w') as f:
            json.dump(rows, f, indent=2)
        print(f"  fast={fd}@{fast['confidence']} "
              f"({fast['duration_s']:.1f}s) "
              f"hammer={hd}@{hammer['confidence']} "
              f"({hammer['duration_s']:.1f}s) gt={gt} "
              f"change={change_both} both_wrong={both_wrong}",
              flush=True)

    with open(DONE_FILE, 'w') as f:
        f.write(f'done {len(rows)} rows\n')
    print(f'DONE {len(rows)} rows')


if __name__ == '__main__':
    main()
