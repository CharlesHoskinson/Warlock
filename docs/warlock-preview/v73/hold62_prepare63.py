"""Preserve GUI62 passing build and failed model fixture; own corrected GUI63."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v62';target=repo/'implementation/warlock-preview-provider-v63';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bp=next(parent.glob('qa/build-*/report.json'));b=json.loads(bp.read_text());assert b['passed'] and len(b['commands'])==94 and all(x['exitCode']==0 for x in b['commands'])
failed=next(parent.glob('qa/enrollment-check-*/report.json'));f=json.loads(failed.read_text());assert not f['passed'] and f['commands'][-1]['name']=='compile' and f['commands'][-1]['exitCode']==1 and 'use of deleted function' in f['error']
for report in [bp,failed]:
 data=json.loads(report.read_text())
 for rel,h in data['inputs'].items():assert sha(parent/rel)==h,rel
 for rel,h in data.get('artifacts',{}).items():assert sha(report.parent/rel)==h,rel
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent)
 if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':False,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(bp),'failedEnrollmentReport':str(failed),'files':files,'scope':'Production full94 build and actual C/socket dynamic enrollment controls pass; new coupled fixture mistakenly returns noncopyable Coordinator by reference through an auto-return API, compile fails before any Quint run. Fresh63 corrects QA fixture only. No GUI62 native campaign or eligible capture/full release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not target.exists()
shutil.copytree(parent,target,ignore=shutil.ignore_patterns('build-*','check-*','metadata-check-*','catalog-check-*','delivery-check-*','intent-check-*','enrollment-check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json','current-build.json'))
p=target/'qa/enrollment-checks.cpp';s=p.read_text();old='auto& queue=endpoint.nativeDemand([](auto& q)->auto&{return q;});';assert s.count(old)==1;s=s.replace(old,'auto& queue=*endpoint.nativeDemand([](auto& q){return &q;});');p.write_text(s)
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Preserve62 full94 passing production/C controls and failed noncopyable Coordinator QA fixture. Correct fixture to borrow pointer from trusted native callback; production receiver/demand/intent/C code unchanged. No scenario/oracle/deadline weakening. Native acceptance remains pending.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS61 held1610/newintent6 363states2mutants. New62 real production atomic nativeDemandView+original intent reservation and trusted growing C API sharing256actors/2items/128MiB/8records/4readers/2views; full94 build/C socket controls pass. Newmodel fixture compilefailed auto-reference to noncopyableCoordinator; retainedheld62/fresh63 onlyfixture pointerborrow. Rerunfullbuild+selectednew8 enrollment and oldmodels; actualNativeRejected proof discoverability still needs bounded frontend trace review. Then exact owning serializednative dynamicC3subjects/originaldeadlines/actualcleanup/pixels. All13S09/releaseopen; no oldunqualifiedsourcepromotion.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]);print(json.dumps({'held':str(manifest),'files':len(files),'source':str(target),'checkpoint':str(event)}))
