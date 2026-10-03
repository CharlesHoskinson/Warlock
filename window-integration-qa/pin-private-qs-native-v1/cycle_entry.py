"""Exact private keyboard binding relay to unchanged real taskbar cycle(1).

This is a setup IPC stimulus, not a Pin helper or a selection override. It
publishes its actual child normal terminal separately; input/selection/menu
delivery remains required from the native probes and genuine QML callback.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,subprocess,sys,time
# -I -S keeps the import path explicit and frozen; no HOME or cwd fallback.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from io_guard import directory,publish_json,sha,strict,exact
from materialize import identity,exact_exec,peer_socket,pin_config
from selection import QS,QS_SHA,CORE,CORE_SHA,QA
def main():
 evidence={'schema':'pin-private-taskbar-cycle-v1','result':'fail','setupOnly':True,'actualInputAcceptance':False,'ordinaryPinHelper':False};destination=None
 try:
  sys.path.insert(0,str(QA))
  from qa_launch import require_qa_scope
  require_qa_scope()
  if len(sys.argv)!=3:raise ValueError('Exact private cycle configuration/hash required')
  path=Path(sys.argv[1]);s=path.lstat()
  if path.resolve()!=path or not stat.S_ISREG(s.st_mode)or stat.S_IMODE(s.st_mode)!=0o600 or s.st_uid!=os.getuid()or s.st_nlink!=1 or s.st_size>1048576 or sha(path)!=sys.argv[2]:raise ValueError('Exact immutable cycle configuration required')
  config=strict(path.read_bytes());directory(config['runtime']);directory(config['home']);directory(config['evidence'])
  if not path.is_relative_to(Path(config['home']))or not Path(config['home']).is_relative_to(config['runtime']):raise ValueError('Exact private cycle config placement required')
  own=identity(os.getpid());destination=Path(config['evidence'])/(str(own['pid'])+'-'+own['start']+'.json');evidence['own']=own
  if sha(__file__)!=config['entrySHA256']or str(Path('/proc/self/exe').resolve())!=config['interpreter']['path']or sha('/proc/self/exe')!=config['interpreter']['sha256']or Path('/proc/self/cmdline').read_bytes()!=b'\0'.join(v.encode()for v in ['/usr/bin/python3','-I','-S',str(Path(__file__).resolve()),str(path),sys.argv[2]])+b'\0':raise ValueError('Exact direct cycle source/interpreter/argv required')
  compositor=config['compositor'];actual=pin_config.source_process(compositor['identity']['pid'],compositor['environment'])
  if actual!=compositor or actual['executable']!=str(CORE)or actual['executableSHA256']!=CORE_SHA:raise ValueError('Exact current selected compositor required')
  ancestors=[];parent=identity(own['parent'])
  if parent['pid']!=compositor['identity']['pid']:
   p=Path('/proc')/str(parent['pid']);argv=[x.decode()for x in(p/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
   expected_command=config['dispatchCommand'].replace('CONFIG_HASH',sys.argv[2])
   if parent['parent']!=compositor['identity']['pid']or str((p/'exe').resolve())!=str(Path('/bin/sh').resolve())or argv!=['/bin/sh','-c',expected_command]:raise ValueError('Exact private compositor dispatcher ancestry required')
   ancestors.append(parent)
  ancestors.append(compositor['identity']);evidence['ancestors']=ancestors
  target=config['requester'];before=exact_exec(target['identity']['pid'],target['identity']['start'],config['environment'],config['command']);evidence['targetBefore']=before
  if pin_config.source_process(target['identity']['pid'],target['environment'],'shell')!=target or Path('/proc/self/cgroup').read_text()!=target['cgroup']:raise ValueError('Exact actual cycle requester/scope required')
  command=[str(QS),'ipc','--pid',str(target['identity']['pid']),'call','--','hoskinson.windows','cycle','1'];deadline=time.monotonic()+2;evidence['command']=command
  child=subprocess.Popen(command,env=config['environment'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);life=identity(child.pid);evidence['child']=life
  proc=Path('/proc')/str(child.pid);observed_argv=[p.decode()for p in(proc/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
  evidence['childSource']=dict(executable=str((proc/'exe').resolve()),sha256=sha(proc/'exe'),argv=observed_argv)
  if evidence['childSource']!=dict(executable=str(QS),sha256=QS_SHA,argv=command)or identity(child.pid)!=life:raise ValueError('Actual private cycle CLI exec/source changed')
  try:out,err=child.communicate(timeout=max(.001,deadline-time.monotonic()))
  except BaseException as e:evidence['childError']=repr(e);raise
  evidence.update(exitCode=child.returncode,gone=not Path('/proc/'+str(child.pid)).exists(),stdout=out.decode(),stderr=err.decode(),targetAfter=exact_exec(target['identity']['pid'],target['identity']['start'],config['environment'],config['command']))
  if child.returncode!=0 or not evidence['gone']or len(out)+len(err)>65536 or err or out.strip()not in(b'',b'true')or evidence['targetAfter']!=before or sha(path)!=sys.argv[2]:raise ValueError('Actual original2s private cycle IPC normal terminal required')
  evidence['result']='pass';return 0
 except BaseException as e:evidence['error']=repr(e);return 1
 finally:
  if destination is not None:publish_json(destination,evidence)
if __name__=='__main__':raise SystemExit(main())
