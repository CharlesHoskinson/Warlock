"""Prioritize current unissued demand in a fresh full GUI derivative."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v79';t=r/'implementation/warlock-preview-provider-v80';m=p/'component-manifest.json';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
d=json.loads(m.read_text());assert d['passed'] and d['sourceHeld'] and not t.exists()
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
f=t/'native/shared-host.c';s=f.read_text();start=s.index('static gboolean imported_poll(gpointer unused)');end=s.index('static void imported_wake',start);phase=s[start:end]
old='    for(guint i=0;i<qa_import_count;i++) {'
assert phase.count(old)==1
new='''    /* Current unissued subjects get the next physically available slot before
     * old actors resume. This changes scheduling order only: exact picker,
     * native scope, cutoff, Broker limits and proof obligations remain below. */
    guint order[3],ordered=0;
    for(guint pass=0;pass<(qa_import_dynamic?2U:1U);pass++) {
        for(guint i=0;i<qa_import_count;i++) {
            if(qa_import_dynamic) {
                g_autofree char *identity=g_strdup_printf("family:%" G_GUINT64_FORMAT,qa_import_subjects[i]);
                const gboolean unissued=!warlock_imported_clients_lease(imported_clients,identity);
                if(unissued!=(pass==0))continue;
            }
            order[ordered++]=i;
        }
    }
    g_assert(ordered==qa_import_count);
    for(guint position=0;position<ordered;position++) {
        const guint i=order[position];'''
phase=phase.replace(old,new);s=s[:start]+phase+s[end:];f.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Unchanged explicit successor core and immutable Elm; full dynamic GTK host visits unissued subjects before resuming issued actors. Same current picker validation, native cutoff, receiver, two-item pool and terminal ownership. Actual native third image after expiry/reopen remains mandatory.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS79 successor full95/new10/22/C45Elm21/originalallchecksheld. Fresh80 fullhost schedules unissued currentpicker subjects before oldactorresume, preserving legacyfixedtwo ordering and all ownership/cutoff guards. Nextfull80compile/currentmodels then serialize native115 actualexpiry/reopen/thirdimage +alloriginal114 controls. Fullreleaseacceptance remainsfalse.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]))
