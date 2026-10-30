## ADDED Requirements
> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

### Requirement: WARLOCK-LOCKCARRIER-001 — Same renderer after native wrapper retirement

WHERE explicit private native icon qualification is selected, WHEN actual session lock causes normal GTK popup grab/wrapper retirement before same-policy rendering is observed, the host SHALL retain the same own WebKit view in at most one private GtkOffscreenWindow until its actual concealed DOM/PNG snapshot completes, then remove that view, destroy the carrier and flush original retained controller commits, without new policy, source grant, capture, clock or deadline; bitmap evidence SHALL NOT claim hardware presentation.

#### Scenario: WARLOCK-LOCKCARRIER-001 native wrapper retires before snapshot

- GIVEN the actual native lock, original authenticated preview job and same actual WebKit/Elm view
- WHEN the original popup wrapper retires while producer cleanup remains pending
- THEN exact native held/new icon reads refuse, the same Elm conceals title/icon in independently decoded WebKit pixels, carrier/view ownership retires once and original ACK waits for actual producer retirement
