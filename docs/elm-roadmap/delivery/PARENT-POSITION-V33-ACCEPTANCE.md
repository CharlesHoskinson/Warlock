# Stationary parent input V30–V35

The V26 failure is corrected on a fresh exact core/plugin/Aquamarine tuple.
Clicks at an unchanged parent pointer position now reach the GTK coordinates
under the visible cursor after same-pixel-mode scale changes. No installed
desktop library or compositor was replaced.

## Source behavior and owning tuple

The previous core received normalized pointer coordinates after discarding the
Aquamarine output identity. It retained the previous logical position across a
logical-only monitor change. V31 retains weak pointer/output identities and the
normalized output-relative point, projects it through that output's logical
box, and routes a changed projection through normal InputManager hit testing.
It synthesizes no button events. Relative/programmatic movement clears the
anchor. Layout replay checks live device/output identities and current backend
input readiness before dispatch.

V28 adds a nonvirtual backend readiness accessor, with no class fields or vtable
changes. V30 adds a thin opaque parent-input status function/header so the
owning core can distinguish Unsupported, Inactive and Ready without including
generated client Wayland protocol definitions. Existing V28 headers are
unchanged in V30; this does not claim that all headers are unchanged from V17.
V29's failed client/server generated-header collision remains archived, as does
V31's initially malformed build runner. V31's corrected build2 runner passed.

V31 retains V22's cursor extent correction. Its incremental archive changes only
PointerManager.cpp.o; the other 432 ordered object payloads remain identical.
The authority source is unchanged and freshly rebuilt against the owning
headers in V32. The frozen manifests and native mappings bind all qualification
to this tuple:

- Core: V31 build-1791098227819326160, SHA-256
  ff1bf9d5e0406eba450add364f67b23bb2501bfcc522296ede3712b50868f01f.
- Authority: V32 build-1791098320875693200, SHA-256
  f1bba468e10cf91ae276e0ca3f890cbdb9282819bd75dfb2871056cff7494f1e.
- Aquamarine: V30 build-1791098020734308423, SHA-256
  1763ba3b38832b67ed70d9470661cdc18073ca0924f1ef962ffcbf61cf754ff5.

## Bounded evidence

V31 passes 61,232 normalized-position CPU cases and the inherited 54,462 cursor
extent cases. Deliberately incorrect remapping and raw cursor-size mutations
fail. V27 executes the actual extracted V30 readiness/status bodies against
typed ownership mocks and the real lifecycle helper: 25 CPU checks cover focus
changes, configure fencing, destruction and backend retirement. These checks
are not native acceptance of those lifecycle paths.

Protected native campaigns use the original deadlines and recipient assertions:

- V33 stationary cursor/click: 195 checks, including unchanged parent coordinates
  after shrink, pixel-mode scale, restore, same-pixel-mode scale 1→2 and 2→1.
  Physical GTK press/release coordinates and captured parent cursor pixels pass.
- V33 original Elm parent-pointer menu/reflow: 68 checks, including actual native
  effect receipts and exact V32 plugin mapping.
- V34 original held-button campaign: 105 checks, retaining coordinate changes,
  controller quit/EOF, duplicate press refusal, unmatched release refusal and
  three-button cleanup cases. These are controller lifecycle cases, not a claim
  of physical device removal acceptance.

All three native campaigns pass normal ordered cleanup in the private protected
host. V35's protected freeze verifies source/artifact hashes, actual core/AQ
mappings, plugin mapping in the menu campaign, and retained failed reports. Its
acceptance-manifest.json archives 1,984 files across the owned V27–V35 slices.
The previous V26 failure and prior component manifests remain unchanged.

## Quint and remaining work

The cursor/parent-position correction has no dedicated Quint model or native
trace refinement claim. The authority retains its previously modeled contract;
the unchanged copied model does not qualify this new input behavior. The next
behavioral model should cover output identity, normalized anchors, logical
layout changes, readiness fencing and superseding movement, then compare
implementation observations against explicitly selected scenarios.

Native focus leave/re-entry, parent configure/generation fencing, capability loss
and device retirement remain open. Multiple outputs and rotation need actual
input/pixel evidence. The V33 host retains the V10 private parent helper for its
bounded normal-lifecycle campaign; device-removal qualification must use the
reviewed removal-safe helper rather than infer it from these runs. Shared shell
integration, physical hardware, accessibility/IME, measured budgets, reversible
deployment and the complete S01–S16/right-click/C00–C06 release gates remain open.
The automatic goal stays active; these counts close only this bounded defect.
