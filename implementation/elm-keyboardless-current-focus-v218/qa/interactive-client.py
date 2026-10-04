"""Import-safe persistent wrapper for the unchanged reviewed parent-input client.

Only the owning private-host runner constructs this object. Receipts acknowledge
parent notify calls; this wrapper asserts no target delivery or paired-release
result. The host owns process/log cleanup if a bounded observation fails.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import struct
import subprocess
import time


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class InteractiveClient:
    def __init__(self, host, original, build_report, expected_report_sha256, *, guard, name="parent-input-interactive"):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", name):
            raise ValueError("Unsafe private client log name")
        self.host, self.original, self.guard = host, original, guard
        self.report_path = Path(build_report)
        if digest(self.report_path) != expected_report_sha256:
            raise RuntimeError("Parent input build report changed")
        build = json.loads(self.report_path.read_text())
        if build.get("passed") is not True:
            raise RuntimeError("Parent input build was not accepted")
        self.binary = Path(build["client"])
        self.binary_sha256 = build["clientSHA256"]
        if digest(self.binary) != self.binary_sha256:
            raise RuntimeError("Parent input client binary changed")
        parents = [row for _, row in host.processes if row.get("name") == "weston"]
        if len(parents) != 1:
            raise RuntimeError("Parent process is ambiguous")
        self.parent = dict(parents[0])
        self.socket_path = host.runtime / "weston-host"
        self.socket_identity = original.socket_identity(self.socket_path, host.runtime)
        self.process = None
        self.sequence = 0
        self.offset = 0
        self.buffer = b""
        self.expected_exit = 0
        self.closed = False
        self.evidence = {
            "scope": "parent-notify-only; no recipient delivery assertion",
            "wrapper": str(Path(__file__).resolve()), "wrapperSHA256": digest(__file__),
            "buildReport": str(self.report_path), "buildReportSHA256": expected_report_sha256,
            "client": str(self.binary), "clientSHA256": self.binary_sha256,
            "buildInputs": dict(build.get("inputs", {})),
            "parent": self.parent, "parentSocket": self.socket_identity, "receipts": [],
        }
        self._peer()
        env = dict(host.env)
        if env.get("XDG_RUNTIME_DIR") != str(host.runtime) or env.get("WAYLAND_DISPLAY") != "weston-host":
            raise RuntimeError("Parent client routing changed")
        env["ELM_PARENT_INPUT_QA"] = "1"
        self.log_path = host.output / (name + ".log")
        descriptor = os.open(self.log_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        log = os.fdopen(descriptor, "wb")
        host.logs.append(log)
        self.process = subprocess.Popen([str(self.binary)], stdin=subprocess.PIPE, stdout=log,
                                        stderr=subprocess.STDOUT, env=env, cwd=host.runtime,
                                        start_new_session=True)
        row = original.process(self.process.pid)
        row.update(name=name, command=[str(self.binary)], log=str(self.log_path))
        self.row = row
        host.processes.append((self.process, row))
        host.evidence[name] = row
        self.evidence["process"] = row
        ready = self._wait(lambda packet: packet.get("ready") is True)
        if ready.get("scope") != "parent-notify-only":
            raise RuntimeError("Unexpected parent client readiness scope")
        self.evidence["ready"] = ready

    def _peer(self):
        self.guard()
        if not self.original.same_process(self.parent):
            raise RuntimeError("Private parent process changed")
        if self.original.socket_identity(self.socket_path, self.host.runtime) != self.socket_identity:
            raise RuntimeError("Private parent socket changed")
        with socket.socket(socket.AF_UNIX) as connection:
            connection.settimeout(2)
            connection.connect(str(self.socket_path))
            pid, uid, _ = struct.unpack("3i", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
        if pid != self.parent["pid"] or uid != os.getuid() or not self.original.same_process(self.parent):
            raise RuntimeError("Private parent socket peer changed")
        if self.original.socket_identity(self.socket_path, self.host.runtime) != self.socket_identity:
            raise RuntimeError("Private parent socket changed during peer check")
        if digest(self.binary) != self.binary_sha256:
            raise RuntimeError("Parent input client binary changed")

    def _packets(self):
        with self.log_path.open("rb") as log:
            log.seek(self.offset)
            data = log.read(65537)
        if len(data) > 65536 or self.offset + len(data) > 4 * 1024 * 1024:
            raise RuntimeError("Parent client log exceeded bounded observation")
        self.offset += len(data)
        self.buffer += data
        if len(self.buffer) > 65536:
            raise RuntimeError("Parent client log line exceeded bound")
        packets = []
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            if not line.startswith(b"{"):
                continue  # Native stderr remains preserved in the owned log.
            packet = json.loads(line)
            if not isinstance(packet, dict):
                raise RuntimeError("Invalid parent client receipt")
            packets.append(packet)
        return packets

    def _wait(self, predicate):
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            self.guard()
            packets = self._packets()
            if len(packets) > 1:
                raise RuntimeError("Multiple parent receipts for one outstanding request")
            for packet in packets:
                if predicate(packet):
                    return packet
                raise RuntimeError("Unexpected or out-of-order parent receipt")
            if self.process.poll() is not None:
                raise RuntimeError("Parent client exited before acknowledgment: " + str(self.process.returncode))
            time.sleep(.02)
        raise RuntimeError("Six-second parent acknowledgment deadline")

    def send(self, command, expected=True):
        if self.closed or self.expected_exit != 0 or not isinstance(expected, bool):
            raise RuntimeError("Parent client is unavailable for another request")
        if not re.fullmatch(r"(?:motion -?[0-9]{1,11} -?[0-9]{1,11}|(?:press|release) [0-9]{1,10}|pointer-capability [01]|keyboard-capability [01]|keyboard-focus [01]|disconnect-held-child [0-9]{1,10} [0-9]{1,20} [1-7]|(?:key-press|key-release) (?:30|42|68)|disconnect-held-key-child [0-9]{1,10} [0-9]{1,20} [1-3])", command):
            raise ValueError("Expected one bounded parent-input command")
        self._peer()
        if self.process.poll() is not None or not self.original.same_process(self.row):
            raise RuntimeError("Parent client identity changed")
        self.sequence += 1
        self.process.stdin.write((command + "\n").encode())
        self.process.stdin.flush()
        receipt = self._wait(lambda packet: type(packet.get("sequence")) is int and packet["sequence"] == self.sequence)
        if receipt.get("scope") != "parent-notify-only" or type(receipt.get("accepted")) is not bool or receipt["accepted"] != expected:
            raise RuntimeError("Unexpected parent request admission")
        self.evidence["receipts"].append({"command": command, **receipt})
        if not expected:
            self.expected_exit = 6  # Frozen helper terminates after its rejected request.
        return receipt

    def _close(self, quit_command):
        if self.closed:
            return self.evidence
        self._peer()
        if self.process.poll() is None:
            if not self.original.same_process(self.row):
                raise RuntimeError("Parent client identity changed before shutdown")
            if quit_command and self.expected_exit == 0:
                self.process.stdin.write(b"quit\n")
                self.process.stdin.flush()
            self.process.stdin.close()
        else:
            self.process.stdin.close()
        code = self.process.wait(timeout=5)
        self.evidence["exitCode"] = code
        self.evidence["shutdown"] = "quit" if quit_command else "eof"
        if code != self.expected_exit:
            raise RuntimeError("Parent client did not exit normally: " + str(code))
        self.closed = True
        return self.evidence

    def quit(self):
        return self._close(True)

    def eof(self):
        return self._close(False)
