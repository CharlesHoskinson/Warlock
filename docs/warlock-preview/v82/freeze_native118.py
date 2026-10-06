"""Freeze only actual passed native118 evidence and its complete input tuple."""
import hashlib, json, pathlib, re, resource, stat, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root = repo / 'implementation/warlock-client-provider-native-v118'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
reports = list(root.glob('qa/native-*/report.json'))
assert len(reports) == 1
path = reports[0]
proof = json.loads(path.read_text())
assert proof['passed'] and proof['cleanupPassed']
assert all(row['passed'] for row in proof['checks'])
assert all(row['exitCode'] == 0 for row in proof['ownedExitCodes'])
for name, value in proof['artifacts'].items():
    assert sha(path.parent / name) == value, name
preflight = json.loads((root / 'qa/preflight.json').read_text())
assert preflight['passed']
for name, value in preflight['inputs'].items():
    assert sha(pathlib.Path(name)) == value, name
previous = json.loads(pathlib.Path(preflight['retainedNative116Report']).read_text())
assert previous['passed'] and len(previous['checks']) == 2433
readonly = {'styleDimPendingNativeReadonlyScope', 'styleAgainDimPendingNativeReadonlyScope',
            'styleRestoreIntermediateReadonlyScope', 'styleCropDimIntermediateReadonlyScope'}
def stable(rows):
    return [re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$', 'opacityPrivateForeignWindowMoved-<native-address>', row['name']) for row in rows if row['name'] not in readonly]
old = stable(previous['checks'])
names = set(old)
assert [name for name in stable(proof['checks']) if name in names] == old
next_resume = proof['nextResumeGUIEvidence']
assert proof['nativeNextResumeIntentGUIBoundedQualified'] and next_resume['exactACK']
assert not next_resume['hardwarePresentation'] and not next_resume['assistiveTechnologyAcceptance']
assert next_resume['sameHostPID'] == proof['nextIntentGUIEvidence']['sameHostPID']
job = next_resume['offer']['job']
original = next_resume['previous']['job']
seed = next_resume['seed']
expired = next_resume['expired']
assert original['request'] == '1' and job['request'] == '2'
assert job['binding'] == original['binding'] and job['clock'] == original['clock']
assert job['context']['incarnation'] == original['context']['incarnation']
assert job['origin'] == seed['lease']
assert int(seed['publication']) > int(expired['publication']) and int(seed['lease']) > int(expired['lease'])
assert int(job['deadline']) == int(seed['source']['scope']['now']) + 2000000000
assert int(job['deadline']) > int(expired['deadline'])
uri = 'elm-shell://preview/' + next_resume['offer']['handle']
assert any(row['uri'] == uri and row['complete'] and row['naturalWidth'] == 320 and row['naturalHeight'] == 240 for row in next_resume['images'])
assert all(row['records'] == 0 and int(row['charge']) == 0 and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] and not row['retirementPending'] for row in next_resume['finalOwnership'])
required = ['nextResumeGUIExpiredWaitingIntentKeepsOriginalJobAndCutoff',
            'nextResumeGUIOldPhysicalAndTerminalOwnersDrained',
            'nextIntentActualPointerNormalExit-resume-close',
            'nextIntentActualPointerNormalExit-resume-reopen',
            'nextResumeGUIExactNextRequestAndLaterPickerLease',
            'nextResumeGUIFreshNativeTwoSecondCutoff',
            'nextResumeGUIActualOwnedURIComplete',
            'nextResumeGUIOriginalAndSuccessorCaptureAndACKExactlyOnce',
            'nextResumeGUIAllPhysicalAndJournalOwnersDrained',
            'feedbackGUIFullHostNormalExit', 'allPriorNative116StableOrderedAssertionsRetained']
assert all(any(row['name'] == name and row['passed'] for row in proof['checks']) for name in required)
provider = repo / 'implementation/warlock-preview-provider-v81/component-manifest.json'
gui = json.loads(provider.read_text())
assert gui['passed'] and gui['sourceHeld']
for name, row in gui['files'].items():
    assert sha(provider.parent / name) == row['sha256'], name
files = {}
for source in sorted(root.rglob('*')):
    rel = source.relative_to(root)
    if '__pycache__' in rel.parts:
        continue
    assert not source.is_symlink(), source
    if source.is_file():
        files[str(rel)] = {'kind': 'file', 'sha256': sha(source), 'size': source.stat().st_size,
                           'mode': oct(stat.S_IMODE(source.stat().st_mode))}
manifest = root / 'component-manifest.json'
assert not manifest.exists()
manifest.write_text(json.dumps({'schema': 1, 'owner': 'f6779148-8f5d-4bdf-8a0f-044184e486f2',
    'passed': True, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'files': files,
    'nativeReport': str(path), 'nativeReportSHA256': sha(path),
    'providerManifest': str(provider), 'providerManifestSHA256': sha(provider),
    'nativeChecks': len(proof['checks']), 'normalOwnedExits': len(proof['ownedExitCodes']),
    'prior116StableControls': len(old), 'nativeNextResumeIntentGUIBoundedQualified': True,
    'nativeAcceptance': False, 'fullReleaseAccepted': False}, indent=2) + '\n')
report = {'passed': True, 'providerManifest': str(provider), 'providerManifestSHA256': sha(provider),
    'nativeManifest': str(manifest), 'nativeManifestSHA256': sha(manifest), 'nativeReport': str(path),
    'nativeChecks': len(proof['checks']), 'normalOwnedExits': len(proof['ownedExitCodes']),
    'prior116StableControls': len(old), 'buildCommands': 95, 'nextResumeScenarios': 13,
    'nextResumeTraces': 29, 'nextResumeStates': 605, 'unsafeMutantsDetected': 3,
    'nativeCControls': 50, 'elmWireControls': 30, 'nativeGuardControls': 22,
    'sameHostThirdLeaseResumeImageACKQualified': True, 'nativeAcceptance': False,
    'ordinaryEligibleCaptureAccepted': False, 'assistiveTechnologyAcceptance': False,
    'fullReleaseAccepted': False,
    'next': 'Commit/publish exact GUI81/failed117/passed118. Continue authority-certified actor/history retirement beyond256 distinct windows, ordinary eligible capture and every original release gate.'}
(repo / 'docs/warlock-preview/v82/report.json').write_text(json.dumps(report, indent=2) + '\n')
sys.path.insert(0, str(repo / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(repo, 'f6779148-8f5d-4bdf-8a0f-044184e486f2', str(root.relative_to(repo)),
    ['PROGRESS native118 actual same-host third lease resume/image/ACK/physical drain PASS ' + str(len(proof['checks'])) + '/' + str(len(proof['ownedExitCodes'])) + ' normal exits, all' + str(len(old)) + 'stable116 controls retained. Failed117 fixture preserved. GUI81 full95/original11/newresume13/29/605/3mutants/C50Elm30 held. Next exact owner commit/publication then actor/history retirement and ordinary eligibility; all original release gates active.'],
    'progress', [str(manifest.relative_to(repo)), 'docs/warlock-preview/v82/report.json']))
