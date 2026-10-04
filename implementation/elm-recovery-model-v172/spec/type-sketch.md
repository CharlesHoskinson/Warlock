# Recovery contract type sketch and review

State: phase in Live,Drain,Recovery,RestartRequested,Starting,Stopped; monotonic
host epoch; bridge and backend availability; bar reservation in logical pixels;
latest admitted effect epoch. Events: renderer failure; backend drained; native
Restart; shell-stop signal; fresh host launch; matching fresh snapshot; renderer
intent tagged with epoch. Only a native Restart in Recovery can request restart.
Old renderer ingress is denied during/after failure; a new instance admits only
its matching epoch after a coherent snapshot. Recovery retains48px reservation.

Reviewed boundary: no transition here models native window effects already in
flight, exact backend cancellation/deadlines, physical pixels/AT/IME, hotplug or
atomic geometry during restart. Native V170 independently checks failure-time
geometry and actual button/restart/old-binding refusal. Formal results are abstract
contract checks, not automated C/Elm refinement or production-supervisor proof.
