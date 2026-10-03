"""Independent complete actual gate replay; preserve iteration-order failure."""
from pathlib import Path
import hashlib,json,os,re,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope()
QA=Path('/home/hoskinson/window-integration-qa');OUT=Path(__file__).resolve().parent
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=QA/'family-preparation-v24-full-proof-v1/report.json';raw=json.loads(old.read_text())
prior=json.loads((QA/'family-preparation-v23-full-proof-v1/report.json').read_text())
assert raw['result']=='fail' and len(raw['checks'])==100
assert [c['command']for c in raw['checks'][:97]]==[c['command']for c in prior['checks']]
assert raw['checks'][97]['command']==['quint','typecheck','renderer_job_role_test.qnt']
assert raw['checks'][98]['command']==['quint','test','renderer_job_role_test.qnt']
assert raw['checks'][99]['command']==['quint','run','renderer_job_role.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=20261002','--verbosity=0']
named=0;models=0
for c in raw['checks']:
    assert c['exitCode']==0 and sha(c['log'])==c['sha256']
    if c['command'][0]=='quint'and c['command'][1]=='test':
        found=re.search(r'(\d+) passing',Path(c['log']).read_text());assert found;named+=int(found[1])
    if c['command'][0]=='quint'and c['command'][1]=='run':models+=1
python_log=Path(raw['checks'][0]['log']).read_text();found=re.search(r'Ran (\d+) tests',python_log)
assert found and python_log.rstrip().endswith('OK');python_count=int(found[1]);assert (python_count,named,models)==(377,332,33)
current={str(p)for p in B.iterdir()if p.is_file()and p.suffix in ('.py','.qnt','.md','.c')}
assert current==set(raw['sources'])
for p,w in raw['sources'].items():assert sha(p)==w['sha256']and stat.S_IMODE(Path(p).stat().st_mode)==w['mode']
inherited=json.loads((B/'v23-source-inheritance-before-v24.json').read_text());changed=[];exact=[]
for n,w in inherited['sources'].items():
    assert sha(w['base'])==w['sha256']and stat.S_IMODE(Path(w['base']).stat().st_mode)==w['mode']
    assert stat.S_IMODE((B/n).stat().st_mode)==w['mode']
    (exact if sha(B/n)==w['sha256']else changed).append(n)
assert len(inherited['sources'])==141 and changed==raw['changedInheritedSources']
assert sorted(changed)==['batch_preview.py','native_runtime.py']and len(exact)==139
plan=json.loads((B/'RENDERER_ROLE_SOURCE_PLAN-v5.json').read_text())
for n,w in plan['sources'].items():assert sha(B/n)==w['proposedSHA256']and sha(B.with_name('service-family-preparation-v23')/n)==w['beforeSHA256']
initial_checker=QA/'family-preparation-v24-full-proof-v1/prove.py';checker=initial_checker.read_text()
old_condition="changed==['batch_preview.py','native_runtime.py']";assert checker.count(old_condition)==1
corrected=checker.replace(old_condition,"sorted(changed)==['batch_preview.py','native_runtime.py']")
for name,data in [('corrected_checker.py',corrected.encode())]:
    with os.fdopen(os.open(OUT/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as f:f.write(data)
row={**raw,'result':'pass','changedInheritedSources':sorted(changed),'inheritedExact':exact,
    'sourceUnchangedDuringProof':True,'independentReplayScope':scope,'retainedInitialCheckerFailure':str(old),
    'retainedInitialCheckerFailureSHA256':sha(old),'checkerCause':'Exact allowed filenames were compared in inherited iteration order; only sorted order correction',
    'initialCheckerSHA256':sha(initial_checker),'correctedCheckerSHA256':sha(OUT/'corrected_checker.py'),
    'allActualOriginalAndNewCommandsReplayed':True,'optionalFullRerunPerformed':False,'nativeAccepted':False}
with os.fdopen(os.open(OUT/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps(dict(result='pass',commands=100,python=python_count,named=named,models=models,sourceConservation139=True,retainedCheckerFailure=True,nativeAccepted=False)))
