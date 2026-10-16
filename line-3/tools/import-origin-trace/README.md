# Import Origin Trace

Trace explicit local `from module import name` statements through module-scope
re-exports to the source definition, without importing or executing project
code. This adds symbol-level provenance to the inherited module map. It uses
only the Python standard library and the delivered Import Budget and Import Map
tools; it works offline on Python 3.9 or newer.

From the repository root, run this working example:

```sh
python3 -B line-3/tools/import-origin-trace/origins.py line-3/tools/import-origin-trace/examples
```

The example follows `app.launch` through `facade.run` to the definition in
`implementation.py`, reports the direct path, and keeps a wildcard import
explicitly unresolved. JSON output includes the bounded source-byte manifest,
map issues and graph cycles. `--strict` exits 1 if a trace is unresolved,
ambiguous or cyclic, or if the inherited mapper reported a warning. Input
budgets are inherited from Import Budget and can be changed with its
`--max-files`, `--max-file-bytes`, `--max-total-bytes`, `--max-entries` and
`--max-depth` options.

```sh
python3 -B -m unittest discover -s line-3/tools/import-origin-trace -v
```

## What happened when tried

The example command and six local tests passed. The observed source was parsed
as bytes and never executed. It yielded one transitive alias path ending at
`implementation.run`, one direct definition path, and one wildcard limitation.
No packages were installed. A source-only trial on `shared/import-drift` completed
for 27 modules and 30 `from`-import names: four local names resolved and 26
nonlocal names stayed unresolved. Strict mode returned 1 for those explicit
unresolved results; they were not guessed as project definitions.

## Limits

Only imports and definitions directly in a module body are followed. Conditional
and nested re-exports, wildcard expansion, dynamic loading, runtime rebinding,
`__getattr__`, plugin hooks and execution order are not inferred. Repeated
module-scope definitions are reported as ambiguous. A resolved origin is static
source evidence, not proof that Python will bind or execute it at runtime.
