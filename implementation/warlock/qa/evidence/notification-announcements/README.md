# Notification arrival permission

The notification center now has session DND and explicit critical-interruption consent controls. Ordinary arrivals are polite; critical arrivals are polite until opted in, and assertive only while DND is off. DND keeps history/actions without producing a new announcement. Changing a preference never replays suppressed or previously observed history. The controls expose pressed state and retain keyed identity. Preferences reset with the Elm shell session; persistence is not promised.

Native reads the standard BYTE urgency hint and retains Low/Normal/Critical facts. Malformed types/values cannot elevate urgency. Critical notifications no longer expire automatically; explicit user/producer lifecycle actions still retire them. Elm owns interruption permission. Native validates only the declared single route and forwards each serial once.

## Observations

The actual compiled root passes fourteen typed checks for baseline/history, new identity, repeated observations, DND suppression, consent, no Focus command, strict urgency and integrated controls. A batch retains every fresh incarnation in its correlation and bounded summaries with a route to details. Mixed-urgency batches remain polite. Stale/repeated input does not announce.

The three-view browser fixture passes the original twelve refusal/owner/repetition/retirement checks and eight additional notification-control/delivery checks: actual keyboard action, pressed state, retained focused control, DND history/no replay, single polite/unopted critical owner, opted critical assertive owner and ordinary politeness with consent enabled. Native session-bus component checks retain every original producer/action/expiry/Unknown/no-replay oracle and add standard urgency, malformed-hint no escalation and critical nonexpiration observations.

The original protected native notification journey passes its action dispatch, other producer isolation, expiry, queued old-incarnation refusal after numeric ID reuse, new-incarnation-only action, actual history text pixels, Escape/no window effect and normal owned cleanup checks. The additional physical-keyboard/real-producer journey observes:

- DND history updates with no new native announcement serial.
- Turning DND off does not replay the suppressed incarnation.
- An unopted critical arrival has one polite region.
- An opted critical arrival has one assertive region.
- An ordinary arrival remains polite while critical consent is enabled.

Each emitted message matches the actual binding/service/admitted revision/incarnation. Native forwarding is once per serial and the real WebKit popup shows the corresponding polite/assertive region. Across the added arrivals the same actual focused DOM node, its control identity and document focus are retained. The initial failed assertion compared the changing event-stamped DOM ID; QA now uses a WeakMap node identity plus the semantic control identity, preserving the original focus oracle. Existing keyboard/action/deadline assertions are unchanged. `native-history.png` is the original history capture, not a speech/braille or all-control visual qualification.

## quint-llm-kit mapping and limits

The additive single-actor model was built and executed incrementally before code using quint-llm-kit’s modeling and implementation workflow. Ten explicitly selected named tests pass; all eight selected witnesses are reached during 1,000 sampled safety traces of up to 30 steps, seed 79502. Historical permission/consent is captured per identity so later preference changes cannot weaken the invariant. Focus remains unchanged and each admitted identity is counted once. Existing announcement-owner, notification action and focus models retain their original properties.

`arrival` maps to strict Notifications observation and fresh-incarnation selection; `dnd`/`optIn` to stamped ConfigureNotificationPolicy messages from actual controls; `sequence`/historical permission to OutcomeAnnouncements; baseline/repetition to admission/no replay. The separate existing owner model and concrete native guard tests cover delivery ownership. The new model abstracts an atomic admitted observation, opaque bounded IDs and a single arrival. It omits byte decoding, multi-entry coalescing, queues/transport loss, process recovery, timing, speech/braille and hardware/resource budgets. Concrete typed/native checks cover some of these boundaries without upgrading the abstraction to acceptance.

The selected three ELM-UI-010 scenarios remain partial. Actual speech and braille under the original stable-focus fixtures, repeated delivery through AT, native AT recovery/relationships and independent original acceptance remain missing. Native batch/coalescing stress and full physical control/profile qualification are separate unfinished observations. Relevant notification expiration/action-refusal and adapter-unavailable announcements remain unimplemented/unqualified; full UI-010/DL-011 and release acceptance are open.

The [freedesktop hints](https://specifications.freedesktop.org/notification/latest/hints.html) and [urgency levels](https://specifications.freedesktop.org/notification/latest/urgency-levels.html) were checked against primary documentation. The candidate makes DND suppress all arrivals and labels critical permission as applying only when DND is off. No policy is inferred from text or counts.

The manifest retains exact originals, current declared source/compiled/ABI hashes and reproduction commands. Failed incremental model/compiler/reuse/readiness/focus-fixture reports remain locally with hashes in `failures.json`; the original specification was not relaxed. The base source commit precedes this delta and is not an acceptance claim. The main desktop was unchanged.
