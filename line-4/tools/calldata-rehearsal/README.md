# Calldata Rehearsal

This is a dependency-free, offline rehearsal for the line's ABI goal. It builds
unsigned calldata from a caller-supplied four-byte selector and static ABI
arguments (`uint256`, `address`, `bool`, and `bytes32`), or strictly decodes
the matching static return words. It never reads a wallet, signs, sends, or
contacts a chain. The selector is supplied by the caller because this small
tool intentionally does not pretend to implement Keccak.

Try one encode/decode round trip from the repository root:

```sh
python3 line-4/tools/calldata-rehearsal/calldata_rehearsal.py --selector 0x70a08231 --types address --values 0x0000000000000000000000000000000000000001
python3 line-4/tools/calldata-rehearsal/calldata_rehearsal.py --selector 0x70a08231 --types uint256 --decode 0x000000000000000000000000000000000000000000000000000000000000002a
```

The first command prints the unsigned `balanceOf(address)` calldata, and the
second prints the decoded return value `42`.
