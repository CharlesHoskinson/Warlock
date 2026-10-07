"""Actual WebKit reload QA stimulus; preserve original unqualified reload path."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v139';root=r/'implementation/warlock-preview-provider-v140';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['gracefulCurrentFailureDrainQualified'] and not root.exists()
for n,row in d['files'].items():assert sha(parent/n)==row['sha256'],n
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/shared-host.c';s=p.read_text();needle='static gboolean qa_controlled_current_cancelled_snapshot;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic gboolean qa_controlled_reload;')
needle='        else if (g_str_equal(argv[i],"--qa-preview-current-cancelled-snapshot")) {qa_controlled_current_cancelled_snapshot=TRUE;qa_controlled_cancelled_snapshot=TRUE;}';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        else if (g_str_equal(argv[i],"--qa-preview-renderer-reload")) qa_controlled_reload=TRUE;')
needle='    if (!asset_dir || !authority_config || !backend_path || !gtk_init_check(NULL,NULL)';assert s.count(needle)==1;s=s.replace(needle,'    if(qa_controlled_reload && (!qa_controlled_preview || !qa_exit || !qa_stay || !qa_client_snapshot || qa_controlled_delayed_snapshot || qa_controlled_cancelled_snapshot || qa_controlled_reader_path || qa_reader_path || qa_icon_reader_path)) {g_printerr("Renderer reload requires separate explicit controlled private qualification\\n");return 2;}\n'+needle);p.write_text(s)
p=root/'native/controlled-preview-host.h';s=p.read_text();needle='static gboolean controlled_failure_draining;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic gboolean controlled_qa_reload_requested;')
needle='    controlled_navigation++;';assert s.count(needle)==1;s=s.replace(needle,needle+'''\n    if(qa_controlled_reload && controlled_driver && !controlled_retired) {
        g_print("controlled-native-qa-reload-start: epoch=%" G_GUINT64_FORMAT " navigation=%" G_GUINT64_FORMAT " initialized=%d sameView=1 actualLoadStarted=1 uri=%s inferredSettlement=0\\n",controlled_epoch,controlled_navigation,controlled_initialized,webkit_web_view_get_uri(target));fflush(stdout);
    }''')
needle='    if(controlled_retiring && !controlled_retire_current(&error))goto uncertain;';assert s.count(needle)==1;s=s.replace(needle,'''    if(qa_controlled_reload && !controlled_qa_reload_requested && controlled_epoch==1 && controlled_initialized && !controlled_retiring && controlled_snapshot_written_epoch==controlled_epoch) {
        /* Explicit private QA only. First real snapshot is already consumed and
         * written; invoke the actual WebKit API, never manufacture a load event,
         * grant, native receipt, epoch or completion. Original handler decides. */
        controlled_qa_reload_requested=TRUE;
        g_print("controlled-native-qa-reload-requested: epoch=%" G_GUINT64_FORMAT " navigation=%" G_GUINT64_FORMAT " actualWebKitReload=1 snapshotWritten=1 inferredSettlement=0\\n",controlled_epoch,controlled_navigation);fflush(stdout);
        webkit_web_view_reload(popup_view);
    }
'''+needle);p.write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'scope':'Fresh GUI140 explicitly gated private actual webkit_web_view_reload after original first actual current snapshot/write/Native projection. Original reload handler increments navigation then marks current live driver uncertain and exits; unchanged to expose actual recovery gap. Readonly actual request/load-start observations never manufacture native facts/results/grants/settlement. Full119 then original normal route and real same-popup reload recovery oracle on original core16/plugin19/AQ155/deadline6. Single policy/issuer/physical/retirement/counters unchanged; candidate not accepted for reload/full release.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,d['owner'],str(root.relative_to(r)),['PROGRESS ownGUI140 actual WebKit reload after first current actual snapshot written, original current navigation/uncertain/failure path unchanged. Real LoadStarted observation/no fabricated event/grant/native settlement. Full119/original normal and same-popup strict close/fresh fixed-grant/same-policy epoch/current-image reload oracle next; original clocks/deadlines/core16/plugin19/AQ155 unchanged, full release/installed drafts foreign preserved.'],'progress',[str((root/'ANCESTRY.json').relative_to(r))]))
