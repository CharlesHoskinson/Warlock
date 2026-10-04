"""Match actual held Qt250 C++ grammar; real subprocess backpressure control."""
import ast,fcntl,hashlib,json,os,re,resource,shlex,subprocess,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from actor import Actor,command
from journal import Refused
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'qa'/('commands-'+str(time.time_ns()));out.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'fakeJournalRealSubprocessOnly':True,'checks':[]}
def check(name,condition):assert condition,name;report['checks'].append({'name':name,'passed':True})
def refused(name,fn):
 try:fn()
 except Refused:check(name,True)
 else:check(name,False)
fixture=ROOT.parent/'elm-qt6-role-journal-fixture-v250'
class Original:
 @staticmethod
 def process(pid):return {'pid':pid,'start':Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]}
def launch(name,source,profile='window-modal'):
 case=out/name;case.mkdir();binary=case/'fake-client';binary.write_text(source);binary.chmod(0o700)
 session=SimpleNamespace(host=SimpleNamespace(runtime=out,processes=[]),env=dict(os.environ),guard=lambda:None)
 return Actor(session,SimpleNamespace(original=Original),binary,case/'evidence',time.monotonic()+1,profile=profile)
try:
 header=out/'commands.hpp';header.write_bytes((fixture/'native/commands.hpp').read_bytes())
 source=out/'grammar.cpp';source.write_text('#include "commands.hpp"\n#include <iostream>\nint main(){std::string s;while(std::getline(std::cin,s)){Command c;std::cout<<(parseCommand(s,c)?"yes":"no")<<std::endl;}}\n')
 binary=out/'grammar';deps=out/'grammar.d';args=['/usr/bin/c++','-std=c++17','-Wall','-Wextra','-Werror','-MD','-MF',str(deps),str(source),'-o',str(binary)]
 p=subprocess.run(args,capture_output=True,timeout=20);(out/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0
 paths=shlex.split(deps.read_text().split(':',1)[1].replace('\\\n',' '))
 ldd=subprocess.check_output(['/usr/bin/ldd',str(binary)],text=True,timeout=3);(out/'ldd.txt').write_text(ldd)
 paths+=re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',ldd,re.M)+['/usr/bin/c++','/usr/bin/ldd','/usr/bin/python3']
 report['externalFiles']={str(Path(p).resolve()):sha(p) for p in paths if not Path(p).resolve().is_relative_to(ROOT.resolve())}
 accepted=[(o,None) for o in ('open-owner','create-owners','create-family','open-modal','close-modal','close-owner','open-nested','close-nested','open-popup','close-popup','inspect','quit')]+[(o,r) for o in ('minimize','restore','maximize','unmaximize','reparent-modal') for r in ('A','C')]
 payload=b''.join(command(i,o,r) for i,(o,r) in enumerate(accepted,1))
 p=subprocess.run([str(binary)],input=payload,capture_output=True,timeout=3)
 check('actual-C++-grammar-all-22-generated-commands',p.returncode==0 and p.stdout.splitlines()==[b'yes']*len(accepted))
 for i,(seq,op,role) in enumerate([(0,'quit',None),(True,'quit',None),(2**63,'quit',None),(1,[] ,None),(1,'inspect','A'),(1,'open-popover',None),(1,'reparent-modal','B'),(1,'reparent-modal',True),(1,'maximize',None)]):refused('invalid-command-'+str(i),lambda s=seq,o=op,r=role:command(s,o,r))
 tree=ast.parse((ROOT/'qa/actor-test.py').read_text())
 fake=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source' for t in n.targets)).replace('MODE','pass')
 actor=launch('ordered-commands',fake)
 try:
  for op,role in [('open-owner',None),('reparent-modal','C'),('maximize','C'),('unmaximize','C'),('open-popup',None),('close-popup',None)]:actor.send(op,time.monotonic()+1,role)
  before=len(actor.record['commands']);refused('invalid-target-not-written',lambda:actor.send('reparent-modal',time.monotonic()+1,'B'));check('no-invalid-attempt-recorded',len(actor.record['commands'])==before)
  actor.close(time.monotonic()+1)
  check('complete-ordered-receipts-and-real-normal-exit',actor.record['normalExit'] and actor.process.returncode==0 and len([r for r in actor.rows if r['event']=='request'])==7)
 finally:actor.abort()
 stalled=fake.replace("emit('ready')", "emit('ready');time.sleep(5)")
 actor=launch('backpressure',stalled)
 try:
  fd=actor.process.stdin.fileno();capacity=fcntl.fcntl(fd,fcntl.F_GETPIPE_SZ)
  assert os.write(fd,b'x'*capacity)==capacity
  deadline=time.monotonic()+.06
  refused('full-pipe-absolute-deadline-refused',lambda:actor.send('inspect',deadline))
  attempt=actor.record['commands'][-1]
  check('full-pipe-no-write-no-replay',attempt.get('bytesWritten',0)==0 and not attempt.get('written',False) and len(actor.record['commands'])==1)
 finally:actor.abort()
 check('backpressure-child-reaped-with-recorded-failure-cleanup',actor.process.returncode==-15 and actor.record['failureCleanupTerminate'] is True)
 report.update(passed=True,compilerSHA256=sha('/usr/bin/c++'),grammarSourceSHA256=sha(source),grammarBinarySHA256=sha(binary),owningCommandsSHA256=sha(header),compileCommand=args)
finally:
 report['inputs']={str(p):sha(p) for p in (Path(__file__),ROOT/'qa/actor.py',ROOT/'qa/journal.py',ROOT/'qa/actor-test.py',fixture/'native/commands.hpp',fixture/'component-manifest.json')}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
