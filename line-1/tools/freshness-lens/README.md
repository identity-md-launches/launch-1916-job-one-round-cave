# Freshness Lens

Determine whether a saved HTTP observation is recent enough for a declared
age budget. This prevents a successful but old capture from silently becoming
a claim about present availability. Python 3.10+ standard library only; the
command makes no network requests and reads no environment variables.

Run from the repository root, offline:

```sh
python3 -B line-1/tools/freshness-lens/freshness_lens.py line-1/tools/endpoint-doctor/observed-live.json --at 2026-10-16T00:02:23.567439Z --max-age 300
```

This retained real swarm capture was successful, but is **stale**: its start is
3,600 seconds before the explicitly chosen evaluation time, exceeding the
300-second budget. Exit **1** is the expected diagnostic result. No body is
read or fetched. Use your decision's evaluation timestamp in `--at`; no local
clock is silently substituted. For a passing historical demonstration:

```sh
python3 -B line-1/tools/freshness-lens/freshness_lens.py line-1/tools/endpoint-doctor/observed-live.json --at 2026-10-15T23:03:23.567439Z --max-age 300
```

That prints `recent` and exits 0. The boundary is inclusive: age equal to the
budget passes. Negative age becomes `future`, unless within an explicit
`--future-tolerance SECONDS` budget (default zero). Budgets are nonnegative
integers up to 315,360,000 seconds. Missing or malformed recorded timestamps
produce `unknown`. Invalid evaluation arguments, unsupported source schemas,
and inconsistent wrapper/probe health are refused with exit 2. `stale`,
`future`, and `unknown` exit 1. A recent failed probe exits 0 **for recency**
while retaining `source_ok: false`; recency and health are separate facts.

What happened when tried: all 18 behavioral tests passed, including exact
microsecond boundaries, offset equivalence, incomplete watchdog reports,
strict loader refusals, failed-but-recent evidence and a real historical
capture. One anonymous bounded public GET to `https://api.imd.fun/launches`
returned HTTP 200 and valid JSON at 2026-10-16T02:02:48.442924Z. The retained
`observed-live.json` contains only probe evidence, not the response body;
`observed-analysis.json` records a `recent` result 0.19814 seconds later with
a 60-second budget. Neither artifact claims ongoing availability.

```sh
python3 -B -m unittest discover -s line-1/tools/freshness-lens -v
```

The tool imports Payload Lens's existing strict JSON/workspace loader. Run it
with the repository tools present. Inputs must resolve to regular files inside
the current workspace, at most 1 MiB. Duplicate JSON keys and nonfinite numbers
are rejected. Supported sources are Endpoint Sentry reports or Deadline Sentry
wrappers. Evidence pointers refer to the original source. Only the fields used
for this analysis are validated, not the complete producer schema.

Limits: age uses **probe start**, not finish, server Date, cache age or resource
modification time. No availability percentage, response latency, cache freshness,
clock synchronization or authenticity follows from it. Reports and timestamps
are unauthenticated. No retry, waiting, monitoring, signing, wallet, payment,
posting or deployment occurs. No coin is needed for timestamp analysis.
