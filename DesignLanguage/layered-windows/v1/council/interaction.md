# Layered-window council: interaction language

Research recommendation, 2026-10-05. This is additive design work; no product behavior or native acceptance is claimed. Council remit: make color, glows, shadows and shading useful while preserving one immutable Elm policy authority, native facts and physical ownership, the original 242 requirements/417 scenarios, separate right-click24/48 and the original release gates and deadlines.

## Decision proposed for consensus

Use the Warlock attention accent to direct attention, neutral shadow and shading to explain depth, and separate compact outcome tokens to explain operations. A steady bounded glow belongs to a native-confirmed active application window; a keyboard navigation candidate gets distinct static corner markers and explicit Candidate label in the owning shell control. Pointer hover is quieter and cannot become confirmed active merely because the pointer arrived. A pin marker remains independent of activity. This makes navigation understandable without letting decoration invent focus, success or stack order.

Candidate styling is a proposal until bound to the existing controller. Do not add independent JavaScript or renderer policy. Color values, widths, shadow radii and budgets must be reconciled with the other council recommendations and frozen before evaluation; this report does not supply unmeasured native budget constants.

## Existing facts that constrain the language

The v6 catalog has a three-tier token system: attention/action/focus map to the brand accent, confirmed to positive, unknown to warning and refused to danger. Dark accent is #B7A2FF; light accent is #583DA4. Existing CSS uses a 3 CSS pixel control outline and gap in browser demonstrations. Those values qualify neither native windows nor output-scale rendering. Active application focus need not use positive green: green is the outcome role, while lilac is attention.

ELM-GNO-006, ELM-KDE-001/005 and ELM-LAY-002 already require paint, hit testing and focus eligibility to agree on a committed native revision. ELM-GNO-004/005 and ELM-KDE-003 preserve family order and reject cyclic transactions. ELM-REV-016 allows minimized windows in shell enumeration without making their live surfaces eligible. ELM-KDE-007 redirects activation to an eligible modal in the selected family and preserves unrelated drafts. Decorations must follow these constraints.

The distinction between packaged Omarchy and effective user bindings matters. Packaged tiling.lua lines44–47 cycle and raise immediately on Alt+Tab. The user's snap.lua lines679–686 replaces those routes with a chooser which commits on Alt release, including minimized entries. Alt_L and Alt_R release mappings are non-consuming. Therefore preserve the complete effective binding identity and action owner; do not impose chooser-on-release semantics on every installation or convert this user's chooser into immediate focus. The same snapshot replaces Super+arrows with snap, Super+Home with minimize-others and Super+Tab with Task View. Respect all443 commands,370 command words and265 effective binding records, not only these examples.

## Independent state axes and presentation

| Axis | Authority and identity | Presentation | Must not imply |
| --- | --- | --- | --- |
| Confirmed active application | Current native focus/application observation, enrolled window incarnation and accepted scene/focus revisions | Solid accent boundary, bounded steady halo and Active indication in shell entry where applicable | Latest candidate, pending activation or process existence is current focus |
| Keyboard navigation candidate | Existing Elm shell navigation state, selected control identity and current observation dependencies | Static accent corner markers on the navigation tile, Candidate text; no active halo | Application input recipient or successful native activation |
| Pointer hover | Existing native pointer route and shell control hover state | Quiet neutral surface/chrome shading | Focus or raise; any configured native focus-follows-pointer remains governed by its existing route |
| Pinned | Acknowledged native pin observation | Pin glyph/check state and accessible Pinned label | Focus, visible-on-all-workspaces, exemption from minimize, lock, output or family rules |
| Family/modal | Native current parent relation and accepted modal recipient | Modest shared shell-chrome relation cue; blocked-owner chrome-only shade plus Modal dialog label | Same process/application means same family; shade establishes an input blockade |
| Occlusion | Current native committed scene | Compose normal decoration with its window in stack order; use existing shell entry to identify fully covered windows | Seeing a lower glow through an unrelated covering surface |
| Minimized/inactive | Native eligibility state; distinct retained preview identity if permitted | Shell entry label and authorized Historical/Loading/Unavailable preview | Source live pixels, direct application hit target or current active glow |
| Pending operation | Original typed operation identity/deadline | Compact pending glyph and Waiting for activation text | Focus success, fresh deadline or permission to restyle the candidate as active |
| Unknown operation | Retained operation identity and reconciliation state | Compact unknown badge plus Activation outcome unknown and declared read/reconcile route | Failure, cancellation, automatic retry or authority to send another mutation |
| Refused operation | Correlated native refusal | Compact refusal badge and concrete reason; focus follows native current observation | Entire family is broken or arbitrary automatic retry |

