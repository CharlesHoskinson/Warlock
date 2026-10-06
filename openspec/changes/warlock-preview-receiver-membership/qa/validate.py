"""Validate additive evidence contract without changing original release scope."""
import hashlib,json,re,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2];OUT=ROOT/'qa'/('validate-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=ROOT/'specs/elm-capture-motion/spec.md';text=spec.read_text();names=re.findall(r'### Requirement: (WARLOCK-RECEIVER-\d+)',text);scenarios=re.findall(r'#### Scenario: (WARLOCK-RECEIVER-\d+) ([^\n]+)',text)
assert names==['WARLOCK-RECEIVER-00'+str(i) for i in range(1,4)]
assert [x[0] for x in scenarios]==names
for token in ['original receiver epoch','metadata inventory','mixed invalid prefix','two live items,128MiB,8 records,4 readers and2 views','old actor request floors','replaying an unknown outcome']:assert token in text,token
baseline=REPO/'docs/elm-roadmap/requirements.json';d=json.loads(baseline.read_text());rows=d['requirements'];assert len(rows)==242 and sum(len(x['scenarios']) for x in rows)==417
plan=REPO/'docs/warlock-preview/v60/S09-EVIDENCE-PLAN.json';p=json.loads(plan.read_text());assert not p['S09Accepted'] and not p['fullReleaseAccepted'] and len(p['scenarios'])==13
inputs={str(x):sha(x) for x in [spec,Path(__file__),baseline,plan,*ROOT.glob('*.md')]}
report={'passed':True,'scope':scope,'inputs':inputs,'requirements':names,'scenarios':scenarios,'frozenBaseline':[242,417],'originalS09ScenarioIds':13,'nativeAcceptance':False,'fullReleaseAccepted':False}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
