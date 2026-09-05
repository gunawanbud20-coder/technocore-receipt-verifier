# Eval Report: fail-closed TCR-1 descriptor schema validation
**Run:** 3
**Date:** 2026-09-06

## Pass criteria

- [x] Reproducibility: focused regression passed twice with identical semantic output; full command reruns from repository root.
- [x] Demonstrability: 11 malformed schema cases are rejected, including extra/missing fields, unsupported or wrong-type artifact types, invalid URIs, and malformed SHA-256 values; generated descriptors remain accepted.
- [x] Negative test: restoring baseline `tcr1_verify.py` made the focused test fail with 11 failures; restoring the fix made it pass.
- [x] User-spec match: this closes a real fail-open gap where an unbound extra descriptor field was accepted and reported as verified.

## Fail criteria

- None hit.

## Verdict: PASS

## Evidence

- `eval-results/descriptor-schema-validation/run-1.json`
- `eval-results/descriptor-schema-validation/run-2.json`
- `eval-results/descriptor-schema-validation/run-3.json`
- `test_tcr1_interop.TCR1InteropTests.test_descriptor_verifier_cli_rejects_noncanonical_descriptor_schema`
