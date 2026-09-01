# Eval Criteria: verify TCR-1 artifact descriptors
**Domain:** build
**Date:** 2026-09-02

## Quality-gate basis

The repository emits TCR-1 artifact descriptors but has no executable consumer that verifies an artifact against one. This is a concrete interoperability gap: downstream users must independently reimplement URI, size, digest, and artifact-type checks.

## Pass criteria (ALL must be true)

1. **Reproducibility**
   - [ ] `python3 -m unittest -v` passes from the repository root.
   - [ ] Repeating the focused verifier tests produces the same result.

2. **Demonstrability**
   - [ ] A descriptor emitted by `build_transport_artifact` verifies through the real CLI with exit code 0.
   - [ ] CLI output is deterministic JSON identifying the verified type, SHA-256, and size.

3. **Fail-closed behavior**
   - [ ] Altered artifact bytes, digest, size, URI, or descriptor/artifact type fail with nonzero exit status.
   - [ ] Duplicate JSON keys in the descriptor or artifact fail with nonzero exit status.
   - [ ] Malformed field types, including booleans as integer sizes, fail with nonzero exit status.

4. **Negative test**
   - [ ] Without the verifier implementation, the focused valid-descriptor test fails.
   - [ ] With implementation restored, focused and full suites pass.

5. **User-spec match**
   - [ ] Contribution adds distinct technical utility, not cosmetic activity.
   - [ ] Live commit and CI are verified under `gunawanbud20-coder` before state is recorded.

## Fail criteria (ANY = no-go)

- Hash or size is trusted without recomputation.
- Critical behavior is mocked.
- Existing artifact output changes silently.
- Test passes without the verifier implementation.
- Full suite or GitHub CI does not pass.

## Output location

- `eval-results/verify-tcr1-descriptors/run-N.json`
- Include exact command, exit code, stdout/stderr tail, criterion result, elapsed time, and artifacts.
