---
title: "Shortcut draft loss reproduced on unchanged production reducer"
source: "Root protected Desktop/ShortcutPreferences baseline and independent result read"
type: notes
ingested: 2026-10-29
tags: [warlock, draft, first-use, baseline]
summary: "A real compiled baseline has ten positive controls and exactly five expected preservation failures; model and fix remain pending."
---

The source-derived DEBT-05 is now reproduced by the actual compiled Desktop/ShortcutPreferences replay, before any production change. Report SHA-256 is `a6bc101e7fa683b5027759477f9bb640791db26c62c30b8da71039b93b7eacb3`; `baselineWitnessValid` is true and overall `passed` is false. Compile and replay commands exit zero; fifteen checks execute with ten positive controls and exactly five expected failures: `sameRevisionRetainsDirty`, `reopenRetainsDirty`, `invalidInventoryKeepsIntentAndBlocksReady`, `changedRevisionKeepsLocalIntent`, `unknownMismatchStaysPending`.

The unchanged production reducer is `d9196adaae768e57e2531b78ad2cd8fd22a2a81ad952d27c7c88d0fc72da8322`. The public baseline worker is the original private witness with module-name change only and no future `.conflicts` field. Binding/request rejection, live read reachability and no read-issued write controls distinguish real contract failure from a non-admitted fixture. Root retains raw output/source hashes; no private report tree is copied into this wiki.

The planned correction preserves dirty intent across same-revision reads, uses explicit per-route conflict reaffirmation for changed stored choices, invalidates writes on read failure without dropping local state, and reconciles Waiting/Unknown only against the required stored/live facts. A stale write receipt must not roll back a newer basis. These contracts and the local model are still under refinement/validation; no production fix or model correctness is claimed by this note. Current native shortcut-admission model stays unchanged.

This is a local production-replay defect, not proof of erased disk preferences, automatic native binding restore, unsaved draft survival across a host crash, native guidance/AT success or whole UI020 acceptance. The original full goal remains active. Sol performs source/report/document review only, no QA or public reducer/model edit.
