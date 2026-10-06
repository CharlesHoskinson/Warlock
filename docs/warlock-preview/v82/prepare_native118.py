"""Preserve117; correct only the new trigger-versus-job fixture comparison."""
import ast, hashlib, json, pathlib, resource, shutil, stat, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent = repo / 'implementation/warlock-client-provider-native-v117'
target = repo / 'implementation/warlock-client-provider-native-v118'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
reports = list(parent.glob('qa/native-*/report.json'))
assert len(reports) == 1
failure = reports[0]
proof = json.loads(failure.read_text())
assert not proof['passed'] and proof['cleanupPassed']
assert all(row['exitCode'] == 0 for row in proof['ownedExitCodes'])
assert [row['name'] for row in proof['checks'] if not row['passed']] == ['nextResumeGUIExpiredWaitingIntentKeepsOriginalJobAndCutoff']
for name, value in proof['artifacts'].items():
    assert sha(failure.parent / name) == value, name
bad = next(row for row in proof['checks'] if not row['passed'])
text = (failure.parent / 'private-evidence/full-imported-feedback.log').read_text()
events = [event for line in text.splitlines() if line.startswith('native-client-events: ') for event in json.loads(line.split(': ', 1)[1])]
requests = [event['event']['trigger'] for event in events if event['kind'] == 'event' and event['event']['kind'] == 'request' and event['identity'] == bad['expired']['identity']]
projected = {key: value for key, value in bad['owner']['job'].items() if key != 'request'}
assert requests == [projected] and bad['owner']['job']['request'] == '1'
assert bad['owner']['resumeDeadline'] == bad['expired']['deadline']
assert bad['owner']['records'] == 0 and int(bad['owner']['charge']) == 0
assert bad['owner']['mappedFDClosed'] and bad['owner']['exportReleased'] and bad['owner']['producerRetired'] and not bad['owner']['retirementPending']
files = {str(path.relative_to(parent)): {'kind': 'file', 'sha256': sha(path), 'size': path.stat().st_size, 'mode': oct(stat.S_IMODE(path.stat().st_mode))} for path in sorted(parent.rglob('*')) if path.is_file() and '__pycache__' not in path.parts}
manifest = parent / 'component-manifest.json'
assert not manifest.exists() and not target.exists()
manifest.write_text(json.dumps({'sourceHeld': True, 'passed': False, 'evidenceIntegrityPassed': True,
    'files': files, 'nativeReport': str(failure), 'nativeAcceptance': False, 'fullReleaseAccepted': False,
    'failure': 'New fixture compared request trigger (no request field by typed contract) with complete known job. Actual one original trigger, original job request1, expired lease2 native cutoff and all physical/journal retirement hold. Fresh118 corrects only this projection comparison; retain all original deadlines and oracles.'}, indent=2) + '\n')
def ignore(path, names):
    return [name for name in names if name in {'component-manifest.json', 'preflight.json', 'ANCESTRY.json', '__pycache__'} or (pathlib.Path(path) == parent / 'qa' and name.startswith(('native-', 'prepare-')))]
shutil.copytree(parent, target, ignore=ignore)
path = target / 'qa/native.py'
text = path.read_text()
old = "companionRequests==[oldCompanion['job']]"
new = "companionRequests==[{key:value for key,value in oldCompanion['job'].items() if key!='request'}]"
assert text.count(old) == 1
text = text.replace(old, new)
ast.parse(text)
path.write_text(text)
path = target / 'qa/prepare.py'
text = path.read_text()
marker = ' assert all(sha(p)==h for p,h in inputs.items());'
assert text.count(marker) == 1
extra = " failed117=REPO/'" + str(failure.relative_to(repo)) + "';proof117=json.loads(failed117.read_text());assert not proof117['passed'] and proof117['cleanupPassed'] and [row['name'] for row in proof117['checks'] if not row['passed']]==['nextResumeGUIExpiredWaitingIntentKeepsOriginalJobAndCutoff'] and all(row['exitCode']==0 for row in proof117['ownedExitCodes']);inputs[str(failed117)]=sha(failed117);pre['retainedFailedTriggerProjectionFixture']=str(failed117)\n"
text = text.replace(marker, extra + marker)
ast.parse(text)
path.write_text(text)
(target / 'ANCESTRY.json').write_text(json.dumps({'owner': 'f6779148-8f5d-4bdf-8a0f-044184e486f2',
    'parent': str(parent), 'parentManifestSHA256': sha(manifest),
    'purpose': 'Unchanged held GUI81 and owning ABI. Correct only the new117 request-trigger projection comparison; actual complete original job still checked independently. Preserve failed117, original native2s/six-second observation deadline and every116 ordered control.',
    'nativeAcceptance': False, 'fullReleaseAccepted': False}, indent=2) + '\n')
sys.path.insert(0, str(repo / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(repo, 'f6779148-8f5d-4bdf-8a0f-044184e486f2', str(target.relative_to(repo)),
    ['PROGRESS117 preserved failed new trigger/fullJob fixture comparison; actual original trigger/job1/expired native cutoff/physical journal drain verified, all119 owned exits normal. Fresh118 corrects only typed projection comparison. Next protected preflight and serial native. GUI81 unchanged held; all original release gates active.'],
    'progress', [str(manifest.relative_to(repo)), str((target / 'ANCESTRY.json').relative_to(repo))]))
