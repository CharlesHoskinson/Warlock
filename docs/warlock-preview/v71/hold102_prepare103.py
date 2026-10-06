"""Preserve preflight refusal before native launch; restore exact held ABI descriptor."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v102';target=repo/'implementation/warlock-client-provider-native-v103';held=repo/'implementation/warlock-client-provider-native-v101';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=next(parent.glob('qa/prepare-*/report.json'));d=json.loads(report.read_text());assert not d['passed'] and not d['nativeLaunched'] and 'native-build-report.json' in d['traceback']
assert not list(parent.glob('qa/native-*'));files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent);assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'passed':False,'files':files,'failure':'CPU preflight correctly refuses missing exact native-build-report.json. Broad native-* copy exclusion omitted a root ABI descriptor, not merely QA directories. No native102 campaign launched. Fresh103 copies exact held native101 descriptor and limits exclusions to generated QA directories; original ABI/guards/scenarios/deadlines unchanged.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
def exclusions(path,names):
 return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path).name=='qa' and (name.startswith('native-') or name.startswith('prepare-')))]
assert not target.exists();shutil.copytree(parent,target,ignore=exclusions)
descriptor=held/'native-build-report.json';row=json.loads((held/'component-manifest.json').read_text())['files']['native-build-report.json'];assert sha(descriptor)==row['sha256'];shutil.copy2(descriptor,target/'native-build-report.json')
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Restore exact held native101 ABI descriptor omitted by copy exclusion; preserve failed102 CPU-only preflight. Same GUI60, new actual own native receiver/journal growth probe, original controls/oracles/deadlines and owning core/plugin tuple.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS heldGUI60 build90/GIO49/delivery6 388states2mutants/catalog8 214/metadata8 210/demand10 564states3mutants. New102 preflight safely failed missing copiedABI descriptor/no native launched, held. Fresh103 restored exactheld101 descriptor with narrower generateddirectory exclusions. CompleteCPUpreflight then serialprotectednative on exact tuple, preserve allprior/native101/original1783 and new actual3actors2physicalitems. All60QAterminal/no native process yet, fullreleaseopen.'],'progress',['implementation/warlock-preview-provider-v60/component-manifest.json',str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))])
print(json.dumps({'heldFiles':len(files),'source':str(target),'checkpoint':str(event)}))
