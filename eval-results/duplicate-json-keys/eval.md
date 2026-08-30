# Eval Criteria: reject ambiguous duplicate JSON keys
**Domain:** security hardening
**Date:** 2026-08-31

## Pass criteria (ALL must be true)

1. **Reproducibility**
   - [ ] `python3 -m unittest -v` passes twice from the repository checkout.
   - [ ] The same duplicate-key snapshot produces the same explicit rejection.

2. **Demonstrability**
   - [ ] A regression test supplies duplicate `messages`, `from`, `nonce`, `text`, and `seq` keys as raw JSON bytes.
   - [ ] Each duplicate-key case raises `ValueError` containing `duplicate JSON key`.

3. **Negative test**
   - [ ] Before implementation, the focused regression test fails because duplicate keys are accepted.
   - [ ] Removing the strict decoder after implementation makes the focused regression test fail; restoring it makes the test pass.

4. **User-spec match**
   - [ ] The change adds distinct security/interoperability utility rather than cosmetic activity.
   - [ ] Existing canonical snapshots and the complete test suite remain supported.

## Fail criteria (ANY = no-go)

- Duplicate-key detection is applied only in tests, not production parsing.
- Valid existing snapshots are rejected.
- Critical JSON parsing is mocked or depends on a network service.
- Full suite, repeated determinism run, live commit, or CI cannot be verified.

## Output location

- `eval-results/duplicate-json-keys/run-N.json`
- Include command, stdout/stderr tail, exit code, pass/fail, duration, and artifact paths.
