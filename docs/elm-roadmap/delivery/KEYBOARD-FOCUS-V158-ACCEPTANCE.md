# Keyboard focus and capability cancellation

Frozen AQ155 changes only Wayland.cpp relative to AQ138. A current keyboard enter
on an owned parent output permits later key/modifier events without inventing
presses from the supplied held array. Leave clears private focus/key/modifier
records before callbacks and cancels recorded keys without retiring devices.
Capability removal cancels before keyboard-vector retirement. Actual callbacks
retain matched devices and the backend across their signals. A private surface
index is forgotten on output destroy/destructor; public headers and every prior
AQ138 exported symbol survive the complete Release library build.

Actual extracted constructor callbacks pass28 checks/eight compiled controls;
actual key admission/cancellation/destructor pass2737/seven; pointer helper152/five;
transport replay63/seven. Total2980 C++ check executions and27 compiled controls.
Constructor callbacks use a typed protocol adapter plus actual Hyprutils shared/
weak ownership and signals, not a live Wayland server. The actual capability
backend-retention body is compiled/source-reviewed; its retirement helper is
executed separately. The transport adapter uses typed no-op cancellation stubs.
Quint passes16 explicitly selected scenarios,1000 traces of at most40 steps and10
typechecked controls. It models one keyboard and two abstract keys, with no C++
callback, multi-object, 768-slot or modifier refinement claim.

Both original152 AQ138 native cases stranded real A/Shift Linux30/42 input and
XKB38/50 shortcut records plus Shift modifier1 for the original six-second
observation deadline. Capability removal retired only the keyboard; focus leave
retired no device. Both had normal cleanup. Their unchanged native runners on
AQ155 now pass38 checks each: exact single GTK releases, empty owning Core input/
shortcut ledgers, zero modifiers, preserved pointer delivery/output, restored
keyboard and a fresh physical key pair, exact process/socket identities, ordered
normal shutdown and observer unload. Parent fixture151 uses owning Weston15 APIs
without pre-fault releases. Native observer132 reads actual Core public state.

AQ155 regression executions: parent-loss37; A/Shift/both masks114; input159;
geometry96 including seven pixel stages; unheld loss26; pointer35. With the two
new cases,543 native check executions pass with cleanup, actual mapped AQ155 and
owning Core89/plugin90 where applicable. These are repeated check executions,
not unique requirements or full roadmap acceptance. Historical scope strings in
unchanged runners refer to earlier baselines; frozen descriptors and process
maps identify the current library. New focus/capability cases cover both keys
held together on the private seat, not multiple physical keyboards or all masks.

Retained failures:153 mutation matcher failed after its model scenarios/traces
passed;154 owning compilation rejected private output-field access although its
typed callback tests passed.155 corrects this without public-header changes.
155 preparation attempt1 records an observed SyntaxError and missing-runner
exit2 summaries; raw stderr was not preserved.157 geometry copy was one directory
too deep and failed its adapter import before any native launch/report; direct
159 copy preserves the runner bytes and passes. All failed source/evidence roots
remain archived unchanged. The unchanged accepted157 siblings are retained.

Hosted goal is active. Next qualify AQ155 with the shared Elm GUI recovery tuple
(Core89/plugin409/current422/runtime420/427) in a fresh independent derivative;
preserve its owner's original geometry08/09/10 work. Native multi-device, physical
hardware, GPU/WebGPU, accessibility/IME, resource/user journeys, full S01-S16 and
applicable C00-C06, reversible deployment and rollback remain open. No installed
or main-desktop change was made. Bounded native acceptance is not release acceptance.
