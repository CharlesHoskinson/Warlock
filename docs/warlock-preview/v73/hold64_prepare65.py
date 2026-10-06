"""Preserve GUI64 passing build and model assertion failure; own corrected GUI65."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v64';target=repo/'implementation/warlock-preview-provider-v65';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bp=next(parent.glob('qa/build-*/report.json'));b=json.loads(bp.read_text());assert b['passed'] and len(b['commands'])==94 and all(x['exitCode']==0 for x in b['commands'])
failed=next(parent.glob('qa/enrollment-check-*/report.json'));f=json.loads(failed.read_text());assert not f['passed'] and f['commands'][-1]['name']=='quint-typecheck' and f['commands'][-1]['exitCode']==1 and 'Trying to infer effect' in f['error']
for report in [bp,failed]:
 data=json.loads(report.read_text())
 for rel,h in data.get('inputs',{}).items():assert sha(parent/rel)==h,rel
 for rel,h in data.get('artifacts',{}).items():assert sha(report.parent/rel)==h,rel
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent)
 if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':False,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(bp),'failedEnrollmentReport':str(failed),'files':files,'scope':'Full94 production build and extended actual C/socket expired-capacity controls pass; original intent6/demand10/delivery6 checks pass. Enrollment model still fails because then(assert) has no state update. Fresh65 adopts independently typechecked action check assertion with s prime equals s, preserving all eight original scenarios/oracles. No native64 or full release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not target.exists()
shutil.copytree(parent,target,ignore=shutil.ignore_patterns('build-*','check-*','metadata-check-*','catalog-check-*','delivery-check-*','intent-check-*','enrollment-check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json','current-build.json'))
review=repo/'docs/warlock-preview/v73/model-review';assert json.loads((review/'report.json').read_text())['passed'];shutil.copy2(review/'enrollment_tests.qnt',target/'spec/enrollment_tests.qnt')
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Preserve64 full94 and extended expired C capacity controls plus failed enrollment then(assert) effect. Adopt exact independently typechecked check action with unchanged safety/assertions and explicit state preservation; all production code unchanged. Add receiver-epoch mutant to actual trace oracle. Build-dependent metadata/catalog runs only after full build terminal. No native qualification or scenario/deadline weakening.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS64 full94 and actual C expired-intent-after-returned-capacity pass; intent6/demand10/delivery6 pass. New enrollment8 stilltypecheckfailed missing unchanged-state action wrapper, preserveheld64. Independent model-review typecheckpasses exact check action; fresh65 imports that wrapper retaining originalscenarioassertions. Add unsafe reused receiver-epoch mutant, then actual new8 coupling, fullcompile and oldregressions; metadata/catalog run afterbuildterminal. Native106 source prepared no launch yet; keep native105 oldoriginal2405 and adddynamicC originaldeadline/actualphysicaldrain, owningtuple/main desktoppreserved. FullS09/S01-S16 releaseopen'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]);print(json.dumps({'held':str(manifest),'files':len(files),'source':str(target),'checkpoint':str(event)}))
