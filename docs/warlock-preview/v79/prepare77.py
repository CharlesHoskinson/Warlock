"""Derive the next full provider without modifying held evidence or caches."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v76';t=r/'implementation/warlock-preview-provider-v77'
m=p/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and d['sourceHeld'] and not t.exists()
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() or n=='current-build.json']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':hashlib.sha256(m.read_bytes()).hexdigest(),'purpose':'Explicit new unissued enrollment after native expiry and a strictly later picker publication and lease. Preserve original same-intent behavior, native request floors and issued physical ownership; retain bounded predecessor correlation. Full original release gates remain open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS public56 verified498df7d; fresh77 source assigned for explicit later unissued enrollment after expiry. New identity requires later publication AND lease; polling cannot renew. Preserve one Elm authority, previous cutoff, native floors, original receiver/receipt/physical ownership and all original gates. Next implement fullC/host contract, compile, selected Quint plus actualC/Elm evidence, serialized native GUI.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]))
