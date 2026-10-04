# Bounded parent pointer delivery V10

The private Weston input module sends actual parent-seat motion and button
events into the exact V8 nested Aquamarine/Hyprland tuple. A GTK3 fixture records
the receiving widget and local coordinates. The protected native run passed 48
checks with normal process cleanup at original 800×600, shrunk 640×480, scaled
960×640 at scale 2, and restored 800×600. The fixture kept the same native
window address and PID across those modes. Each mode produced one left press and
release on `parent-input-recipient`; the recorded coordinates differed from the
chosen interior widget point by less than one logical pixel.

The exact source, owning tuple, protected build, native report, artifacts and
retained failed attempts are hashed in
`implementation/elm-parent-input-probe-v10/qa/slice-manifest.json`. The final
report is `qa/native-1791094099568473380/report.json` under that directory.

The test deliberately moves away from the child's initial cursor position.
A parent notification at the unchanged position did not cause the child to
recompute its pointer target. GTK's event window for the EventBox differs from
`get_window()` while `Gtk.get_event_widget()` and the signal recipient both
identify the intended widget; the final oracle checks those identities, a
stable press/release event window, and exact window incarnation.

This is bounded pointer-delivery evidence. Cursor pixels, rotation, parent
surface transitions during injection, multiple outputs, full menu journeys,
accessibility and release qualification remain open. No main-desktop change or
activation occurred.
