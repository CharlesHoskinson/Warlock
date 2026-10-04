# Actual276 privileged-drain failure

All 27 recorded diagnostic checks passed again, including independent roots, actual pixels with unchanged lastCommit, orderly GTK exit, empty native clients and plugin unload. Final activation cleanup failed and remains unaccepted.

Documents captured a live owned descendant PID3672157/start11646706 with real UID1000 and effective/saved/filesystem UID0, parent PID3672151. The supervisor first signalled the unprivileged primary and correctly refused to signal the privileged helper. That refusal raised in the main drain. Its error-cleanup loop called signal_active outside the protected reap try, repeated the same refusal and escaped before terminal emission. Two actual tracebacks and a journal ending at signal-identity-refused establish this control flow. The final error is an incomplete activation journal, not proof that a complete terminal wrapper stayed live.

The privileged child's executable is not recorded, so exact fusermount attribution remains unproven. Current credentials now establish the real privilege boundary; no arbitrary executable whitelist or privileged signaling is warranted. A fresh successor needs bounded wait accounting for privileged owned descendants, robust error-drain exception handling and terminal evidence on every path, while preserving exact PID/start/kernel wait statuses and original cleanup deadlines. If any helper survives or attribution fails, cleanup must still refuse.

Other raw journals completed. Captured systemd1 binfalse exit1 and GVfs cancellation are distinct classified outcomes; all are retained. No source correction, GUI or native acceptance is performed in this packet.
