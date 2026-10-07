"""Retain original focused-window fault precondition through actual pointer input."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v203';root=repo/'implementation/warlock-client-provider-native-v204'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();pre=json.loads((parent/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
failed=parent/'qa/native-1791405070407842700/report.json';report=json.loads(failed.read_text());assert not report['passed'] and report['cleanupPassed'] and len(report['checks'])==91 and 'finalFallbackActualKeyboardRecipient' in report['error']
assert report['combinedKnownPreviewBeforeRestartQualified'] and report['combinedControlledPreviewRestartQualified'] and report['actualWindowCommandDurableUnknownQualified']
assert all(r['exitCode']==0 for r in report['previewFixtureCleanupExits'])
assert not root.exists();root.mkdir(mode=0o700);(root/'qa').mkdir(mode=0o700)
for base,target in [(parent,root),(parent/'qa',root/'qa')]:
 for p in base.iterdir():
  if p.is_file() and p.name not in {'preflight.json','ANCESTRY.json','component-manifest.json'}:shutil.copy2(p,target/p.name)
p=root/'qa/native-window-restart.py';source=p.read_text();old='   preview.begin_close(2);preview.release(2)\n';assert source.count(old)==1
source=source.replace(old,old+"   if not final_minimized:\n    native_window=next(w for w in window_facts()['facts']['windows'] if w['incarnation']==target);x,y,width,height=native_window['geometry']\n    click({'point':[x+40,y+80],'visible':True})\n    focused_before_fault=wait(lambda:window_facts() if window_facts()['facts']['focused']==target else None)\n    check('combinedRealPointerEstablishesOriginalFinalFaultFocus',focused_before_fault['facts']['focused']==target and len(journal())==1 and journal()[0]==explicit,facts=focused_before_fault)\n    input_state('beforeFinalRendererFailure',False)\n    report['originalFinalFaultFocusEstablishedByActualPointer']=True\n   report['popupDismissalFocusRestorationQualified']=False\n")
ast.parse(source);p.write_text(source)
inputs=dict(pre['inputs']);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');inputs[str(failed)]=sha(failed);inputs[str(pathlib.Path(__file__))]=sha(__file__)
for base in [root,root/'qa']:
 for p in base.iterdir():
  if p.is_file():inputs[str(p)]=sha(p)
pre.update(inputs=inputs,retainedNative203Failure=str(failed),retainedNative203FailureSHA256=sha(failed));(root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'retainedFailure':str(failed),'failureSHA256':sha(failed),'change':'Background click used to close fresh preview clears focus; actual pointer click and independent native/keyboard receipts reestablish the original visible-fixture fault precondition before the second renderer failure. Minimized fixture is never refocused. Original final fallback keyboard/pixel/cohort checks retained, no additional window effect, historical Unknown unchanged. Popup-dismissal focus restoration remains unqualified.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['Native203 retained91-check failure at final fallback keyboard: original strict preview retirement before recovery/actual native Restart/Unknown history/no replay/fresh native capture/source pixels and new strict close pass, but deliberate background close clears focus before second renderer fault. Fresh204 uses actual pointer/native focused fact/keyboard receipt to reestablish original focused-visible-fixture fault precondition, retains original final keyboard/pixels/normal/cohort/deadline controls and never refocuses minimized fixture. Popup-dismissal focus restoration remains separate open gate; production unchanged.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str(failed.relative_to(repo))]))
