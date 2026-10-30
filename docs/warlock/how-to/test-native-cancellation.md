# Test the native cancellation stage on this development host

Use this guide for the strict client codec and isolated native ordering fixture. It does not enable cancellation in the normal desktop or install Warlock. You need the reviewed source, pinned machine-local core/AQ/plugin and private parent packet, an actual owned contributor record, and root's serialized QA slot. Missing these artifacts is a prerequisite failure; do not substitute the system compositor or older plugin.

## Check client boundaries

The current test source is `implementation/warlock/qa/check-cancellation-endpoint.py`. Run it through the unchanged protected CPU launcher under the coordinator's authenticated QA hold. It uses explicit native response doubles; a pass establishes strict schema/correlation checks and local client cache behavior, not socket authentication or actual native outcomes. Preserve source/tool hashes, seed, failed cases and the complete command/report before interpreting the result. The retained [executed CPU driver](../../../implementation/warlock/qa/evidence/native-cancellation-client-20261030/cpu/executed-runner.py) documents the reviewed scoped invocation and source snapshot.

## Run the isolated native fixture

After verifying the current repository entrypoint and its pinned private packet against source review, use the coordinator-provided real record path. Replace `ACTUAL_RECORD.json` and `/absolute/repo` below; do not overwrite a participant record to make the command green.

```sh
PYTHONDONTWRITEBYTECODE=1 \
  python3 -B docs/warlock-build-loop/v2/loop.py \
  --record .warlock-contributor/ACTUAL_RECORD.json native \
  --runner /absolute/repo/implementation/warlock/qa/native-cancellation-orders.py
```

The launcher must reside in the repository. It pins the reviewed machine-local fixture; it accepts no modes or extra arguments. The fixture checks the new owning compositor-only tuple before load, actual core/plugin/AQ identity, private Wayland/session bus routing, no X11/DRM fallback, independent real GTK roots, both ordering cases and actual state after late opposing operations. It stores exact terminal receipts durably before ACK and requires explicit normal exits before cleanup. An unsuccessful cleanup or assertion is a failed run even when earlier behavior checks passed.

## Read the outcome at the right scope

Inspect the actual terminal report, normal-exit statuses and retained failure history. Do not restart a live or merely timed-out observation handle. Preserve original deadlines and change a concrete demonstrated defect before retrying. The [current packet](../../../implementation/warlock/qa/evidence/native-cancellation-client-20261030/LIMITS.md) retains a failed shutdown-syntax run and its one-line correction; the successful retry does not rewrite it.

The fixture does not send physical Escape, force native Unknown, inspect native per-generation resource tokens or run the production durable daemon/Elm path. Its local wrong-key check does not reach the producer. Those original obligations remain open after a pass. Use the [protocol reference](../reference/cancellation-protocol.md) for exact fields and custody rules; older full-composition locks remain historical and cannot qualify changed native source.
