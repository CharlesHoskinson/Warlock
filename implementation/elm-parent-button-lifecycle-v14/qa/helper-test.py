"""CPU receipt-parser checks against actual held InteractiveClient methods.

No constructor, subprocess, peer connection, GUI, or input injection is invoked.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "qa/interactive-client.py"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    sys.path.insert(0, "/home/hoskinson/window-integration-qa")
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    out = ROOT / "qa" / ("helper-test-" + str(time.time_ns()))
    out.mkdir(mode=0o700)
    inputs = out / "inputs"
    inputs.mkdir(mode=0o700)
    hashes = {str(path): digest(path) for path in (SOURCE, Path(__file__).resolve())}
    for path in hashes:
        target = inputs / Path(path).name
        shutil.copy2(path, target)
        target.chmod(0o400)
    spec = importlib.util.spec_from_file_location("actual_interactive_client_cpu", SOURCE)
    actual = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(actual)
    report = {"passed": False, "scope": "actual parser CPU methods; no process/GUI/input launch", "qaScope": scope,
              "sources": hashes, "checks": []}
    index = 0

    def client(data=b"", guard=None, exit_code=None):
        nonlocal index
        index += 1
        path = out / ("owned-log-%02d.log" % index)
        path.write_bytes(data)
        path.chmod(0o600)
        calls = []
        value = actual.InteractiveClient.__new__(actual.InteractiveClient)
        value.log_path, value.offset, value.buffer = path, 0, b""
        value.guard = guard if guard is not None else lambda: calls.append("guard")
        value.process = SimpleNamespace(poll=lambda: exit_code, returncode=exit_code)
        return value, calls

    def check(name, test):
        try:
            evidence = test()
            report["checks"].append({"name": name, "passed": True, "evidence": evidence})
        except Exception as error:
            report["checks"].append({"name": name, "passed": False, "error": repr(error)})

    def rejects(function, fragment, kind=RuntimeError):
        try:
            function()
        except kind as error:
            assert fragment in str(error), str(error)
            return str(error)
        raise AssertionError("Expected rejection: " + fragment)

    receipt = {"sequence": 1, "accepted": True, "scope": "parent-notify-only"}
    wire = (json.dumps(receipt) + "\n").encode()
    predicate = lambda packet: type(packet.get("sequence")) is int and packet["sequence"] == 1

    def exact_one():
        value, calls = client(wire)
        assert value._wait(predicate) == receipt and calls == ["guard"]
        return {"guardCalls": len(calls), "receipt": receipt}
    check("one-exact-acknowledgment", exact_one)

    def ready():
        packet = {"ready": True, "scope": "parent-notify-only"}
        value, calls = client((json.dumps(packet) + "\n").encode())
        assert value._wait(lambda row: row.get("ready") is True) == packet and calls
        return packet
    check("actual-readiness-packet", ready)

    def duplicate():
        value, _ = client(wire + wire)
        return rejects(lambda: value._wait(predicate), "Multiple parent receipts")
    check("duplicate-ack-in-one-read-rejected", duplicate)

    def extra():
        value, _ = client(wire + b'{"sequence":99}\n')
        return rejects(lambda: value._wait(predicate), "Multiple parent receipts")
    check("matching-ack-plus-unexpected-json-rejected", extra)

    def malformed():
        value, _ = client(b'{"sequence":\n')
        return rejects(value._packets, "Expecting value", json.JSONDecodeError)
    check("malformed-json-rejected", malformed)

    def partial():
        value, _ = client(wire[:-1])
        assert value._packets() == [] and value.buffer == wire[:-1]
        with value.log_path.open("ab") as log:
            log.write(b"\n")
        assert value._packets() == [receipt] and value.buffer == b""
        assert value._packets() == []
        return {"bytesConsumed": value.offset, "notReplayed": True}
    check("partial-newline-held-once", partial)

    def out_of_order():
        value, calls = client(b'{"sequence":2,"accepted":true}\n')
        rejection = rejects(lambda: value._wait(predicate), "out-of-order")
        assert calls == ["guard"]
        return rejection
    check("out-of-order-sequence-rejected", out_of_order)

    def boolean_sequence():
        value, _ = client(b'{"sequence":true,"accepted":true}\n')
        return rejects(lambda: value._wait(predicate), "out-of-order")
    check("boolean-sequence-does-not-alias-one", boolean_sequence)

    def guarded():
        def deny():
            raise RuntimeError("test host identity denied")
        value, _ = client(wire, guard=deny)
        rejection = rejects(lambda: value._wait(predicate), "host identity denied")
        assert value.offset == 0 and value.buffer == b""
        return {"rejection": rejection, "logNotConsumed": True}
    check("host-guard-before-receipt-acceptance", guarded)

    def stderr():
        data = b"diagnostic preserved\n" + wire
        value, _ = client(data)
        assert value._wait(predicate) == receipt and value.log_path.read_bytes() == data
        return {"stderrPreserved": True}
    check("native-stderr-preserved-outside-json", stderr)

    def read_bound():
        value, _ = client(b"x" * 65537)
        return rejects(value._packets, "bounded observation")
    check("single-read-byte-bound", read_bound)

    def line_bound():
        value, _ = client(b"x" * 65536)
        assert value._packets() == []
        with value.log_path.open("ab") as log:
            log.write(b"x")
        return rejects(value._packets, "line exceeded bound")
    check("partial-line-cumulative-bound", line_bound)

    def total_bound():
        value, _ = client()
        value.offset = 4 * 1024 * 1024
        with value.log_path.open("r+b") as log:
            log.seek(value.offset)
            log.write(b"x")
        return rejects(value._packets, "bounded observation")
    check("total-log-observation-bound", total_bound)

    def exited():
        value, calls = client(exit_code=6)
        rejection = rejects(lambda: value._wait(predicate), "exited before acknowledgment: 6")
        assert calls == ["guard"]
        return rejection
    check("early-client-exit-is-not-ack", exited)

    def negative_exit():
        packet = dict(receipt, accepted=False)
        value, _ = client((json.dumps(packet) + "\n").encode(), exit_code=6)
        assert value._wait(predicate) == packet
        return {"refusalObservedBeforeNormalExit6": True}
    check("refusal-ack-readable-before-exit6", negative_exit)

    def deadline():
        value, calls = client()
        with patch.object(actual.time, "monotonic", side_effect=[0, 7]):
            rejection = rejects(lambda: value._wait(predicate), "Six-second")
        assert calls == []
        return rejection
    check("expired-ack-deadline-refuses", deadline)

    for path, expected in hashes.items():
        if digest(path) != expected:
            report["checks"].append({"name": "source-held-" + Path(path).name, "passed": False})
    report["passed"] = all(row["passed"] for row in report["checks"]) and len(report["checks"]) == 16
    report["artifacts"] = {str(path.relative_to(out)): digest(path) for path in sorted(out.rglob("*")) if path.is_file()}
    target = out / "report.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "checks": len(report["checks"]), "report": str(target)}), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
