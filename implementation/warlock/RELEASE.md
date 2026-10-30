# Building the local release candidate

`adapter/release_builder.py` owns a fixed build recipe and a hash-verified input
lock for ELM-DEL-003. It builds Main, Bar and Popup, recompiles all eleven native
host units, runs the host self-tests and a compiled reducer regression, and
assembles `warlock-candidate.tar`. It retains the separately qualified exact
core/plugin/Aquamarine artifacts; it does not rebuild or replace that ABI pair.

The lock records candidate sources and adapters, Elm compiler/package files,
Python/Node/Quint build and test tools, compiler helpers, native headers and
libraries, package-config metadata, versions, relevant search environment,
artifact symlink identities and the native pair's build provenance. The builder
checks every recorded hash before creating output, rediscovers header resolution,
copies a fresh source/package snapshot, and verifies the original inputs again
after building. A changed consumed source or tool/library alias refuses rather
than silently producing a new baseline.

Capture, verification and builds invoke compilers and require the unchanged
protected launcher. The current checkout uses these paths:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B \
  /home/hoskinson/omarchy-windows-parity/implementation/warlock/adapter/release_builder.py \
  verify --lock /home/hoskinson/omarchy-windows-parity/implementation/warlock/build-lock.json \
  --sha256 REVIEWED_LOCK_SHA256
```

Use `build` instead of `verify` and add `--output /absolute/new-build-directory`
to create a package. Substitute the reviewed lock hash from the retained evidence;
do not rebaseline a mismatch. The output directory must not already exist. Source
changes, dependency upgrades or changed search environment require an explicitly
reviewed new lock, captured with `capture --repo /absolute/repo --output
/absolute/new-lock.json` through the same launcher. Capture never overwrites an
existing manifest. A different machine needs a reviewed equivalent protected
launcher and matching local input cache; this manifest is not a dependency
installer or permission to update the compiler.

The output includes raw command logs, a build report, compiled artifacts and a
package directory. `MANIFEST.json` inside the archive records payload hashes and
the native pair with relative paths. The Aquamarine loader alias is retained.
Archive entries use fixed ordering, timestamps, ownership and modes; local build
paths and raw logs stay outside the distributable. This deterministic assembly
does not prove two clean isolated offline rebuilds until that campaign runs.

`adapter/release_repro.py run` runs the complete recipe twice in fresh Bubblewrap
network, mount, PID, IPC and UTS namespaces. It copies only locked canonical
files and recorded filesystem aliases into a verified input snapshot, mounts
that snapshot read-only, and gives each build a separate empty output directory
and temporary filesystem. Both recipes receive the same `/build` path; no host
package directory, desktop socket or mutable cache is exposed. ELF interpreter
lookup paths and implicit compiler link inputs belong to the lock too.

Run it through the same protected launcher, replacing the builder command above
with this command and supplying a new absolute output directory:

```sh
/usr/bin/python3 -B \
  /home/hoskinson/omarchy-windows-parity/implementation/warlock/adapter/release_repro.py \
  run --lock /home/hoskinson/omarchy-windows-parity/implementation/warlock/build-lock.json \
  --sha256 REVIEWED_LOCK_SHA256 --output /absolute/new-reproducibility-directory
```

The command verifies the reviewed lock before staging, checks isolation against
a listening parent socket and a host-only marker, and verifies inputs within
each build before and after compilation. The report retains namespace/core-limit
observations, the input snapshot identity, both build logs and SHA-256 comparisons
of actual payload files and archives. A build failure, input identity difference,
changed recorded artifact or distributable mismatch blocks release and returns
nonzero. Matching hashes qualify this build observation only; other release
gates and independent acceptance remain separate.

The original protected build reproduces the existing Elm assets and native host
bytes. Its direct reducer and native self-tests pass. A real consumed source
alteration is rejected before output creation, and restoration verifies against
that original lock. See [the input-lock evidence](qa/evidence/release-input-lock/README.md).
The subsequent [offline campaign](qa/evidence/offline-reproducibility/README.md)
rebuilds the updated locked recipe in two fresh isolated filesystems, compares
all payload and archive hashes, and exercises deliberate archive, payload and
same-content loader-alias mismatches. The original input-lock packet remains
historical; the new packet identifies the current lock and source tuple.

The builder now requires the [component and notice review](release/COMPLIANCE.md)
before packaging. Its catalogs pin source evidence and exact payload ownership;
unknown dispositions block the archive and retain a diagnostic report. A passing
gate includes the SBOM, notice texts and disposition records, followed by an
exact archive audit bound to the original in-memory review receipt. Later
payload or metadata changes refuse even with a matching rewritten manifest and
archive. The initial catalogs remain unapproved, and the historical
lock cannot authorize this changed recipe. Focused protected checks cover the
production gate and mutation refusals; a real candidate cross-check remains open.

The package is explicitly **not installable or release accepted**. Complete
compiler/build-tool upstream source provenance, SBOM and redistribution notices,
independent reproducibility review, full native/AT/IME/hardware/resource acceptance,
accepted Omarchy fallback and main-session deployment remain required. Preparing
this archive neither activates a shell nor restarts the compositor. Use the
[offline recovery contract](RECOVERY.md) when preparing the eventual reviewed
component launch and rollback routes.

For a reviewed derivative native tuple, `capture` additionally accepts both
`--native-tuple /absolute/tuple.json` and `--native-tuple-sha256 SHA256`.
Without these flags the original historical pair remains the default. The
selected tuple must describe the core, authority plugin, Aquamarine, host,
source/build reports and exact private loader alias; their recorded inputs are
checked and captured. The new lock preserves the selected host and Elm asset
identities and refuses a rebuild that changes them. Capture is not acceptance:
current native build receipts do not attest every original core/Aquamarine
compiler, source and dependency input, and complete provenance remains open.
Unknown redistribution dispositions continue to block the actual package.

Use the unchanged protected launcher from this checkout, with
`PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=/home/charles/Warlock/window-integration-qa`.
Capture a *new* reviewed lock; never overwrite the frozen historical lock. Run
`qa/check-release-tuple.py /absolute/tuple.json SHA256` through that same
launcher to check the actual selection and refusals. After independent review,
use the resulting reviewed lock hash for `release_repro.py run`; two clean
isolated offline builds and a full SBOM/notice review remain separate gates.
The capture environment must resolve both the selected core and plugin to the
selected Aquamarine SONAME alias. Set the reviewed private library search path
before capture; it is locked and must be identical during verify/build. A
same-SONAME system library, changed alias or changed resolution is refused.

## Current frontend recipe

`adapter/current_build.py` provides capture/build/validate for a separately reviewed current frontend lock and report. It preserves the historical release builder's native tuple and asset equality checks; its three-root output is not an accepted release package. Follow the [current frontend procedure](../../docs/warlock/how-to/build-current-frontend.md). Native host object composition/ABI/provider identity, upstream source provenance, offline two-build reproducibility and compliance remain separate.
