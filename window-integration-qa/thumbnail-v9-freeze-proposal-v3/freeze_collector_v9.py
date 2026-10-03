"""Root-owned reviewed complete source freeze. No GUI or main writes."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

QA=Path('/home/hoskinson/window-integration-qa')
B=QA/'family-preparation-thumbnail-v9'
D=QA/'thumbnail-v9-renderer-binding-design-v1'
V24=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
sys.path.insert(0,str(QA));sys.path.insert(0,str(B))
from qa_launch import require_qa_scope
require_qa_scope()
import native_integration as candidate
import module_binding as binding
import collector_v9_closure

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def regular(path,expected):
    path=Path(path).absolute();info=path.lstat()
    if not stat.S_ISREG(info.st_mode)or path.is_symlink()or not re.fullmatch('[0-9a-f]{64}',expected)or sha(path)!=expected:raise ValueError('exact regular reviewed packet required: '+str(path))
    return json.loads(path.read_text())

parser=argparse.ArgumentParser()
parser.add_argument('--review',type=Path,required=True)
parser.add_argument('--review-sha256',required=True)
parser.add_argument('--ready',type=Path,required=True)
parser.add_argument('--ready-sha256',required=True)
parser.add_argument('--dry-run',action='store_true',help='Verify whole proposed union without creating any collector manifest')
args=parser.parse_args()
REVIEW=args.review.absolute();READY=args.ready.absolute()
if not REVIEW.is_relative_to(QA)or not READY.is_relative_to(QA)or REVIEW==B/'frozen-inputs.json':raise ValueError('external owned QA review and source-ready required')
review=regular(REVIEW,args.review_sha256)
ready=regular(READY,args.ready_sha256)
if review.get('result')!='pass'or ready.get('sourceReady')is not True or ready.get('nativeAccepted')is not False:raise ValueError('source review/source-ready only; acceptance not implied')
PROOF=Path(ready['fullProof']['path']).absolute()
proof=regular(PROOF,ready['fullProof']['sha256'])
if not PROOF.parent.parent==QA or not PROOF.parent.name.startswith('thumbnail-v9-full-proof-'):raise ValueError('actual original full proof path required')
if (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'])!=('pass',155,180,13,True):raise ValueError('full original unfiltered V9 proof required')
if len(proof['checks'])!=40 or any(row['exitCode']!=0 for row in proof['checks']):raise ValueError('all original plus new formal commands must complete normally')
for name,value in proof['sources'].items():
    p=Path(name)
    if sha(p)!=value['sha256']or stat.S_IMODE(p.stat().st_mode)!=value['mode']:raise ValueError('full proof source changed: '+name)
for name,value in ready['inputs'].items():
    p=Path(name)
    if sha(p)!=value or stat.S_IMODE(p.stat().st_mode)!=ready['inputModes'][name]:raise ValueError('exact reviewed source-ready bytes/modes changed: '+name)
for name,value in ready['symlinks'].items():
    if not Path(name).is_symlink()or os.readlink(name)!=value:raise ValueError('exact reviewed link changed: '+name)
DESIGN_HANDOFF=D/'source-handoff-v1.json'
design=regular(DESIGN_HANDOFF,'3d462b4baae512d7fdc21ca00b01249c9e4c3242b9b6f293229db4ed9bce2641')
INTENDED_REVIEW=QA/'thumbnail-v9-root-intended-source-review-v1.json'
regular(INTENDED_REVIEW,'2882aa270919e5aae0a1d8623fd64a1f5556661c15586be72289728b58492225')
for name,value in design['inputs'].items():
    p=Path(name)
    if p.is_symlink()or sha(p)!=value or stat.S_IMODE(p.stat().st_mode)!=design['inputModes'][name]:raise ValueError('stable approved design changed: '+name)
source_map=json.loads((D/'intended-source-map-v2.json').read_text())
alias=ready['aliasCorrection']
ALIAS_REVIEW=QA/'thumbnail-v9-closure-alias-root-source-review-v1.json'
CRASH_REVIEW=QA/'thumbnail-v9-root-crash-and-kernel-source-review-v1.json'
if alias['reviewPath']!=str(ALIAS_REVIEW)or alias['reviewSHA256']!='0910502428600fb7920df33bae2053d54801df10fc63387828d2cef4431f7a3e'or alias['closureSHA256']!='3ef9b46881587023d642cee353ed84b4bf8de6eb9e264bfbaf1448980e1c0742':raise ValueError('exact independently approved alias correction required')
regular(ALIAS_REVIEW,alias['reviewSHA256'])
regular(CRASH_REVIEW,'22068652ebb4af9f11c301eb7077e5181b0bf58aeeae3a07221e950c36ef7450')
for name,value in source_map['sources'].items():
    expected=alias['closureSHA256']if name=='collector_v9_closure.py'else value['intendedSHA256']
    if sha(B/name)!=expected:raise ValueError('reviewed seven sources plus exact alias correction changed: '+name)
if binding.MANIFEST!=V24/'manifest-family-preparation-v24.json'or binding.MANIFEST_SHA256!='b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c':raise ValueError('exact selected reviewed V24 manifest required')
regular(binding.MANIFEST,binding.MANIFEST_SHA256)

original_save=candidate.save
class PreviewDone(Exception):pass
preview_packet=None
def complete_save(path,row):
    if Path(path)!=B/'frozen-inputs.json':raise ValueError('only fresh collector source manifest may be written')
    row={**row,'inputs':dict(row['inputs']),'inputModes':dict(row['inputModes']),'symlinks':dict(row['symlinks'])}
    def add_file(p):
        p=Path(p).absolute();info=p.lstat();name=str(p)
        if not stat.S_ISREG(info.st_mode)and not stat.S_ISLNK(info.st_mode):raise ValueError('recorded regular/alias complete evidence file required: '+name)
        value=sha(p);mode=stat.S_IMODE(p.stat().st_mode)
        collector_v9_closure.retained_file(name,value,mode,row['inputs'],row['inputModes'],row['symlinks'])
        if name in row['inputs']and row['inputs'][name]!=value or name in row['inputModes']and row['inputModes'][name]!=mode:raise ValueError('conflicting complete evidence source: '+name)
        row['inputs'][name]=value;row['inputModes'][name]=mode
    def add_tree(folder):
        if not folder.is_dir()or folder.is_symlink():raise ValueError('complete selected evidence folder required')
        for p in sorted(folder.rglob('*')):
            if '__pycache__'in p.parts:continue
            if p.is_symlink():
                name=str(p);target=os.readlink(p)
                if name in row['symlinks']and row['symlinks'][name]!=target:raise ValueError('conflicting evidence link')
                row['symlinks'][name]=target
            elif p.is_file():add_file(p)
            elif not p.is_dir():raise ValueError('unknown evidence artifact type')
    # Explicit union repeats the selected source guard. It must include V24,
    # frozen V7, the actual failed V7 attempt, V8 component and its evidence.
    collector_v9_closure.retain(row['inputs'],row['inputModes'],row['symlinks'])
    # Current external design/intents/handoff/reviews/proofs do not appear in
    # predecessor manifests. Include them explicitly with every declared mode.
    for folder in (D,PROOF.parent,Path(__file__).parent):add_tree(folder)
    for p in (REVIEW,READY,INTENDED_REVIEW,DESIGN_HANDOFF,ALIAS_REVIEW,CRASH_REVIEW,QA/'qa_run.py',QA/'qa_launch.py'):
        add_file(p)
    for name,value in ready['inputs'].items():
        add_file(name)
        if row['inputs'][name]!=value or row['inputModes'][name]!=ready['inputModes'][name]:raise ValueError('source-ready changed during freeze')
    if set(row['inputs'])!=set(row['inputModes']):raise ValueError('all frozen byte inputs require exact modes')
    row.update(collectorProof=str(PROOF),collectorProofSHA256=sha(PROOF),rootSourceReview=str(REVIEW),rootSourceReviewSHA256=sha(REVIEW),sourceReady=str(READY),sourceReadySHA256=sha(READY),intendedSourceReview=str(INTENDED_REVIEW),intendedSourceReviewSHA256=sha(INTENDED_REVIEW),selectedServiceManifest=str(binding.MANIFEST),selectedServiceManifestSHA256=binding.MANIFEST_SHA256,original38BaselineAccepted=False,original34FaultsAccepted=False,rendererNativeCoexistenceAccepted=False,profileHooks=False,mainGUIWrites=False)
    collector_v9_closure.verify_links(row['symlinks'])
    for name,value in row['inputs'].items():
        p=Path(name)
        collector_v9_closure.retained_file(name,value,row['inputModes'][name],row['inputs'],row['inputModes'],row['symlinks'])
    collector_v9_closure.verify_links(row['symlinks'])
    for name,value in row['symlinks'].items():
        if not Path(name).is_symlink()or os.readlink(name)!=value:raise ValueError('complete freeze link changed: '+name)
    if args.dry_run:
        global preview_packet
        if (B/'frozen-inputs.json').exists():raise ValueError('preview requires still-unfrozen fresh collector')
        preview_packet=row
        raise PreviewDone()
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    parent=os.open(B,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
    try:os.fsync(parent)
    finally:os.close(parent)

candidate.save=complete_save
try:
    try:candidate.freeze()
    except PreviewDone:
        if not args.dry_run or preview_packet is None:raise
finally:candidate.save=original_save
if args.dry_run:
    packet=preview_packet
    print(json.dumps({'result':'source-closure-preview-pass','inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['symlinks']),'manifestCreated':False,'nativeAccepted':False,'nativeLaunch':False}))
else:
    # The wrapper extends a copy. Report and independently verify the actual
    # persisted union; never derive final counts from candidate.freeze's return.
    path=B/'frozen-inputs.json';before=sha(path)
    packet=candidate.verify()
    persisted=regular(path,before)
    if packet!=persisted or sha(path)!=before:raise ValueError('persisted complete union changed during final verification')
    print(json.dumps({'result':'source-freeze-pass','manifest':str(path),'manifestSHA256':before,'inputs':len(persisted['inputs']),'modes':len(persisted['inputModes']),'links':len(persisted['symlinks']),'nativeAccepted':False,'nativeLaunch':False}))
