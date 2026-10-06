"""Validate additive evidence contract without changing original release scope."""
import hashlib,json,re,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2];OUT=ROOT/'qa'/('validate-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=ROOT/'specs/elm-capture-motion/spec.md';text=spec.read_text();names=re.findall(r'### Requirement: (WARLOCK-METADATA-\d+)',text);scenarios=re.findall(r'#### Scenario: (WARLOCK-METADATA-\d+) ([^\n]+)',text)
assert names==['WARLOCK-METADATA-00'+str(i) for i in range(1,5)]
assert [x[0] for x in scenarios]==names
for token in ['canonical uint64','independently of Elm progress','immutable Elm lifecycle','two assets','actual consumption/close','exact known current preview job']:assert token in text,token
baseline=REPO/'docs/elm-roadmap/requirements.json';d=json.loads(baseline.read_text());rows=d['requirements'];assert len(rows)==242 and sum(len(x['scenarios']) for x in rows)==417
plan=REPO/'docs/warlock-preview/v54/S09-EVIDENCE-PLAN.json';p=json.loads(plan.read_text());assert not p['S09Accepted'] and not p['fullReleaseAccepted'] and len(p['scenarios'])==13
inputs={str(x):sha(x) for x in [spec,Path(__file__),baseline,plan,*ROOT.glob('*.md')]}
report={'passed':True,'scope':scope,'inputs':inputs,'requirements':names,'scenarios':scenarios,'frozenBaseline':[242,417],'originalS09ScenarioIds':13,'nativeAcceptance':False,'fullReleaseAccepted':False}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
