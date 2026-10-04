"""Actual captured V132 Python functions, private durable store and owned pipes.

Endpoint/catalog/event acquisition are CPU doubles: no compositor, GTK or native
execution. Blocking-output witness is a unit availability limit, not a GUI fault.
"""
import hashlib, json, os, resource, shlex, shutil, socket, subprocess, sys, time, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = next(p for p in ROOT.parents if (p / 'AGENTS.md').is_file())
SOURCE = ROOT

def load(adapter):
    sys.path.insert(0, str(adapter))
    import daemon
    return daemon

if len(sys.argv) > 1 and sys.argv[1] == 'worker':
    daemon = load(Path(sys.argv[2]))
    if sys.argv[3] == 'backpressure':
        try:
            daemon.send({'protocolVersion':3,'kind':'host-refresh','payload':'x'*500000})
        except daemon.OutputFailure:
            try: daemon.send({'protocolVersion':3,'kind':'host-disconnected'})
            except daemon.OutputFailure: raise SystemExit(7)
        raise SystemExit(8)
    if sys.argv[3] == 'concurrent':
        import threading
        threads=[threading.Thread(target=lambda n=n: [daemon.send({'thread':n,'index':i}) for i in range(20)]) for n in range(4)]
        for thread in threads:thread.start()
        for thread in threads:thread.join()
        raise SystemExit(0)
    if sys.argv[3] == 'confirmed-delivery-failure':
        from recovery_store import RecoveryStore
        config=json.loads(Path(sys.argv[4]).read_text())
        bound={'lifetime':'9007199254740993','session':'8','frontend':'1'}
        intent={'request':'42','generation':'44','incarnation':'8','operation':'minimize','context':{'lifetime':bound['lifetime'],'epoch':'1','output':'3','revision':'4'}}
        class Client:
            def effect(self, incoming):
                assert incoming==intent
                return {'protocolVersion':3,'kind':'effect-outcome','effectProtocol':1,'binding':bound,'intent':intent,'status':'Committed','reason':'','revision':'5','outputGeneration':'3'}
        client=Client();client.bound=bound
        with RecoveryStore(config['runtime'],config['instance'],bound['lifetime']) as store:
            command=[sys.argv[5],sys.argv[4],json.dumps([{'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':bound,'intent':intent}]),json.dumps(bound)]
            assert subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
            os.set_blocking(1,False)
            while True:
                try:os.write(1,b' ' * 4096)
                except BlockingIOError:break
            try:daemon.handle_request(client,None,{'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':bound,'intent':intent},store)
            except daemon.OutputFailure:raise SystemExit(7)
        raise SystemExit(8)
    config = Path(sys.argv[4])
    class Endpoint:
        def __init__(self, **kwargs): self.bound = {'lifetime':'9007199254740993','session':'8','frontend':'1'}
        def hello(self): return {'protocolVersion':3,'kind':'attached','binding':self.bound}
    events, peer = socket.socketpair()
    daemon.Endpoint = Endpoint
    daemon.CatalogTransport = lambda *args: None
    daemon.event_socket = lambda client: events
    if sys.argv[3] == 'startup-backpressure':
        os.set_blocking(1,False)
        while True:
            try:os.write(1,b' '*4096)
            except BlockingIOError:break
    sys.argv = ['daemon', str(config)]
    raise SystemExit(daemon.run())

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
OUT = ROOT / 'qa' / ('review-' + str(time.time_ns()))
(OUT / 'inputs/adapter').mkdir(parents=True)
shutil.copy2(__file__, OUT / 'inputs/review.py')
for p in (SOURCE / 'adapter').glob('*.py'):
    shutil.copy2(p, OUT / 'inputs/adapter' / p.name)
adapter = OUT / 'inputs/adapter'
daemon = load(adapter)
from recovery_store import RecoveryStore
from endpoint import Refused
checks = []
report = {'passed':False, 'nativeAcceptance':False, 'releaseAcceptance':False,
          'scope':'Actual V132 broker framing/send/recovery store with CPU endpoint/catalog/event doubles and owned pipes; no native execution',
          'checks':checks, 'sourceInputs':{str(p.relative_to(SOURCE)):hashlib.sha256(p.read_bytes()).hexdigest() for base in ['adapter','native'] for p in (SOURCE/base).glob('*') if p.is_file()}}
processes = []
def check(name, condition):
    checks.append({'name':name,'passed':bool(condition)})
    assert condition, name
def refused(fn):
    try: fn()
    except Refused: return True
    return False
