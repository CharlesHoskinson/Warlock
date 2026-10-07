"""Own native readonly current visual custody before ordered renderer activation."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v117';root=repo/'implementation/warlock-preview-provider-v118';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeElmOutboxChecks']==207 and d['fullBuildCommands']==112 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Expose creator-owned readonly copies of the latest successfully processed typed visual projection from the original native-owned Elm worker, without rerunning Elm or re-emitting commands. Refuse absent/closed/uncertain/inflight authority. Preserve original policy, native ordinal/effect/physical gates and held evidence. Ordered renderer channel, authentic host input/ticket custody, WebKit/Core reload and delayed refusal/process recovery remain separate.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,d['owner'],str(root.relative_to(repo)),['PROGRESS own freshGUI118 native readonly current visual custody. Parent117 original native207 plus90 visual comparisons/codec101/display150/current lifetime37/13/backpressure48/Quint8/20/405/three guards/full112 held; PUBLIC86 verified separately. Add creator-owned readonly visual projection copying, with no JS invocation/replayed effects/ticket allocation or model reconstruction. Absent/closed/uncertain/inflight policy refuses; ordinary backpressure does not erase the last successfully committed projection. Next couple getter to actual original C/Native issuer and pure decoder, then owned ordered authenticated projection channel/durable input/ticket custody before real WebKit/Core. All native/full release gates remain open; no installed changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
