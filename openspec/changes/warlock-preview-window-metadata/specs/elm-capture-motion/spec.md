# ADDED requirements

### Requirement: WARLOCK-METADATA-001 — Correlated current fallback

WHEN fallback metadata arrives, the single Elm presenter SHALL admit only exact owner binding and incarnation with a positive canonical uint64 revision newer than its retained metadata revision, bounded labels, and consistent application/generic/unavailable icon resolution; rejected events SHALL emit no effects and SHALL NOT mutate lifecycle policy, clocks or receipts.

#### Scenario: WARLOCK-METADATA-001 current and stale metadata

- GIVEN a current enrolled preview and admitted revision
- WHEN a newer metadata message or a malformed, foreign, duplicate or older message arrives
- THEN only the current exact newer message updates title/icon, without any capture or cleanup command

### Requirement: WARLOCK-METADATA-002 — Native icon authority

WHEN an icon is opened or read, the native endpoint SHALL validate the registered view, opaque canonical token, owner binding, current source incarnation, privacy revision, unlocked presence and application identity independently of Elm progress, and SHALL refuse unauthorized reads without supplying another source's bytes.

#### Scenario: WARLOCK-METADATA-002 held reader and incarnation/privacy change

- GIVEN a held partially consumed icon reader and delayed frontend
- WHEN the source locks, disappears, changes application or is replaced
- THEN both held and newly opened old-token reads refuse and no foreign pixels are supplied

### Requirement: WARLOCK-METADATA-003 — Concealed locked fallback

WHEN an exact known current preview job receives an authenticated locked-source denial, the existing immutable Elm lifecycle SHALL conceal its title and icon until a valid coherent fresh authenticated unlock observation, retaining original cleanup, scope, clock, expiry and terminal ACK obligations.

#### Scenario: WARLOCK-METADATA-003 lock before scope update

- GIVEN the retained scope is still unlocked and a current owned preview exists
- WHEN an exact locked-source denial arrives before a locked scope and then metadata or another denial arrives
- THEN title/icon remain concealed without fabricating a scope or retirement proof; only a fresh coherent unlock observation can restore visibility

### Requirement: WARLOCK-METADATA-004 — Bound and physically retire icon ownership

WHILE native icon bytes or readers exist, the endpoint SHALL account for retained physical assets and readers, enforce two assets, 64KiB per encoded asset and four readers, and SHALL NOT erase reader ownership on revocation or teardown; capacity SHALL return only after actual consumption/close.

#### Scenario: WARLOCK-METADATA-004 held replaced assets

- GIVEN two distinct superseded assets each have a held reader
- WHEN a third icon update or endpoint teardown is requested
- THEN the update is backpressured and teardown refuses; actual reader closure releases its reference and permits capacity to return
