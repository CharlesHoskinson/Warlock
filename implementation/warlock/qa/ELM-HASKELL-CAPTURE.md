# Unattributed capture receiver (development QA)

This receiver is a development tool, excluded from the production runtime.
Warlock-authored production remains Elm and Haskell. A captured image does not
establish rendering attribution, native interaction or original-scenario acceptance.

## Reference

`elm_haskell_frame_receiver.decode_frame(stdout)` accepts one complete UTF-8 JSON
line from the reviewed capture bootstrap. The frame is bounded below 4 MiB with
65,536 bytes reserved, schema 1, duplicate keys refused, canonical base64, and an
image receipt with exact positive byte length and lowercase SHA-256. Metadata has
bounded depth and size. Unattributed, unobserved and unchecked-deadline flags must
remain unchanged. The returned facts always retain `nativeAccepted=false` and
`renderObserved=false`.

For a hash-matching payload, the receiver separately checks PNG chunk framing,
CRCs and the expected 800×600 header. It does not decompress pixels. A malformed,
hash-matching PNG remains available for diagnosis with `containerCRCVerified=false`.
Invalid JSON, hash mismatch or oversized frames raise `FrameError`; the caller
must preserve its original process observation for diagnosis.

`archive_frame(stdout, parent, name)` creates a fresh archive below a trusted,
UID-owned mode-0700 parent. Producer filenames never determine output paths.
Files use fixed names and mode 0600, exclusive creation, bounded writes and fsync.
Existing names and symlinks refuse. Partial archives can remain after I/O failure;
never retry the same name. Each owned descriptor is closed once; operation and
close failures are retained together. The parent and its ancestors require no
hostile same-UID mutation during use.

## How to use in a protected runner

Retain the entire bounded `ToolObservation`, including stderr, process exit,
containment and custody. A nonzero exit must not discard captured stdout. Pass
its complete stdout bytes to `archive_frame` using a newly allocated evidence
name. Keep process-lifecycle and native-scenario judgments separate from receiver
facts. Run through the existing protected QA/native launchers; this module grants
no authority to bypass them or the original stop history.

## Verification and limits

Protected CPU evidence from 31 October 2026:

- Eight receiver tests cover large payloads, malformed/duplicate JSON, changed
  status flags, size/hash/base64 corruption, fixed paths, permissions, replay,
  symlinks, partial writes and injected descriptor-close failures.
- The actual Haskell Export encoder produced a 1,921,772-byte frame containing a
  deterministic synthetic 1,441,103-byte PNG. Its child exited 7. The production
  process wrapper retained exact stdout; the independent receiver verified and
  archived the same SHA-256. The owned cgroup was empty and removed without force.

Evidence is retained under the local preparation directory in
`frame-receiver-controls-1793426517716419202/report.json`,
`large-frame-pipe-compile-1793426528720597747/report.json`, and
`large-frame-pipe-controls-1793426560084374827/report.json`.
These establish bounded output handling, not a real GUI capture or rendering oracle.
