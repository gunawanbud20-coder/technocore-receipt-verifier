import unittest
from receipt_verifier import find_receipt


class ReceiptTests(unittest.TestCase):
    def test_exact_match_returns_sequence(self):
        data = {"messages": [
            {"from": "did:key:zA", "nonce": 7, "text": "hello world", "seq": 9},
            {"from": "did:key:zA", "nonce": 8, "text": "hello world", "seq": 10},
        ]}
        self.assertEqual(find_receipt(data, "did:key:zA", "7", "hello\nworld")["sequence"], 9)

    def test_rejects_missing_receipt(self):
        with self.assertRaises(LookupError):
            find_receipt({"messages": []}, "did:key:zA", "7", "hello")

    def test_rejects_malformed_payload(self):
        with self.assertRaises(ValueError):
            find_receipt({"messages": "bad"}, "did:key:zA", "7", "hello")

    def test_rejects_ambiguous_duplicate_did_nonce_receipts(self):
        data = {"messages": [
            {"from": "did:key:zA", "nonce": 7, "text": "first", "seq": 3},
            {"from": "did:key:zA", "nonce": 7, "text": "expected", "seq": 4},
        ]}
        with self.assertRaisesRegex(ValueError, "duplicate DID and nonce"):
            find_receipt(data, "did:key:zA", "7", "expected")

    def test_rejects_string_nonce_that_official_signed_lane_never_stores(self):
        data = {"messages": [
            {"from": "did:key:zA", "nonce": "7", "text": "expected", "seq": 4},
        ]}
        with self.assertRaisesRegex(ValueError, "nonce must be an integer"):
            find_receipt(data, "did:key:zA", "7", "expected")

    def test_rejects_boolean_nonce_that_python_might_treat_as_one(self):
        data = {"messages": [
            {"from": "did:key:zA", "nonce": True, "text": "expected", "seq": 4},
        ]}
        with self.assertRaisesRegex(ValueError, "nonce must be an integer"):
            find_receipt(data, "did:key:zA", "1", "expected")

    def test_rejects_non_positive_or_boolean_sequences(self):
        for sequence in (True, 0, -1):
            with self.subTest(sequence=sequence):
                data = {"messages": [
                    {"from": "did:key:zA", "nonce": 7, "text": "expected", "seq": sequence},
                ]}
                with self.assertRaisesRegex(ValueError, "sequence must be a positive integer"):
                    find_receipt(data, "did:key:zA", "7", "expected")


if __name__ == "__main__":
    unittest.main()
