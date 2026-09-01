# Eval Report: verify TCR-1 artifact descriptors
**Run:** 3
**Date:** 2026-09-02

## Pass criteria

- [x] Reproducibility: the 18 focused interop tests passed twice; the 26-test full suite passed.
- [x] Demonstrability: an artifact and descriptor generated through the documented command path verified with exit 0 and deterministic JSON output.
- [x] Fail-closed behavior: altered size/digest, wrong URI/type, duplicate keys, and boolean size each exit nonzero.
- [x] Negative test: removing `tcr1_verify.py` made the valid-descriptor regression fail; restoring it made focused and full suites pass.
- [x] User-spec match: adds an executable descriptor consumer to close a concrete interoperability gap.

## Fail criteria

None hit.

## Verdict: PASS

## Evidence

- `eval-results/verify-tcr1-descriptors/run-1.json`
- `eval-results/verify-tcr1-descriptors/run-2.json`
- `eval-results/verify-tcr1-descriptors/run-3.json`
- `tcr1_verify.py`
- `test_tcr1_interop.py`
