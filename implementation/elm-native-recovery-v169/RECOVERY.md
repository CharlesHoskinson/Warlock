# Native renderer-failure recovery prototype

On a renderer failure the host quarantines all script-message ingress, closes the
popup grab, cancels/drains I/O and ends the backend normally. Existing per-output
GTK layer bars retain their48px reservation. Dead renderer widgets are replaced
by trusted native text and a Restart button. No native window effect can originate
from this state. SIGTERM/SIGINT cancel recovery. A native button requests exit3;
it does not accept a renderer command or execute a shell command.

A supervisor must treat exit3 as an explicit restart request, bind a fresh backend
and coherent Elm snapshot and refuse retired packets. This prototype directly
qualifies the GTK button/request and fresh host launch in private QA; production
supervisor and keyboard-only/recovery AT routes remain required next work. Output
hotplug while in recovery, pending-effect reconciliation, restoration transitions
and atomic workarea preservation during the actual restart remain separate gates.
No renderer failure can restart the compositor or close application windows.
