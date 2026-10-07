"""Keep original native retirement running after a current snapshot failure."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v138';root=r/'implementation/warlock-preview-provider-v139';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and not d['passed'] and d['actualCurrentFailureDrainCounterexample'] and not root.exists()
for n,row in d['files'].items():assert sha(parent/n)==row['sha256'],n
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'spec/current_failure_drain.qnt').write_text('''module current_failure_drain {
 type State={failed:bool,closing:bool,owned:bool,closed:bool,exited:bool,unknown:bool,epoch:int,policy:int}
 type Event=Fault|NativeSettled|StrictRetire|Exit|LaterIntent|StaleError|Unknown
 var s:State
 pure val initial={failed:false,closing:false,owned:true,closed:false,exited:false,unknown:false,epoch:1,policy:1}
 pure def earlyExit(st:State):State={...st,exited:true}
 pure def reduce(st:State,e:Event):State=match e {
  | Fault => if(st.exited)st else {...st,failed:true,closing:true}
  | NativeSettled => if(st.closing and not(st.unknown)){...st,owned:false} else st
  | StrictRetire => if(st.closing and not(st.owned) and not(st.unknown)){...st,closed:true,closing:false} else st
  | Exit => if(st.failed and st.closed and not(st.owned) and not(st.unknown)){...st,exited:true} else st
  | LaterIntent => st
  | StaleError => st
  | Unknown => if(st.exited or st.closed)st else {...st,failed:true,closing:true,unknown:true}
 }
 pure def safe(st:State):bool=all{st.epoch==1,st.policy==1,st.closed implies not(st.owned or st.unknown),st.exited implies (st.failed and st.closed and not(st.owned or st.unknown))}
 action init=s'=initial
 action fire(e:Event):bool=s'=reduce(s,e)
 action step={nondet e=Set(Fault,NativeSettled,StrictRetire,Exit,LaterIntent,StaleError,Unknown).oneOf();fire(e)}
 val safety=safe(s)
}
''')
(root/'spec/current_failure_drain_tests.qnt').write_text('''module current_failure_drain_tests {
 import current_failure_drain.* from "./current_failure_drain"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run originalEarlyExitLeavesCustody=init.then(fire(Fault)).then(check(not(safe(earlyExit(s)))))
 run currentFailureRetainsCustody=init.then(fire(Fault)).then(fire(Exit)).then(check(s.failed and s.closing and s.owned and not(s.exited)))
 run nativeReceiptsPrecedeStrictCloseAndExit=init.then(fire(Fault)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.failed and s.closed and s.exited and not(s.owned)))
 run laterIntentCannotCancelFailure=init.then(fire(Fault)).then(fire(LaterIntent)).then(check(s.failed and s.closing and s.owned))
 run rendererDisposalCannotSettle=init.then(fire(Fault)).then(fire(StaleError)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.owned and not(s.closed or s.exited)))
 run unknownNeverNormalExit=init.then(fire(Unknown)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.failed and s.unknown and s.owned and not(s.closed or s.exited)))
 run staleOldErrorDoesNotFailCurrent=init.then(fire(StaleError)).then(check(not(s.failed) and s.owned))
 run noGrantOrPolicyReset=init.then(fire(Fault)).then(fire(LaterIntent)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Exit)).then(check(s.epoch==1 and s.policy==1 and s.failed))
}
''')
p=root/'qa/current-failure-drain-model.py';s=(root/'qa/async-error-scope-model.py').read_text().replace('async-error-scope','current-failure-drain').replace('async_error_scope','current_failure_drain').replace('len(selected)==10','len(selected)==8').replace("glob('named-*.itf.json')))==10","glob('named-*.itf.json')))==8").replace('namedScenarios=10','namedScenarios=8').replace('1360041','1390041').replace('1360042','1390042');s=s.replace('Original async result scope/error disposition abstraction only, including legacy error-before-scope counterexample and proposed scope-before-current-error handling; original independent physical, terminal, journal and confirmation Drain remains Native authority. Same policy/context replacement/pending intent/stale callback safety is model scope only. Named selection and invariant samples are model evidence, not actual GTK/WebKit, physical reveal or release acceptance.','Current failure drain abstraction only: failure/owned custody/quarantine, independent native settlement, strict close before failure exit, later intent no cancellation/reset, stale error no authority and explicit Unknown. NativeSettled represents separately required original physical/journal/confirmation witnesses, never a UI inferred result. This model does not prove actual native source/receipts/liveness/deadlines, graceful recovery, physical reveal or release; actual Native168 failure and fresh native fix oracle qualify separately.');p.write_text(s)
p=root/'native/shared-host.c';s=p.read_text();needle='static guint64 controlled_current_epoch(void);';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic void controlled_snapshot_failure(GError *error);')
needle='        client_snapshot_free(snapshot);client_failure(error);return;';assert s.count(needle)==1;s=s.replace(needle,'''        const gboolean controlled_result=snapshot->controlled_visual!=NULL;
        client_snapshot_free(snapshot);
        if(controlled_result)controlled_snapshot_failure(error);else client_failure(error);
        return;''');p.write_text(s)
p=root/'native/controlled-preview-host.h';s=p.read_text();needle='static gboolean controlled_retiring,controlled_retired;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic gboolean controlled_failure_draining;')
needle='static gboolean controlled_wire_room(gsize bytes) {';assert s.count(needle)==1;s=s.replace(needle,'''static void controlled_snapshot_failure(GError *error) {
    /* The matching renderer failed; original Native duties are still known.
     * Keep their existing poll/receipt path alive instead of exiting early.
     * An uncertain native result still uses the original strict refusal path. */
    g_printerr("Native client producer failed: %s\\n",error?error->message:"Owner unavailable");g_clear_error(&error);
    failed=TRUE;controlled_failure_draining=TRUE;controlled_retiring=TRUE;
    controlled_curtain();controlled_paint_cancel();controlled_initialized=FALSE;
    GError *native_error=NULL;
    if(!controlled_driver || !controlled_visual ||
       !warlock_visual_channel_invalidate(controlled_visual,G_OBJECT(popup_view),&native_error) ||
       !warlock_policy_driver_quarantine(controlled_driver,controlled_epoch,&native_error)) {
        controlled_fault(native_error);return;
    }
    g_clear_pointer(&controlled_last_visual,g_free);
    g_print("controlled-native-current-failure-drain: epoch=%" G_GUINT64_FORMAT " quarantine=1 originalNative=1 failureRetained=1 inferredSettlement=0\\n",controlled_epoch);fflush(stdout);
}
'''+needle)
needle='    return controlled_replace_retired_renderer(error);';assert s.count(needle)==1;s=s.replace(needle,'''    if(controlled_failure_draining) {
        /* Original policy/physical/journal/confirmation close already passed.
         * Failure remains failure; do not reopen or construct a replacement. */
        g_print("controlled-native-current-failure-retired: epoch=%" G_GUINT64_FORMAT " failureRetained=1 originalStrictClose=1\\n",controlled_epoch);fflush(stdout);
        gtk_main_quit();return TRUE;
    }
    return controlled_replace_retired_renderer(error);''');p.write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'scope':'Fresh GUI139 implements actual held138/Native168 current-error drain repair. Matching controlled snapshot failure retains original failure outcome/curtain, invalidates visual and uses original urgent driver quarantine, sticky retiring producer, original input/step/poll/receipt/strict retirement loop. Renderer admission/visual offers stop; only after original strict native close and closed policy report may original failure exit proceed, with no replacement/reopen/reset/forged settlement. Native uncertainty retains original failclosed refusal path. Legacy current errors and old-scope disposition unchanged. New failure-drain model8/200 and current full119 next, then unchanged original168 oracle and normal/old-canceled regressions. Candidate not accepted; full release remains open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,d['owner'],str(root.relative_to(r)),['PROGRESS ownGUI139 current matching snapshot failure retains failure/curtain, original urgent native quarantine and sticky retiring scope; keep original input/step/poll/receipt custody until original strict Native close, then exit failure1 without replacement/reset/inferred settlement. New model8/200/full119 then byte-identical168 actual drain oracle and unchanged normal/old-canceled controls. Candidate unaccepted/full release remains open/installed drafts foreign preserved.'],'progress',[str((root/'ANCESTRY.json').relative_to(r))]))