These axes can coexist. If a candidate is already confirmed active, retain both meanings: active boundary on the application if currently eligible, selected frame on its shell entry. If pointer hover targets a different entry, it stays subdued. Pending and Unknown markers remain tied to their original operation even when another target becomes current. If the native keyboard recipient is the shell during a chooser, do not fabricate application keyboard focus; distinguish current native active-application observations from a retained Previous active marker according to the existing native focus contract. A new native fact is required before making a stronger focus claim.

Decoration order is deterministic: first apply native eligibility and committed scene order; paint each window's shadow behind that same window within its allowed band, then surface/chrome, active boundary, and chrome-local relation markers. Candidate frame and operation status belong to their shell control under its declared shell layer. Nothing in this table raises a window, changes paint rank, changes the native input region or retains a surface resource beyond its authorized lifetime. Popup controls retain their own keyboard focus contract; application-active and popup-focused are different scopes. Physical popup/modal elevation remains derived from the committed native surface role and family constraints regardless of whether its controls currently own keyboard focus; focus treatment cannot flatten a popup into the owner band or lift an ordinary window into a popup band.

## Proposed EARS clauses and corresponding OpenSpec scenarios

IDs below are council-local draft IDs for the coordinator to map into the final additive packet. Existing IDs stay unchanged.

### Requirement: WL-LAYER-I01 — Independent interaction and outcome roles

WHEN Warlock displays layered-window navigation, Warlock SHALL derive confirmed active, keyboard candidate, hover, pin, eligibility and operation outcome cues from their respective existing typed state axes, preserving independent identities and a non-color distinction between active and selected.

#### Scenario: Candidate differs from confirmed active

- GIVEN A is native-confirmed active and B is the current chooser candidate
- WHEN the chooser paints B
- THEN B's shell control has Candidate frame and text while A's eligible application retains only its native-confirmed active cue
- AND B receives no application active halo or success label from selection alone

#### Scenario: Candidate is already active

- GIVEN the same window has current active native observation and chooser selection
- WHEN both scopes are presented
- THEN application-active and shell-selected cues remain distinguishable without suppressing either meaning

### Requirement: WL-LAYER-I02 — Activation confirmation and unresolved outcomes

WHEN a typed activation request is emitted, Warlock SHALL preserve its original operation identity and deadline and SHALL use correlated native observation/settlement for activation status; Pending or Unknown SHALL NOT invent focus success or automatically replay the request.

#### Scenario: Delayed activation

- GIVEN B is selected and activation is pending while current native observation still identifies A
- WHEN the pending interval passes without settlement
- THEN Pending remains explicit until the existing outcome protocol transitions it
- AND no timer gives B a confirmed-active cue or renews its original deadline

#### Scenario: Unknown followed by read reconciliation

- GIVEN B's activation outcome is Unknown and a later authenticated current observation identifies C as active
- WHEN that observation is reconciled
- THEN the current active cue follows C while B's retained operation outcome is settled only by its existing admissible protocol
- AND observing C does not replay B's activation

### Requirement: WL-LAYER-I03 — Decorative effects preserve scene and hit authority

WHILE glow, shadow or shading is rendered, Warlock SHALL compose it from the same committed native eligibility and ordered scene revision as its associated live surface, clip it under covering surfaces, and SHALL NOT grant decorative pixels independent application hit or focus authority.

#### Scenario: Unrelated opaque cover

- GIVEN an eligible active window is partially covered by an unrelated opaque higher window
- WHEN its glow and shadow are composited
- THEN covered decoration does not reveal the lower window through the cover
- AND a click in the cover reaches the eligible native recipient under the pre-existing input-region/modal exceptions

#### Scenario: Minimized or inactive source

- GIVEN a minimized or inactive nonsticky source is enumerated in the switcher
- WHEN the source is selected
- THEN only the separate shell control receives selection decoration and authorized preview behavior
- AND no live source halo, application input region or excluded live pixel is restored by decoration

### Requirement: WL-LAYER-I04 — Modal family relationship without unrelated suppression

