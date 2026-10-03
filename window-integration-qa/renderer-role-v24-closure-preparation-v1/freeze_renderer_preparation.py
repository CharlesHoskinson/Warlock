"""V24 reviewed CPU source closure, with failed native V7 retained."""
from pathlib import Path
import argparse,hashlib,json,os,stat

B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
BASE=B.with_name('service-family-preparation-v23')/'manifest-family-preparation-v23.json'
BASE_SHA='0d2b7b231eaa26c6618783b1cb2305c2a989586b3a7cb371716e2d67603c82e2'
QA=Path('/home/hoskinson/window-integration-qa')
V7=QA/'family-preparation-thumbnail-v7/frozen-inputs.json'
V7_SHA='d066ecf9b9ec94f0fe096d117464ba0f611f5b4d655792c0f1f8c6c339cd90eb'
PROOF=QA/'family-preparation-v24-full-proof-replay-v2/report.json'
READY=B/'source-ready-v24.json'
MANIFEST=B/'manifest-family-preparation-v24.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify(packet):
    if set(packet['inputs'])!=set(packet['inputModes']):raise ValueError('incomplete exact byte/mode closure')
    for p,h in packet['inputs'].items():
        if sha(p)!=h or stat.S_IMODE(Path(p).stat().st_mode)!=packet['inputModes'][p]:raise ValueError('closure changed: '+p)
    for p,target in packet['links'].items():
        if not Path(p).is_symlink()or os.readlink(p)!=target:raise ValueError('closure link changed: '+p)