try:
    runtime = OUT / 'runtime'; runtime.mkdir(mode=0o700)
    config = OUT / 'config.json'
    config.write_text(json.dumps({'runtime':str(runtime),'instance':'qa_eof_134'})); config.chmod(0o600)
    worker = [sys.executable,'-B',str(OUT/'inputs/review.py'),'worker',str(adapter)]
    for payload, expected, name in [(b'',0,'empty EOF'), (b'{',1,'truncated EOF'),
                                  (b'{"kind":"unknown"}\n',1,'closed unsupported request')]:
        child = subprocess.Popen(worker+['main',str(config)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        processes.append(child)
        started=time.monotonic(); out, err=child.communicate(payload,timeout=3)
        frames=[json.loads(line) for line in out.splitlines()]
        check(name+' normal/failure code',child.returncode==expected)
        check(name+' current full attached binding',frames[0]['binding']=={'lifetime':'9007199254740993','session':'8','frontend':'1'})
        check(name+' disconnect only on failure',any(f['kind']=='host-disconnected' for f in frames)==bool(expected))
        check(name+' bounded owned CPU completion',time.monotonic()-started<3)
    bound={'lifetime':'9007199254740993','session':'8','frontend':'1'}
    intent={'request':'41','generation':'43','incarnation':'7','operation':'minimize',
            'context':{'lifetime':bound['lifetime'],'epoch':'1','output':'3','revision':'4'}}
    native=OUT/'inputs/native';native.mkdir()
    for name in ['admission-test.c','host-journal.h','surface.h']:
        shutil.copy2(SOURCE/'native'/name,native/name)
    flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True))
    command=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function',str(native/'admission-test.c'),'-o',str(OUT/'admission'),*flags]
    compiled=subprocess.run(command,capture_output=True,text=True,timeout=90)
    (OUT/'compile.stdout').write_text(compiled.stdout);(OUT/'compile.stderr').write_text(compiled.stderr)
    report['compileCommand']=command
    check('actual C schema5 host admission helper compiles',compiled.returncode==0)
    with RecoveryStore(runtime,'qa_eof_134',bound['lifetime']) as store:
        admitted=subprocess.run([str(OUT/'admission'),str(config),json.dumps([{'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':bound,'intent':intent}]),json.dumps(bound)],capture_output=True,text=True,timeout=3)
        report['admissionRun']={'exitCode':admitted.returncode,'stdout':admitted.stdout,'stderr':admitted.stderr}
        check('actual C admits original full key before broker begin',admitted.returncode==0)
        check('durable initial exact intent accepted',store.begin(bound,intent,1) is True)
        check('same exact intent never resubmitted',store.begin(bound,intent,1) is False)
    renewed=dict(bound,session='9',frontend='2')
    with RecoveryStore(runtime,'qa_eof_134',bound['lifetime']) as store:
        unknown=store.recovery_frames(renewed)
        check('reopened schema5 preserves original full intent',unknown[1]['intent']==intent)
        check('recovery transport binds current session/frontend',unknown[1]['binding']==renewed)
        check('durable unresolved record retains original issued binding',store.read()['binding']==bound)
        check('watermarks preserve counters',unknown[0]['request']=='41' and unknown[0]['generation']=='43')
        check('foreign lifetime refused',refused(lambda:store.recovery_frames(dict(renewed,lifetime='2'))))
    frames=daemon.FrontendFrames()
    check('exact4096 newline-inclusive frame accepted',list(frames.feed(b'x'*4095+b'\n'))==[b'x'*4095])
    check('oversized frame refused',refused(lambda:list(daemon.FrontendFrames().feed(b'x'*4096))))
    frames=daemon.FrontendFrames();list(frames.feed(b'{'))
    check('partial final frame is not normal EOF',refused(frames.finish))
    child=subprocess.Popen(worker+['concurrent'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    processes.append(child);out,err=child.communicate(b'',timeout=3)
    packets=[json.loads(line) for line in out.splitlines()]
    check('concurrent output complete atomic frames',child.returncode==0 and len(packets)==80 and not err)
    check('every concurrent frame delivered once',len({(p['thread'],p['index']) for p in packets})==80)
    disk=OUT/'regular-output'
    with disk.open('wb') as stream:
        child=subprocess.Popen(worker+['concurrent'],stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.PIPE)
        processes.append(child);child.wait(timeout=3)
    check('regular-file stdout remains supported',child.returncode==0 and len(disk.read_bytes().splitlines())==80)
    for mode in ['backpressure','confirmed-delivery-failure','startup-backpressure']:
        child=subprocess.Popen(worker+[mode,str(config),str(OUT/'admission')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        processes.append(child);child.stdin.close();child.stdin=None
        started=time.monotonic();child.wait(timeout=3.8);elapsed=time.monotonic()-started
        out,err=child.communicate(timeout=1)
        check(mode+' bounded failure instead of indefinite hang',child.returncode==(1 if mode=='startup-backpressure' else 7) and 2.8<=elapsed<3.8)
        check(mode+' no appended disconnected receipt/trailer',b'host-disconnected' not in out)
        if mode=='backpressure':check('partial output does not become completed frame',bool(out) and b'\n' not in out)
    with RecoveryStore(runtime,'qa_eof_134',bound['lifetime']) as store:
        state=store.read()
        check('delivery failure preserves confirmed durable status',state['status']=='Committed' and state['intent']['request']=='42')
        settlements=store.settlement_frames(renewed)
        check('renewed frontend synchronizes original confirmed full key',any(f['record']['binding']==bound and f['record']['intent']==state['intent'] for f in settlements))
        check('confirmed original key is not recovered as Unknown',not any(f['kind']=='host-uncertain' and f['intent']==state['intent'] for f in store.recovery_frames(renewed)))
    child=subprocess.Popen(worker+['main',str(config)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    processes.append(child);child.stdout.close();child.stdin.close();child.stdin=None
    started=time.monotonic();child.wait(timeout=1)
    check('closed output peer causes prompt failure without exception-cleanup retry',child.returncode==1 and time.monotonic()-started<1)
    report['passed']=True
except Exception as error:
    report.update(error=repr(error),traceback=traceback.format_exc())
finally:
    for child in processes:
        if child.poll() is None:
            child.terminate()
            try:child.wait(timeout=3)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=3)
    report['processExitCodes']=[p.returncode for p in processes]
    report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}))
    raise SystemExit(not report['passed'])
