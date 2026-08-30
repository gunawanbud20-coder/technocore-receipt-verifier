# Eval Report: reject ambiguous duplicate JSON keys
**Run:** 3
**Date:** 2026-08-31

## Pass criteria

- [x] Reproducibility: the complete 16-test suite passed repeatedly.
- [x] Demonstrability: raw snapshots with duplicate `messages`, `from`, `nonce`, `text`, and `seq` keys are rejected with `duplicate JSON key`.
- [x] Negative test: default `json.loads` accepted all five ambiguous cases and failed the regression; restoring the strict object-pairs decoder passed it.
- [x] User-spec match: signed snapshot verification now has one unambiguous interpretation across JSON implementations.

## Fail criteria

- None hit.

## Verdict: PASS

## Evidence

- `eval-results/duplicate-json-keys/run-1.json` — RED baseline
- `eval-results/duplicate-json-keys/run-2.json` — fix removed, eval failed
- `eval-results/duplicate-json-keys/run-3.json` — fix restored, focused and full suites passed
