# Applied parent layout

Actual owning-core derivative, additive to CHILD/CACHE and LAYOUT01/02.
- CORE-LAYOUT-01: WHEN a child receives set_position, its applied m_position SHALL remain unchanged until the parent state applies.
- CORE-LAYOUT-02: WHEN a valid child receives place_above/place_below, requests SHALL update pending parent paint order without mutating applied order; sibling/parent validation SHALL precede mutation.
- CORE-LAYOUT-03: WHEN the parent applies state, pending child position/order SHALL apply before its public commit observation. If the parent itself is synchronized, its child layout SHALL wait for that parent state to apply.
- CORE-LAYOUT-04: WHEN a queued role/parent is destroyed, weak identity and current parent membership SHALL prevent stale operations retargeting new native resources.
- CORE-LAYOUT-05: WHILE alive, pending layout storage SHALL belong to the same native wl_display and retire with it; bounded admission failure SHALL report protocol no-memory, without changing public class layouts or Elm policy authority.

Use fresh external registry, preserve694 original class headers/layout and431 archive payloads; rebuild owning Compositor/Subcompositor TUs, relink and compile exact source plugin against696 headers. Prototype admission bounds do not establish measured S02 budgets. Native LAYOUT01/02 and CACHE01..05 qualifications are separate from sibling destruction/cohort/fence/FIFO/hardware/provider/WebKit/fullrelease and original Omarchy obligations.
