# v626 handoff

This is a minimal startup-order derivative of v616, with no desktop installation
or native campaign. `qa/startup.py` passed 22 checks, including actual C lock
contention/success, zero post-attached startup broker lock acquisition, unchanged
frame order, restored live callback, serial scope releases and staged failure.
The unchanged public Elm replay driver passed 51 checks.

The final protected build is selected by `qa/current-build.json`. The first build
passed compilation but captured the copied stale pointer; its evidence remains
and is not selected for native deployment. The final build has no pointer input.
`component-manifest.json` validates that final build and freezes owned source,
artifacts and CPU evidence. Root owns subsequent native qualification.

The causal native diagnosis is compatible with the exact logged C failure path;
the deterministic control proves the source race is executable. Native errno was
not recorded. Treat v618 as failed, preserve it unchanged and use a fresh native
packet to test this repair with the same original deadline and oracles.
