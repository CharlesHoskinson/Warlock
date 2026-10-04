#!/usr/bin/python3
"""Real filesystem + unchanged compiled C admissions; no compositor launched."""
import copy, hashlib, json, os, pathlib, stat, subprocess, sys, tempfile, time
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapter'))
from retirement_ledger import RetirementLedger, ObservationJoin, release_payload
from grant_endpoint import NativeBinding, RetirementProof
from admission_ledger import AdmissionLedger, storage_key
from durable_ledger import encoded, key
from endpoint import Refused

OLD={'lifetime':'19','session':'1','frontend':'1'}
NOW={'lifetime':'19','session':'2','frontend':'1'}
def record(bound=OLD,number='12',target='2',status='Unknown',protocol=1):
    return {'schema':2,'effectProtocol':protocol,'binding':copy.deepcopy(bound),'status':status,
            'intent':{'request':number,'generation':number,'incarnation':target,
                      'operation':'minimize' if protocol==1 else 'maximize',
                      'context':{'lifetime':bound['lifetime'],'epoch':bound['frontend'],'output':'7','revision':'21'}}}
def join(r=None):
    r=r or record()
    proof=RetirementProof(NativeBinding.parse(NOW),NativeBinding.parse(r['binding']),'3','19','retire','Retired')
    value=ObservationJoin(r,proof)
    value.expect('action','91'); value.expect('geometry','37')
    value.accept('action','91',NOW,{'lifetime':'19','epoch':'1','output':'7','revision':'22'})
    value.accept('geometry','37',NOW,{'lifetime':'19','epoch':'1','output':'7','revision':'29'})
    return value
def child(runtime,stop,mode):
    ledger=RetirementLedger(runtime,'Test','19'); events=[]
    originals={n:getattr(os,n) for n in ['fsync','replace','unlink']}
    def wrap(name):
        def call(*a,**kw):
            if mode=='before-failure' and len(events)+1==int(stop):
                events.append(name);raise OSError('injected before '+name)
            result=originals[name](*a,**kw)
            # _save finally cleans an already renamed temporary; ignore ENOENT.
            events.append(name)
            if len(events)==int(stop):
                if mode=='crash': os._exit(73)
                raise OSError('injected after '+name)
            return result
        return call
    try:
        with patch.multiple(os,**{n:wrap(n) for n in originals}): ledger.release(join())
    except OSError:
        assert ledger.poisoned
        try:ledger.snapshot()
        except Refused:pass
        else:raise AssertionError('Storage failure acknowledged further state')
        pathlib.Path(runtime,'fault.json').write_text(json.dumps(events)); ledger.close(); return 74
    ledger.close(); return 0
if len(sys.argv)>1 and sys.argv[1]=='child':sys.exit(child(*sys.argv[2:]))

OUT=ROOT/'qa'/('tests-'+str(time.time_ns()));OUT.mkdir()
checks=[]
def check(name,condition):
    checks.append({'name':name,'passed':bool(condition)})
    if not condition:raise AssertionError(name)
def denied(name,fn):
    try:fn()
    except (Refused,OSError,ValueError):check(name,True)
    else:check(name,False)
def call(args):
    p=subprocess.run(args,capture_output=True,text=True)
    return p
flags=call(['pkg-config','--cflags','--libs','json-glib-1.0']).stdout.split()
compiler=call(['cc','-std=gnu11','-O2',str(ROOT/'native/admission-test.c'),'-o',str(OUT/'admission-test'),*flags])
(OUT/'compile.stdout').write_text(compiler.stdout);(OUT/'compile.stderr').write_text(compiler.stderr)
check('unchanged actual C admission producer compiles',compiler.returncode==0)
def setup(runtime,protocol=1):
    runtime.mkdir(mode=0o700)
    config=runtime/'config.json';config.write_bytes(encoded({'runtime':str(runtime),'instance':'Test'}));config.chmod(0o600)
    host(runtime,record(status='Pending',protocol=protocol),0)
    ledger=RetirementLedger(str(runtime),'Test','19')
    return ledger
def host(runtime,r,expected):
    request={'protocolVersion':3,'kind':'window-effect','effectProtocol':r['effectProtocol'],'binding':r['binding'],'intent':r['intent']}
    p=call([str(OUT/'admission-test'),str(runtime/'config.json'),json.dumps([request]),json.dumps(r['binding'])])
    check('real C admission exit '+str(expected),p.returncode==expected)
