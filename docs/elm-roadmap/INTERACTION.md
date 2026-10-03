# Frozen default interaction contract

These defaults resolve the final UI/UX reviews. P0 must turn them into versioned fixture oracles before implementation qualification. Changes require a new policy version, explicit preference migration and revalidation; they cannot be silently selected after test results.

## Taskbar and window activation

Application pin means a persistent launcher entry; window always-on-top is a separate native state. Primary pointer click and keyboard activation have the same decision table:

| Listed family count | State | Primary action |
| --- | --- | --- |
| Zero | Pinned launcher | Request one launch |
| One | Inactive | Activate visibly |
| One | Minimized | Restore then activate visibly |
| One | Active and eligible | Minimize family |
| Multiple | Any | Open labeled group picker; selection activates visibly |

The explicit New instance action requests a new launch. It is never inferred from a failed activation. Family entries include minimized windows without treating them as live scene candidates. Native refusal preserves observed state and exposes correlated feedback.

Cross-workspace activation navigates the owning output to the target's preserved ordinary workspace, then restores if necessary and activates the eligible modal-family target. Another output becomes the keyboard-focus output; the window is not silently transferred. Navigation and restoration remain individually receipted, generation-bound effects. A refusal preserves a usable visible focus target. If workspace navigation commits but restore is refused, select an eligible visible fallback on the destination workspace or perform a separately validated compensation to the prior workspace; never assume the original target remains visible or replay uncertain effects. Explicit Task View transfer is a separate accepted operation.

Minimizing the focused family selects the most recently committed eligible application family in the current effective workspace set, or the desktop/no-application-focus state. Minimizing an unfocused family preserves focus. Lock/security rules always override ordinary succession.

## Switcher

Default scope is ordinary user-session application families across workspaces and outputs, including minimized families. Lock, protected/security-only and unlisted surfaces are excluded. Represent each family once by family identity. For a minimized family use its identity-bound entry; resolve the eligible modal target only after accepted restoration. For a live family represent its eligible modal target. Sort by last committed activation descending; stable incarnation order resolves equal/no-history entries. Native stacking alone does not determine recency.

With history A then B then C, C is current and frozen order is C,B,A. First forward selects B; further forward selects A,C,B. Initial reverse selects A; reverse wraps in the opposite direction. Zero candidates is a no-op. One candidate remains active or is visibly restored/activated, never minimized by switching. Cancel preserves initial focus and activation history. Only a committed activation changes recency.

Freeze candidates for a chord. Late arrivals wait for the next chord. Remove retired candidates by identity; if selected candidate dies, choose the next surviving entry in traversal direction, or cancel safely if none remain. Release-before-readiness and Escape remain native ordered control events.

## Search, overview and menus

Search ranks case-folded exact display-name matches first, prefix matches second, token matches third; stable desktop-entry identity breaks ties. Search indexed localized display name, generic name and declared keywords; executable text is not an arbitrary command route. Current query and catalog generations own selection. Initial, loading, no-match, unavailable and refusal states are distinct. Enter cannot launch a removed identity or results from an old query. Preserve query/focus on failure; retry refresh does not auto-launch.

Task View shows workspace markers and family entries, allows selection and explicit transfer, and dismisses without mutation. An empty workspace stays navigable. Workspace create/delete/rename are supported only when the native workspace adapter declares the operation; otherwise the labeled controls expose the unsupported state instead of implying parity. Any supported operation uses the same native receipt and recovery contract.

Menus and jump lists use secondary click or Menu/Shift-F10 and labeled keyboard controls. Escape dismisses the innermost scope first. Restore the surviving parent scope or identity-bound opener; if unavailable, use the eligible committed-MRU/desktop fallback. Never activate a replacement incarnation. Dense taskbar/group lists use bounded scrolling with a reachable overflow affordance; reveal keyboard selection and preserve configured order.

## Feedback, accessibility and preferences

P0 freezes numeric feedback and quiescence intervals alongside performance budgets, before candidate evaluation. After the feedback threshold, show accessible pending/reconciling status; preserve cancellation and independent controls. Success requires correlated native confirmation. Unknown outcomes permit observation/reconciliation, never blind replay. Refused menus remain open with the reason and reachable next action; explicit dismissal remains possible.

Every interactive control has native accessible name, role, state, value, relationships and supported actions. Pixels are decorative; restore controls are separately identified. Announcements do not move focus and repeated receipts do not repeat speech/braille output. Notifications use polite announcements by default, honor do-not-disturb, and only explicitly opted-in urgency may interrupt; expiration/action refusal announces when relevant to a focused or user-invoked notification.

System reduced-motion preference is the default. An explicit versioned user override wins; reset removes the override. Changes apply without restart at the next valid presentation opportunity, settling the existing transaction without replay or deadline reset. IME-consumed Enter/Escape/arrows cannot trigger shell submission or dismissal; composition generation and field identity prevent late writes.

P0 freezes measurable contrast, target/focus geometry and supported text scaling/reflow rather than choosing convenient thresholds after results. States carry non-color cues. Long labels, text enlargement and small outputs preserve reachable actions through wrapping, scrolling or labeled overflow. Numeric thresholds and user-tested usability results remain pending measurement, and block qualification until frozen and passed.

On output removal, dismiss displaced popups to eligible focus or rehost on the declared surviving output. Keep ordinary workspace identities; offer keyboard-reachable application recovery and reject removed-output generations. With no outputs, suspend presentation safely; reconcile/rehost when an output returns.

First-use guidance is dismissible, keyboard accessible and available again in help/settings. Preserve customized shortcuts; conflicts require an explicit choice rather than silent overwrite. Offline rollback instructions are available outside the Elm host. Onboarding completion is never needed to use the desktop.
