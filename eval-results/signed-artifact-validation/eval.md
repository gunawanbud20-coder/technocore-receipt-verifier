# Eval Criteria: signed artifact validation
**Domain:** security hardening
**Date:** 2026-09-03

## Pass criteria (ALL must be true)
- [ ] A forged `technocore-signed-room-receipt` with a self-consistent TCR-1 descriptor is rejected by the CLI.
- [ ] A legitimately signed generated artifact remains accepted by the CLI.
- [ ] Exact command `python3 -m unittest -v` passes from a fresh checkout.
- [ ] Two unchanged full-suite runs produce the same test count and result.
- [ ] Negative test: removing signed-artifact validation makes the forged-signature regression fail.
- [ ] Re-applying validation makes focused and full suites pass.

## Fail criteria (ANY = no-go)
- Critical signature verification is mocked.
- Unsigned receipt behavior regresses.
- Validation claims snapshot presence without access to the snapshot.
- Test passes on baseline.

## Output location
- `eval-results/signed-artifact-validation/run-N.json`
- Include command, stdout tail, exit code, elapsed time, criterion verdict, and artifact paths.
