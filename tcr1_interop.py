#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from receipt_verifier import find_receipt, reject_duplicate_keys, sweep


CLAIM_SCOPE = "transport-presence-only"
BASE58BTC_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE64URL_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def _did_public_key(did):
    if not isinstance(did, str) or len(did) != 56 or not did.startswith("did:key:z6Mk"):
        raise ValueError("DID must be a canonical Ed25519 did:key")
    number = 0
    for character in did[9:]:
        if character not in BASE58BTC_ALPHABET:
            raise ValueError("DID must use canonical base58btc")
        number = number * 58 + BASE58BTC_ALPHABET.index(character)
    decoded = number.to_bytes((number.bit_length() + 7) // 8, "big")
    if len(decoded) != 34 or not decoded.startswith(b"\xed\x01"):
        raise ValueError("DID must contain an Ed25519 public key")
    return decoded[2:]


def verify_signed_artifact(document):
    """Verify the signed tuple embedded in a signed room-receipt artifact."""
    if (
        not isinstance(document, dict)
        or set(document) != {"claim_scope", "receipt", "signed_transport", "type", "version"}
        or document["claim_scope"] != "cryptographically-verified-signed-transport"
        or document["type"] != "technocore-signed-room-receipt"
        or type(document["version"]) is not int
        or document["version"] != 1
        or not isinstance(document["receipt"], dict)
        or not isinstance(document["signed_transport"], dict)
    ):
        raise ValueError("signed artifact has invalid schema")
    receipt = document["receipt"]
    transport = document["signed_transport"]
    nonce = receipt.get("nonce")
    text = receipt.get("text")
    signature = transport.get("signature")
    snapshot_sha256 = transport.get("snapshot_sha256")
    if (
        set(receipt) != {"did", "nonce", "sequence", "text"}
        or set(transport) != {"did", "nonce", "room", "signature", "snapshot_sha256"}
        or not isinstance(receipt["did"], str)
        or not isinstance(nonce, str)
        or not nonce.isascii()
        or not nonce.isdigit()
        or not 1 <= len(nonce) <= 19
        or type(receipt["sequence"]) is not int
        or receipt["sequence"] <= 0
        or not isinstance(text, str)
        or sweep(text) != text
        or transport["did"] != receipt["did"]
        or transport["nonce"] != nonce
        or not isinstance(transport["room"], str)
        or not transport["room"]
        or not isinstance(signature, str)
        or len(signature) != 86
        or any(character not in BASE64URL_ALPHABET for character in signature)
        or not isinstance(snapshot_sha256, str)
        or len(snapshot_sha256) != 64
        or any(character not in "0123456789abcdef" for character in snapshot_sha256)
    ):
        raise ValueError("signed artifact has invalid schema")
    try:
        did = transport["did"]
        room = transport["room"]
        raw_signature = base64.b64decode(signature + "==", altchars=b"-_", validate=True)
        Ed25519PublicKey.from_public_bytes(_did_public_key(did)).verify(
            raw_signature, f"{room}|{nonce}|{receipt['text']}".encode("utf-8")
        )
    except Exception as error:
        raise ValueError("signed artifact signature does not verify") from error


def build_signed_transport_artifact(snapshot, room, did, signature, nonce, text, uri):
    """Verify and export an official Technocore say-signed transport tuple."""
    payload = json.loads(snapshot, object_pairs_hook=reject_duplicate_keys)
    receipt = find_receipt(payload, did, nonce, text)
    try:
        if (
            not isinstance(signature, str)
            or len(signature) != 86
            or any(character not in BASE64URL_ALPHABET for character in signature)
        ):
            raise ValueError("signature must be 86 unpadded base64url characters")
        raw_signature = base64.b64decode(signature + "==", altchars=b"-_", validate=True)
        Ed25519PublicKey.from_public_bytes(_did_public_key(did)).verify(
            raw_signature, f"{room}|{nonce}|{receipt['text']}".encode("utf-8")
        )
    except Exception as error:
        raise ValueError("signature does not verify official room canonical string") from error
    document = {
        "claim_scope": "cryptographically-verified-signed-transport",
        "receipt": receipt,
        "signed_transport": {
            "did": did,
            "nonce": str(nonce),
            "room": room,
            "signature": signature,
            "snapshot_sha256": hashlib.sha256(snapshot).hexdigest(),
        },
        "type": "technocore-signed-room-receipt",
        "version": 1,
    }
    encoded = json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8") + b"\n"
    descriptor = {
        "type": document["type"],
        "uri": uri,
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "size": len(encoded),
    }
    return encoded, descriptor


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


def write_signed_transport_artifact(target, snapshot, room, did, signature, nonce, text):
    path = Path(target)
    encoded, descriptor = build_signed_transport_artifact(
        snapshot, room, did, signature, nonce, text, f"file:{path.name}"
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
    parser.add_argument("--room")
    parser.add_argument("--signature")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    snapshot = Path(args.room_json).read_bytes()
    if (args.room is None) != (args.signature is None):
        parser.error("--room and --signature must be supplied together")
    if args.room is not None:
        descriptor = write_signed_transport_artifact(
            args.output, snapshot, args.room, args.did, args.signature, args.nonce, args.text
        )
    else:
        payload = json.loads(snapshot, object_pairs_hook=reject_duplicate_keys)
        descriptor = write_transport_artifact(
            args.output, payload, args.did, args.nonce, args.text
        )
    print(json.dumps(descriptor, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
