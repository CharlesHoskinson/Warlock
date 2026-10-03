"""Real own IPC/kernel same-gap regression against bounded V15 arm; no GUI."""
from pathlib import Path
import importlib.util,json,hashlib,os,socket,subprocess,tempfile,threading,time
from unittest.mock import patch
from types import SimpleNamespace
import helper_observer as observer,helper_setup
from test_evaluations import EvaluationProtocol
B=Path(__file__).resolve().parent;OLD=B.with_name('toolkit-held-matrix-v14')
import evaluation_setup as setup
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();report={};child=None;thread=None;stop=threading.Event()
try:
 with tempfile.TemporaryDirectory()as d:
  root=Path(d);config,_,_=EvaluationProtocol().fixture(root,'reload');harness=config['queryRoots']['harness'];harness.update(source=str(Path(__file__).resolve()),sourceSHA256=sha(Path(__file__)))
  for ticket in config['evaluationTickets']:ticket['root']=dict(harness)
  endpoint=root/'owned.sock';server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(str(endpoint));server.listen();server.settimeout(.1)
  raw=b'{"version":"owned CPU fixture only"}';st=endpoint.stat();config.update(socket=str(endpoint),socketIdentity=[st.st_dev,st.st_ino,st.st_uid],versionSHA256=observer.digest_bytes(raw))
  for ticket in config['evaluationTickets']:
   ticket['armIPC'].update(socketIdentity=config['socketIdentity'],replySHA256=config['versionSHA256'])
  requests=[]
  def serve():
   while not stop.is_set():
    try:conn,_=server.accept()
    except socket.timeout:continue
    with conn:
     value=conn.recv(32);requests.append(value.decode());assert value==b'j/version';conn.sendall(raw)
  thread=threading.Thread(target=serve);thread.start()
  entry=root/'exact-owned-entry';entry.write_text('#!/usr/bin/python3\nimport sys\nprint("ready",flush=True)\nsys.stdin.read()\n');entry.chmod(0o700)
  config.update(helpers={'snap':{'wrapper':str(entry),'actual':str(root/'exact-owned-actual')},'shell':{'wrapper':str(root/'exact-owned-shell'),'actual':str(root/'exact-owned-shell-actual'),'invocation':'owned-unused-shell'}},log=str(root/'journal.jsonl'),allowed=[])
  Path(config['log']).touch(mode=0o600);path=root/'config.json';helper_setup.write_json(path,config)
  controls=[]
  def cpu_ctl(*args):
   controls.append(list(args));assert args[0]=='repl'
   if 'print(table.concat' in args[1]:
    ticket=config['evaluationTickets'][-1];return '\n'.join([ticket['nonce'],ticket['kind'],str(ticket['count']),'0'])
   assert 'hl.env(' in args[1];return ''
  session=SimpleNamespace(guard=lambda:None,ctl=cpu_ctl,evidence={})
  evaluation=setup.Evaluations({'WINDOW_QA_HELPER_CONFIG':str(path)},config,session,root,{})
  original=observer.evaluation_operation;observations={};real_pending=setup.pending_helper_processes;release_event=threading.Event()
  def pending_after_auth(*args):
   value=real_pending(*args)
   if value and child is not None:release_event.set()
   return value
  def auth_then_spawn(*args):
   global child
   result=original(*args);observations['configBeforeSpawn']=observer.read_config(path)==config;observations['quietBeforeSpawn']=setup.pending_helper_processes(config)==[]
   if child is not None:return result
   child=subprocess.Popen([str(entry)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert child.stdout.readline().strip()=='ready'
   def release():
    assert release_event.wait(3);child.stdin.close();child.wait(timeout=3)
   release_thread=threading.Thread(target=release);release_thread.start();observations['releaseThread']=release_thread
   observations['identity']=observer.process(child.pid);observations['exactPendingAfterAuth']=real_pending(config);return result
  with patch.object(observer,'evaluation_operation',side_effect=auth_then_spawn),patch.object(setup,'pending_helper_processes',side_effect=pending_after_auth):
   ticket=evaluation.arm('reload',['reload'])
  assert observations['configBeforeSpawn'] and observations['quietBeforeSpawn'] and len(observations['exactPendingAfterAuth'])==1
  assert observer.read_config(path)==config and len(config['evaluationTickets'])==2 and evaluation.current==ticket
  observations.pop('releaseThread').join(3)
  child.wait(timeout=3);child.stdout.close();assert child.returncode==0 and setup.pending_helper_processes(config)==[]
  evidence=json.loads(Path(evaluation.report['evaluationArmDiagnostics'][0]).read_text());assert evidence['accepted'] and evidence['atomicReplaceOccurred'] and evidence['publicationObservedBeforeDeadline'];assert any(row.get('exactPendingProcesses')for row in evidence['attempts']);assert len([row for row in evidence['attempts']if row['stage']=='published'])==1
  stop.set();thread.join(2);server.close();assert not thread.is_alive()
  report=dict(result='pass actual owned kernel repaired gap',observations=observations,configurationPublishedExactlyOnce=True,prospectiveTicketUnpublishedUntilQuiet=True,armEvidence=evidence,controls=controls,helperExitedNormally=child.returncode==0,ipcRequests=requests,selectedIPCFullEOF=True,originalEvaluationSourceSHA256=sha(OLD/'evaluation_setup.py'),cpuFixtureOnly=True,actualV14ArmBranchProved=False,nativeLaunch=False)
except BaseException as error:report=dict(result='fail',error=repr(error),traceback=__import__('traceback').format_exc(),nativeLaunch=False)
finally:
 if child and child.poll()is None:child.stdin.close();child.wait(timeout=3)
 stop.set()
 if thread:thread.join(2)
fd=os.open(B/'arm-kernel-repaired-publication-final.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w')as out:json.dump(report,out,indent=2);out.write('\n')
print(json.dumps(report));raise SystemExit(report['result'].startswith('fail'))
