# Read a retained result without rerunning it

Use this guide to assess a recorded claim before choosing verification or reusing evidence. You need the checkout, Python's standard library and Git. Reading JSON, hashing retained bytes and inspecting a ledger do not compile or run a campaign. Never execute a copied `executed-*.py` file merely because it appears in an archive.

## Start with the original and its disposition

From the repository root:

```sh
python3 -B plugins/warlock-contributor/scripts/warlock.py --repo "$PWD" \
  inspect --requirement ELM-ARC-007 --scenario receipt-committed
```

Read the original oracle and verification permission separately from the ledger result. For this example, the [acceptance record](../../warlock-build-loop/v2/receipt-committed-acceptance-20261030.json) binds the allowed production bridge evidence to immutable source `a4168e63302ba0872c49e62cd4a3e76144ed1efa`; it is not proof that native code was loaded. The [lifecycle limits](../../../implementation/warlock/qa/evidence/receipt-output-lifecycle-20261030/LIMITS.md) retain the RED baseline, corrected route and finite coverage. Whole ARC007 and cancellation remain separate.

## Verify the retained archive's bytes

This concrete example checks the [receipt-corrected composition archive](../../../implementation/warlock/qa/evidence/receipt-current-composition-20261030/manifest.json). It reads files only:

```sh
python3 - <<'PYTHON'
from pathlib import Path
import hashlib, json
root = Path("implementation/warlock/qa/evidence/receipt-current-composition-20261030").resolve()
manifest = json.loads((root / "manifest.json").read_text())
for name, expected in manifest["files"].items():
    path = (root / name).resolve(strict=True)
    assert path.is_relative_to(root) and path.is_file(), name
    data = path.read_bytes()
    assert len(data) == expected["size"], name
    assert hashlib.sha256(data).hexdigest() == expected["sha256"], name
print("Retained files match:", len(manifest["files"]))
PYTHON
```

The selected archive has 21 entries. A mismatch is a finding; retain the report and investigate the source of the difference. Do not regenerate the manifest over changed files, repair raw compiler whitespace or silently replace old reports. This command establishes manifest-to-current-file equality only. It does not independently authenticate the manifest, prove every reported input was consumed, or revalidate a runtime that references external machine paths.

## Distinguish three different source questions

1. **Which source was tested?** Read the executed driver, source/input hashes, command records and independent review. A successful build recipe is different from an actual native journey.
2. **Is that immutable source recorded?** For an acceptance claim, compare the claimed full commit and Git blob hashes. `git show FULL_COMMIT:repository/path` reads the recorded source without checking it out. A current working file with a different hash does not rewrite the old result.
3. **Does it apply to the current candidate?** Require explicit source-role composition or fresh verification for changed dependencies. The composition archive above records 9 capture checks, 51 composition contracts and 23 release-consumer checks, not a native load or a new two-build campaign. Its earlier native artifacts are intentionally retained with their historical/current roles.

Read exit codes, assertion failures, normal process exits, teardown and unreached stages individually. For example, a cleanup pass does not turn a failed host into success; a model's sampled invariant result does not establish its unmodelled executor or allocation-failure paths. Separate proposal, bounded implementation check, independently accepted scenario and release acceptance using [the status reference](../reference/status-and-evidence.md).

## Carry the finding into the selected work

Write the precise observed gap and smallest verification needed. If no defect is established, say so. Use [retrofit guidance](retrofit-existing-code.md) for an existing boundary and [selected verification](verify-selected-change.md) for an authorized check. Preserve failed gates as well as valid technical evidence: the [receipt publication audit](../../warlock-build-loop/v2/receipt-status-publication-audit-20261030.json) explicitly records a failed staging review even though later forensic file auditing passed. Documentation or a new hash check cannot retroactively change that gate.
