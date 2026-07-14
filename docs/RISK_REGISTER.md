# AFIMS-R v0.4.0 risk register

| Risk | Consequence | Current control | Residual status |
|---|---|---|---|
| Reference fixtures are finite and authored with the evaluator | Passing 85/85 can overstate real-world detection | Certification scope is explicitly limited; production and universal claims are prohibited | Open; requires independent adversarial and domain corpora |
| Final Confidence question 14 is not globally decidable | A universal “no improvement exists” claim would be unsound | Deterministic bounded audit plus an explicit non-exhaustive scope qualifier | Accepted only for the declared fixture pack |
| Generator, validator, and certifier run in one local trust domain | Process compromise could affect all three roles | Distinct identities, self-certification/collision gates, sealed evidence | Open until services and credentials are independently isolated |
| Evidence is mutable on a local filesystem | Local hashes detect changes but do not prevent them | Per-case hashes, manifests, read-back verification | Closed only after external WORM/COMPLIANCE execution |
| External governance dependencies may change | Unpinned downloads/actions can introduce supply-chain drift | Vendored governance source is hash-verified | Open: pin OPA, MinIO client, Trivy action, and installer digests before production |
| CI gate statuses could be asserted without evidence inspection | OPA could accept a narrative PASS | Root workflow executes tests, asserts generated JSON fields, verifies checksums, then runs RG-026/RG-027 | Residual dependence on protected workflow and branch governance |
| L4 evidence may be stale or bound to another artifact | False production-readiness claim | v3.2 policy checks digest, production environment, verification, and validity interval | Not executed locally |
| Hashes do not establish semantic correctness | Incorrect fixtures may be perfectly hashed | Executable evaluators, negative cases, group coverage, independent future review | Open; independent corpus review required |
| Unicode, locale, unit, and parser edge cases are unbounded | Missed numeric/entity changes | Targeted fixtures and regression tests | Open; expand fuzz/property-based testing |
| Threshold calibration may not transfer between domains | False PASS/FAIL rates | Fail-closed critical gates and scope declaration | Open; calibrate on labeled domain datasets |
