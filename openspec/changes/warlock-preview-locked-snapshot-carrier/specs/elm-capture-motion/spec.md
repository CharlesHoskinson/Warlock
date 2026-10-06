# ADDED Requirements

### Requirement: WARLOCK-LOCKCARRIER-001 — Same renderer after native wrapper retirement

WHERE explicit private native icon qualification is selected, WHEN actual session lock causes normal GTK popup grab/wrapper retirement before same-policy rendering is observed, the host SHALL retain the same own WebKit view in at most one private GtkOffscreenWindow until its actual concealed DOM/PNG snapshot completes, then remove that view, destroy the carrier and flush original retained controller commits, without new policy, source grant, capture, clock or deadline; bitmap evidence SHALL NOT claim hardware presentation.

#### Scenario: WARLOCK-LOCKCARRIER-001 native wrapper retires before snapshot

- GIVEN the actual native lock, original authenticated preview job and same actual WebKit/Elm view
- WHEN the original popup wrapper retires while producer cleanup remains pending
- THEN exact native held/new icon reads refuse, the same Elm conceals title/icon in independently decoded WebKit pixels, carrier/view ownership retires once and original ACK waits for actual producer retirement
