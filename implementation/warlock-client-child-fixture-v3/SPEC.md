# Parent-committed child layout qualification

Retain CHILD01..05 and CACHE01..05, all original native681 checks, cache46 trace
states, actual owning core/source/AQ tuple and all original deadlines.
- LAYOUT-01: WHILE child position changes are pending without a parent commit,
  pixels and capture context SHALL retain applied geometry. WHEN the parent
  commits, pixels and context SHALL reflect the new position.
- LAYOUT-02: WHILE below/above-parent stacking changes are pending without a
  parent commit, pixels and capture context SHALL retain applied paint order.
  WHEN the parent commits, pixels and context SHALL reflect that order.

Preserve failed oracles and source hashes. Independent native PNG decoding,
physical consumer/export/producer retirement, ordinary exits, main-desktop and
unrelated-peer preservation remain required. Native membership initialization,
sibling sequencing/destruction, async fences/FIFO/presentation and ordinary
renderer/provider/WebKit/fullrelease are separate obligations. Omarchy and all
mandatory242/417, separate24/48 remain unchanged.
