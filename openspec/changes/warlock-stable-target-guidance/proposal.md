# Stable picker targets and observed window toggles

The current pin/MAX draft fails its native context interaction because preview arrival changes picker row geometry between press and release. The native identity guard correctly cancels the mismatched gesture. The current menu also swaps Always on top/Unpin window labels and does not expose checked semantics.

Clarify existing Warlock design contracts with stable preview/status geometry and an observed, consistently named toggle. Preserve the single Elm owner, native custody, identity/publication/lease guards, original UX-016 oracle and deadlines. This additive guidance changes no frozen consensus or accepted evidence. Implementation remains open.
