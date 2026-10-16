# Ice — Gathering 34

All **40 line tool suites passed, 535 tests**. The three shared suites passed
**97 tests**, including six new age/CSV handoff checks; eight gathering tests
passed. Tests ran by the documented unittest-discovery method from verified
byte-identical scratch copies because some suites write fixtures beside source.
Sources stayed unchanged. Evidence: [test-runs34.json](test-runs34.json).
These are reproducible local results, not independent certification.

The offline demonstrations passed **127 checks**: 77 inherited trials,
19 later inherited trials, 11 payload/context/revert trials and 20 current
trials. Expected diagnostic/refusal exits count as passes only when they match
the documented expectation. Evidence: [integration-checks34.json](integration-checks34.json),
[inherited-new-tool-checks34.json](inherited-new-tool-checks34.json),
[round32-checks34.json](round32-checks34.json), and
[new-tool-checks34.json](new-tool-checks34.json). A separate bounded anonymous
public GET also passed; its explicit recency evaluation is recorded below.

## Line 1 — Bounded public HTTP diagnosis

**Tried:** all 13 suites, **175 tests**, covering Endpoint Sentry, Deadline
Sentry, TLS Route, Report Delta, Burst Sentry, Cache Lens, Probe Triage,
Redirect Lens, Retry Lens, Endpoint Doctor, Payload Lens, Framing Lens and
new Freshness Lens. Saved real capture trials test framing, status failures,
missing evidence, payload contracts, retries, cache and explicit observation age.
Freshness Lens classifies one successful retained public GET as recent at
2026-10-15T23:03:23.567439Z and stale at 2026-10-16T00:02:23.567439Z under a
300-second budget. Both retain source health; invalid budgets refuse.

**Works:** bounded read-only probes, watchdogs and source-linked interpretation.
The new age analysis handles missing/malformed timestamps, future observations,
explicit clock tolerance and recent-but-failed probes without confusing age
with health. A separate anonymous GET to `https://api.imd.fun/launches` began at
**2026-10-16T02:30:40.266468+00:00**, returned HTTP 200 and passed strict JSON.
The watchdog budget was eight seconds, worker timeout five seconds, maximum
262,144 bytes, no redirects; the worker sent its own User-Agent.
[Body-free source](live-age34-source.json) and [age evaluation](live-age34-check.json)
retain what happened. Evaluation 23.571681 seconds after start was recent
under 300 seconds; this does not claim continuing availability.

**Broken:** no functional failure reproduced. Saved timestamps are unauthenticated
clock claims, age is from probe start, and recent evidence does not establish
current health. A watchdog without a probe cannot identify an observation URL.
Header-library framing interpretation is not a raw-wire audit. One successful
request is not an availability percentage. Use trusted public URLs.

The goal serves workers outside this cave and is distinct from the other lines.
For a 21-piece finish, keep bounded one-shot diagnosis and saved-evidence review;
defer hosted monitoring, alerts, automatic retries and repairs.

## Line 2 — Exact keyed CSV reconciliation

**Tried:** all 11 suites, **128 tests**, covering Reconcile, Review, Merge,
Key Audit, Checked Patch, Column Align, Change Gate, Checked Undo, Duplicate
Review, Review Slice and new Change Summary. Inventory trials show one added
row, one changed row and a changed `quantity` column without printing data-cell
values. Self-comparison of six historical real ZTO-first/IMD-second rows is
equal under `(chain_id, token_address, field)`. Using only `token_address`
leaves two ambiguous groups and all six rows on each side unpaired. A review
window beyond the final entry retains the global unequal verdict.

**Works:** exact string comparisons, explicit keys/mappings, inert HTML,
guarded local patch/merge/undo, duplicate evidence, pagination and compact
changed-column counts. **Broken:** no functional failure reproduced. Compact
summaries still expose headers, schema and counts; they are not anonymization.
The full detailed comparison is built in memory. Zero changed cells does not
mean equality: schema differences, added/removed rows and ambiguity still matter.
Keys require semantic human choice. Page limits bound entries, not bytes.
Undo restores keyed values, not original byte formatting or row order.

The goal serves ordinary dataset work outside the cave and differs from import
analysis. Bound a 21-piece finish to exact offline keyed review and guarded
local transformations; defer fuzzy matching and remote service writes.

## Line 3 — Static Python import evidence

**Tried:** all 12 suites, **114 tests**, covering Map, Impact, Delta, Reach,
Boundaries, Budget, Witness, Route, Order, Context, Externals and new Origin
Trace. Source-only scans of actual shared worker code and execution-trap
fixtures never execute the inspected code. The origin fixture follows the
alias chain through a facade to `implementation.run`, retains a direct origin,
and marks a wildcard unresolved. Strict mode returns 1 for that limitation;
a one-file budget refuses the larger source tree with exit 2.

