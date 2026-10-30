# Settings migration verification

Original ELM-DEL-015 scope: versioned validated appearance schema, atomic writes
and exact pre-migration copy before the implemented schema1-to2 upgrade. Existing
baseline/regressions/source review remain immutable in
[the first packet](../settings-migration-20261030/LIMITS.md).

New actual production-store evidence: 56 checks across 11 deliberate abrupt child
exits (os._exit(85), no Python cleanup) at file sync, backup link/unlink,
directory sync and active rename boundaries. A normal completion exits 86 and
cannot satisfy the cut assertion. Fresh Store reopening yields complete expected
old/new valid state; original active or backup bytes remain exact. Two-link
publication interruption refuses later save; other pre-rename cuts allow explicit
retry, and stale post-rename proposals refuse. No automatic migration/replay.
Protected scope 49d54b4f2b0a4df1bd998dbf8107695a,
invocation 5f57b278dd3a4b72b1294c8600e70912, exited 0.

The corrected finite model passes 29 explicitly selected named tests, init and
five bounded safety samples (1000 traces each, max 30 steps, seed 20261030).
[Root model review](model-review.md) explains source correspondence and the
retained unexecuted v1 fixture defect. Protected model command identities and
hashes are recorded with raw outputs. No exhaustive or universal proof claimed.

An abrupt process exit is not hardware power loss. fsync/rename semantics and
storage behavior are assumptions; these observations do not prove every possible
failure, arbitrary JSON/concurrent edits, automatic two-link cleanup, native
settings journeys, accessibility or release/deployment acceptance. Postrename
Unknown is not a failed migration that rolled back.

Independent original-oracle disposition and exact canonical hashes are separate
from these observations. The original 242 requirements/417 scenarios remain intact.
Diataxis: storage reference updated; existing verification how-to remains correct
and its protected command route is unchanged; source-navigation tutorial and
ownership explanation remain unaffected by this verification-only increment.
