# Eval Criteria: TCR-1 transport-receipt interoperability

## Pass criteria

- [x] `build_transport_artifact` emits deterministic canonical JSON.
- [x] TCR-1 descriptor SHA-256 and size match the exact artifact bytes.
- [x] Artifact states `claim_scope=transport-presence-only` and makes no eligibility claim.
- [x] Existing output paths are never overwritten.
- [x] Existing receipt-verifier tests remain green.
- [x] Negative test: removing the implementation makes the new test fail.
- [x] Commit is pushed from `gunawanbud20-coder` and CI succeeds.

## Fail criteria

- Adds network or private-key dependency.
- Treats room sequence/signature as contribution truth, acceptance, or eligibility.
- Duplicates TCR-1 signature verification instead of producing an interoperable artifact.
