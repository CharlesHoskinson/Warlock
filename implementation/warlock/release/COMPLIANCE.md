# Package component and notice review

ELM-DEL-005 / `delivery-005` requires the release package's shipped components,
applicable upstream notices and redistribution dispositions to be accounted for.
The production builder now has a strict component-review gate. It does not
establish permission or release acceptance from a recorded hash or a `reviewed`
label.

`adapter/release_compliance.py` inventories actual payload files and symlink
spellings, checks their identities against the two component catalogs, verifies
source and notice bytes, and returns a deterministic report. Every payload file
has one catalog owner. A generated bundle can contain several components through
explicit `contains` relationships; embedded shipped components must be reachable
from a component that owns a shipped file. Build components are recorded
separately and cannot own payload files. The five original categories—compiler,
packages, host, native libraries and assets—must be represented.

The catalogs are `native-components.json` and `language-components.json`.
Provenance paths are relative to the repository; notice paths are relative to
both the candidate and packaged payload. Notice texts under `notices/` retain
their source bytes. A component without notices requires an explicit reviewed
notice-applicability disposition. Missing provenance, unreviewed dispositions,
unaccounted files, conflicting ownership, changed notices and unsafe links block
the gate. Catalog assertions remain subject to independent review.

`release_builder.py` captures the catalogs, compliance implementation, notice
files and referenced provenance as locked inputs. A new lock records its source
root explicitly so a relocated build candidate still checks the same evidence.
The old frozen lock lacks these inputs and cannot authorize a new package.
Changing those historical bytes or silently blessing a different native tuple
is not a recovery procedure.

Before creating an archive, the builder copies the notices into the payload and
writes `compliance-report.json` alongside the build output. A failed review
retains that report and refuses packaging. A passing review adds these files to
the payload:

- `release/compliance/SBOM.json`: component inventory and pre-metadata payload
  identities, including the stated inventory boundary.
- `release/compliance/dispositions.json`: the component disposition records.
- `release/compliance/review.json`: the complete deterministic review result.

The builder retains an immutable in-memory receipt containing the reviewed
payload identities and the original generated metadata hashes. The final audit
requires that receipt for a compliance-bearing package and compares it with the
actual files again. Rewriting a later manifest and archive cannot bless changed
assets, notices, metadata or symlink spellings. The audit also reruns safe
inventory checks, so matching transport metadata cannot admit an escaping link.

The package manifest then hashes the generated metadata. The archive audit
compares exact member names, types, bytes and symlink spellings against the
payload and manifest, including the manifest itself. This separate boundary
avoids circular self-hashes. It rejects duplicate archive members and changed or
missing contents.

The Quint companions exposed the earlier review-to-manifest gap with actual
production functions before the receipt fix. Their corrected correspondence
checks retain that observation and require refusal after the fix. The models
cover ownership, provenance/notices, packaging phases, transport identities and
composition using bounded domains, explicit tests and sampled runs. Several
snapshot invariants restate their atomic decision conditions; these establish
conditional model consistency, not an independent semantic proof of Python,
filesystem concurrency or the full desktop. Intra-function and future external
mutations remain outside that assurance. Output is privately owned, and a
successful audit is a point-in-time observation.

## Current disposition

The retained catalogs deliberately report unknown dispositions. The historical
core, authority plugin and Aquamarine artifacts named by the current pair are
absent from this checkout; archived substitutes have different hashes. Complete
native source correspondence, the compiler binary's correspondence with its
upstream source, applicable project grants and independent redistribution review
remain unresolved. The external build-tool and system-library inventories also
retain their review gaps. The copied notices and pinned package sources provide
bounded evidence, not an approved distributable.

`INDEPENDENT-REVIEW.json` records the independent review and missing original
observations. A real candidate package and its archive still need to be
cross-checked after a coherent source and native tuple is available. Existing
native, AT/IME, hardware, resource, journey, deployment and rollback gates remain
separate.

## Focused verification

Run the actual production API, builder integration and independent mutation
checks through the unchanged protected launcher. On this checkout, set
`PYTHONDONTWRITEBYTECODE=1` and
`PYTHONPATH=/home/charles/Warlock/window-integration-qa`, then invoke
`window-integration-qa/qa_run.py -- /usr/bin/python3 -B` with one of:

- `implementation/warlock/qa/check-release-compliance.py`
- `implementation/warlock/qa/check-release-compliance-integration.py`
- `implementation/warlock/qa/check-release-sbom.py`

These checks exercise real production functions with controlled payloads,
including refusal and restoration cases. Their success does not build or accept
the missing historical native tuple, qualify a real release, or make a legal
determination. Preserve failed observations as well as passing evidence.
