# Sibling consumer integration

Extend held238 journal/Actor interfaces to consume held253's actual E role and
closed sibling commands, preserving all existing bounds, ordering, profiles,
terminal checks, input recipients and subprocess ownership. Invalid parent
targets must refuse before the command is written.

Check GTK reparent evidence against one exact reparent request, a subsequent
E `requested-parent` row, and post-request inspections of both E and the expected
live A/B parent. Bind instance/map/resource identities for both. Require actual
GTK transient resource and modal state in the intent row and final inspection.
This proves toolkit journal consistency only; actual Wayland set_parent, native
ownership, focus and held-input retirement remain full GTK05 acceptance gates.
Preserve failed238 native evidence and the original GTK01–08 contract.
