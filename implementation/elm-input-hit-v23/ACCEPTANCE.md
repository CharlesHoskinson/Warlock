# Bounded input-hole repair

The input selector now consults the existing surface-tree input hit tester inside
Wayland client content before returning a window. This prevents the later main
surface fallback from accepting an input-region hole. Window decorations outside
content and the existing X11 path retain their selection policy. This candidate
preserves earlier modal, minimize and renderer changes in the archive lineage.

Two continuous-redraw private native campaigns passed 94 and 97 checks with clean
shutdown. The first covers input pass-through to an independent lower owner,
solid-region delivery to the top peer, restored full-region delivery, actual
keyboard recipients and immutable retained masks. The second reruns the preserved
failing hole above MAX and its remaining original regression scenarios. The frozen
compiled V21 decoder accepted all 44 actual packets from these campaigns, while
keeping scene, correlation and presentation claims false. Ordinary rendering
regression is recorded separately in the final slice manifest.

Both V22 native failures remain unchanged. A V23 preflight failure caused by a
missing fresh fixture manifest is also preserved; it launched no native desktop.
The subsequent run uses the prepared source manifest. The compile-pair README is
an immutable historical input stating verification pending; this document records
the later findings and `qa/slice-manifest.json` records exact accepted evidence.

This is a bounded unit-scale, untransformed, quiescent pointer/keyboard proof.
Buffer/viewport/clip mapping, transformed and scaled outputs, complete roles,
multiple devices, presentation, performance, human usability, accessibility/IME
and release acceptance remain open. No new Quint run is claimed for this repair;
previous architecture/model evidence is separate. Nothing is installed on the
live desktop. Next: actual output changes and coherent scene dependencies, then
integrated taskbar/navigation/previews and the full UI/UX strategy.