def inventory():
    if sha(BASE)!=BASE_SHA:raise ValueError('frozen V23 manifest changed')
    base=json.loads(BASE.read_text());verify(base)
    inputs=dict(base['inputs']);modes=dict(base['inputModes']);links=dict(base['links'])
    def add(p,expected=None,mode=None):
        p=Path(p).absolute();h=sha(p);actual=stat.S_IMODE(p.stat().st_mode)
        if expected is not None and h!=expected or mode is not None and actual!=mode:raise ValueError('witness changed: '+str(p))
        for alias in (p,p.resolve()):
            name=str(alias)
            if name in inputs and(inputs[name]!=h or modes[name]!=actual):raise ValueError('conflicting alias: '+name)
            inputs[name]=h;modes[name]=actual
        for alias in (p,*p.parents):
            if alias.is_symlink():
                target=os.readlink(alias)
                if str(alias)in links and links[str(alias)]!=target:raise ValueError('conflicting symlink')
                links[str(alias)]=target
    add(BASE,BASE_SHA)
    if sha(V7)!=V7_SHA:raise ValueError('frozen failed V7 manifest changed')
    original_v7=json.loads(V7.read_text())
    # V7's frozen host schema uses symlinks; bind its exact known schema.
    verify({'inputs':original_v7['inputs'],'inputModes':original_v7['inputModes'],'links':original_v7['symlinks']})
    for p,h in original_v7['inputs'].items():add(p,h,original_v7['inputModes'][p])
    for p,target in original_v7['symlinks'].items():
        if p in links and links[p]!=target:raise ValueError('inherited link conflict')
        links[p]=target
    add(V7,V7_SHA)
    proof=json.loads(PROOF.read_text())
    if (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'])!=('pass',377,332,33,True):raise ValueError('complete inherited and role proof required')
    prior=json.loads((QA/'family-preparation-v23-full-proof-v1/report.json').read_text())
    if len(proof['checks'])!=100 or any(c['exitCode']for c in proof['checks'])or [c['command']for c in proof['checks'][:97]]!=[c['command']for c in prior['checks']]:raise ValueError('original commands or final gate changed')
    for p,w in proof['sources'].items():add(p,w['sha256'],w['mode'])
    for c in proof['checks']:add(c['log'],c['sha256'])
    inherited=json.loads((B/'v23-source-inheritance-before-v24.json').read_text());changed=[]
    for name,w in inherited['sources'].items():
        add(w['base'],w['sha256'],w['mode'])
        if stat.S_IMODE((B/name).stat().st_mode)!=w['mode']:raise ValueError('inherited mode changed')
        if sha(B/name)!=w['sha256']:changed.append(name)
    if sorted(changed)!=['batch_preview.py','native_runtime.py']or len(inherited['sources'])!=141:raise ValueError('unexpected inherited delta')
    plan=json.loads((B/'RENDERER_ROLE_SOURCE_PLAN-v5.json').read_text())
    if sha(B/'INTENDED_RENDERER_ROLE_PATCH-v5.diff')!=plan['patchSHA256']:raise ValueError('reviewed intended patch changed')
    for n,w in plan['sources'].items():
        if sha(B/n)!=w['proposedSHA256']or sha(B.with_name('service-family-preparation-v23')/n)!=w['beforeSHA256']:raise ValueError('reviewed runtime correction differs')
    formal=json.loads((B/'renderer-role-formal-before-runtime-v3.json').read_text())
    if (formal['result'],formal['namedCases'],formal['samples'],formal['steps'],formal['runtimeUnchanged'])!=('pass',36,2000,100,True):raise ValueError('formal-before-runtime proof absent')
    for n,h in formal['modelSHA256'].items():add(B/n,h)
    for n,h in formal['runtimeBeforeSHA256'].items():add(B.with_name('service-family-preparation-v23')/n,h)
    focused=QA/'renderer-role-focused-replay-v2/report.json';adapter=QA/'renderer-role-adapter-lock-replay-v1/report.json'
    a=json.loads(adapter.read_text());f=json.loads(focused.read_text())
    if f['result']!='pass'or f['exitCode']!=0 or not f['sourceUnchanged']:raise ValueError('actual focused role proof absent')
    for n,w in f['sources'].items():add(B/n,w['sha256'],w['mode'])
    if a['result']!='pass'or len(a['cases'])!=2 or not a['sourceUnchanged']:raise ValueError('actual adapter proof absent')
    for n,h in a['sourceSHA256'].items():add(B/n,h)
    for case in a['cases']:
        if not case['receiptAndKeeperReturnedBeforeMaterialRelease']or not case['actualNativeDesktopAdapter']or not all(case['cleanup'].values()):raise ValueError('actual locks/terminal proof absent')
    for folder in (B,PROOF.parent,QA/'family-preparation-v24-full-proof-v1',QA/'renderer-job-closure-counterexample-v1',QA/'renderer-role-focused-failure-v1',focused.parent,adapter.parent,QA/'renderer-role-v7-failure-replay-v1',V7.parent/'attempt-baseline-1',Path(__file__).resolve().parent):
        for p in folder.rglob('*'):
            if p.is_file()and '__pycache__'not in p.parts and p not in (READY,MANIFEST):add(p)
    fields={k:v for k,v in base.items()if k not in ('inputs','inputModes','links','proof','proofSHA256','baseManifest','baseManifestSHA256','changedInheritedSources','sourceReady','sourceReadySHA256')}
    fields.update(version='family-preparation-v24-source',baseManifest=str(BASE),baseManifestSHA256=BASE_SHA,
        retainedFailedNativeV7Manifest=str(V7),retainedFailedNativeV7ManifestSHA256=sha(V7),changedInheritedSources=sorted(changed),
        proof=str(PROOF),proofSHA256=sha(PROOF),sourcePlan=str(B/'RENDERER_ROLE_SOURCE_PLAN-v5.json'),sourcePlanSHA256=sha(B/'RENDERER_ROLE_SOURCE_PLAN-v5.json'),
        rendererRoleImplemented=True,rendererNativeCoexistenceAccepted=False,original38BaselineAccepted=False,original34FaultsAccepted=False,
        nativePerformanceAccepted=False,nativeAccepted=False,mainChanged=False,requestDeadlineSeconds=2,thumbnailDeadlineSeconds=1,
        inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
    verify(fields);return fields

def write(path,packet):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:
        json.dump(packet,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def main():
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--collect',action='store_true');g.add_argument('--freeze',action='store_true');g.add_argument('--verify',action='store_true');args=parser.parse_args()
    if args.verify:packet=json.loads(MANIFEST.read_text());verify(packet)
    elif args.collect:packet=inventory();write(READY,packet)
    else:
        ready=json.loads(READY.read_text());verify(ready);packet=inventory()
        if ready!=packet:raise ValueError('reviewed ready closure differs')
        packet={**packet,'sourceReady':str(READY),'sourceReadySHA256':sha(READY)};write(MANIFEST,packet)
    print(json.dumps(dict(result='pass',inputs=len(packet['inputs']),modes=len(packet['inputModes']),links=len(packet['links']),manifest=str(MANIFEST),nativeAccepted=False)))

if __name__=='__main__':main()
