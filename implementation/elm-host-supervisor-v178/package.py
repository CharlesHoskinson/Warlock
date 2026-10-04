"""Materialize the accepted V169 runtime inventory, including compiled assets."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
packet_path = REPO / "implementation/elm-native-recovery-qa-v171/qa/slice-manifest.json"
packet = json.loads(packet_path.read_text())
assert packet["passed"]
build_path = REPO / packet["evidence"]["build"]["path"]
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(build_path) == packet["evidence"]["build"]["sha256"]
build = json.loads(build_path.read_text())
assert build["passed"]
files = [build_path.parent / "elm-host"]
for directory in ["assets", "adapter"]:
    files += sorted((build_path.parent / "inputs" / directory).iterdir())
for path in files:
    assert path.is_file() and not path.is_symlink()
    assert packet["files"][str(path.relative_to(REPO))] == digest(path)
native = json.loads((REPO / packet["evidence"]["native"]["path"]).read_text())
manifest = {"schema": 1, "scope": "Bounded V169 component runtime; not a release/deployment selection",
            "host": str(files[0]), "assets": str(build_path.parent / "inputs/assets"),
            "backend": str(build_path.parent / "inputs/adapter/daemon.py"),
            "coreSHA256": native["pair"]["core"]["sha256"],
            "files": {str(p): digest(p) for p in files}}
(ROOT / "runtime-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("Sealed accepted native host, compiled assets and adapter:", len(files), "files")
