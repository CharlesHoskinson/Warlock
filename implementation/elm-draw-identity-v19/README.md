# Draw-time identity binding

Fresh V18 native derivative. The core records authority lifetime and mapped window
incarnation in each surface dispatch when it occurs. A bounded weak-reference
registry supplies scalar identities; there is no callback into unloaded plugin
code and no reference that keeps an application window alive. Binding updates
preallocate before swapping; missing bindings remain explicitly unbound.

Serialization preserves captured identities. Current member/lifetime comparisons
only mark retirement; they never replace the captured identity with a new one.
Protocol2 explicitly represents authority, incarnation, unbound and retired state.
One diagnostic retained snapshot per authenticated session permits inspecting old
frames across unmap/remap. Hello clears the retained snapshot; plugin unload clears
the registry. Retained frames are historical evidence, not current scene admission.

Private native proof includes the original 63 behavior checks, plus a 81-check full-redraw
campaign with unchanged overlap/pixel/pointer/keyboard assertions and three natural
GTK hide/show checks. The retained Peer draw stays incarnation 1 and retired after
unmap/remap; fresh draws use incarnation 6. These are observed identities from this
run, not fixed product values. Complete allocator-address reuse and native authority
reload campaigns remain open.

The updated typed Elm decoder accepts historical tokens without admitting them as
current dispatch traces. It rejects mismatched nullable token pairs, bounds and
protocol versions and guards current traces against unbound/retired/lifetime
mismatch. Canonical scene remains false. The 26 compiled checks include 16 actual
native packets, malformed packets and counter/retirement boundaries.

Quint independently runs six named identity scenarios and 1000 invariant samples
(40 steps). Its invariant compares token validity with an independent mapping
lifecycle generation oracle; a model variant omitting authority comparison must
fail the authority-reuse scenario. These are abstract proofs, not native refinement.

The failed compiler string concatenation and first native attempt are preserved.
That native attempt reached 77 checks before an unnecessary legacy keyword call
failed in the Lua-configured fixture; the retained-frame experiment now uses the
already configured full-redraw variant. The initial pair inventory is preserved
as build-pair-initial.json. No earlier accepted source/proof packet was changed.

Draw identities are now captured at dispatch, but surface identities, buffer/input
masks, draw-time geometry/output generations, dependency coherence, presentation,
all role/device routes, GPU performance, AT/IME and release gates remain open.
Prototype limits are still 256 bindings, 32 monitor slots and 1024 draws; these are
not approved product budgets. Nothing is installed on the user's desktop.
