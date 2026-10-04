"""Verify reviewed native runner preflight and publish immutable source hold; no GUI."""
import hashlib,json,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir();checks=[]
report={'passed':False,'nativeAcceptance':False,'scope':'Native runner source, AST preservation and actual owning tuple preflight closure only; no GUI or operation acceptance','checks':checks}
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
try:
 selected=ROOT/'qa/preflight-1791107198982356291/report.json';r=json.loads(selected.read_text());check('actual preflight passed',r['passed'] is True and all(x['passed'] is True for x in r['checks']))
 for rel,digest in r['inputs'].items():check('tested source '+rel,sha(ROOT/rel)==digest and sha(selected.parent/'inputs'/rel)==digest)
 for rel,digest in r['artifacts'].items():check('retained preflight '+rel,sha(selected.parent/rel)==digest)
 u=json.loads((ROOT/'upstream.json').read_text())
 for p,k in [('parentHost','parentHostSHA256'),('parentRunner','parentRunnerSHA256'),('copiedClientHelper','copiedClientHelperSHA256'),('originalCoreHost','originalCoreHostSHA256'),('clientHelperParent','clientHelperParentSHA256')]:check('frozen ancestor '+p,sha(Path(u[p]))==u[k])
 check('selected own host pinned',sha(ROOT/'candidate_host.py')==u['selectedHostSHA256'])
 check('executed scope preserved',u['executedScenarioScope']==['GEOMETRY-MENU-'+str(i).zfill(2) for i in [1,2,3,4,5,6,7,8,10]])
 report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if report['passed']:
 files={}
 for p in sorted(ROOT.rglob('*')):
  if p.is_symlink():raise RuntimeError('Unexpected held source symlink')
  if p.is_file() and p.name!='held-source-manifest.json':files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
 m={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'allContractScenariosPassed':False,'fullRoadmapAccepted':False,'scope':report['scope'],'files':files,'preflightReport':{'path':str(selected.relative_to(ROOT)),'sha256':sha(selected)},'freezeReport':{'path':str((OUT/'report.json').relative_to(ROOT)),'sha256':sha(OUT/'report.json')},'selectedTuple':r['selectedTuple'],'executedScenarioScope':u['executedScenarioScope'],'scenario09':u['scope09']}
 (ROOT/'qa/held-source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(OUT/'report.json');raise SystemExit(not report['passed'])
