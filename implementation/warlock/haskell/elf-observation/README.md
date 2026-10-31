# Declared ELF observations

This Haskell preparation library parses bounded GNU readelf 2.47 captures and
checks an explicitly supplied ELF dependency graph. It performs no process launch,
filesystem discovery or dynamic loading. It does not admit a runtime or prove GUI
behavior. The source is the qualified private parser/graph baseline; the newer
source-to-namespace placement adapter remains separate pending qualification.

## API reference

`Warlock.Elf.Readelf.parseReadelf` requires a `Capture` attestation and complete
bounded ASCII output from the selected readelf invocation. It retains interpreter,
SONAME, ordered dependencies, dynamic flags, program headers and version records.
The parser checks the supported textual grammar; it does not validate arbitrary ELF
bytes or establish the caller's capture provenance.

`Warlock.Elf.Graph.resolveDeclaredWithSearchPlans` accepts caller-selected `Input`
objects, limits, source-bound `OriginWitness` values and per-object `SearchPlan`
values. It checks class, byte order, machine, SONAME and required version names.
A PIE may be the root but cannot satisfy a shared-library edge. An invalid first
candidate refuses; search does not fall through to a later candidate. Per-object
search plans do not propagate to children. The legacy entry points retain their
conservative refusal behavior.

The returned graph retains runtime and search obligations. Symbol precedence,
relocations, TLS, NODELETE, namespace placement, helper/config/device inputs and
physical resource lifetime require separate evidence. The baseline supports only
its explicit narrow `$ORIGIN` contract; a source path is not a namespace witness.

## Caller how-to

Collect source identities, byte counts and hashes through the reviewed held-file
resolver and fixed-tool owner. Supply the corresponding complete readelf captures;
never construct a capture-completeness assertion from a truncated log. Declare
only selected providers and their controlled search order. Handle `Left` as an
unresolved observation, retain failures, and review every returned runtime/search
obligation before using the result in a launch plan.

Build and test this package through Warlock's protected CPU QA launcher. It needs
GHC 9.6.7 and installed base, bytestring and containers dependencies; the public
package adds no package-index or native-library dependency. Its pure controls use
in-memory captures, including malformed metadata and unsafe search/ABI cases.
See [qualification.json](qualification.json) for exact source and evidence scope.
A tutorial for a runnable window awaits the integrated host and native observation.

## Ownership explanation

The caller owns provenance and provider selection; this library owns bounded text
and declared-edge validation. The process owner, namespace launcher and native
authority retain their own distinct responsibilities. A graph success cannot
replace any of those contracts or accept an original EARS scenario.
