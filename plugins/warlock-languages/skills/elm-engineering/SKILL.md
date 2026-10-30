---
name: elm-engineering
description: Implement or review Elm GUI, pure update functions, JSON decoders, commands, subscriptions and accessible views against Haskell backend contracts.
---

All Warlock GUI elements are Elm. Haskell owns backend and reviewed native/runtime
integration. Read current ownership and wire contracts before changing a boundary;
never create competing GUI/backend authority for the same window effect.

Keep Model/Msg/update pure. Represent lifecycle, permission and receipts with
custom types and opaque validated constructors. Decode external values explicitly;
unknown fields, versions, mismatched identity and stale epochs must follow the
actual contract. Represent full-width native identities without Float rounding.
Views and retained history cannot mint native execution or replay permissions.

Commands describe effects; subscriptions follow real consumers and owned active
transactions. Sequence dependent effects using correlated receipts, not incidental
batch order. Keep original deadlines and distinguish Unknown from refusal or
cancellation. Revocation and control delivery must survive popup dismissal.

Use semantic HTML, keyboard routes and identity-bound focus scopes; preserve IME
composition and native accessibility requirements. Decorative presentation must
not change hit testing or native resource ownership. Elm compiler output is a
build artifact, not a reason to add another authored GUI policy layer.

Compile actual owning Elm roots with the pinned project compiler through protected
QA. Exercise the production update/decoder/view path, positive reachability and
stale/duplicate/disconnect cases. Use elm-test fuzzers or equivalent reviewed
property/sequence harnesses with retained seeds and counterexamples; use Quint
for authority/ordering invariants and map its abstractions to actual source.
A replay or typecheck does not prove native input, AT, IME, resource or whole-EARS
acceptance. Preserve failures and requalify changed source tuples.

Fetch current primary APIs with Scrapling: https://guide.elm-lang.org/ and
https://package.elm-lang.org/ . Publish design ideas and source-bound observations
in the living wiki; coordinate source ownership and protected QA through AgentBus.
