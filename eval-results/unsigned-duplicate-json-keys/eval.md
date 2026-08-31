# Eval Criteria: reject duplicate keys in unsigned CLI snapshots
**Domain:** bug fix
**Date:** 2026-09-01 (WIB)

## Pass criteria (ALL must be true)

1. **Reproducibility**
   - [ ] `python3 -m unittest -v` succeeds from a fresh checkout after installing `requirements.txt`.
   - [ ] Repeating the focused test produces the same result.

2. **Demonstrability**
   - [ ] A CLI regression test supplies a room snapshot with duplicate `messages` keys.
   - [ ] The CLI exits nonzero and creates no artifact for that ambiguous snapshot.

3. **Negative test**
   - [ ] On baseline parsing (`json.loads(snapshot)`), the focused regression test fails because the CLI exits zero and creates an artifact.
   - [ ] With strict parsing restored, the focused test and full suite pass.

4. **User-spec match**
   - [ ] The change adds distinct verifier utility rather than cosmetic activity.
   - [ ] Existing signed and unsigned valid-artifact behavior remains covered by the full suite.

## Fail criteria (ANY = no-go)

- Duplicate keys are silently resolved by last-key-wins parsing.
- The rejected command leaves an output artifact.
- Critical parsing behavior is mocked.
- Full suite, compile check, or CI fails.

## Output location

- `eval-results/unsigned-duplicate-json-keys/run-N.json`
- Each run records command, exit code, output tail, criterion result, and artifact paths.
