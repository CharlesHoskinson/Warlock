"""Fresh QA-only real original reader stimulus; preserve GUI132 runtime policy."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v132';root=r/'implementation/warlock-preview-provider-v133';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['actualGUIRealmReopenQualified'] and not root.exists()
for n,row in d['files'].items():assert sha(parent/n)==row['sha256'],n

def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/shared-host.c';s=p.read_text();needle='static gboolean qa_controlled_delayed_snapshot;';assert s.count(needle)==1;s=s.replace(needle,needle+'\nstatic const char *qa_controlled_reader_path;')
needle='        else if (g_str_equal(argv[i],"--qa-preview-delayed-snapshot")) qa_controlled_delayed_snapshot=TRUE;';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        else if (g_str_equal(argv[i],"--qa-controlled-preview-reader") && i+1<argc) qa_controlled_reader_path=argv[++i];')
needle='    if(qa_controlled_delayed_snapshot && ';i=s.index(needle);s=s[:i]+'    if(qa_controlled_reader_path && (!qa_controlled_preview || !qa_exit || !qa_stay || !qa_client_snapshot || qa_controlled_delayed_snapshot || qa_reader_path || qa_icon_reader_path || qa_reader_control(qa_controlled_reader_path)!=QA_READER_HOLD)) {g_printerr("Controlled reader requires explicit private qualification and original hold file\\n");return 2;}\n'+s[i:];p.write_text(s)
p=root/'native/controlled-preview-host.h';s=p.read_text();needle='static char *controlled_last_private_status;';assert s.count(needle)==1
code='''
/* Explicit QA-only actual original URI reader. It supplies no Native fact,
 * ticket, grant or settlement. The original GIO reader itself keeps physical
 * custody until the private monotonic release stimulus closes that reader. */
static GInputStream *controlled_held_reader;
static char *controlled_held_uri;
static gboolean controlled_reader_probed,controlled_reader_released;
static gboolean controlled_reader_hold(GError **error) {
    if(!qa_controlled_reader_path || controlled_held_reader || controlled_reader_released)return TRUE;
    if(qa_reader_control(qa_controlled_reader_path)!=QA_READER_HOLD) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Original controlled reader hold stimulus required");return FALSE;
    }
    g_autofree char *identity=g_strdup_printf("family:%" G_GUINT64_FORMAT,qa_import_subjects[0]);
    g_autofree char *uri=NULL;gsize length=0;guint8 first=0;
    if(!warlock_imported_clients_uri(imported_clients,identity,&uri,error) || !uri || !*uri)return FALSE;
    controlled_held_reader=preview_uri_router_open(controlled_router,popup_view,uri,&length,error);
    if(!controlled_held_reader)return FALSE;
    controlled_held_uri=g_strdup(uri);
    if(g_input_stream_read(controlled_held_reader,&first,1,NULL,error)!=1 || first!=137) {
        if(!error || !*error){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Original controlled PNG reader byte required");}
        return FALSE;
    }
    g_print("controlled-native-reader-held: epoch=%" G_GUINT64_FORMAT " actualGIO=1 firstByte=%u bytes=%zu physicalSettlement=0\\n",controlled_epoch,first,length);fflush(stdout);return TRUE;
}
static gboolean controlled_reader_tick(GError **error) {
    if(!controlled_held_reader)return TRUE;
    QAReaderControl control=qa_reader_control(qa_controlled_reader_path);
    if(control==QA_READER_INVALID || (control==QA_READER_HOLD && controlled_reader_probed) || (control==QA_READER_RELEASE && !controlled_reader_probed)) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Original controlled reader monotonic stimulus required");return FALSE;
    }
    if(control==QA_READER_PROBE && !controlled_reader_probed) {
        GError *held_error=NULL,*fresh_error=NULL;guint8 byte=0;gsize length=0;
        gssize read=g_input_stream_read(controlled_held_reader,&byte,1,NULL,&held_error);
        GInputStream *fresh=preview_uri_router_open(controlled_router,popup_view,controlled_held_uri,&length,&fresh_error);
        const gboolean held_denied=read==-1 && g_error_matches(held_error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED);
        const gboolean fresh_denied=!fresh && g_error_matches(fresh_error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED);
        g_clear_error(&held_error);g_clear_error(&fresh_error);
        if(fresh){g_input_stream_close(fresh,NULL,NULL);g_object_unref(fresh);}
        controlled_reader_probed=TRUE;
        g_print("controlled-native-reader-probed: epoch=%" G_GUINT64_FORMAT " heldRead=%zd heldDenied=%d freshDenied=%d actualGIO=1 physicalSettlement=0\\n",controlled_epoch,read,held_denied,fresh_denied);fflush(stdout);
    }
    if(control==QA_READER_RELEASE) {
        if(!g_input_stream_close(controlled_held_reader,NULL,error))return FALSE;
        g_clear_object(&controlled_held_reader);controlled_reader_released=TRUE;g_clear_pointer(&controlled_held_uri,g_free);
        g_print("controlled-native-reader-released: epoch=%" G_GUINT64_FORMAT " originalCloseCalls=1 nativeGrantReset=0\\n",controlled_epoch);fflush(stdout);
    }
    return TRUE;
}
'''
s=s.replace(needle,needle+'\n'+code)
needle='        if(policy && warlock_visual_channel_current(controlled_visual,policy,G_OBJECT(popup_view),&error))imported_image_report(object);';assert s.count(needle)==1
s=s.replace(needle,'        if(policy && warlock_visual_channel_current(controlled_visual,policy,G_OBJECT(popup_view),&error) && imported_image_report(object) && !controlled_reader_hold(&error)) {controlled_fault(error);return TRUE;}')
needle='    if(!controlled_produce(&error))goto uncertain;';assert s.count(needle)==1;s=s.replace(needle,'    if(!controlled_reader_tick(&error) || !controlled_produce(&error))goto uncertain;')
needle='    if(controlled_uncertain || !g_queue_is_empty(&controlled_pending)) {';assert s.count(needle)==1;s=s.replace(needle,'    if(controlled_held_reader || controlled_uncertain || !g_queue_is_empty(&controlled_pending)) {')
needle='    g_print("controlled-renderer-context-replaced: retiredEpoch=';i=s.index(needle);s=s[:i]+'    g_print("controlled-native-replacement-admission: retiredEpoch=%" G_GUINT64_FORMAT " pendingPopup=%d publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT " freshDOMRequired=1\\n",controlled_epoch,parent!=NULL,surface_gate.publication,surface_gate.lease);fflush(stdout);\n'+s[i:];p.write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'scope':'Fresh GUI133 preserves original GUI132 host producer/policy/Native gates. Adds explicit disabled-by-default QA-only original URI/GIO reader hold->probe->release and actual pending-parent replacement observation. Native GIO reader retains physical duty; no simulated grant/fact/effect/settlement or deadline extension. Full119 then unchanged normal controls and actual pending-intent probe must expose existing behavior before any production fix.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS own fresh GUI133 from held132: disabled-by-default QA-only original native-authorized URI/GIO reader retained across actual popup close/new intent. Original router/reader keeps actual physical closure duty; native old grant/policy/producer/deadlines unchanged. Secure original hold->probe->release stimulus observes denied old/fresh reads then original one close; actual parent/lease proof at renderer replacement. Full119 and native unchanged29/13 then pending-intent original deadline test next; no production fix until counterexample. Full release/physical reveal/recovery/resource remain open; installed/drafts/foreign preserved.'],'progress',[str((root/'ANCESTRY.json').relative_to(r))]))
