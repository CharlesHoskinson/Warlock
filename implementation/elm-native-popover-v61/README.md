# Rejected GTK3 popover surface experiment V61

Experiment only: the existing single Elm/WebKit view is hosted in a GtkPopover attached to a native 48px bar with exclusive zone48 and keyboard modeNone. The temporary GTK opener is not the final Elm taskbar. This experiment was required to resolve actual native role support before the shared Elm controller/bar/popup integration.

Optimized Main/native host build, original compiled effect20/shell27 and three host self-test groups pass. V62 measures native monitor reserved=[0,48,0,0]. The first run missed bar buffer readiness and never observed a coherent rendered view. Its original six-second observation deadline, source and cleanup are preserved.

The second run waits for the actual bar buffer attachment, receives real pointer events and reaches a coherent700x420 Elm DOM. However the Wayland trace creates wl_subsurface rather than xdg_popup, with negative Y placement progressing to -449 relative to the top bar. The actual xdg_popup parent-role assertion fails. DOM coherence is not proof of a visible/native popup; protocol grab, dismissal and subsequent input cases are not accepted. Normal host/backend exit and private cleanup occur on this second failure.

Disposition: no-go for this GTK3 GtkPopover route as the specified production popup container. The workarea reservation component is observed; no production popup/taskbar, layering/keyboard/AT/IME or release acceptance is claimed. GTK Layer Shell upstream documents popup/popover support generally, but that does not establish the protocol role of every GTK widget. See https://github.com/wmww/gtk-layer-shell and the preserved V62 actual protocol logs.

Next: test GTK native popup-window/menu role support (or alternative host toolkit), retaining one typed logical Elm interaction model and separate native surface lifetimes. Final Elm bar controls, per-output geometry, exact input regions, keyboard/grab/dismissal/focus, fullscreen/lock and hardware/release remain open. Installed desktop/drafts unchanged. No new Quint run for this native toolkit experiment.
