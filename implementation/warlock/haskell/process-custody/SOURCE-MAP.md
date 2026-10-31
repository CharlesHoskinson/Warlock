# Source correspondence

The integrated selected descriptor core and its fixture sources are byte copies of the qualified CPU composition:

- `src/Warlock/Capture/Process/Internal.hsc`: SHA256 `838cce25e8b8cc8aea8ffc686e8bd877c535355e7bbc6a09e5a2dca517170ceb`.
- `src/Warlock/Capture/Process/Owner.hs`: SHA256 `3f02dc906eb9ce2490821d6e09b131ba019e09d19707db053ba9980fccc89123`.
- `src/Warlock/Capture/Process/Whitelist.hsc`: SHA256 `2795215b7abbadf6bf1e836f1164c5925549a59555853f32c64438866c88deea`.
- `fixture-selected/Main.hs`: SHA256 `ddb77f498858d132315f2768854e7e74a78fbf18b7f081cf49191a1e7d3806de`.
- `test/SelectedFD.hs`: SHA256 `5664dd7ebf961d90786c249e68c786a1872231bc78cdb4ad55c32288a8875ad1`.

The core derives from `selected-fd-shadow-fix-root-v17`; Owner and Whitelist derive from `terra-1-owner-whitelist-integration-v16`. The root derivative changes only a shadowed local parameter. The selected child derives from `selected-fd-child-root-v2`. Lease and Transfer retain their prior v12 implementations. The public facade remains opaque; the descriptor fixture entry point is internal.

`qualification.json` records the fresh package build and actual internal, public and selected descriptor suites with package-built children. Earlier source and assembly receipts remain historical and are not transferred to this assembly. The eight selected controls cover selected identities, ambient file/socket exclusion, parent flags, failed-exit diagnostics, duplicate and count refusal, expired budget and retained post-publication quarantine. They do not establish every fault, selected-ticket composition, automatic recovery, arbitrary GUI dependencies or native acceptance.

The implementation targets Linux/glibc and pins process 1.6.19.0 because it uses the reviewed internal ProcessHandle constructor. HANDOFF.md preserves the original pre-integration proposal. SHA256SUMS records current files; it does not confer source provenance or redistribution rights.
