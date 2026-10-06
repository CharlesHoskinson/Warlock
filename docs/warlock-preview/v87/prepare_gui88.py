"""Preserve GUI87 failure and create fresh GUI88 with retirement/control fixes."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v87';t=r/'implementation/warlock-preview-provider-v88';assert not t.exists()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
build=next(p.glob('qa/build-*/report.json'));b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==95
failed=next(p.glob('qa/elm-retirement-check-*/report.json'));f=json.loads(failed.read_text());assert not f['passed'] and 'After readiness, duplicate terminal' in f['error']
for rel,value in b['inputs'].items():assert sha(p/rel)==value,rel
for rel,value in f['inputs'].items():assert sha(pathlib.Path(rel))==value,rel
for rel,value in f['artifacts'].items():assert sha(failed.parent/rel)==value,rel
files={}
for source in sorted(p.rglob('*')):
 rel=source.relative_to(p)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not source.is_symlink(),source
 if source.is_file():files[str(rel)]={'kind':'file','sha256':sha(source),'size':source.stat().st_size,'mode':oct(stat.S_IMODE(source.stat().st_mode))}
manifest=p/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':False,'sourceHeld':True,'buildReport':str(build),'failedRetirementReport':str(failed),'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual full optimized GUI/native build95 passed. New compiled Elm retirement replay failed: duplicate terminal ACK emitted after readiness. Preserve this failure; accepted cache also requires permanent retirement release. Native/control/turnover unqualified.'},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(manifest),'purpose':'Fix retained failed Elm retirement duplicate ACK after readiness, immediately retire accepted packets without expiry, add original-popup explicit control continuity before native removal activation. All original gates remain.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
source=t/'src/PreviewLifecycle.elm';s=source.read_text().replace('idle, settled)','idle, settled, retire)')
s+='\n\n-- Permanent native retirement relinquishes historical pixels immediately.\n-- Physical owners and known jobs remain until exact terminal receipts.\nretire : Model -> (Model,List Command)\nretire (Model initial) =\n    let final = {state=initial,effects=[]} |> revoke |> mapState (\\st -> {st | demand=False})\n    in (Model final.state,final.effects)\n'
source.write_text(s)
source=t/'src/PreviewPresenter.elm';s=source.read_text()
old='let (closed,commands) = closeEntry entry\n                            pending ='
new='let (closed,commands) = retireEntry entry\n                            pending ='
assert s.count(old)==1;s=s.replace(old,new)
old='if not (eventOwns identity wire && familyFrameOwns entry.source wire)';assert s.count(old)==1
s=s.replace(old,'if entry.readySent || not (eventOwns identity wire && familyFrameOwns entry.source wire)')
position=s.index('outcomeDecoder :')
helper='retireEntry : Entry -> (Entry,List Preview.Command)\nretireEntry entry =\n    case entry.model of\n        Nothing -> ({entry | stamp=Nothing,local=Nothing},[])\n        Just lifecycle ->\n            let (retiring,commands) = Preview.retire lifecycle\n            in ({entry | model=Just retiring,stamp=Nothing,local=Nothing},commands)\n\n'
s=s[:position]+helper+s[position:];source.write_text(s)
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS heldGUI86 full95/original12/C96/decoder13-25-439states-3mutants/aggregate9068CPUthrough280 subjects. HeldfailedGUI87: duplicate terminal ACK after readiness exposed by actual compiled replay. FreshGUI88 fixes no further controls afterReady and permanent accepted packet release; explicit per-popup control continuity/typed host completion and full-native turnover next. Preserve exact journal/physical/clock/deadline gates.'],'progress',[str(manifest.relative_to(r)),str((t/'ANCESTRY.json').relative_to(r))]))
