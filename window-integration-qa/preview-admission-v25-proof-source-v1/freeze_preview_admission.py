"""External V25 complete-union inventory; no native or installed mutations."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat

QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-preview-lock-admission-v25')
BASE=B.with_name('service-family-preparation-v24')/'manifest-family-preparation-v24.json'
BASE_SHA='b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c'
V9=QA/'family-preparation-thumbnail-v9/frozen-inputs.json'
V9_SHA='1820c23f20e585411a6245b23fb373b2119342ea441dce5dbcbb4000227b0444'
PROOF=QA/'preview-admission-v25-full-proof-v1/report.json'
READY=B/'source-ready-v25.json'
MANIFEST=B/'manifest-preview-admission-v25.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def closure_module():
    path=V9.parent/'collector_v9_closure.py'
    if sha(path)!='3ef9b46881587023d642cee353ed84b4bf8de6eb9e264bfbaf1448980e1c0742':raise ValueError('approved dual-alias implementation changed')
    spec=importlib.util.spec_from_file_location('v25_retained_alias',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def verify(packet):
    if set(packet['inputs'])!=set(packet['inputModes']):raise ValueError('complete byte/mode declarations required')
    module=closure_module();module.verify_links(packet['links'])
    for name,digest in packet['inputs'].items():module.retained_file(name,digest,packet['inputModes'][name],packet['inputs'],packet['inputModes'],packet['links'])
    module.verify_links(packet['links'])

def inventory():
    inputs={};modes={};links={}
    def merge(name,digest,mode):
        if name in inputs and (inputs[name]!=digest or modes[name]!=mode):raise ValueError('conflicting byte/mode alias: '+name)
        inputs[name]=digest;modes[name]=mode
    def add(path,expected=None,mode=None):
        path=Path(path).absolute();digest=sha(path);actual=stat.S_IMODE(path.stat().st_mode)
        if expected is not None and digest!=expected or mode is not None and actual!=mode:raise ValueError('source changed: '+str(path))
        for alias in (path,*path.parents):
            if alias.is_symlink():
                target=os.readlink(alias)
                if str(alias)in links and links[str(alias)]!=target:raise ValueError('conflicting selected link')
                links[str(alias)]=target
        # Explicitly capture the regular backing for every selected byte alias.
        merge(str(path.resolve(strict=True)),digest,actual);merge(str(path),digest,actual)
    for path,expected,key in ((BASE,BASE_SHA,'links'),(V9,V9_SHA,'symlinks')):
        if path.is_symlink()or sha(path)!=expected:raise ValueError('selected frozen manifest changed')
        packet=json.loads(path.read_text());normalized={**packet,'links':packet[key]};verify(normalized)
        for name,target in normalized['links'].items():
            if name in links and links[name]!=target:raise ValueError('inherited link conflict')
            links[name]=target
        for name,digest in packet['inputs'].items():merge(name,digest,packet['inputModes'][name])
        add(path,expected)
    proof=json.loads(PROOF.read_text())
    if (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'],proof['original100CommandsExact'])!=('pass',395,377,34,True,True):raise ValueError('complete original unfiltered proof required')
    if len(proof['checks'])!=103 or any(row['exitCode']for row in proof['checks']):raise ValueError('all required command completions absent')
    for name,row in proof['sources'].items():add(name,row['sha256'],row['mode'])
    for row in proof['checks']:add(row['log'],row['sha256'])
    add(PROOF)
    selected=json.loads((QA/'preview-lock-admission-design-v2/intended-source-map-final.json').read_text())
    for name,row in selected.items():add(B/name,row['proposedSHA256'],row['originalMode']);add(BASE.parent/name,row['originalSHA256'],row['originalMode'])
    provenance=json.loads((B/'v24-source-provenance.json').read_text());changed=[]
    for name,digest in provenance['copied'].items():
        original=BASE.parent/name;add(original,digest)
        current=B/name
        if stat.S_IMODE(current.stat().st_mode)!=stat.S_IMODE(original.stat().st_mode):raise ValueError('inherited mode changed')
        if sha(current)!=digest:changed.append(name)
    if sorted(changed)!=sorted(selected):raise ValueError('unapproved inherited source delta')
    for folder in (B,PROOF.parent,QA/'preview-lock-admission-design-v1',QA/'preview-lock-admission-design-v2',QA/'thumbnail-v9-agent-baseline-failure-v1',V9.parent/'attempt-baseline-1',QA/'readonly-reservation-contention-root-v1',QA/'controller-housekeeping-contention-root-v1',Path(__file__).parent):
        for path in folder.rglob('*'):
            if path.is_file()and '__pycache__'not in path.parts and path not in(READY,MANIFEST):add(path)
    for name,digest in (
        ('preview-lock-admission-root-review-v1.json','3b99c50346e70397f61710d15884e675ff7e7da27fb43b8c2d786503d98e9ed2'),
        ('preview-lock-admission-root-final-source-review-v1.json','0da5f1372d5909e5d0d66df3da3c0f9ef8bb4bd1744584c640d3f21873c07b71'),
        ('readonly-reservation-contention-root-v1/report.json','40b713c814021727c684b924b88b7864c49d02c9b1edb4a0d9a13908803197d1'),
        ('controller-housekeeping-contention-root-v1/report.json','571e740617230dc952d2555fbc266c3a062c2736fa9700d13cf8ab3e4e146336')):add(QA/name,digest)
    base=json.loads(BASE.read_text());fields={k:v for k,v in base.items()if k not in('inputs','inputModes','links','proof','proofSHA256','baseManifest','baseManifestSHA256','sourceReady','sourceReadySHA256','changedInheritedSources')}
    fields.update(version='preview-lock-admission-v25-source',baseManifest=str(BASE),baseManifestSHA256=BASE_SHA,retainedFailedNativeV9Manifest=str(V9),retainedFailedNativeV9ManifestSHA256=V9_SHA,
        changedInheritedSources=sorted(changed),proof=str(PROOF),proofSHA256=sha(PROOF),sourcePlan=str(QA/'preview-lock-admission-design-v2/source-handoff-final.json'),sourcePlanSHA256=sha(QA/'preview-lock-admission-design-v2/source-handoff-final.json'),
        admissionSourceImplemented=True,original38BaselineAccepted=False,original34FaultsAccepted=False,nativePerformanceAccepted=False,nativeAccepted=False,mainChanged=False,requestDeadlineSeconds=2,thumbnailDeadlineSeconds=1,housekeepDeadlineSeconds=.6,
        inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
    verify(fields);return fields

def write(path,packet):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as out:json.dump(packet,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())

def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    for flag in ('collect','freeze','verify'):group.add_argument('--'+flag,action='store_true')
    args=parser.parse_args()
    if args.verify:packet=json.loads(MANIFEST.read_text());verify(packet)
    elif args.collect:packet=inventory();write(READY,packet)
    else:
        ready=json.loads(READY.read_text());verify(ready);packet=inventory()
        if ready!=packet:raise ValueError('reviewed ready closure changed')
        packet={**packet,'sourceReady':str(READY),'sourceReadySHA256':sha(READY)};write(MANIFEST,packet)
    print(json.dumps(dict(result='pass',inputs=len(packet['inputs']),modes=len(packet['inputModes']),links=len(packet['links']),manifest=str(MANIFEST),nativeAccepted=False)))

if __name__=='__main__':main()
