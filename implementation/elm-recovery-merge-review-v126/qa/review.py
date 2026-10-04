#!/usr/bin/env python3
"""Capture an independent source review; no native acceptance is implied."""
import datetime
import hashlib
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parents[1]
FILES = [
    "elm-shared-observation-recovery-v121/src/Shell.elm",
    "elm-shared-observation-recovery-v121/src/OutputController.elm",
    "elm-unsent-operation-disposition-v122/src/Shell.elm",
    "elm-unsent-operation-disposition-v122/src/Effects.elm",
    "elm-unsent-operation-disposition-v122/src/OutputController.elm",
    "elm-unsent-operation-disposition-v122/src/TaskbarShell.elm",
    "elm-unsent-operation-disposition-v122/src/UnsentOperation.elm",
]

def main():
    destination = HERE / "qa" / ("review-" + str(time.time_ns()))
    destination.mkdir(parents=True, exist_ok=False)
    inventory = []
    for name in FILES:
        source = ROOT / "implementation" / name
        before = source.stat()
        payload = source.read_bytes()
        captured = destination / "inputs" / name
        captured.parent.mkdir(parents=True, exist_ok=True)
        captured.write_bytes(payload)
        after = source.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
            raise RuntimeError("Source changed while captured: " + name)
        inventory.append({"source": str(source), "snapshot": str(captured), "sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)})
    report = {
        "observedUTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kind": "independent-source-review",
        "nativeAcceptance": False,
        "releaseAcceptance": False,
        "inventory": inventory,
        "findings": [
            {"id": "R126-01", "status": "reviewed", "finding": "V121 checks exact current observation IDs before native dismissal or prepared-selection cancellation. An obsolete certificate consumes its transport record without those UI effects."},
            {"id": "R126-02", "status": "reviewed", "finding": "V122 settles operations before the observation/current-popup lease guard. Its Shell requires exact original binding, protocol, full intent, issued membership and Pending unresolved state; unrelated Unknown operations are retained."},
            {"id": "R126-03", "status": "requires-behavioral-oracle", "finding": "V121 UnsentObservations can clear an attach ID while retaining attachNeeded and defer reissue behind Pending effects or another read. Later refreshObservations does not consult attachNeeded. Test delayed attach recovery without another topology change; source inspection alone does not establish reachability or acceptance."},
            {"id": "R126-04", "status": "merge-contract", "finding": "Merge operation settlement and read/UI recovery as separate proof paths. Do not place Pending-only local refusal behind matchesUnsent or current popup lease, and do not allow operation proof to dismiss an unrelated newer menu."},
        ],
        "nextGate": "Hold and qualify final derivatives; merge into current shared context/recovery source; run original native menu/retirement scenarios on owning current ABI with unchanged deadlines.",
    }
    path = destination / "report.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": str(path), "filesCaptured": len(inventory), "openBehavioralFindings": 1, "nativeAcceptance": False}))

if __name__ == "__main__":
    main()
