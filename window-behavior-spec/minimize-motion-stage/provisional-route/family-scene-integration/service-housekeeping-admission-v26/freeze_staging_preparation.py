"""Reviewed V23 source closure; no deployment or native launches."""
from pathlib import Path
import argparse,hashlib,json,os,stat
B=Path(__file__).resolve().parent
BASE=B.with_name('service-family-preparation-v22')/'manifest-family-preparation-v22.json'
BASE_SHA='e616b23b7c397cc767ce91e855a4520dd42311c97087797b332772ba63d1fc5e'
QA=Path('/home/hoskinson/window-integration-qa')
PROOF=QA/'family-preparation-v23-full-proof-v1/report.json'
READY=B/'source-ready-v23.json'
MANIFEST=B/'manifest-family-preparation-v23.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(packet):
    if set(packet['inputs'])!=set(packet['inputModes']):raise ValueError('incomplete source modes')
    for p,h in packet['inputs'].items():
        if sha(p)!=h or stat.S_IMODE(Path(p).stat().st_mode)!=packet['inputModes'][p]:raise ValueError('source changed: '+p)
    for p,target in packet['links'].items():
        if not Path(p).is_symlink()or os.readlink(p)!=target:raise ValueError('link changed: '+p)
def inventory():
    if sha(BASE)!=BASE_SHA:raise ValueError('frozen V22 manifest changed')
    base=json.loads(BASE.read_text());verify(base);inputs=dict(base['inputs']);modes=dict(base['inputModes']);links=dict(base['links'])
    def add(p,expected=None,mode=None):
        p=Path(p).absolute();h=sha(p);actual=stat.S_IMODE(p.stat().st_mode)
        if expected is not None and h!=expected or mode is not None and actual!=mode:raise ValueError('witness changed: '+str(p))
        for alias in (p,p.resolve()):
            name=str(alias)
            if name in inputs and(inputs[name]!=h or modes[name]!=actual):raise ValueError('conflicting alias')
            inputs[name]=h;modes[name]=actual
        for alias in (p,*p.parents):
            if alias.is_symlink():
                target=os.readlink(alias)
                if str(alias)in links and links[str(alias)]!=target:raise ValueError('conflicting symlink')
                links[str(alias)]=target
    add(BASE,BASE_SHA)
    proof=json.loads(PROOF.read_text())
    if (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'])!=('pass',359,296,32,True):raise ValueError('required final proof absent')
    if len(proof['checks'])!=97 or any(c['exitCode'] for c in proof['checks']):raise ValueError('incomplete final commands')
    for p,w in proof['sources'].items():add(p,w['sha256'],w['mode'])
    for c in proof['checks']:add(c['log'],c['sha256'])
    changed=[];inherited=json.loads((B/'v22-source-inheritance-before-v23.json').read_text())
    for name,w in inherited['sources'].items():
        add(w['base'],w['sha256'],w['mode'])
        if stat.S_IMODE((B/name).stat().st_mode)!=w['mode']:raise ValueError('inherited mode changed')
        if sha(B/name)!=w['sha256']:changed.append(name)
    if changed!=['batch_preview.py']or len(inherited['sources'])!=134:raise ValueError('inherited source scope changed')
    plan=json.loads((B/'STAGING_SOURCE_PLAN-v2.json').read_text())
    if sha(B/'batch_preview.py')!=plan['proposedSHA256']or sha(B/'INTENDED_BATCH_PREVIEW_PATCH.diff')!=plan['patchSHA256']:raise ValueError('reviewed patch changed')
    if sha(Path(plan['formalPath']))!=plan['formalSHA256']:raise ValueError('formal-before-runtime proof changed')
    for n,h in plan['modelSHA256'].items():
        if sha(B/n)!=h:raise ValueError('reviewed staging model changed')
    for folder in (B,QA/'family-preparation-v23-full-proof-v1',QA/'family-preparation-v23-staging-replay-v1',QA/'family-preparation-v22-agent-review-v1'):
        for p in folder.rglob('*'):
            if p.is_file()and '__pycache__'not in p.parts and p not in (READY,MANIFEST):add(p)
    replay=json.loads((QA/'family-preparation-v23-staging-replay-v1/staging-lifecycle-replay.json').read_text())
    if replay['result']!='pass'or not replay['observation']['cleanupReturnedBeforeReadRelease']or not replay['observation']['receiptAcquiredBeforeReadRelease']or not replay['observation']['exactStagingEpochRefusedDuringScan']:raise ValueError('actual staging closure proof absent')
    fields={k:v for k,v in base.items()if k not in ('inputs','inputModes','links','proof','proofSHA256','baseManifest','baseManifestSHA256','changedInheritedSources')}
    fields.update(baseManifest=str(BASE),baseManifestSHA256=BASE_SHA,changedInheritedSources=changed,ancestralV20Changes=base['changedInheritedSources'],proof=str(PROOF),proofSHA256=sha(PROOF),sourcePlan=str(B/'STAGING_SOURCE_PLAN-v2.json'),sourcePlanSHA256=sha(B/'STAGING_SOURCE_PLAN-v2.json'),original38BaselineAccepted=False,original34FaultsAccepted=False,nativePerformanceAccepted=False,inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
    verify(fields);return fields

def write(path,packet):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(packet,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--collect',action='store_true');g.add_argument('--freeze',action='store_true');g.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.verify:
        packet=json.loads(MANIFEST.read_text());verify(packet)
    elif a.collect:
        packet=inventory();write(READY,packet)
    else:
        if not READY.is_file():raise ValueError('reviewable source-ready required')
        ready=json.loads(READY.read_text());verify(ready);packet=inventory()
        if packet!=ready:raise ValueError('source-ready closure differs')
        packet={**packet,'sourceReady':str(READY),'sourceReadySHA256':sha(READY)};write(MANIFEST,packet)
    print(json.dumps(dict(result='pass',inputs=len(packet['inputs']),modes=len(packet['inputModes']),links=len(packet['links']),manifest=str(MANIFEST),nativeAccepted=False)))
if __name__=='__main__':main()
