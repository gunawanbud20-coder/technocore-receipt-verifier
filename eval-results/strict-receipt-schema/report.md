# Eval Report: fail-closed signed receipt schema

**Date:** 2026-08-28 WIB  
**Official source inspected:** `flop-labs/technocore-chat` commit `9c7df0e3616c` and `src/store.py`

## Pass criteria

- [x] Reproducibility: runs 3 and 4 each passed the same 9 tests.
- [x] Demonstrability: executable tests reject ambiguous duplicate DID/nonce records, non-integer nonce values, boolean nonce values, and boolean/non-positive sequences.
- [x] Negative test: restoring baseline `receipt_verifier.py` made 6 assertions fail in run 2.
- [x] User-spec match: deterministic TCR-1 artifact hashing and exclusive creation remain covered and passing.

## Fail criteria

- None hit.

## Verdict: PASS

## Evidence

- `run-1.json`: initial focused RED test.
- `run-2.json`: production hardening reverted; full eval failed as required.
- `run-3.json`: hardening restored; 9/9 passed.
- `run-4.json`: unchanged reproducibility run; 9/9 passed.
