# Haskell process custody

Status: the standalone package passed a fresh offline strict build and its focused internal and public test suites under protected CPU QA with an owned child cgroup. See `qualification.json` for exact evidence and limits. This package contains the v13 process core and unchanged v12 lease/transfer sources, with an opaque caller facade. These focused tests do not transfer the historical 66-control result or establish namespace, native GUI or original-scenario acceptance. `HANDOFF.md` preserves the author’s pre-execution proposal.

## Tutorial

A caller may create one `Owner`, construct an absolute `AdmissionDeadline`, and use `runTool` for the exact supported pinned tools. Inspect `status` after each operation. `Quarantined` is retained custody, not successful cleanup; keep the owner alive and hand it to the trusted supervisor. Do not drop a quarantined owner or assume a close proves process retirement.

## How-to for root

Review the exact files and original qualification, then use the protected launcher and commands in HANDOFF. The fixture executable is built from this package; pass its actual `cabal list-bin` result to the internal test and record its resulting hash. Root must provide external bounded child containment for any test failure. Do not substitute system paths or a previously qualified fixture hash.

## Reference

The public module exports abstract `Owner`, `HeldExecutable`, `TransferTicket`, `SelectedSpawn`, `Session`, and `AdmissionDeadline`. `runTool` accepts only its existing fixed tools and verified hashes; selected use needs an already issued lease and ticket. Neither raw FD, issuer, fixture hook, owner mutations nor transfer owner tokens are exposed. `deadlineAfter` constructs the existing single absolute admission budget; cleanup may exceed it to retain custody.

## Explanation

Trusted integration must co-build a separately reviewed issuer module inside the package boundary, using the held resolver's exclusive verified descriptor and transferring close ownership exactly once. T4's channel/Pair binding and resolver issuer are not implemented here. The trusted component can import the hidden Lease and Transfer internals only within that reviewed package component; arbitrary package clients cannot. Do not open these modules in exposed-modules as a shortcut. A potentially alive quarantined child needs a real persistent supervisor; the component alone is not one. Original scenario, native and release claims remain open.
