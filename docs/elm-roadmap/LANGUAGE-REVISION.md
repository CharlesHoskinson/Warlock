# Current implementation-language revision

The current Warlock-authored product uses Elm and Haskell only. Every GUI element
is Elm. Backend/runtime integration is Haskell, with one policy owner per decision.
Generated Elm output and separately inventoried system libraries are distinct
from authored product components. No Python runtime ships.

The pre-revision register is preserved at
[the baseline](baselines/requirements-pre-language-20261030.json), SHA256
`a0c2093cc7769e05b70cc81aa3c001dbcbffe936cc17d1c494d7ab2fdc8b3b1b`.
[language-revision.json](language-revision.json) explicitly changes implementation
wording in ARC002, DEL003, DEL012, REN023 and TEA005. All242 IDs,417 scenario
objects and every verification statement are unchanged. Existing evidence remains
bound to its original source, not automatically accepted for a replacement.

The generator applies exact before-value and ID preconditions after author-input
normalization and role assignment, then emits the current register, traceability
and capability deltas. Original author contributions remain preserved. The Muse
controller separately records frozen-original and current-revision inventories.

Current design/interface work is authorized and coordinated by ten agents.
Rearming implementation requires reviewed architecture/native feasibility,
versioned Elm/Haskell interfaces, protected Quint/correspondence/fuzz results,
aligned current specifications, a reviewed workflow plugin and a truthful
checkpoint. Design readiness does not replace original native or release gates.
