"""Collect independently verified complete source handoff; never freeze/launch."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

Q=Path('/home/hoskinson/window-integration-qa')
B=Q/'family-preparation-thumbnail-v9'
V8=Q/'family-preparation-thumbnail-v8'
D=Q/'thumbnail-v9-renderer-binding-design-v1'
A=Q/'thumbnail-v9-closure-alias-design-v1'
OUT=Path(__file__).parent
sys.path.insert(0,str(Q));sys.path.insert(0,str(B))
from qa_launch import require_qa_scope
scope=require_qa_scope()
import collector_v9_closure as closure
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
PROOF=Q/'thumbnail-v9-full-proof-v2/report.json'
proof=json.loads(PROOF.read_text())
if (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'])!=('pass',155,180,13,True):raise ValueError('exact full unfiltered proof required')
if len(proof['checks'])!=40 or any(row['exitCode']for row in proof['checks']):raise ValueError('complete actual command proof required')
for name,value in proof['sources'].items():
    if sha(name)!=value['sha256']or stat.S_IMODE(Path(name).stat().st_mode)!=value['mode']:raise ValueError('full proof source changed: '+name)
for check in proof['checks']:
    if sha(check['log'])!=check['sha256']:raise ValueError('actual completed proof log changed')

source_map=json.loads((D/'intended-source-map-v2.json').read_text())
for name,value in source_map['sources'].items():
    expected='3ef9b46881587023d642cee353ed84b4bf8de6eb9e264bfbaf1448980e1c0742'if name=='collector_v9_closure.py'else value['intendedSHA256']
    if sha(B/name)!=expected:raise ValueError('approved intended source changed: '+name)
old=json.loads((Q/'thumbnail-v8-terminal-source-handoff-v1.json').read_text())
changed=[]
for name,value in old['inputs'].items():
    p=Path(name);new=B/p.relative_to(V8)
    if sha(p)!=value or stat.S_IMODE(p.stat().st_mode)!=old['inputModes'][name]:raise ValueError('immutable V8 source changed')
    if sha(new)!=value:changed.append(str(p.relative_to(V8)))
    if stat.S_IMODE(new.stat().st_mode)!=old['inputModes'][name]:raise ValueError('inherited original mode changed')
if sorted(changed)!=sorted(n for n,r in source_map['sources'].items()if r['oldSHA256']is not None):raise ValueError('undeclared original source delta')
def function(path,name):
    s=Path(path).read_text();node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)and n.name==name)
    return ast.get_source_segment(s,node)
checks={name:function(B/'module_binding.py',name)==function(V8/'module_binding.py',name)for name in ('batch_relations','batch_identity','archive_final','validate_evidence','validate_ledger','data_probe','bind_recovery','validate_recovery_evidence')}
checks['baselineWholeMain']=function(B/'native_integration.py','main')==function(V8/'native_integration.py','main')
checks['faultWholeMainInverse']=function(B/'native_faults.py','main')==function(V8/'native_faults.py','main').replace('service-family-preparation-v23','service-family-preparation-v24').replace('actual V23 baseline binding','actual V24 baseline binding')
for name in ('test_actual_binding.py','test_batch_binding.py'):
    def assertions(path):return[ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(Path(path).read_text()))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr.startswith('assert')]
    checks['allOriginalOutcomeAssertions.'+name]=assertions(B/name)==assertions(V8/name)
if not all(checks.values()):raise ValueError('complete original source/oracle conservation failed')

inputs={};modes={};links={}
closure.retain(inputs,modes,links)
def add_file(p):
    p=Path(p).absolute();name=str(p);value=sha(p);mode=stat.S_IMODE(p.stat().st_mode)
    if name in inputs and inputs[name]!=value or name in modes and modes[name]!=mode:raise ValueError('complete source evidence alias conflict')
    inputs[name]=value;modes[name]=mode
def add_tree(folder):
    for p in sorted(folder.rglob('*')):
        if '__pycache__'in p.parts:continue
        if p.is_symlink():
            name=str(p);target=os.readlink(p)
            if name in links and links[name]!=target:raise ValueError('complete evidence link conflict')
            links[name]=target
        elif p.is_file():add_file(p)
        elif not p.is_dir():raise ValueError('unknown evidence object')

folders=[B,D,A,OUT,Q/'thumbnail-v9-initial-positive-cpu-v1',Q/'thumbnail-v9-focused-kernel-v1',Q/'thumbnail-v9-fixture-syntax-epoch-v1',Q/'thumbnail-v9-full-proof-v1',Q/'thumbnail-v9-full-proof-v2',Q/'thumbnail-v9-failed-source-epoch-v1',Q/'thumbnail-v9-source-conservation-v1',Q/'thumbnail-v9-focused-alias-kernel-v1',Q/'thumbnail-v9-freeze-proposal-v1',Q/'thumbnail-v9-freeze-proposal-v2',Q/'thumbnail-v9-freeze-proposal-v3']
for folder in folders:add_tree(folder)
pins={Q/'thumbnail-v9-root-intended-source-review-v1.json':'2882aa270919e5aae0a1d8623fd64a1f5556661c15586be72289728b58492225',Q/'thumbnail-v9-closure-alias-root-source-review-v1.json':'0910502428600fb7920df33bae2053d54801df10fc63387828d2cef4431f7a3e',Q/'thumbnail-v9-root-crash-and-kernel-source-review-v1.json':'22068652ebb4af9f11c301eb7077e5181b0bf58aeeae3a07221e950c36ef7450'}
for p,digest in pins.items():
    if sha(p)!=digest:raise ValueError('exact independent root review changed')
    add_file(p)
for p in (Q/'qa_run.py',Q/'qa_launch.py'):add_file(p)
if set(inputs)!=set(modes):raise ValueError('every full closure byte requires its mode')
closure.verify_links(links)
for name,value in inputs.items():closure.retained_file(name,value,modes[name],inputs,modes,links)
closure.verify_links(links)
row={'result':'source-ready-pass','sourceReady':True,'nativeAccepted':False,'nativeLaunch':False,'mainChanged':False,'normalHostExitAccepted':False,'rendererNativeCoexistenceAccepted':False,'original38BaselineAccepted':False,'original34FaultsAccepted':False,'fullWindowsParityAccepted':False,'stage':str(B),'selectedV24ManifestSHA256':'b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c','fullProof':{'path':str(PROOF),'sha256':sha(PROOF),'pythonTests':155,'named':180,'models':13,'samples':2000,'steps':100,'commands':40},'aliasCorrection':{'reviewPath':str(Q/'thumbnail-v9-closure-alias-root-source-review-v1.json'),'reviewSHA256':pins[Q/'thumbnail-v9-closure-alias-root-source-review-v1.json'],'closureSHA256':sha(B/'collector_v9_closure.py')},'preservedFailure':{'path':str(Q/'thumbnail-v9-full-proof-v1/report.json'),'sha256':sha(Q/'thumbnail-v9-full-proof-v1/report.json'),'actualRan':144,'passed':143},'inheritedV8':{'inputs':439,'exact':439-len(changed),'declaredDeltas':changed},'originalConservation':checks,'freezerProposal':{'path':str(Q/'thumbnail-v9-freeze-proposal-v3/freeze_collector_v9.py'),'sha256':sha(Q/'thumbnail-v9-freeze-proposal-v3/freeze_collector_v9.py')},'completeEvidenceFolders':[str(f)for f in folders],'rootReviewPins':{str(p):h for p,h in pins.items()},'inputs':inputs,'inputModes':modes,'symlinks':links,'scope':scope,'pending':'Root independent source/log review, complete-union dry review/freeze/preflight, sole original38 actual baseline; faults34 conditional on accepted baseline.'}
path=OUT/'source-ready.json'
with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'result':row['result'],'ready':str(path),'sha256':sha(path),'inputs':len(inputs),'modes':len(modes),'links':len(links),'freezerSHA256':row['freezerProposal']['sha256'],'nativeLaunch':False}))
