# Eval Report: signed Technocore transport verification
**Run #:** 3
**Date:** 2026-08-29 WIB

## Pass criteria

- [x] Reproducibility: clean virtualenv installed `requirements.txt`; two consecutive full runs passed the same 15 tests.
- [x] Demonstrability: a real Ed25519 key signed the official `lobby|7|shipped verifier` bytes and the CLI exported a parsed `cryptographically-verified-signed-transport` artifact.
- [x] Exact provenance: artifact preserves the DID/signature/nonce/room and SHA-256 of exact snapshot bytes.
- [x] Error paths: room, nonce, text, DID, signature, noncanonical DID/base64url, and partial CLI options reject.
- [x] Negative test: removing the `Ed25519PublicKey.verify` call produced five focused failures; restoring it passed.
- [x] Regression: existing unsigned artifact behavior and all receipt tests pass.

## Fail criteria

- None hit.

## Verdict: PASS

## Value statement

The verifier now distinguishes snapshot membership from cryptographically verified signed transport by validating the preserved official Technocore Ed25519 tuple and binding it to the exact snapshot bytes.

## Evidence

- `eval-results/signed-transport-verification/run-1.json`
- `eval-results/signed-transport-verification/run-2.json`
- `eval-results/signed-transport-verification/run-3.json`
