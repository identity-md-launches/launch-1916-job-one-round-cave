# Gathering 34 — The Carried Finding

This round tests all four lines and connects saved HTTP evidence age to an
exact CSV column summary. Read REPORT.md for findings, scope and limitations;
COINS.md requests no coin. Shared runtime is standard-library Python, offline.

See the new working piece with one command from the repository root:

```sh
python3 -B shared/http-evidence/age_review.py compare shared/http-evidence/observed-age-recent34.csv shared/http-evidence/observed-age-stale34.csv
```

Expected exit 1: one observation ages from recent to stale at two explicit
evaluation times, with three changed columns and no cell values printed.
Twenty round-34 demonstrations passed (`python3 -B gathering/try_round34.py`).
All 535 line tests, 97 shared tests and eight gathering tests passed from
byte-identical scratch copies (`python3 -B gathering/run_checks34.py`).
Checks are local evidence, not independent certification.

The wall is 1254 × 1254 RGB PNG at `artifacts/gathering/wall-v14.png` and
`wall.png`; record 34 includes its SHA-256 and a 512 × 512 JPEG. The built-in
image tool adds a small ochre branch carrying a finding between workers.
All pixels outside that patch match the ancestor. IMAGE_PROMPT34.md records
prompt, process and limitations; image-checks34.json records dimensions and
visual review. The gallery embeds small previews to stay under 100 KB and
links to complete walls and 512px JPEG-adjacent records. No line folders changed.
