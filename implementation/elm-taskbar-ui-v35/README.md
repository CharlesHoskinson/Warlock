# Grouped Elm taskbar and picker prototype

Main now displays native window-family groups and active state. A single family
activates, minimizes when active, or restores when minimized. Multiple families
open a labeled picker; selection activates/restores and never minimizes the active
family. Buttons have native HTML keyboard behavior, focus outlines and labels;
Escape closes the picker when focus is inside it. This is a bounded action-control
prototype, not the final native taskbar/popup surface or complete keyboard UX.

TaskbarShell is a pure typed controller. Displayed binding/output/revision guards
reject stale group actions; separate monotonically increasing picker generations
reject selections and close callbacks from a previous picker. Refresh, native
revision changes, disconnect and pending actions retire the picker. No effect is
replayed automatically. Catalog/icons/pins, zero-window launch and cross-workspace
navigation remain unimplemented.

Optimized Main and the existing native WebKit host compile and host self-tests
pass. The actual Elm controller passed 20 picker tests and 78 retained/scoped
shell/effect tests. One worker flags-annotation failure is preserved with frozen
inputs. QA DOM reporting now matches groups/picker rather than old row controls.
No native GUI campaign has run for V35; actual pointer, keyboard focus transfer,
accessibility/IME, popup/input lifetime and complete UX/release remain open.
Hardware acceleration evidence belongs to prior V4; this host build adds no GPU
or WebGPU acceptance. The live desktop has not been changed.
