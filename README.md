# Technocore Receipt Verifier

Standalone offline verifier for Technocore room receipts. It accepts saved room JSON and requires an exact match on DID, nonce, and swept text before returning a server sequence.

```bash
python3 receipt_verifier.py room.json   --did 'did:key:z6Mk...' --nonce 123 --text 'published artifact'
python3 -m unittest -v
```

No network access or private seed is required.

## Fail-closed signed-record validation

The verifier follows the official signed-room storage schema: `nonce` must be a
JSON integer and `seq` must be a positive JSON integer (booleans are rejected,
even though Python otherwise treats them as integers). A repeated `from` +
`nonce` pair makes the payload ambiguous and is rejected instead of selecting a
convenient copy. These checks prevent hand-edited, merged, or type-confused room
JSON from being promoted into a TCR-1 artifact.

The command-line nonce still uses Technocore's wire form: 1–19 ASCII digits.

## TCR-1 interoperability

A verified room receipt can be exported as deterministic canonical JSON and
referenced as a TCR-1 artifact:

```bash
python3 tcr1_interop.py room.json \
  --did 'did:key:z6Mk...' --nonce 123 --text 'published artifact' \
  --output room-receipt.json
```

The command prints a TCR-1-compatible artifact descriptor containing the exact
file URI, SHA-256 digest, and byte size. Output creation is exclusive: an
existing artifact is never overwritten.

The exported document deliberately carries
`claim_scope: transport-presence-only`. It proves only that the exact
DID/nonce/text tuple occurred in the supplied room payload. It **does not**
establish authorship, contribution truth, issuer acceptance, payment, or
eligibility. TCR-1 remains responsible for signing the task receipt and
verifying artifact integrity.
