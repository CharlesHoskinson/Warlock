"""Hold CPU-only native103; correct a reviewed probe command before launch."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v103';target=repo/'implementation/warlock-client-provider-native-v104';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=next(parent.glob('qa/prepare-*/report.json'));d=json.loads(report.read_text());assert d['passed'] and not d['nativeLaunched'] and not list(parent.glob('qa/native-*'))
for name,h in d['inputs'].items():assert sha(pathlib.Path(name))==h,name
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent);assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'scope':'CPU preflight passed and owning tuple verified; source review found new probe Release encoded job/handle rather than original required complete frame envelope. No native103 campaign launched. Fresh104 corrects probe command to the actual original typed schema, retaining production decoder/guards/oracles/deadlines.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
def exclusions(path,names):return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path).name=='qa' and (name.startswith('native-') or name.startswith('prepare-')))]
assert not target.exists();shutil.copytree(parent,target,ignore=exclusions)
p=target/'receiver-growth-probe.cpp';text=p.read_text();old='w.text("kind","release").begin("job").job(jobs[entry-1]).end().text("handle",uri::encode(packets[entry-1].token).substr(20)).finish()';new='w.text("kind","release").begin("frame").begin("job").job(jobs[entry-1]).end().text("handle",uri::encode(packets[entry-1].token).substr(20)).boolean("owned",true).boolean("signaled",packets[entry-1].signaled).text("fidelity","client").array("coverage").element("client").endArray().counter("expires",packets[entry-1].expires).end().finish()';assert text.count(old)==1;p.write_text(text.replace(old,new,1))
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Source review caught incorrect probe-only Release envelope before any native launch. Fresh104 emits original complete immutable frame schema. Same heldGUI60/own native grant/original2item budgets and original scenarios/deadlines.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS103 CPU preflight passed exactGUI60/owningtuple; independent source review caught probe-only incompleteRelease envelope before native launch. HeldCPU-only103 fresh104 corrects originalcompleteframe command; productiondecoder/guardunchanged. Recompilepreflight then serialprotectednative allold+growth controls. Fullreleaseopen/main desktoppreserved.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))])
print(json.dumps({'heldFiles':len(files),'source':str(target),'checkpoint':str(event)}))
