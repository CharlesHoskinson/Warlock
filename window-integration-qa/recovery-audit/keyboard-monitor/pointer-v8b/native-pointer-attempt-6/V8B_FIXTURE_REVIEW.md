# V8b fixture-only readiness correction

Retained attempt5 report e3342b7b81732567f92405cbd2f7f410a3a605ecbd9625aeced0fd7a4d6b2867
passed69 reached native gates and all14preservation, then failed actual GTK popup
hit. Input96,120 was exactly window A origin, official callback0,0; settled
real popup position[75,-42], child bounds[12,11,186,34], transform0 imply child
center276,106. Initial sampled geometry was not logged; no exact initial
allocation values are inferred. The prior failure is retained and no popup
product claim is made.

Exact GTK4.22.4 sources/provenance are pinned in popup-primary: popup() only
sets visible, map→present queues allocation, compute_bounds only requires a
transform and succeeds without testing positive dimensions. The new fixture
requires mapped native surface + positive popover/button/bounds sizes + actual
Gtk.pick(center) returning the real popup button, records monotonic allocation
snapshot/target BEFORE native input, then reads actual double coordinates using
exact Hyprland get_cursor_pos (pushnumber, no floor), with independent integer
IPC and post-input GTK hit timestamps. No scale conversion is introduced.

No product/SO/reader/capability/model changes. Product v8 SO remains
af79dfc55411edd8dbbf5d56e3047fb4f1bf1479412b42f488045d4925d30992.
The popup parent AX mapping, actual Orca popup child, negative logical coordinate,
reader enable/disable/toggle/outage/restart/full-command and all14preservation
gates remain mandatory. The GDK a11y critical from attempt5 remains independent
unresolved evidence; a corrected target does not waive it or popup AX gates.

Six geometry source tests and all43 previous Python guards PASS. All previous
296frozen inputs and retained attempt5 remain unchanged. Native not run; output
native-pointer-attempt-6 is absent. Await root review/exclusive grant.
