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
convenient copy. Both command-line entry points also reject duplicate JSON keys
at any nesting level instead of accepting Python's last-key-wins interpretation.
These checks prevent hand-edited, merged, or type-confused room JSON from being
promoted into a TCR-1 artifact.

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
existing artifact is never overwritten. Save the descriptor and independently
verify all four bindings (file URI, byte size, digest, and artifact type):

```bash
python3 tcr1_interop.py room.json \
  --did 'did:key:z6Mk...' --nonce 123 --text 'published artifact' \
  --output room-receipt.json > room-receipt.descriptor.json
python3 tcr1_verify.py room-receipt.descriptor.json room-receipt.json
```

The verifier exits nonzero if either JSON document has duplicate keys, if a
field has an invalid type, if an unsigned receipt is not the canonical
four-field envelope and four-field receipt produced above, or if any binding
differs. A successful run emits a single deterministic JSON result with
`verified: true` and the recomputed SHA-256 and size.

The exported document deliberately carries
`claim_scope: transport-presence-only`. It proves only that the exact
DID/nonce/text tuple occurred in the supplied room payload. It **does not**
establish authorship, contribution truth, issuer acceptance, payment, or
eligibility. TCR-1 remains responsible for signing the task receipt and
verifying artifact integrity.

### Cryptographically verified signed transport

If the original unpadded base64url signature was preserved by the sender, pass
it with the room name to verify Technocore's official
`room|nonce|swept-text` Ed25519 canonical string before export:

```bash
python3 tcr1_interop.py room.json \
  --did 'did:key:z6Mk...' --nonce 123 --text 'published artifact' \
  --room lobby --signature '86-character-unpadded-base64url' \
  --output signed-room-receipt.json
```

This artifact is separately labelled
`cryptographically-verified-signed-transport`, preserves the signed tuple, and
binds it to the SHA-256 digest of the exact input snapshot bytes. The server's
ordinary room response does not retain signatures, so this stronger mode is
available only when the sender kept the original signature.
