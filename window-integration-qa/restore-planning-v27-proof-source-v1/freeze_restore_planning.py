"""Complete V27 source/evidence inventory; root owns final freeze/native."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat

QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')
BASE=B.with_name('service-housekeeping-admission-v26')/'manifest-housekeeping-admission-v26.json'
BASE_SHA='e98809f3cee21c3fc8a0447c98c76915cc3083df2ac1090f1531c7fa3b25a1b2'
B11=QA/'family-preparation-thumbnail-v11/frozen-inputs.json'
B11_SHA='53f6ddde08633dc3bfab3cbadfde2997695bf189b095382e2805cd1e8441a3c9'
DESIGN=QA/'restore-planning-design-v4'
PROOF=QA/'restore-planning-v27-full-proof-v1/report.json'
READY=B/'source-ready-v27.json'
MANIFEST=B/'manifest-restore-planning-v27.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def closure():
    path=QA/'family-preparation-thumbnail-v10/collector_v9_closure.py'
    if sha(path)!='3ef9b46881587023d642cee353ed84b4bf8de6eb9e264bfbaf1448980e1c0742':raise ValueError('approved selected alias implementation changed')
    spec=importlib.util.spec_from_file_location('v27_retained_alias',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def verify(packet):
    if set(packet['inputs'])!=set(packet['inputModes']):raise ValueError('complete bytes/modes required')
    module=closure();module.verify_links(packet['links'])
    for name,digest in packet['inputs'].items():module.retained_file(name,digest,packet['inputModes'][name],packet['inputs'],packet['inputModes'],packet['links'])
    module.verify_links(packet['links'])

def inventory():
    inputs={};modes={};links={}
    def merge(name,digest,mode):
        if name in inputs and (inputs[name]!=digest or modes[name]!=mode):raise ValueError('conflicting source declaration: '+name)
        inputs[name]=digest;modes[name]=mode
    def add(path,expected=None,mode=None):
        path=Path(path).absolute();digest=sha(path);actual=stat.S_IMODE(path.stat().st_mode)
        if expected is not None and digest!=expected or mode is not None and actual!=mode:raise ValueError('selected source changed: '+str(path))
        for alias in (path,*path.parents):
            if alias.is_symlink():
                target=os.readlink(alias)
                if str(alias) in links and links[str(alias)]!=target:raise ValueError('selected link conflict')
                links[str(alias)]=target
        merge(str(path.resolve(strict=True)),digest,actual);merge(str(path),digest,actual)
    for path,expected,key in ((BASE,BASE_SHA,'links'),(B11,B11_SHA,'symlinks')):
        if path.is_symlink() or sha(path)!=expected:raise ValueError('immutable predecessor changed')
        row=json.loads(path.read_text());packet={**row,'links':row[key]};verify(packet)
        for name,target in packet['links'].items():
            if name in links and links[name]!=target:raise ValueError('inherited link conflict')
            links[name]=target
        for name,digest in row['inputs'].items():merge(name,digest,row['inputModes'][name])
        add(path,expected)
    proof=json.loads(PROOF.read_text())
    if (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'],proof['original106CommandsExact'])!=('pass',424,435,37,True,True):raise ValueError('original unfiltered proof incomplete')
    if len(proof['checks'])!=112 or any(row['exitCode'] for row in proof['checks']):raise ValueError('required command completion absent')
    for name,row in proof['sources'].items():add(name,row['sha256'],row['mode'])
    for row in proof['checks']:add(row['log'],row['sha256'])
    add(PROOF)
    selected=json.loads((DESIGN/'intended-source-map.json').read_text())['files']
    for name,row in selected.items():add(B/name,row['new']['sha256'],row['old']['mode']);add(BASE.parent/name,row['old']['sha256'],row['old']['mode'])
    provenance=json.loads((B/'v26-source-provenance.json').read_text());changed=[]
    for name,row in provenance['copied'].items():
        add(BASE.parent/name,row['sha256'],row['mode'])
        current=B/name
        if stat.S_IMODE(current.stat().st_mode)!=row['mode']:raise ValueError('inherited mode changed')
        if sha(current)!=row['sha256']:changed.append(name)
    if sorted(changed)!=sorted(selected):raise ValueError('unapproved inherited product/test delta')
    for folder in (B,PROOF.parent,QA/'restore-planning-v27-focused-proof-v1',QA/'restore-planning-v27-focused-proof-v2',QA/'restore-planning-v27-focused-proof-v3',
        QA/'restore-planning-v27-source-epoch-v1',QA/'restore-planning-empty-plan-counterexample-v1',
        QA/'restore-planning-concurrency-v1',QA/'restore-planning-concurrency-v2',QA/'restore-batch-parser-v3',
        QA/'restore-planning-design-v1',QA/'restore-planning-design-v2',QA/'restore-planning-design-v3',DESIGN,
        QA/'thumbnail-v11-agent-restore-failure-v1',B11.parent/'attempt-baseline-1',Path(__file__).parent):
        for path in folder.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path not in (READY,MANIFEST):add(path)
    for path,digest in (
        (QA/'restore-planning-root-design-review-v1.json','45592d7462410b58502e947db9488a2a5b4dd6c1a6e5c39f5cfecfb386b5fae4'),
        (QA/'restore-planning-design-v3/source-handoff.json','81e8791043090b1e854f4d6452d8d0deef7cbc1402dacfbaddcc462fbc334fcb')):add(path,digest)
    # No mutable top-level status documents are selected by recursive QA walks.
    base=json.loads(BASE.read_text());fields={k:v for k,v in base.items() if k not in ('inputs','inputModes','links','proof','proofSHA256','baseManifest','baseManifestSHA256','sourceReady','sourceReadySHA256','changedInheritedSources')}
    fields.update(version='restore-planning-v27-source',baseManifest=str(BASE),baseManifestSHA256=BASE_SHA,
        retainedFailedNativeB11Manifest=str(B11),retainedFailedNativeB11ManifestSHA256=B11_SHA,
        changedInheritedSources=sorted(changed),proof=str(PROOF),proofSHA256=sha(PROOF),
        sourcePlan=str(DESIGN/'source-handoff.json'),sourcePlanSHA256=sha(DESIGN/'source-handoff.json'),
        restorePlanningSourceImplemented=True,maxDestinationWorkers=3,maxDestinationMembers=64,
        original38BaselineAccepted=False,original34FaultsAccepted=False,nativePerformanceAccepted=False,nativeAccepted=False,
        mainChanged=False,requestDeadlineSeconds=2,thumbnailDeadlineSeconds=1,housekeepDeadlineSeconds=.6,
        inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
    verify(fields);return fields

def write(path,row):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    for flag in ('collect','freeze','verify'):group.add_argument('--'+flag,action='store_true')
    args=parser.parse_args()
    if args.verify:packet=json.loads(MANIFEST.read_text());verify(packet)
    elif args.collect:packet=inventory();write(READY,packet)
    else:
        ready=json.loads(READY.read_text());verify(ready);packet=inventory()
        if ready!=packet:raise ValueError('reviewed source-ready changed')
        packet={**packet,'sourceReady':str(READY),'sourceReadySHA256':sha(READY)};write(MANIFEST,packet)
    print(json.dumps({'result':'pass','inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['links']),'manifest':str(MANIFEST),'nativeAccepted':False}))
if __name__=='__main__':main()
