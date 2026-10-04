# Controlled popup paint and input landmarks

Fresh272 preserves held253. P still contains an actual GtkButton and its real
clicked callback. The button child now contains a64×40 drawing area and label.
The area paints a declared dark background and magenta8×8 at(4,4). `landmark*`
fields measure that area in actual GTK native coordinates; separate `button*`
fields measure the real button, including its native surface transform.

`draw_popup` requires the live widget, current area pointer and popover ancestry.
`popover_clicked` additionally requires the current button pointer. Retirement
clears both borrowed pointers before widget destruction. Existing role resources,
controllers, window paint, family graph, standard state APIs and command grammar
remain unchanged. The ancestor and all failed/successful test attempts are kept.

Actual GTK compilation and CLI51/callback19/lifecycle22 controls passed. The new
actual extracted popup callbacks pass stale-area, wrong-ancestry, retired/replaced
widget and exact paint/click checks; three applied unsafe controls are rejected.
Mock object tests do not establish native GTK input, presentation or placement.

FullGTK260 must separately sample the declared popup marker via raw xdg_popup
geometry and measured GTK transform, click the actual button bounds with complete
recipient guards, and prove normal popup retirement. No theme-color inference or
full GTK06/native acceptance is made here. No GUI or installed configuration edits.
