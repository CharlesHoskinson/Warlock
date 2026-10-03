# Coherent taskbar action projection

Implements typed Elm grouping of native root/child window families, observed focus,
application hints and ordinary-workspace availability. Primary actions are activate,
restore or minimize for one family; multiple families require a labeled picker.
Picker selection activates or restores, including an already active family. Empty
application hints remain separate anonymous families. The zero-window pinned-launch
rule is modeled only: catalog resolution, pins and launch effects are not implemented.

Displayed button callbacks carry binding, output generation and native facts revision.
Stale callbacks and duplicate Pending actions emit no effect. An explicit malformed
replay stamp cannot fall back to a current scope. The adapter brackets snapshots with
facts and refuses raced membership/application/minimized projections; snapshot and
facts revisions are separate namespaces. Native endpoint admission rejects nonfinite
geometry, malformed workspace identities and capability bool/integer aliases.

Verification: actual Elm Main/Replay/Shell compiles, 64 retained effects/activation/
recovery checks, 14 displayed-scope checks, 87 family/decision checks and 26 actual
Python endpoint/join checks. Quint runs 12 explicitly selected named scenarios and
1,000 invariant samples of up to 40 steps. Two model syntax failures and one Elm
annotation failure are preserved with their frozen sources. A fresh exact-ABI plugin
build passes; this version has not been loaded or tested against real windows.

The existing Main view remains an action-control harness. A production taskbar with
catalog icons/pins, picker UI and native popup/input lifetime is the next integration.
Application hints are not qualified desktop catalog identities. Complete canonical
paint/input scene, cross-workspace navigation, physical outputs/devices, presentation,
GPU/WebGPU, accessibility/IME, human UX and release remain open. No requirement or
whole sprint is accepted by this bounded slice; the user's desktop is unchanged.
