"""Freeze GUI81 only after verifying current build, models and wire evidence."""
import hashlib, json, pathlib, resource, stat, sys

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root = repo / 'implementation/warlock-preview-provider-v81'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def only(pattern):
    paths = list(root.glob(pattern))
    assert len(paths) == 1, paths
    return paths[0]

def verify(path):
    proof = json.loads(path.read_text())
    assert proof['passed'], (path, proof.get('error'))
    for name, value in proof['inputs'].items():
        p = pathlib.Path(name)
        assert sha(p if p.is_absolute() else root / p) == value, name
    for name, value in proof.get('artifacts', {}).items():
        assert sha(path.parent / name) == value, name
    return proof

build_path = only('qa/build-*/report.json')
build = verify(build_path)
assert len(build['commands']) == 95
assert all(row['exitCode'] == 0 for row in build['commands'])
for section in ['compilerDependencies', 'linkedLibraries', 'tools']:
    for name, row in build[section].items():
        assert sha(pathlib.Path(name)) == row['sha256'], name
assert sha(build_path.parent / 'elm-host') == build['binarySHA256']
reports = {}
for key, pattern, count in [
    ('modelReport', 'qa/check-*/report.json', 10),
    ('deliveryModelReport', 'qa/delivery-check-*/report.json', 6),
    ('resumeModelReport', 'qa/resume-model-check-*/report.json', 8),
    ('intentModelReport', 'qa/intent-check-*/report.json', 6),
    ('enrollmentModelReport', 'qa/enrollment-check-*/report.json', 8),
    ('receiptModelReport', 'qa/receipt-check-*/report.json', 8),
    ('metadataModelReport', 'qa/metadata-check-*/report.json', 8),
    ('catalogModelReport', 'qa/catalog-check-*/report.json', 8),
]:
    path = only(pattern)
    proof = verify(path)
    assert proof['namedScenarios'] == count
    reports[key] = str(path)
    if 'compiledBuild' in proof:
        assert proof['compiledBuild'] == {'path': str(build_path), 'sha256': sha(build_path)}
for key, pattern in [('feedbackReport', 'qa/feedback-check-*/report.json'),
                     ('resumeCReport', 'qa/resume-check-*/report.json'),
                     ('nextIntentReport', 'qa/next-intent-check-*/report.json'),
                     ('nextResumeReport', 'qa/next-resume-check-*/report.json')]:
    path = only(pattern)
    proof = verify(path)
    reports[key] = str(path)
    if key == 'feedbackReport':
        assert proof['namedScenarios'] == 9 and len(proof['coupledTraces']) == 21
        assert proof['guardControls']['checks'] == 43 and proof['nativeFixtureControls']['checks'] == 18
    elif key == 'resumeCReport':
        assert proof['checks'] == 79 and proof['elmEvidence']['checks'] == 17
    elif key == 'nextIntentReport':
        assert proof['namedScenarios'] == 10 and len(proof['coupledTraces']) == 22
        assert proof['unsafeMutantsDetected'] == 2
        assert proof['wireControls']['checks'] == 21 and proof['wireControls']['cControls'] == 45
    else:
        assert proof['namedScenarios'] == 13 and len(proof['coupledTraces']) == 29
        assert proof['statesCompared'] == 605 and proof['unsafeMutantsDetected'] == 3
        assert proof['wireControls']['checks'] == 30 and proof['wireControls']['cControls'] == 50
        assert [(row['mode'], row['checks']) for row in proof['nativeGuardControls']] == [('guard-retirement', 12), ('guard-receiver', 10)]
    if 'fullBuild' in proof:
        assert proof['fullBuild'] == {'path': str(build_path), 'sha256': sha(build_path)}

evidence = {}
for name in ['catalog-enrollment-replay', 'delivery-extension-physical-tests',
             'metadata-privacy-replay', 'metadata-icon-physical-tests',
             'receiver-extension-physical-tests', 'imported-admission-tests',
             'imported-lifecycle-tests', 'dynamic-enrollment-tests']:
    proof = json.loads((build_path.parent / (name + '.stdout')).read_text().splitlines()[-1])
    assert proof['passed']
    evidence[name] = proof
assert evidence['dynamic-enrollment-tests']['checks'] == 34
files = {}
for path in sorted(root.rglob('*')):
    rel = path.relative_to(root)
    if any(part in {'elm-stuff', 'mutable-elm-home', 'elm-home', '__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:
        continue
    assert not path.is_symlink(), path
    if path.is_file():
        files[str(rel)] = {'kind': 'file', 'sha256': sha(path), 'size': path.stat().st_size,
                           'mode': oct(stat.S_IMODE(path.stat().st_mode))}
manifest = root / 'component-manifest.json'
assert not manifest.exists()
manifest.write_text(json.dumps({
    'schema': 1, 'owner': 'f6779148-8f5d-4bdf-8a0f-044184e486f2',
    'passed': True, 'sourceHeld': True, 'buildReport': str(build_path),
    **reports, 'files': files, 'evidence': evidence, 'evidenceIntegrityPassed': True,
    'nativeAcceptance': False, 'fullReleaseAccepted': False,
    'scope': 'Full95 current Elm/native build and all eleven existing regression suites. Explicit expired unissued resume succession: 13 selected Quint cases, 29 actual helper/Broker traces, 605 compared states, three unsafe native mutants detected; C/socket guards22, actual C50/optimized Elm30. New test inputs compiled separately after unchanged full build inputs. Same-host third picker lease/native image/ACK qualification remains open; no ordinary eligibility or full release acceptance.'
}, indent=2) + '\n')
(repo / 'docs/warlock-preview/v82/component-report.json').write_text(json.dumps({
    'passed': True, 'providerManifest': str(manifest), 'providerManifestSHA256': sha(manifest),
    'buildCommands': 95, 'nextResumeScenarios': 13, 'nextResumeTraces': 29,
    'nextResumeStates': 605, 'unsafeMutantsDetected': 3, 'nativeCControls': 50,
    'elmWireControls': 30, 'nativeGuardControls': 22,
    'nativeAcceptance': False, 'fullReleaseAccepted': False,
    'next': 'Qualify expired unissued resume on a third actual picker lease in native117; preserve all116 stable controls, then continue actor/history retirement, ordinary capture and original release gates.'
}, indent=2) + '\n')
sys.path.insert(0, str(repo / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(repo, 'f6779148-8f5d-4bdf-8a0f-044184e486f2', str(root.relative_to(repo)),
    ['PROGRESS GUI81 held: full95 and all eleven original regressions; new resume13/29/605states/3unsafeMutants/guards22/C50Elm30 passed. Native third lease117 next. All original release gates preserved.'],
    'progress', [str(manifest.relative_to(repo)), 'docs/warlock-preview/v82/component-report.json']))
