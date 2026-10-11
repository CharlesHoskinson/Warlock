# Manifest-driven release build

ELM-DEL-003 `delivery-003` remains partial. The production builder verifies a
single local lock, rebuilds all three production Elm roots and eleven native
host units, runs native self-tests and nineteen compiled reducer checks, and
assembles a 26,030,080-byte archive with payload hashes and a relative native
pair manifest. The exact retained core/plugin/Aquamarine artifacts and required
Aquamarine loader alias survive packaging. No desktop session is activated.

The final protected observation has twelve checks and eighteen successful build
phases. All three Elm assets and the rebuilt host are byte-identical to existing
artifacts. A consumed Main.elm file in the private source snapshot was changed:
the builder rejected it before output creation, and restored bytes verified
without rebaselining. A changed tool symlink with identical target bytes also
refused. The persistent `implementation/warlock/build-lock.json` then verified
9,223 source/tool/package/header/library/provenance inputs in a separate protected
process. Its reviewed SHA-256 is recorded in this packet; the 4 MB lock is kept
once in the candidate rather than duplicated here. The generated archive remains
local at the recorded build path and is not a published release binary.

The archive uses fixed ownership, timestamps, modes and entry ordering. This is
one manifest-driven build, not the original two-isolated-offline-build campaign.
Complete compiler/build-tool upstream source provenance, closed offline input
inventory, SBOM/notices/redistribution disposition, full native/AT/IME/hardware/
resource acceptance, accepted Omarchy fallback, deployment and independent review
remain open. Byte identity preserves existing bounded artifact observations; it
never upgrades their scope to full release acceptance. No model or ordinary Elm/
native window authority changed. Quint's installed distribution/version and
sources are pinned for the existing workflow; no new reducer model was needed
for this artifact/build recipe change.

The earlier passing reports are historical: the first predates archive export,
and the second predates explicit Python bytecode-cache pinning. They are not the
current lock proof. Source.patch excludes only the large lock file, whose exact
bytes are committed directly and referenced by hash. All logs remain verbatim.
