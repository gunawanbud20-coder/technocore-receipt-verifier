# Eval Criteria: signed Technocore transport verification
**Domain:** build
**Date:** 2026-08-29

## Quality-gate basis

Fresh concrete interoperability need: flop-labs/technocore-chat issue #281 asks transport artifacts to preserve and verify the official `room|nonce|swept-text` Ed25519 tuple instead of promoting snapshot membership to cryptographically verified transport.

## Pass criteria (ALL must be true)

1. **Reproducibility**
   - [x] `python3 -m unittest -v` passes from a fresh checkout after `python3 -m pip install -r requirements.txt`.
   - [x] Two consecutive full-suite runs report the same test count and zero failures.

2. **Demonstrability**
   - [x] An official-format Ed25519 `did:key` signature over `room|nonce|swept-text` verifies and the exported artifact labels it `cryptographically-verified-signed-transport`.
   - [x] Exported canonical JSON preserves `did`, unpadded base64url `signature`, `nonce`, swept text, sequence, and a SHA-256 digest of the exact supplied room snapshot bytes.

3. **Negative/error paths**
   - [x] A changed room, nonce, text, signature, or DID is rejected.
   - [x] Malformed DID/signature encodings fail closed without uncaught decoder errors.
   - [x] Removing the signature verification call makes the focused eval fail; restoring it makes the eval pass.

4. **User-spec match**
   - [x] Utility is distinct from existing snapshot-membership verification: callers can distinguish snapshot membership from cryptographically verified signed transport.
   - [x] Existing unsigned transport artifact behavior and full test suite remain green.

## Fail criteria (ANY = no-go)

- Signature accepted without Ed25519 verification.
- Re-serialized JSON is hashed instead of exact input snapshot bytes.
- Existing artifacts are silently relabeled as cryptographically verified.
- Tests depend on network access.
- Full suite or GitHub CI is not green.

## Output location

- `eval-results/signed-transport-verification/run-N.json`
- Include command, exit code, stdout/stderr tail, criterion verdicts, duration, and artifact paths.
