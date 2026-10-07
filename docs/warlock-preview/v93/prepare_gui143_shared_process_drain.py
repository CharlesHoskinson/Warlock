"""Retain shared process failure while original known native duties drain."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v142';root=r/'implementation/warlock-preview-provider-v143';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and not d['passed'] and d['actualSharedRendererProcessCounterexample'] and not root.exists()
for n,row in d['files'].items():assert sha(parent/n)==row['sha256'],n
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/host.c';s=p.read_text();needle='static gboolean qa_exit, reported, failed, shutting_down, renderer_failed, quit_requested;';assert s.count(needle)==1;s=s.replace(needle,needle+'\n/* Optional owning shared-host hook; standalone legacy behavior stays exact. */\nstatic gboolean (*renderer_failure_drain_hook)(void);')
needle='if (error) { g_printerr("Native delivery failed: %s\\n",error->message); g_error_free(error); failed=TRUE; gtk_main_quit(); }';assert s.count(needle)==1
s=s.replace(needle,'if (error) { g_printerr("Native delivery failed: %s\\n",error->message); g_error_free(error); failed=TRUE; if(!renderer_failure_drain_hook || !renderer_failure_drain_hook())gtk_main_quit(); }');p.write_text(s)
p=root/'native/shared-host.c';s=p.read_text();needle='#define main inherited_main\n#include "host.c"\n#undef main';assert s.count(needle)==1;s=s.replace(needle,'#define main inherited_main\n#define terminated inherited_terminated\n#include "host.c"\n#undef terminated\n#undef main\nstatic void terminated(WebKitWebView*,WebKitWebProcessTerminationReason,gpointer);')
needle='#include "controlled-preview-host.h"';assert s.count(needle)==1;s=s.replace(needle,needle+'''
static void terminated(WebKitWebView *target,WebKitWebProcessTerminationReason reason,gpointer unused) {
    if(shutting_down)return;
    if(qa_controlled_preview && (controlled_driver || controlled_process_failure_draining)) {
        /* Shared related views report the same actual process loss. Keep its
         * original failure and recovery path, but never let duplicate signals
         * abandon known Native duties before original strict retirement. */
        g_printerr("Web process terminated: %d\\n",reason);
        if(controlled_begin_renderer_failure(TRUE))return;
    }
    inherited_terminated(target,reason,unused);
}
''')
needle='if(qa_controlled_preview){controlled_curtain();g_signal_connect(popup_view,"load-changed",G_CALLBACK(controlled_load_changed),NULL);';assert s.count(needle)==1;s=s.replace(needle,'if(qa_controlled_preview){renderer_failure_drain_hook=controlled_delivery_failure;controlled_curtain();g_signal_connect(popup_view,"load-changed",G_CALLBACK(controlled_load_changed),NULL);')
needle='    if (renderer_failed && !quit_requested) {recovery_show();gtk_main();}';assert s.count(needle)==1;s=s.replace(needle,'''    if (renderer_failed && !quit_requested) {
        if(qa_controlled_preview && controlled_driver && !controlled_retired) {
            /* An uncertain realm is not restart authority. Original strict
             * close remains refused; preserve failure and report the gap. */
            g_printerr("Shared recovery refused: original native custody not strictly retired\\n");
        } else {recovery_show();gtk_main();}
    }''');p.write_text(s)
p=root/'native/controlled-preview-host.h';s=p.read_text();needle='static gboolean controlled_failure_draining;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic gboolean controlled_process_failure_draining;')
needle='static gboolean controlled_wire_room(';assert s.count(needle)==1;s=s.replace(needle,'''static gboolean controlled_begin_renderer_failure(gboolean process_failure) {
    if(!controlled_driver)return FALSE;
    failed=TRUE;
    if(process_failure){renderer_failed=TRUE;controlled_process_failure_draining=TRUE;}
    if(controlled_retired) {if(process_failure)gtk_main_quit();return TRUE;}
    if(controlled_uncertain) {controlled_fault(NULL);return TRUE;}
    if(controlled_failure_draining)return TRUE; // Duplicates never cancel drain.
    controlled_failure_draining=TRUE;controlled_retiring=TRUE;
    controlled_curtain();controlled_paint_cancel();controlled_initialized=FALSE;
    GError *error=NULL;
    if(!controlled_visual ||
       !warlock_visual_channel_invalidate(controlled_visual,G_OBJECT(popup_view),&error) ||
       !warlock_policy_driver_quarantine(controlled_driver,controlled_epoch,&error)) {
        controlled_fault(error);return TRUE;
    }
    g_clear_pointer(&controlled_last_visual,g_free);
    g_print("controlled-native-renderer-failure-drain: epoch=%" G_GUINT64_FORMAT " processFailure=%d quarantine=1 originalNative=1 failureRetained=1 inferredSettlement=0\\n",controlled_epoch,process_failure);fflush(stdout);
    return TRUE;
}
static gboolean controlled_delivery_failure(void) {
    if(!qa_controlled_preview)return FALSE;
    /* Actual evaluation finish/error remains consumed by its original callback.
     * A late delivery error cannot exit a known closing realm or dispose it.
     * The independently delivered real termination signal selects GTK recovery. */
    return controlled_begin_renderer_failure(FALSE);
}
'''+needle)
p.write_text(s)
(root/'spec/shared_process_drain.qnt').write_text('''module shared_process_drain {
 type State={failed:bool,processFailed:bool,closing:bool,owned:bool,closed:bool,unknown:bool,recovery:bool,exited:bool,policy:int,epoch:int,navigation:int,snapshot:int}
 type Event=Signal|DeliveryError|NativeSettled|StrictRetire|Recovery|Exit|Unknown|LaterIntent|OldEvent
 var s:State
 pure val initial={failed:false,processFailed:false,closing:false,owned:true,closed:false,unknown:false,recovery:false,exited:false,policy:1,epoch:1,navigation:1,snapshot:1}
 pure def earlyRecovery(st:State):State={...st,recovery:true}
 pure def reduce(st:State,e:Event):State=match e {
  | Signal => if(st.exited)st else {...st,failed:true,processFailed:true,closing:if(st.closed)false else true}
  | DeliveryError => if(st.exited)st else {...st,failed:true,closing:if(st.closed)false else true}
  | NativeSettled => if(st.closing and not(st.unknown)){...st,owned:false} else st
  | StrictRetire => if(st.closing and not(st.owned or st.unknown)){...st,closed:true,closing:false} else st
  | Recovery => if(st.processFailed and st.closed and not(st.owned or st.unknown)){...st,recovery:true} else st
  | Exit => if(st.failed and st.closed and not(st.owned or st.unknown)){...st,exited:true} else st
  | Unknown => if(st.closed or st.exited)st else {...st,unknown:true,failed:true,closing:true}
  | LaterIntent => st
  | OldEvent => st
 }
 pure def safe(st:State):bool=all{st.policy==1,st.epoch==1,st.navigation==1,st.snapshot==1,st.closed implies not(st.owned or st.unknown),st.recovery implies (st.processFailed and st.failed and st.closed and not(st.owned or st.unknown)),st.exited implies (st.failed and st.closed and not(st.owned or st.unknown))}
 action init=s'=initial
 action fire(e:Event):bool=s'=reduce(s,e)
 action step={nondet e=Set(Signal,DeliveryError,NativeSettled,StrictRetire,Recovery,Exit,Unknown,LaterIntent,OldEvent).oneOf();fire(e)}
 val safety=safe(s)
}
''')
(root/'spec/shared_process_drain_tests.qnt').write_text('''module shared_process_drain_tests {
 import shared_process_drain.* from "./shared_process_drain"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run originalEarlyRecoveryUnsafe=init.then(fire(Signal)).then(check(not(safe(earlyRecovery(s)))))
 run processSignalRetainsNativeCustody=init.then(fire(Signal)).then(fire(Recovery)).then(check(s.processFailed and s.failed and s.closing and s.owned and not(s.recovery)))
 run deliveryErrorCannotExitKnownCustody=init.then(fire(DeliveryError)).then(fire(Exit)).then(check(s.failed and s.owned and not(s.processFailed or s.exited)))
 run strictClosePrecedesGTKRecovery=init.then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(check(s.closed and s.recovery and not(s.owned)))
 run duplicateSignalsDoNotCancelDrain=init.then(fire(Signal)).then(fire(DeliveryError)).then(fire(Signal)).then(fire(LaterIntent)).then(check(s.failed and s.processFailed and s.closing and s.owned))
 run unknownPreventsRecoveryOrExit=init.then(fire(Signal)).then(fire(Unknown)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(fire(Exit)).then(check(s.unknown and s.owned and not(s.closed or s.recovery or s.exited)))
 run knownFailureOutcomeRetained=init.then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(fire(Exit)).then(check(s.failed and s.processFailed and s.closed and s.exited))
 run noPolicyGrantOrClockReset=init.then(fire(DeliveryError)).then(fire(Signal)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Recovery)).then(check(s.policy==1 and s.epoch==1 and s.navigation==1 and s.snapshot==1))
 run staleEventDoesNotSettle=init.then(fire(Signal)).then(fire(OldEvent)).then(fire(StrictRetire)).then(check(s.owned and not(s.closed)))
}
''')
s=(root/'qa/known-renderer-reload-model.py').read_text().replace('known-renderer-reload','shared-process-drain').replace('known_renderer_reload','shared_process_drain').replace('1410041','1430041').replace('1410042','1430042')
a=s.index("'scope':");b=s.index(",'nativeAcceptance'",a);s=s[:a]+"'scope':"+repr('Bounded shared process failure/duplicate signal/actual delivery error abstraction: original policy/epoch/nav/snapshot preserved, known original Native settlement/strict close BEFORE GTK recovery or original failure exit, explicit Unknown refuses retirement/recovery/replay. NativeSettled projects separately required original physical/journal/confirmation witnesses, not process disappearance or UI inference. Actual failed142/186 and unchanged fresh process oracle required. Not full refinement, whole-host restart/window command journal/durable Unknown/all termination schedules/physical/hardware/full release acceptance.')+s[b:]
(root/'qa/shared-process-drain-model.py').write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'scope':'Fresh GUI143 repairs actual held142/186 shared WebKit death entering GTK recovery before original native realm closure. Owning shared terminated wrapper retains original reason/failure/recovery and known quarantine/native loop; duplicate same-process signals and original evaluation error callback preserve failure without early GTK unwind while original native duties close. Standalone/noncontrolled inherited behavior unchanged. Original strict retire precedes GTK recovery; unretired/uncertain custody explicitly refuses recovery/restart controls. No policy/issuer/grant/epoch/nav/snapshot/clock/reset/replay changes; original recovery UI and expected failure exit stay separate from whole-host restart/durable Unknown/window-command recovery. Full119/new model9/200 then unchanged186 oracle plus original normal/reload/failure/stale/reader regressions. Candidate unaccepted; full release remains open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,d['owner'],str(root.relative_to(r)),['PROGRESS ownGUI143 defers original shared process termination and original delivery-error GTK exit while same known original Native quarantine/input/step/poll/receipts close strict custody BEFORE GTK recovery. Duplicate actual signals preserve sticky failure; uncertainty/unretired forbids recovery/restart. Original failure1/model/issuer/grants/clocks/deadlines unchanged. Full119/model9/200 then unchanged186 actualprocess oracle plus regressions. Whole-host restart/durable Unknown/window commands/physical/full release remain open.'],'progress',[str((root/'ANCESTRY.json').relative_to(r))]))
