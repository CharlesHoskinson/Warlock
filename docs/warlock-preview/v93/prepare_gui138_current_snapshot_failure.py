"""Expose a real matching-current WebKit cancellation through original failure."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v137';root=r/'implementation/warlock-preview-provider-v138';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['actualCancelledOldResultQualified'] and not d['currentMatchingErrorNativeQualified'] and not root.exists()
for n,row in d['files'].items():assert sha(parent/n)==row['sha256'],n
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/shared-host.c';s=p.read_text();needle='static gboolean qa_controlled_cancelled_snapshot;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic gboolean qa_controlled_current_cancelled_snapshot;')
needle='        else if (g_str_equal(argv[i],"--qa-preview-cancelled-reopened-snapshot")) {qa_controlled_delayed_snapshot=TRUE;qa_controlled_reopened_snapshot=TRUE;qa_controlled_cancelled_snapshot=TRUE;}';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        else if (g_str_equal(argv[i],"--qa-preview-current-cancelled-snapshot")) {qa_controlled_current_cancelled_snapshot=TRUE;qa_controlled_cancelled_snapshot=TRUE;}')
needle='    if(qa_controlled_delayed_snapshot && (!qa_controlled_preview || !qa_exit || !qa_stay || !qa_client_snapshot))';assert s.count(needle)==1;s=s.replace(needle,'    if((qa_controlled_delayed_snapshot || qa_controlled_current_cancelled_snapshot) && (!qa_controlled_preview || !qa_exit || !qa_stay || !qa_client_snapshot))')
needle='    if(qa_controlled_reader_path && (!qa_controlled_preview || !qa_exit || !qa_stay || !qa_client_snapshot || qa_controlled_delayed_snapshot || qa_reader_path';assert s.count(needle)==1;s=s.replace(needle,'    if(qa_controlled_reader_path && (!qa_controlled_preview || !qa_exit || !qa_stay || !qa_client_snapshot || qa_controlled_delayed_snapshot || qa_controlled_current_cancelled_snapshot || qa_reader_path')
needle='    if (!asset_dir || !authority_config || !backend_path || !gtk_init_check(NULL,NULL)';assert s.count(needle)==1;s=s.replace(needle,'    if(qa_controlled_current_cancelled_snapshot && qa_controlled_delayed_snapshot) {g_printerr("Current cancellation cannot retain an old result\\n");return 2;}\n'+needle)
needle='    if(!image) {client_snapshot_free(snapshot);client_failure(error);return;}';assert s.count(needle)==1;s=s.replace(needle,'''    if(!image) {
        if(qa_controlled_current_cancelled_snapshot && snapshot->controlled_visual) {
            /* Readonly QA observation after the original matching-scope guard.
             * No synthetic error/result, authority, settlement or graceful exit. */
            g_print("controlled-native-current-snapshot-error: scopeCurrent=1 actualCancelled=%d originalFinishCalls=1 nativeSettlement=0\\n",g_error_matches(error,G_IO_ERROR,G_IO_ERROR_CANCELLED));fflush(stdout);
        }
        client_snapshot_free(snapshot);client_failure(error);return;
    }''');p.write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'scope':'Fresh GUI138 adds explicitly gated private current-snapshot cancellation stimulus using original actual canceled GCancellable/WebKit operation with delayed retention disabled. Readonly observation only after original current-scope guard, original failure/strict custody paths retained. Original real finish once/old guard/issuer/single policy/physical products/deadlines unchanged. Full119 then separate actual current-error negative control, unchanged normal and canceled-old-result regressions. Current-error negative host1 must never become normal-exit or graceful-drain acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,d['owner'],str(root.relative_to(r)),['PROGRESS ownGUI138 real current matching WebKit cancellation/no old-result hold, readonly post-original-scope-guard observation and original client_failure/strict native custody unchanged. Full119 then actual expected host1 negative control plus unchanged normal/old-canceled regressions; never classify failure as normal drain/recovery. Full release/physical/recovery/workload gates remain; installed drafts foreign preserved.'],'progress',[str((root/'ANCESTRY.json').relative_to(r))]))
