# Private startup evidence / first failure retention

This fresh fixture-only revision preserves frozen V1 and failed attempt1. The
runtime-only native SO, native policy/fence/ABI, pointer cases and all underlying
host/AQ libraries are unchanged. Complete campaign scope is unchanged.

Actual startup needs the exact owned compositor output, IPC peer/socket/commit,
AQ mapping and mandatory-parent/configure markers before clients or policy.
Current Hyprutils file logging uses a buffered ofstream without flush per line;
waiting for its file tail is not a correct live oracle. Enable stdout logging in
this private Lua only; primary logger println+fflush makes each actual line
observable. Inspect actual owned child stdout and Weston log with bounded wait.
Aquamarine source sends ACK before lifecycle acknowledgement/announcement and
actual WAYLAND-1 publication. Require configure marker and real published output
alongside the unchanged ABI, mandatory library mapping and healthy diagnostics.
Never substitute an archived later ACK for missing live startup evidence.
Archived full transport gate remains required after normal teardown.

A first startup/scenario error is immutable in the result report. Later cleanup
or transport errors are appended with stage/traceback and never replace it.
No receiver may exist when startup fails: cleanup must accept None without new
failure or native input. Preserve complete owned host evidence on all errors.
Output prints only bounded counts/phase summaries/report path+hash/error; full
maps, exact state/catalog snapshots and detailed source/packet evidence stay in
private0600 report artifacts. Native launches still require root's exact grant.
