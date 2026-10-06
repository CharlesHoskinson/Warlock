"""Freeze GUI88 only after verifying current build, models and wire evidence."""
import hashlib, json, pathlib, resource, stat, sys

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root = repo / 'implementation/warlock-preview-provider-v88'
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

retirement_path = only('qa/retirement-decoder-check-*/report.json')
retirement = verify(retirement_path)
assert retirement['namedScenarios'] == 13 and len(retirement['coupledTraces']) == 25
assert retirement['statesCompared'] == 439 and retirement['unsafeMutantsDetected'] == 3
assert retirement['fullBuild'] == {'path': str(build_path), 'sha256': sha(build_path)}
reports['retirementDecoderReport'] = str(retirement_path)
c_path = only('qa/retirement-c-check-*/report.json')
c = verify(c_path)
assert [row['mode'] for row in c['controls']] == ['valid','retired','bad-clock','bad-request','regress']
assert c['checks'] == sum(row['checks'] for row in c['controls'])
assert c['fullBuild'] == {'path': str(build_path), 'sha256': sha(build_path)}
reports['retirementCReport'] = str(c_path)
evidence = {}
for name in ['catalog-enrollment-replay', 'delivery-extension-physical-tests',
             'metadata-privacy-replay', 'metadata-icon-physical-tests',
             'receiver-extension-physical-tests', 'imported-admission-tests',
             'imported-lifecycle-tests', 'dynamic-enrollment-tests']:
    proof = json.loads((build_path.parent / (name + '.stdout')).read_text().splitlines()[-1])
    assert proof['passed']
    evidence[name] = proof
assert evidence['dynamic-enrollment-tests']['checks'] == 34
actor_path=only('qa/actor-retirement-check-v3-*/report.json')
actor=verify(actor_path)
assert actor['checks']==9068 and actor['evidence'][1]['sequentialSubjects']==280
assert not actor['actorTurnoverAccepted'] and not actor['nativeAcceptance'] and not actor['fullReleaseAccepted']
reports['actorRetirementReport']=str(actor_path)
elm_path=only('qa/elm-retirement-check-*/report.json');elm=verify(elm_path);assert elm['evidence']['checks']==33
prefix_path=only('qa/control-prefix-check-v3-*/report.json');prefix=verify(prefix_path);assert prefix['namedScenarios']==7 and len(prefix['coupledTraces'])==15 and prefix['statesCompared']==180 and prefix['unsafeMutantsDetected']==3
adapter_path=only('qa/control-adapter-check-*/report.json');adapter=verify(adapter_path);assert adapter['evidence']['checks']==10
reports.update(elmRetirementReport=str(elm_path),controlPrefixReport=str(prefix_path),controlAdapterReport=str(adapter_path))
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
    'scope': 'Actual aggregate-native C/socket retirement9068 checks through280 synthetic subjects with original neighbor. Full current GUI88 build95, all original12 regression suites, typed retirement decoder13/25/439states/three mutants and C96. Elm33 controls verify exact settlement, readiness after ACK, no further controls afterReady, immediate accepted-packet release and native-clock replay cutoff. Actual C control prefix7 selected/15coupled/180states/three unsafe mutations plus actual popup adapter10 controls. Real WebKit/native retirement activation, captured physical retirement and continuing native/Elm turnover remain unqualified; ordinary eligibility and every original release gate remain open.'
}, indent=2) + '\n')
(repo / 'docs/warlock-preview/v88/component-report.json').write_text(json.dumps({
    'passed': True, 'providerManifest': str(manifest), 'providerManifestSHA256': sha(manifest),
    'buildCommands': 95, 'elmRetirementControls':33, 'controlPrefixScenarios':7, 'controlPrefixTraces':15, 'controlPrefixStates':180, 'unsafeControlPrefixMutants':3, 'controlAdapterControls':10, 'actorRetirementChecks':9068, 'syntheticSequentialSubjects':280, 'actorRetirementReport':str(actor_path), 'nextResumeScenarios': 13, 'nextResumeTraces': 29,
    'nextResumeStates': 605, 'unsafeMutantsDetected': 3, 'nativeCControls': 50,
    'elmWireControls': 30, 'nativeGuardControls': 22,
    'nativeAcceptance': False, 'fullReleaseAccepted': False,
    'next': 'Qualify full current GUI88/core16/plugin18 through fresh serialized native125 preserving every original124 oracle/deadline. Integrate exact own native retirement observation/readiness/completion routing in a fresh derivative; qualify actual continuing native/Elm turnover beyond256 and all original release gates.'
}, indent=2) + '\n')
sys.path.insert(0, str(repo / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(repo, 'f6779148-8f5d-4bdf-8a0f-044184e486f2', str(root.relative_to(repo)),
    ['PROGRESS GUI88 held full95/original12/C96/decoder13-25-439states-3mutants/aggregate9068 through280 synthetic subjects, Elm33, Cprefix7-15-180states-3mutants and adapter10. FailedGUI87 duplicate ACK after readiness and early fixture/model failures preserved. Fresh native125 on exact unchanged owning core16/plugin18 must retain all original124 runtime gates. Native retirement observation/readiness/completion routing and real continuing native/Elm turnover remain unqualified; ordinary capture and all full release gates remain open.'],
    'progress', [str(manifest.relative_to(repo)), 'docs/warlock-preview/v88/component-report.json']))
