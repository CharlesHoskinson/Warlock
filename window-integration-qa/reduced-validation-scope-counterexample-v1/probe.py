"""Actual V18 controllers with explicitly fake Desktop/Transport; CPU only."""
from pathlib import Path
import hashlib,json,os,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
S=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-reduced-validation-v18');sys.path.insert(0,str(S))
from test_reduced_validation import Tests
scope=require_qa_scope();fixture=Tests();fixture.setUp();result={}
try:
 old,receipt=fixture.moving();expected=[(w['address'],w['stableId'],w['pid'])for w in old.members];closed=fixture.d.windows.pop();fixture.d.native=[w for w in fixture.d.native if w['stableId']!=closed['stableId']];before=list(fixture.d.commits)
 ack=fixture.ack(old);fresh=fixture.c.current;freshObject=fresh is not old;initialMembers=list(fresh.members);fixture.d.block.set();fixture.wait(lambda:fixture.c.current is None)
 after=fixture.d.commits[len(before):]
 result=dict(result='counterexample reproduced'if len(after)==2 else 'counterexample not reproduced',scope=scope,actualControllerSources={n:hashlib.sha256((S/n).read_bytes()).hexdigest()for n in ('scene_controller.py','scene_manager.py','visual_retirement.py')},acceptedReceipt=receipt['receipt'],originalFamily=expected,closedMember=(closed['address'],closed['stableId'],closed['pid']),exactVisualACK=ack,freshObjectCreated=freshObject,freshInitialMembers=initialMembers,actualPostACKFakeNativeEffects=after,retainedHistoryProfile=fixture.c.history[-1].profile,nativeCommands=False,fixtureScope='actual controllers, fake Desktop effects and explicit authenticated-transport standin; no GUI/kernel native evidence')
finally:fixture.tearDown()
p=Path(__file__).with_name('result.json');fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in result.items()if k not in ('retainedHistoryProfile','actualControllerSources')}));raise SystemExit(result['result']!='counterexample reproduced')
