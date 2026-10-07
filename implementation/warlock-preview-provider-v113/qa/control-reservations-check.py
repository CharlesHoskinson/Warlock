"""Explicit Quint traces against actual native cleanup reservations and C dispatch."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('control-reservations-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]
names+=['spec/control_reservations.qnt','spec/control_reservations_tests.qnt','qa/control-reservations-check.py']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual inactive native reservation bank and C dispatcher/confirmation matched after every selected and sampled Quint event: capacity, reserved ordinal tail, immutable slot tickets, exact grant, retained prefixes and confirmation barrier. Synthetic native-approved command bodies; explicit first-event near-exhaustion fixture uses a separate grant representing a prior confirmed history. No physical admission, actual cleanup budget derivation, WebKit, effects, reload or native/full release acceptance.'}
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
    args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/control-reservations-replay.cpp','-o',str(out/'checks'),*flags]
    run('compile',args)
    folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'control_reservations_tests.qnt').read_text());assert len(selected)==11
    run('typecheck',[tool,'typecheck','control_reservations_tests.qnt'],folder)
    run('selected',[tool,'test','control_reservations_tests.qnt','--main=control_reservations_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=970051','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
    assert len(list(out.glob('named-*.itf.json')))==11
    run('samples',[tool,'run','control_reservations.qnt','--main=control_reservations','--backend=typescript','--invariant=safety','--seed=970052','--max-samples=200','--max-steps=30','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
    traces=[];compared=0
    for path in sorted(out.glob('*.itf.json')):
        proof=json.loads(run('replay-'+path.stem,[str(out/'checks'),str(path)]));assert proof['passed'];compared+=proof['statesCompared'];traces.append({'path':str(path),'statesCompared':proof['statesCompared']})
    mutants=[]
    for name,old,new,witness,oracle in [
        ('spend-reserved-ordinal-tail','reserved_>remaining-quota','false','reservedOrdinalTailProtectsCleanup','Compiled reservation membership'),
        ('reset-issued-on-release','rows_.erase(found);return true;','rows_.erase(found);issued_=0;return true;','confirmedReleaseNeverResetsIssuer','Compiled original issued prefix'),
        ('release-unconfirmed-ticket','if(ordinal>channel_.confirmed)return false;','if(ordinal>channel_.confirmed && false)return false;','unconfirmedTicketKeepsReservation','Compiled reservation membership'),
        ('discard-original-slot-ticket','if(previous!=row.slots.end()) {','if(previous!=row.slots.end() && false) {','sameSlotRetryKeepsOriginalOrdinal','Compiled original admission outcome')]:
        changed=out/name;shutil.copytree(out/'inputs',changed);p=changed/'native/control_reservations.hpp';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
        mutant_args=[*args];mutant_args[mutant_args.index('-o')+1]=str(changed/'checks');run(name+'-compile',mutant_args,changed)
        trace=next(out.glob('named-'+witness+'-*.itf.json'))
        p=subprocess.run([str(changed/'checks'),str(trace)],capture_output=True,text=True,timeout=180)
        (changed/'replay.stdout').write_text(p.stdout);(changed/'replay.stderr').write_text(p.stderr)
        assert p.returncode==1 and oracle in p.stderr and 'Sanitizer' not in p.stderr,(name,p.stdout,p.stderr)
        mutants.append({'name':name,'compiled':True,'witness':witness,'namedObservableMismatch':True,'oracle':oracle})
    assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
    report.update(passed=True,namedScenarios=11,invariantSamples=200,coupledTraces=traces,statesCompared=compared,unsafeCompiledNativeMutantsDetected=4,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1300]}),flush=True);sys.exit(not report['passed'])
