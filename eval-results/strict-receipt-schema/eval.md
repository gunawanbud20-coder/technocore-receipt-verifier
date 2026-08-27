# Eval Criteria: fail-closed signed receipt schema
**Domain:** security hardening
**Date:** 2026-08-28 WIB

## Pass criteria (ALL must be true)

1. **Reproducibility**
   - [x] `python3 -m unittest -v` exits 0 from a clean checkout.
   - [x] Two unchanged runs report the same test count and result.
2. **Demonstrability**
   - [x] Tests prove valid official signed-room records use integer nonce and positive integer sequence.
   - [x] Tests prove string/bool nonce, bool/non-positive sequence, and duplicate DID+nonce records are rejected.
3. **Negative test**
   - [x] Baseline verifier fails the new strict-schema tests.
   - [x] Restoring the hardened verifier makes the full suite pass.
4. **User-spec match**
   - [x] Change is substantive TCR-1 receipt security hardening informed by official Technocore source.
   - [x] Existing deterministic TCR-1 artifact and exclusive-write behavior remain green.

## Fail criteria (ANY = no-go)

- Valid records accepted by the official signed lane are rejected.
- Ambiguous duplicate receipts are silently resolved.
- Critical verification is mocked.
- Existing artifact hash/exclusive-write tests regress.

## Output location

- `eval-results/strict-receipt-schema/run-N.json`
- Each run records command, exit code, output tail, criterion result, and elapsed time.
