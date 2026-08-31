#!/usr/bin/env python3
import argparse
import json
import unicodedata
from pathlib import Path

INVISIBLE = {"Cc", "Cf", "Cs", "Co", "Zl", "Zp"}


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


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
    nonce_text = str(nonce)
    if not nonce_text.isascii() or not nonce_text.isdigit() or not 1 <= len(nonce_text) <= 19:
        raise ValueError("nonce must be 1-19 ASCII digits")
    expected_nonce = int(nonce_text)
    same_nonce = [m for m in messages if isinstance(m, dict)
                  and m.get("from") == did
                  and (str(m.get("nonce")) == str(expected_nonce)
                       or m.get("nonce") == expected_nonce)]
    for message in same_nonce:
        if type(message.get("nonce")) is not int:
            raise ValueError("receipt nonce must be an integer")
        if type(message.get("seq")) is not int or message["seq"] <= 0:
            raise ValueError("receipt sequence must be a positive integer")
    if len(same_nonce) > 1:
        raise ValueError("room payload contains duplicate DID and nonce records")
    matches = [m for m in same_nonce if m.get("text") == clean
               and isinstance(m.get("seq"), int)]
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
    payload = json.loads(
        Path(args.room_json).read_text(), object_pairs_hook=reject_duplicate_keys
    )
    print(json.dumps(find_receipt(payload, args.did, args.nonce, args.text), sort_keys=True))


if __name__ == "__main__":
    main()
