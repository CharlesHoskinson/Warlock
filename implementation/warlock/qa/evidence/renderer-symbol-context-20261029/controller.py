"""Fixed-purpose GDB Python controller. Run only in the reviewed protected QA scope."""
import gdb,hashlib,json,os,pathlib,re,resource,select,signal,stat,struct,subprocess,sys,threading,time
D=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-symbols-v1')
RUNNER=D/'diagnostic-runner.py';BASE=D.parent.parent/'native-new-instance.py';HOST=D.parent.parent.parent/'host/elm-host';RENDERER=pathlib.Path('/usr/lib/webkit2gtk-4.1/WebKitWebProcess');GDB=pathlib.Path('/usr/bin/gdb');PYTHON=pathlib.Path('/usr/bin/python3.14')
EXPECTED={RUNNER:'7bb724351897d2ce3726c8725f018c4d44f2bbf657de92dc20f417f0bf53f1b9',BASE:'9fce62de80ea0f2b57169d79f9806aa1be895fc62dc885b6999ed4e013fafbc1',HOST:'4377b11ce0afe9e1072210666aa872118b032995275a20657058771e5e6c8347',RENDERER:'afe6c0f50e08a762747c65e4b7fc04551960338af72c67649f287b3c4808f2e5',GDB:'e95c07efc239f1cc02ef8b85b0ec2e95ee7e5f43a77a2f92a202a5e3e5ffcadf',PYTHON:'375532f83be620283ab780c14ca6bcc5907dc379d2b621de0c5d0a112cf5458b'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checked_files():
 st=D.lstat();assert stat.S_ISDIR(st.st_mode) and st.st_uid==1000 and stat.S_IMODE(st.st_mode)==0o700 and D.resolve()==D
 for p,h in EXPECTED.items():
  st=p.lstat();assert stat.S_ISREG(st.st_mode) and not st.st_mode&0o022 and sha(p)==h
  assert st.st_uid==(0 if p in (RENDERER,GDB,PYTHON) else 1000)
def mark(name):
 fd=os.open(D/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
def marker(name):
 try:st=(D/name).lstat()
 except FileNotFoundError:return False
 assert stat.S_ISREG(st.st_mode) and st.st_uid==1000 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1
 return True
def info(pid):
 p=pathlib.Path('/proc')/str(pid);raw=(p/'stat').read_text();f=raw[raw.rfind(')')+2:].split();return int(f[1]),f[19]
def procvalid(pid,start,cg,exe):
 p=pathlib.Path('/proc')/str(pid);return p.stat().st_uid==1000 and info(pid)[1]==str(start) and (p/'cgroup').read_text().strip()==cg and (p/'exe').resolve(strict=True)==exe.resolve(strict=True)
def descendant(pid,ancestor):
 parent=info(pid)[0];seen={pid}
 while parent!=ancestor and parent>1 and parent not in seen:seen.add(parent);parent=info(parent)[0]
 return parent==ancestor
def children(pid):
 # Traverse only the owned host subtree; never scan unrelated processes.
 found=[];seen={pid};todo=[pid]
 while todo:
  parent=todo.pop();tasks=pathlib.Path('/proc')/str(parent)/'task'
  try:tids=list(tasks.iterdir())
  except FileNotFoundError:continue
  if len(tids)>1024:raise RuntimeError('owned task bound exceeded')
  for task in tids:
   if not task.name.isdigit():continue
   try:ids=[int(x) for x in (task/'children').read_text().split()]
   except FileNotFoundError:continue
   for child in ids:
    if child in seen:continue
    seen.add(child);found.append(child);todo.append(child)
    if len(found)>256:raise RuntimeError('owned descendant bound exceeded')
 return found
def state(pid):
 for line in (pathlib.Path('/proc')/str(pid)/'status').read_text().splitlines():
  if line.startswith('State:'):return line.split(':',1)[1].strip()[0]
 raise RuntimeError('missing process state')
def build_id(fd):
 # Read bounded ELF64 little-endian PT_NOTE records only; never execute mapped files.
 header=os.pread(fd,64,0)
 if len(header)<64 or header[:6]!=b'\x7fELF\x02\x01':return None
 phoff=struct.unpack_from('<Q',header,32)[0]; entsize,count=struct.unpack_from('<HH',header,54)
 size=os.fstat(fd).st_size
 if entsize<56 or entsize>4096 or count>256 or phoff>size or entsize*count>size-phoff:return None
 headers=os.pread(fd,entsize*count,phoff)
 for index in range(count):
  pos=index*entsize
  if pos+56>len(headers):return None
  typ,_,offset,_,_,length,_,_=struct.unpack_from('<IIQQQQQQ',headers,pos)
  if typ!=4 or length>1048576 or offset>size or length>size-offset:continue
  notes=os.pread(fd,length,offset); n=0
  while n+12<=len(notes):
   namesz,descsz,kind=struct.unpack_from('<III',notes,n);n+=12
   if namesz>len(notes)-n:break
   name=notes[n:n+namesz];n+=(namesz+3)&~3
   if descsz>len(notes)-n:break
   desc=notes[n:n+descsz];n+=(descsz+3)&~3
   if kind==3 and name.rstrip(b'\0')==b'GNU':return desc.hex()
 return None

def mapping_evidence(pid,index):
 # Only the verified owned inferior; preserve map text plus identity-checked mapped ELF build IDs.
 proc=pathlib.Path('/proc')/str(pid); raw=(proc/'maps').read_text()
 if len(raw.encode())>2*1024*1024:raise RuntimeError('mapping evidence bound')
 fd=os.open(D/('diagnostic-maps-'+str(index)+'.txt'),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as f:f.write(raw)
 objects={}
 for line in raw.splitlines():
  parts=line.split(None,5)
  if len(parts)<6:continue
  _,_,_,device,inode,path=parts
  if not path.startswith('/') or inode=='0':continue
  key=(device,inode,path)
  if key in objects:continue
  if len(objects)>=512:raise RuntimeError('mapped object bound')
  item={'device':device,'inode':inode,'path':path,'buildId':None}
  objects[key]=item
  if path.endswith(' (deleted)') or '..' in pathlib.PurePosixPath(path).parts:
   item['unavailable']='deleted or noncanonical path';continue
  try:
   target=str(proc/'root')+path
   fd=os.open(target,os.O_RDONLY|os.O_CLOEXEC)
   try:
    st=os.fstat(fd);major,minor=(int(v,16) for v in device.split(':'))
    if st.st_ino!=int(inode) or os.major(st.st_dev)!=major or os.minor(st.st_dev)!=minor:
     item['unavailable']='mapped file identity mismatch'
    else:
     item['buildId']=build_id(fd)
     if item['buildId'] is None:item['unavailable']='no readable ELF64 GNU build ID'
   finally:os.close(fd)
  except (OSError,ValueError,struct.error) as error:item['unavailable']=type(error).__name__
 out=D/('diagnostic-modules-'+str(index)+'.json')
 fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as f:json.dump(list(objects.values()),f,indent=2)
 return {'maps':str(D/('diagnostic-maps-'+str(index)+'.txt')),'modules':str(out),'objects':len(objects),'buildIds':sum(1 for item in objects.values() if item['buildId'])}

assert os.getuid()==1000 and os.geteuid()==1000 and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1' and resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
checked_files();assert pathlib.Path('/proc/self/exe').resolve()==GDB.resolve();assert sha(pathlib.Path('/proc/self/exe'))==EXPECTED[GDB]
cg=pathlib.Path('/proc/self/cgroup').read_text().strip();assert re.fullmatch(r'0::/user\.slice/user-1000\.slice/user@1000\.service/qa\.slice/qa-harness\.slice/qa-harness-[a-zA-Z0-9-]+\.scope',cg)
for name in ['supervisor-ready','diagnostic-ready.json','release','abort','diagnostic-stack-1.log','diagnostic-stack-2.log','diagnostic-stack-3.log','diagnostic-result.json','session-result.json']:assert not (D/name).exists() and not (D/name).is_symlink()
child=None;pidfd=None;attached=False;observed=[];exits=[];cancel=threading.Event();watchdog=None;target=None;failure=None;child_exit=None
try:
 mark('supervisor-ready')
 child=subprocess.Popen(['/usr/bin/python3.14','-B',str(RUNNER),'--at-actions'],stdin=subprocess.DEVNULL)
 deadline=time.monotonic()+120
 while not marker('diagnostic-ready.json'):
  if child.poll() is not None or time.monotonic()>=deadline:raise RuntimeError('owned diagnostic child exited or readiness timed out')
  time.sleep(.025)
 fd=os.open(D/'diagnostic-ready.json',os.O_RDONLY|os.O_NOFOLLOW);st=os.fstat(fd);assert stat.S_ISREG(st.st_mode) and st.st_uid==1000 and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1
 with os.fdopen(fd) as f:packet=json.load(f)
 assert set(packet)=={'hostPid','hostStart','cgroup','hostSHA256','sourceRunnerSHA256','instrumented','acceptance'} and packet['instrumented'] is True and packet['acceptance'] is False
 assert packet['hostSHA256']==EXPECTED[HOST] and packet['sourceRunnerSHA256']==EXPECTED[BASE] and packet['cgroup']==cg
 host=int(packet['hostPid']);hoststart=str(packet['hostStart']);assert procvalid(host,hoststart,cg,HOST) and descendant(host,child.pid) and descendant(host,os.getpid())
 matches=[]
 for pid in children(host):
  try:
   _,start=info(pid)
   if procvalid(pid,start,cg,RENDERER) and descendant(pid,host) and descendant(pid,os.getpid()):matches.append((pid,start))
  except (FileNotFoundError,ProcessLookupError,PermissionError):continue
 assert len(matches)==1,('Expected exactly one owned renderer',matches);pid,start=matches[0];target=pid;pidfd=os.pidfd_open(pid)
 assert not select.select([pidfd],[],[],0)[0] and procvalid(pid,start,cg,RENDERER) and procvalid(host,hoststart,cg,HOST) and descendant(pid,host) and descendant(pid,os.getpid())
 signal.pidfd_send_signal(pidfd,signal.SIGSTOP);deadline=time.monotonic()+5
 while state(pid) not in ('T','t'):
  if time.monotonic()>=deadline:raise TimeoutError('owned renderer stop deadline')
  time.sleep(.025)
 checked_files();assert not select.select([pidfd],[],[],0)[0] and procvalid(pid,start,cg,RENDERER) and procvalid(host,hoststart,cg,HOST) and descendant(pid,host) and descendant(pid,os.getpid())
 # Bind the exact verified owned image and namespace before attaching; no fallback to host-root paths.
 exe=pathlib.Path('/proc')/str(pid)/'exe'; root=pathlib.Path('/proc')/str(pid)/'root'
 assert sha(exe)==EXPECTED[RENDERER] and os.path.samefile(exe,RENDERER)
 assert root.is_dir() and os.access(root,os.R_OK|os.X_OK)
 gdb.execute('set sysroot '+str(root),to_string=True)
 gdb.execute('set solib-search-path '+str(root)+'/usr/lib:'+str(root)+'/lib',to_string=True)
 gdb.execute('file '+str(exe),to_string=True)
 gdb.execute('attach '+str(pid),to_string=True);attached=True
 assert not select.select([pidfd],[],[],0)[0] and gdb.selected_inferior().pid==pid and procvalid(pid,start,cg,RENDERER) and procvalid(host,hoststart,cg,HOST) and descendant(pid,host) and descendant(pid,os.getpid())
 # Ask GDB to resolve the inferior libraries under its verified root before release.
 solib_status=gdb.execute('sharedlibrary',to_string=True)
 pre_maps=mapping_evidence(pid,0)
 assert not select.select([pidfd],[],[],0)[0] and procvalid(pid,start,cg,RENDERER) and procvalid(host,hoststart,cg,HOST) and descendant(pid,host) and descendant(pid,os.getpid())
 signal.pidfd_send_signal(pidfd,signal.SIGCONT);mark('release')
 tracked=gdb.selected_inferior();snapshots=[]
 def stop_event(event):
  if not isinstance(event,gdb.SignalEvent):return
  event_thread=getattr(event,'inferior_thread',None)
  if gdb.selected_inferior()!=tracked or (event_thread is not None and event_thread.inferior!=tracked):raise RuntimeError('foreign inferior stop')
  observed.append(event.stop_signal)
 def exit_event(event):
  if getattr(event,'inferior',None)!=tracked:raise RuntimeError('foreign inferior exit')
  try:exit_signal=str(gdb.parse_and_eval('$_exitsignal'))
  except gdb.error:exit_signal=None
  exits.append({'exitCode':getattr(event,'exit_code',None),'exitSignal':exit_signal})
 gdb.events.stop.connect(stop_event);gdb.events.exited.connect(exit_event)
 def interrupt_after_deadline():
  if not cancel.wait(120):os.kill(os.getpid(),signal.SIGINT)
 watchdog=threading.Thread(target=interrupt_after_deadline,daemon=True);watchdog.start()
 resume='continue'
 while True:
  previous=len(observed)
  try:gdb.execute(resume,to_string=True)
  except gdb.error as error:print('Diagnostic resume ended:',str(error));break
  if len(observed)==previous:break
  fatal=observed[-1]
  if fatal not in ('SIGSEGV','SIGABRT','SIGBUS','SIGILL','SIGFPE','SIGTRAP'):break
  assert gdb.selected_inferior()==tracked and tracked.pid==pid and procvalid(pid,start,cg,RENDERER) and descendant(pid,host) and descendant(pid,os.getpid())
  assert len(tracked.threads())<=128
  index=len(snapshots)+1
  try: mapped=mapping_evidence(pid,index)
  except (OSError,RuntimeError,ValueError,struct.error) as error: mapped={'error':type(error).__name__+': '+str(error)}
  def optional_info(command):
   try:return gdb.execute(command,to_string=True)
   except gdb.error as error:return command+' unavailable: '+str(error)
  output='candidate='+fatal+'\n'+gdb.execute('thread apply all bt 12',to_string=True)+'\n'+optional_info('info sharedlibrary')+'\n'+optional_info('info proc mappings')+'\n'+optional_info('info files')
  assert len(output.encode())<=2*1024*1024
  index=len(snapshots)+1;fd=os.open(D/('diagnostic-stack-'+str(index)+'.log'),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:f.write(output)
  snapshots.append({'candidate':fatal,'index':index,'mappingEvidence':mapped})
  # Forward every actual candidate. After the third capture, pass any later
  # candidate without stopping, so the original signal cannot be swallowed.
  if index==3:
   for name in ('SIGSEGV','SIGABRT','SIGBUS','SIGILL','SIGFPE','SIGTRAP'):gdb.execute('handle '+name+' nostop noprint pass',to_string=True)
  resume='signal '+fatal
 cancel.set()
 if attached:
  try:gdb.execute('detach',to_string=True)
  except gdb.error:pass
  attached=False
 dead=bool(select.select([pidfd],[],[],0)[0]);result={'candidateSignals':[row['candidate'] for row in snapshots],'observedStops':observed,'snapshots':snapshots,'preReleaseMappings':pre_maps,'solibStatus':solib_status,'gdbExitEvents':exits,'rendererProcessDeathObserved':dead,'source':'ancestor diagnostic','diagnosticOnly':True,'acceptance':False}
 fd=os.open(D/'diagnostic-result.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2)
except BaseException as error:
 try:
  if not marker('abort'):mark('abort')
 except BaseException:pass
 failure=type(error).__name__+': '+str(error);print('Ancestor diagnostic stopped:',failure)
finally:
 cancel.set()
 if attached:
  try:gdb.execute('detach',to_string=True)
  except gdb.error:pass
 if pidfd is not None:
  try:signal.pidfd_send_signal(pidfd,signal.SIGCONT)
  except ProcessLookupError:pass
  os.close(pidfd)
 if child is not None:
  try:child_exit=child.wait(timeout=120)
  except subprocess.TimeoutExpired:failure='Owned child did not exit; root must use existing native-loop cleanup';print(failure)
 result={'diagnosticOnly':True,'acceptance':False,'childExitCode':child_exit,'failure':failure,'target':target}
 try:
  fd=os.open(D/'session-result.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2)
 except BaseException as error:failure='Cannot write session result: '+repr(error)
if failure:raise RuntimeError(failure)
