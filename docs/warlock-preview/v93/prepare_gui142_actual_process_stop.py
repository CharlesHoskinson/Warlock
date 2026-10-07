"""Actual shared WebKit process stop; retain original fatal/recovery behavior."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v141';root=r/'implementation/warlock-preview-provider-v142';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['actualKnownRendererReloadQualified'] and not root.exists()
for n,row in d['files'].items():assert sha(parent/n)==row['sha256'],n
docs=pathlib.Path(__file__).parent
p=docs/'NATIVE-ADMISSION-CONTROLS.md';s=p.read_text();assert 'CONTROL-047 shared renderer process failure' not in s
p.write_text(s+'''\nCONTROL-047 shared renderer process failure (EARS): WHEN an actual shared
WebKit renderer process terminates while the original native preview duties
remain known, the host SHALL invalidate/conceal renderer authority, retain the
failure outcome and original policy/binding/counters, quarantine the original
realm and continue its original native receipt/retirement progress. BEFORE
showing recovery controls or offering a restart that could discard that realm,
the host SHALL obtain original strict native policy/physical/ticket/journal/
confirmation close and empty custody. A WebKit termination signal, disposal or
new process SHALL NOT certify settlement or reset/replay Unknown. IF original
custody becomes uncertain, strict retirement/restart SHALL remain refused with
explicit uncertainty. Recovery after that drain and original window-command
journal/Unknown preservation SHALL qualify separately on one coherent tuple;
known preview drain alone is not whole shared-host recovery acceptance.
Original observer/operation deadlines and failed evidence SHALL remain.
''')
p=r/'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md';p.write_text(p.read_text()+'''
### Requirement: Shared renderer termination preserves native custody before recovery
Actual shared renderer process termination SHALL retain its failure and original
native custody. Known preview duties SHALL drain through original native receipts
and strict close before GTK recovery/restart controls. Native uncertainty SHALL
prevent normal retirement/restart; process disappearance SHALL NOT infer settlement.

#### Scenario: Actual shared WebKit process termination after current capture
- GIVEN one original captured image and first actual snapshot with native duties known
- WHEN the actual WebKit terminate-process API delivers the original termination signal
- THEN renderer authority is invalidated and the original realm urgently quarantined
- AND original native receipts and independent physical/journal/confirmation gates close custody before GTK recovery controls
- AND failure remains failure with no policy/grant/navigation/snapshot/deadline reset or inferred settlement
- AND whole-host restart, outstanding window commands and durable Unknown qualify separately

#### Scenario: Uncertain native duties at shared process failure
- WHEN original native custody is uncertain at renderer termination
- THEN strict retirement and restart remain refused and Unknown is retained without automatic replay
''')
p=r/'openspec/changes/warlock-preview-actor-retirement/tasks.md';p.write_text(p.read_text()+'''\n- [ ] Implement/qualify CONTROL-047 actual shared WebKit process stop after current
  capture: original known preview duty drain/strict close before GTK recovery,
  original failure/identity/clock/no-reset/no-replay retained. Whole-host restart,
  window-command journal/Unknown and uncertainty remain separate required gates.
''')
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/shared-host.c';s=p.read_text();needle='static gboolean qa_controlled_reload;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic gboolean qa_controlled_process_stop;')
needle='        else if (g_str_equal(argv[i],"--qa-preview-renderer-reload")) qa_controlled_reload=TRUE;';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        else if (g_str_equal(argv[i],"--qa-preview-renderer-process-stop")) qa_controlled_process_stop=TRUE;')
needle='    if(qa_controlled_reload && (';assert s.count(needle)==1;s=s.replace(needle,'    if(qa_controlled_process_stop && (!qa_controlled_preview || !qa_exit || !qa_stay || !qa_client_snapshot || qa_controlled_reload || qa_controlled_delayed_snapshot || qa_controlled_cancelled_snapshot || qa_controlled_reader_path || qa_reader_path || qa_icon_reader_path)) {g_printerr("Renderer process stop requires separate explicit controlled private qualification\\n");return 2;}\n'+needle)
needle='g_signal_connect(popup_view,"load-changed",G_CALLBACK(controlled_load_changed),NULL);';assert s.count(needle)==1;s=s.replace(needle,needle+'if(qa_controlled_process_stop)g_signal_connect(popup_view,"web-process-terminated",G_CALLBACK(controlled_qa_process_terminated),NULL);');p.write_text(s)
p=root/'native/controlled-preview-host.h';s=p.read_text();needle='static gboolean controlled_qa_reload_requested;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic gboolean controlled_qa_process_stop_requested;')
needle='static void controlled_load_changed(';assert s.count(needle)==1;s=s.replace(needle,'''static void controlled_qa_process_terminated(WebKitWebView *target,WebKitWebProcessTerminationReason reason,gpointer unused) {
    (void)unused;
    if(qa_controlled_process_stop && target==popup_view) {
        g_print("controlled-native-qa-process-terminated: epoch=%" G_GUINT64_FORMAT " currentView=1 reason=%d actualWebKitSignal=1 nativeSettlement=0\\n",controlled_epoch,reason);fflush(stdout);
    }
}
'''+needle)
needle='    if(controlled_retiring && !controlled_retire_current(&error))goto uncertain;';assert s.count(needle)==1;s=s.replace(needle,'''    if(qa_controlled_process_stop && !controlled_qa_process_stop_requested && controlled_epoch==1 && controlled_initialized && !controlled_retiring && controlled_snapshot_written_epoch==controlled_epoch) {
        /* Explicit private QA only, after original snapshot finish/write.
         * Actual shared WebKit process API; never synthesize a signal, native
         * grant, receipt, closure or settlement. Original handlers decide. */
        controlled_qa_process_stop_requested=TRUE;
        g_print("controlled-native-qa-process-stop-requested: epoch=%" G_GUINT64_FORMAT " navigation=%" G_GUINT64_FORMAT " actualTerminateWebProcess=1 snapshotWritten=1 nativeSettlement=0\\n",controlled_epoch,controlled_navigation);fflush(stdout);
        webkit_web_view_terminate_web_process(popup_view);
    }
'''+needle);p.write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'scope':'Fresh GUI142 adds disabled-by-default separate private actual WebKit terminate-web-process stimulus only after original first current snapshot/write. Original shared related-view process topology, terminated callback, fatal GTK unwind/recovery and strict Native teardown unchanged to expose drain-before-recovery gap. Readonly original popup termination reason observation never manufactures native settlement. Full119 then unchanged normal and actual process-stop strict custody-before-GTK-recovery oracle on original core16/plugin19/AQ155/deadlines. No issuer/Elm policy/grant/reset/replay/installed changes. Candidate unaccepted; full shared-host recovery/release open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,d['owner'],str(root.relative_to(r)),['PROGRESS ownGUI142 actual shared WebKit process stop after current captured snapshot, original fatal/recovery/strict Native refusal preserved. Readonly real signal/reason, no synthetic process/native fact. Full119 then actual process/custody-before-GTK recovery oracle and original normal route. CONTROL047 EARS/OpenSpec original-clock/failure/no-reset/no-replay; full shared-host recovery/Unknown/window command/physical/release remains open.'],'progress',[str((root/'ANCESTRY.json').relative_to(r))]))
