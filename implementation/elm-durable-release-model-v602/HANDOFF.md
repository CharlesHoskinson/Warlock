# Durable reservation-release model

This is an independent executable Quint prototype for the V600 filesystem-ledger design. It changes no production ledger, shared checkpoint or native authority. The protected CPU campaign passes **31 explicitly selected named scenarios**, **2,000 bounded sampled traces with at most80 transitions**, and **15 typechecked deliberate mutations**, each producing an actual assertion counterexample. This is CPU architecture evidence, not exhaustive verification or filesystem/native acceptance.

## State and ordering

Historical key1 remains Unknown in a bounded history independently of its live reservation. Retirement acknowledgement never changes that historical outcome into Committed. Only a distinct explicit key2 may dispatch after durable release and acknowledgement; old/future/duplicate keys and exhausted history fail closed.

Release requires the native exact-key Retired proof. Registered, foreign-key, stale-epoch/barrier and future-barrier proofs are rejected. Distinct action request11 and geometry request12 must correlate to the current frontend generation and native sequence2 strictly after retirement barrier1. One observation, crossed requests, stale/future sequence or an old-generation completion after crash cannot prepare release. Frontend generations saturate at4 and stop read/new-effect admission rather than wrap.

The write protocol explicitly separates proof write, proof-file fsync, proof-directory fsync, Prepared-record write/fsync/directory fsync, exact admission unlink/directory fsync, Released-record write and final fsync. A successful fsync transition represents the relevant record's durable commit; its filesystem-specific implementation is outside this model.

Prepared recovery retains the reservation even when unlink is already durable. A crash before admission-directory fsync restores the old admission file; a crash after that fsync preserves its absence but remains blocked until Released is durably committed. Frontend acknowledgement and new explicit dispatch occur only afterwards. A durably Released record cannot recreate the exact old admission key.

A targeted scenario exposed a real prototype defect: repeated Prepared-directory completion after Released regressed the journal stage. The corrected action only transitions stage0 to Prepared. `qa/failed-stage-regression/` retains the failed source/assertion. Late prepare completion must not rewrite a terminal Released record in the real ledger either.

## Scenarios and negative controls

Named scenarios cover successful release, Prepared restart, pre-prepare unlink, acknowledgement before final fsync, nondurable/durable unlink crashes, released-key resurrection, Unknown preservation, registered/foreign/stale/future proofs, separate read correlations, history saturation, stage monotonicity, old-generation reads and generation exhaustion. Ten additional named tests crash immediately after each write/fsync boundary of the protocol.

Mutants weaken premature acknowledgement, Prepared restart, prepare-before-unlink, registered/foreign/future proof rejection, both-read prerequisites, request correlation, observation freshness, released-key suppression, history-to-commit inference, old-intent refusal, stage monotonicity, generation correlation and bounded history. Every mutant typechecks; each selected named scenario then fails by assertion, not parser/tool failure. Quint grammar drafts are preserved separately under `qa/failed-*`.

`qa/report.json` records exact selected and actually executed names, commands, seeds, bounded campaign parameters, output hashes, source hashes and mutation outcomes. Passing named traces are retained as ITF files. Mutation counterexample states appear in their retained assertion logs; these do not claim minimal counterexamples.

## Boundaries and assumptions

The native authority epoch and exact target identity are held stable across the modeled daemon crashes. Native-authority replacement, scene/output changes, PID/address reuse, parser/authentication semantics, malicious files/symlinks, real power-loss durability, permission/fsync failure, directory renames and concurrent writers require separate implementation tests. Native proof truth is represented by `nativeRetired`; it is not obtained from a real compositor.

The disk abstraction assumes successful synchronized writes survive, while unsynchronized writes may be lost on crash. It uses no actual files or fsync syscalls. Released-record final fsync stands for whatever file/directory synchronization the real publication mechanism requires. The real V600 implementation must prove those details and preserve original command deadlines. Current sequence/identity domains are intentionally small, and sampled traces do not exhaust interleavings or prove liveness under arbitrary scheduling.

`committed` describes only the old historical Unknown key. `effect` describes dispatch of the separately admitted new key, not native completion. The model deliberately has no rule inferring a window effect or Committed outcome from release acknowledgement.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-durable-release-model-v602/qa/run.py
```

Preserve the current source/evidence before preparing another derivative. Root can compare the modeled transitions to V600 independently; this component grants no native deployment or full-roadmap acceptance.