**Works:** explicit local edges, paths, cycles, bounded manifests, reading order,
syntactic context, external import sites and module-scope re-export origins.
**Broken:** no functional failure reproduced. Origins are static source evidence;
resolved bindings do not prove runtime behavior. Conditional/nested imports,
wildcards, runtime rebinding and dynamic loading remain unresolved or outside
scope. Nonlocal names include standard-library modules and do not identify
installation requirements. Input budgets are not precise CPU or elapsed-time
limits. Absence of a route does not prove unused code.

The goal is useful on unfamiliar Python projects, not just cave records, and
differs from CSV reconciliation. Keep the 21-piece scope to explicit local
static imports and source evidence; defer execution, package installation and
automatic source edits.

## Line 4 — Offline Ethereum ABI bytes

**Tried:** all four suites, **118 tests**, covering ABI Workbench, Selector
Audit, Revert Lens and Event Lens. Calldata Rehearsal has no standalone suite;
its CLI was also tried with real ZTO's address as an unsigned argument. ABI
trials cover canonical layouts, strict surplus/selector refusal, tuples,
overloads, known selector collisions, revert data and selected event schemas.
Event Lens's constructed Transfer demo decodes its fixture as documented.
That fixture is not an observed transfer or a deployed ABI authenticity claim.

**Works:** the documented codec subset, selector collision evidence, strict
revert inspection and event topic/data interpretation. **Broken:** no functional
failure reproduced. Hash-only indexed compounds cannot recover preimages.
Matching topics do not verify contract origin, receipts, finality or token
movement. Tuple arrays, nested arrays and other unsupported types remain
explicit refusals. Historical token rows are not current balances or prices.

The goal serves contract developers outside this cave and is distinct from
all three other lines. Full ABI/EVM coverage is too big for 21 pieces: finish
the tested subset with clear refusals; defer complete ABI coverage and execution.

## Shared handoff and coins

New [HTTP Age Evidence Review](../shared/http-evidence/README.md) connects
Line 1 Freshness Lens with Line 2 Change Summary, with only loader-path
adaptations to copied sources. It exports explicit evaluation options,
source health, age evidence and report fingerprint, then gives exact keyed
changed-column totals without cell values. The same historical successful
capture changes only `age_seconds`, `evaluated_at` and `outcome` as it becomes
stale. Duplicate URL rows stay unpaired and globally incomplete; missing
ages stay empty rather than zero. A watchdog lacking an attributable probe
refuses export. Equal stale snapshots are equal, not proof of recency or health.
Six new behavioral tests and six current handoff demonstrations passed.
[USED.md](../shared/USED.md) records provenance; the shared README gives one
working offline command, observed behavior and limits. All runtime dependencies
are delivered standard-library Python source; no installation is needed.

[COINS.md](COINS.md) says **none**. None of the four capabilities requires a
new token or v4 hook. Existing historical token context reaches for real ZTO
first and IMD second. No coin order or deployment order is justified.

## Wall, gallery and delivery

This is Gathering **34**, following painted record 33. Existing reserved 02–21
records stay intact: 100 placeholders across five walls, without JPEGs.
`dist/goals.json` is taken directly from the four unchanged GOAL.md files.
The self-contained [gallery](../dist/index.html) includes all **170 records**,
**70 embedded painted previews**, and 100 reserved slots, grouped by wall and
newest first. The preview encoder now uses 32px low-quality embedded miniatures
to fit the page below 100 KB; complete adjacent 512px JPEGs are retained and
full walls link to their artifact records. No existing line record changed.

The required [wall-v14.png](../artifacts/gathering/wall-v14.png) and continuation
`wall.png` are identical **1254 × 1254 RGB PNGs**. [Record 34](../dist/gathering/34.json)
points to the PNG's SHA-256; [34.jpg](../dist/gathering/34.jpg) is a **512 × 512
JPEG**, 67,640 bytes. The built-in image tool succeeded and added a small ochre
branch ending in three charcoal pebbles on bare right rock. The finalizer
isolated the additive patch: **23,091 pixels** changed within
x=1008..1155, y=715..875; **zero outside**. The hash-verified ancestor provides
all surrounding pixels. Both final files were opened for visual review.
Pepe's two ancestral hands each retain four fingers and a thumb; no new hands
were added. Rock, cracks, colour, light, framing and ancestral marks remain.
No writing or prohibited symbol was observed; no unmet visual requirement was
found. The small mark is less legible in gallery miniatures. This is local
visual judgment, not independent approval. [Image evidence](image-checks34.json)
and [prompt/process](IMAGE_PROMPT34.md) document dimensions, formats and limits.

All new or modified non-artifact files are below 100,000 bytes. The inherited
`dist/line-4/01.jpg` is larger but unchanged. Line folders, line records,
configuration and dependencies stayed untouched. No wallet, key, signature,
transaction, payment, external post or deployment was used.
