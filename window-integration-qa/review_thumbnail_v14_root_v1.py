#!/usr/bin/python3
"""Independent review of the original unprofiled collector and V28 pairing."""
import datetime, hashlib, importlib.util, json, os, re, stat, sys
from pathlib import Path
Q=Path('/home/hoskinson/window-integration-qa')
D=Q/'thumbnail-v14-pairing-proposal-v1'
sys.path.insert(0,str(D))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
H=Q/'thumbnail-v14-source-handoff-v1.json'
R=Q/'thumbnail-v14-source-ready-v1.json'
assert sha(H)=='78cb609f1350c07594295fa46643abb63153cbb02acac4367ab0c01e34c4410a'
assert sha(R)=='725ecd721723ad1f89359137658d64757b2633572478b33a6a202ee10dccce56'
F=D/'freeze_collector_v14.py'
assert sha(F)=='7139ce6ec455ea9870efe9f323566c19c2caeff10cc07510c45e9a892883bd8d'
spec=importlib.util.spec_from_file_location('review_b14_freezer',F)
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
ready=json.loads(R.read_bytes());f.verify(ready)
current=f.inventory()
assert current==ready
assert len(ready['inputs'])==23441 and len(ready['symlinks'])==287
for path,digest,key in f.selected_packets():
    ancestor=json.loads(path.read_bytes())
    for field in ['inputs','inputModes']:
        assert all(ready[field].get(k)==v for k,v in ancestor[field].items())
    assert all(ready['symlinks'].get(k)==v for k,v in ancestor[key].items())
proof_path=Q/'thumbnail-v14-cpu-proof-v1/report.json'
assert sha(proof_path)=='8acac3c2c5a52ee81af0f4e6cb8a876dfbc51c584929a773c22dc03bf6da7eb3'
proof=json.loads(proof_path.read_bytes())
cpu=proof['checks'][0]
assert cpu['exitCode']==0 and cpu['argv']==['/usr/bin/python3','-B',str(f.B/'run_collector_v9_cpu.py')]
assert cpu['cwd']=='/home/hoskinson'
text=Path(cpu['log']).read_text()
actual={name+'.'+method:status for method,name,status in re.findall(r'^(test\S+) \(([^)]+)\) \.\.\. (.*)$',text,re.M)}
assert actual==proof['perTestResults'] and len(actual)==169 and all(v=='ok' for v in actual.values())
assert 'Ran 169 tests' in text and text.rstrip().endswith('OK')
assert proof['originalUnfilteredTestIdentitiesExact'] and proof['sourceUnchangedDuringProof']
assert proof['allModelsNewlyRun'] is False and len(proof['checks'])==43
for old,w in proof['retainedFormalDependencies'].items():
    assert sha(old)==sha(w['current'])==w['sha256']
    assert stat.S_IMODE(Path(old).stat().st_mode)==stat.S_IMODE(Path(w['current']).stat().st_mode)==w['mode']
assert ready['changedCollectorSources']==['module_binding.py','native_faults.py']
assert ready['originalBaselineRequired']==38 and ready['originalFaultsRequired']==34
assert ready['profileInstalled'] is False and ready['nativeAccepted'] is False
out=Q/'thumbnail-v14-root-source-review-v1.json'
row=dict(result='pass',schema='root-thumbnail-v14-source-review-v1',observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    handoffSHA256=sha(H),sourceReadySHA256=sha(R),freezerSHA256=sha(F),reviewToolSHA256=sha(__file__),
    files=len(ready['inputs']),links=len(ready['symlinks']),actualCPU=169,retainedModels=14,retainedNamedScenarios=205,
    allModelsNewlyRun=False,wholeAncestorsConserved=True,wholeCollectorInverseExact=True,unprofiledObserverExact=True,
    selectedManifestSHA256=ready['selectedServiceManifestSHA256'],originalBaselineRequired=38,originalFaultsRequired=34,
    approved='Freeze the reviewed complete union; verify; run one original unprofiled baseline38 in its private QA scope. Fault34 remains ungranted.',
    reviewed='Original runner, source conservation, two selector patch, freezer publication/union, actual CPU driver and proof, compatible native tuple and QA crash guards.',
    nativeAccepted=False,mainChanged=False)
raw=(json.dumps(row,indent=2)+'\n').encode()
with os.fdopen(os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as stream:
    stream.write(raw);stream.flush();os.fsync(stream.fileno())
fd=os.open(out.parent,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps(dict(result='pass',reviewSHA256=sha(out),files=len(ready['inputs']),actualCPU=169,nativeAccepted=False)))
