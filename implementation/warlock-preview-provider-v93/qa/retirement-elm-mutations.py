"""Compile unsafe Elm changes and detect each via coupled Quint witness."""
import hashlib,json,os,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-elm-mutations-'+str(time.time_ns()));out.mkdir()
sys.path.insert(0,str(root/'qa'));import toolchain
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'commands':[],'inputs':{},'scope':'Separately compiled unsafe Elm guards detected by explicitly selected coupled Quint observable state/command witnesses; not physical/native retirement acceptance.'}
try:
 build=next(root.glob('qa/build-*/report.json'));proof=json.loads(build.read_text());assert proof['passed'] and len(proof['commands'])==95
 for rel,h in proof['inputs'].items():assert sha(root/rel)==h,rel
 refinement=next(root.glob('qa/retirement-refinement-check-v2-*/report.json'));d=json.loads(refinement.read_text());assert d['passed'] and d['namedScenarios']==10 and d['unsafeModelMutantsDetected']==3
 report['inputs'][str(refinement)]=sha(refinement);report['inputs'][str(build)]=sha(build)
 for rel,h in d['inputs'].items():assert sha(root/rel)==h,rel;report['inputs'][str(root/rel)]=h
 for rel,h in d['artifacts'].items():assert sha(refinement.parent/rel)==h,rel
 info=toolchain.verify();shutil.copytree(root/info['elmHome'],out/'mutable-elm-home')
 mutations=[]
 for name,file,old,new,witness in [
  ('global-sibling-order','PreviewPresenter.elm','not entry.readySent || not settled || not exact || not frontier','not entry.readySent || not settled || not exact || not frontier || not (Retirement.fresh ledger.observed fact.native)','completionBehindSiblingObservation'),
  ('rewind-shared-cutoff','NativeActorRetirement.elm','in if newest then {updated | settled=Just fact} else updated','in if newest || not newest then {updated | settled=Just fact} else updated','olderCompletionCannotRewindCutoff'),
  ('forget-before-ready','PreviewPresenter.elm','not entry.readySent || not settled || not exact || not frontier','not (entry.readySent || not entry.readySent) || not (settled || not settled) || not exact || not frontier','pendingJobCannotForget')]:
  changed=out/name;changed.mkdir();shutil.copytree(build.parent/'inputs/src',changed/'src');shutil.copy2(root/'elm.json',changed/'elm.json')
  for p in (changed/'src').glob('*.elm'):report['inputs'].setdefault(str(root/'src'/p.name),sha(root/'src'/p.name))
  p=changed/'src'/file;s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  argv=[str(root/info['compiler']),'make','src/PreviewPresenterReplay.elm','--optimize','--output=preview-replay.js']
  toolchain.verify();p=subprocess.run(argv,cwd=changed,env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')),capture_output=True,text=True,timeout=180);toolchain.verify()
  (changed/'compile.stdout').write_text(p.stdout);(changed/'compile.stderr').write_text(p.stderr)
  report['commands'].append({'name':name+'-compile','argv':argv,'exitCode':p.returncode});assert p.returncode==0,p.stderr or p.stdout
  trace=next(refinement.parent.glob('named-'+witness+'-*.itf.json'));report['inputs'][str(trace)]=sha(trace)
  argv=['node',str(root/'qa/retirement-refinement-replay.js'),str(changed/'preview-replay.js'),str(root/'qa/native-source-fixture.json'),str(trace)]
  p=subprocess.run(argv,cwd=changed,capture_output=True,text=True,timeout=180)
  (changed/'replay.stdout').write_text(p.stdout);(changed/'replay.stderr').write_text(p.stderr)
  assert p.returncode==1 and 'AssertionError' in p.stderr and trace.name+' step ' in p.stderr,(name,p.stdout,p.stderr)
  mutations.append({'name':name,'compiled':True,'witness':str(trace),'observableMismatch':True,'exitCode':p.returncode})
 assert all(sha(pathlib.Path(p))==h for p,h in report['inputs'].items())
 report.update(passed=True,unsafeCompiledElmMutantsDetected=3,mutants=mutations,toolchain=info)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and not any(x in {'mutable-elm-home','elm-stuff'} for x in p.relative_to(out).parts)}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1000]}),flush=True);sys.exit(not report['passed'])
