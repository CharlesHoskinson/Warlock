"""Derive next full GUI for explicit expired unissued resume succession."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v80';t=r/'implementation/warlock-preview-provider-v81';m=p/'component-manifest.json';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
d=json.loads(m.read_text());assert d['passed'] and d['sourceHeld'] and not t.exists()
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Explicit later expired unissued resume intent after exact old-job physical retirement, preserving original job and Broker request floor. Keep one predecessor, fresh native identity/clock/observation and strict later picker stamps, same native two-second cutoff. All original release gates remain open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS public57 verified5d78ac5 fullGUI80/native116 2433/274 normal/all2423stable114 retained, receiptscommitted50f5e23. Fresh81 assigned for explicit expired unissued resume succession after original proof retirement; never reset native/Elm request floors or original-job identity. Next actualC/host code, compile, selected coupled models/CElm/native qualification. All original fullreleasegatesactive.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]))
