"""Fix actual premature Elm ACK, retaining all observed counterexamples."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v70';t=r/'implementation/warlock-preview-provider-v71';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
bp=next(p.glob('qa/build-*/report.json'));assert json.loads(bp.read_text())['passed']
fp=next(p.glob('qa/resume-check-*/report.json'));assert not json.loads(fp.read_text())['passed'] and 'before source registration' in json.loads(fp.read_text())['error']
files={}
for f in sorted(p.rglob('*')):
 rel=f.relative_to(p)
 if any(part in {'elm-stuff','mutable-elm-home','__pycache__'} for part in rel.parts):continue
 assert not f.is_symlink(),f
 if f.is_file():files[str(rel)]={'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode)),'kind':'file'}
m=p/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':False,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(bp),'files':files,'scope':'Full94 native/Elm build, actual C normal/expiry/receiver pass. Same Elm original-job history now reaches early future receipt, revealing real PreviewLifecycle receipt bug: unknown terminal job is ACKed because absent from known after update. Preserve counterexample; fresh71 requires exact known-before or exact retained terminal(job,sequence), with one bounded replay slot per lifecycle. No fabricated job/floor/history.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not t.exists();shutil.copytree(p,t,ignore=shutil.ignore_patterns('build-*','*check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json'))
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Fix actual early future receipt ACK in immutable Elm; retain one exact terminal tuple for duplicate ACK delivery, preserve job request counters and native resume ownership','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS70C and full94 pass but actualElm earlyfutureproof ACK counterexample found and held. Fresh71 fixes realreceipt correlation, boundedexactterminalreplay; native resume production unchanged67. CompileactualchangedElm, replaynewC/Elm17andselectedreceipt model, thenowningnative. Alloriginalfullreleasegatesremainactive.'], 'progress',[str(m.relative_to(r)),str(fp.relative_to(r))]);print(json.dumps({'source':str(t),'held':str(m),'checkpoint':str(e)}))
