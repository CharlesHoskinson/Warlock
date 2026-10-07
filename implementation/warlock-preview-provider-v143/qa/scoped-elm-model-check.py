"""Explicit Quint scenario/command/state refinement to the single compiled policy."""
import hashlib,json,os,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('scoped-elm-model-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'src').glob('*') if p.is_file()]+['elm.json','qa/scoped-elm-refinement.js','qa/scoped-elm-model-check.py','qa/toolchain.py','qa/toolchain.json','qa/native-source-fixture.json','spec/scoped_elm_realm.qnt','spec/scoped_elm_realm_tests.qnt']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual optimized single Elm PreviewPresenter coupled to explicit scoped realm model traces. Native facts are trace stimuli; actual C/Native/outbox coupling qualified separately. Physical closure and real host integration remain open.'}
def run(name,args,cwd=None,env=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',env=env,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 sys.path.insert(0,str(root/'qa'));from toolchain import verify
 held=verify();shutil.copytree(root/held['elmHome'],out/'mutable-elm-home');env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home'))
 binary=out/'realm.js';args=[str(root/held['compiler']),'make','src/ScopedPreviewPresenterReplay.elm','--optimize','--output='+str(binary)]
 run('optimized-elm',args,env=env)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'scoped_elm_realm_tests.qnt').read_text());assert len(selected)==20
 run('typecheck',[tool,'typecheck','scoped_elm_realm_tests.qnt'],folder)
 run('selected',[tool,'test','scoped_elm_realm_tests.qnt','--main=scoped_elm_realm_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1130011','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
 assert len(list(out.glob('named-*.itf.json')))==20
 run('samples',[tool,'run','scoped_elm_realm.qnt','--main=scoped_elm_realm','--backend=typescript','--invariant=safety','--seed=1130012','--max-samples=200','--max-steps=30','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
 traces=sorted(out.glob('*.itf.json'));e=json.loads(run('compiled-refinement',['node','qa/scoped-elm-refinement.js',str(binary),'qa/native-source-fixture.json',*[str(p) for p in traces]]).stdout);assert e['passed']
 mutants=[]
 for name,file,old,new,witness in [
  ('foreign-realm','NativePreviewRealm.elm','if same current domain then Just event else Nothing','if True then Just event else Nothing','oldRealmCannotSupplyTerminal'),
  ('wrong-floor','PreviewPresenter.elm','entry.retirement /= Nothing || not (floorMatches entry seed) ||','entry.retirement /= Nothing || False ||','wrongFloorCannotRevoke'),
  ('premature-final','PreviewPresenter.elm','entry.retirement /= Nothing || not entry.detachReadySent || entry.detachment /= Just seed || not (floorMatches entry seed) ||\n                        not (entry.model |> Maybe.map Preview.settled |> Maybe.withDefault True) ||','entry.retirement /= Nothing || entry.detachment /= Just seed ||','prematureCompletionCannotRemove'),
  ('skip-gap','PreviewPresenter.elm','else if UInt64.next scoped.processed /= Just delivery.ordinal then','else if False then','completionGapCannotAdvance'),
  ('changed-repeat-ack','PreviewPresenter.elm','if Dict.get identity scoped.completed == Just (delivery.ordinal,seed) then','if True then','changedFactCannotReack'),
  ('missing-repeat-ack','PreviewPresenter.elm','if Dict.get identity scoped.completed == Just (delivery.ordinal,seed) then (prior,ack)','if Dict.get identity scoped.completed == Just (delivery.ordinal,seed) then (prior,encode [])','lostProcessingAckRepeatsExactAck')]:
  target=out/name;shutil.copytree(out/'inputs',target,ignore=shutil.ignore_patterns('elm-stuff'));p=target/'src'/file;s=p.read_text();assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new));compiled=target/'realm.js';changed=[*args];changed[-1]='--output='+str(compiled);run(name+'-compile',changed,target,env)
  trace=next(out.glob('named-'+witness+'-*.itf.json'));r=run(name+'-witness',['node','qa/scoped-elm-refinement.js',str(compiled),'qa/native-source-fixture.json',str(trace)],target,required=False)
  assert r.returncode==1 and 'AssertionError' in r.stderr and witness in r.stderr,(name,r.stderr);mutants.append({'name':name,'compiled':True,'witness':witness,'originalObservableMismatch':True})
 verify();assert all(sha(root/n)==v for n,v in report['inputs'].items())
 report.update(passed=True,namedScenarios=20,selectedNames=selected,invariantSamples=200,evidence=e,unsafeCompiledElmVariantsDetected=6,mutants=mutants)
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2600]}),flush=True);sys.exit(not report['passed'])
