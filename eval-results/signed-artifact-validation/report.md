# Eval Report: signed artifact validation
**Run:** 3
**Date:** 2026-09-03

## Pass criteria
- [x] Forged signed artifact with a recomputed, self-consistent descriptor is rejected.
- [x] Legitimately signed generated artifact is accepted.
- [x] `python3 -m unittest -v` passes: 28 tests.
- [x] Two unchanged full-suite runs both passed 28 tests.
- [x] Negative test: reverting production validation made the forged-signature regression fail.
- [x] Re-applied validation passed focused and full suites.

## Fail criteria
- None hit. Ed25519 verification uses the real cryptography implementation and the tool does not claim snapshot presence.

## Verdict: PASS

## Evidence
- `run-1.json` — baseline RED
- `run-2.json` — production-reverted negative test
- `run-3.json` — restored GREEN and deterministic full-suite runs
