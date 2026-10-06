"""Hold failed90 close barrier; derive91 without discarding any evidence."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v90';t=r/'implementation/warlock-preview-provider-v91'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
build=next(p.glob('qa/build-*/report.json'));b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==95
for rel,h in b['inputs'].items():assert sha(p/rel)==h,rel
failure=next(p.glob('qa/actor-retirement-channel-check-v1-*/report.json'));d=json.loads(failure.read_text())
assert not d['passed'] and 'UnconfirmedRetirementCompletionMustPreventNativeOwnerClose' in d['error']
assert [(v['name'],v['exitCode']) for v in d['commands'] if v['exitCode']!=0]==[('short',2)]
for rel,h in d['inputs'].items():assert sha(p/rel)==h,rel
for rel,h in d['artifacts'].items():assert sha(failure.parent/rel)==h,rel
assert not (p/'component-manifest.json').exists() and not t.exists()
files={}
for path in sorted(p.rglob('*')):
 rel=path.relative_to(p)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not path.is_symlink(),path
 if path.is_file():files[str(rel)]={'kind':'file','sha256':sha(path),'size':path.stat().st_size,'mode':oct(stat.S_IMODE(path.stat().st_mode))}
manifest=p/'component-manifest.json'
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'buildReport':str(build),'retainedCompletionCloseFailure':str(failure),'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Full95 build passed new native C retention/readiness/final-delivery API. Actual C/socket synthetic retirement passes original physical/ACK/receiver gates and exposes owner-close discarding its last unacknowledged completion; this failed source is held. Historical standalone report inputs remain tied to their own snapshots, never substituted for current integration evidence.'},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
source=t/'native/imported-clients.cpp';s=source.read_text()
old='extern "C" gboolean warlock_imported_clients_empty(WarlockImportedClients* owner){return owner && owner->value.empty();}'
new='extern "C" gboolean warlock_imported_clients_empty(WarlockImportedClients* owner){return owner && owner->thread==g_thread_self() && owner->value.empty() && (!owner->retirementJournal || owner->retirementJournal->size()==0);}'
assert s.count(old)==1;s=s.replace(old,new)
old='try {require(owner->value.empty(),"Outstanding shared imported physical or journal ownership");'
new='try {require(owner->thread==g_thread_self() && owner->value.empty() && (!owner->retirementJournal || owner->retirementJournal->size()==0),"Outstanding shared imported physical, proof or retirement delivery ownership");'
assert s.count(old)==1;s=s.replace(old,new);source.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(manifest),'purpose':'Fix real C/socket pending-completion owner-close loss: empty and close retain observation/completion transport records until original processing ACK, without changing physical or original terminal-proof gates. Next actual native/Elm transport and host routing.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS held qualifiedGUI89/native126/core16/plugin18 PASS2465/277normalclean/all2457prior125fixed and async10/30/641/3model+3compiledElm mutants. GUI90 full95 compiled new C/native retirement journal pipeline; actualC/socket close discarded unacknowledged final completion. Heldfailed90 and fresh91 empty/close transport barrier fix. Compile current91 and rerun original physical/receipt/neighbor/control oracles; add unissued zero-floor native/C case; actual Elm delivery wrappers/host activation and all original release/turnover/capture gates remain.'],'progress',[str(manifest.relative_to(r)),str((t/'ANCESTRY.json').relative_to(r))]))
