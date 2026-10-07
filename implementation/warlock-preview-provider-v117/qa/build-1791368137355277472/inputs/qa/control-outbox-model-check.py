"""Couple explicitly selected bounded outbox Quint traces to the actual JS."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('control-outbox-model-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=['assets/retained-preview-controls.js','qa/control-outbox-replay.js','qa/control-outbox-model-check.py','spec/control_outbox.qnt','spec/control_outbox_tests.qnt']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual bounded JS queue, issued/confirmed prefixes, exact immutable repeated wire, ordered transmission attempts and results against explicitly selected Quint traces. Boundary uses an explicit initial-counter fixture. No native admission cleanup reservations, actual WebKit activation or effect/physical acceptance.'}
def run(name,args,cwd=None):
    p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
    (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
    report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
    assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
    for rel in names:
        p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
    run('syntax',['node','--check','assets/retained-preview-controls.js'])
    folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'control_outbox_tests.qnt').read_text());assert len(selected)==10
    run('typecheck',[tool,'typecheck','control_outbox_tests.qnt'],folder)
    run('selected',[tool,'test','control_outbox_tests.qnt','--main=control_outbox_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=950061','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
    assert len(list(out.glob('named-*.itf.json')))==10
    run('samples',[tool,'run','control_outbox.qnt','--main=control_outbox','--backend=typescript','--invariant=safety','--seed=950062','--max-samples=200','--max-steps=30','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
    traces=[];compared=0
    for path in sorted(out.glob('*.itf.json')):
        evidence=json.loads(run('replay-'+path.stem,['node','qa/control-outbox-replay.js','assets/retained-preview-controls.js',str(path)]));assert evidence['passed'];compared+=evidence['statesCompared'];traces.append({'trace':path.name,'statesCompared':evidence['statesCompared']})
    mutants=[]
    for name,old,new,witness,wanted in [
        ('skip-missing-receipt','BigInt(receipt.controlOrdinal)!==queue[0].ordinal','BigInt(receipt.controlOrdinal)<queue[0].ordinal','gapReceiptCannotReleaseQueue','Original receipt prefix'),
        ('forget-failed-post','try {post(queue[0].wire);return true;} catch(_error) {return false;}','try {post(queue[0].wire);return true;} catch(_error) {queue.shift();return false;}','failedPostPreservesQueuedPacket','Bounded retained packet occupancy'),
        ('ignore-queue-capacity','queue.length>=capacity || issued===maximum','issued===maximum','queueBackpressureConsumesNoOrdinal','Original issued ordinal')]:
        changed=out/name;shutil.copytree(out/'inputs',changed);p=changed/'assets/retained-preview-controls.js';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
        run(name+'-syntax',['node','--check','assets/retained-preview-controls.js'],changed)
        trace=next(out.glob('named-'+witness+'-*.itf.json'));p=subprocess.run(['node','qa/control-outbox-replay.js','assets/retained-preview-controls.js',str(trace)],cwd=changed,capture_output=True,text=True,timeout=180)
        (changed/'replay.stdout').write_text(p.stdout);(changed/'replay.stderr').write_text(p.stderr)
        assert p.returncode==1 and 'AssertionError' in p.stderr and wanted in p.stderr,(name,p.stdout,p.stderr)
        mutants.append({'name':name,'syntaxPassed':True,'witness':witness,'namedObservableMismatch':True})
    assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
    report.update(passed=True,namedScenarios=10,invariantSamples=200,coupledTraces=traces,statesCompared=compared,unsafeActualJSVariantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1500]}),flush=True);sys.exit(not report['passed'])
