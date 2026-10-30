# HTTP owner model

Development-only Quint model of the intended Elm/Haskell transport owner. This is
supporting architecture and regression work, not a native implementation or
acceptance of an original Warlock scenario. Production remains Elm/Haskell;
all GUI elements remain Elm. The source-proposal header is preserved from the
reviewed input; qualification was performed separately.

The model distinguishes listener shutdown, request detach/close/drain and terminal
shared-owner destruction. The three post-free regression cases require retirement,
new frontend creation and timeout handling to stop after terminal destruction.
Environmental time may still advance. Transport availability grants no native
operations and does not replace the original native identity or deadline.

## Recorded qualification

With Quint 0.33.0 and seed 20261030, protected CPU checks passed both model/test
typechecks, executable initialization, all 20 individually selected original tests,
all three post-free regression tests and seven invariant samples of 1,000 traces
with at most 20 steps. Independent source review confirmed the three added guards.

The 10,000-trace, 40-step full-action sample reached 21 of 22 instrumented actions;
expiry was not observed. A larger 100,000-trace sample also observed no expiry and
failed its positive-coverage assertion. Both failed coverage records are retained.
The explicit no-abort/no-owner-shutdown scenario in
`http_owner_expiry_sampling.qnt` reached expiry in 746 of 1,000 traces. This
restricted scenario is not full-action coverage or a liveness proof.

The model abstracts authentication, cookie installation, OS errors, GLib callback
scheduling and physical socket closure. Its clock may stop at its bounded limit.
It cannot prove raw parsing, cryptographic secrecy, real callback quiescence,
WebKit behavior, native authority/resource retirement, or original 242-requirement /
417-scenario acceptance. The Haskell server's unresolved ownership defects remain
separate. The stopped host probe remains stopped; no runtime admission follows.

## Reproduce

Use the repository's protected CPU launcher and authenticated AgentBus QA ownership
protocol. Typecheck both `http_owner.qnt` and `http_owner_test.qnt`. Run each named
`run` definition in `http_owner_test.qnt` and `http_owner_regression.qnt` with an
anchored `--match=^NAME$`; require a positively selected passing test rather than
relying on a default selector. Use seed 20261030. Model sampling uses `quint run`,
not exhaustive verification. The restricted sampler must explicitly select main
`http_owner_expiry_sampling` and step `expiryScenario`.

Private machine evidence paths and source/review hashes are retained in
`qualification.json`. Those receipts are provenance references, not portable test
outputs or a complete toolchain/source distribution. A fresh environment must
produce its own protected results. Keep all failure records and original release,
packaging, native, AT/IME, deadline and resource obligations.
