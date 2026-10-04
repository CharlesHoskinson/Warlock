"""Verify a selected protected CPU preflight and hold this QA source; no GUI."""
import argparse, hashlib, json, os, resource, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
parser = argparse.ArgumentParser()
parser.add_argument('--preflight', type=Path, required=True)
args = parser.parse_args()
selected = args.preflight.resolve(strict=True)
assert selected.is_relative_to(ROOT / 'qa') and selected.name == 'report.json'
OUT = ROOT / 'qa' / ('freeze-' + str(time.time_ns()))
OUT.mkdir()
checks = []
report = {'passed': False, 'nativeAcceptance': False, 'checks': checks,
          'scope': 'QA reconnect source preservation and owning tuple preflight; no GUI'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(name, value):
    checks.append({'name': name, 'passed': bool(value)})
    assert value, name

try:
    r = json.loads(selected.read_text())
    check('actual preflight passed', r['passed'] is True and all(x['passed'] for x in r['checks']))
    for relative, digest in r['inputs'].items():
        check('tested source ' + relative, sha(ROOT / relative) == digest and sha(selected.parent / 'inputs' / relative) == digest)
    for relative, digest in r['artifacts'].items():
        check('retained preflight ' + relative, sha(selected.parent / relative) == digest)
    u = json.loads((ROOT / 'upstream.json').read_text())
    for p, k in [('parentHost', 'parentHostSHA256'), ('parentRunner', 'parentRunnerSHA256'),
                 ('copiedClientHelper', 'copiedClientHelperSHA256'), ('originalCoreHost', 'originalCoreHostSHA256'),
                 ('clientHelperParent', 'clientHelperParentSHA256'), ('preservedReconnectFailure', 'preservedReconnectFailureSHA256')]:
        check('retained ancestor ' + p, sha(Path(u[p])) == u[k])
    check('selected own host pinned', sha(ROOT / 'candidate_host.py') == u['selectedHostSHA256'])
    check('scenario scope preserved', u['executedScenarioScope'] == ['GEOMETRY-MENU-' + str(i).zfill(2) for i in range(1, 11)])
    manifest = Path(r['selectedTuple']['relayManifest'])
    check('reviewed relay pinned', sha(manifest) == r['selectedTuple']['relayManifestSHA256'])
    packet = json.loads(manifest.read_text())
    check('relay source held', packet['sourceHeld'] is True and packet['evidenceIntegrityPassed'] is True)
    relay_root = manifest.parents[1]
    for relative, row in packet['files'].items():
        path = relay_root / relative
        check('relay closure ' + relative, not path.is_symlink() and path.resolve().is_relative_to(relay_root) and sha(path) == row['sha256'])
    for relative, target in packet.get('symlinks', {}).items():
        path = relay_root / relative
        check('relay retained symlink ' + relative, path.is_symlink() and os.readlink(path) == target)
    report['passed'] = True
except Exception as error:
    report['error'] = repr(error)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
if report['passed']:
    files = {}
    for path in sorted(ROOT.rglob('*')):
        if path.is_symlink():
            raise RuntimeError('Unexpected source symlink')
        if path.is_file() and path.name != 'held-source-manifest.json':
            files[str(path.relative_to(ROOT))] = {'sha256': sha(path), 'size': path.stat().st_size, 'mode': oct(path.stat().st_mode & 0o777)}
    hold = {'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True,
            'nativeAcceptance': False, 'allContractScenariosPassed': False, 'fullRoadmapAccepted': False,
            'scope': report['scope'], 'files': files, 'selectedTuple': r['selectedTuple'],
            'preflightReport': {'path': str(selected.relative_to(ROOT)), 'sha256': sha(selected)},
            'freezeReport': {'path': str((OUT / 'report.json').relative_to(ROOT)), 'sha256': sha(OUT / 'report.json')},
            'executedScenarioScope': u['executedScenarioScope'], 'scenario09': u['scope09']}
    destination = ROOT / 'qa' / 'held-source-manifest.json'
    with destination.open('x') as stream:
        stream.write(json.dumps(hold, indent=2) + '\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])