def admission_path(ledger,r):return ledger.path/'admissions-v1'/(storage_key(r)+'.json')
try:
    runtime=OUT/'normal'; ledger=setup(runtime)
    initial=ledger.snapshot(); old5=(ledger.path/'ledger-v5.json').read_bytes()
    check('C Pending imported as Unknown',initial['entries']==[record()])
    check('Unknown target blocks before proof',ledger.blocked('19','2'))
    host(runtime,record(NOW,'13',status='Pending'),1)
    value=join(); events=[]
    originals={n:getattr(os,n) for n in ['fsync','replace','unlink']}
    def logged(name):
        def f(*a,**kw):
            result=originals[name](*a,**kw)
            events.append({'op':name,'directory':stat.S_ISDIR(os.fstat(a[0]).st_mode) if name=='fsync' else None})
            return result
        return f
    with patch.multiple(os,**{n:logged(n) for n in originals}):release=ledger.release(value)
    (OUT/'release-order.json').write_text(json.dumps(events,indent=2))
    check('prepare file + rename + root barrier before unlink + admission barrier + final file/rename/root',
          [e['op'] for e in events]==['fsync','fsync','replace','fsync','unlink','fsync','fsync','replace','fsync'] and
          [e['directory'] for e in events if e['op']=='fsync']==[True,False,True,True,False,True])
    state=ledger.snapshot()
    check('release returned only final durable phase',release['phase']=='Released')
    check('historical Unknown exact and latest never Committed',state['releases'][0]['record']==record() and state['latest'] is None)
    check('exact admission gone',not admission_path(ledger,record()).exists())
    check('live reservation released',not ledger.blocked('19','2') and state['entries']==[])
    check('independent read IDs revisions retained',release['observation']==value.observation())
    check('v5 predecessor remains byte-identical',old5==(ledger.path/'ledger-v5.json').read_bytes())
    ledger.close();ledger=RetirementLedger(str(runtime),'Test','19')
    check('release idempotent across restart',ledger.release(join())==release)
    fresh=join();fresh.proof.update(requestId='4',sequence='20')
    fresh.requested.update(action='92',geometry='38')
    fresh.accepted['action']['revision']='23';fresh.accepted['geometry']['revision']='30'
    check('fresh valid join preserves immutable first disposition',ledger.release(fresh)==release)
    check('fresh join never relabels stored read IDs',ledger.snapshot()['releases'][0]['observation']==value.observation())
    host(runtime,record(status='Pending'),0)
    ledger.synchronization_snapshot()
    check('late exact C key removed without resurrection',not admission_path(ledger,record()).exists() and not ledger.blocked('19','2'))
    denied('retired binding cannot submit different new intent',lambda:ledger.begin(OLD,record(OLD,'13')['intent']))
    host(runtime,record(NOW,'13',status='Pending'),0)
    check('only fresh explicit C-admitted next request can begin',ledger.begin(NOW,record(NOW,'13')['intent']))
    check('new request does not rewrite old history',ledger.snapshot()['releases'][0]['record']==record())
    denied('new request blocks duplicate target',lambda:ledger.begin(NOW,record(NOW,'14')['intent']))
    ledger.close()

    for outcome in ['Committed','Refused']:
        runtime=OUT/('settled-absence-fsync-'+outcome);ledger=setup(runtime)
        ledger._settle_record(record(status=outcome));admission_path(ledger,record()).unlink()
        real_fsync=os.fsync
        def failing_admission_fsync(fd):
            if pathlib.Path('/proc/self/fd/'+str(fd)).readlink().name=='admissions-v1':raise OSError('admission absence fsync EIO')
            return real_fsync(fd)
        try:
            with patch.object(os,'fsync',failing_admission_fsync):ledger.synchronization_snapshot()
        except OSError:check('definitive absence barrier failure propagates '+outcome,True)
        else:check('definitive absence barrier failure propagates '+outcome,False)
        check('inherited absence barrier error poisons '+outcome,ledger.poisoned)
        denied('absence barrier poison snapshot '+outcome,ledger.snapshot)
        denied('absence barrier poison begin '+outcome,lambda:ledger.begin(NOW,record(NOW,'13')['intent']))
        denied('absence barrier poison release '+outcome,lambda:ledger.release(join()))
        ledger.close();ledger=RetirementLedger(str(runtime),'Test','19')
        check('absence barrier corrected on explicit reopen '+outcome,ledger.snapshot()['settled']==[] and ledger.snapshot()['settlementHistory']==[record(status=outcome)])
        ledger.close()

    # Matching latest Unknown remains full history after removing its live entry.
    runtime=OUT/'latest';ledger=setup(runtime)
    state=ledger.snapshot();state['latest']=copy.deepcopy(state['entries'][0]);ledger._save(state)
    ledger.release(join());check('latest Unknown is preserved with released history',ledger.snapshot()['latest']==record());ledger.close()
    runtime=OUT/'protocol2';ledger=setup(runtime,2);ledger.release(join(record(protocol=2)))
    check('geometry effect protocol retains Unknown',ledger.snapshot()['releases'][0]['record']==record(protocol=2));ledger.close()

    for status in ['Pending','Unknown','Committed','Refused']:
        runtime=OUT/('migration-'+status);runtime.mkdir(mode=0o700)
        (runtime/'config.json').write_bytes(encoded({'runtime':str(runtime),'instance':'Test'}));(runtime/'config.json').chmod(0o600)
        host(runtime,record(status='Pending'),0)
        v5=AdmissionLedger(str(runtime),'Test','19')
        state=v5.snapshot();state['entries'][0]['status']=status if status in ['Pending','Unknown'] else 'Unknown';state['latest']=copy.deepcopy(state['entries'][0]);v5._save(state)
        if status in ['Committed','Refused']:v5._settle_record(record(status=status))
        path=v5.path;before=(path/'ledger-v5.json').read_bytes();v5.close()
        ledger=RetirementLedger(str(runtime),'Test','19');state=ledger.snapshot()
        check('populated V5 bytes unchanged '+status,(path/'ledger-v5.json').read_bytes()==before)
        if status in ['Pending','Unknown']:
            check('populated V5 normalized durably '+status,state['entries']==[record()] and state['latest']==record())
            broken=copy.deepcopy(state);broken['entries']=[];broken['latest']=None
            denied('populated predecessor cannot lose reservation '+status,lambda:ledger._validate(broken))
            ledger.release(join())
        else:
            check('populated definitive history retained '+status,state['settlementHistory']==[record(status=status)])
            admission_path(ledger,record()).unlink();ledger.synchronization_snapshot()
            check('definitive history survives admission disappearance '+status,ledger.snapshot()['settlementHistory']==[record(status=status)])
        ledger.close()

    for stage in ['Prepared','Released']:
        runtime=OUT/('cleanup-'+stage);ledger=setup(runtime);calls=[0];original=os.unlink
        def cleanup_failure(name,*a,**kw):
            if str(name).startswith('retirement-pending-'):
                calls[0]+=1
                if calls[0]==(1 if stage=='Prepared' else 2):raise OSError('cleanup EIO')
            return original(name,*a,**kw)
        try:
            with patch.object(os,'unlink',cleanup_failure):ledger.release(join())
        except OSError:check('cleanup error propagates '+stage,True)
        else:check('cleanup error propagates '+stage,False)
        check('cleanup error poisons '+stage,ledger.poisoned)
        denied('cleanup poison refuses snapshot '+stage,ledger.snapshot)
        denied('cleanup poison refuses begin '+stage,lambda:ledger.begin(NOW,record(NOW,'13')['intent']))
        denied('cleanup poison refuses release '+stage,lambda:ledger.release(join()))
        ledger.close();ledger=RetirementLedger(str(runtime),'Test','19')
        check('cleanup failure reopen completes barriers '+stage,not ledger.blocked('19','2'))
        ledger.close()

    runtime=OUT/'history-controls';ledger=setup(runtime);ledger.release(join());state=ledger.snapshot()
    broken=copy.deepcopy(state);broken['settled'].append(record(status='Committed'))
    denied('Released Unknown cannot also be Committed',lambda:ledger._validate(broken))
    broken=copy.deepcopy(state);broken['settlementHistory'].append(record(status='Refused'))
    denied('Released Unknown cannot also be definitive history',lambda:ledger._validate(broken))
    broken=copy.deepcopy(state);broken['releases']=[]
    denied('save cannot drop released history',lambda:ledger._save(broken))
    check('rejected history rewrite poisons writer',ledger.poisoned);ledger.close()

    runtime=OUT/'capacity-control';ledger=setup(runtime);state=ledger.snapshot()
    state['settlementHistory']=[record(OLD,str(100+i),str(100+i),'Committed') for i in range(64)]
    state['watermarks'][0].update(request='163',generation='163');ledger._save(state)
    host(runtime,record(NOW,'13','3',status='Pending'),0)
    denied('full synthetic definitive history refuses new effect before submit',lambda:ledger.begin(NOW,record(NOW,'13','3')['intent']))
    check('capacity refusal preserves old Unknown and all synthetic history',ledger.snapshot()['entries']==[record()] and len(ledger.snapshot()['settlementHistory'])==64)
    ledger.close()

    for stop in range(1,10):
        for mode in ['crash','failure','before-failure']:
            runtime=OUT/(mode+'-'+str(stop));ledger=setup(runtime);ledger.close()
            p=call([sys.executable,'-B',str(__file__),'child',str(runtime),str(stop),mode])
            (OUT/(mode+'-'+str(stop)+'.stderr')).write_text(p.stderr)
            check(mode+' interruption at boundary '+str(stop),p.returncode==(73 if mode=='crash' else 74))
            restart_events=[]
            saved={n:getattr(os,n) for n in ['fsync','unlink']}
            def restart_log(name):
                def f(*a,**kw):
                    result=saved[name](*a,**kw)
                    restart_events.append((name,stat.S_ISDIR(os.fstat(a[0]).st_mode) if name=='fsync' else None))
                    return result
                return f
            with patch.multiple(os,**{n:restart_log(n) for n in saved}):ledger=RetirementLedger(str(runtime),'Test','19')
            state=ledger.snapshot()
            prepared_visible=stop>=3 if mode!='before-failure' else stop>=4
            if not prepared_visible:
                check('unprepared restart stays blocked '+mode,ledger.blocked('19','2') and state['releases']==[])
                ledger.release(join())
            else:
                check('prepared/released restart completes both barriers '+mode+str(stop),not ledger.blocked('19','2') and state['releases'][0]['phase']=='Released')
                check('restart journal barrier before retiring/exposing '+mode+str(stop),restart_events[0]==('fsync',True))
                if any(e[0]=='unlink' for e in restart_events):check('restart barrier precedes unlink '+mode+str(stop),restart_events.index(('fsync',True))<next(i for i,e in enumerate(restart_events) if e[0]=='unlink'))
            check('restart never invents outcome '+mode+str(stop),ledger.snapshot()['releases'][0]['record']['status']=='Unknown')
            ledger.close()

    good=join();payload=release_payload(good.record,good.proof,good.observation())
    for field,bad in [('grantState','Registered'),('grantState','Future'),('sequence','0'),('sequence',True),('requestId','01'),('protocolVersion',True),('retirementProtocol',True),('operation','erase')]:
        p=copy.deepcopy(payload['proof']);p[field]=bad
        denied('proof rejects '+field+'='+str(bad),lambda p=p:release_payload(payload['record'],p,payload['observation']))
    for name,mutate in [
        ('foreign queried session',lambda p:p['proof']['queriedBinding'].update(session='3')),
        ('foreign proof lifetime',lambda p:p['proof']['binding'].update(lifetime='20')),
        ('Unknown cannot become Committed',lambda p:p['record'].update(status='Committed')),
        ('cross-generation reads',lambda p:p['observation']['geometryContext'].update(output='8')),
        ('foreign observation epoch',lambda p:p['observation']['actionContext'].update(epoch='2')),
        ('extra observation field',lambda p:p['observation'].update(extra='1'))]:
        p=copy.deepcopy(payload);mutate(p)
        denied(name,lambda p=p:release_payload(**p))
    partial=ObservationJoin(record(),RetirementProof(NativeBinding.parse(NOW),NativeBinding.parse(OLD),'3','19','retire','Retired'))
    denied('unsolicited read refused',lambda:partial.accept('action','91',NOW,payload['observation']['actionContext']))
    partial.expect('action','91')
    denied('wrong accepted read ID refused',lambda:partial.accept('action','90',NOW,payload['observation']['actionContext']))
    denied('current binding changed refused',lambda:partial.accept('action','91',OLD,payload['observation']['actionContext']))
    partial.accept('action','91',NOW,payload['observation']['actionContext'])
    denied('action alone cannot release',partial.observation)
    denied('duplicate accepted read refused',lambda:partial.accept('action','91',NOW,payload['observation']['actionContext']))

    for unsafe in ['symlink','hardlink','public','changed-predecessor','duplicate-json','missing-after-marker','marker-bool','marker-float']:
        runtime=OUT/unsafe;ledger=setup(runtime);path=ledger.path;ledger.close()
        ledgerfile=path/'ledger-v6.json'
        if unsafe=='symlink':
            backup=path/'original';ledgerfile.rename(backup);ledgerfile.symlink_to(backup.name)
        elif unsafe=='hardlink':os.link(ledgerfile,path/'alias')
        elif unsafe=='public':ledgerfile.chmod(0o644)
        elif unsafe=='changed-predecessor':
            p=path/'ledger-v5.json';p.write_bytes(p.read_bytes()+b' ')
        elif unsafe=='duplicate-json':ledgerfile.write_bytes(b'{"schema":6,"schema":6}')
        elif unsafe.startswith('marker-'):
            p=path/'ledger-v6.initialized';m=json.loads(p.read_text());m['schema']=True if unsafe=='marker-bool' else 1.0;p.write_bytes(encoded(m))
        else:ledgerfile.unlink()
        denied('unsafe store '+unsafe,lambda:RetirementLedger(str(runtime),'Test','19'))

    report={'passed':True,'checks':checks,'assertions':len(checks),'claim':'CPU filesystem ordering/crash-visible restart plus actual compiled C admissions only',
            'nativeAcceptance':False,'powerLossSimulation':False,'productionWired':False,'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['adapter','native'] for p in (ROOT/d).glob('*') if p.is_file()}}
except BaseException as error:
    report={'passed':False,'checks':checks,'error':repr(error)}
    raise
finally:
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(OUT/'report.json',flush=True)
