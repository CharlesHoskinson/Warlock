# Reviewed native QA helper sources

This additive package contains the completion-aware virtual pointer source, exact two-output kiosk shell source patch, private configuration header, fresh tuple validator and two-output host adapter. It does not replace existing runtime sources, native reference records, private parent verification, scope/cleanup or IPC EOF and peer-identity handling. The original completion framework patch is retained as review context only; it embeds historical task paths and must not be applied as a product patch.

`inputs-lock.json` is a frozen input list derived from existing build and provider reports. A reviewed caller supplies its SHA-256 independently; a lock does not authorize itself. Output must be a new empty private directory outside the repository. Under the existing protected QA launcher run:

```sh
python3 -B qa/native-runtime-helpers/build_helpers.py --repo /absolute/repository --output /absolute/private/empty-output --lock-sha256 REVIEWED_LOCK_SHA256
```

The caller independently reviews and pins the resulting `report.json` hash. The exported `verify_build(report_path, report_sha256, lock_path, lock_sha256, repo, package)` checks all pinned inputs, generated source, output files and report disposition. Pass a callback invoking this function to `two_output_adapter.wrap(existing, verify_build)`; the existing reviewed adapter must still check parent foundation, helper ownership, private process cleanup, sockets and complete EOF protocol. The package does not launch any compositor or load any module.

The current lock depends on repository paths `window-integration-qa/private-weston-host-v2/primary/weston-15.0.1/`, `window-integration-qa/private-weston-host-v2/prefix/usr/`, and `installed/home/.local/share/hypr-window-controls/qa/` plus exact host headers, tools and libraries listed in the lock. A fresh checkout missing any of these or a host with different hashes requires independently reviewed replacements; it is not yet a generally portable build. The output module embeds build paths and is not asserted bit-identical across output directories. A build pass is CPU evidence only, not native ABI or GUI acceptance.
