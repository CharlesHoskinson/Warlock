"""Reject completed old renderer scope before applying its error to current GUI."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v136';root=r/'implementation/warlock-preview-provider-v137';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and not d['passed'] and d['actualCancelledOldResultCounterexample'] and not root.exists()
for n,row in d['files'].items():assert sha(parent/n)==row['sha256'],n
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/shared-host.c';s=p.read_text();old='''    if(!image) {client_snapshot_free(snapshot);client_failure(error);return;}
    if(snapshot->controlled_visual && !controlled_snapshot_matches(snapshot,object)) {
        cairo_surface_destroy(image);client_snapshot_free(snapshot);
        g_print("controlled-native-snapshot-refused: currentProjection=0 hardwarePresentation=0\\n");fflush(stdout);return;
    }''';new='''    /* Finish consumes the original result once. Only the original current
     * renderer scope may report an error against this GUI; a retired result
     * owns its own image/error, never the current policy or native jobs. */
    if(snapshot->controlled_visual && !controlled_snapshot_matches(snapshot,object)) {
        if(image)cairo_surface_destroy(image);
        g_clear_error(&error);client_snapshot_free(snapshot);
        g_print("controlled-native-snapshot-refused: currentProjection=0 hardwarePresentation=0\\n");fflush(stdout);return;
    }
    if(!image) {client_snapshot_free(snapshot);client_failure(error);return;}'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'scope':'Fresh GUI137 fixes actual held136/Native159 canceled old-result counterexample. Original finish once; original full controlled view/epoch/navigation/projection/current-channel guard precedes current failure reporting. Disposes only old result image if present and its original GError; matching-current errors retain original client_failure and strict native custody. No native issuer/single Elm policy/physical product/grant/deadline/reset/producer/QA oracle changes. Full119, model10/200 and unchanged actual native oracle/regressions next.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,d['owner'],str(root.relative_to(r)),['PROGRESS ownGUI137 original current renderer scope guard before reporting completion error fixes actual old canceled result shutdown; original finish once/NULL-image-safe old-error disposal/no native settlement, matching-current errors retain original failclosed. Next full119/Quint10/200/unchanged actual canceled oracle and normal/success/delayed/rapid controls; full release open/installed drafts foreign preserved.'],'progress',[str((root/'ANCESTRY.json').relative_to(r))]))
