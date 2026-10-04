import hashlib,json,pathlib,shutil,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
r=pathlib.Path(__file__).resolve().parents[1]
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
tests='qa/tests-1791156450215833695/report.json';model='qa/model-1791156437536198594/report.json';mutants='qa/mutations-1791156450199634567/report.json'
t=json.loads((r/tests).read_bytes());m=json.loads((r/model).read_bytes());c=json.loads((r/mutants).read_bytes())
assert t['passed'] and t['assertions']==462 and m['passed'] and c['passed']
for p,d in t['sourceSHA256'].items():assert row(r/p)['sha256']==d,p
assert row(r/'spec/admission.qnt')['sha256']==m['specSHA256']
for x in c['controls']:
 if x['version']=='original':assert row(r/'adapter/authority.py')['sha256']==x['sourceSHA256']
assert row(r/'adapter/archive_base.py')==row(r.parent/'elm-paged-history-storage-v647/adapter/archive.py')
parents={}
for name in ['elm-paged-history-storage-v647','elm-paged-ledger-integration-review-v661']:
 p=r.parent/name/'component-manifest.json';parents[name]=row(p)
value={'pythonVersion':sys.version,'pythonExecutable':{'path':sys.executable,'resolved':str(pathlib.Path(sys.executable).resolve()),**row(pathlib.Path(sys.executable))},'quintVersion':subprocess.run(['quint','--version'],capture_output=True,text=True,check=True).stdout.strip(),'quintExecutable':{'path':shutil.which('quint'),'resolved':str(pathlib.Path(shutil.which('quint')).resolve()),**row(pathlib.Path(shutil.which('quint')))},'scope':'local executable/source metadata; transitive Python/Quint dependency inventories not fully pinned'}
(r/'qa/tool-metadata.json').write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
manifest=r/'component-manifest.json';assert not manifest.exists();assert not any(p.is_symlink() for p in r.rglob('*'))
files={str(p.relative_to(r)):row(p) for p in sorted(r.rglob('*')) if p.is_file()}
value={'schema':1,'component':r.name,'parents':parents,'testsReport':tests,'modelReport':model,'mutationReport':mutants,'newFSAssertions':462,'sourceClosure':'final adapters/spec/test-runner SHA256 checked against reports; exact647 base retained','scope':'atomic admission plus independent request/generation and conservative completion reservation only','nativeAcceptance':False,'CIntegrated':False,'completionImplemented':False,'migrationImplemented':False,'S15Accepted':False,'powerLossQualified':False,'files':files}
manifest.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
for name,v in files.items():assert row(r/name)==v,name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'newFSAssertions':462}))
