#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path

from receipt_verifier import find_receipt


CLAIM_SCOPE = "transport-presence-only"


def build_transport_artifact(payload, did, nonce, text, uri):
    """Build a deterministic room-receipt artifact and its TCR-1 descriptor.

    The artifact proves only that an exact DID/nonce/text tuple appeared in the
    supplied room payload. It does not establish authorship, task acceptance,
    contribution truth, payment, or eligibility.
    """
    receipt = find_receipt(payload, did, nonce, text)
    document = {
        "claim_scope": CLAIM_SCOPE,
        "receipt": receipt,
        "type": "technocore-room-receipt",
        "version": 1,
    }
    encoded = (
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
        + b"\n"
    )
    descriptor = {
        "type": "technocore-room-receipt",
        "uri": uri,
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "size": len(encoded),
    }
    return encoded, descriptor


def write_transport_artifact(target, payload, did, nonce, text):
    """Exclusively create a canonical artifact; never overwrite existing evidence."""
    path = Path(target)
    encoded, descriptor = build_transport_artifact(
        payload, did, nonce, text, f"file:{path.name}"
    )
    with path.open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    return descriptor


def main():
    parser = argparse.ArgumentParser(
        description="Export a canonical Technocore room receipt as a TCR-1 artifact"
    )
    parser.add_argument("room_json")
    parser.add_argument("--did", required=True)
    parser.add_argument("--nonce", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = json.loads(Path(args.room_json).read_text(encoding="utf-8"))
    descriptor = write_transport_artifact(
        args.output, payload, args.did, args.nonce, args.text
    )
    print(json.dumps(descriptor, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
