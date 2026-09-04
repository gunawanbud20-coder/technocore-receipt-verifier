# Eval Criteria: validate signed artifact schema
**Domain:** security hardening
**Date:** 2026-09-05 WIB

## Fresh gap and value

Baseline `5a2046c076d4472b937aa3db5b97485e64b147f5` verifies the embedded Ed25519 signature but does not validate the signed artifact envelope, receipt, signed-transport field set, or snapshot digest format. Consequently a digest-consistent artifact can carry a valid transport signature while asserting a noncanonical claim scope or carrying unbound fields.

**Value statement:** Offline verification now rejects signature-valid signed receipt artifacts whose envelope, receipt, transport tuple, or snapshot digest is not the canonical exported schema.

## Pass criteria (ALL must be true)

1. **Reproducibility**
   - [ ] `python3 -m unittest -v` passes twice with the same test count from the dependency-installed checkout.
   - [ ] `python3 -m compileall -q .` and `git diff --check` exit zero.

2. **Demonstrability**
   - [ ] A regression test proves the baseline CLI accepts a hash-consistent, signature-valid artifact with a false `claim_scope`.
   - [ ] The fixed CLI rejects noncanonical envelope fields, receipt fields/types, transport fields/types, and malformed `snapshot_sha256`.
   - [ ] A generated canonical signed artifact still verifies through the real CLI.

3. **Negative test**
   - [ ] Before production changes, the focused regression fails for the expected reason (CLI exits 0 for the malformed artifact).
   - [ ] Reverting only the production fix after GREEN makes the focused regression fail again.
   - [ ] Restoring the fix makes focused and full suites pass.

4. **User-spec match**
   - [ ] Change is in standalone owned repo `gunawanbud20-coder/technocore-receipt-verifier` under verified GitHub identity.
   - [ ] Live commit and GitHub CI are verified before state is recorded.

## Fail criteria (ANY = no-go)

- Signature verification is weakened or mocked.
- Existing canonical signed or unsigned artifacts stop verifying.
- The eval passes on baseline.
- Full suite or GitHub CI fails.
- Contribution duplicates an existing signed-schema validation commit.

## Output location

- `eval-results/signed-artifact-schema/run-N.json`
- `eval-results/signed-artifact-schema/report.md`
