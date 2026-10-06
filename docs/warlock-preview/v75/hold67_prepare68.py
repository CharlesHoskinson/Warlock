"""Preserve successful GUI and failed new fixtures; correct only fresh fixtures."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v67';t=r/'implementation/warlock-preview-provider-v68';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
build=next(p.glob('qa/build-*/report.json'));d=json.loads(build.read_text());assert d['passed'] and len(d['commands'])==94
failed=next(p.glob('qa/resume-check-*/report.json'));d=json.loads(failed.read_text());assert not d['passed'] and 'misleading-indentation' in d['error']
failure=p/'qa/resume-model-preflight-failure.json';failure.write_text(json.dumps({'passed':False,'scope':'Runner fails before compilation/model execution: generated input list points to absent qa/resume-check.py instead of qa/resume-model-check.py','runnerSHA256':sha(p/'qa/resume-model-check.py'),'nativeAcceptance':False},indent=2)+'\n')
files={}
for f in sorted(p.rglob('*')):
 rel=f.relative_to(p)
 if any(part in {'elm-stuff','mutable-elm-home','__pycache__'} for part in rel.parts):continue
 assert not f.is_symlink(),f
 if f.is_file():files[str(rel)]={'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode)),'kind':'file'}
m=p/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':False,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(build),'files':files,'scope':'Changed production full94 build passed; new C fixture Werror indentation and model runner missing self-path failed before execution. Fresh68 corrects only fixture indentation/runner self-path; production unchanged. No native67 qualification.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not t.exists();shutil.copytree(p,t,ignore=shutil.ignore_patterns('build-*','*check-*','component-manifest.json','resume-model-preflight-failure.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json'))
f=t/'qa/resume-model-check.py';s=f.read_text();assert s.count("'qa/resume-check.py'")==1;f.write_text(s.replace("'qa/resume-check.py'","'qa/resume-model-check.py'"))
f=t/'native/resume-enrollment-test.cpp';s=f.read_text();assert s.count('<<std::endl;return 0;')==1;f.write_text(s.replace('<<std::endl;return 0;','<<std::endl;\n return 0;'))
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Fixture-only indentation and model runner self-path corrections after held67/full94 production pass; all production code/spec/oracles/deadlines unchanged','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS production67 full94 build passes original lifecycle. New fixture Werror indentation and model runner missing self-path failed before execution; exact67 held, fresh68 only corrections. Retained resume deadline/original receiver/real rejected job remains actual production; full original release scope active.'], 'progress',[str(m.relative_to(r)),str(build.relative_to(r))]);print(json.dumps({'held':str(m),'files':len(files),'source':str(t),'checkpoint':str(event)}))
