# Eval Criteria: validate unsigned TCR-1 receipt artifacts
**Domain:** security hardening
**Date:** 2026-09-04

## Pass criteria (ALL must be true)

1. **Reproducibility**
   - [x] `python3 -m unittest -v` passes from a clean checkout after installing `requirements.txt`.
   - [x] Repeating the full suite produces the same pass count and exit code.

2. **Demonstrability**
   - [x] A descriptor with correct URI, size, SHA-256, and type for the hollow artifact `{"type":"technocore-room-receipt"}` is rejected by `tcr1_verify.py`.
   - [x] Generated valid unsigned and signed artifacts remain accepted.

3. **Negative test**
   - [x] On baseline `e4441a4`, the hollow-artifact regression test fails because the verifier exits zero.
   - [x] With validation restored, the same regression test passes because the verifier exits nonzero.

4. **User-spec match**
   - [x] Validation requires the canonical unsigned artifact's exact top-level fields, version, claim scope, and receipt field types/values.
   - [x] No existing interoperability behavior regresses.

## Fail criteria (ANY = no-go)

- The critical verification path is mocked or stubbed.
- A digest-valid hollow or malformed unsigned receipt prints `verified: true`.
- Existing valid unsigned or signed artifact tests fail.
- The eval passes on baseline.
- Full-suite output is flaky across two unchanged runs.

## Output location

- `eval-results/unsigned-artifact-validation/run-N.json`
- Each run records command, exit code, stdout/stderr tail, elapsed time, criterion verdicts, and artifact paths.
