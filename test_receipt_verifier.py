import unittest
from receipt_verifier import find_receipt


class ReceiptTests(unittest.TestCase):
    def test_exact_match_and_latest_sequence(self):
        data = {"messages": [
            {"from": "did:key:zA", "nonce": "7", "text": "hello world", "seq": 3},
            {"from": "did:key:zA", "nonce": "7", "text": "hello world", "seq": 9},
            {"from": "did:key:zA", "nonce": "8", "text": "hello world", "seq": 10},
        ]}
        self.assertEqual(find_receipt(data, "did:key:zA", "7", "hello\nworld")["sequence"], 9)

    def test_rejects_missing_receipt(self):
        with self.assertRaises(LookupError):
            find_receipt({"messages": []}, "did:key:zA", "7", "hello")

    def test_rejects_malformed_payload(self):
        with self.assertRaises(ValueError):
            find_receipt({"messages": "bad"}, "did:key:zA", "7", "hello")


if __name__ == "__main__":
    unittest.main()
