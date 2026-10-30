# Current compliance identity declarations: bounded scope

Source/evidence review only; no QA or edits. Correcting stale current identity declarations is appropriate. It must not change unresolved licensing, redistribution or notice-applicability status, waive inventory checks, or rewrite historical evidence.

Actual qa/runs/offline-reproducibility-1793327808907331096/report.json records a PASSED namespace probe (exit0, distinct net/mount/PID namespaces, blocked parent network socket, read-only input, hidden host source, core1). The later capture phase fails at the stale native/shared-host.c provenance digest. There is no capture lock, buildA, buildB or distributable comparison. Calling this a probe failure would be inaccurate; calling it original DEL004 completion would also be inaccurate.

Read-only current catalog scan finds14 stale provenance rows after the integrated release_tuple change:

* native-generated-host: native/shared-host.c.
* warlock-generated-elm-assets: Announcement.elm, Desktop.elm, Main.elm, OutcomeAnnouncements.elm, OutputController.elm, Presentation.elm, Shell.elm, ShortcutPreferences.elm, SurfaceRenderer.elm.
* warlock-web-assets: assets/context.js and popup-adapter.js.
* warlock-adapter-sources: adapter/recovery_profile.py and release_tuple.py.

There are also two new Elm modules absent from generated-assets provenance (AnnouncementMessage.elm, SurfaceSnapshot.elm) and two newly shipped adapter files absent from adapter ownership/provenance (current_build.py, current_native.py). No obsolete adapter mapping was found. Updating only the stale digests would therefore leave incomplete declaration inventories.

Use current reviewed composition159926... and frontend65b909... as the expected artifact identities: all19 current assets, selected hosta6b0f0..., unchanged core/authority/Aquamarine and their exact alias. Update expected payload hashes and actual project-source/adapter provenance from the reviewed current files, not by approving whatever a later build emits. The builder must still require rebuilt host/all19 asset equality and exact ownership. If an actual later artifact differs, preserve the failure; do not rebaseline catalog hashes merely to pass it.

Catalog provenance is repository-relative and each reference is independently hashed. Preserve old catalog bytes, old native-tuple-20261028.json and prior manifests as immutable history; a new repository-relative copy/reference to the exact current composition may be added with its known digest and explicit scope. Do not rewrite the historical tuple or label its old generated assets as current. Changed current provenance rows may point to current source bytes, with old declarations retained as historical catalog/evidence, not as live stale-path checks. Keep existing component IDs/categories/scopes/contains relationships and notice bytes/hashes intact; add the actual new files under their existing project component owners. No invented license or notice decision follows from a hash update.

The existing production compliance behavior is decisive: release_compliance.review rejects every unreviewed redistribution disposition and absent reviewed notice-applicability disposition, even when every file hash matches. package_compliance writes the actual compliance report and blocks before archive creation if review.ok is false. Keep those existing rules unchanged. Current catalogs deliberately contain unknown statuses; correcting identity declarations can unblock capture but will not by itself make an approved distributable. This is an expected remaining gate, not a reason to mark unknown as reviewed or bypass compliance for a passing package comparison.

Actual clean offline host/frontend rebuild and two-package DEL004 comparison remain unproven. A subsequent first-build compliance refusal would be retained release-blocking evidence, not an invented second build or matched distributable result. No native UI/AT trial is needed to update these metadata declarations, and the stopped pin/top/New instance work stays stopped.
