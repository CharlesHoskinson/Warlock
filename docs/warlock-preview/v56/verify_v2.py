import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).parent;REPO=ROOT.parents[2];OUT=ROOT/('verify-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'S09-EVIDENCE-PLAN.json';d=json.loads(p.read_text());prior=REPO/'docs/warlock-preview/v54/S09-EVIDENCE-PLAN.json';old=json.loads(prior.read_text())
assert [(x['requirementId'],x['scenarioId'],x['taskId']) for x in d['scenarios']]==[(x['requirementId'],x['scenarioId'],x['taskId']) for x in old['scenarios']] and len(d['scenarios'])==13
assert not d['S09Accepted'] and not d['fullReleaseAccepted'] and all(x['status']=='partial-unaccepted' for x in d['scenarios'])
for rel,h in d['inputs'].items():
 if isinstance(h,dict):assert set(h)=={'path','sha256'};rel,h=h['path'],h['sha256']
 assert sha(REPO/rel)==h,rel
baseline=REPO/'docs/elm-roadmap/requirements.json';rows=json.loads(baseline.read_text())['requirements'];assert len(rows)==242 and sum(len(x['scenarios']) for x in rows)==417
packet=REPO/'docs/warlock-preview/v55/report.json';proof=json.loads(packet.read_text());assert proof['passed'] and proof['nativeTitleIconFallbackBoundedQualified'] and not proof['S09Accepted'] and not proof['fullReleaseAccepted'] and proof['nativeControls']==2372
for component in proof['components']:
 m=REPO/component['path'];assert sha(m)==component['sha256'];held=json.loads(m.read_text())
 for rel,row in held['files'].items():assert sha(m.parent/rel)==row['sha256'],rel
report={'passed':True,'scope':scope,'inputs':{str(x):sha(x) for x in [p,prior,packet,baseline,Path(__file__)]},'originalS09Identities':13,'frozenBaseline':[242,417],'nativeAcceptance':False,'fullReleaseAccepted':False}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
