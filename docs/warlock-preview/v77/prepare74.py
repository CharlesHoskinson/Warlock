"""Preserve incomplete73 build and restore exact held toolchain in fresh74."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v73';t=r/'implementation/warlock-preview-provider-v74';held=r/'implementation/warlock-preview-provider-v72';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert not t.exists() and not (p/'component-manifest.json').exists() and len(list(p.glob('qa/build-*')))==1
files={str(f.relative_to(p)):{'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))} for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
(p/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'passed':False,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'failure':'Preparation73 recursively excluded elm-home, including held qa/toolchain/elm-home. Build refused missing held inventory before compilation. Raw incomplete build inputs retained; fresh74 restores the exact72-held toolchain, no toolchain downgrade.'},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'ANCESTRY.json','component-manifest.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if n.startswith(('build-','feedback-check-','resume-check-')) or n=='__pycache__' or n=='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore);shutil.copytree(held/'qa/toolchain',t/'qa/toolchain')
pin=json.loads((t/'qa/toolchain.json').read_text());assert all(sha(t/name)==row['sha256'] for name,row in pin['heldFiles'].items())
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(p/'component-manifest.json'),'purpose':'Unchanged72 feedback production and corrected73 new fixture, restoring exact unchanged held compiler/packages omitted by recursive copy filter. Full build/models/C/nativeDOM qualification pending.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS preserve73 incomplete build/toolchain-copy failure; exactnative/Elmproductionunchanged72, fixturecorrected73. Fresh74 restores verified exactheldtoolchain, fullGUIbuild95 thenfeedback9coupled/nativeCcontrols andserializednativeDOM. All original release gates active.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]);print(json.dumps({'source':str(t),'checkpoint':str(e)}))
