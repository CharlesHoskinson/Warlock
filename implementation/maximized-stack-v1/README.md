# Native floating MAX stacking correction candidate

Source-only candidate for owning Hyprland commit `efb50993780079460b0cbed1363e2166a2de1d9f` (v0.56.2). No build, compositor restart, plugin reload, GUI stimulus or deployment performed. Installed bridge reviewed read-only at `/home/hoskinson/src/hyprbars-dragend-initfix/familyBridge.cpp`; current plugin path reported by root is `~/.local/lib/libhyprbars-controls-v18.so`. Candidate adds only a final renderer-pass guard and does not emulate maximize by resizing.

## Confirmed source mismatch

Exact owning Git sources are copied under `original/` and hashed in `source-manifest.json`; the sparse working checkout is not used as the source of truth.

- `src/desktop/state/WindowState.cpp:41–64`: `moveToZ` marks only the moved window `m_allowedOverFullscreen=top`, refreshes that window's input/alpha and rotates the bottom-to-top stack. Raising floating MAX leaves previously raised ordinary float eligibility intact.
- `src/desktop/state/ViewHitTester.cpp:75–130`: floating hit testing iterates the stack in reverse and includes floating native MAX in eligible candidates. After MAX is raised, it can receive the hit first.
- `src/render/Renderer.cpp:331–440`: ordinary floating windows are drawn first, fullscreen/MAX owner next, then all eligible ordinary floating windows again. Previously raised float peers draw over MAX regardless of their stack position, even though hit testing returns MAX.
- `src/desktop/view/Window.cpp:952–979`: pin/allowed/group membership participates in fullscreen input and visibility policy. Clearing peer flags would change more than rendering order.
- Installed `familyBridge.cpp:134–157` raises an owner's intermediate/deepest modal chain after the owner; this places its dialogs after MAX without modifying input semantics.

This confirms a code path for render/hit disagreement. It does not prove that this is the only cause of the user's Brave overlap behavior; live reproduction remains required.

## Candidate change

`floating-max-stack.patch` applies to the exact original Renderer.cpp. In the final over-fullscreen pass, only when the owner is **floating** with internal native mode **MAXIMIZED**, skip ordinary peers that appear before that owner in the current bottom-to-top stack. They were already drawn below MAX in the ordinary floating pass and may still show in exposed geometry outside MAX. Keep pinned peers exempt. Preserve every existing fullscreen, workspace, special-workspace, mapped and render eligibility predicate.

The current stack is read each frame, so raise and lower both work without a new hook or peer state cache. True/exclusive fullscreen and tiled MAX remain unchanged. No allowedOverFullscreen, input blocker, alpha goal, return geometry, workspace or maximize mode is mutated. The update adds O(n) trivial checks to an already O(n) final pass, with no new IPC, process, query or extra stack traversal.

Clearing below-MAX peers' allowedOver flags in a moveToZ hook would block input and make whole peers fade, including exposed regions outside MAX; it also introduces synchronization on raise/lower/close/transfers/pin/modal changes. The renderer correction is narrower. Existing pin ordering among multiple ordinary floats remains its own acceptance topic; exemption here preserves pinned-above-MAX behavior and does not claim a complete pinned ordering repair.

## Integration boundary

This core change requires a new compositor binary and therefore a controlled compositor restart. Do not restart the user's current desktop or close drafts as an incidental step. Build/test first in the root-owned serial private native campaign. Pair the candidate compositor with a plugin built for its exact owning headers/ABI gate; absence of public class-layout changes does not waive the exact core/plugin pairing requirement.

Wrapping the full renderer method from the existing plugin cannot filter one member of its internal final pass through public APIs. Hooking every `renderWindow` call or modifying global peer flags during render would add recursion/global-state/cleanup risks and depend on private rendering internals. A small reviewed core patch is preferable to a nested interception workaround.

## Validation

Six tests passed through `/home/hoskinson/window-integration-qa/qa_run.py`. Bounded policy cases cover raise/lower, all 24 permutations of MAX plus three floats with all eight pin subsets (192 combinations), modal chains, native fullscreen and tiled MAX unchanged. Source tests verify owning hashes, exact patch content and absence of state mutation. These are source/model tests, not a C++ build or native acceptance.

Required native campaign: Brave floating native MAX with two overlapping normal floats; alternating Alt+Tab and pointer hits, exposed geometry outside MAX, lower/re-raise, pin/unpin, modal/nested modal, return geometry, true fullscreen, tiled MAX, workspaces/special workspaces, multiple displays and cancellation/reload. Compare rendered top window and native hit at the same coordinates after real presentation. Preserve all original deadlines and failing evidence.
