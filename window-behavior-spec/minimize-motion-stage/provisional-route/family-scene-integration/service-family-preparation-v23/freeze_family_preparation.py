"""Freeze reviewed family thumbnail service; read-only source inventory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

B=Path(__file__).resolve().parent
BASE=B.parent/'service-readonly-ipc-v20/manifest-readonly-ipc-v20.json'
BASE_SHA='d3d836eda0e2a25681df4ca80740ca94f8d2084ea1c48f8834293b740122c068'
QA=Path('/home/hoskinson/window-integration-qa')
PROOF=QA/'family-preparation-v22-full-proof-v2/report.json'
MANIFEST=B/'manifest-family-preparation-v22.json'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inventory():
    if sha(BASE)!=BASE_SHA:raise ValueError('frozen V20 base changed')
    base=json.loads(BASE.read_text());inputs={};modes={};links={}
    def add(path,expected=None,mode=None):
        p=Path(path);p=p if p.is_absolute() else Path('/home/hoskinson')/p
        digest=sha(p);actual=stat.S_IMODE(p.stat().st_mode)
        if (expected is not None and digest!=expected) or (mode is not None and actual!=mode):raise ValueError('declared source changed: '+str(p))
        for alias in (p,p.resolve()):
            name=str(alias)
            if name in inputs and (inputs[name]!=digest or modes[name]!=actual):raise ValueError('conflicting source alias')
            inputs[name]=digest;modes[name]=actual
        for alias in (p,*p.parents):
            if alias.is_symlink():
                target=os.readlink(alias)
                if str(alias) in links and links[str(alias)]!=target:raise ValueError('conflicting link alias')
                links[str(alias)]=target
    if set(base['inputs'])!=set(base['inputModes']):raise ValueError('base modes incomplete')
    for p,h in base['inputs'].items():add(p,h,base['inputModes'][p])
    for p,target in base['links'].items():
        if not Path(p).is_symlink() or os.readlink(p)!=target:raise ValueError('base link changed')
        links[p]=target
    add(BASE,BASE_SHA)
    proof=json.loads(PROOF.read_text())
    if (proof.get('result'),proof.get('pythonTests'),proof.get('quintNamedScenarios'),proof.get('quintModels'),proof.get('sourceUnchangedDuringProof'))!=('pass',350,280,31,True):raise ValueError('required full final proof absent')
    for p,row in proof['sources'].items():add(p,row['sha256'],row['mode'])
    for check in proof['checks']:add(check['log'],check['sha256'])
    add(PROOF)
    provenance=json.loads((B/'base-v20-source-provenance-v1.json').read_text());changed=[]
    for name,h in provenance['copied'].items():
        original=BASE.parent/name;add(original,h)
        if stat.S_IMODE((B/name).stat().st_mode)!=stat.S_IMODE(original.stat().st_mode):raise ValueError('inherited mode changed')
        if sha(B/name)!=h:changed.append(name)
    if sorted(changed)!=['native_desktop.py','scene_controller.py'] or len(provenance['copied'])!=120:raise ValueError('inherited scope differs')
    for path in B.iterdir():
        if path.is_file() and path!=MANIFEST:add(path)
    for path in (QA/'batch-preview-final-cpu-v1.json',QA/'batch-preview-final-cpu-v1.log',
                 QA/'batch-preview-lock-counterexample-v1.json',QA/'batch-preview-capture-order-counterexample-v1.json'):
        # Lock counterexample is owned by this candidate; all others external.
        if path.name=='batch-preview-lock-counterexample-v1.json':path=B/path.name
        add(path)
    for folder in ('batch-preview-initial-lock-review-v1','batch-preview-capture-order-epoch-v1','family-preparation-v22-full-proof-v1'):
        for path in (QA/folder).rglob('*'):
            if path.is_file():add(path)
    # The existing native collector retains the selected Magick coder/config
    # closure too. Pin the selected executable and its direct loader inputs here.
    add('/usr/bin/magick')
    result=subprocess.run(['/usr/bin/ldd','/usr/bin/magick'],capture_output=True,text=True,timeout=5)
    if result.returncode:raise ValueError('selected thumbnail executable loader closure failed')
    for line in result.stdout.splitlines():
        for word in line.split():
            if word.startswith('/') and Path(word).is_file():add(word)
    if any(sha(p)!=h or stat.S_IMODE(Path(p).stat().st_mode)!=modes[p] for p,h in inputs.items()):raise ValueError('source moved during inventory')
    fields={k:base[k] for k in ('pairedManifest','pairedManifestSHA256','pairedNativeSHA256','producerManifest','producerManifestSHA256','producer','producerSHA256')}
    fields.update(baseManifest=str(BASE),baseManifestSHA256=BASE_SHA,changedInheritedSources=sorted(changed),originalDeadlineSeconds=2,
        nativeAccepted=False,mainChanged=False,productionDeployed=False,batchTargetAPISelected=False,actorSemanticCancellationPaired=False,readonlyLongevityPaired=False,
        proof=str(PROOF),proofSHA256=sha(PROOF),inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
    return fields

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if MANIFEST.exists():raise SystemExit('immutable manifest already exists')
    packet=inventory()
    if args.freeze:
        with MANIFEST.open('x') as output:json.dump(packet,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
    print(json.dumps({'result':'pass','inputs':len(packet['inputs']),'links':len(packet['links']),'frozen':args.freeze,'nativeAccepted':False}))

if __name__=='__main__':main()
