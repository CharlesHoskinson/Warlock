"""Own ordered native visual custody and a pure renderer receiver."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v118';root=repo/'implementation/warlock-preview-provider-v119';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['readonlyVisualCPUQualified'] and d['fullBuildCommands']==112 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Native creator/context-owned visual snapshot custody, monotonically issued renderer leases and visual sequence separate from native control ordinals; pure Elm receiver without lifecycle policy. Exact pending retries and latest snapshot acceptance require original policy getter; stale contexts/domain/ack refuse. Actual host activation, DOM/frame/physical concealment and authenticated WebKit callback bindings remain separate gates.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,d['owner'],str(root.relative_to(repo)),['PROGRESS own freshGUI119 native creator/context-owned ordered visual custody and pure Elm renderer receiver. Parent118 held original native207+90+74/lifetime37+15/Quint14/26/430/five guards/backpressure48+28/full112 PUBLIC87 verified. Add native monotonic renderer leases and separate visual sequence; exact pending replay, current-cache comparison before ack, stale context/domain refusal, explicit invalidation/concealment and no second lifecycle policy. Keep original native control ordinals, policy/effects/physical authorities unchanged. First compile/couple C/JSC and pure receiver with ordered/stale/reload cases; actual WebKit context authentication/DOM/frame/physical concealment, host input/ticket custody/retry, uncertain worker and delayed proposal liveness remain open; Native130 legacy actual baseline and full release gates preserved.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
