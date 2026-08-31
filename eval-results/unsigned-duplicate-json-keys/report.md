# Eval Report: reject duplicate keys in unsigned CLI snapshots
**Run #:** 3
**Date:** 2026-09-01 WIB

## Pass criteria

- [x] Reproducibility: focused regression passed twice; full `python3 -m unittest -v` passed with 18 tests.
- [x] Demonstrability: real subprocess tests feed duplicate top-level `messages` keys to both CLI entry points; both reject the input and TCR-1 creates no artifact.
- [x] Negative test: removing the two strict parsing hooks made both regressions fail because each CLI returned exit code 0; restoring hooks made both focused tests and the full suite pass.
- [x] User-spec match: closes the remaining unsigned last-key-wins ambiguity while retaining strict signed parsing and all valid-artifact tests.

## Fail criteria

- None hit.

## Verdict: PASS

## Evidence

- `eval-results/unsigned-duplicate-json-keys/run-1.json` — initial RED
- `eval-results/unsigned-duplicate-json-keys/run-2.json` — hooks disabled, both evals fail
- `eval-results/unsigned-duplicate-json-keys/run-3.json` — hooks restored, 18-test suite passes
