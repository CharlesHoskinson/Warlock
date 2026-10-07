"""Explicit Quint bookkeeping traces against the actual native readiness journal."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-poll-check-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]
names+=['spec/retirement_poll_v2.qnt','spec/retirement_poll_tests_v2.qnt','qa/retirement-poll-check-v2.py']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual bounded native journal selection matched after every Quint event, including original canonical wires, foreign epoch, empty/wrapped polling and retained prefixes. Fake native records; aggregate physical ownership and native query bounds require separate C/socket test.'}
def run(name,args,cwd=None):
    p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
    (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
    report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
    assert p.returncode==0,p.stderr or p.stdout
    return p.stdout
try:
    for rel in names:
        p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
    flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
    args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/retirement-poll-replay.cpp','-o',str(out/'checks'),*flags]
    run('compile',args)
    folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'retirement_poll_tests_v2.qnt').read_text());assert len(selected)==10
    run('typecheck',[tool,'typecheck','retirement_poll_tests_v2.qnt'],folder)
    run('selected',[tool,'test','retirement_poll_tests_v2.qnt','--main=retirement_poll_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=940051','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
    assert len(list(out.glob('named-*.itf.json')))==10
    run('samples',[tool,'run','retirement_poll_v2.qnt','--main=retirement_poll','--backend=typescript','--invariant=safety','--seed=940052','--max-samples=200','--max-steps=30','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
    traces=[];compared=0
    for path in sorted(out.glob('*.itf.json')):
        proof=json.loads(run('replay-'+path.stem,[str(out/'checks'),str(path)]));assert proof['passed'];compared+=proof['statesCompared'];traces.append({'path':str(path),'statesCompared':proof['statesCompared']})
    mutants=[]
    for name,old,new,witness in [
        ('starve-after-blocked-row','auto row=rows_.upper_bound(pollAfter_);','auto row=rows_.begin();','blockedFirstDoesNotStarveNeighbor'),
        ('poll-unaccepted-observation','if(row->second.readyAccepted && !row->second.completion) {','if(!row->second.completion) {','unacceptedObservationExcluded'),
        ('poll-completed-row','if(row->second.readyAccepted && !row->second.completion) {','if(row->second.readyAccepted) {','completedRowExcluded')]:
        changed=out/name;shutil.copytree(out/'inputs',changed);p=changed/'native/retirement_journal.hpp';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
        mutant_args=[*args];mutant_args[mutant_args.index('-o')+1]=str(changed/'checks');run(name+'-compile',mutant_args,changed)
        trace=next(out.glob('named-'+witness+'-*.itf.json'))
        p=subprocess.run([str(changed/'checks'),str(trace)],capture_output=True,text=True,timeout=180)
        (changed/'replay.stdout').write_text(p.stdout);(changed/'replay.stderr').write_text(p.stderr)
        assert p.returncode==1 and 'Compiled fair one-candidate selection' in p.stderr and 'Sanitizer' not in p.stderr,(name,p.stdout,p.stderr)
        mutants.append({'name':name,'compiled':True,'witness':witness,'namedObservableMismatch':True})
    assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
    report.update(passed=True,namedScenarios=10,invariantSamples=200,coupledTraces=traces,statesCompared=compared,unsafeCompiledNativeMutantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1300]}),flush=True);sys.exit(not report['passed'])
