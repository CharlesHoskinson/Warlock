# V22 design evidence

V21 remains unchanged. `v21-history-measurement-final.json` records1,031 actual
Unix-peer requests with matching genuine durable rows, no synthetic records,
no runtime override, all534 input hashes/modes unchanged, and no failure.
Seven repeated real queries were measured at each archive history length, with
seven active rows after each point. Original1s absolute query bound stayed exact.
Proactive maintenance rotated actual64-row batches separately with a constant
remaining-budget callback; this measures maintenance elapsed time but does NOT
prove its original absolute deadline. Nothing establishes arbitrary history
acceptance, native baseline acceptance, or physical steady-state latency.

| Archived rows | Segments | Median ms | Max ms |
|---:|---:|---:|---:|
|0|0|23.480|31.260|
|64|1|46.585|64.941|
|128|2|109.743|144.743|
|256|4|144.716|173.365|
|512|8|300.906|357.845|
|768|12|441.730|501.991|
|1024|16|463.012|621.009|

V21 `ReadonlyIPC.authority` invokes `validate_storage`, which traverses every
segment and predecessor; measured cost increases with archived length while
active-row count stays bounded. These are observed costs, not a model of host
scheduling or an attribution for the retained native preparation failure.

Three actual Quint named counterexample witnesses show a deliberately weak
cached-startup Boolean admits a separately valid owner, FD or tip replacement;
the proposed exact current binding rejects each. They are design-antipattern
counterexamples, not claims that V21 accepts those replacements. Additional
named witnesses cover both bad-peer-after-valid-reply and partial-then-valid
reply as terminal connection refusal, and publication-before-adoption crashes.

`olderAncestorDamageIsNotSilentlyClaimedCurrentTest` deliberately exposes the
proposed historical boundary: unrelated fresh data may pass after unborrowed
older ancestor damage, while no all-history-current claim is made. Full audit
and restart refuse that damage. This boundary requires root review before any
runtime change; the immutable V21 guards remain as implemented.

Initial syntax/model API failures are retained. First annotated-return and tuple
pattern draft failed parsing; first executable draft used Map.set on absent keys
and failed23 named cases. The source/log are retained; Map.put fixes insertion.
A42-case intermediate proof and48-case symbolic-seals proof are retained.
Final seals use actual kernel-observed47, separate regular read-only archive FD
role, and complete disk publication/token model. No runtime has been copied.
