# Eval Report: validate unsigned TCR-1 receipt artifacts
**Run:** 3
**Date:** 2026-09-04

## Pass criteria

- [x] Reproducibility: `python3 -m unittest -v` passed twice with 31/31 tests.
- [x] Demonstrability: a digest-valid hollow unsigned artifact is rejected; generated valid unsigned and signed artifacts remain accepted.
- [x] Negative test: restoring baseline `tcr1_verify.py` made the regression fail because the CLI returned zero; restoring validation made it pass.
- [x] User-spec match: exact envelope/receipt fields, version, claim scope, nonce, sequence, and swept text are validated without regressing existing interoperability tests.

## Fail criteria

- None hit.

## Verdict: PASS

## Evidence

- `eval-results/unsigned-artifact-validation/run-1.json`
- `eval-results/unsigned-artifact-validation/run-2.json`
- `eval-results/unsigned-artifact-validation/run-3.json`
