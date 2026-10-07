"""Each unsafe retained-channel guard compiles, then fails its exact Elm witness."""
import hashlib,json,os,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-delivery-elm-mutants-'+str(time.time_ns()));out.mkdir()
from toolchain import verify
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[root/'elm.json',root/'qa/retirement-delivery-elm-mutants.py',root/'qa/retirement-delivery-refinement.js',root/'qa/native-source-fixture.json',*sorted((root/'src').glob('*.elm'))]
report={'passed':False,'inputs':{str(p):sha(p) for p in paths},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
    found=list(root.glob('qa/retirement-delivery-model-check-*/report.json'));assert len(found)==1
    refinement=found[0];d=json.loads(refinement.read_text());assert d['passed'] and d['namedScenarios']==14 and d['unsafeModelMutantsDetected']==3
    report['inputs'][str(refinement)]=sha(refinement)
    for rel,value in d['inputs'].items():assert sha(root/rel)==value,rel
    for rel,value in d['artifacts'].items():assert sha(refinement.parent/rel)==value,rel
    info=verify();shutil.copytree(root/info['elmHome'],out/'mutable-elm-home');mutants=[]
    for name,old,new,witness in [
        ('skip-delivery-gap','else if UInt64.next ledger.processed /= Just delivery.ordinal then (prior,encode [])','else if UInt64.compare delivery.ordinal ledger.processed /= GT then (prior,encode [])','gapCannotRemoveReadyActor'),
        ('lose-repeat-ack','else if UInt64.compare delivery.ordinal ledger.processed /= GT then (prior,acknowledge)','else if UInt64.compare delivery.ordinal ledger.processed /= GT then (prior,encode [])','lostProcessingAckRetriesOnlyAck'),
        ('legacy-downgrade','ledger.channel /= Nothing || not entry.readySent || not settled || not exact || not frontier','not entry.readySent || not settled || not exact || not frontier','retainedChannelRejectsLegacy')]:
        changed=out/name;changed.mkdir();shutil.copytree(root/'src',changed/'src');shutil.copy2(root/'elm.json',changed/'elm.json')
        p=changed/'src/PreviewPresenter.elm';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
        args=[str(root/info['compiler']),'make','src/PreviewPresenterReplay.elm','--optimize','--output=preview-replay.js']
        verify();p=subprocess.run(args,cwd=changed,env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')),capture_output=True,text=True,timeout=180);verify()
        (changed/'compile.stdout').write_text(p.stdout);(changed/'compile.stderr').write_text(p.stderr)
        report['commands'].append({'name':name+'-compile','argv':args,'exitCode':p.returncode});assert p.returncode==0,p.stderr or p.stdout
        trace=next(refinement.parent.glob('named-'+witness+'-*.itf.json'));report['inputs'][str(trace)]=sha(trace)
        args=['node',str(root/'qa/retirement-delivery-refinement.js'),str(changed/'preview-replay.js'),str(root/'qa/native-source-fixture.json'),str(trace)]
        p=subprocess.run(args,cwd=changed,capture_output=True,text=True,timeout=180)
        (changed/'replay.stdout').write_text(p.stdout);(changed/'replay.stderr').write_text(p.stderr)
        assert p.returncode==1 and 'AssertionError' in p.stderr and trace.name+' step ' in p.stderr,(name,p.stdout,p.stderr)
        mutants.append({'name':name,'compiled':True,'witness':str(trace),'observableMismatch':True,'exitCode':p.returncode})
    assert all(sha(pathlib.Path(p))==h for p,h in report['inputs'].items())
    report.update(passed=True,unsafeCompiledElmMutantsDetected=3,mutants=mutants,toolchain=info)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and not any(x in {'mutable-elm-home','elm-stuff'} for x in p.relative_to(out).parts)}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1000]}),flush=True);sys.exit(not report['passed'])
