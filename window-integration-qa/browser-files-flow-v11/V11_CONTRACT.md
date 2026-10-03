# Browser V11 metadata diagnostic

V10 retains the strict deleted BrowserMetrics failure despite its local-memory
configuration request. V11 records raw metadata before the unchanged mapping
authority decision. It never grants mapping authority or supplies an exception.

Observe only the exact owned root browser PID/start/UID/QA scope/frozen executable
and private profile. Retain captured browser mappings, matching device/inode FD
inventory and full stat, readlink, bounded raw fdinfo/mountinfo, parsed flags and
errors, plus fresh maps and exact lifetime after observation. All metadata is
attached before risky reads so a failure cannot discard the cause. Guard drift
refuses. Absence, duplicates, missing FD and unexpected mode are observations;
none prove authority. No new command, subprocess, browser input or cleanup path.

The existing seven Quint authority and focus models and all original actual input
oracles remain unchanged. CPU/kernel tests must demonstrate exact deleted inode
observations and retained read/lifetime failures. Only later actual evidence plus
source/formal review can justify a separately specified runtime data contract.
No main GUI/restoration/config writes or production/browser-source equivalence.
