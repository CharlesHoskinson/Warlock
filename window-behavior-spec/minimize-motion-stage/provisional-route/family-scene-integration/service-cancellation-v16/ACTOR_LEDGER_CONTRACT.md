# V16 authenticated per-actor ledger

This source-only derivative inherits frozen RecoveryV17 manifest b7169939fcb0f50281fc50f4e897a3085e68ae4706d3426139fd9d58174d8aa4. Existing V16 live/actor proofs and frozen V17 remain immutable. No native acceptance is claimed.

## Provenance and current intent

A renderer can exist before a receipt. Every job therefore registers its exact actor (or explicit service-wide owner), role, PID/start, sealed producer/handoff/launcher material, exact argv and selected environment. The kernel-authenticated keeper independently observes those claimed process fields at the still-closed launch gate. A source digest cannot replace that observation. Job identities remain unique for the keeper's entire life. Accepted metadata and its hash remain in the complete ledger after closure.

Cancellation freezes one actor under the manager's exact current receipt/token/captured identity/complete member scope and current runtime lease. Freeze is authenticated and durable; a frozen actor cannot register further work. Jobs for another actor and service housekeeping continue. The current receipt is not falsely attributed to pre-receipt renderer launches. Freeze revision and complete historical job digest bind the actor witness, while unrelated actor revisions do not revoke it.

## Durability and closure

The keeper fsyncs each register, release, physical completion, native returned-result proof and freeze transition to its exact anchored private root before replying. The service persists the exact keeper snapshot before opening the gate. A failed durable transition latches ledger failure and no attest/release is possible; cleanup remains the inherited exact whole-keeper group protocol. History is never truncated: limits refuse a new registration before its gate, rather than forgetting an older uncertain job. Whole-keeper terminal closure and non-native group closure remain mandatory for restart paths.

An empty process group proves physical closure only. A native-effect/export job additionally requires an explicit exact durable semantic result proof tied to its registered source/lifetime and accepted result journal. It is not supplied merely by successful process exit or stdout. An uncertain native boundary is latched; neither another completion nor empty groups clears it. This derivative provides no uncertain-return waiver.

A per-actor terminal attestation is an authenticated fresh reply over the same kernel peer, exact keeper PID/start/UID/nonce/sealed-source/root/service/session, exact freeze intent, actor revision and complete ledger digest. Every historical selected-actor job must be normally physically complete; every native job must have its matching durable returned result; no active selected-actor group, missing history, unknown error or uncertain effect is permitted. Actual child lifetime/material is checked at registration, actual retained pidfd group closure at completion. The service compares the complete expected actor inventory before and after attestation, then persists it. Self-reported JSON, inferred zero job count, whole-keeper stop or absence of a PID cannot substitute.

## Invalidations and restart

Any current actor/receipt/token/scope, source/root/session/service/keeper identity, selected-actor revision or historical inventory replacement invalidates a partial witness. A keeper persistence fault, dropped history, crash, uncertain effect or unknown source remains quarantine. Restart must reauthenticate physical whole-keeper terminal closure and retained complete durable actor ledger and intent; there is no live attestation after keeper death. A durable cancel outcome is explicit non-settlement and ACK precedes source disposal. Current live cancellation ingress remains unimplemented until this ledger and the controller drain/observation obligations are wired and tested.

## Formal abstraction

Positive equality tokens model exact material/argv/environment and full scopes; `source` is the selected-and-observed source projection, not a Boolean. `issuer` distinguishes keeper PID/start, nonce, source, service lifetime, session and root inode. `intent` distinguishes actor, receipt, token and full scope. Registration and semantic native return carry separate durable flags. Latched faults and uncertainty cannot be erased by later apparent success. Actual kernel/source tests must discharge these abstractions before product authority is claimed.
