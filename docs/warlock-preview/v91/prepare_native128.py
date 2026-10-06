"""Retain failed127 preflight reference omission; derive verified metadata adapter."""
import ast,hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v127';target=repo/'implementation/warlock-client-provider-native-v128'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failed=parent/'qa/prepare-1791327001336256741/report.json';proof=json.loads(failed.read_text())
assert not proof['passed'] and not proof['nativeLaunched'] and proof['error']=="KeyError('asynchronousRetirementReport')"
assert not target.exists() and not (parent/'component-manifest.json').exists()
files={}
for p in sorted(parent.rglob('*')):
    assert not p.is_symlink(),p
    if p.is_file():files[str(p.relative_to(parent))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json'
manifest.write_text(json.dumps({'schema':1,'sourceHeld':True,'passed':False,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','files':files,'retainedPreflightFailure':str(failed),'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Native127 preflight never launched native GUI: heldGUI92 omitted three asynchronous report reference keys although those passing reports and source/artifacts are held. Keep source/metadata failure; fresh128 resolves references from exact held inventory before any qualification.'},indent=2)+'\n')
def ignore(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==parent/'qa' and n.startswith(('native-','prepare-')))]
shutil.copytree(parent,target,ignore=ignore)
p=target/'qa/prepare.py';s=p.read_text()
marker=" for field in ['asynchronousRetirementReport','asynchronousRefinementReport','asynchronousElmMutantReport']:"
assert s.count(marker)==1
extra=""" compatibility={}
 for field,pattern in [('asynchronousRetirementReport','qa/retirement-async-check-*/report.json'),('asynchronousRefinementReport','qa/retirement-refinement-check-v2-*/report.json'),('asynchronousElmMutantReport','qa/retirement-elm-mutations-*/report.json')]:
  found=list(provider.glob(pattern));assert len(found)==1
  rel=str(found[0].relative_to(provider));assert rel in providerHeld['files'] and sha(found[0])==providerHeld['files'][rel]['sha256']
  providerHeld[field]=str(found[0]);compatibility[field]={'path':str(found[0]),'sha256':sha(found[0])}
 pre['providerCompatibilityReferences']={'providerManifestSHA256':sha(providerManifest),'references':compatibility}
"""
s=s.replace(marker,extra+marker);ast.parse(s);p.write_text(s)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Resolve exactly heldGUI92 passing asynchronous report references without changing its immutable manifest. Preserve every original native126 scenario and deadline. No native campaign was launched from127.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS heldGUI92 full95/alloriginal12/retained45+14/34/667/3model+3compiledElm and48CnativeElm controls. Native127 failed preflight on omitted asynchronous reference keys before any native launch; source/report held. Fresh128 resolves references from exact heldGUI92 inventory, then preflight/serialized original126 campaign. Actual host transport and all original release gates remain open.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
