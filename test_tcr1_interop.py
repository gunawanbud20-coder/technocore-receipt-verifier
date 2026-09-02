import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tcr1_interop import (
    build_signed_transport_artifact,
    build_transport_artifact,
    write_transport_artifact,
)


B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _base58(raw):
    number = int.from_bytes(raw, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = B58[remainder] + encoded
    return encoded


def _signed_identity(seed=b"\x11" * 32):
    key = Ed25519PrivateKey.from_private_bytes(seed)
    did = "did:key:z" + _base58(b"\xed\x01" + key.public_key().public_bytes_raw())
    return key, did


class TCR1InteropTests(unittest.TestCase):
    def setUp(self):
        self.room = {
            "messages": [
                {
                    "from": "did:key:zA",
                    "nonce": 7,
                    "text": "shipped verifier",
                    "seq": 42,
                }
            ]
        }

    def test_descriptor_matches_deterministic_transport_artifact(self):
        encoded, descriptor = build_transport_artifact(
            self.room, "did:key:zA", "7", "shipped verifier", "file:room-receipt.json"
        )
        document = json.loads(encoded)
        self.assertEqual(document["type"], "technocore-room-receipt")
        self.assertEqual(document["version"], 1)
        self.assertEqual(document["claim_scope"], "transport-presence-only")
        self.assertNotIn("eligibility", json.dumps(document).lower())
        self.assertEqual(encoded, json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n")
        self.assertEqual(descriptor, {
            "type": "technocore-room-receipt",
            "uri": "file:room-receipt.json",
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "size": len(encoded),
        })

    def test_signed_artifact_verifies_official_room_canonical_string(self):
        key, did = _signed_identity()
        room = {"messages": [{**self.room["messages"][0], "from": did}]}
        room_bytes = json.dumps(room, separators=(",", ":")).encode()
        signature = base64.urlsafe_b64encode(
            key.sign(b"lobby|7|shipped verifier")
        ).decode().rstrip("=")

        encoded, _ = build_signed_transport_artifact(
            room_bytes, "lobby", did, signature, "7", "shipped verifier", "file:signed.json"
        )

        document = json.loads(encoded)
        self.assertEqual(document["claim_scope"], "cryptographically-verified-signed-transport")
        self.assertEqual(document["signed_transport"]["did"], did)
        self.assertEqual(document["signed_transport"]["nonce"], "7")
        self.assertEqual(document["signed_transport"]["room"], "lobby")
        self.assertEqual(document["signed_transport"]["signature"], signature)
        self.assertEqual(
            document["signed_transport"]["snapshot_sha256"],
            hashlib.sha256(room_bytes).hexdigest(),
        )
        self.assertEqual(document["receipt"]["sequence"], 42)

    def test_signed_artifact_rejects_duplicate_json_keys(self):
        key, did = _signed_identity()
        signature = base64.urlsafe_b64encode(
            key.sign(b"lobby|7|shipped verifier")
        ).decode().rstrip("=")
        valid_message = (
            f'{{"from":"{did}","nonce":7,"text":"shipped verifier","seq":42}}'
        )
        duplicate_cases = {
            "messages": f'{{"messages":[],"messages":[{valid_message}]}}',
            "from": (
                f'{{"messages":[{{"from":"did:key:zA","from":"{did}",'
                '"nonce":7,"text":"shipped verifier","seq":42}]}'
            ),
            "nonce": (
                f'{{"messages":[{{"from":"{did}","nonce":6,"nonce":7,'
                '"text":"shipped verifier","seq":42}]}'
            ),
            "text": (
                f'{{"messages":[{{"from":"{did}","nonce":7,"text":"other",'
                '"text":"shipped verifier","seq":42}]}'
            ),
            "seq": (
                f'{{"messages":[{{"from":"{did}","nonce":7,'
                '"text":"shipped verifier","seq":41,"seq":42}]}'
            ),
        }

        for name, snapshot in duplicate_cases.items():
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    build_signed_transport_artifact(
                        snapshot.encode(),
                        "lobby",
                        did,
                        signature,
                        "7",
                        "shipped verifier",
                        "file:signed.json",
                    )

    def test_signed_artifact_rejects_noncanonical_did_key_encoding(self):
        key, did = _signed_identity()
        noncanonical_did = did[:9] + "1" + did[9:]
        room = {"messages": [{**self.room["messages"][0], "from": noncanonical_did}]}
        signature = base64.urlsafe_b64encode(
            key.sign(b"lobby|7|shipped verifier")
        ).decode().rstrip("=")

        with self.assertRaisesRegex(ValueError, "signature does not verify"):
            build_signed_transport_artifact(
                json.dumps(room).encode(),
                "lobby",
                noncanonical_did,
                signature,
                "7",
                "shipped verifier",
                "file:signed.json",
            )

    def test_signed_artifact_rejects_altered_signed_tuple(self):
        key, did = _signed_identity()
        _, other_did = _signed_identity(b"\x22" * 32)
        signature_bytes = key.sign(b"lobby|7|shipped verifier")
        signature = base64.urlsafe_b64encode(signature_bytes).decode().rstrip("=")
        bad_signature = bytearray(signature_bytes)
        bad_signature[0] ^= 1
        bad_signature = base64.urlsafe_b64encode(bad_signature).decode().rstrip("=")
        cases = {
            "room": (did, 7, "shipped verifier", "meta", signature),
            "nonce": (did, 8, "shipped verifier", "lobby", signature),
            "text": (did, 7, "changed verifier", "lobby", signature),
            "did": (other_did, 7, "shipped verifier", "lobby", signature),
            "signature": (did, 7, "shipped verifier", "lobby", bad_signature),
        }
        for name, (case_did, nonce, text, room, case_signature) in cases.items():
            with self.subTest(name=name):
                snapshot = {"messages": [{
                    "from": case_did,
                    "nonce": nonce,
                    "text": text,
                    "seq": 42,
                }]}
                with self.assertRaisesRegex(ValueError, "signature does not verify"):
                    build_signed_transport_artifact(
                        json.dumps(snapshot).encode(),
                        room,
                        case_did,
                        case_signature,
                        str(nonce),
                        text,
                        "file:signed.json",
                    )

    def test_signed_artifact_rejects_standard_base64_signature_alphabet(self):
        for seed_number in range(1, 256):
            key, did = _signed_identity(bytes([seed_number]) * 32)
            signature = base64.urlsafe_b64encode(
                key.sign(b"lobby|7|shipped verifier")
            ).decode().rstrip("=")
            if "-" in signature or "_" in signature:
                break
        standard_signature = signature.replace("-", "+").replace("_", "/")
        room = {"messages": [{**self.room["messages"][0], "from": did}]}

        with self.assertRaisesRegex(ValueError, "signature does not verify"):
            build_signed_transport_artifact(
                json.dumps(room).encode(),
                "lobby",
                did,
                standard_signature,
                "7",
                "shipped verifier",
                "file:signed.json",
            )

    def test_cli_exports_verified_signed_transport_artifact(self):
        key, did = _signed_identity()
        room = {"messages": [{**self.room["messages"][0], "from": did}]}
        signature = base64.urlsafe_b64encode(
            key.sign(b"lobby|7|shipped verifier")
        ).decode().rstrip("=")
        with tempfile.TemporaryDirectory() as temp:
            snapshot = Path(temp) / "room.json"
            output = Path(temp) / "signed.json"
            snapshot.write_bytes(json.dumps(room, separators=(",", ":")).encode())
            run = subprocess.run(
                [
                    sys.executable,
                    "tcr1_interop.py",
                    str(snapshot),
                    "--did", did,
                    "--nonce", "7",
                    "--text", "shipped verifier",
                    "--room", "lobby",
                    "--signature", signature,
                    "--output", str(output),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(
                json.loads(output.read_bytes())["claim_scope"],
                "cryptographically-verified-signed-transport",
            )

    def test_cli_rejects_partial_signed_transport_options(self):
        _, did = _signed_identity()
        room = {"messages": [{**self.room["messages"][0], "from": did}]}
        with tempfile.TemporaryDirectory() as temp:
            snapshot = Path(temp) / "room.json"
            output = Path(temp) / "signed.json"
            snapshot.write_text(json.dumps(room))
            run = subprocess.run(
                [
                    sys.executable,
                    "tcr1_interop.py",
                    str(snapshot),
                    "--did", did,
                    "--nonce", "7",
                    "--text", "shipped verifier",
                    "--room", "lobby",
                    "--output", str(output),
                ],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(output.exists())

    def test_cli_rejects_duplicate_keys_in_unsigned_snapshot(self):
        duplicate_snapshot = (
            '{"messages":[],"messages":['
            '{"from":"did:key:zA","nonce":7,"text":"shipped verifier","seq":42}'
            "]}"
        )
        with tempfile.TemporaryDirectory() as temp:
            snapshot = Path(temp) / "room.json"
            output = Path(temp) / "receipt.json"
            snapshot.write_text(duplicate_snapshot)
            run = subprocess.run(
                [
                    sys.executable,
                    "tcr1_interop.py",
                    str(snapshot),
                    "--did", "did:key:zA",
                    "--nonce", "7",
                    "--text", "shipped verifier",
                    "--output", str(output),
                ],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(output.exists())

    def test_write_is_exclusive_and_preserves_exact_hashed_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "receipt.json"
            descriptor = write_transport_artifact(
                target, self.room, "did:key:zA", "7", "shipped verifier"
            )
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), descriptor["sha256"])
            with self.assertRaises(FileExistsError):
                write_transport_artifact(
                    target, self.room, "did:key:zA", "7", "shipped verifier"
                )

    def test_descriptor_verifier_cli_accepts_generated_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "receipt.json"
            descriptor_path = Path(temp) / "descriptor.json"
            descriptor = write_transport_artifact(
                artifact, self.room, "did:key:zA", "7", "shipped verifier"
            )
            descriptor_path.write_text(json.dumps(descriptor))

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout), {
                "sha256": descriptor["sha256"],
                "size": descriptor["size"],
                "type": "technocore-room-receipt",
                "verified": True,
            })

    def test_descriptor_verifier_cli_accepts_valid_signed_artifact(self):
        key, did = _signed_identity()
        room = {"messages": [{**self.room["messages"][0], "from": did}]}
        room_bytes = json.dumps(room, separators=(",", ":")).encode()
        signature = base64.urlsafe_b64encode(
            key.sign(b"lobby|7|shipped verifier")
        ).decode().rstrip("=")
        encoded, descriptor = build_signed_transport_artifact(
            room_bytes, "lobby", did, signature, "7", "shipped verifier", "file:signed.json"
        )

        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "signed.json"
            descriptor_path = Path(temp) / "descriptor.json"
            artifact.write_bytes(encoded)
            descriptor_path.write_text(json.dumps(descriptor))

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(json.loads(run.stdout)["verified"])

    def test_descriptor_verifier_cli_rejects_forged_signed_artifact(self):
        key, did = _signed_identity()
        room = {"messages": [{**self.room["messages"][0], "from": did}]}
        room_bytes = json.dumps(room, separators=(",", ":")).encode()
        signature = base64.urlsafe_b64encode(
            key.sign(b"lobby|7|shipped verifier")
        ).decode().rstrip("=")
        encoded, _ = build_signed_transport_artifact(
            room_bytes, "lobby", did, signature, "7", "shipped verifier", "file:signed.json"
        )
        document = json.loads(encoded)
        document["signed_transport"]["signature"] = (
            "A" if signature[0] != "A" else "B"
        ) + signature[1:]
        forged = json.dumps(
            document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode() + b"\n"

        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "signed.json"
            descriptor_path = Path(temp) / "descriptor.json"
            artifact.write_bytes(forged)
            descriptor_path.write_text(json.dumps({
                "type": document["type"],
                "uri": "file:signed.json",
                "sha256": hashlib.sha256(forged).hexdigest(),
                "size": len(forged),
            }))

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("signed artifact signature does not verify", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_descriptor_verifier_cli_rejects_altered_artifact_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "receipt.json"
            descriptor_path = Path(temp) / "descriptor.json"
            descriptor = write_transport_artifact(
                artifact, self.room, "did:key:zA", "7", "shipped verifier"
            )
            descriptor_path.write_text(json.dumps(descriptor))
            artifact.write_bytes(artifact.read_bytes() + b" ")

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("artifact size does not match descriptor", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_descriptor_verifier_cli_rejects_digest_mismatch_at_same_size(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "receipt.json"
            descriptor_path = Path(temp) / "descriptor.json"
            descriptor = write_transport_artifact(
                artifact, self.room, "did:key:zA", "7", "shipped verifier"
            )
            descriptor_path.write_text(json.dumps(descriptor))
            altered = bytearray(artifact.read_bytes())
            altered[-2] ^= 1
            artifact.write_bytes(altered)

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("artifact SHA-256 does not match descriptor", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_descriptor_verifier_cli_rejects_uri_for_different_file(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "receipt.json"
            descriptor_path = Path(temp) / "descriptor.json"
            descriptor = write_transport_artifact(
                artifact, self.room, "did:key:zA", "7", "shipped verifier"
            )
            descriptor["uri"] = "file:other.json"
            descriptor_path.write_text(json.dumps(descriptor))

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("descriptor URI does not name artifact", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_descriptor_verifier_cli_rejects_artifact_type_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "receipt.json"
            descriptor_path = Path(temp) / "descriptor.json"
            descriptor = write_transport_artifact(
                artifact, self.room, "did:key:zA", "7", "shipped verifier"
            )
            descriptor["type"] = "technocore-signed-room-receipt"
            descriptor_path.write_text(json.dumps(descriptor))

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("artifact type does not match descriptor", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_descriptor_verifier_cli_rejects_duplicate_descriptor_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "receipt.json"
            descriptor_path = Path(temp) / "descriptor.json"
            descriptor = write_transport_artifact(
                artifact, self.room, "did:key:zA", "7", "shipped verifier"
            )
            descriptor_path.write_text(
                '{"sha256":"' + "0" * 64 + '",'
                + json.dumps(descriptor, separators=(",", ":"))[1:]
            )

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("duplicate JSON key: sha256", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_descriptor_verifier_cli_rejects_boolean_size(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "receipt.json"
            descriptor_path = Path(temp) / "descriptor.json"
            descriptor = write_transport_artifact(
                artifact, self.room, "did:key:zA", "7", "shipped verifier"
            )
            descriptor["size"] = True
            descriptor_path.write_text(json.dumps(descriptor))

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("descriptor has invalid size", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_descriptor_verifier_cli_rejects_duplicate_artifact_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "receipt.json"
            descriptor_path = Path(temp) / "descriptor.json"
            artifact_bytes = (
                b'{"type":"other","type":"technocore-room-receipt","version":1}\n'
            )
            artifact.write_bytes(artifact_bytes)
            descriptor = {
                "type": "technocore-room-receipt",
                "uri": "file:receipt.json",
                "sha256": hashlib.sha256(artifact_bytes).hexdigest(),
                "size": len(artifact_bytes),
            }
            descriptor_path.write_text(json.dumps(descriptor))

            run = subprocess.run(
                [sys.executable, "tcr1_verify.py", str(descriptor_path), str(artifact)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(run.returncode, 0)
            self.assertIn("duplicate JSON key: type", run.stderr)
            self.assertEqual(run.stdout, "")


if __name__ == "__main__":
    unittest.main()
