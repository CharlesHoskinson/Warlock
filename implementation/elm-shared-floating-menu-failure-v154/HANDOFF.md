# Preserved native floating-window capability failure

V152 ran through the serialized native coordinator and unchanged protected
launcher on combined source380/core89/plugin90/AQ105. It reached 44 checks,
including cleanup checks, and failed `floatingMenuHasMultipleActualEnabledActions`.
Normal webview/backend exit, empty native client census and private-host cleanup
passed. Earlier tiled menu/pixel/minimize/restore gates passed in this run;
retirement and new geometry operations were not reached.

The authority target was explicitly selected by title, PID, address and original
incarnation. Its final geometry facts show floating=true, constrainedSize=true,
geometryEligible=false and maximize=false; the menu correctly retained only
Minimize as enabled. This is a representative GTK capability gap to investigate,
not evidence that the complete floating Maximize requirement is satisfied.
Do not remove the failed assertion or substitute an unconstrained client to
close the representative-application gate. An unconstrained fixture still has
its separate original geometry08/09/10 qualification duties.

V150 and V151 were unlaunched review predecessors. Their sources/preflights
remain preserved with the reasons for target/protocol/incarnation tightening.
V153 independently reviews the authority constraint policy. Any production
correction requires a fresh specification/source/owning ABI pair and original
native deadline/postcondition checks. No installed desktop change was made.

The previous turn made concrete progress by freezing and committing the combined
recovery source. This turn adds a reviewed native test and retains new failure
evidence that selects the next capability-policy investigation. Full S01–S16,
right-click, UIUX, release, deployment and rollback remain active obligations.
