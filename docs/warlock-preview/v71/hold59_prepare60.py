"""Keep successful trace comparisons and failed unsafe-mutant compilation."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v59';target=repo/'implementation/warlock-preview-provider-v60';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=next(parent.glob('qa/delivery-check-*/report.json'));d=json.loads(p.read_text());assert not d['passed'] and d['commands'][-1]['name']=='missing-admission-compile' and len(d['coupledTraces'])==16
for rel,h in d['inputs'].items():assert sha(parent/rel)==h,rel
for rel,h in d['artifacts'].items():assert sha(p.parent/rel)==h,rel
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent)
 if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'passed':False,'files':files,'failure':'All six selected Quint scenarios/150 samples/16 actual GIO+Broke journal coupled traces passed. Unsafe missing-admission mutant intentionally omitted its sole broker use; Werror correctly rejected unused parameter before mutation behavior test. Fresh60 marks that mutant parameter intentionally unused. Production source/guards unchanged.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not target.exists();shutil.copytree(parent,target,ignore=shutil.ignore_patterns('build-*','check-*','metadata-check-*','catalog-check-*','delivery-check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json','current-build.json'))
p=target/'qa/delivery-check.py';text=p.read_text();old="'view(popup,registered);return true;'";assert text.count(old)==1;text=text.replace(old,"'(void)broker;view(popup,registered);return true;'",1);p.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Retain actual59 selected model/GIO traces and failed mutation compiler fixture. Mark intentionally unused broker parameter in missing-admission unsafe mutant only; real production guards/Werror untouched. Full compile/native acceptance remains pending.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS actual59 six selected/150samples/16physicalGIO+journal traces passed; mutation compile failed intentional unused parameter, evidence held. Fresh60 only mutationfixture correction, production ownepoch/map/ACK unchanged. Fullcompile+mutants+models, then native102 actual3actors/2chargeditems/oldreader/Cjournalgrowth; all59handles terminal, desktop/foreignchanges preserved/fullreleaseopen.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))])
print(json.dumps({'heldFiles':len(files),'source':str(target),'checkpoint':str(event)}))
