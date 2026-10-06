# ADDED Requirements

### Requirement: WARLOCK-ICONLOCK-001 — Native held and new icon authority

WHEN an own source locks while an actual icon reader is held and frontend delivery waits, the native endpoint SHALL refuse both held and newly opened old-token reads before original policy effects, retain physical reader/asset accounting until actual close, and SHALL NOT supply old or foreign icon bytes.

#### Scenario: WARLOCK-ICONLOCK-001 lock before policy processing

- GIVEN the actual full GUI owns an authenticated icon token, a partially consumed reader and original preview frame
- WHEN the private native session locks and frontend processing is delayed
- THEN both actual reads refuse while original preview resources and the held icon reader remain charged; original expiry and job do not change

### Requirement: WARLOCK-ICONLOCK-002 — Concealed fallback during producer retirement

WHEN exact authenticated locked-source denial reaches the same Elm policy, its rendered fallback SHALL conceal title and icon before the original producer retires, SHALL preserve original pending resources and exact cleanup/ACK identity, and SHALL NOT invent a new scope, native clock or terminal proof.

#### Scenario: WARLOCK-ICONLOCK-002 actual locked popup

- GIVEN an actual private native session lock and original producer pending retirement after exact Elm Release
- WHEN the full GUI fallback is observed in its DOM and independent WebKit PNG
- THEN Preview unavailable and zero icon elements/pixels are rendered without old/foreign preview pixels, while original terminal ACK waits for actual native retirement

### Requirement: WARLOCK-ICONLOCK-003 — Private control boundary

WHERE explicit private qualification is selected, WHEN hold/probe/release stimulus is read, the host SHALL require exact bounded file bytes in a UID-owned0700 nonsymlink parent and UID-owned0600 nonsymlink regular single-link file, reject returning to hold after probe, bound validated undispatched effects to four and preserve original ACK delivery; control bytes SHALL NOT provide grants, URIs, scopes, clocks or policy outcomes.

#### Scenario: WARLOCK-ICONLOCK-003 malformed and bounded stimuli

- GIVEN wrong ownership, permissions, links, oversized or malformed bytes or a returning hold
- WHEN the private control boundary is exercised
- THEN qualification refuses without enrolling an alternate source or dropping retained ownership

### Requirement: WARLOCK-ICONLOCK-004 — Binding-scoped metadata revision

WHEN a valid native actor binding changes, the presenter SHALL clear the former title/icon/revision domain, retain exact old cleanup obligations, reject old-binding metadata and admit only authenticated current-binding metadata with its own positive delivery revision.

#### Scenario: WARLOCK-ICONLOCK-004 new binding with lower revision

- GIVEN admitted former-binding metadata and an original owned job
- WHEN a valid new binding attaches with its own lower positive metadata revision
- THEN old metadata cannot reappear, current metadata is admitted, and no old cleanup is erased or duplicated

### Requirement: WARLOCK-ICONLOCK-005 — Native icon theme invalidation

WHEN GTK reports an icon-theme change, the provider SHALL invalidate its native icon cache and use existing polling to publish current correlated metadata, without new capture authority, timer, original deadline renewal or resource-owner erasure.

#### Scenario: WARLOCK-ICONLOCK-005 theme changes without title change

- GIVEN current title/application and a resolved native icon
- WHEN the native theme changes while source metadata is otherwise unchanged
- THEN new current icon metadata is published through the same owner and existing polling, respecting held-reader/resource bounds and original preview job identity
