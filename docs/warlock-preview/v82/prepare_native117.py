"""Derive native117 from held116; add a third actual picker lease only."""
import ast, hashlib, json, pathlib, resource, shutil, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent = repo / 'implementation/warlock-client-provider-native-v116'
target = repo / 'implementation/warlock-client-provider-native-v117'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
manifest = parent / 'component-manifest.json'
held = json.loads(manifest.read_text())
assert held['passed'] and held['sourceHeld'] and not target.exists()
for name, row in held['files'].items():
    assert sha(parent / name) == row['sha256'], name
provider = repo / 'implementation/warlock-preview-provider-v81/component-manifest.json'
gui = json.loads(provider.read_text())
assert gui['passed'] and gui['sourceHeld'] and 'nextResumeReport' in gui
def ignore(path, names):
    return [name for name in names if name in {'component-manifest.json', 'preflight.json', 'ANCESTRY.json', '__pycache__'} or (pathlib.Path(path) == parent / 'qa' and name.startswith(('native-', 'prepare-')))]
shutil.copytree(parent, target, ignore=ignore)
path = target / 'qa/prepare.py'
text = path.read_text()
assert text.count("provider=REPO/'implementation/warlock-preview-provider-v80'") == 1
text = text.replace("provider=REPO/'implementation/warlock-preview-provider-v80'", "provider=REPO/'implementation/warlock-preview-provider-v81'")
marker = ' assert all(sha(p)==h for p,h in inputs.items());'
assert text.count(marker) == 1
extra = " nextResumeReport=pathlib.Path(providerHeld['nextResumeReport']);resumeNext=json.loads(nextResumeReport.read_text());assert resumeNext['passed'] and resumeNext['namedScenarios']==13 and len(resumeNext['coupledTraces'])==29 and resumeNext['unsafeMutantsDetected']==3 and resumeNext['wireControls']['checks']==30 and resumeNext['wireControls']['cControls']==50;inputs[str(nextResumeReport)]=sha(nextResumeReport);pre['nextResumeReport']=str(nextResumeReport)\n"
extra += " prior116=REPO/'" + str(pathlib.Path(held['nativeReport']).relative_to(repo)) + "';proof116=json.loads(prior116.read_text());assert proof116['passed'] and proof116['cleanupPassed'] and len(proof116['checks'])==2433 and all(row['exitCode']==0 for row in proof116['ownedExitCodes']);inputs[str(prior116)]=sha(prior116);pre['retainedNative116Report']=str(prior116)\n"
text = text.replace(marker, extra + marker)
ast.parse(text)
path.write_text(text)
path = target / 'qa/native.py'
text = path.read_text()
marker = "   web.terminate();web.wait(timeout=5);check('feedbackGUIFullHostNormalExit'"
assert text.count(marker) == 1
text = text.replace(marker, (repo / 'docs/warlock-preview/v82/native-third-lease.inc').read_text() + marker)
# Retain the exact old assertion order while adding an independent116 audit.
marker = " check('allPriorNative105StableOrderedAssertionsRetained',"
start = text.index(marker)
end = text.index('\n', start) + 1
extra = " prior116=json.loads(pathlib.Path(pre['retainedNative116Report']).read_text());prior116Stable=stableNames(prior116['checks']);prior116Names=set(prior116Stable)\n check('allPriorNative116StableOrderedAssertionsRetained',len(prior116['checks'])==2433 and [name for name in stableNames(r['checks']) if name in prior116Names]==prior116Stable,stableControls=len(prior116Stable),priorRawControls=2433)\n"
text = text[:end] + extra + text[end:]
ast.parse(text)
path.write_text(text)
(target / 'ANCESTRY.json').write_text(json.dumps({
    'owner': 'f6779148-8f5d-4bdf-8a0f-044184e486f2', 'parent': str(parent),
    'parentManifestSHA256': sha(manifest), 'providerManifest': str(provider),
    'providerManifestSHA256': sha(provider),
    'purpose': 'Current held GUI81; unchanged owning ABI and original116 campaign. Add third real pointer picker lease after an unissued companion resume expires. Verify retained original job/cutoff/exact physical-terminal drain, fresh native2s successor request2, actual owned image and exact ACK; retain all stable116 ordered controls. No original deadline or oracle changes.',
    'nativeAcceptance': False, 'fullReleaseAccepted': False
}, indent=2) + '\n')
sys.path.insert(0, str(repo / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(repo, 'f6779148-8f5d-4bdf-8a0f-044184e486f2', str(target.relative_to(repo)),
    ['PROGRESS GUI81 held full95/original11/newresume13/29/605/3mutants/C50Elm30. Fresh native117 adds third actual picker lease after companion unissued resume expiry and old physical/journal drain; all116 stable identities/deadlines retained. Next protected preflight then serial owning-ABI native GUI. Full release remains open.'],
    'progress', [str((target / 'ANCESTRY.json').relative_to(repo))]))
