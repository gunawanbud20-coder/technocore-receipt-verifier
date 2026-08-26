import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tcr1_interop import build_transport_artifact, write_transport_artifact


class TCR1InteropTests(unittest.TestCase):
    def setUp(self):
        self.room = {
            "messages": [
                {
                    "from": "did:key:zA",
                    "nonce": "7",
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


if __name__ == "__main__":
    unittest.main()
