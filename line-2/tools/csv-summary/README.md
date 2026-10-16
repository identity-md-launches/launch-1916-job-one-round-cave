# CSV Change Summary

Summarize a fresh exact keyed CSV comparison without printing data-cell values,
including key values. This Python 3.9+ standard-library tool helps a worker see
which columns account for changes before opening a full reconciliation report.
Run from the repository root and retain the sibling `csv-reconcile/` tool.

One command shows it working with the existing inventory fixtures:

```sh
python3 -B line-2/tools/csv-summary/summary.py line-2/tools/csv-gate/demo-before.csv line-2/tools/csv-gate/demo-after.csv --key item
```

When tried, it exited **1** (differences found), reporting one added row, one
changed row, one unchanged row, and one changed cell in `quantity`. It printed
no item names, quantities, owners or input paths. The comparison is complete
but unequal. An equal comparison exits **0**; invalid input exits **2**, with
no partial stdout and a generic error on stderr.

Repeat `--key` for composite keys. Values are exact strings: `01` differs from
`1`, and whitespace is meaningful. Row/header order alone makes no difference.
The report includes:

- Global `equal` and `complete` verdicts and row totals from CSV Reconcile.
- Schema additions/removals, including schema-only differences.
- Changed common non-key columns, sorted by changed-row count descending, then
  literal column name. Each row contributes at most once per column. Their sum
  is `changed_cells_on_common_columns`; one row can contribute several cells.
- Counts of all records left unpaired on each side because either side has
  duplicate keys. These records are excluded from added/removed/changed counts,
  even if the duplicate rows are identical or absent on the opposite side.

Added/removed rows do not contribute cell changes. Added/removed columns are
schema changes, not common-column edits. Therefore zero changed cells does
**not** establish equality or completeness. Key edits appear as removal and
addition. Empty keys retain the engine's literal-string semantics; choose keys
whose meaning suits the dataset. There is no guessing, normalization or ignore
option. Use CSV Reconcile or CSV Review Slice when individual records matter.

The report deliberately omits cell values, record numbers and input paths, but
it exposes header names, key-column names, counts and schema. It is **not an
anonymization or privacy guarantee**. Keep sensitive information out of headers
if sharing reports. Parser/I/O errors are generic to avoid echoing filenames
or malformed cell contents; argparse's usage errors can echo supplied options.

The engine admits workspace-local UTF-8 CSVs with unique nonempty headers,
consistent record width, at most 16 MiB and 100,000 records per file. Both
files and the full detailed comparison are held in memory before aggregation;
compact output does not reduce peak comparison memory. Keep inputs stable:
the reads do not form an atomic snapshot. No file is changed, no dependency
is installed, and no network, coin, wallet or payment is needed.

Checks:

```sh
python3 -B -m unittest discover -s line-2/tools/csv-summary -v
```

All **12 behavioral tests passed**, covering field counts/order, exact strings,
composite keys, row/header reordering, schema drift, additions/removals,
duplicate groups, empty inputs/keys, value omission and CLI exit/error behavior.
The unchanged engine's **17 tests passed** from a byte-identical scratch copy.
An offline self-comparison of the retained historical ZTO-first/IMD-second
six-row observation CSV was equal under `(chain_id, token_address, field)`;
using only `token_address` reported two ambiguous groups and six unpaired rows
on each side. Those observations are historical, not fresh chain evidence.
