# Committed shell appearance preferences

Settings now offers **Disable soft effects** and **Reduce transparency**. Save
applies both through the existing immutable Elm preference transaction and native
private store. Unconfirmed saves cannot replay; draft flags do not change the
rendered appearance. Effects-off removes soft shadows while retaining solid focus,
active/attention edges and selected-state contours. Reduced transparency uses
opaque shell backing. Toggle buttons expose their draft state through aria-pressed.

A real native keyboard journey saves both flags, preserves the exact Saved receipt,
rejects an otherwise valid scale-77 proposal, restarts the entire host and observes
both stored flags in the bar and popup. The new controls remain named, keyboard
reachable and visibly painted with a solid focus outline. The owner inspected
[the native restart frame](popup-settings-after-restart.png). Normal owned-helper
and client exit, plugin unload and private cleanup pass. The original nine-surface
keyboard journey also passes with zero pointer injection. Its exact fixture is
recoverable from nine-surface-driver.patch and the recorded owning snapshot/hash;
only the later supplementary Settings observation differs from the current runner.

The initial native pass did not isolate invalid scale: its schema-2 proposal also
omitted flags. It is retained with that limitation and is superseded by the valid-
shape scale-77 refusal in native-report.json. The later supplementary capture
failed before ordinary Tab revealed the successor; the failure is retained.
No programmatic focus repair, changed deadline or window-effect retry is used.

Schema-1 settings are read with safe false flags without rewriting the file.
Identical saves do not migrate it; an explicit changed save writes schema 2 under
revision CAS. Legacy writes cannot discard the new flags; future schema 3 stays
preserved. Actual store tests cover restart, strict Boolean values, invalid scales,
concurrent/stale writes and Unknown after rename. The owning host separately admits
strict schema-2 values; its previous malformed/legacy request tests remain intact.

Component rendering checks cover all four flag pairs in Night, Dawn and High
Contrast at 200% text: real keyboard targets, solid focus, aria-pressed, suppressed
shadows and opaque backing. These are browser observations, separate from native
pixels. Native AT, every surface/profile/output and independent original acceptance
remain open. This delivers the shell preference route for WARLOCK-LAYER-010; the
full layered-window token, window-decoration and accessibility contracts remain open.

## quint-llm-kit model handoff

The additive layer-appearance.qnt leaves the original settings.qnt unchanged.
Flags 0/1/2/3 abstract neither/effects-off/reduced-transparency/both. The single
transaction projection models callback ordering at atomic state boundaries:
edit/save/delivered/lost/compete/refuse/refresh/staleReceipt map to Settings.edit,
Settings.propose + Desktop.SaveSettings, Settings.receive, the store's CAS and
post-rename Unknown, and Settings.observe through explicit read reconciliation.
Stored/nativeRevision correspond to the private store; draft/applied/knownRevision
to Elm draft and observed snapshot; request/writes count explicit submissions.
Confirmed records the last correlated committed or explicit-read appearance.

Five explicitly selected named tests, positive witnesses (543 bothCommitted,
454 unknownHeld, 436 staleRefused) and 1,000 sampled safety traces of 30 steps pass.
The model has no native pixel, timing, input-focus, schema-codec, transport-refinement
or UInt64 overflow proof; actual Elm/store/host/browser/native evidence covers its
separate boundaries. No original acceptance property is weakened.

See [manifest](manifest.json), [compiled report](compiled-report.json),
[native report](native-report.json), [browser report](browser-report.json), and
[model report](model-report.json). Requirement/release acceptance is still partial.
