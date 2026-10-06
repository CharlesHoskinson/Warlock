"""Fresh source for cross-window asynchronous retirement and trusted native routing."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v88';t=r/'implementation/warlock-preview-provider-v89';assert not t.exists()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
m=p/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and d['sourceHeld']
for rel,row in d['files'].items():assert sha(p/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Independent incoming native retirement observations/completions across actors: per-actor exact settlement, permanent evidence and native-clock anti-replay cutoff without invented global event order. Then trusted native observation/readiness/completion routing with retained completion delivery before continuing full native/Elm >256 turnover.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS Native125 preflight passed currentGUI88/core16/plugin18; serialized native65582 confirmed live on launch. Fresh GUI89 exercises independently queued per-window retirement observations/final facts without a global event order. Keep source-clock cutoff monotone while allowing exact delayed sibling completion; then native gateway/routing and retained completion delivery, actual continuing >256 native/Elm and all original release gates.'],'progress',[str((t/'ANCESTRY.json').relative_to(r)),str(m.relative_to(r))]))
