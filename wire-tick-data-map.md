# Wire tick data map — read-only probes, 2026-10-31

Source of truth: `wire.py` on mrfloppy (`~/llm/wire-experiment/wire.py`), live process arguments, and sampled tick files. No file was modified; no service was restarted.

## Modes and processes (live, 2026-10-31)

| Port | Mode | Tick Hz | Tick log every | Runs dir |
|---|---|---|---|---|
| 17780 | dual | 40 | 10 (sampled 1-in-10) | `runs/bit-dual/` |
| 17778 | dual | 40 | 10 (sampled 1-in-10) | `runs/bit-asym/` |
| 17779 | shared | 4 | 1 (default: every tick) | `runs/bit-shared/` |
| 17777 | byte-stream | — | — | `runs/` (dir/len/hex records, NOT tick data) |

## Tick record format (shared mode)

Broadcast to observers at full fidelity every tick; written to disk as JSON
(`write_json`) every `--tick-log-every` ticks, plus per-minute `agg` records.

```json
{"ts": 1793404800.0086942, "tick": 1373525, "a": 1, "b": 1, "wire": 1,
 "mode": "shared", "a_conn": true, "b_conn": true}
```

- `a` = agent A's bit that tick; `b` = agent B's bit; `wire = a | b` (shared-OR).
- Dual mode records have the same shape MINUS `wire` (each agent receives the
  peer's bit directly; `a`/`b` are still the sent bits).
- `agg` records (`{"type": "agg", "ticks", "tick_hz_est", "a_rate", "b_rate",
  "coincidence"}`) are per-minute summaries and are NEVER tick rows.

## File layout

- Shared-mode tick files: `runs/bit-shared/YYYYMMDDT000000Z.jsonl`, daily,
  ~33–42 MB, ~260k–430k tick rows per file.
- Tick numbers are CONSECUTIVE within a file (verified: all successive diffs = 1
  in the sampled file, 273,215 tick rows). The counter RESETS on process restart:
  tick numbers in a later-dated file can be LOWER than in an earlier file.
  Rule: one file = one sequence. Never concatenate files by tick number; count
  APs within one file only, with segment boundaries explicit.
- Dual-mode files are SAMPLED (1-in-10 ticks): tick numbers are NOT consecutive.
  They are excluded from any density/AP analysis that assumes a complete
  sequence, unless the gaps are handled explicitly (they are not, in this map).
- Byte-stream files in `runs/*.jsonl` (`dir`/`len`/`hex`) contain no tick data.
- Observer files (`*.observer.jsonl`) contain `pred` records
  (`ts`, `type: pred`, `dir`, `len`, `correct`, `accuracy`, `bytes_seen`) — model
  prediction telemetry, NOT tick bits. This was the format sampled in the first
  A2 probe and is why the tick-bit object was initially unidentified.

## Measured regimes (full-file rates, read-only)

| File (bit-shared) | Tick rows | Tick range | a rate | b rate | wire rate | Usability |
|---|---|---|---|---|---|---|
| 20261005T000000Z | 294,541 | 332,750–627,290 | 0.9898 | 1.0000 | 1.0000 | SATURATED — excluded |
| 20261007T000000Z | 434,014 | 2,441,528–2,875,541 | 0.4028 | 0.7593 | 0.8527 | Informative densities — candidate |
| 20261025T000000Z | 262,856 | 895,007–1,157,862 | 0.5013 | 0.0000 | 0.5013 | Peer silent — special case only |
| 20261031T000000Z | 273,215 | 1,373,525–1,646,739 | 0.9903 | 1.0000 | 1.0000 | SATURATED — excluded |

Saturation rule (pre-registered in the AP protocol): a sequence with density
outside (0.2, 0.8) is excluded from the AP trial — at density 1.0 every triple
is a progression and the count carries no information; at density 0.99 the same
degeneracy nearly holds.

## Extraction recipe (for the Kelley–Meka trial)

1. Read one shared-mode file; keep rows with a `tick` field; drop `agg` rows.
2. Assert tick numbers are consecutive over the chosen window (diff == 1).
3. Emission sequences, in the file's own terms: `A_t = a`, `B_t = b`,
   `W_t = wire`. Which agent is the "drive" is NOT asserted by this map — the
   Oct 6 dependence analysis (E-W1) conditioned on "drive emits 1 | peer
   silent"; the drive/peer identity must be pinned from the run's launch
   record before any claim names a side. The trial counts APs in `A` and in
   `W` as stated in the protocol, without naming a side "drive".
4. APs are counted within the window only; window and sequence are fixed in
   the protocol before counting.

## What this map does NOT claim

- No claim about which side is the drive agent in any run.
- No claim that the Oct 7 file is the E-W1 population (Oct 6 file is missing
  from bit-shared/; the 72h/E-W1 analysis may span files or use observer
  broadcasts). The AP trial population is chosen by the protocol's stated
  density/continuity rule, not by assumed identity with E-W1.
- No AP count is reported in this map. Counts live only in the trial results
  produced under the AP protocol.
