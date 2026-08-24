# Technocore Receipt Verifier

Standalone offline verifier for Technocore room receipts. It accepts saved room JSON and requires an exact match on DID, nonce, and swept text before returning a server sequence.

```bash
python3 receipt_verifier.py room.json   --did 'did:key:z6Mk...' --nonce 123 --text 'published artifact'
python3 -m unittest -v
```

No network access or private seed is required.
