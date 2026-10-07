"""Prepare a distinct real-current-error negative oracle, retaining normal runner."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent;p=docs/'native166_current_failure_runner.py';assert not p.exists();s=(docs/'native138_controlled_curtain_runner.py').read_text()
s=s.replace('"""Actual controlled host admission/policy/pure renderer in reviewed private GUI."""','"""Actual matching-current WebKit cancellation, expected failure without settlement."""')
needle="'--qa-preview-snapshot',str(private/'controlled-webkit.png')";assert s.count(needle)==1;s=s.replace(needle,"'--qa-preview-current-cancelled-snapshot','--qa-preview-snapshot',str(private/'current-cancelled-webkit.png')")
a=s.index('   image_rows=wait(');b=s.index('\n  finally:',a)
s=s[:a]+'''   wait(lambda:web.poll() is not None)
   text=full_log()
   check('controlledCurrentCancellationUsesActualOriginalWebKit','controlled-native-snapshot-cancel-request: request=1 actualCancellable=1 realWebKit=1 nativeSettlement=0' in text)
   check('controlledCurrentCancellationOriginalFinishConsumedOnce',text.count('controlled-native-snapshot-finish-outcome: image=0 cancelled=1 retainedEpoch=1 currentEpoch=1 replacedView=0 originalFinishCalls=1 nativeSettlement=0')==1)
   check('controlledCurrentCancellationMatchesOriginalScopeGuard',text.count('controlled-native-current-snapshot-error: scopeCurrent=1 actualCancelled=1 originalFinishCalls=1 nativeSettlement=0')==1 and 'controlled-native-snapshot-refused:' not in text)
   check('controlledCurrentFailureRetainsOriginalFailureExit',web.returncode==1 and text.count('Native client producer failed: Operation was cancelled')==1 and 'shared-host-exit: failure=0' not in text,exitCode=web.returncode)
   check('controlledCurrentFailureNeverAcceptsSnapshotArtifact',not list(private.glob('current-cancelled-webkit.png*')) and 'native-client-webkit-snapshot: saved=1' not in text)
   states=private_states();last=states[-1] if states else None
   check('controlledCurrentFailureRetainsOriginalNativeCustody',last is not None and not last['privatePolicy']['realm']['closed'] and bool(last['privatePolicy']['models']) and 'Controlled native teardown incomplete: Original policy/input/ticket/physical/journal/confirmation custody prevents realm retirement' in text,state=last)
   check('controlledCurrentFailureCannotClaimNewRealmOrRetirement','controlled-native-reopened:' not in text and 'controlled-native-realm-retired:' not in text and 'controlled-native-snapshot-held:' not in text)
   r.update(actualCurrentMatchingErrorNativeQualified=True,actualCurrentCancellationConsumedOnce=True,actualCurrentFailureNativeCustodyRetained=True,expectedFailureExitCode=1,normalControlledHostClosureQualified=False,gracefulCurrentFailureDrainQualified=False,physicalRevealQualified=False,physicalConcealmentQualified=False,hardwarePresentationQualified=False,actualCapturedPixelsQualified=False,fullWorkloadProgressQualified=False,reloadRecoveryQualified=False)
''' +s[b:]
needle="all(row['exitCode']==0 for row in r.get('ownedExitCodes',[]))";assert s.count(needle)==1;s=s.replace(needle,"all(row['exitCode']==(1 if row['name']=='controlled-host' else 0) for row in r.get('ownedExitCodes',[])) and any(row['name']=='controlled-host' and row['exitCode']==1 for row in r.get('ownedExitCodes',[]))")
ast.parse(s);p.write_text(s);print(p)
