#!/usr/bin/env python3
"""Offline ABI rehearsal: encode a static call and decode static return words."""
import argparse
import json
import re
import sys

WORD = 32
ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")


def word(value: int) -> bytes:
    if not 0 <= value < 1 << 256:
        raise ValueError("uint256 is out of range")
    return value.to_bytes(WORD, "big")


def encode_arg(typ: str, value: str) -> bytes:
    if typ == "uint256":
        return word(int(value, 0))
    if typ == "address":
        if not ADDRESS.fullmatch(value):
            raise ValueError("address must be a 20-byte 0x-prefixed value")
        return bytes(12) + bytes.fromhex(value[2:])
    if typ == "bool":
        if value.lower() not in {"true", "false"}:
            raise ValueError("bool must be true or false")
        return word(int(value.lower() == "true"))
    if typ == "bytes32":
        raw = bytes.fromhex(value[2:] if value.startswith("0x") else value)
        if len(raw) != WORD:
            raise ValueError("bytes32 must contain exactly 32 bytes")
        return raw
    raise ValueError(f"unsupported static ABI type: {typ}")


def encode_call(selector: str, types: list[str], values: list[str]) -> str:
    if not re.fullmatch(r"0x[0-9a-fA-F]{8}", selector):
        raise ValueError("selector must be four bytes, written as 0x followed by 8 hex digits")
    if len(types) != len(values):
        raise ValueError("types and values must have the same length")
    return "0x" + selector[2:].lower() + b"".join(encode_arg(t, v) for t, v in zip(types, values)).hex()


def decode_words(types: list[str], data: str) -> list[object]:
    if not re.fullmatch(r"0x[0-9a-fA-F]*", data) or len(data[2:]) % 64:
        raise ValueError("return data must be an even-length 0x-prefixed word sequence")
    raw = bytes.fromhex(data[2:])
    if len(raw) != WORD * len(types):
        raise ValueError("this rehearsal expects one 32-byte return word per type")
    values = []
    for index, typ in enumerate(types):
        chunk = raw[index * WORD : (index + 1) * WORD]
        if typ == "uint256":
            values.append(int.from_bytes(chunk, "big"))
        elif typ == "address":
            if any(chunk[:12]):
                raise ValueError("address word has non-zero high bytes")
            values.append("0x" + chunk[12:].hex())
        elif typ == "bool":
            if chunk not in (bytes(WORD), word(1)):
                raise ValueError("bool word must be 0 or 1")
            values.append(bool(chunk[-1]))
        elif typ == "bytes32":
            values.append("0x" + chunk.hex())
        else:
            raise ValueError(f"unsupported static ABI type: {typ}")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selector", required=True)
    parser.add_argument("--types", required=True, help="comma-separated static ABI types")
    parser.add_argument("--values", help="comma-separated call values")
    parser.add_argument("--decode", metavar="HEX", help="decode return words instead of encoding")
    args = parser.parse_args()
    types = [item.strip() for item in args.types.split(",") if item.strip()]
    try:
        if args.decode is not None:
            result = decode_words(types, args.decode)
        else:
            if args.values is None:
                raise ValueError("--values is required for encoding")
            result = encode_call(args.selector, types, [item.strip() for item in args.values.split(",")])
        print(json.dumps(result, separators=(",", ":")))
    except (ValueError, TypeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
