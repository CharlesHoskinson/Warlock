# Warlock philosophy — design philosophy

The user selected **Warlock** on 2026-10-05. The technical principles below retain the ten-reviewer consensus. The original ballot and its former naming proposal remain immutable research history. Existing Elm requirement IDs, source paths and ABI names stay stable. These are design commitments; release capabilities still require their specified evidence.

## One sentence

Warlock keeps user intent, visible state and native behavior in agreement so people can work with confidence.

## One paragraph

Warlock treats desktop interaction as a commitment to the person using it. One coherent model records intent and observed state; typed events make changes explicit, and native authority determines what actually happened. The interface responds promptly, preserves context and distinguishes pending work, confirmed outcomes and uncertainty. Familiar conventions and coherent defaults reduce decisions, while customization preserves the same interaction guarantees. Accessibility belongs to every control, fluid motion respects attention and reduced-motion preferences, and background work has a measured cost. Failures remain understandable and recovery preserves unresolved obligations. We evolve the system through reproducible evidence, with qualified release and rollback paths.

## Manifesto

### 1. Optimize for confidence

People should know which window receives an action and whether its outcome is confirmed, refused or still unconfirmed. Keep targets, focus and outcomes understandable through rapid input, changing outputs and interruptions. Treat preserved user context as a design constraint.

### 2. Keep one coherent account of the desktop

Maintain one controller model of user intent and ordinary UI policy, with native facts held as read-only observations of native authority. Derive surfaces from it, make state changes explicit and keep effect descriptions inspectable. Immutable state and typed events serve this coherence; architecture choices must demonstrate their practical value.

### 3. Let native reality settle physical claims

The compositor and native services own input eligibility, window effects, pixels, clocks and physical resource lifetime. A sent request is a request. A confirmed effect, a displayed frame and a retired buffer each require their own evidence. UI timing cannot grant native authority.

### 4. Respond promptly and report honestly

Provide useful feedback while work is pending. Preserve the distinction between requested, committed, refused, cancelled, presented and unconfirmed. Explain unavailable actions and safe next steps in plain language. Preserve independent controls and never automatically replay Unknown or uncertain operations; reconcile with native truth first.

### 5. Make continuity part of correctness

Keep control identity stable through unrelated changes, and preserve eligible selection and focus as distinct states. Motion follows presented geometry and the user's current preferences. Support reversal where the operation permits it, and provide equivalent reduced-motion behavior. Appearance changes cannot silently change the target of an action.

### 6. Make accessibility a complete interaction path

Keyboard, pointer, speech, braille and input methods participate in the same behavior contract. Names, roles, states, focus and announcements must agree with available actions. Qualify the native route, including constrained geometry, text enlargement and composition. Announcements reach the user once under the frozen attention policy, without moving focus.

### 7. Design ownership and recovery together

Every admitted resource has an owner and a path to release. Cancellation requests start cleanup; they do not prove it completed. Restart and reconciliation preserve unknown outcomes, replay protection and original deadlines. Prepare a working recovery path before introducing a new failure mode.

### 8. Provide coherent defaults and principled customization

Choose familiar, consistent defaults for everyday work. Publish the rules that shortcuts, menus, focus and disabled controls follow. Allow deliberate customization while retaining identity, accessibility, privacy and recovery guarantees. A setting should change its declared behavior predictably.

### 9. Spend resources deliberately

Keep queues, retained history, captures and diagnostic records bounded through explicit admission and proof-safe reclamation. Never forget unresolved outcomes, cleanup obligations or replay floors to make space. Give control and cleanup traffic the capacity to progress. Pace visible-consumer work under a frozen policy and suspend unnecessary recurring work when no consumer needs it. Diagnostics contain only allowlisted facts, never secrets, draft content or pixels, and never act as authority. Measure responsiveness, memory, CPU and power across the whole process group on supported hardware.

### 10. Make evidence govern change

Write observable contracts before changing behavior. Use models to explore races, replay to expose regressions and native observations to qualify the actual system. Preserve failed experiments and distinguish evidence levels. Ship a coherent, reproducible release with a tested rollback path.

## Decision rule

Prefer the simplest change that improves confidence and continuity while preserving native authority, accessibility, bounded ownership and recoverability. If a tradeoff weakens one of those commitments, state the affected contract, measure the consequence and resolve it before release.

## Traceability for reviewers

- Confidence/coherence: ELM-ADOPT-001–008,016,017,020,025.
- Native truth and ownership:009,010,021,025–028.
- Continuity/accessibility:012,016–020,023,029,030.
- Recovery/privacy:002,003,009–015.
- Resource discipline and evidence:001,004,005,013,021–028 and existing release-closure gates.

The [Rails Doctrine](https://rubyonrails.org/doctrine) is an example of explicit priorities guiding a framework; these principles are derived from this project's contracts rather than copied from Rails. The Warlock name and visual identity do not add release gates or establish competitive superiority.
