import hashlib,json,os,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[];result={'passed':False,'nativeAcceptance':False,'checks':checks}
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
try:
 selected=ROOT/'qa/characterization-1791125837259617921/report.json';r=json.loads(selected.read_text());check('actual producer31 checks/13 samples passed',r['passed'] is True and len(r['checks'])==31 and r['samples']==13 and r['nativeAcceptance'] is False)
 check('actual tested runner unchanged',sha(ROOT/'qa/test.py')==r['testSourceSHA256'])
 for rel,digest in r['artifacts'].items():check('retained tested artifact '+rel,sha(selected.parent/rel)==digest)
 for name,digest in r['compilerDependencies'].items():check('compiler owning dependency '+name,sha(name)==digest)
 for name,digest in r['linkedLibraries'].items():check('actual resolved library '+name,sha(name)==digest)
 result.update(passed=True,sourceSHA256=sha(Path(__file__)))
except Exception as error:result['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n')
if result['passed']:
 files={};links={}
 for p in sorted(ROOT.rglob('*')):
  if p.name=='component-manifest.json':continue
  if p.is_symlink():links[str(p.relative_to(ROOT))]=os.readlink(p)
  elif p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o777}
 m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'dispatchAcceptance':False,'modelAcceptance':False,'producerSchemaConsistencyPassed':False,'files':files,'symlinks':links,'scope':r['scope'],'report':{'path':str(selected.relative_to(ROOT)),'sha256':sha(selected)},'freezeReport':{'path':str((OUT/'report.json').relative_to(ROOT)),'sha256':sha(OUT/'report.json')},'ambiguities':r['ambiguities'],'limitations':r['limitations']}
 with (ROOT/'component-manifest.json').open('x') as f:f.write(json.dumps(m,indent=2)+'\n')
print(OUT/'report.json');raise SystemExit(not result['passed'])