WHEN a current eligible modal family is navigated, Warlock SHALL attach relation and blocked-owner cues only to the native-confirmed family and redirect activation under the existing modal rule without changing unrelated families or user drafts.

#### Scenario: Modal owner and unrelated peer

- GIVEN A owns eligible modal M and unrelated application U has an open draft
- WHEN the user activates A then U
- THEN the existing native route resolves A activation to M and allows U activation independently
- AND owner chrome-only shading never dims U or forwards A click coordinates as an M client click

#### Scenario: Family relation becomes stale

- GIVEN a selected entry references an older native family revision
- WHEN the relation changes before activation admission
- THEN the stale intent cannot promote old relatives and is reconciled under the existing stale-refusal contract
- AND relation color never reconstructs the family from process identity

### Requirement: WL-LAYER-I05 — Effective Omarchy navigation semantics

WHEN layered-window navigation uses an adopted Omarchy binding, Warlock SHALL preserve the effective modifier, key, submap, press/release/repeat/non-consuming semantics, current user override precedence and native action owner without altering the original operation deadline.

#### Scenario: Effective Alt chooser release

- GIVEN this user's frozen chooser override with Alt_L and Alt_R non-consuming release routes
- WHEN Alt+Tab moves the candidate and the owning Alt release commits it
- THEN selection and activation follow the existing chooser route with one original operation identity
- AND selecting a minimized entry does not make its live source eligible before accepted restore

#### Scenario: Packaged immediate route

- GIVEN a distinct effective mapping retains packaged immediate cycle/raise
- WHEN Alt+Tab is invoked
- THEN Warlock does not insert chooser-on-release policy or defer the original route merely to display the new style

### Requirement: WL-LAYER-I06 — Hover remains a separate presentation scope

WHILE a pointer hovers over a layered-window control, Warlock SHALL use a subordinate hover cue and SHALL NOT synthesize application focus or activation from that hover; any configured native focus-follows-pointer policy SHALL continue through its established owner.

#### Scenario: Hover differs from selected

- GIVEN B is selected by keyboard and the pointer rests over C
- WHEN the surface repaints
- THEN B retains its selected frame, C shows subordinate hover treatment and the native focus observation is unchanged by style

### Requirement: WL-LAYER-I07 — Lifetime and reconciliation remove invalid decoration

WHEN a native target incarnation, output, scene eligibility or authorized visual lease becomes invalid, Warlock SHALL withdraw invalid live decoration under the existing lifecycle contract, retain unresolved operation records under their original identities and reconcile navigation without retargeting a pending mutation.

#### Scenario: Selected target disappears

- GIVEN B is selected and a request referencing B's exact incarnation is unresolved
- WHEN B is destroyed or removed by output/workspace change
- THEN B's invalid live decoration is withdrawn and shell navigation follows its declared fallback
- AND the retained operation is not silently rebound to the replacement candidate or renewed

### Requirement: WL-LAYER-I08 — Honest qualification of visual language

WHEN layered-window interaction acceptance is assessed, Warlock SHALL distinguish source, model, browser and native proof and SHALL retain the original full-release acceptance gates, scenario identities, oracles and deadlines.

#### Scenario: Browser specimen is insufficient

- GIVEN a layered-window specimen correctly distinguishes Active, Selected, Pending and Unknown
- WHEN release acceptance is reviewed
- THEN the specimen proves only its labeled browser/style scope
- AND scene pixels, hit recipients, native focus receipts, family/workspace races, output variants, resource budgets, accessibility and original S01–S16 gates remain separately required

## Reference decisions and disagreement record

Borrow the distinction between navigation focus and selection from desktop guidance, but bind application activation claims to Warlock's typed native truth. Microsoft recommends input-appropriate visual feedback, keyboard focus rectangles/highlights and focus boundaries with two contrasting parts; adopt those concepts without importing its platform gesture changes, product colors or numeric native window tokens. Keep its decorative Reveal-style lighting optional and bounded: continuous hover lighting adds no required authority or navigation information. [Microsoft visual feedback](https://learn.microsoft.com/en-us/windows/apps/develop/input/guidelines-for-visualfeedback) (primary page inspected 2026-10-05; page reports update2026-09-27).

The Apple focus-and-selection page was located, but the fetched official page requires JavaScript and provides no readable guidance. It supplies no binding claims or numeric values here. [Apple focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection/). No inference from its inaccessible body is used.

