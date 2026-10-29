---
title: "Architecture research landing"
created: 2026-10-29
updated: 2026-10-29
tags: [warlock, architecture, evidence]
category: topic
volatility: hot
sources: [raw/notes/2026-10-29-knowledge-space-and-delivery-observation.md]
summary: "Pending primary-source GNOME/KDE/Elm synthesis, with explicit historical/current distinctions and migration questions."
---

# Architecture research landing

Status: the [reviewed Elm architecture study](../../../../docs/warlock-build-loop/v2/ELM-ARCHITECTURE-RESEARCH.md) is now available. Root and Astra reviewed its prerequisite-observation wording: a receipt alone may not prove mutation or presentation. The study is evidence-linked research and proposed design, not target adoption, a completed refactor or native acceptance. No private brief or full paper is copied here.

## Reviewed findings and primary reading

The study recommends retaining current Elm 0.19 TEA: explicit model/message/update, commands and subscriptions, typed ports, meaningful domain modules and validated opaque values. Historical `Signal`, `lift` and `async` examples describe older research, not APIs to introduce into the current application. No additional reactive framework is implied.

Its primary reading is Evan Czaplicki’s 2012 *Elm: Concurrent FRP for Functional GUIs* thesis; Czaplicki and Stephen Chong’s PLDI 2013 *Asynchronous Functional Reactive Programming for GUIs*; Conal Elliott’s 2009 *Push-Pull Functional Reactive Programming*; and Neelakantan Krishnaswami’s ICFP 2013 *Higher-Order Functional Reactive Programming without Spacetime Leaks*. The [reviewed article](../../../../docs/warlock-build-loop/v2/ELM-ARCHITECTURE-RESEARCH.md#papers-to-study-in-order) links primary full texts and separates their semantics from Warlock-specific inferences. Their questions about asynchronous responsiveness, demand, retained history and lifetime ownership guide design; none proves native scheduling, zero-copy, retirement or a renderer repair.

The concrete first proposal is an opaque pure `SurfaceSnapshot` value/codec extracted from `SurfaceRenderer`. It would remove a direct policy-to-HTML dependency while preserving wire shape, validated identity, accessors and authority. A residual path through `OutcomeAnnouncements` → `Announcement` still reaches HTML and is explicitly a later seam; the first extraction cannot make the whole policy graph HTML-free. Existing local-edit/pending-query behavior must be preserved, not silently strengthened by a new blanket publication or bounds rule. Normalized valid encode/decode idempotence is distinct from raw encoding identity; duplicate-key checks belong at the raw parser boundary.

Ordered effects require the correlated prerequisite observation demanded by their protocol, not `Cmd.batch` order or any receipt alone. Atomic decoded packets are not atomic native transactions across ledger, mutation, surface opening, queue and teardown. These are constraints for a selected staged migration, not claims every current route already satisfies them.

## Questions the synthesis must answer

1. Which actual Warlock module owns each state transition, effect, subscription and native lifetime? Where do presentation roots project state, and where would a refactor accidentally create a second policy authority?
2. What do official GNOME Shell/Mutter/GJS and KDE Plasma/KWin/Frameworks sources teach about compositor, frontend and service ownership? Which toolkit or UX coupling should Warlock reject?
3. How does current Elm 0.19 TEA structure models, custom types, commands, subscriptions, ports and module boundaries? Which historical Signal-era FRP claims concern glitches, space leaks or asynchronous scheduling, and which do not describe current Elm?
4. How do those lessons apply to actual input/focus routing, output/authority identities, preview custody/retirement and effects that must not replay after Unknown or restart?
5. What is the smallest reversible production extraction, with exact paths/interfaces, invariant correspondence, source provenance and meaningful regression checks? Why is it preferable to a larger rewrite?

## Evidence policy

Use official documentation and primary author/conference full texts; read the material and distinguish quoted claims from architectural inference. A list of papers is not a design. Preserve exact links, versions/commits where relevant and known limits. Historical Elm Signals are not a recommendation to use removed APIs in Elm 0.19. GNOME/KDE are architectural references, not replacements for the required Windows-like interactions.

The staged plan must preserve 242/417, persistent pins/order, exact group selection, authorized historical/live preview distinctions, typed protocol and deadlines, no duplicate effects, grants/incarnations, AT/IME, drafts and reversible deployment. Current renderer and first-use failures remain unresolved by research. Review architecture at sprint boundaries and integration batches; publish only reviewed owned changes through the standing loop.

## Sources

- [Authorization, original scope and current evidence limits](../../raw/notes/2026-10-29-knowledge-space-and-delivery-observation.md)
- [Standing architecture process](../../../../docs/warlock-build-loop/v2/ARCHITECTURE-REVIEW.md)

## Web tool preference

The user explicitly requires Scrapling for browsing/downloading web sources. Root verifies uv tool `scrapling[fetchers,rag]` 0.5 and the `scrapling` / `scrapling-mcp` commands, with an actual GET 200 of official Elm modules markdown. Preserve existing primary sources without unnecessary refetch. The rag extra resolves the initial markdownify dependency failure. Keep installation verification separate from research conclusions.

## Refactor contracts and fuzzing

The standing [fuzzing and Elm contracts workflow](../../../../docs/warlock-build-loop/v2/FUZZING-CONTRACTS.md) applies to the selected extraction. State validated construction and unchanged wire/accessor/admission invariants before changing the type boundary. Test actual production routes with reachable valid controls and malformed/boundary/sequence cases where applicable. Record reproducible seeds, budgets, source/tool/generator versions and retained minimized failures. Opaque types, successful fuzzing and model sampling do not establish original native acceptance. No elm-test installation or product test dependency is claimed by this article.
