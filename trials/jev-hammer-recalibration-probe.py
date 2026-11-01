#!/usr/bin/env python3
"""Item 5, step 2: READ-ONLY hammer probes (runs ON mrfloppy).

Hammer :8201 direct port only (never the router). Same payload as the
valid JEV lag run (jev-lag-run.py): model 'hammer', same system prompts,
same user-prompt construction, temp 0, max_tokens 4096, stream False,
chat_template_kwargs enable_thinking False, 1 retry on unparseable
output (retry success counts as ok -- the lag-run flag fix).

Logprobs: capability-checked first with ONE call carrying
logprobs:true + top_logprobs:5. If the response carries
choices[0].logprobs.content, all probe calls use the same params
(greedy sampling is unaffected by logprob reporting) and per-token
features are extracted. If the call errors or returns no logprobs,
logprobs are recorded as UNAVAILABLE and the probe runs plain --
never invented.

Items: the 100 lag items (jev-lag-items.json), prompts built exactly
as in jev-lag-run.py. GT = item 'expected' (== calculator GT in the
lag run, gt_mismatch 0/100). Fast seat NOT called here.

Outputs (~/jev-test/hammer-recalibration/):
  jev-hammer-recalibration-probe.json / .jsonl (rows, checkpointed),
  jev-hammer-recalibration-probe-done (marker).
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HAMMER = "http://127.0.0.1:8201/v1/chat/completions"
RUN_DIR = "/home/joshua/jev-test/hammer-recalibration"
ITEMS_FILE = "/home/joshua/jev-test/lag-run/jev-lag-items.json"
OUT_JSON = os.path.join(RUN_DIR, "jev-hammer-recalibration-probe.json")
OUT_JSONL = os.path.join(RUN_DIR, "jev-hammer-recalibration-probe.jsonl")
DONE_FILE = os.path.join(RUN_DIR, "jev-hammer-recalibration-probe-done")

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


def build_user(it):
    if it["type"] == "a":
        return (f"Function: {it['function']}\nSpec: {it['spec']}\n"
                f"OLD code:\n```python\n{it['old_code']}\n```\n"
                f"NEW code (after the change):\n```python\n{it['new_code']}\n```\n"
                f"Diff (OLD -> NEW):\n```diff\n{it['diff']}\n```\n"
                f"Tests (the NEW code must pass ALL of these):\n"
                f"```python\n{it['tests']}\n```\n"
                f"Decide: does the NEW code pass ALL the given "
                f"tests? Reply with JSON only.")
    return (f"Function: {it['function']}\nSpec: {it['spec']}\n"
            f"Implementation A:\n```python\n{it['impl_a']}\n```\n"
            f"Implementation B:\n```python\n{it['impl_b']}\n```\n"
            f"Which implementation better satisfies the spec? "
            f"Reply with JSON only.")


def call_seat(url, model, system, user, with_logprobs):
    body = {"model": model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": 0, "max_tokens": 4096, "stream": False,
            "chat_template_kwargs": {"enable_thinking": False}}
    if with_logprobs:
        body["logprobs"] = True
        body["top_logprobs"] = 5
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code}
    except Exception as e:
        return {"_error": str(e)}


def parse_decision(content, allowed):
    if content is None:
        return (None, None, False, False, False, False)
    think = "<think>" in content
    stripped = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
    stripped = re.sub(r"<think>.*$", "", stripped, flags=re.DOTALL)
    if not stripped.strip():
        return (None, None, False, think, True, False)
    m = re.search(r"\{[^{}]*\"decision\"[^{}]*\}", stripped, re.DOTALL)
    if not m:
        return (None, None, True, think, False, False)
    obj_text = m.group(0)
    outside = (stripped[:m.start()] + stripped[m.end():]).strip()
    prose = bool(outside)
    try:
        obj = json.loads(obj_text)
    except Exception:
        return (None, None, prose, think, False, False)
    dec = obj.get("decision")
    conf = obj.get("confidence")
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
    s = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    s = re.sub(r"<think>.*$", "", s, flags=re.DOTALL)
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    s = s.strip()
    return s in allowed and "{" not in s


def logprob_features(resp, content):
    """Extract per-token features from choices[0].logprobs.content."""
    try:
        entries = resp["choices"][0]["logprobs"]["content"]
    except Exception:
        return None
    if not entries:
        return None
    tokens = [e.get("token", "") for e in entries]
    lps = [e.get("logprob") for e in entries]
    if any(lp is None for lp in lps):
        return None
    recon = "".join(tokens)
    offsets = []
    pos = 0
    for t in tokens:
        offsets.append((pos, pos + len(t)))
        pos += len(t)

    def span_mean(pattern):
        m = re.search(pattern, recon)
        if not m:
            return None
        s, e = m.span(1)
        vals = [lps[i] for i, (a, b) in enumerate(offsets)
                if a < e and b > s]
        if not vals:
            return None
        return sum(vals) / len(vals)

    def span_margin(pattern):
        m = re.search(pattern, recon)
        if not m:
            return None
        s, e = m.span(1)
        margins = []
        for i, (a, b) in enumerate(offsets):
            if a < e and b > s:
                cands = entries[i].get("top_logprobs") or []
                probs = sorted((c.get("logprob") for c in cands
                                if c.get("logprob") is not None),
                               reverse=True)
                if len(probs) >= 2:
                    import math
                    margins.append(math.exp(probs[0]) - math.exp(probs[1]))
        return sum(margins) / len(margins) if margins else None

    import math
    top1 = [math.exp(lp) for lp in lps]
    return {
        "recon_matches_content": (recon == content),
        "n_tokens": len(tokens),
        "mean_logprob": sum(lps) / len(lps),
        "min_logprob": min(lps),
        "mean_top1_prob": sum(top1) / len(top1),
        "decision_logprob": span_mean(r'"decision"\s*:\s*"([^"]+)"'),
        "confidence_logprob": span_mean(r'"confidence"\s*:\s*([0-9]*\.?[0-9]+)'),
        "decision_margin": span_margin(r'"decision"\s*:\s*"([^"]+)"'),
    }


def ask(url, model, system, user, allowed, with_logprobs):
    t0 = time.monotonic()
    resp = call_seat(url, model, system, user, with_logprobs)
    content = None
    lp_feat = None
    n_tokens = None
    if isinstance(resp, dict) and "_http_error" not in resp and "_error" not in resp:
        try:
            content = resp["choices"][0]["message"]["content"]
        except Exception:
            content = None
        try:
            n_tokens = resp.get("usage", {}).get("completion_tokens")
        except Exception:
            n_tokens = None
        if with_logprobs:
            lp_feat = logprob_features(resp, content or "")
    dec, conf, prose, think, empty, ok = parse_decision(content, allowed)
    n_attempts = 1
    raw = content
    if not ok:
        resp2 = call_seat(url, model, system, user, with_logprobs)
        n_attempts = 2
        content2 = None
        lp_feat2 = None
        n_tokens2 = None
        if isinstance(resp2, dict) and "_http_error" not in resp2 and "_error" not in resp2:
            try:
                content2 = resp2["choices"][0]["message"]["content"]
            except Exception:
                content2 = None
            try:
                n_tokens2 = resp2.get("usage", {}).get("completion_tokens")
            except Exception:
                n_tokens2 = None
            if with_logprobs:
                lp_feat2 = logprob_features(resp2, content2 or "")
        dec2, conf2, prose2, think2, empty2, ok2 = parse_decision(content2, allowed)
        if ok2:
            dec, conf, prose, think, empty = dec2, conf2, prose2, think2, empty2
            ok = True
            raw = content2
            lp_feat = lp_feat2
            n_tokens = n_tokens2
        else:
            prose = prose or prose2
            think = think or think2
            empty = empty or empty2
            raw = content2 or content
    dur = time.monotonic() - t0
    return {
        "decision": dec, "confidence": conf, "prose": prose,
        "think": think, "empty": empty, "contract_ok": ok,
        "bare_word": is_bare_word(raw, allowed),
        "raw": (raw or "")[:1500], "raw_len": len(raw or ""),
        "duration_s": dur, "n_attempts": n_attempts,
        "completion_tokens": n_tokens, "logprob_features": lp_feat,
    }


def main():
    os.makedirs(RUN_DIR, exist_ok=True)
    with open(ITEMS_FILE) as f:
        items = json.load(f)["items"]
    # Capability check: ONE call with logprobs params.
    it0 = items[0]
    sys0 = SYS_A if it0["type"] == "a" else SYS_B
    allowed0 = ["pass", "fail"] if it0["type"] == "a" else ["A", "B"]
    probe = call_seat(HAMMER, "hammer", sys0, build_user(it0), True)
    logprobs_ok = False
    logprobs_reason = "unknown"
    if isinstance(probe, dict) and "_http_error" in probe:
        logprobs_reason = f"http_error_{probe['_http_error']}"
    elif isinstance(probe, dict) and "_error" in probe:
        logprobs_reason = f"error_{probe['_error']}"
    else:
        try:
            entries = probe["choices"][0]["logprobs"]["content"]
            if entries:
                logprobs_ok = True
                logprobs_reason = "logprobs.content present"
            else:
                logprobs_reason = "logprobs.content empty"
        except Exception:
            logprobs_reason = "no logprobs.content in response (param ignored)"
    print(f"logprobs supported: {logprobs_ok} ({logprobs_reason})", flush=True)

    rows = []
    done = set()
    if os.path.exists(OUT_JSONL):
        with open(OUT_JSONL) as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    rows.append(r)
                    done.add(r["problem_id"])
        print(f"resuming: {len(rows)} rows done", flush=True)

    for it in items:
        pid = it["problem_id"]
        if pid in done:
            continue
        allowed = ["pass", "fail"] if it["type"] == "a" else ["A", "B"]
        system = SYS_A if it["type"] == "a" else SYS_B
        res = ask(HAMMER, "hammer", system, build_user(it), allowed, logprobs_ok)
        gt = it["expected"]
        dec = res["decision"]
        row = {
            "problem_id": pid, "source": it["source"], "type": it["type"],
            "function": it["function"], "prompt_ref": it["prompt_ref"],
            "ground_truth": gt,
            "hammer_decision": dec, "hammer_confidence": res["confidence"],
            "hammer_prose": res["prose"], "hammer_think": res["think"],
            "hammer_empty": res["empty"],
            "hammer_contract_ok": res["contract_ok"],
            "hammer_bare_word": res["bare_word"],
            "hammer_raw": res["raw"], "hammer_raw_len": res["raw_len"],
            "hammer_duration_s": res["duration_s"],
            "hammer_n_attempts": res["n_attempts"],
            "hammer_completion_tokens": res["completion_tokens"],
            "hammer_logprob_features": res["logprob_features"],
            "hammer_correct": (dec == gt) if dec is not None else None,
            "logprobs_supported": logprobs_ok,
        }
        rows.append(row)
        with open(OUT_JSONL, "a") as f:
            f.write(json.dumps(row) + "\n")
        with open(OUT_JSON, "w") as f:
            json.dump({"logprobs_supported": logprobs_ok,
                       "logprobs_reason": logprobs_reason,
                       "rows": rows}, f, indent=2)
        print(f"  {pid} {it['type']} hammer={dec}@{res['confidence']} "
              f"correct={row['hammer_correct']} "
              f"({res['duration_s']:.2f}s, {res['n_attempts']} att)",
              flush=True)

    with open(DONE_FILE, "w") as f:
        f.write(f"done {len(rows)} rows logprobs={logprobs_ok}\n")
    print(f"DONE {len(rows)} rows logprobs={logprobs_ok}")


if __name__ == "__main__":
    main()
