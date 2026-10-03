# Preserved terminal-report gap

Activation committed in the native authority and the backend supplied fresh
snapshots, but the stable-order UI did not change its final rows. The DOM-only QA
reporter observed neither the transaction attribute nor native message delivery,
so the original six-second assertion deadline expired waiting for a terminal
report. The failed packet, compiled inputs and clean shutdown are preserved.

V31 adds event-driven reporting on native message delivery and transaction/ARIA
mutations, keeping the same original deadline and intended GUI/recovery assertions.
This packet does not qualify the complete native GUI campaign. Stable window order
is implemented in the view but needs the accepted V31 native proof.