Initial design preference was a detached/double candidate frame rather than dashed pattern, while the depth reviewer proposed a dashed perimeter. Cross-review accepts the color reviewer's shared-violet corner marker on the shell tile and explicit Candidate label, with no candidate halo. All approaches require static, shape-distinct, contrast-qualified cues; the final packet must choose one deterministic recipe. Reviewers agree on neutral separation shadows, owner chrome-only modal shading, no client-text dimming, committed scene composition, no layer-rank change and no decorative input area. Native focus and candidate generations remain independent: a newly admissible native B focus observation is valid even if shell candidate has moved to C. Reject focus facts only under the existing native revision/incarnation protocol. No disagreement with frozen native policy is authorized.

## Exact local source identities inspected

SHA-256 binds the observations above; no source listed here was modified.

| Source | SHA-256 |
| --- | --- |
| AGENTS.md | 0b290ba5e79a6be5ab16572741e275384ed47398eece952b9ff515702fd18d02 |
| docs/HANDOFF.md | 339f702523fe5f4113700978c14c84e6eaa289ba964053d2d1e7d4954dacdbbd |
| docs/warlock-build-loop/design-language-v1/INSTRUCTIONS.md | 7d6eaf650ea7f5091eace9f17188a6d6bf610c7cb654677b1a185a98b18bdf50 |
| DesignLanguage/CONSENSUS.md | 5907b395ba7473126976cd6498f63d90add54045778ca5ea7c1f577bac9c9009 |
| DesignLanguage/WORKPLAN.md | 986d257d98c09802759e63ffb0894a22780bbc47b4a4e6279c3316dea090e1cc |
| DesignLanguage/catalog/v6/tokens.json | 352eca419c1e1c4150810f02bf5bb6f0b8a2dabd144e8c7077a6ca30b4a988c9 |
| DesignLanguage/catalog/v6/catalog.css | e9100c79584decec271713d271fae2da86d22709e4c27614c7dbb445d6c2a164 |
| DesignLanguage/catalog/v6/component-manifest.json | 7378d1a9eddfa2af95623db7d30e6c3d6b5dff62d10828839fca2ab30f9b6ba4 |
| openspec/changes/warlock-design-language/specs/warlock-design-language/spec.md | 95d0b637e49033860a16f9f6ef27fb9db147ff6fc3d50edf6e7a6c456cb05353 |
| openspec/changes/elm-desktop-pivot/specs/elm-layering/spec.md | 685509a72ff963316eb4d70543f6dbc0d5b52fdf09368f0c5a3ce0ee369936e3 |
| openspec/changes/warlock-omarchy-compatibility/specs/omarchy-compatibility/spec.md | 77d35562c2ce803a9908b64a6b9cda9daf24a0d6c2eb2b5ebe366a3af3895f02 |
| docs/warlock-compatibility/omarchy-v1/sources/packaged/bindings/tiling.lua | 85aac24c8a44fc3d0513e77ac2c59eefb179228834d6670ec76fb310d9f99aaf |
| docs/warlock-compatibility/omarchy-v1/sources/user/snap.lua | 389bc19a23e090e1a43d446fc927a65e265b1742bbbd15a88b1163ef0fc59e7c |
| docs/warlock-compatibility/omarchy-v1/effective-bindings.json | 406005980db7bd091707f952f9420a107b91b5e328eeef235c0492b0e10a7c34 |

## Integration and verification advice

Map these clauses into S06 eligibility/layering, S07 input/focus, S09 preview, S11 feedback, S12 accessibility, S13 output and S02 budget contracts without changing their frozen identities. Reuse existing typed observation, target, operation and receipt structures; add only reviewed presentation role/token derivations in the owning Elm model. The producer carries confirmed native scene/focus/incarnation facts; renderers consume roles and compose pixels without becoming a second controller.

Select Quint cases explicitly: candidate versus active, pointer versus candidate, shell-recipient versus previous application, stale family/output/incarnation, Unknown retained during new observations, minimized candidate and late activation receipts. Couple them to actual Elm role derivation when implemented. Native fixtures must independently verify pixels, input recipients and correlated focus receipts on the exact owning core/plugin pair. Test partial and full occlusion, supported modal depth, user Alt release routes, actual hover policy, output changes and paused/stalled frontend. Capture animation/render resource ownership and measure accepted numeric budget thresholds; glow simplicity does not close S02 by assertion.
