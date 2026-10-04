# Existing GTK standard state request path

Held253 already implements targeted `maximize A|C` and `unmaximize A|C`, using
the actual GTK window APIs. Held257's Actor accepts those operations. No fixture
extension or new command is needed for the standardGTK portion of GTK02.

The protected CPU proof compiles the extracted production state-dispatch body
and actual command header against instrumented API boundaries. It executes all
four operations for A and C, absent-owner refusal, and applied wrong-state and
wrong-owner controls. This proves which API is requested, not its asynchronous
native effect. The emitted `requested-state` record is expressly not completion.

Native GTK02 must join the exact current actor/role/resource with actual standard
xdg_toplevel configure states, ACK/buffer, observed GDK state, native geometry and
pixels, then unmaximize and verify ordinary restoration. Broker geometryEffect2
capability refusal remains a separate test; it cannot skip standard GTK behavior.
Geometry constraints, CSD transforms, drafts and identity remain required.

No GUI or installed configuration is changed. Full GTK02/native acceptance is
false until the complete native journey passes on the selected owning tuple.
