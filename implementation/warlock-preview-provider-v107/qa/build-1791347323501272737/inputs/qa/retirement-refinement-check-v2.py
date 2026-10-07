"""Explicit asynchronous Quint scenarios coupled to actual full-build Elm."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-refinement-check-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
names=['spec/retirement_async.qnt','spec/retirement_async_tests_v2.qnt','qa/retirement-refinement-replay.js','qa/native-source-fixture.json','qa/retirement-refinement-check-v2.py']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Two independently delivered actor-retirement channels coupled to actual full-build immutable Elm and ordered commands. Synthetic native facts; physical/native transport and continuing >256-window turnover remain open.'}
def run(name,args,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
try:
 build=next(root.glob('qa/build-*/report.json'));proof=json.loads(build.read_text());assert proof['passed'] and len(proof['commands'])==95
 for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
 report['fullBuild']={'path':str(build),'sha256':sha(build)}
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 compiled=out/'preview-replay.js';shutil.copy2(build.parent/'inputs/assets/preview-replay.js',compiled);report['compiledElmSHA256']=sha(compiled)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'retirement_async_tests_v2.qnt').read_text());assert len(selected)==10
 run('typecheck',[str(tool),'typecheck','retirement_async_tests_v2.qnt'],folder)
 run('selected',[str(tool),'test','retirement_async_tests_v2.qnt','--main=retirement_async_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=890051','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
 assert len(list(out.glob('named-*.itf.json')))==10
 run('samples',[str(tool),'run','retirement_async.qnt','--main=retirement_async','--backend=typescript','--invariant=safety','--seed=890052','--max-samples=300','--max-steps=30','--n-traces=20','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
 traces=sorted(out.glob('*.itf.json'))
 evidence=json.loads(run('compiled-replay',['node',str(out/'inputs/qa/retirement-refinement-replay.js'),str(compiled),str(out/'inputs/qa/native-source-fixture.json'),*[str(p) for p in traces]]))
 assert evidence['passed'] and len(evidence['coupledTraces'])==30
 mutants=[]
 for name,old,new,witness in [
  ('global-sibling-gate','if(st.first and st.readyFirst)','if(st.first and st.readyFirst and not(st.pendingSecond))','completionBehindSiblingObservation'),
  ('rewind-shared-clock','cutoff:if(st.cutoff>102)st.cutoff else 102','cutoff:102','olderCompletionCannotRewindCutoff'),
  ('premature-removal','if(st.first and st.readyFirst)','if(st.first)','pendingJobCannotForget')]:
  changed=out/name;shutil.copytree(folder,changed);p=changed/'retirement_async.qnt';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  run(name+'-typecheck',[str(tool),'typecheck','retirement_async_tests_v2.qnt'],changed)
  p=subprocess.run([str(tool),'test','retirement_async_tests_v2.qnt','--main=retirement_async_tests','--backend=typescript','--match=^'+witness+'$','--seed=890053','--max-samples=1'],cwd=changed,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  assert p.returncode!=0 and 'QNT508' in p.stdout+p.stderr and 'Assertion failed' in p.stdout+p.stderr,(name,p.stdout,p.stderr)
  mutants.append({'name':name,'witness':witness,'namedAssertionFailure':True})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,selectedNames=selected,namedScenarios=10,invariantSamples=300,evidence=evidence,unsafeModelMutantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:900]}),flush=True);sys.exit(not report['passed'])
