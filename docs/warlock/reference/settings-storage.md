# Appearance settings storage

Implemented by [shell_preferences.py](../../../implementation/warlock/adapter/shell_preferences.py).
The native-selected store directory is `$XDG_STATE_HOME/warlock`, or
`~/.local/state/warlock` when unset. The frontend cannot supply a storage path.
The directory is private and operations share `taskbar.lock`.

| File | Current behavior |
| --- | --- |
| `settings.json` | Validated active appearance settings, schema 1 or 2 |
| `settings.schema-1.json` | Exact original bytes retained before an explicit schema-1 upgrade; never overwritten by the store |
| `settings.*.tmp` | Private temporary publication files; not authoritative settings |

Schema 2 contains a canonical nonzero revision and values for `theme`,
`textScale`, `effectsOff` and `reducedTransparency`. Themes are `night`, `dawn`
and `high-contrast`; scales are 100, 125, 150 and 200. Both flags are strict
Booleans. Unknown fields and schemas are refused without rewriting the file.

Schema-1 reads supply false defaults for both flags in memory. Reading does not
upgrade the file. An explicit changed schema-2 save with the current revision
first persists the exact schema-1 original, including its formatting. The store
syncs that file and its directory before creating and atomically renaming the
new active file. Stale revisions, invalid proposals and no-op saves do not
initiate migration. Later schema-2 saves retain the original backup.

`Saved` reports a completed save and durability barriers. A failure before active
replacement raises an error and leaves the old active file. Failure of the final
directory sync after active replacement returns `Unknown`; read back the actual
state instead of automatically replaying the write. It does not promise rollback.

Backup conflicts, symlinks, shared files and unexpected hardlinks are refused.
FIFO paths are opened nonblocking and rejected as nonregular storage. An
interruption between backup-link publication and temporary-name removal can
leave a two-link original: both original bytes and the old active file remain
recoverable, but subsequent upgrade attempts refuse. Automatic cleanup/recovery
of that condition is not implemented; do not bypass the hardlink check.

The [initial recorded checks](../../../implementation/warlock/qa/evidence/settings-migration-20261030/LIMITS.md)
exercise the actual store with temporary files and injected syscall failures.
[Further verification](../../../implementation/warlock/qa/evidence/settings-migration-verification-20261030/LIMITS.md)
adds eleven abrupt process-exit/reopen boundaries and a source-correlated finite
Quint model with 29 explicitly selected named tests and five bounded safety
samples. These are not physical power-loss experiments or native settings journeys.
