"""Keep reserved-name Quint failure and derive a fresh corrected source."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v58';target=repo/'implementation/warlock-preview-provider-v59';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports=list(parent.glob('qa/*-*/report.json'));assert len(reports)==3
for p in reports:
 d=json.loads(p.read_text())
 for rel,h in d['inputs'].items():assert sha(parent/rel)==h,rel
 for rel,h in d.get('artifacts',{}).items():assert sha(p.parent/rel)==h,rel
 if p.parent.name.startswith('delivery-check-'):assert not d['passed'] and d['commands'][-1]['name']=='quint-typecheck' and "Built-in name 'enabled'" in (p.parent/'quint-typecheck.stderr').read_text()
 else:assert d['passed'],p
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent)
 if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'passed':False,'files':files,'failure':'Quint model attempted to redefine builtin enabled and next. Actual fullGUI90/C-bootstrap own/fork guards/GIO49 and demand10 passed. Fresh59 renames only model function/local binding; retain original source/evidence and no native deadline/oracle changes.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not target.exists();shutil.copytree(parent,target,ignore=shutil.ignore_patterns('build-*','check-*','metadata-check-*','catalog-check-*','delivery-check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json','current-build.json'))
p=target/'spec/delivery.qnt';text=p.read_text();assert text.count('enabled(')==2 and text.count('val next=')==1;text=text.replace('enabled(','eventAdmitted(').replace('val next=','val updated=').replace('...next,','...updated,');p.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Correct reserved model identifiers enabled/next in fresh source while retaining accepted physical guards and C own-process extension. No production logic or original scenario/deadline weakening.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS58 fullGUI90/newGIO49/Cown+fork/demand10 pass; newQuint failed reserved enabled/next names and held. Fresh59 fixes only names. Run selected model before newfullcompile, keep coupled exactnative physical/journal observations, then native102 actualgrowth on owning ABI; originalrelease/eligibility remain open. All58 handles terminal; native102 source owned/no actual native launched.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))])
print(json.dumps({'heldFiles':len(files),'source':str(target),'checkpoint':str(event)}))
