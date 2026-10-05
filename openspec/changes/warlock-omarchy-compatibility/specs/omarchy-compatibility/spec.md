## ADDED Requirements

### Requirement: Omarchy vocabulary

EARS `WARLOCK-OMARCHY-001`: WHEN Warlock presents command search, command help or
settings actions, Warlock SHALL recognize every installed Omarchy command route
and alias, preserve its terminology and argument contract, and route execution
to the established command owner without silently substituting another action.

#### Scenario: Complete installed vocabulary

- GIVEN the immutable installed command inventory, including hidden routes and aliases
- WHEN the integrated command router and help inventory are qualified
- THEN every route has an explicit mapping and preserves its argument contract
- AND discovering or displaying a route does not execute it or elevate privileges

#### Scenario: Missing external owner

- GIVEN an adopted route whose external command owner is unavailable
- WHEN the user requests that route
- THEN Warlock reports the unavailable capability using the existing error model
- AND preserves unresolved operation identity and ownership

### Requirement: Effective shortcut compatibility

EARS `WARLOCK-OMARCHY-002`: WHEN Warlock loads shortcut preferences, Warlock SHALL
retain all effective Omarchy bindings with user overrides taking precedence,
including modifier, key/keycode, submap, mouse, repeat, release, long-press,
lock-screen and consumption semantics, and SHALL preserve each native action's
recipient and original operation deadline.

#### Scenario: User overrides survive integration

- GIVEN packaged defaults and the installed user's effective overrides
- WHEN the coherent Warlock release is started and its shortcut mapping is qualified
- THEN every effective mapping has the same intended action and precedence
- AND pin, snap, Alt-drag, Alt-Tab and minimize-others preserve their current key chords

#### Scenario: Repeat and release retain identity

- GIVEN an active repeat, release, mouse or submap binding
- WHEN its original press is followed by changes to focus, publication or lifetime
- THEN the release is delivered according to the native input ownership contract
- AND Warlock does not retarget the held action or renew its original deadline

### Requirement: One typed action owner

EARS `WARLOCK-OMARCHY-003`: WHEN an adopted shortcut invokes a Warlock shell or
window action, Warlock SHALL use the existing single immutable Elm policy and
typed native authority boundary, retain conflict resolution explicitly, and
SHALL NOT serialize runtime Lua callback identifiers as portable action targets.

#### Scenario: Popup and input-method ownership

- GIVEN a menu, picker or IME composition with an enrolled native input recipient
- WHEN an adopted Omarchy shortcut is pressed
- THEN the declared global or local route follows that binding's original semantics
- AND native recipient, held-key cleanup and IME behavior have actual qualification evidence

#### Scenario: Shortcut collision

- GIVEN two proposed actions with the same effective binding identity
- WHEN Warlock imports or edits the mappings
- THEN the declared override order resolves the conflict or reports it explicitly
- AND the previously effective action is not silently changed

### Requirement: Compatibility release and rollback

EARS `WARLOCK-OMARCHY-004`: WHEN an integrated Warlock release is qualified,
Warlock SHALL record per-route and per-binding compatibility evidence on its
coherent owning source/ABI tuple and SHALL preserve the user's shortcut settings
through installation, restart and rollback.

#### Scenario: Qualification requires actual action routing

- GIVEN the complete installed inventory and the proposed integrated mapping
- WHEN release acceptance is assessed
- THEN missing or unverified mappings remain open
- AND source inventory, browser demonstrations and model passes alone cannot qualify native shortcuts

#### Scenario: Reversible configuration preservation

- GIVEN the user's recorded custom mappings and a prepared release installation
- WHEN the release is rolled back after an interrupted upgrade or restart
- THEN the preceding compatible configuration and effective mappings are restored
- AND the original user drafts and main desktop are preserved
