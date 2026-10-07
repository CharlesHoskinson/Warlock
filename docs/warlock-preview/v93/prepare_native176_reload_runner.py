"""Prepare actual same-popup reload oracle from original owning native runner."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent;p=docs/'native176_renderer_reload_runner.py';assert not p.exists();s=(docs/'native155_reopened_snapshot_runner.py').read_text().replace("'--qa-preview-reopened-snapshot'","'--qa-preview-renderer-reload'").replace('delayed-webkit.png','reload-webkit.png')
a=s.index("   wait(lambda:'controlled-native-snapshot-held:");b=s.index('   def current_image():',a)
s=s[:a]+'''   wait(lambda:'controlled-native-qa-reload-requested:' in full_log())
   check('controlledActualWebKitReloadRequestedAfterOriginalSnapshot','controlled-native-qa-reload-requested: epoch=1 navigation=1 actualWebKitReload=1 snapshotWritten=1 inferredSettlement=0' in full_log() and (private/'reload-webkit.png').is_file())
   wait(lambda:'controlled-native-qa-reload-start:' in full_log())
   check('controlledActualOriginalViewReloadLoadStarted','controlled-native-qa-reload-start: epoch=1 navigation=2 initialized=1 sameView=1 actualLoadStarted=1 uri=elm-shell://app/controlled-popup.html inferredSettlement=0' in full_log())
   first_epoch=1;first_binding=issued['privatePolicy']['commands']['binding']
   decoder=s.host.launch('controlled-first-reload-pixels',[pre['pixelOracle'],str(private/'reload-webkit.png')],env=env);decoder.wait(timeout=5);check('controlledBeforeReloadOriginalPixelOracleNormalExit',decoder.returncode==0)
   first_pixels=json.loads((private/'controlled-first-reload-pixels.log').read_text());check('controlledBeforeReloadActualSourcePixels',first_pixels['red']==19200 and first_pixels['green']==0 and first_pixels['blue']==0,pixels=first_pixels)
   check('controlledReloadDoesNotFailTheOriginalHost',web.poll() is None and 'Native client producer failed:' not in full_log())
   def drained():
    states=private_states()
    if not states:return None
    state=states[-1];policy=state['privatePolicy'];transport=state['transport']
    return state if not policy['models'] and not policy['realm']['ingress']['pending'] and not policy['realm']['deferred'] and not state['retainedInputs'] and not state['postedTickets'] and not state['confirmations'] and not state['returnedEventBatches'] and transport['pending']==0 else None
   closed=wait(lambda:next((state for state in reversed(private_states()) if state['privatePolicy']['realm']['epoch']=='1' and state['privatePolicy']['realm']['closed']),None))
   check('controlledReloadOriginalRealmStrictlyClosedBeforeReplacement',not closed['privatePolicy']['models'] and not closed['retainedInputs'] and not closed['postedTickets'] and not closed['confirmations'] and not closed['returnedEventBatches'] and closed['transport']['pending']==0,state=closed)
   wait(lambda:'controlled-renderer-context-replaced: retiredEpoch=1 ' in full_log())
   check('controlledReloadReplacementKeepsSamePopupLease','controlled-native-replacement-admission: retiredEpoch=1 pendingPopup=1 ' in full_log() and ' lease=1 freshDOMRequired=1' in full_log())
   reopened=wait(lambda:next((state for state in reversed(private_states()) if int(state['privatePolicy']['realm']['epoch'])>first_epoch and state['privatePolicy']['models'] and int(state['transport']['nativeIssuedThrough'])>0 and int(state['transport']['deliveredThrough'])>0),None))
   second_epoch=int(reopened['privatePolicy']['realm']['epoch'])
   check('controlledReloadOriginalPolicyAndNativeBindingRetained',second_epoch==2 and reopened['privatePolicy']['commands']['binding']==first_binding and reopened['privatePolicy']['visuals']['surface']['lease']=='1' and 'controlled-native-reopened: previousEpoch=1 nativeEpoch=2 samePolicy=1 sameBinding=1 originalNative=1 grantResets=0 rendererPolicies=0' in full_log(),state=reopened)
   wait(lambda:'controlled-renderer-initialized: nativeEpoch=2 ' in full_log())
   check('controlledReloadFreshRendererInitializedOnceEachEpoch',full_log().count('controlled-renderer-initialized:')==2)
''' +s[b:]
s=s.replace("image.name=='reload-webkit.png.request-2.png' and not (private/'reload-webkit.png').exists()","image.name=='reload-webkit.png.request-2.png' and (private/'reload-webkit.png').is_file()")
s=s.replace("paint['height']==420,observation=paint)","paint['height']==420 and int(paint['navigation'])>=3 and paint['lease']=='1',observation=paint)")
s=s.replace("final['nativeEffectError']=='' and full_log().count('controlled-native-snapshot-released:')==1","final['nativeEffectError']=='' and final['privatePolicy']['realm']['closed']")
s=s.replace('actualOldResultAcrossReopenedRealmQualified=True,','actualControlledRendererReloadQualified=True,actualSamePopupLeaseAcrossReloadQualified=True,actualBeforeReloadSourcePixels=first_pixels,')
s=s.replace("full_log().count('controlled-renderer-initialized:')==1","full_log().count('controlled-renderer-initialized: nativeEpoch=1 ')==1")
ast.parse(s);p.write_text(s);print(p)
