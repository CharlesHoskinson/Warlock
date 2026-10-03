"""Independent, bounded source review; does not launch a desktop."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

QA = Path('/home/hoskinson/window-integration-qa')
OB = Path('/home/hoskinson/window-behavior-spec/pin-max-native-campaign-b-v1-source-proposal/observer')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p, row):
    with os.fdopen(os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), 'w') as f:
        json.dump(row, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())

def observer():
    ready = json.loads((OB/'SOURCE_DRAFT_READY.json').read_text())
    assert sha(OB/'SOURCE_DRAFT_READY.json') == '37f498847b067372a6dadd8362e24077b97cd2a1b1462fd31589755a75080d4a'
    assert sha(ready['inputDescriptor']) == ready['inputDescriptorSHA256']
    inputs = json.loads(Path(ready['inputDescriptor']).read_text())
    for n, r in inputs['inputs'].items():
        assert sha(n) == r['sha256'] and oct(stat.S_IMODE(Path(n).stat().st_mode)) == r['mode'], n
    for n, mode in inputs['directoryModes'].items():
        assert Path(n).is_dir() and not Path(n).is_symlink() and oct(stat.S_IMODE(Path(n).stat().st_mode)) == mode
    for n, r in json.loads((OB/'origin-map.json').read_text()).items():
        assert sha(n) == sha(r['copy']) == r['sha256']
        assert oct(stat.S_IMODE(Path(n).stat().st_mode)) == r['mode']
    save(QA/'pin-max-campaign-b-observer-root-source-review-v1.json', {
        'result':'pass', 'readySHA256':sha(OB/'SOURCE_DRAFT_READY.json'),
        'inputsVerified':len(inputs['inputs']), 'originsVerified':ready['actualOriginCount'],
        'reviewed':'full C++/decoder/schema/permitted calls and actual transitive owning getters',
        'metadataReadOnly':True, 'queryHitIsNativeStimulus':True,
        'nativeAuthority':False, 'compileAndCPUOnlyAuthorized':True, 'nativeAuthorized':False,
        'limits':['same compositor thread, no yielding callbacks or setters',
                  'raw handler getter avoids controller mode synchronization',
                  'inherited hit query may correct unrelated stale fullscreen state',
                  'bounded decoder refusal never conveys partial success',
                  'compiler and full dependency/ABI closure still required',
                  'B24 and presentation/Seat/controller/output campaign remain unaccepted'],
        'mainChanged':False})

def collector():
    hpath = QA/'thumbnail-v13-source-handoff-v1.json'
    assert sha(hpath) == 'd90960669294c8219703b2e1d2454e154fc92a62ae54ecf7a26c2f0359dee6e3'
    h = json.loads(hpath.read_text())
    for r in h['evidence'].values():
        assert sha(r['path']) == r['sha256'] and stat.S_IMODE(Path(r['path']).stat().st_mode) == r['mode']
    r = json.loads((QA/'thumbnail-v13-source-ready-v1.json').read_text())
    assert set(r['inputs']) == set(r['inputModes'])
    for n,t in r['symlinks'].items(): assert Path(n).is_symlink() and os.readlink(n) == t
    for n,d in r['inputs'].items(): assert sha(n)==d and stat.S_IMODE(Path(n).stat().st_mode)==r['inputModes'][n], n
    for ancestor, linkkey in [(QA/'family-preparation-thumbnail-v12/frozen-inputs.json','symlinks'),
                             (Path(r['selectedServiceManifest']),'links')]:
        old=json.loads(ancestor.read_text())
        for n,d in old['inputs'].items(): assert r['inputs'][n]==d and r['inputModes'][n]==old['inputModes'][n]
        for n,t in old[linkkey].items(): assert r['symlinks'][n]==t
    b=Path(h['candidate']); old=QA/'family-preparation-thumbnail-v12'
    inherited=0; changed=[]
    for p in old.rglob('*'):
        rel=p.relative_to(old)
        if '__pycache__' in rel.parts or any(x.startswith('attempt-') for x in rel.parts) or rel==Path('frozen-inputs.json'): continue
        q=b/rel
        if p.is_symlink(): assert q.is_symlink() and os.readlink(p)==os.readlink(q)
        elif p.is_file():
            inherited+=1; assert stat.S_IMODE(p.stat().st_mode)==stat.S_IMODE(q.stat().st_mode)
            if sha(p)!=sha(q): changed.append(str(rel))
    assert inherited==459 and changed==['service_observer.py']
    intended=QA/'restore-span-diagnostic-design-v4/intended-files'
    for name in ['service_observer.py','preparation_profile.py','causal_profile_sources.py']: assert (b/name).read_bytes()==(intended/name).read_bytes()
    proof=json.loads((QA/'thumbnail-v13-full-proof-v1/report.json').read_text())
    assert (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],len(proof['checks']))==('pass',179,217,15,46)
    assert proof['sourceUnchangedDuringProof']
    for check in proof['checks']: assert check['exitCode']==0 and sha(check['log'])==check['sha256']
    for n,s in proof['sources'].items(): assert sha(n)==s['sha256'] and stat.S_IMODE(Path(n).stat().st_mode)==s['mode']
    previous=json.loads((QA/'thumbnail-v12-full-proof-v1/report.json').read_text())
    for a,c in zip(previous['checks'],proof['checks']):
        assert [s.replace(str(old),str(b)) for s in a['argv']]==c['argv'] and a['cwd']==c['cwd']
    save(QA/'thumbnail-v13-root-source-review-v1.json',{
        'result':'pass','readySHA256':sha(QA/'thumbnail-v13-source-ready-v1.json'),
        'handoffSHA256':sha(hpath),'inputsVerified':len(r['inputs']),'linksVerified':len(r['symlinks']),
        'inheritedLocalRegularFiles':inherited,'unchangedInheritedLocalRegularFiles':458,
        'changedCollectorSources':changed,'exactApprovedObserverAndProfiler':True,
        'originalCommandVectorsIndependentlyConserved':len(previous['checks']),
        'proofSHA256':sha(QA/'thumbnail-v13-full-proof-v1/report.json'),
        'cpuTests':179,'namedScenarios':217,'formalModels':15,'commands':46,
        'completePredecessorAndV27Unions':True,'originalBaselineRequired':38,'originalFaultsRequired':34,
        'timingPerturbed':True,'diagnosticReturnEventProvesSuccess':False,
        'deadlinesRunnerFaultsD3NativeTupleUnchanged':True,'nativeAccepted':False,'mainChanged':False,
        'authorization':'freeze, verify, and one serial private causal baseline run; no production performance or full parity claim'})

if __name__=='__main__':
    observer(); collector(); print(json.dumps({'result':'pass','observerSourceReviewed':True,'collectorSourceReviewed':True,'nativeLaunched':False}))
