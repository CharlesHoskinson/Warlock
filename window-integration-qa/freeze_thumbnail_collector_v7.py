"""Root-only complete collector evidence freeze; no GUI or main changes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

QA=Path('/home/hoskinson/window-integration-qa')
B=QA/'family-preparation-thumbnail-v7'
sys.path.insert(0,str(QA));sys.path.insert(0,str(B))
from qa_launch import require_qa_scope
require_qa_scope()
import native_integration as candidate
import module_binding
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--review',type=Path,required=True);args=parser.parse_args()
REVIEW=args.review.absolute()
assert REVIEW.parent.parent==QA and REVIEW.parent.name.startswith('thumbnail-v7-agent-review-')
review=json.loads(REVIEW.read_text())
if review.get('result')!='pass':raise ValueError('independent corrected collector review must pass')
PROOF=QA/'thumbnail-v7-full-proof-v3/report.json'
proof=json.loads(PROOF.read_text())
if (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'])!=('pass',120,109,10,True):raise ValueError('required corrected full collector proof absent')
if len(proof['checks'])!=31 or any(c['exitCode'] for c in proof['checks']):raise ValueError('full corrected commands incomplete')
for path,v in proof['sources'].items():
    if sha(path)!=v['sha256'] or stat.S_IMODE(Path(path).stat().st_mode)!=v['mode']:raise ValueError('full proof source changed: '+path)
if sha(module_binding.MANIFEST)!=module_binding.MANIFEST_SHA256:raise ValueError('selected V23 freeze changed')
original_save=candidate.save
attachments=[QA/'family-preparation-v23-root-review-v1',QA/'thumbnail-v7-full-proof-v1',QA/'thumbnail-v7-full-proof-v2',QA/'thumbnail-v7-full-proof-v3',QA/'thumbnail-v7-initial-binding-cpu-failure-v1',QA/'thumbnail-v7-callback-formal-before-runtime-v1',QA/'thumbnail-v7-callback-formal-before-runtime-v2',QA/'thumbnail-v7-callback-source-epoch-v1',QA/'thumbnail-v7-agent-review-v1',REVIEW.parent]
files=[Path(__file__),QA/'prepare_thumbnail_collector_v7.py',QA/'thumbnail-v7-root-source-conservation-v1.json',QA/'thumbnail-v7-pairing-assembly-failure-v1.json',QA/'thumbnail-v7-crash-handoff-source-audit-v1.json',QA/'qa_run.py',QA/'qa_launch.py',Path('/home/hoskinson/Documents/crash-noise/HANDOFF-codex-window-qa.md')]
def complete_save(path,row):
    if Path(path)!=B/'frozen-inputs.json':raise ValueError('only fresh collector manifest may be written')
    row={**row,'inputs':dict(row['inputs']),'inputModes':dict(row['inputModes']),'symlinks':dict(row['symlinks'])}
    def add(path):
        p=Path(path).absolute();value=sha(p);mode=stat.S_IMODE(p.stat().st_mode)
        for alias in (p,p.resolve()):
            name=str(alias)
            if name in row['inputs'] and row['inputs'][name]!=value or name in row['inputModes'] and row['inputModes'][name]!=mode:raise ValueError('conflicting complete evidence source')
            row['inputs'][name]=value;row['inputModes'][name]=mode
        for alias in (p,*p.parents):
            if alias.is_symlink():
                name=str(alias);target=os.readlink(alias)
                if name in row['symlinks'] and row['symlinks'][name]!=target:raise ValueError('conflicting evidence alias')
                row['symlinks'][name]=target
    for folder in attachments:
        if not folder.is_dir():raise ValueError('required immutable evidence folder absent: '+str(folder))
        for p in sorted(folder.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:add(p)
    for witness_path in files:add(witness_path)
    if set(row['inputs'])!=set(row['inputModes']):raise ValueError('complete frozen input modes required')
    row.update(collectorProof=str(PROOF),collectorProofSHA256=sha(PROOF),independentReview=str(REVIEW),independentReviewSHA256=sha(REVIEW),selectedServiceManifest=str(module_binding.MANIFEST),selectedServiceManifestSHA256=module_binding.MANIFEST_SHA256,original38BaselineAccepted=False,original34FaultsAccepted=False,profileHooks=False,mainGUIWrites=False)
    for name,value in row['inputs'].items():
        if sha(name)!=value or stat.S_IMODE(Path(name).stat().st_mode)!=row['inputModes'][name]:raise ValueError('complete freeze source moved: '+name)
    destination=Path(path)
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    parent=os.open(destination.parent,os.O_DIRECTORY|os.O_RDONLY|os.O_CLOEXEC)
    try:os.fsync(parent)
    finally:os.close(parent)
candidate.save=complete_save
packet=candidate.freeze()
candidate.save=original_save
print(json.dumps({'result':'pass','manifest':str(B/'frozen-inputs.json'),'manifestSHA256':sha(B/'frozen-inputs.json'),'inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['symlinks']),'nativeAccepted':False,'mainChanged':False}))
