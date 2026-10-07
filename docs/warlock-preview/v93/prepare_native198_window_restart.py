"""Observe exact recovered Unknown and immutable native retirement history.

Native197 reached real Restart/fresh binding but expected obsolete Pending.
The current ledger explicitly normalizes unresolved records to Unknown.
"""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v197';root=repo/'implementation/warlock-client-provider-native-v198'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((parent/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
failed=parent/'qa/native-1791403580402133774/report.json';report=json.loads(failed.read_text())
assert not report['passed'] and report['cleanupPassed'] and len(report['checks'])==37
failed_check=next(c for c in report['checks'] if c['name']=='replacementReceivesFreshlyBoundOriginalUnknownIntent')
assert not failed_check['passed'] and failed_check['frame']['record']['status']=='Unknown'
assert not root.exists();root.mkdir(mode=0o700);(root/'qa').mkdir(mode=0o700)
for base,target in [(parent,root),(parent/'qa',root/'qa')]:
 for p in base.iterdir():
  if p.is_file() and p.name not in {'preflight.json','ANCESTRY.json','component-manifest.json'}:shutil.copy2(p,target/p.name)
p=root/'qa/native-window-restart.py';source=p.read_text()
old="uncertain['binding']==fresh_binding and uncertain['record']['binding']==old_binding and uncertain['record']['intent']==old_request['intent'] and uncertain['record']['status']=='Pending'"
assert source.count(old)==1;source=source.replace(old,"uncertain['binding']==fresh_binding and uncertain['record']==dict(admitted,status='Unknown')")
old="check('freshCoherentSnapshotPrecedesNewEffects',projection()['phase']=='Coherent' and not journal(),projection=projection())"
assert source.count(old)==1
source=source.replace(old,old+"\n   released=wait(lambda:next((f for f in frames('backend-frame: ') if f.get('kind')=='host-reservation-released' and f.get('record')==uncertain['record']),None))\n   proof=released['release']['proof'];observed=released['release']['observation']\n   check('reservationReleaseHasActualNativeRetirementAndFreshAcceptedReads',proof['grantState']=='Retired' and proof['queriedBinding']==old_binding and proof['binding']==fresh_binding and observed['actionContext']['lifetime']==old_binding['lifetime'] and observed['geometryContext']['lifetime']==old_binding['lifetime'],frame=released)\n   history=json.loads((recovery_dir/'ledger-v6.json').read_text())\n   historical=next(r for r in history['releases'] if r['record']==uncertain['record'])\n   check('durableReservationReleasePreservesExactHistoricalUnknown',historical['phase']=='Released' and historical['record']==dict(admitted,status='Unknown') and historical['proof']==proof and historical['observation']==observed,history=historical)\n   report['historicalUnknownBeforeNewAction']=historical")
old="report['recovery']={'mode':";assert source.count(old)==1
source=source.replace(old,"history_after=json.loads((recovery_dir/'ledger-v6.json').read_text())\n   check('newExplicitOutcomeDoesNotRewriteHistoricalUnknown',historical in history_after['releases'],history=historical)\n   report['actualWindowCommandRestartQualified']=True\n   report['actualWindowCommandDurableUnknownQualified']=True\n   report['recovery']={'mode':")
ast.parse(source);p.write_text(source)
inputs=dict(pre['inputs']);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');inputs[str(failed)]=sha(failed);inputs[str(pathlib.Path(__file__))]=sha(__file__)
for base in [root,root/'qa']:
 for p in base.iterdir():
  if p.is_file():inputs[str(p)]=sha(p)
pre.update(inputs=inputs,retainedNative197Failure=str(failed),retainedNative197FailureSHA256=sha(failed));(root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'retainedFailure':str(failed),'failureSHA256':sha(failed),'change':'Exact current recovered Unknown, actual native binding retirement/post-proof reads and immutable historical Unknown before and after newer explicit command. Original pre-restart Pending admission remains checked. No native outcome inference, replay or production change.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['Native197 retained37-check failure at obsolete Pending expectation after real committed restore/lost receipt/native Restart/fresh same-lifetime binding. Current contract normalizes exact original record to Unknown; Native198 requires exact Unknown plus actual native retirement/post-proof reads and unchanged historical Unknown after newer explicit command. Original before-restart Pending/pixels/keyboard/identities/deadlines retained. Combined controlled-preview restart/full release open.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str(failed.relative_to(repo))]))
