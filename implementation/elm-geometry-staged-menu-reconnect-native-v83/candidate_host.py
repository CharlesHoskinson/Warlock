"""Reuse the held V77 exact private host and owning pair without changing policy."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
PARENT=REPO/'implementation/elm-geometry-staged-menu-native-v77'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
manifest=PARENT/'qa/held-source-manifest.json'
if digest(manifest)!='d5a9c11862d587175890cc814e852f1f73cb3481fa497883e7e4941236da6559':raise RuntimeError('Exact V77 host source hold changed')
packet=json.loads(manifest.read_text())
if not packet['sourceHeld'] or not packet['evidenceIntegrityPassed']:raise RuntimeError('V77 source not held')
for relative,row in packet['files'].items():
 path=PARENT/relative
 if path.is_symlink() or digest(path)!=row['sha256']:raise RuntimeError('V77 held source/evidence changed: '+relative)
spec=importlib.util.spec_from_file_location('held_v77_private_host',PARENT/'candidate_host.py');selected=importlib.util.module_from_spec(spec);spec.loader.exec_module(selected)
base=selected.base;original=selected.original;input_tuple=selected.input_tuple;pair_tuple=selected.pair_tuple
ReviewedWestonHost=selected.ReviewedWestonHost;PrivateHyprSession=selected.PrivateHyprSession
EXPECTED_INPUT_MANIFEST=selected.EXPECTED_INPUT_MANIFEST;EXPECTED_PAIR_MANIFEST=selected.EXPECTED_PAIR_MANIFEST
