"""Quarantine known same-URI reload; original strict native drain admits replacement."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v140';root=r/'implementation/warlock-preview-provider-v141'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and not d['passed'] and d['actualRendererReloadCounterexample'] and not root.exists()
for n,row in d['files'].items():assert sha(parent/n)==row['sha256'],n
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/controlled-preview-host.h';s=p.read_text();needle='static gboolean controlled_failure_draining;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic gboolean controlled_reload_retiring;')
needle='    if(controlled_driver && !controlled_retired)controlled_fault(g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Renderer navigation retains original live policy; reload recovery not qualified"));';assert s.count(needle)==1
s=s.replace(needle,'''    if(controlled_driver && !controlled_retired) {
        /* Reload discards renderer authority, never Native custody. Only this
         * trusted document with known duties may keep its original drain loop.
         * Unexpected navigation or uncertain/failing ownership stays fatal. */
        if(controlled_uncertain || controlled_failure_draining ||
           g_strcmp0(webkit_web_view_get_uri(target),"elm-shell://app/controlled-popup.html") ||
           (!controlled_initialized && !controlled_reload_retiring)) {
            controlled_fault(g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Renderer navigation lacks known original reload custody"));return;
        }
        if(controlled_reload_retiring)return; // Later reload cannot cancel retirement.
        controlled_reload_retiring=TRUE;controlled_retiring=TRUE;controlled_initialized=FALSE;
        controlled_paint_cancel();GError *error=NULL;
        if(!controlled_visual ||
           !warlock_visual_channel_invalidate(controlled_visual,G_OBJECT(target),&error) ||
           !warlock_policy_driver_quarantine(controlled_driver,controlled_epoch,&error)) {
            controlled_fault(error);return;
        }
        g_clear_pointer(&controlled_last_visual,g_free);
        g_print("controlled-native-reload-quarantine: epoch=%" G_GUINT64_FORMAT " navigation=%" G_GUINT64_FORMAT " originalNative=1 samePopup=1 inferredSettlement=0\\n",controlled_epoch,controlled_navigation);fflush(stdout);
        /* Original tick/receipts/strict close decide when to replace the view.
         * No grant, epoch, policy, snapshot ordinal or native fact is reset. */
    }''')
needle='    controlled_retired=FALSE;controlled_retiring=FALSE;controlled_initialized=FALSE;';assert s.count(needle)==1;s=s.replace(needle,needle+'controlled_reload_retiring=FALSE;');p.write_text(s)
(root/'spec/known_renderer_reload.qnt').write_text('''module known_renderer_reload {
 type State={owned:bool,closing:bool,closed:bool,unknown:bool,failed:bool,initialized:bool,replaced:bool,dom:bool,epoch:int,policy:int,lease:int,navigation:int,snapshot:int}
 type Event=Reload|NativeSettled|StrictRetire|Replace|DOMReady|Admit|Capture|OldCallback|Unknown|Failure|LaterIntent
 var s:State
 pure val initial={owned:true,closing:false,closed:false,unknown:false,failed:false,initialized:true,replaced:false,dom:true,epoch:1,policy:1,lease:1,navigation:1,snapshot:1}
 pure def legacyReload(st:State):State={...st,unknown:true,failed:true,navigation:st.navigation+1}
 pure def reduce(st:State,e:Event):State=match e {
  | Reload => if(st.closed or st.failed)st else {...st,closing:true,initialized:false,dom:false,navigation:st.navigation+1}
  | NativeSettled => if(st.closing and not(st.unknown)){...st,owned:false} else st
  | StrictRetire => if(st.closing and not(st.owned or st.unknown)){...st,closed:true,closing:false,initialized:false} else st
  | Replace => if(st.closed and not(st.owned or st.unknown or st.failed or st.replaced)){...st,replaced:true,dom:false,navigation:st.navigation+1} else st
  | DOMReady => if(st.replaced and st.closed){...st,dom:true} else st
  | Admit => if(st.closed and st.replaced and st.dom and not(st.unknown or st.failed)){...st,epoch:st.epoch+1,closed:false,owned:true,initialized:true,replaced:false} else st
  | Capture => if(st.initialized and not(st.closed or st.closing or st.unknown or st.failed)){...st,snapshot:st.snapshot+1} else st
  | OldCallback => st
  | LaterIntent => st
  | Unknown => {...st,unknown:true,initialized:false,closing:if(st.closed)false else true}
  | Failure => {...st,failed:true,initialized:false,closing:if(st.closed)false else true}
 }
 pure def safe(st:State):bool=all{st.policy==1,st.lease==1,st.epoch>=1,st.navigation>=st.epoch,st.snapshot>=1,st.closed implies not(st.owned),st.initialized implies not(st.closing or st.closed or st.unknown or st.failed),st.replaced implies (st.closed and not(st.owned))}
 action init=s'=initial
 action fire(e:Event):bool=s'=reduce(s,e)
 action step={nondet e=Set(Reload,NativeSettled,StrictRetire,Replace,DOMReady,Admit,Capture,OldCallback,Unknown,Failure,LaterIntent).oneOf();fire(e)}
 val safety=safe(s)
}
''')
(root/'spec/known_renderer_reload_tests.qnt').write_text('''module known_renderer_reload_tests {
 import known_renderer_reload.* from "./known_renderer_reload"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run legacyReloadBecomesUncertain=init.then(check(legacyReload(s).failed and legacyReload(s).unknown and legacyReload(s).owned))
 run reloadDoesNotSettleOriginalCustody=init.then(fire(Reload)).then(fire(StrictRetire)).then(fire(Replace)).then(check(s.owned and s.closing and not(s.replaced or s.initialized or s.failed)))
 run nativeSettlementPrecedesStrictReplacement=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(check(s.closed and s.replaced and not(s.owned or s.initialized)))
 run freshDOMPrecedesAdmission=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(Admit)).then(check(s.epoch==1 and not(s.initialized)))
 run laterEpochKeepsPolicyAndLease=init.then(fire(Reload)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(DOMReady)).then(fire(Admit)).then(fire(Capture)).then(check(s.epoch==2 and s.policy==1 and s.lease==1 and s.navigation==3 and s.snapshot==2 and s.initialized))
 run staleCallbackHasNoAuthority=init.then(fire(Reload)).then(fire(OldCallback)).then(check(s.owned and s.closing and not(s.initialized)))
 run laterIntentCannotCancelDrain=init.then(fire(Reload)).then(fire(LaterIntent)).then(fire(Reload)).then(check(s.owned and s.closing and s.navigation==3 and not(s.initialized)))
 run unknownPreventsReplacement=init.then(fire(Reload)).then(fire(Unknown)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(fire(DOMReady)).then(fire(Admit)).then(check(s.owned and s.unknown and s.epoch==1 and not(s.initialized or s.closed or s.replaced)))
 run currentFailureCannotRecoverAsSuccess=init.then(fire(Failure)).then(fire(NativeSettled)).then(fire(StrictRetire)).then(fire(Replace)).then(check(s.failed and s.closed and not(s.replaced or s.initialized)))
}
''')
s=(root/'qa/current-failure-drain-model.py').read_text().replace('current-failure-drain','known-renderer-reload').replace('current_failure_drain','known_renderer_reload').replace('==8','==9').replace('namedScenarios=8','namedScenarios=9').replace('1390041','1410041').replace('1390042','1410042')
a=s.index("'scope':");b=s.index(",'nativeAcceptance'",a)
s=s[:a]+"'scope':"+repr('Bounded known same-URI renderer reload abstraction: one original policy and popup lease, strict Native settlement/closure BEFORE renderer replacement and fresh DOM/fixed grant/later epoch, navigation/snapshot chronology, stale callback no authority, sticky retirement and Unknown/failure no reset/replay. NativeSettled is an independently required original physical/journal/confirmation witness, not inferred from UI or this model. Actual failed140/176 and same unchanged native oracle required; no full native refinement, arbitrary/process/uncertain recovery, original deadline/hardware/physical reveal/full release claim.')+s[b:]
(root/'qa/known-renderer-reload-model.py').write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'scope':'Fresh GUI141 repair of actual140/176 reload-as-uncertain failure. Known trusted same-URI initialized current renderer reload cancels visual authority and urgently quarantines original realm, keeping sticky original Native input/step/poll/receipts alive. Only original strict close permits fresh fixed-grant replacement inside same popup/native lease, fresh DOM and later original Native epoch on identical policy. Unexpected navigation/uncertain/failing ownership retain original fault path. Only ephemeral reload state clears after new admission; no original grant/policy/nav/snapshot/clock reset. Full119/new Quint9/200 then unchanged176 reload oracle and original six regressions. Candidate unaccepted; full release open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,d['owner'],str(root.relative_to(r)),['PROGRESS ownGUI141 implements known same-URI reload quarantine and original strict native drain before same-popup fresh DOM/fixed-grant renderer and later original native epoch on identical policy. Held140/176 failure preserved. Unexpected URI/Native uncertainty/failure remain failclosed, no reset/replay/inferred settlement. Full119/model9/200 then unchanged176 actual reload oracle plus original normal/current-error/old-error/rapid/delayed/success regressions. Installed drafts/foreign preserved, full release open.'],'progress',[str((root/'ANCESTRY.json').relative_to(r))]))
