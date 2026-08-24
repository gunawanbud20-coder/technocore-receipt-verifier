#!/usr/bin/env python3
import argparse
import json
import unicodedata
from pathlib import Path

INVISIBLE = {"Cc", "Cf", "Cs", "Co", "Zl", "Zp"}


def sweep(text):
    clean = "".join(" " if unicodedata.category(c) in INVISIBLE else c for c in text).strip()
    if not clean:
        raise ValueError("nothing visible remains after sweep")
    return clean


def find_receipt(payload, did, nonce, text):
    messages = payload.get("messages") if isinstance(payload, dict) else None
    if not isinstance(messages, list):
        raise ValueError("room payload must contain a messages list")
    clean = sweep(text)
    matches = [m for m in messages if isinstance(m, dict)
               and m.get("from") == did and str(m.get("nonce")) == str(nonce)
               and m.get("text") == clean and isinstance(m.get("seq"), int)]
    if not matches:
        raise LookupError("receipt not found for exact DID, nonce, and swept text")
    match = max(matches, key=lambda m: m["seq"])
    return {"did": did, "nonce": str(nonce), "text": clean, "sequence": match["seq"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("room_json")
    p.add_argument("--did", required=True)
    p.add_argument("--nonce", required=True)
    p.add_argument("--text", required=True)
    args = p.parse_args()
    print(json.dumps(find_receipt(json.loads(Path(args.room_json).read_text()), args.did, args.nonce, args.text), sort_keys=True))


if __name__ == "__main__":
    main()
