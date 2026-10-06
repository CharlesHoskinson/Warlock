"""Freeze GUI89 only after verifying current build, models and wire evidence."""
import hashlib, json, pathlib, resource, stat, sys

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root = repo / 'implementation/warlock-preview-provider-v92'
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
async_path=only('qa/retirement-async-check-*/report.json');asynchronous=verify(async_path);assert asynchronous['evidence']['checks']==9
refine_path=only('qa/retirement-refinement-check-v2-*/report.json');refinement=verify(refine_path)
assert refinement['namedScenarios']==10 and refinement['invariantSamples']==300 and refinement['unsafeModelMutantsDetected']==3
assert len(refinement['evidence']['coupledTraces'])==30 and refinement['evidence']['statesCompared']==641
mutant_path=only('qa/retirement-elm-mutations-*/report.json');mutations=verify(mutant_path);assert mutations['unsafeCompiledElmMutantsDetected']==3
assert all(row['compiled'] and row['observableMismatch'] for row in mutations['mutants'])
channel_path=only('qa/retirement-delivery-check-*/report.json');channel=verify(channel_path);assert channel['evidence']['checks']==45
delivery_path=only('qa/retirement-delivery-model-check-*/report.json');delivery=verify(delivery_path)
assert delivery['namedScenarios']==14 and delivery['invariantSamples']==300 and delivery['unsafeModelMutantsDetected']==3
assert len(delivery['evidence']['coupledTraces'])==34 and delivery['evidence']['statesCompared']==667
delivery_mutant_path=only('qa/retirement-delivery-elm-mutants-*/report.json');delivery_mutants=verify(delivery_mutant_path)
assert delivery_mutants['unsafeCompiledElmMutantsDetected']==3 and all(row['compiled'] and row['observableMismatch'] for row in delivery_mutants['mutants'])
roundtrip_path=only('qa/retirement-native-elm-check-v3-*/report.json');roundtrip=verify(roundtrip_path)
assert roundtrip['evidence']['checks']==18 and roundtrip['evidence']['nativeCChecks']==30 and roundtrip['evidence']['normalOwnedExit']
for failed_pattern in ['qa/retirement-native-elm-check-[0-9]*/report.json','qa/retirement-native-elm-check-v2-*/report.json']:
    failed_path=only(failed_pattern);failed=json.loads(failed_path.read_text());assert not failed['passed']
    for rel,value in failed['inputs'].items():assert sha(root/rel)==value,rel
    for rel,value in failed['artifacts'].items():assert sha(failed_path.parent/rel)==value,rel
reports.update(retainedDeliveryReport=str(channel_path),retainedDeliveryModelReport=str(delivery_path),retainedDeliveryElmMutantsReport=str(delivery_mutant_path),retainedDeliveryNativeElmReport=str(roundtrip_path))
regressions=only('../../docs/NO-SUCH-PATTERN') if False else repo/'docs/warlock-preview/v91/regressions92-1791326662431424853/report.json'
assert json.loads(regressions.read_text())['passed']
reports['originalRegressionReport']=str(regressions)

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
    'scope': 'Current GUI92 full95/all original12 and all original retirement/control regressions. Retained processing channel45 controls and14 selected Quint scenarios/34 compiled Elm traces/667 state-command comparisons with3 precise model and3 separately compiled Elm mutants. Actual C/socket/native/Elm round trip18 frontend and30 C checks: original request/cancellation/proofs/ACK/readiness, lost final and lost processing ACK, exact retained neighbor, close barrier and normal exit. Synthetic native retirement and untouched reservations; actual WebKit retained routing, captured resources and continuing real native windows remain unqualified. Original S01-S16 and all release gates remain open.'
}, indent=2) + '\n')
(repo / 'docs/warlock-preview/v91/component-report.json').write_text(json.dumps({
    'passed': True, 'providerManifest': str(manifest), 'providerManifestSHA256': sha(manifest),
    'buildCommands': 95, 'asynchronousRetirementControls':9,'asynchronousRetirementScenarios':10,'asynchronousRetirementTraces':30,'asynchronousRetirementStates':641,'unsafeAsynchronousModelMutants':3,'unsafeAsynchronousElmMutants':3,'elmRetirementControls':33, 'controlPrefixScenarios':7, 'controlPrefixTraces':15, 'controlPrefixStates':180, 'unsafeControlPrefixMutants':3, 'controlAdapterControls':10, 'actorRetirementChecks':9068, 'syntheticSequentialSubjects':280, 'actorRetirementReport':str(actor_path), 'nextResumeScenarios': 13, 'nextResumeTraces': 29,
    'nextResumeStates': 605, 'unsafeMutantsDetected': 3, 'nativeCControls': 50,
    'elmWireControls': 30, 'nativeGuardControls': 22,
    'nativeAcceptance': False, 'fullReleaseAccepted': False,
    'retainedDeliveryControls':45,'retainedDeliveryScenarios':14,'retainedDeliveryTraces':34,'retainedDeliveryStates':667,'unsafeRetainedDeliveryModelMutants':3,'unsafeRetainedDeliveryElmMutants':3,'retainedNativeElmControls':48,'next':'Qualify current GUI92 on exact unchanged core16/plugin18 through native127 preserving every original126 gate. FreshGUI93 must retain typed native channel/observations/readiness/final retry and outgoing control delivery liveness in actual shared host; real >256-window turnover and all original release gates remain.'
}, indent=2) + '\n')
sys.path.insert(0, str(repo / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(repo, 'f6779148-8f5d-4bdf-8a0f-044184e486f2', str(root.relative_to(repo)),
    ['PROGRESS heldGUI92 full95/all original12/legacy retirement and prefix regressions; retained45/14selected/34actualElmtraces/667state-command comparisons/3model+3compiledElm mutants, actualCnativeElm48controls/normalexit/lostfinal/lostACK/neighbor/closebarrier. Native127 exact core16/plugin18 must preserve all original126 gates. FreshGUI93 actual host/channel routing and reliable outgoing transport; real windows/capture and all original GUI gates remain.'],
    'progress', [str(manifest.relative_to(repo)), 'docs/warlock-preview/v91/component-report.json']))
