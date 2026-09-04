# Eval Report: validate signed artifact schema
**Date:** 2026-09-05 WIB
**Baseline:** `5a2046c076d4472b937aa3db5b97485e64b147f5`

## Pass criteria

- [x] Reproducibility: two consecutive unchanged full-suite runs passed 33/33 tests; a restored post-negative run also passed 33/33.
- [x] Demonstrability: a real `tcr1_verify.py` CLI regression constructs a digest-consistent artifact with a valid Ed25519 signature and false `authorship` scope; baseline accepts it and the fix rejects it.
- [x] Canonical schema: exact envelope, receipt, and signed-transport field sets plus scalar types, canonical text, tuple bindings, signature encoding, and lowercase SHA-256 format are validated before signature verification.
- [x] Negative test: reverting only `tcr1_interop.py` produced 10 expected failures; restoring it passed focused and full suites.
- [x] Regression: canonical signed artifacts and all existing unsigned/signed behavior pass.
- [x] Static checks: `python3 -m compileall -q .` and `git diff --check` exit 0.

## Fail criteria

- None hit locally.

## Verdict: PASS

Live commit and GitHub CI evidence are recorded atomically in the scheduler state only after remote verification.

## Evidence

- `eval-results/signed-artifact-schema/run-1.json`
- `eval-results/signed-artifact-schema/run-2.json`
- `eval-results/signed-artifact-schema/run-3.json`
- `/tmp/signed-schema-red.log`
- `/tmp/signed-schema-negative.log`
- `/tmp/signed-schema-restored-full.log`
