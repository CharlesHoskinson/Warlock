# Geometry observer diagnostic packet

This packet retains the V35 negotiated observer build and CPU checks, the V37 runner, the corrected V38 workspace-scoped adapter and CPU checks, and the V39 native attempt. It grants no native observer, geometry effect, menu integration, or release acceptance. No requirements are marked complete.

V35 passed 117 decoder/transport CPU checks and compiled its observer plugin against the exact V28 core and owning headers. V38 passed 132 CPU checks, including two workspaces with distinct workareas sharing one output owner, conflicting-owner rejection, and detection of the original output-scoping defect. The legacy effect endpoint remains unchanged; geometry negotiation advertises observation with effects false and no operations.

V39's retained native attempt failed `ordinary:truthfulUnsupportedGeometryAndConstraints`; cleanup passed. The real plugin was mapped, the separate observation negotiation succeeded, and ordinary identity/geometry readbacks preceded the failed constraint assertion. Maximize, restore, duplicate transitions and subsequent recovery checks were not reached and remain unqualified. The failure is preserved with its original runner, captured inputs, logs, facts, and report.

The diagnosis directory records the actual xdg-shell protocol defaults and owning header implementation. The client sends no size limits, but the owning implementation initializes maximum size to a finite default, which the observer classifies as constrained. A fresh core candidate must distinguish unspecified limits from explicit constraints; changing the fixture or relaxing the assertion would not repair ordinary clients.

The manifest records all four packet inventories and exact external build, core, ABI header, dependency, link, client and component evidence. `qa/freeze.py --verify` rechecks those hashes without launching a desktop. A successful freeze means evidence integrity only. Workarea changes, output-owner replacement, actual geometry effects, fullscreen policy, transport integration and broader native acceptance remain open.
