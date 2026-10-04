# Native GTK popup-window role experiment

V65 retires host popup-active state, GTK grab and seat grab on native unmap; V66 passes19 actual native checks, including outside dismissal, application pointer/keyboard afterward, reopen with one binding and native Escape.

A native48px top bar reserves exclusive48 and requests keyboardNone. A transient GTK_WINDOW_POPUP uses GDK move-to-rect and a seat grab to host the existing single Elm/WebKit engine. Native trace establishes xdg_surface.get_popup plus layer_surface.get_popup and xdg_popup.grab, configure(50,48,700,420); screenshot inspected. GDK unmap retirement makes the GTK widget eligible for explicit reopening. The initial and corrected sources/builds/failure receipts remain separate.

Build-only checks include optimized Main/native host, original compiled effect20/shell27 and three host self-test groups. No new Quint run, production taskbar or complete requirement acceptance is claimed. The temporary GTK opener and raw native Escape handler are experiment scaffolding, awaiting an Elm control, scoped lifecycle integration and composition/IME policy. Native role/grab/dismissal proof is separate from UI/single-source model and hardware/AT acceptance.

Open: replace native opener with Elm bar and one typed logical controller plus presentation-only popup view; stale native unmap/grab/reopen epochs, per-output layout, bounds/scale/transform, fullscreen/lock, exact input margins, full effect/launcher regression, AT/IME/human UX, activation and GPU/WebGPU/release. Main desktop/drafts/configs remain untouched.

Upstream API references: https://docs.gtk.org/gdk3/method.Seat.grab.html and https://raw.githubusercontent.com/GNOME/gtk/gtk-3-24/gdk/wayland/gdkwindow-wayland.c . Actual local role traces govern acceptance; API documentation alone does not establish behavior.
