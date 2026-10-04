# Native taskbar projection qualification

The frozen V33 core/plugin passed 100 ordinary native checks and 131 continuous
full-redraw diagnostic checks in serial private Wayland sessions. The original V28
80/111 assertion identities are retained by configuration variant. Ten new
bracketing/application-hint pairs per run preserve actual focus, ownership,
minimized family and client-class metadata. Both runs cleaned all owned processes
and private runtimes; the live desktop was unchanged.

The frozen compiled V33 TaskbarReplay worker admitted all 20 actual native packets
and passed 120 grouping/action checks. Two root families form one application-hint
group; modal/late descendants collapse, focus resolves to its root, minimized roots
remain enumerated and picker selections activate/restore. This is action projection
only: application hints are not catalog identities; no complete paint/input scene,
presentation, taskbar GUI, human/accessibility/GPU/IME or release acceptance.
