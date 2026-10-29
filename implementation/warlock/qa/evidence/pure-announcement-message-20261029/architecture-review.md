# AnnouncementMessage: remove the remaining authority-to-HTML import

Source-only proposal against `abe216442c84d858f0c676b48e9bf1704e14ce51`. Three proposed files are beside this document; `proposal.json` pins original and proposed bytes. Nothing is applied to product source; no compilation, tests, native execution or acceptance is claimed.

## Decision and observed benefit

Extract exactly the existing `Announcement.Message` record alias and `encodeMessage` function into `AnnouncementMessage`. `OutcomeAnnouncements` imports the pure value module. `Announcement` retains its public Message/encodeMessage aliases plus all decoder, receive and Html view behavior.

Current dependency: `OutputController -> OutcomeAnnouncements -> Announcement -> Html` and `Announcement -> SurfaceRenderer -> Html/PreviewVisual`.

Proposed dependency: `OutputController -> OutcomeAnnouncements -> AnnouncementMessage -> Json.Encode/UInt64`. Presentation still uses `Announcement -> AnnouncementMessage` plus its existing Html/SurfaceRenderer dependencies.

Static lexical traversal of the current `src/*.elm` import graph found Html dependencies reachable from OutputController only through this announcement edge. Substituting the proposed import removes all reachable Html/Browser imports from OutputController's graph. This is a bounded source observation, not a compiler/runtime proof; rerun against actual integrated bytes. Main remains a Browser entry point and is not claimed Html-free. Snapshot plus this extraction establish the intended pure authority/value boundary without renaming feature modules or changing policy.

## Exact scope and API

New `AnnouncementMessage.elm`:

```elm
module AnnouncementMessage exposing (Message, encodeMessage)

type alias Message =
    { interrupt : Bool
    , sequence : Counter
    , correlation : String
    , text : String
    }
```

The encoder body is copied verbatim, retaining object field order `interrupt`, `sequence`, `correlation`, `text`, canonical UInt64 string serialization, and exact input text. Its inferred extensible-record input signature is retained; do not accidentally narrow it with a new closed-record annotation. The conceptual signature is `{ a | interrupt : Bool, sequence : Counter, correlation : String, text : String } -> E.Value`.

This is an existing public record alias, **not** a newly opaque validated type. In particular, local construction and encoding do not enforce positive sequence, nonempty/bounded text or correlation. Decoder guards remain in Announcement at receive. Changing this into an opaque validated Message would require changing producers and callers and is outside this semantics-preserving slice. Do not claim encoder/decoder roundtripping for every constructible Message; zero sequence or empty/oversize text may encode today but fail the existing receiver decoder.

`Announcement.elm` changes only its Json.Encode import to AnnouncementMessage, its Message alias to `AnnouncementMessage.Message`, and its encoder to `AnnouncementMessage.encodeMessage`. Keep `strict`, `positive`, `bounded`, `scope`, `route`, `messageDecoder`, `receive`, and `view` byte-identical. Keep current alias exposure for public compatibility. `OutcomeAnnouncements.elm` changes only the import and two qualified references: Model's Message and encode's encoder. Observe/correlation/sequence/priority/DND behavior is unchanged.

Current source consumer inventory: OutcomeAnnouncements is the only production consumer of Announcement.Message and Announcement.encodeMessage. Bar/Popup depend on Announcement.Model/receive/view and need no source changes. OutputController depends on OutcomeAnnouncements and needs no source change. Existing replay modules consume OutcomeAnnouncements/OutputController and become integration witnesses. Do not migrate Announcement's SurfaceRenderer snapshot facade in the same slice: that is a legitimate presentation-to-render dependency and is unnecessary to remove the policy edge.

## Original scope

Use original ELM-UI-010 scenarios `announce-launch refusal`, `announce-transfer refusal`, and `announce-settings validation failure` as the bounded supporting slice. Their original verification still requires native/keyboard/AT observations where applicable, including speech/braille and no focus movement. This extraction supplies component equivalence only and closes no scenario by itself.

Keep the broader UI-010 announcement policy intact: ordinary notifications polite, critical interruption only with opted-in consent, DND/history/no replay, exact correlation and repeated receipt silence. Native owner, publication, lease, deliver bit and routing checks remain unchanged. Windows taskbar, application pin versus always-on-top, exact group target and loading/historical/live/unavailable previews remain unchanged invariants, not new claims.

## Smallest decisive verification

1. Fresh pinned build of actual Main, Bar and Popup as one asset package. Changed Announcement/OutcomeAnnouncements/new module invalidate the old three-root source receipt; never cite the snapshot `58eb...` report as a build of these new bytes. Confirm compatibility wrappers and current source/toolchain inventory.
2. Existing `qa/AnnouncementReplay.elm` against actual new OutputController/OutcomeAnnouncements: 12 source assertions include matched launch refusal, preserved query/open state, no requested focus, identity correlation, repeat silence, same words/new request -> fresh serial, foreign-binding refusal ignored, owner retirement no allocation, and transfer refusal. Use the reviewed feedback runner under the protected scope; preserve emitted frames/messages as well as booleans. Inspect current harness dependencies rather than automatically invoking the broad historical `check-search.py --announcements` chain.
3. Existing `NotificationAnnouncementReplay.elm` is a small additional policy witness for the shared encoder: ordinary/opted critical interrupt bits, no history replay, DND silence/history, batch identity and no requested focus. This is useful because a swapped/dropped interrupt field could otherwise pass refusal-only tests. No new model is needed for a pure value/encoder move.
4. A small actual-production encoder differential compares pinned old Announcement.encodeMessage (only private module rename) with new AnnouncementMessage.encodeMessage and public Announcement.encodeMessage facade. Seeded messages vary interrupt, exact counters (zero, one, adjacent >2^53, max), Unicode, quotes/backslashes, empty/control/oversized text and correlation. Require exact `E.encode 0` output equality, canonical sequence strings and exact text preservation; include at least one additional ignored record field to ensure extensible public API remains compilable. Invalid receiver strings are encoder-equivalence cases, not assertions that receiver admits them. Bound cases and seed explicitly, preserve full failing input and source/tool hashes; do not call fixed cases randomized sequence fuzzing.

The production receiver and Html tree are unchanged by exact source comparison. If an existing small receiver replay is already accessible, retain its exact-once/current-owner/publication/lease checks; do not fabricate AT or audible output from encoded messages or Html nodes. Browser/native/AT checks are only needed for their original acceptance claims, not to assert this purely structural extraction is equivalent.

Contracts: before encode, field types and Counter are defined; after encode, exactly four fields carry those values in original order; no state or effects change. Before outcome observation, existing authoritative Desktop state is supplied; after, correlation, sequence, message priority and effects must equal the prior implementation. The observation logic is not touched, so no new policy theorem is claimed. On failure retain the exact delta/counterexample; do not weaken receiver bounds or original policy to make equality pass.

## Integration and documentation

Root selects the contributor record and owns public source/README/QA/evidence updates. This private three-file patch is reversible as one source batch; preserve unrelated foreign files. After checks, update DEBT-02 with exact source/verification and residual scope, the architecture reference/explanation with the new value boundary, and wiki with the lesson that protocol data must not live in a view module. Graph update/eval and the end loop gate remain required. No requirement acceptance or root-cause repair is implied.

No further reviewer council, framework, toolkit change, generated protocol schema or native service is needed. One terminal source reviewer may independently check exact extraction and one existing harness owner may prepare the bounded encoder comparison when root selects the slice.
