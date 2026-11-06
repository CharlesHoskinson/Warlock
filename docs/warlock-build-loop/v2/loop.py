#!/usr/bin/env python3
"""Always check the contributor contract; retain the original native QA launcher."""
import argparse,hashlib,importlib.util,pathlib,subprocess,sys
import fcntl,json,os,re,signal
from contextlib import contextmanager

# Exact archived coordinator and launcher bytes; only their host path changes.
PINNED_NATIVE_SOURCES = {
 'implementation/elm-build-loop-v1/loop.py': '13216f4226f4fdb2e439604459e860763ce351fa77cec0f6082c30195372dbd6',
 'window-integration-qa/qa_run.py': '656f118c268e9f762f2d62c859d146043d74c83b72cd5457b779f1e30cb183a1',
 'window-integration-qa/qa_launch.py': '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23',
}

def checked_native_source(root, relative):
 path=root
 for part in pathlib.PurePosixPath(relative).parts:
  path=path/part
  if path.is_symlink():raise ValueError('Native source symlink refused: '+relative)
 if not path.is_file():raise ValueError('Native source unavailable: '+relative)
 body=path.read_bytes()
 if hashlib.sha256(body).hexdigest()!=PINNED_NATIVE_SOURCES[relative]:
  raise ValueError('Pinned native source changed: '+relative)
 return path,body

def portable_coordinator(root):
 checked={name:checked_native_source(root,name) for name in PINNED_NATIVE_SOURCES}
 path,body=checked['implementation/elm-build-loop-v1/loop.py']
 spec=importlib.util.spec_from_file_location('_warlock_frozen_native_coordinator',path)
 module=importlib.util.module_from_spec(spec)
 # Execute the checked bytes, retaining every original lock/guard/supervisor.
 exec(compile(body,str(path),'exec'),module.__dict__)
 module.PROTECTED_LAUNCHER=checked['window-integration-qa/qa_run.py'][0]
 return module

def contributor_module(root):
 path=root/'plugins/warlock-contributor/scripts/warlock.py'
 spec=importlib.util.spec_from_file_location('_warlock_delivery_checker',path)
 module=importlib.util.module_from_spec(spec)
 exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
 return module

@contextmanager
def delivery_lock(checker,root):
 parent,name=checker.open_parent(checker.safe(root,'.warlock-contributor/.records.lock'),create=True)
 descriptor=None
 try:
  descriptor=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent)
  fcntl.flock(descriptor,fcntl.LOCK_EX)
  yield
 finally:
  if descriptor is not None:os.close(descriptor)
  os.close(parent)

