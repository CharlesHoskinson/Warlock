---
name: haskell-engineering
description: Implement or review Haskell pure policy, typed contracts, effects, STM and Cabal projects; use for Haskell production code and Haskell diagnostics.
---


Use current Elm/Haskell architecture and original requirement/scenario oracles.
All GUI is Elm; Haskell owns backend policy and reviewed native integration.
Preserve historical source/evidence without transferring acceptance to new code.
Use protected QA for builds, models, fuzzing and native checks; coordinate through
AgentBus, fetch primary sources with Scrapling and record ideas/results in the wiki.

Read the Cabal project and GHC version first. Keep pure transition/reducer policy
separate from IO interpreters. Use newtypes/smart constructors and algebraic data
types to make invalid states unrepresentable. Keep public signatures explicit;
prefer total pattern matching and Either/Maybe to partial functions or error.
Use typeclasses, type families and extensions only when they clarify this domain.

Bracket acquired resources and mask asynchronous exceptions only around the small
ownership transition that requires it. Model concurrent shared state with STM
where appropriate; do not perform arbitrary IO inside retryable transactions.
Bound queues, retain task ownership and distinguish cancellation requests from
observed native retirement. Use strictness and profiling based on measured leaks,
not blanket strictness or speculative optimization.

Check with cabal build all and cabal test all using the project's pinned compiler
and dependency plan through protected QA. Enable -Wall, -Wcompat,
-Wincomplete-uni-patterns and -Wincomplete-record-updates; keep warning policy
explicit for project code. Use HLS with the matching GHC, Fourmolu formatting and
HLint. QuickCheck/Hedgehog properties should express requirements, not mirror the
implementation; compare the interpreter to the formal model where applicable.

Primary references: https://cabal.readthedocs.io/ and
https://haskell-language-server.readthedocs.io/ . Consult current primary APIs
through Scrapling. HLS diagnostics and pure properties do not prove native IO.
