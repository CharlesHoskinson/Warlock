# SurfaceSnapshot five-file proposal — SOURCE_READY

Source review only; no compile, tests, model run, native execution, or original-scenario acceptance. Compared actual current production sources to `/home/charles/.local/state/warlock-team/20261028/native-rebuild/surface-snapshot-root-v1/` proposal. The five proposal file hashes agree with `proposal.json` SHA-256 `20635d2359efa76735d2193dbb90342f3a8948c0046db3109802bffa18f6efe1`:

| Proposed file | SHA-256 |
|---|---|
| SurfaceSnapshot.elm | `58298ea43fffba3da6bcc64f1456b47bcde3607d476ef99465be0c98c2b433d7` |
| SurfaceRenderer.elm | `f6c653573c1b73b32df132ada5033a1e34aa2cfa1a2dcbb42be4320a4a98a7b8` |
| OutputController.elm | `aaf1729287ff61595a237201b261e7c1ce11c8f2353c620171f48aff99d86f38` |
| Presentation.elm | `8c635b330641c4c06895357bdaee430b8eeed9b8ae88a83742f703c9f23a5dd6` |
| Main.elm | `7f5ddbe6fedf775e143b684ec60c9bfbdf15606414ed4fafc2c5553b514821c2` |

Baseline actual source hashes: renderer `48e03f50fd509ea0e42e23d7a1aa26396122350ab824c8dc179952b5bfd28c63`, output controller `8da2227997dda10570707c456df8b00fcc000291c66a8ec2a48e8d5321cee8dc`, presentation `8c3463230d93b768f48784a37ae9e4da7a225defa6f209b3100258af5196c0e9`, Main `6d797e72117cb0e057638eca1c29bcec8c1fa536221bccd605de48978458cf19`.

The old renderer span `strict` through `action` exactly matches, byte for byte, the proposal's Snapshot span; it retains strict fields, optional legacy defaults, bounds, identity/DOM uniqueness, mode/checked/focus-only constraints, UInt64 behavior, normalized encoding, action envelopes and the existing `pendingQuery` overlay. The old `viewWithPreview` body is byte-identical after replacing its old private constructor pattern with `SurfaceSnapshot.details current`. HTML, DOM event decoders and inline query/preedit packets are otherwise untouched. No stronger raw duplicate-key detection or native atomicity is asserted.

`OutputController` and `Presentation` differ only by replacing the `SurfaceRenderer` module name with `SurfaceSnapshot`; therefore their admission comparisons and local edit/query logic remain textually unchanged. Main differs solely by removing its unused renderer import; port, update, timer and subscription ordering are unchanged. Renderer retains the prior exposed function names and delegates each to the new module; its `type alias Snapshot = SurfaceSnapshot.Snapshot` makes facade callers use the same value type. The proposed Snapshot constructor is not exported; `Control` and `Details` records are visible, but cannot construct a Snapshot. Existing `pendingQuery` remains a deliberately available display-only update, not an arbitrary snapshot builder. No type mismatch or second policy was identified by source inspection; Elm compilation remains necessary.

Pure `SurfaceSnapshot` imports JSON, Set, Settings and UInt64 only. Current `Settings` imports Json and UInt64; `UInt64` imports Json. No proposed cycle or native/Html dependency enters that new module by those inspected edges. The refactor only removes direct renderer imports: `OutputController -> OutcomeAnnouncements -> Announcement -> SurfaceRenderer -> Html` remains, because `Announcement.elm` combines message type and HTML rendering. It is a separately scoped next seam, not solved by this five-file proposal. Do not modify it to inflate this slice.

No code moves into the host, no authority/ABI/custody/port clock changes, and no claim that `shared_commit` later ledger/mutation/open/queue stages are native atomic. Root should still exercise contract/property sequences against actual production paths with fixed seeds and preserved counterexamples, original malformed/valid/disabled/stale/lease cases, IME/local-edit and preview semantics, and inspect the selected protected build/replay tuple. Original UI-004 taskbar-group, UX-005 exact member and UI-016 preview oracles require their own appropriate native/AT evidence. Current 242/417 scope, failed diagnosis, deadlines, unknown/no-replay and frozen proofs remain binding.
