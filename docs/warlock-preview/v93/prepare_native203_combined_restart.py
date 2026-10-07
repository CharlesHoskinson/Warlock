"""Fresh fixture-focus adaptation; retain202 real captured/held-reader evidence."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v202';root=repo/'implementation/warlock-client-provider-native-v203'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();pre=json.loads((parent/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
failed=parent/'qa/native-1791404861355868537/report.json';report=json.loads(failed.read_text());assert not report['passed'] and report['cleanupPassed'] and len(report['checks'])==27
assert report['originalControlledPreview']['pixels']['red']==19200
log=(failed.parent/'native-evidence/generation-1.log').read_text();assert 'Activate ELM-AUTHORITY-FIXTURE' in log and 'controlled-native-reader-probed: epoch=1 heldRead=-1 heldDenied=1 freshDenied=1' in log
assert not any(line.startswith('frontend-request: ') and json.loads(line.split(': ',1)[1])['kind']=='window-effect' for line in log.splitlines())
assert not root.exists();root.mkdir(mode=0o700);(root/'qa').mkdir(mode=0o700)
for base,target in [(parent,root),(parent/'qa',root/'qa')]:
 for path in base.iterdir():
  if path.is_file() and path.name not in {'preflight.json','ANCESTRY.json','component-manifest.json'}:shutil.copy2(path,target/path.name)
p=root/'qa/native-window-restart.py';source=p.read_text();old='   preview.begin_close(1)\n';assert source.count(old)==1
source=source.replace(old,old+"   check('combinedActualFixtureRefocusPreservesMinimizeDecision',s.ctl('dispatch',\"hl.dsp.focus({window='address:\"+actual_fixture['address']+\"'})\").strip()=='ok')\n")
old='  finally:\n   for process in reversed(apps):';assert source.count(old)==1
source=source.replace(old,"  finally:\n   # Failure cleanup closes an actual already-revoked reader; it supplies no\n   # acceptance or native settlement and does not alter the qualification path.\n   if not report['passed'] and 'preview' in globals():\n    text=preview.text()\n    if 'controlled-native-reader-probed:' in text and 'controlled-native-reader-released:' not in text and supervisor.poll() is None:\n     generation=2 if 'second' in globals() else 1\n     preview.reader_stimulus(generation,'release')\n     deadline=time.monotonic()+6\n     while time.monotonic()<deadline and supervisor.poll() is None and 'controlled-native-reader-released:' not in preview.text():s.guard();time.sleep(.04)\n     report['abortReaderCleanup']={'requested':True,'originalReaderCloseObserved':'controlled-native-reader-released:' in preview.text(),'nativeSettlementInferred':False}\n   for name,process in globals().get('preview_fixtures',[]):\n    if process.poll() is None:\n     control_file=OUTPUT/(name+'-control');temporary=control_file.with_suffix('.tmp');temporary.write_text('1 quit\\n');temporary.chmod(0o600);temporary.replace(control_file);process.wait(timeout=5)\n    report.setdefault('previewFixtureCleanupExits',[]).append({'name':name,'exitCode':process.returncode,'expected':0})\n   for process in reversed(apps):")
ast.parse(source);p.write_text(source)
inputs=dict(pre['inputs']);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');inputs[str(failed)]=sha(failed);inputs[str(pathlib.Path(__file__))]=sha(__file__)
for base in [root,root/'qa']:
 for path in base.iterdir():
  if path.is_file():inputs[str(path)]=sha(path)
pre.update(inputs=inputs,retainedNative202Failure=str(failed),retainedNative202FailureSHA256=sha(failed));(root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'retainedFailure':str(failed),'failureSHA256':sha(failed),'change':'Actual compositor fixture focus after real popup close preserves original Minimize oracle; real reader and child-fixture failure cleanup only. No bypass of taskbar policy, synthetic native fact or production change. Original deadlines retained.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['Native202 retained27-check failure after real captured pure-preview source red19200/known Native ticket/held original GIO/close and both reads revoked: primary correctly offers Activate after popup focus change, original Minimize wait expires with no window command sent. Fresh203 restores actual fixture focus through compositor to retain original Minimize command oracle; adds actual already-revoked reader and normal source/companion failure cleanup. Original combined duty/Unknown/native Restart/fresh owner/pixels/keyboard/clock/strict close/deadlines retained; production unchanged.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str(failed.relative_to(repo))]))
