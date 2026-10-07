"""Explicit Quint bookkeeping traces against the actual native readiness journal."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-readiness-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]
names+=['spec/retirement_readiness.qnt','spec/retirement_readiness_tests.qnt','qa/retirement-readiness-check.py']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual native bounded transport journal/readiness metadata; fake native records. Commit is a trusted caller operation, not a journal claim of physical cleanup or Elm readiness. Original C/native/Elm v4 separately validates actor receiver/physical/proof barriers and one-shot readiness.'}
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
    args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/retirement-readiness-replay.cpp','-o',str(out/'checks'),*flags]
    run('compile',args)
    folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'retirement_readiness_tests.qnt').read_text());assert len(selected)==8
    run('typecheck',[tool,'typecheck','retirement_readiness_tests.qnt'],folder)
    run('selected',[tool,'test','retirement_readiness_tests.qnt','--main=retirement_readiness_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=930051','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
    assert len(list(out.glob('named-*.itf.json')))==8
    run('samples',[tool,'run','retirement_readiness.qnt','--main=retirement_readiness','--backend=typescript','--invariant=safety','--seed=930052','--max-samples=200','--max-steps=30','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
    traces=[];compared=0
    for path in sorted(out.glob('*.itf.json')):
        proof=json.loads(run('replay-'+path.stem,[str(out/'checks'),str(path)]));assert proof['passed'];compared+=proof['statesCompared'];traces.append({'path':str(path),'statesCompared':proof['statesCompared']})
    mutants=[]
    for name,old,new,witness in [
        ('forget-accepted-ready','row->second.readyAccepted=true;return true;','row->second.readyAccepted=false;return true;','exactReadinessRetained'),
        ('invent-unaccepted-readiness','if(!row.readyAccepted || row.completion)continue;','if(row.completion)continue;','observationDoesNotInventReadiness'),
        ('ignore-receiver-epoch','popup==popup_ && epoch==epoch_ && binding==owner_','popup==popup_ && (epoch==epoch_ || epoch!=epoch_) && binding==owner_','foreignEpochCannotReadReady')]:
        changed=out/name;shutil.copytree(out/'inputs',changed);p=changed/'native/retirement_journal.hpp';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
        mutant_args=[*args];mutant_args[mutant_args.index('-o')+1]=str(changed/'checks');run(name+'-compile',mutant_args,changed)
        trace=next(out.glob('named-'+witness+'-*.itf.json'))
        p=subprocess.run([str(changed/'checks'),str(trace)],capture_output=True,text=True,timeout=180)
        (changed/'replay.stdout').write_text(p.stdout);(changed/'replay.stderr').write_text(p.stderr)
        wanted='Compiled transport outcome' if name=='ignore-receiver-epoch' else 'Compiled retained readiness membership'
        assert p.returncode==1 and wanted in p.stderr and 'Sanitizer' not in p.stderr,(name,p.stdout,p.stderr)
        mutants.append({'name':name,'compiled':True,'witness':witness,'namedObservableMismatch':True})
    assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
    report.update(passed=True,namedScenarios=8,invariantSamples=200,coupledTraces=traces,statesCompared=compared,unsafeCompiledNativeMutantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1300]}),flush=True);sys.exit(not report['passed'])
