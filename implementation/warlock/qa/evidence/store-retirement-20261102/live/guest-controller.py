#!/usr/bin/env python3
"""ROOT-EXECUTED guest QA support. No work on import; no input or screenshots.
run STAGE_JSON starts one original28s application-only trial; probe ROOT samples
fresh guards for the host checked-QMP adapter. Native/release acceptance false.
"""
import hashlib,json,math,os,re,signal,stat,subprocess,sys,time,uuid
from pathlib import Path

if sys.flags.optimize != 0: raise RuntimeError('Guard assertions require nonoptimized Python')

ENV=dict(os.environ,OMARCHY_PATH='/usr/share/omarchy',LANG='C.UTF-8',LC_ALL='C.UTF-8',GDK_BACKEND='wayland')
for _key in ('DISPLAY','XAUTHORITY'):ENV.pop(_key,None)
FOOT_PID,FOOT_BIRTH=2095,'6930'

def command(args,timeout=1.2,check=True):
 r=subprocess.run(args,env=ENV,capture_output=True,text=True,timeout=timeout)
 if check and r.returncode:raise RuntimeError('Command refused '+args[0]+': '+r.stderr[-300:])
 return r

def atomic(directory,name,value):
 temporary=directory/(name+'.tmp')
 fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as out:json.dump(value,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
 temporary.replace(directory/name)

def file_pin(path,expected=None):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 with os.fdopen(fd,'rb') as stream:
  before=os.fstat(stream.fileno());assert stat.S_ISREG(before.st_mode), 'file_pin-L29'
  h=hashlib.sha256()
  for block in iter(lambda:stream.read(65536),b''):h.update(block)
  after=os.fstat(stream.fileno())
  stamp=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  assert stamp(before)==stamp(after), 'file_pin-L34'
  value={'device':before.st_dev,'inode':before.st_ino,'size':before.st_size,'sha256':h.hexdigest()}
 if expected is not None:assert value['sha256']==expected, 'file_pin-L36'
 return value

def proc(pid):
 p=Path('/proc')/str(pid);raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split()
 status=(p/'status').read_text();image=(p/'exe').stat()
 limits=(p/'limits').read_text();core=next(line.split()[4:6] for line in limits.splitlines() if line.startswith('Max core file size'))
 return {'pid':pid,'birth':a[19],'ppid':int(a[1]),'pgid':int(a[2]),'uid':p.stat().st_uid,
  'device':image.st_dev,'inode':image.st_ino,'size':image.st_size,
  'namespacePids':[int(n) for line in status.splitlines() if line.startswith('NSpid:') for n in line.split()[1:]],
  'cgroup':(p/'cgroup').read_text().strip(),'core':core}

def parse_birth(raw,pid):
 prefix=str(pid)+' (';end=raw.rfind(') ')
 if not raw.startswith(prefix) or end<len(prefix):raise ValueError('bad stat header')
 fields=raw[end+2:].split()
 if len(fields)<20 or fields[0] not in ('R','S','D','Z','T','t','X','x','K','W','P','I','N'):
  raise ValueError('bad stat fields')
 birth=fields[19]
 if not birth.isascii() or not birth.isdecimal():raise ValueError('bad birth')
 return birth

def proc_context():
 procroot=Path('/proc').stat();cgroot=Path('/sys/fs/cgroup').stat()
 parse_birth(Path('/proc/self/stat').read_text(),os.getpid())
 candidates=[]
 for line in Path('/proc/self/mountinfo').read_text().splitlines():
  left,sep,right=line.partition(' - ');fields=left.split();tail=right.split()
  if sep and len(fields)>=6 and len(tail)>=3 and fields[4]=='/proc' and tail[0]=='proc':
   candidates.append((fields[0],fields[5],tail[2]))
 if len(candidates)!=1:raise ValueError('proc mount unknown')
 options=set((candidates[0][1]+','+candidates[0][2]).split(','))
 if any(opt.startswith('hidepid=') and opt not in ('hidepid=0','hidepid=off') for opt in options):
  raise ValueError('proc visibility restricted')
 ns=Path('/proc/self/ns/pid').stat()
 return {'proc':[procroot.st_dev,procroot.st_ino],'mount':list(candidates[0]),
         'pidNamespace':[ns.st_dev,ns.st_ino],'cgroupRoot':[cgroot.st_dev,cgroot.st_ino]}

def group_stamp(group):
 path=Path('/sys/fs/cgroup')/group.lstrip('/')
 metadata=path.lstat()
 if not stat.S_ISDIR(metadata.st_mode):raise ValueError('cgroup path not a directory')
 return [metadata.st_dev,metadata.st_ino]

def principal_observation(pid,birth,expected):
 try:
  if type(pid) is not int or pid<=0 or not isinstance(birth,str) or not birth.isascii() or not birth.isdecimal():
   raise ValueError('bad pinned identity')
  before=proc_context()
  if before!=expected:raise ValueError('proc context changed')
  try:raw=(Path('/proc')/str(pid)/'stat').read_text()
  except FileNotFoundError:
   if proc_context()!=before:raise ValueError('proc context changed')
   return ('absent',None)
  observed=parse_birth(raw,pid)
  if proc_context()!=before:raise ValueError('proc context changed')
  return ('present',{'pid':pid,'birth':observed}) if observed==birth else ('different-birth',None)
 except (OSError,ValueError,IndexError,StopIteration,KeyError,TypeError) as error:
  return ('unknown',type(error).__name__)

def foot():
 value=proc(FOOT_PID);assert value['birth']==FOOT_BIRTH and value['uid']==os.getuid(), 'foot-L49'
 assert Path(os.readlink(Path('/proc')/str(FOOT_PID)/'exe')).name=='foot', 'foot-L50'
 return value

def members(unit):
 assert re.fullmatch(r'warlock-live-usability-[a-f0-9]{16}\.scope',unit), 'members-L54'
 r=command(['systemctl','--user','show',unit,'--property=ControlGroup','--property=ActiveState','--property=MemoryMax','--property=LoadState'],check=False)
 props=dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
 if r.returncode or not props.get('ControlGroup'):return [],{'known':False,'exit':r.returncode,'properties':props}
 root=Path('/sys/fs/cgroup')/props['ControlGroup'].lstrip('/')
 if not root.is_dir():return [],{'known':False,'properties':props}
 found=set()
 def walk_error(error):raise error
 walked=False
 for path,_,files in os.walk(root,onerror=walk_error):
  walked=True
  if 'cgroup.procs' not in files:raise OSError('incomplete cgroup inventory')
  found.update(map(int,(Path(path)/'cgroup.procs').read_text().split()))
 if not walked:raise OSError('cgroup inventory unavailable')
 return sorted(found),{'known':True,'properties':props}

def sample(root,pinned=None):
 context=proc_context()
 run=root/'run-01';state=json.loads((run/'controller-state.json').read_text());config=json.loads((run/'backend.json').read_text())
 assert state['guestRoot']==str(root) and state['deadlineMonotonicNs']==config['deadlineMonotonicNs'], 'sample-L68'
 assert int(state['deadlineMonotonicNs'])-int(state['generatedMonotonicNs'])==28_000_000_000, 'sample-L69'
 assert command(['omarchy-shell','lock','isLocked']).stdout.strip()=='false', 'sample-L70'
 own,status=members(state['unit']);assert status['known'] and status['properties']['ActiveState']=='active', 'sample-L71'
 assert status['properties']['MemoryMax']=='2147483648', 'sample-L72'
 group=status['properties']['ControlGroup'];assert 'qa-harness.slice' in group, 'sample-L73'
 groupIdentity=group_stamp(group)
 images={name:file_pin(root/'assets'/name,state['images'][name]['sha256']) for name in ('warlock-ui-owner','warlock-ui-backend')}
 assert images==state['images'], 'sample-L75'
 clients=json.loads(command(['hyprctl','clients','-j']).stdout);candidates=[]
 for client in clients:
  if client.get('pid') not in own or not client.get('mapped') or client.get('hidden') or client.get('visible') is False:continue
  process=proc(client['pid'])
  if all(process[k]==images['warlock-ui-owner'][k] for k in ('device','inode','size')) and process['namespacePids'] and process['namespacePids'][-1]==1:candidates.append((client,process))
 assert len(candidates)==1, 'sample-L81'
 client,engine=candidates[0];broker=proc(engine['ppid']);backend=proc(broker['ppid'])
 assert backend['pid']==state['launcherPID'], 'sample-L83'
 for process,image in ((engine,images['warlock-ui-owner']),(broker,images['warlock-ui-owner']),(backend,images['warlock-ui-backend'])):
  assert process['pid'] in own and process['uid']==os.getuid() and process['core']==['1','1'], 'sample-L85'
  assert process['cgroup']=='0::'+group or process['cgroup'].startswith('0::'+group+'/'), 'sample-L86'
  assert all(process[k]==image[k] for k in ('device','inode','size')), 'sample-L87'
 assert engine['ppid']==broker['pid'] and broker['ppid']==backend['pid'], 'sample-L88'
 active=json.loads(command(['hyprctl','activewindow','-j']).stdout)
 assert active.get('pid')==engine['pid'] and active.get('address')==client['address'], 'sample-L90'
 monitors=json.loads(command(['hyprctl','monitors','-j']).stdout);assert len(monitors)==1, 'sample-L91'
 monitor=monitors[0];assert tuple(monitor[k] for k in ('width','height','scale','transform','x','y'))==(1280,800,1,0,0,0), 'sample-L92'
 assert monitor.get('dpmsStatus') is True, 'sample-L93'
 assert all(type(n) in (int,float) for n in client['at']+client['size']) and all(n>0 for n in client['size']), 'sample-L94'
 saved=foot();layers=json.loads(command(['hyprctl','layers','-j']).stdout)
 cursor=json.loads(command(['hyprctl','cursorpos','-j']).stdout)
 assert isinstance(cursor,dict) and set(cursor)=={'x','y'}, 'sample-L97'
 assert all(type(cursor[axis]) in (int,float) and math.isfinite(cursor[axis]) for axis in ('x','y')), 'sample-L98'
 assert 0<=cursor['x']<1280 and 0<=cursor['y']<800, 'sample-L99'
 if proc_context()!=context or group_stamp(group)!=groupIdentity:raise ValueError('observation context changed during sample')
 identity={'procContext':context,'groupIdentity':groupIdentity,'unit':state['unit'],'attempt':state['attempt'],'group':group,'deadline':state['deadlineMonotonicNs'],
  'engine':engine,'broker':broker,'backend':backend,'address':client['address'],'at':client['at'],'size':client['size'],'foot':saved}
 if pinned is not None:assert identity==pinned, 'sample-L102'
 return {'identity':identity,'remainingNs':int(state['deadlineMonotonicNs'])-time.monotonic_ns(),
  'client':client,'clients':clients,'monitor':monitor,'layers':layers,'cursor':cursor,'scopeState':status,'originalDurationSeconds':28}

def cleanup_passes(failure,cleanup):
 return failure is None and not cleanup.get('error') and cleanup.get('launcherReaped') is True and cleanup.get('scopeInventoryConfirmedEmpty') is True and cleanup.get('footPreserved') is True and cleanup.get('idleRestore',{}).get('exactEnabledRestored') is True and cleanup.get('originalOwnedBirthsRemain')==[] and cleanup.get('originalOwnedBirthsUnknown')==[]

def run(stage):
 os.umask(0o077);root=Path(stage['guestRoot']);assert root.is_absolute() and root.is_dir() and not root.is_symlink()
 run_dir=root/'run-01';run_dir.mkdir(mode=0o700)
 assert stage['originalTrialDurationSeconds']==28
 assets=root/'assets';helper=assets/'omarchy_ui_mvp.py';assert helper.is_file() and not helper.is_symlink()
 images={name:file_pin(assets/name,stage[key]) for name,key in (('warlock-ui-owner','guestOwnerSHA256'),('warlock-ui-backend','guestBackendSHA256'))}
 for role,name in (('controller','HttpMain'),('bar','HttpBar'),('popup','HttpPopup')):file_pin(assets/(name+'.html'),stage['html'][role]['sha256'])
 idle=json.loads(command(['omarchy-shell','idle','status']).stdout);assert type(idle.get('enabled')) is bool
 original_foot=foot();assert command(['omarchy-shell','lock','isLocked']).stdout.strip()=='false'
 atomic(run_dir,'preservation-before.json',{'idleOriginal':idle,'foot':original_foot,'clients':json.loads(command(['hyprctl','clients','-j']).stdout)})
 unit='warlock-live-usability-'+uuid.uuid4().hex[:16]+'.scope';p=None;deadline=None;failure=None;observations=[];known=None;forced=False;start=time.monotonic()
 def interrupted(number,_frame):raise InterruptedError('signal '+str(number))
 signal.signal(signal.SIGTERM,interrupted)
 try:
  command(['omarchy-shell','idle','disable'])
  args=['python3','-B',str(helper),'guest-config','--run-dir',str(run_dir),'--duration-seconds','28','--controller-html',str(assets/'HttpMain.html'),'--bar-html',str(assets/'HttpBar.html'),'--popup-html',str(assets/'HttpPopup.html'),'--ui-owner-bin',str(assets/'warlock-ui-owner'),'--ui-backend-bin',str(assets/'warlock-ui-backend'),'--catalog-root','/usr/share/applications']
  with (run_dir/'guest-config.stdout').open('x') as out,(run_dir/'guest-config.stderr').open('x') as err:subprocess.run(args,env=ENV,stdout=out,stderr=err,check=True,timeout=12)
  manifest=json.loads((run_dir/'mvp-guest-manifest.json').read_text());deadline=int(manifest['deadlineMonotonicNs'])/1e9
  assert int(manifest['deadlineMonotonicNs'])-int(manifest['generatedMonotonicNs'])==28_000_000_000
  with (run_dir/'backend.stdout').open('x') as out,(run_dir/'backend.stderr').open('x') as err:
   p=subprocess.Popen(['systemd-run','--user','--scope','--quiet','--slice=qa-harness.slice','--unit='+unit,'--property=MemoryMax=2G','--','prlimit','--core=1:1','--',str(assets/'warlock-ui-backend'),str(run_dir/'backend.json')],env=ENV,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
   atomic(run_dir,'controller-state.json',{'unit':unit,'attempt':unit.removesuffix('.scope'),'guestRoot':str(root),'launcherPID':p.pid,'images':images,'generatedMonotonicNs':manifest['generatedMonotonicNs'],'deadlineMonotonicNs':manifest['deadlineMonotonicNs'],'nativeOperations':[],'nativeAccepted':False})
   while p.poll() is None and time.monotonic()<deadline:
    try:
     row=sample(root,known);known=row['identity'];row['monotonic']=time.monotonic();observations.append(row)
     if len(observations)>160:raise RuntimeError('Observation bound')
     atomic(run_dir,'live-current.json',row)
    except (AssertionError,OSError,subprocess.SubprocessError,ValueError) as error:
     if known is not None:
      detail=str(error) if isinstance(error,AssertionError) and re.fullmatch(r'(?:sample|foot|file_pin|members)-L[0-9]+',str(error)) else 'observation-unknown'
      raise RuntimeError('Pinned live attempt guard failed: '+type(error).__name__+':'+detail) from error
    time.sleep(.15)
   if p.poll() is None:
    forced=True;command(['systemctl','--user','kill','--kill-whom=all','--signal=KILL',unit],check=False)
    p.wait(timeout=3)
 except BaseException as error:failure=type(error).__name__+': '+str(error)
 finally:
  cleanup={}
  try:
   own,status=members(unit);cleanup['before']=status
   if own or (p is not None and p.poll() is None):
    forced=True;cleanup['killExit']=command(['systemctl','--user','kill','--kill-whom=all','--signal=KILL',unit],check=False).returncode
   cleanup['stopExit']=command(['systemctl','--user','stop',unit],timeout=3,check=False).returncode
   if p is not None:
    try:p.wait(timeout=3);cleanup['launcherReaped']=True
    except subprocess.TimeoutExpired:cleanup['launcherReaped']=False
   groupBefore=group_stamp(known['group']) if known is not None else None
   own,status=members(unit);cleanup['remaining']=own;cleanup['after']=status
   cleanup['scopeInventoryConfirmedEmpty']=bool(known is not None and status.get('known') and own==[] and status.get('properties',{}).get('ControlGroup')==known['group'] and groupBefore==known['groupIdentity'] and group_stamp(known['group'])==groupBefore and proc_context()==known['procContext'])
   if not status.get('known'):
    cleanup['scopeInventoryUnknown']=True
  except BaseException as error:cleanup['error']=type(error).__name__
  cleanup['originalOwnedBirthsRemain']=[]
  cleanup['originalOwnedBirthsUnknown']=[]
  if known is None:
   cleanup['originalOwnedBirthsUnknown'].append({'role':'all','reason':'identity-not-pinned'})
  else:
   for role in ('engine','broker','backend'):
    state,value=principal_observation(known[role]['pid'],known[role]['birth'],known['procContext'])
    if state=='present':cleanup['originalOwnedBirthsRemain'].append({'role':role,'process':value})
    elif state=='unknown':cleanup['originalOwnedBirthsUnknown'].append({'role':role,'errorClass':value})
  try:
   restore=command(['omarchy-shell','idle','enable' if idle['enabled'] else 'disable'],check=False)
   after=json.loads(command(['omarchy-shell','idle','status']).stdout)
   cleanup['idleRestore']={'exit':restore.returncode,'original':idle,'after':after,'exactEnabledRestored':after.get('enabled')==idle['enabled']}
  except BaseException as error:cleanup['idleRestoreError']=type(error).__name__
  try:cleanup['footAfter']=foot();cleanup['footPreserved']=cleanup['footAfter']['birth']==original_foot['birth']
  except BaseException as error:cleanup['footPreserved']=False;cleanup['footError']=type(error).__name__
  atomic(run_dir,'observations.json',observations)
  atomic(run_dir,'trial-result.json',{'scope':'Actual current Elm/Haskell application-only VM usability trial; no native/release/AT/IME acceptance','originalDurationSeconds':28,'exit':p.returncode if p else None,'failure':failure,'forcedAtOriginalDeadlineOrRefusal':forced,'elapsed':time.monotonic()-start,'unit':unit,'pinnedIdentity':known,'cleanup':cleanup,'nativeOperations':[],'providerCleanupQualified':False,'nativeAccepted':False,'releaseAccepted':False})
 return 0 if p is not None and p.returncode==0 and not forced and cleanup_passes(failure,cleanup) else 1

if __name__=='__main__':
 if sys.argv[1]=='run':raise SystemExit(run(json.loads(sys.argv[2])))
 if sys.argv[1]=='probe':print(json.dumps(sample(Path(sys.argv[2]))));raise SystemExit(0)
 raise SystemExit('Expected run STAGE_JSON | probe GUEST_ROOT')
