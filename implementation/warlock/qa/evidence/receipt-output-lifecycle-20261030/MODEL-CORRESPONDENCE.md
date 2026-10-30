The executed root model v2 has two opaque full-intent keys with distinct targets,
separate current/unresolved/issued state and two observed outputs. Each action is
one local reducer transition; native messages and validated recovery proofs are
external observations, not atomic native effects. The corrected receipt updates
only an exact current key for every admitted outcome, independently of output;
all other records, scene, counters and sent-effect count remain unchanged.

The v1 proposal's impossible output2-to-old-output1 issuance is excluded in v2
by requiring scene1 in beginOld. V2 also checks the newer unresolved status.
Its handoff's earlier paragraph about output-gated Unknown is superseded by the
root correction section and actual executed rule. releaseOld describes only an
already-issued single-owner/no-preserveShared branch; full proof validation and
arbitrary-many-request behavior are not modeled. See final independent review.
