# Compiled lifecycle evidence

`replay.py` freezes inputs, compiles `Replay.elm` and `RouterReplay.elm`, and runs
external JSON oracles against the actual Elm modules. Node only sends events and
asserts results; it contains no substitute state machine. All QA uses the
protected `qa_run.py` launcher. Failed reports and exact source copies remain.

The inherited V1 fixture assertions remain, with receipts correlated to their
original emitted binding. Additional cases cover independent targets, late and
wrong receipts, Unknown rebinding, 64 outstanding operations, 128 retained
retirements and fail-closed overflow on the 129th unique attempt, deduplication,
feedback bounds, strict provider fields/actions/counters, Unicode and raw UTF-8
byte limits. Raw cyclic JavaScript graphs and deep malformed native JSON test
safe rejection without serializing error values.

The generic core admits 64 distinct declared Launch actions. The window-only
provider vocabulary has fewer distinct actions; 64 repeated window aliases are
invalid despite their unique row IDs. Provider transport capacity and supported
window semantics are tested separately.

Router cases register real emitted Menu.Dispatch effects against validated
providers and native protocol-3/effect-protocol-1 commands. Receipts match the
complete original native key. Outer revision hints do not create observations.
The independent registry-capacity case deliberately commits one local core
operation without clearing its router mapping, exposing a full router with room
in the core. This is adversarial unit setup, not a legitimate production route.

`mutations.py` changes copied Elm source, compiles each variant, and requires the
named external oracle to detect ignored receipt binding, eviction of unresolved
operations, retirement-ledger reset, and ignored native receipt binding. Compiler
failure alone does not count as detection. `historical.py` separately tests saved
native Minimize/Restore frames; it does not qualify current native execution.

These checks establish bounded CPU behavior. They do not certify a live producer,
authenticate arbitrary callers, execute commands, or establish native popup,
focus, geometry, accessibility, or whole-desktop acceptance.
