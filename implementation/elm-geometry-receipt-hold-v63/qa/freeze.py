"""Verify exact CPU inputs/evidence and frozen backend before publishing source hold."""
import hashlib,json,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir();checks=[]
report={'passed':False,'scope':'CPU source/evidence integrity only; no native acceptance','checks':checks}
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
try:
 selected=ROOT/'qa/hold-1791104684942757105/report.json';r=json.loads(selected.read_text())
 check('45 actual wrapper checks passed',r['passed'] is True and len(r['checks'])==45 and all(x['passed'] is True for x in r['checks']))
 for rel,digest in r['inputs'].items():check('current tested source '+rel,sha(ROOT/rel)==digest and sha(selected.parent/'inputs'/rel)==digest)
 for rel,digest in r['artifacts'].items():check('retained evidence '+rel,sha(selected.parent/rel)==digest)
 for row in r['processes']:check('owned CPU child terminal '+row['mode'],not row.get('forcedCleanup') and row['code']==(0 if row['mode']=='release' else 1))
 manifest=Path(r['backend']['manifest']);check('exact frozen V59 manifest',sha(manifest)==r['backend']['sha256']=='90b3838d01da30e9e99f76290eb7dd96bd49a84499b602e38e6339b4e97d68e3')
 m=json.loads(manifest.read_text())
 for row in m['files']:check('V59 frozen file '+row['path'],sha(manifest.parent/row['path'])==row['sha256'])
 build=Path(m['buildRoot'])
 for rel,digest in r['backend']['artifacts'].items():check('imported captured backend '+rel,sha(build/rel)==digest)
 report['passed']=True;report['selectedReport']={'path':str(selected.relative_to(ROOT)),'sha256':sha(selected)}
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if report['passed']:
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='held-source-manifest.json'}
 packet={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':report['scope'],'files':files,'backend':r['backend'],'acceptanceReport':report['selectedReport'],'freezeReport':{'path':str((OUT/'report.json').relative_to(ROOT)),'sha256':sha(OUT/'report.json')}}
 (ROOT/'qa/held-source-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
print(OUT/'report.json');raise SystemExit(not report['passed'])
