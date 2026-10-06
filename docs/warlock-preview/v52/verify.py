"""Verify original S09 identities and bounded evidence without closing gates."""
import hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).parent;REPO=ROOT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((ROOT/'S09-EVIDENCE-PLAN.json').read_text())
for row in plan['inputs'].values():assert sha(REPO/row['path'])==row['sha256']
backlog=json.loads((REPO/plan['inputs']['backlog']['path']).read_text())
requirements=json.loads((REPO/plan['inputs']['requirements']['path']).read_text())['requirements']
assert len(requirements)==242 and sum(len(row['scenarios']) for row in requirements)==417
selected=[row for row in backlog['backlog'] if row['sprint']=='S09']
original=[(row['id'],name) for row in selected for name in row['acceptanceScenarioIds']]
actual=[(row['requirementId'],row['scenarioId']) for row in plan['scenarios']]
assert len(selected)==9 and len(original)==len(set(original))==13 and actual==original
native=json.loads((REPO/plan['inputs']['native']['path']).read_text())
assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==2341
checks={row['name']:row for row in native['checks']}
for row in plan['scenarios']:
    assert row['status']=='partial-unaccepted' and row['remainingEvidence']
    assert row['boundedPassingNativeControls'] and all(checks[name]['passed'] for name in row['boundedPassingNativeControls'])
assert not plan['S09Accepted'] and not plan['nativeAcceptance'] and not plan['fullReleaseAccepted']
out=ROOT/('verify-'+str(time.time_ns()));out.mkdir()
report={'passed':True,'scope':scope,'inputs':{str(ROOT/'S09-EVIDENCE-PLAN.json'):sha(ROOT/'S09-EVIDENCE-PLAN.json'),str(pathlib.Path(__file__)):sha(pathlib.Path(__file__))},'originalRequirements':9,'originalScenarioIds':13,'frozenBaseline':[242,417],'allScenariosRemainPartialUnaccepted':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'nextExecutableSlice':plan['nextExecutableSlice']}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(out/'report.json'),'S09Accepted':False}))
