# Aletheia: design inventory and research adoption

Aletheia is the working name for the window system. The philosophy is in [PHILOSOPHY.md](PHILOSOPHY.md). Naming is an editorial proposal; technical Elm IDs and source/ABI paths remain stable.

This packet records ten actual independent reviews: five gpt-6.1-sol reviewers and five claude-opus-5-5/high CLI reviewers, paired across immutable state, typed events, error reporting, accessibility/UX and fluid interaction. Source snapshots, initial reports, votes, corrections and execution provenance remain separate. [CONSENSUS.md](CONSENSUS.md) records explicit convergence:29 guarded refinements,015 deferred, all ten philosophy/remaining-work votes and all ten endorsements of the final030 scenario correction. [Validation](qa/validation-20261005T102253587812Z/report.json) passed28 structural checks and strict OpenSpec1.14.0 validation of both changes; the earlier failed formatting check is preserved.

## Design and evidence

[INVENTORY.md](INVENTORY.md) records the frozen design and limitations. The 338 input files are hash-bound in source-manifest.json. Modern Elm uses immutable models, typed messages and pure updates, with a single controller and derived bar/popup views. Native services own physical effects, authentication, pixels, clocks and resource retirement. The architectural distinction matters: [Elm commands do not guarantee batch ordering](https://package.elm-lang.org/packages/elm/core/1.0.5/Platform-Cmd#batch); dependent effects require authenticated protocol evidence.

The existing GUI has component and bounded native evidence. Production preview integration, original preview/restore/recovery/drag cases, hardware and native AT/IME, measured budgets and a coherent reversible release still require qualification. This packet neither edits runtime code nor closes those gates.

## Research choices

The literature supports explicit state-and-command refinement, complete isolated replay and bounded persistent state. [Model-View-Update-Communicate](https://doi.org/10.4230/LIPIcs.ECOOP.2020.14) illustrates how effects and protocols can be typed, but its Links/linear-typing theorem does not transfer to our Elm/native boundary. [Trace validation against TLA+](https://arxiv.org/abs/2404.16075) motivates checking concrete execution against explicit abstractions; sampled model success is not native acceptance. [Okasaki's persistent structures](https://www.cs.cmu.edu/~rwh/students/okasaki.pdf) inform immutable sharing while retained roots still require a measured history and memory policy.

We adopt the applicable contracts into our present architecture: strict typed boundaries, operation-specific dependency evidence, proof-safe reclamation, truthful uncertainty, localizable error catalogs, private bounded diagnostics, stable control identities, complete native accessibility, presentation-aware motion and paced visible-consumer capture. The tradeoffs are schema/fixture maintenance, retained reconciliation state, explicit dependency metadata and hardware qualification cost. Conditional caching requires demonstrated benefit; new local diagnostic export remains deferred. No recommendation alone adds a mandatory baseline gate.

## Work and specifications

- [ADOPTION-EARS.md](ADOPTION-EARS.md) / [requirements.json](requirements.json): additive research contracts, exact scenarios and provenance.
- [WORKPLAN.md](WORKPLAN.md) / [WORKPLAN.json](WORKPLAN.json): mapping to the existing twelve FRP work items.
- [REMAINING-WORK-EARS-V2.md](REMAINING-WORK-EARS-V2.md) / [remaining-work-v2.json](remaining-work-v2.json): original 242 requirements and 417 scenarios mapped exactly once to release packages, plus separate right-click 24/48 and draft closure contracts.
- [Research OpenSpec](../../../../openspec/changes/elm-design-adoption/proposal.md): research adoption draft.
- [Release-closure OpenSpec](../../../../openspec/changes/elm-release-closure/proposal.md): remaining release qualification draft.

Existing main baseline and in-flight OpenSpecs stay authoritative. All implementation tasks remain unchecked. Drafts require reviewed integration before promotion; model, replay, CPU, browser, native, hardware and accessibility evidence remain distinct.

The build-loop checkpoint records this consensus as progress, with production provider integration and original release gates still open. Existing user authorization supports internal review and implementation; the research drafts introduce no new user permission step. Versioned ballot/draft status strings describe their historical review stage; CONSENSUS.json records the final disposition.
