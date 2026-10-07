"""Reviewed actual process-stop custody oracle and unchanged normal package."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent
s=(docs/'native184_renderer_reload_runner.py').read_text().replace('--qa-preview-renderer-reload','--qa-preview-renderer-process-stop').replace('reload-webkit.png','process-stop-webkit.png')
a=s.index("   wait(lambda:'controlled-native-qa-reload-requested:'");b=s.index('\n  finally:',a)
s=s[:a]+'''   wait(lambda:'controlled-native-qa-process-stop-requested:' in full_log())
   check('controlledActualSharedProcessStopAfterOriginalSnapshot','controlled-native-qa-process-stop-requested: epoch=1 navigation=1 actualTerminateWebProcess=1 snapshotWritten=1 nativeSettlement=0' in full_log() and (private/'process-stop-webkit.png').is_file())
   wait(lambda:'controlled-native-qa-process-terminated:' in full_log())
   check('controlledActualOriginalPopupProcessTerminationSignal',full_log().count('controlled-native-qa-process-terminated: epoch=1 currentView=1 reason=2 actualWebKitSignal=1 nativeSettlement=0')==1 and 'Web process terminated: 2' in full_log())
   decoder=s.host.launch('controlled-process-first-pixels',[pre['pixelOracle'],str(private/'process-stop-webkit.png')],env=env);decoder.wait(timeout=5);check('controlledProcessOriginalPixelOracleNormalExit',decoder.returncode==0)
   pixels=json.loads((private/'controlled-process-first-pixels.log').read_text());check('controlledProcessActualOriginalSourcePixels',pixels['red']==19200 and pixels['green']==0 and pixels['blue']==0,pixels=pixels)
   wait(lambda:'native-recovery-ready:' in full_log())
   text=full_log();states=private_states();last=states[-1] if states else None
   check('controlledSharedProcessNativeCustodyClosedBeforeGTKRecovery',last is not None and last['privatePolicy']['realm']['closed'] and not last['privatePolicy']['models'] and not last['retainedInputs'] and not last['postedTickets'] and not last['confirmations'] and not last['returnedEventBatches'] and last['transport']['pending']==0 and 'controlled-native-realm-retired: epoch=1 ' in text and text.index('controlled-native-realm-retired: epoch=1 ')<text.index('native-recovery-ready:'),state=last)
   check('controlledSharedProcessFailureDoesNotAdmitReplacement','controlled-native-reopened:' not in text and 'controlled-renderer-context-replaced:' not in text and full_log().count('controlled-renderer-initialized:')==1)
   check('controlledOriginalGTKRecoveryControlsAvailable','native-recovery-ready: views=1 backend-normal=1' in text and 'recovery-control: id=1 ' in text)
   web.terminate();web.wait(timeout=5);text=full_log()
   check('controlledSharedProcessFailureOutcomeRetainedAfterStrictDrain',web.returncode==1 and 'shared-host-exit: failure=1 rendered=1' in text and 'Controlled native teardown incomplete:' not in text and 'GLib-GObject-CRITICAL' not in text,exitCode=web.returncode)
   r.update(actualSharedWebKitProcessTerminationQualified=True,actualKnownSharedProcessNativeDrainQualified=True,actualGTKRecoveryAfterStrictDrainQualified=True,expectedFailureExitCode=1,normalControlledHostClosureQualified=False,actualProcessBeforeStopSourcePixels=pixels,physicalRevealQualified=False,physicalConcealmentQualified=False,hardwarePresentationQualified=False,actualCapturedPixelsQualified=False,fullWorkloadProgressQualified=False,reloadRecoveryQualified=False,wholeHostRestartQualified=False,durableUnknownRecoveryQualified=False)
'''+s[b:]
needle="all(row['exitCode']==0 for row in r.get('ownedExitCodes',[]))";assert s.count(needle)==1;s=s.replace(needle,"all(row['exitCode']==(1 if row['name']=='controlled-host' else 0) for row in r.get('ownedExitCodes',[]))")
p=docs/'native186_process_stop_drain_runner.py';assert not p.exists();ast.parse(s);p.write_text(s)
for old,new,name in [(178,185,'cancelled_snapshot_normal'),(184,186,'renderer_reload')]:
 s=(docs/f'prepare_native{old}_{name}.py').read_text();needle=f"root=repo/'implementation/warlock-client-provider-native-v{old}';provider=repo/'implementation/warlock-preview-provider-v141'";assert s.count(needle)==1
 s=s.replace(needle,f"root=repo/'implementation/warlock-client-provider-native-v{new}';provider=repo/'implementation/warlock-preview-provider-v142'").replace(f'ownNative{old}',f'ownNative{new}').replace('GUI141','GUI142')
 if new==186:
  s=s.replace('native184_renderer_reload_runner.py','native186_process_stop_drain_runner.py')
  a=s.index("scope='Distinct actual current original WebKit reload");b=s.index(")\nassert all",a)
  s=s[:a]+"scope="+repr('Distinct actual shared related WebKit process termination after first original current captured snapshot; first original GTK/DOM/native admission/issuance/no legacy controls, real API stop and original popup termination reason2, actual first source red19200. Mandatory strict original native realm close/empty model/input/ticket/confirmation/returned-batch/transport BEFORE original GTK recovery controls, failure retained/no new renderer/realm/reset/replay, original backend normal and explicit failure1 after recovery dismissal/no incomplete teardown or criticals. Original observer6/core16/plugin19/AQ155/physical/journal/confirmation/deadlines unchanged. Original normal18529-control oracle separate. May fail: original fatal behavior retained142 to expose gap; no whole-host restart/durable Unknown/uncertain/hardware/full S09/release acceptance.')+s[b:]
  a=s.index("['PROGRESS ownNative186");b=s.index("],'progress'",a)
  s=s[:a]+repr(['PROGRESS ownNative186 packaged actual shared WebKit process stop/reason2/first current pixels, original native custody strict-close BEFORE GTK recovery oracle, original failure outcome after explicit recovery dismissal. Original142 fatal/recovery/strict Native gates unchanged, no synthetic settlement/reset/replay. Original normal185 separate; observer6/core16/plugin19/AQ155/deadlines unchanged. Full whole-host restart/durable Unknown/uncertain/physical/release gates remain.'])[:-1]+s[b:]
 p=docs/f'prepare_native{new}_'+pathlib.Path(name+'.py') if False else docs/f'prepare_native{new}_{"process_stop" if new==186 else name}.py'
 assert not p.exists();ast.parse(s);p.write_text(s);print(p)
