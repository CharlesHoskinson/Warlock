# V1 failure and fresh fixture-only correction

Retain V1 attempt1 report SHA49d13f38f36fe6a2f8b0c5d314413a5c2bbcdb3318913e0ebee87dc4815cdc14.
It reached five startup gates, launched no campaign clients/phases, and retained
healthy archived parent transport plus all19 preservation/cleanup checks. The
received=None cleanup exception overwrote the first error; its exact original
exception cannot now be recovered. Do not relabel the old attempt PASS.

Primary source at the exact installed Hyprland commit initializes AQ after logger
configuration. Logger::recheckCfg enables stdout only when debug:enable_stdout_logs
is true. V1 specified disable_logs=false, leaving stdout disabled. The installed
Hyprutils0.14.2 implementation writes file lines through buffered ofstream without
flush, whereas stdout uses println plus fflush. ACK markers near the file's final
buffer can be absent from a live file read and present after logger destruction.

The actual installed-library offline probe confirms this: both live files were
zero bytes while the logger stayed alive; enabled stdout delivered the actual
mandatory marker before close. After close each file contained134 bytes. This is
source-backed evidence of the deficient live-file oracle; it does not recover the
lost exception or claim a bridge/parent transport defect.

Fresh V2 enables stdout only in the private Lua. Before clients, it checks the
actual registered child's flushed stdout and Weston log, preserves each observed
file hash/length and marker state, and keeps the strict12-second limit. Fatal
transport diagnostics fail immediately. Configure marker plus actual published
WAYLAND-1 and exact library mapping follow the primary AQ sequence: sendAckConfigure
precedes acknowledgement and monitor announcement. The independent terminal
archive gate remains. No delayed archive can substitute for missing startup proof.

First error/traceback is immutable; later failures append stage/traceback. Cleanup
accepts an absent receiver. Stdout prints a bounded summary while full evidence
stays in private files. The CLI sets process-only umask077 after scope validation.
Runtime-only SO241432e7, actual host/AQ, native fence/policy and all full campaign
case/helper bodies are unchanged. No native V2 run has occurred.

Primary sources are archived with URLs/hashes in primary-startup/provenance.json:
https://github.com/hyprwm/Hyprland/blob/efb50993780079460b0cbed1363e2166a2de1d9f/src/debug/log/Logger.cpp
https://raw.githubusercontent.com/hyprwm/hyprutils/v0.14.2/src/cli/Logger.cpp
