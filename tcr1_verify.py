#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

from receipt_verifier import reject_duplicate_keys


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
    print(json.dumps({
        "sha256": descriptor["sha256"],
        "size": descriptor["size"],
        "type": descriptor["type"],
        "verified": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
