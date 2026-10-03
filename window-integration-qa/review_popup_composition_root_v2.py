#!/usr/bin/python3
"""Review source-only full-popup and observed-input composition."""
import datetime,hashlib,json,os,re,stat
from pathlib import Path
Q=Path('/home/hoskinson/window-integration-qa');B=Q/'pin-frontend-composition-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ready=B/'source-ready-v2.json'
assert sha(ready)=='9a4a936b861e044f0891609aa367724b9d92d9362ea06ecd511a35c388017aa2'
r=json.loads(ready.read_bytes())
assert len(r['inputs'])==1828 and set(r['inputs'])==set(r['inputModes']) and len(r['symlinks'])==2
for p,h in r['inputs'].items():
    assert sha(p)==h and stat.S_IMODE(Path(p).stat().st_mode)==r['inputModes'][p]
for p,target in r['symlinks'].items():assert Path(p).is_symlink() and os.readlink(p)==target
plan=json.loads(Path('/home/hoskinson/window-behavior-spec/process-private-qs-route-plan-v1/source-plan-handoff.json').read_bytes())
assert len(plan['inputs'])==1518
for field in ['inputs','inputModes','symlinks']:
    assert all(r[field].get(k)==v for k,v in plan[field].items())
build=json.loads((B/'probe-build-report.json').read_bytes())
assert sha(B/'probe-build-report.json')=='fec6e7ffc62604168b94564cf96f768c348f0717ceb8c73c877e4a2cd86d52e3'
assert build['result']=='pass' and build['sourceStable'] and build['nativeLoaded'] is False
assert len(build['selectedDependencies'])==606 and all(x['exitCode']==0 for x in build['commands'])
for p,w in build['inputs'].items():assert r['inputs'][p]==w['sha256'] and r['inputModes'][p]==w['mode']
for p in build['selectedDependencies']:assert p in build['inputs']
assert sha(build['binary'])==build['binarySHA256']
formal=json.loads((B/'formal-composition-v3-before-source.json').read_bytes())
assert formal['result']=='pass' and formal['sourceStable'] and formal['implementationAbsent'] and formal['models']==1
assert all(x['exitCode']==0 for x in formal['commands'])
assert any('24 passing' in x['stdout'] or '24 passing' in x['stderr'] for x in formal['commands'])
assert any('--max-samples=2000' in x['command'] and '--max-steps=100' in x['command'] and '[ok] No violation found' in x['stdout'] for x in formal['commands'])
for name,count in [('cpu-report.json',28),('cpu-receipt-loop-v2-report.json',1)]:
    x=json.loads((B/name).read_bytes())
    assert x['result']=='pass' and x['exitCode']==0 and x['sourceStable']
    assert re.search(r'Ran '+str(count)+r' tests?\b',x['stderr']) and x['stderr'].rstrip().endswith('OK')
    assert x['controlledDataNotNativeAuthority'] is True
    for p,h in x['sourceSHA256'].items():assert sha(p)==h
js=json.loads((B/'qml-js-v2-cpu-report.json').read_bytes())
assert js['result']=='pass' and js['exitCode']==0 and js['sourceStable'] and js['actualQtQSNativeSemantics'] is False
conservation=json.loads((B/'source-conservation-report.json').read_bytes())
assert conservation['result']=='pass' and len(conservation['checks'])==48 and all(x['passed'] for x in conservation['checks'])
for flag in ['installedQSPositiveAccepted','nonNullPopupAccepted','actualInputDeliveryAccepted','reliabilityAccepted','nativeRunnable','GUI','mainChanges']:assert r[flag] is False
out=Q/'popup-composition-root-source-review-v2.json'
row=dict(result='pass',schema='root-popup-composition-source-review-v2',observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    sourceReadySHA256=sha(ready),reviewToolSHA256=sha(__file__),inputs=1828,links=2,
    fullPlanAndV10AncestorConserved=True,originalA2ProtocolUnchanged=True,originalActionPredicatesAndBudgetsConserved=True,
    focusedDecoderControllerCPU=28,originalReceiptLoopCPU=1,exactQMLAsJavaScriptChecks=6,actualQtQSClaim=False,
    formalNamed=24,formalTraces=2000,sourceInverseChecks=48,actualProbeCompiled=True,actualProbeLoaded=False,
    reviewed='All four complete source diffs, exact popup/context decoder, balanced mouse/Return episode decoder, original effect reconstruction, 24-case Quint model, proof/build/dependency closure and source-only provenance.',
    approved='Prepare a fresh source-only private installed-Quickshell launcher/materialization packet with exact compatible core/plugin/probe/provider tuple and owned helper/config seal; preserve original feature gates and fixed reliability schedule. Root review and freeze precede GUI grant.',
    GUIAuthorized=False,nativeAccepted=False,fullParityAccepted=False,mainChanged=False)
raw=(json.dumps(row,indent=2)+'\n').encode()
with os.fdopen(os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
fd=os.open(out.parent,os.O_RDONLY|os.O_DIRECTORY)
try:os.fsync(fd)
finally:os.close(fd)
print(json.dumps({'result':'pass','reviewSHA256':sha(out),'sourceInputs':1828,'GUIAuthorized':False}))
