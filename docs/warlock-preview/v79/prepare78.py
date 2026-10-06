"""Retain missing-cache preflight failure and restore the exact held toolchain."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v77';t=r/'implementation/warlock-preview-provider-v78';original=r/'implementation/warlock-preview-provider-v76'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert not t.exists() and not (p/'component-manifest.json').exists()
failure={'passed':False,'stage':'held-toolchain-preflight','error':'Fresh77 preparation omitted qa/toolchain directory. Full build refused changed toolchain inventory before compiling. Fresh78 restores exact held76 toolchain; production and all QA/oracles remain unchanged.','nativeAcceptance':False,'fullReleaseAccepted':False}
(p/'preparation-failure.json').write_text(json.dumps(failure,indent=2)+'\n')
files={str(f.relative_to(p)):{'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))} for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
(p/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'passed':False,'files':files,**failure},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','preparation-failure.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore);shutil.copytree(original/'qa/toolchain',t/'qa/toolchain')
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(p/'component-manifest.json'),'heldToolchain':str(original/'qa/toolchain.json'),'purpose':'Unchanged77 next-intent production/QA with exact restored76 held toolchain. Preserve failure before compile; all original release gates remain open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS explicit laterintent ledger/C/fullhost/model/socketElm implemented77. Preparation excluded heldtoolchain and preflight refused beforecompile; retained77failure. Fresh78 restores exact76cache only. Nextfullbuild and selected10successor/nativeC/Elm checks. Original native/release gates preserved.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]))
