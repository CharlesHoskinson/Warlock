GTK landmark coordinates are measured with `gtk_widget_compute_bounds` against
its GtkNative widget. GtkNative's reported translation converts surface to widget
coordinates ([official GTK API](https://docs.gtk.org/gtk4/method.Native.get_surface_transform.html));
therefore surface = native-widget landmark point minus that translation. Raw
GdkEvent position remains a separate observation in surface coordinates
([GTK coordinate systems](https://docs.gtk.org/gtk4/coordinates.html)).

For the currently qualified equal-extent window profile, compositor output
point = native real origin + surface point − actual committed xdg window-geometry
origin. The actual window geometry must be extracted from that role's raw owning
Wayland trace, independently of its input callback. Do not add its origin twice,
substitute controller-local coordinates, or multiply logical coordinates by a
buffer scale. The pure helper refuses unequal real/window-geometry extents and
noninteger/out-of-output sample points; those are explicit open native profiles.

Popup position/grab ownership requires the reviewed owned-popup observer plus
raw immediate xdg parent/grab serial. A root's window conversion alone does not
qualify popup conversion or presentation. Screenshots, physical native input,
configure/ACK/commit chronology and stable before/after identity remain separate
required observations. No GTK presentation or recipient proof exists yet.
