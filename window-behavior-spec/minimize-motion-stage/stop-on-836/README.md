# Guarded idempotent stop on accepted836

Helper-only candidate; no provisional route code and no QML/core/wrapper changes.
SHA2566d9a21114cfc9d8ed4a4669bb4c1a585375abd56bf27de2783e203926dcecbaa.
`controller.diff` from accepted836 adds only the guarded24-line stop function and CLI stop branch.

Absent/refused socket with no runtime, or exclusive daemon lock + empty journal + no live PID, succeeds idle without daemon startup/recovery. Pending/invalid journal, busy startup lock or live PID without listener returns failure and preserves journal/actor. Submitted shutdown is sent once and retains normal cleanup behavior.

Formal stop_contract.qnt/test has4 named scenarios and2000 samples. test_stop.py has7 actual AF_UNIX/process cases, including existing-listener shutdown then repeated idle stop, refused stale socket/dead PID, blocked startup lock, live actor and pending recovery. Previous105 regression cases remain unchanged.

Offline runner: `python3 ~/window-behavior-spec/minimize-motion-stage/stop-on-836/check_offline.py` (112 Python +17 actual QML +3 parsers, Python/Bash syntax, previousfreeze/family/ordering plusstop models).

Root owns installation/backup and any real installed-service actor probe. No need to rerun full GUI motion for this isolated lifecycle change.
