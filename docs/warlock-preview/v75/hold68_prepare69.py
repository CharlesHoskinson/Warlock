"""Retain preflight and fixture failures; adopt independently reviewed model."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v68';t=r/'implementation/warlock-preview-provider-v69';review=r/'docs/warlock-preview/v75/model-review';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
bp=next(p.glob('qa/build-*/report.json'));assert json.loads(bp.read_text())['passed']
fp=next(p.glob('qa/resume-check-*/report.json'));assert not json.loads(fp.read_text())['passed'] and 'Explicit same journal membership extension' in json.loads(fp.read_text())['error']
mp=next(p.glob('qa/resume-model-check-*/report.json'));assert not json.loads(mp.read_text())['passed'] and 'Built-in name' in json.loads(mp.read_text())['error']
rp=next(review.glob('coupled-*/report.json'));model=json.loads(rp.read_text());assert model['passed'] and model['namedScenarios']==8 and model['unsafeMutantsDetected']==3
files={}
for f in sorted(p.rglob('*')):
 rel=f.relative_to(p)
 if any(part in {'elm-stuff','mutable-elm-home','__pycache__'} for part in rel.parts):continue
 assert not f.is_symlink(),f
 if f.is_file():files[str(rel)]={'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode)),'kind':'file'}
m=p/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':False,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(bp),'files':files,'scope':'Full94 production passes. New model used reserved next identifier; C fixture attempted second journal attach instead of explicit membership extension and failed, retaining ASAN failure cleanup diagnostics. Model-only review corrects identifier, passes selected8 and24 actual traces/3mutants. Fresh69 changes only reviewed model identifier and fixture journal extension; no production changes.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not t.exists();shutil.copytree(p,t,ignore=shutil.ignore_patterns('build-*','*check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json'))
for name in ['resume.qnt','resume_tests.qnt']:shutil.copy2(review/name,t/'spec'/name)
f=t/'native/resume-enrollment-test.cpp';s=f.read_text();old='enroll(23);check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error)';new='enroll(23);check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error)';assert s.count(old)==1;f.write_text(s.replace(old,new))
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Reviewed model reserved identifier correction and fixture proper same-owner extend_delivery; all production unchanged from full94 held68','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS full94 production68 passes; modelreview actual8/24traces/3mutants passes; preserve68 model builtin identifier and C fixture duplicatejournalattach failures. Fresh69 only reviewed model and explicitextendfixture; test actualC/Elm then owningnative. Alloriginalreleasegates remainactive.'], 'progress',[str(m.relative_to(r)),str(rp.relative_to(r))]);print(json.dumps({'source':str(t),'held':str(m),'modelStates':model['statesCompared'],'checkpoint':str(e)}))
