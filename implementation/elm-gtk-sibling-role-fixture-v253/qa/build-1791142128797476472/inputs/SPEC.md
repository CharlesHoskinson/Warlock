# Closed sibling operations

This is an additive native fixture contract, not a new desktop policy model.
Inherited244 commands retain their syntax and scope. Add plain `open-sibling`
and `close-sibling`, and targeted `reparent-sibling A|B`.

`open-sibling` requires live A and absent E, creates a new E instance in the
family group (or inherited default-group profile), transient for A and modal.
`close-sibling` requires live E and retires it. Reparent requires live E and
the selected live parent; all other targets refuse before changing a relation.
Reparent preserves E's instance, draft and controllers, calls the actual GTK
transient setter, then journals `requested-parent` with the actual current GTK
parent surface. Raw Wayland and native observations must confirm the effect.

The relation graph is acyclic by construction: B→A, D→B, E→A or B, C independent.
Owner retirement closes P first for A, then recursively closes current transient
children in stable role-index order, then closes the owner. Unrelated roles stay
live. The command parser accepts no general reparent endpoint or arbitrary graph.
