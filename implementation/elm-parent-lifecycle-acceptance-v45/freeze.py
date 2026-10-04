"""Bind model witnesses, extracted routing replay and private native lifecycle evidence."""
import hashlib
import json
import os
from pathlib import Path
import resource

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parent
IMPL = ROOT.parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def verify_dict(base, packet):
    for rel, digest in packet.items():
        assert sha(base / rel) == digest, rel


ancestor = IMPL / 'elm-parent-position-acceptance-v35/acceptance-manifest.json'
assert sha(ancestor) == '065c68738aee68266fa90340e5a3e7d30d9384f96a204b49f5cdc692139c13b5'
prior = read(ancestor)
assert prior['passed'] and not prior['releaseAcceptance']
pair = read(prior['pairManifest'])
assert sha(prior['pairManifest']) == prior['pairManifestSHA256']
core = pair['nativePair']['core']
aq = prior['aqTuple']
assert sha(core['path']) == core['sha256']
assert sha(aq['library']) == aq['librarySHA256']
reports = []


def verify_report(path, native=False):
    r = read(path)
    assert r['passed']
    verify_dict(path.parent, r['artifacts'])
    for key in ['inputs', 'sourceInputs']:
        verify_dict(Path('/'), r.get(key, {}))
    if native:
        assert r['cleanupPassed'] and not r['mainDesktopActions']
        assert all(c['passed'] for c in r['checks'])
        host = r['privateHost']
        assert host['runtimeGone'] and not host['remainingDescendants'] and not host['cleanupErrors']
        assert host['xwaylandEnabled'] is False
        assert host['hyprlandMaps']['files'][str(Path(core['path']).resolve())] == core['sha256']
        assert host['privateAquamarine']['mappedFiles'][str(Path(aq['library']).resolve())] == aq['librarySHA256']
    reports.append({'path': str(path), 'sha256': sha(path), 'scope': r['scope'], 'native': native,
                    'checks': len(r['checks']) if native else None})
    return r


model_path = IMPL / 'elm-parent-position-model-v37/qa/model-1791099188929216528/report.json'
model = verify_report(model_path)
assert model['executedNamedScenarios'] == 19 and model['invariantSamples'] == 1000 and model['mutantsRejected'] == 3
assert sha(IMPL / 'elm-parent-position-model-v37/spec/parent.qnt') == model['sourceSHA256']
replay_path = IMPL / 'elm-parent-position-traces-v39/qa/replay-1791099459626872187/report.json'
replay = verify_report(replay_path)
assert replay['traces'] == 19 and replay['states'] == 86 and replay['mutantsRejected'] == 3
cap_path = IMPL / 'elm-parent-capability-v40/qa/native-1791099701423667415/report.json'
cap = verify_report(cap_path, native=True)
assert len(cap['checks']) == 135 and len(cap['capabilityCycles']) == 2

build_path = IMPL / 'elm-parent-capability-v40/build-1791099632854316645/report.json'
build = read(build_path)
assert build['passed']
verify_dict(build_path.parent / 'inputs', build['inputs'])
verify_dict(IMPL / 'elm-parent-capability-v40', build['inputs'])
verify_dict(Path('/'), build['dependencies'])
verify_dict(Path('/'), build['owningFiles'])
assert sha(build['module']) == build['moduleSHA256'] and sha(build['client']) == build['clientSHA256']

failed = []
for name in ['elm-parent-position-model-v36', 'elm-parent-position-traces-v38',
             'elm-parent-focus-v41', 'elm-parent-focus-v42', 'elm-parent-focus-v43',
             'elm-parent-focus-v44', 'elm-parent-focus-v46']:
    candidates = list((IMPL / name / 'qa').glob('*/report.json'))
    assert len(candidates) == 1 and read(candidates[0])['passed'] is False
    failed.append({'path': str(candidates[0]), 'sha256': sha(candidates[0])})

owned = ['elm-parent-position-model-v36', 'elm-parent-position-model-v37',
         'elm-parent-position-traces-v38', 'elm-parent-position-traces-v39',
         'elm-parent-capability-v40', 'elm-parent-focus-v41', 'elm-parent-focus-v42',
         'elm-parent-focus-v43', 'elm-parent-focus-v44', 'elm-parent-focus-v46', ROOT.name]
files = []
out = ROOT / 'acceptance-manifest.json'
assert not out.exists()
for name in owned:
    for p in sorted((IMPL / name).rglob('*')):
        if p == out:
            continue
        if p.is_symlink():
            files.append({'path': str(p.relative_to(IMPL)), 'symlink': os.readlink(p)})
        elif p.is_file():
            files.append({'path': str(p.relative_to(IMPL)), 'sha256': sha(p), 'size': p.stat().st_size})
out.write_text(json.dumps({
    'schema': 1, 'passed': True, 'releaseAcceptance': False, 'mainDesktopActions': False,
    'scope': 'Bounded model/extracted routing comparison and private parent pointer capability lifecycle',
    'ancestorAcceptance': str(ancestor), 'ancestorAcceptanceSHA256': sha(ancestor),
    'modelNamedScenarios': 19, 'modelInvariantSamples': 1000, 'modelMaxSteps': 40,
    'extractedWitnessStates': 86, 'fullProgramRefinement': False, 'nativeFocusAcceptance': False,
    'reports': reports, 'retainedFailures': failed,
    'remaining': ['Native parent focus loss/layout and full occlusion progress (V44/V46 failed)',
                  'Native staged/ACK/current-generation parent configure fencing and queued work retirement',
                  'Multiple outputs/rotation and physical input/output loss',
                  'Shared-shell coherent core integration, AT/IME, budgets, full roadmap and reversible release'],
    'files': files,
}, indent=2) + '\n')
print(json.dumps({'passed': True, 'manifest': str(out), 'files': len(files),
                  'capabilityChecks': len(cap['checks']), 'retainedFailures': len(failed)}))
