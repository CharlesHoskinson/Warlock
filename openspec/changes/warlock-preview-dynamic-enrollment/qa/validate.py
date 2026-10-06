"""Verify additive dynamic enrollment requirements preserve the frozen release inventory."""
import hashlib,json,re,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2];OUT=ROOT/'qa'/('validate-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=ROOT/'specs/elm-capture-motion/spec.md';text=spec.read_text();names=re.findall(r'### Requirement: (WARLOCK-ENROLL-\d+)',text);scenarios=re.findall(r'#### Scenario: (WARLOCK-ENROLL-\d+) ([^\n]+)',text)
assert names==['WARLOCK-ENROLL-00'+str(i) for i in range(1,5)] and [row[0] for row in scenarios]==[name for name in names for _ in range(2)]
for token in ['one native critical section','original receiver epoch','original deadline','typed local','exact final ACK','request floor','explicit subject admission']:assert token in text,token
baseline=REPO/'docs/elm-roadmap/requirements.json';rows=json.loads(baseline.read_text())['requirements'];assert len(rows)==242 and sum(len(x['scenarios']) for x in rows)==417
sys.path.insert(0,str(REPO/'implementation/elm-build-loop-v1'));import loop;inventory=loop.coordinator_status(REPO);assert inventory['baselineVerification']['verified'] and inventory['rightClickAmendment']['requirements']==24 and inventory['rightClickAmendment']['scenarios']==48
plan=REPO/'docs/warlock-preview/v60/S09-EVIDENCE-PLAN.json';p=json.loads(plan.read_text());assert not p['S09Accepted'] and not p['fullReleaseAccepted'] and len(p['scenarios'])==13
inputs={str(x):sha(x) for x in [spec,Path(__file__),baseline,plan,*ROOT.glob('*.md')]}
(OUT/'report.json').write_text(json.dumps({'passed':True,'scope':scope,'inputs':inputs,'requirements':names,'scenarios':scenarios,'frozenBaseline':[242,417],'originalS09ScenarioIds':13,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n');print(OUT/'report.json')
