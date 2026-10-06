"""Fresh owner source for reliable retirement completion delivery."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v89';t=r/'implementation/warlock-preview-provider-v90';assert not t.exists()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
m=p/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and d['sourceHeld']
for rel,row in d['files'].items():assert sha(p/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Trusted native retirement observation, exact Elm readiness, atomic native all-map cleanup, and bounded retained completion delivery with independent nonreused transport ordinals and contiguous Elm processing acknowledgments. Original receiver epoch and native obligations remain mandatory; this source is unqualified until built and exercised.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS own freshGUI90 for trusted native retirement observation/readiness/completion routing. Bounded journal reserves final wire before native erasure and retries original completion until exact original-receiver contiguous Elm delivery ACK; transport receipt cannot certify physical cleanup. Native126 on heldGUI89/core16/plugin18 launched serialized. Preserve current live campaign and all original release/turnover/capture gates.'],'progress',[str((t/'ANCESTRY.json').relative_to(r)),str(m.relative_to(r))]))