def guarded_delivery_spawn(root,record_path,candidate,selection,scope,argv,spawn):
 """Recheck under the existing record lock at the actual spawn boundary.

 No participant event or acceptance is manufactured. Root records the actual
 launch receipt and consumes the outer job through the delivery event API.
 Source claims remain advisory against other processes sharing this UID.
 """
 checker=contributor_module(root)
 with delivery_lock(checker,root):
  reqs,state=checker.context(root)
  record=checker.read(checker.safe(root,record_path));record['_recordPath']=record_path
  checked=checker.validate_execution_precheck(root,record,reqs,state,candidate,scope,selection)
  action=checked['nextRootAction']
  if list(argv)!=action['argv']:raise ValueError('Protected command differs from reviewed delivery candidate')
  child=spawn()
  # A spawn exception leaves the record untouched. A post-spawn receipt error
  # must retire the owned process group rather than escape supervision.
  try:
   stat=(pathlib.Path('/proc')/str(child.pid)/'stat').read_text()
   birth=stat.rsplit(')',1)[1].split()[19]
   print(json.dumps({'deliveryLaunch':{'record':record_path,'candidateSha256':action['candidateSha256'],
         'selection':selection,'scope':scope,'pid':child.pid,'startTicks':birth,
         'argv':list(argv),'acceptanceInferred':False}}),flush=True)
  except BaseException:
   try:os.killpg(child.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   try:child.wait(timeout=5)
   except subprocess.TimeoutExpired:
    os.killpg(child.pid,signal.SIGKILL);child.wait()
   raise
  return child

class DeliverySubprocess:
 def __init__(self,original,root,args,scope):
  self.original,self.root,self.args,self.scope=original,root,args,scope
 def __getattr__(self,name):return getattr(self.original,name)
 def Popen(self,argv,**kwargs):
  if not kwargs.get('start_new_session'):raise ValueError('Protected delivery requires owned process-group supervision')
  return guarded_delivery_spawn(self.root,self.args.record,self.args.candidate,self.args.expect_selection,
      self.scope,argv,lambda:self.original.Popen(argv,**kwargs))

def cpu_command(root,checker,args):
 reqs,state=checker.context(root)
 record=checker.read(checker.safe(root,args.record));record['_recordPath']=args.record
 result=checker.validate_execution_precheck(root,record,reqs,state,args.candidate,'cpu',args.expect_selection)
 argv=result['nextRootAction']['argv']
 if (len(argv)!=7 or argv[:4]!=[sys.executable,'-B',str(root/'tools/qa_cpu.py'),'--review'] or
     argv[5]!='--sha256' or re.fullmatch('[0-9a-f]{64}',argv[6]) is None):
  raise ValueError('CPU delivery requires the unchanged reviewed qa_cpu packet invocation')
 packet=pathlib.Path(argv[4])
 if not packet.is_file() or packet.is_symlink() or hashlib.sha256(packet.read_bytes()).hexdigest()!=argv[6]:
  raise ValueError('CPU review packet differs')
 return argv

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--repo',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[3])
 p.add_argument('--record',default='.warlock-contributor/slice.json')
 sub=p.add_subparsers(dest='command',required=True)
 sub.add_parser('check')
 native=sub.add_parser('native');native.add_argument('--runner',required=True)
 native.add_argument('--candidate');native.add_argument('--expect-selection',type=int)
 native.add_argument('arguments',nargs=argparse.REMAINDER)
 cpu=sub.add_parser('cpu');cpu.add_argument('--candidate',required=True);cpu.add_argument('--expect-selection',required=True,type=int)
 args=p.parse_args(argv);root=args.repo.resolve()
 checker=root/'plugins/warlock-contributor/scripts/warlock.py'
 if not checker.is_file():print('Warlock contributor checker is missing.',file=sys.stderr);return 2
 command=[sys.executable,'-B',str(checker),'--repo',str(root),'--record',args.record,'--json','check','--require-record']
 before=subprocess.run(command,cwd=root)
 if before.returncode:return before.returncode
 if args.command=='check':return 0
 tail=(args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments) if args.command=='native' else []
 # Frozen main retains containment, lock, conflict probe, supervision and codes.
 try:
  coordinator=portable_coordinator(root)
  record_path=root/args.record
  record=json.loads(record_path.read_text()) if record_path.is_file() else {}
  if not record and (getattr(args,'candidate',None) or args.command=='cpu'):
   raise ValueError('Managed delivery participant is missing')
  managed=record.get('workflowPolicy')==2
  if args.command=='cpu':
   if not managed:raise ValueError('CPU delivery wrapper requires workflow-policy2')
   argv=cpu_command(root,contributor_module(root),args)
   coordinator.subprocess=DeliverySubprocess(subprocess,root,args,'cpu')
   with coordinator.native_lock(root):
    if coordinator.find_qa_conflicts():raise ValueError('Existing protected QA process')
    code=coordinator.supervise_native(argv,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),pass_fds=()).returncode
  elif managed:
   if not args.candidate or args.expect_selection is None:raise ValueError('Native delivery requires candidate and selection generation')
   coordinator.subprocess=DeliverySubprocess(subprocess,root,args,'native')
   code=coordinator.run_native(root,pathlib.Path(args.runner),tail)
  else:
   code=coordinator.main(['--repo',str(root),'native','--runner',args.runner,'--',*tail])
 except (OSError,ValueError,KeyError,TypeError) as error:
  print(str(error),file=sys.stderr);code=2
 if code<0:code=128-code
 after=subprocess.run(command,cwd=root)
 return code if code else after.returncode

if __name__=='__main__':raise SystemExit(main())
