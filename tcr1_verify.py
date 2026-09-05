#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

from receipt_verifier import reject_duplicate_keys, sweep
from tcr1_interop import verify_signed_artifact


DESCRIPTOR_TYPES = {
    "technocore-room-receipt",
    "technocore-signed-room-receipt",
}


def validate_descriptor_schema(descriptor):
    if (
        not isinstance(descriptor, dict)
        or set(descriptor) != {"sha256", "size", "type", "uri"}
        or not isinstance(descriptor["type"], str)
        or descriptor["type"] not in DESCRIPTOR_TYPES
        or not isinstance(descriptor["uri"], str)
        or not descriptor["uri"]
        or not isinstance(descriptor["sha256"], str)
        or len(descriptor["sha256"]) != 64
        or any(character not in "0123456789abcdef" for character in descriptor["sha256"])
    ):
        raise ValueError("descriptor has invalid schema")


def verify_unsigned_artifact(document):
    if (
        set(document) != {"claim_scope", "receipt", "type", "version"}
        or document["claim_scope"] != "transport-presence-only"
        or document["type"] != "technocore-room-receipt"
        or type(document["version"]) is not int
        or document["version"] != 1
        or not isinstance(document["receipt"], dict)
    ):
        raise ValueError("unsigned artifact has invalid schema")
    receipt = document["receipt"]
    nonce = receipt.get("nonce")
    text = receipt.get("text")
    if (
        set(receipt) != {"did", "nonce", "sequence", "text"}
        or not isinstance(receipt["did"], str)
        or not receipt["did"]
        or not isinstance(nonce, str)
        or not nonce.isascii()
        or not nonce.isdigit()
        or not 1 <= len(nonce) <= 19
        or type(receipt["sequence"]) is not int
        or receipt["sequence"] <= 0
        or not isinstance(text, str)
        or sweep(text) != text
    ):
        raise ValueError("unsigned artifact has invalid schema")


def main():
    parser = argparse.ArgumentParser(
        description="Verify a TCR-1 descriptor against a local artifact"
    )
    parser.add_argument("descriptor_json")
    parser.add_argument("artifact")
    args = parser.parse_args()
    descriptor = json.loads(
        Path(args.descriptor_json).read_bytes(), object_pairs_hook=reject_duplicate_keys
    )
    try:
        validate_descriptor_schema(descriptor)
    except (TypeError, ValueError) as error:
        parser.error(str(error))
    artifact_path = Path(args.artifact)
    artifact = artifact_path.read_bytes()
    if type(descriptor.get("size")) is not int or descriptor["size"] < 0:
        parser.error("descriptor has invalid size")
    if descriptor["uri"] != f"file:{artifact_path.name}":
        parser.error("descriptor URI does not name artifact")
    if len(artifact) != descriptor["size"]:
        parser.error("artifact size does not match descriptor")
    if hashlib.sha256(artifact).hexdigest() != descriptor["sha256"]:
        parser.error("artifact SHA-256 does not match descriptor")
    artifact_document = json.loads(artifact, object_pairs_hook=reject_duplicate_keys)
    if not isinstance(artifact_document, dict) or artifact_document.get("type") != descriptor["type"]:
        parser.error("artifact type does not match descriptor")
    if descriptor["type"] == "technocore-signed-room-receipt":
        try:
            verify_signed_artifact(artifact_document)
        except ValueError as error:
            parser.error(str(error))
    elif descriptor["type"] == "technocore-room-receipt":
        try:
            verify_unsigned_artifact(artifact_document)
        except ValueError as error:
            parser.error(str(error))
    print(json.dumps({
        "sha256": descriptor["sha256"],
        "size": descriptor["size"],
        "type": descriptor["type"],
        "verified": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
