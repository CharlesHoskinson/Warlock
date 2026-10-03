"""Bounded metadata-only attribution of copied Files read-only unlinked tmpfs data."""
from pathlib import Path
import base64,hashlib,os,re,stat

MAX_MAP_BYTES=4*1024*1024
MAX_FDS=4096
MAX_DATA=1024*1024
NAME=re.compile(r'/dev/shm/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} \(deleted\)')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def bounded(path,limit=MAX_MAP_BYTES):
 with Path(path).open('rb') as stream:raw=stream.read(limit+1)
 if len(raw)>limit:raise RuntimeError('Owned metadata exceeds bound:'+str(path))
 return raw
def maps(raw):
 rows=[]
 for line in raw.decode().splitlines():
  p=line.split(maxsplit=5)
  if len(p)!=6:continue
  start,end=[int(x,16) for x in p[0].split('-')];major,minor=[int(x,16) for x in p[3].split(':')]
  rows.append({'line':line,'begin':start,'end':end,'offset':int(p[2],16),'permissions':p[1],'device':os.makedev(major,minor),'inode':int(p[4]),'path':p[5]})
 return rows
def identity(expected,frozen):
 pid=expected['pid'];p=Path('/proc')/str(pid);start=bounded(p/'stat',16384).decode().rsplit(')',1)[1].split()[19]
 if start!=expected['start']:raise RuntimeError('Owned shared-data PID lifetime changed')
 status=bounded(p/'status',65536).decode();uids=[int(x) for x in next(x for x in status.splitlines() if x.startswith('Uid:')).split()[1:]]
 cgroup=bounded(p/'cgroup',65536).decode();own=bounded('/proc/self/cgroup',65536).decode()
 if uids!=[os.getuid()]*4 or cgroup!=own or 'qa-harness-' not in cgroup:raise RuntimeError('Owned shared-data UID/scope differs')
 exe=str((p/'exe').resolve());row=frozen.get(exe)
 if not row:raise RuntimeError('Owned shared-data executable not frozen')
 st=Path(exe).stat();sha=digest(Path(exe).read_bytes())
 if sha!=row['sha256'] or stat.S_IMODE(st.st_mode)!=row['mode']:raise RuntimeError('Owned shared-data executable changed')
 mountns=os.readlink(p/'ns/mnt')
 if mountns!=os.readlink('/proc/self/ns/mnt'):raise RuntimeError('Shared-data mount namespace ambiguity')
 return {'pid':pid,'start':start,'uids':uids,'cgroup':cgroup,'exe':exe,'exeSHA256':sha,'mountNamespace':mountns}
def mount(pid):
 raw=bounded(Path('/proc')/str(pid)/'mountinfo',1024*1024);found=[]
 for line in raw.decode().splitlines():
  if not line.strip():continue
  if ' - ' not in line:raise RuntimeError('Malformed shared-data mount metadata')
  before,after=line.split(' - ',1);fields=before.split();tail=after.split()
  if len(fields)<6 or len(tail)<3:raise RuntimeError('Incomplete shared-data mount metadata')
  if fields[4]=='/dev/shm':
   major,minor=map(int,fields[2].split(':'))
   found.append({'id':int(fields[0]),'device':os.makedev(major,minor),'root':fields[3],'path':fields[4],'type':tail[0],'source':tail[1],'line':line})
 if len(found)!=1 or found[0]['type']!='tmpfs' or found[0]['root']!='/' or found[0]['device']!=Path('/dev/shm').stat().st_dev:raise RuntimeError('Shared-data /dev/shm mount/device ambiguous')
 return found[0]
def fdinfo(raw):
 fields={}
 for line in raw.decode().splitlines():
  if ':' in line:
   k,v=line.split(':',1)
   if k in fields:raise RuntimeError('Duplicate producer fdinfo field')
   fields[k]=v.strip()
 value={k:int(fields[k],8 if k=='flags' else 10) for k in ('flags','mnt_id','ino')}
 if value['flags']&os.O_ACCMODE!=os.O_RDONLY or value['flags']&os.O_PATH:raise RuntimeError('Producer FD is not read-only data')
 return value
def metadata(pid,number,mapping,mount_row,evidence=None):
 # The caller attaches this dict before calling; failure cannot discard metadata.
 evidence={} if evidence is None else evidence
 evidence.update(pid=pid,fd=number,expectedMapping=mapping,selectedMount=mount_row,accepted=False,errors={})
 path=Path('/proc')/str(pid)/'fd'/str(number);st=None;target=None;raw=None;info=None
 def error(key,exc):evidence['errors'][key]={'type':type(exc).__name__,'errno':getattr(exc,'errno',None),'error':str(exc)}
 try:
  st=path.stat()
  evidence['stat']={k:getattr(st,k) for k in ('st_mode','st_ino','st_dev','st_nlink','st_uid','st_gid','st_size','st_atime_ns','st_mtime_ns','st_ctime_ns','st_blocks','st_blksize','st_rdev')}
  evidence['stat'].update(fileType=stat.S_IFMT(st.st_mode),fullMode=stat.S_IMODE(st.st_mode),deviceMajor=os.major(st.st_dev),deviceMinor=os.minor(st.st_dev))
 except Exception as exc:error('stat',exc)
 try:target=os.readlink(path);evidence['target']=target
 except Exception as exc:error('target',exc)
 try:
  raw=bounded(Path('/proc')/str(pid)/'fdinfo'/str(number),16384)
  evidence['rawFdinfo']={'base64':base64.b64encode(raw).decode(),'bytes':len(raw),'sha256':digest(raw)}
 except Exception as exc:error('fdinfoRead',exc)
 try:
  mount_raw=bounded(Path('/proc')/str(pid)/'mountinfo',1024*1024)
  evidence['rawMountinfo']={'base64':base64.b64encode(mount_raw).decode(),'bytes':len(mount_raw),'sha256':digest(mount_raw)}
 except Exception as exc:error('mountinfoRead',exc)
 if raw is not None:
  try:info=fdinfo(raw);evidence['fdinfo']=info
  except Exception as exc:error('fdinfoParse',exc)
 if st is not None:
  evidence['conjuncts']={'targetMatches':target==mapping['path'],'mappingDeviceInodeMatches':(st.st_dev,st.st_ino)==(mapping['device'],mapping['inode']),'regular':stat.S_ISREG(st.st_mode),'fullMode600':stat.S_IMODE(st.st_mode)==0o600,'uidMatches':st.st_uid==os.getuid(),'unlinked':st.st_nlink==0,'sizeBounded':0<st.st_size<=MAX_DATA,'mountDeviceMatches':st.st_dev==mount_row['device']}
 if evidence['errors']:
  raise RuntimeError('Producer FD diagnostic metadata unavailable:'+','.join(evidence['errors']))
 if target!=mapping['path'] or (st.st_dev,st.st_ino)!=(mapping['device'],mapping['inode']):raise RuntimeError('Producer FD target/device/inode changed')
 if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode)!=0o600 or st.st_uid!=os.getuid() or st.st_nlink!=0 or not 0<st.st_size<=MAX_DATA or st.st_dev!=mount_row['device']:raise RuntimeError('Producer FD regular/UID/full mode/unlink/size/device differs')
 if info['ino']!=st.st_ino or info['mnt_id']!=mount_row['id']:raise RuntimeError('Producer fdinfo inode/mount differs')
 page=os.sysconf('SC_PAGE_SIZE');length=mapping['end']-mapping['begin'];offset=mapping['offset']
 if mapping['permissions']!='r--p' or mapping['begin']%page or length<=0 or length%page or offset%page or offset>=st.st_size or length>MAX_DATA or length>((st.st_size-offset+page-1)//page)*page:raise RuntimeError('Read-only VMA offset/range exceeds producer data size')
 evidence['accepted']=True
 return {'fd':number,'target':target,'device':st.st_dev,'inode':st.st_ino,'uid':st.st_uid,'mode':stat.S_IMODE(st.st_mode),'nlink':st.st_nlink,'size':st.st_size,'mtimeNs':st.st_mtime_ns,'ctimeNs':st.st_ctime_ns,'fdinfo':info}

def no_exec(mapping,raws):
 for raw in raws:
  for alias in maps(raw):
   if (alias['device'],alias['inode'])==(mapping['device'],mapping['inode']) and 'x' in alias['permissions']:raise RuntimeError('Executable alias of proposed shared data in observed owned maps')
def observe(proof,batch,consumer,producer,frozen,guard,peer,read_maps=None):
 """Mutate caller-owned evidence; caller persists it in finally before accepting."""
 proof.update(accepted=False,mappings={},scope='Captured owned batch plus before/after copied Files and private compositor maps; not global or continuous inspection')
 read_maps=read_maps or (lambda pid:bounded(Path('/proc')/str(pid)/'maps'))
 guard();before_peer=peer();before_consumer=identity(consumer,frozen);before_producer=identity(producer,frozen)
 if before_peer['pid']!=producer['pid'] or before_peer['uid']!=os.getuid():raise RuntimeError('Owned private compositor kernel peer differs')
 if consumer['pid']==producer['pid']:raise RuntimeError('Shared-data roles must be distinct owned processes')
 proof.update(consumerBefore=before_consumer,producerBefore=before_producer,privatePeerBefore=before_peer)
 exact=[r for r in batch['processes'] if r['identity']['pid']==consumer['pid'] and r['identity']['start']==consumer['start']]
 if len(exact)!=1:raise RuntimeError('One exact copied Files raw batch required')
 initial=exact[0]['maps'].encode();candidates=[r for r in maps(initial) if NAME.fullmatch(r['path'])]
 proof['consumerRawMapsSHA256']=digest(initial)
 if not candidates:
  proof.update(accepted=False,noCandidate=True);return proof
 c_before=read_maps(consumer['pid']);p_before=read_maps(producer['pid']);cm=mount(consumer['pid']);pm=mount(producer['pid'])
 if cm!=pm:raise RuntimeError('Consumer/producer tmpfs mount differs')
 proof.update(consumerMapsBeforeSHA256=digest(c_before),producerMapsBeforeSHA256=digest(p_before),mountBefore=cm,observations=[])
 inventory=sorted(int(p.name) for p in (Path('/proc')/str(producer['pid'])/'fd').iterdir())
 if len(inventory)>MAX_FDS:raise RuntimeError('Producer FD inventory exceeds bound')
 for candidate in candidates:
  observation={'mapping':candidate,'accepted':False};proof['observations'].append(observation)
  if candidate not in maps(c_before):raise RuntimeError('Consumer VMA changed before producer observation')
  no_exec(candidate,[r['maps'].encode() for r in batch['processes']]+[c_before,p_before]);matches=[]
  for number in inventory:
   st=(Path('/proc')/str(producer['pid'])/'fd'/str(number)).stat()
   if (st.st_dev,st.st_ino)==(candidate['device'],candidate['inode']):matches.append(number)
  observation['matchingProducerFDs']=matches
  if len(matches)!=1:raise RuntimeError('Exactly one owned compositor producer FD required')
  observation['producerFDDiagnosticBefore']={}
  observation['producerFDBefore']=metadata(producer['pid'],matches[0],candidate,pm,observation['producerFDDiagnosticBefore'])
 guard();after_peer=peer();c_after=read_maps(consumer['pid']);p_after=read_maps(producer['pid'])
 after_consumer=identity(consumer,frozen);after_producer=identity(producer,frozen);cm_after=mount(consumer['pid']);pm_after=mount(producer['pid'])
 proof.update(consumerAfter=after_consumer,producerAfter=after_producer,privatePeerAfter=after_peer,consumerMapsAfterSHA256=digest(c_after),producerMapsAfterSHA256=digest(p_after),mountAfter=cm_after)
 if before_peer!=after_peer or before_consumer!=after_consumer or before_producer!=after_producer or cm!=cm_after or pm!=pm_after:raise RuntimeError('Shared-data consumer/producer lifetime/peer/mount changed')
 for observation in proof['observations']:
  candidate=observation['mapping'];number=observation['matchingProducerFDs'][0]
  if candidate not in maps(c_after):raise RuntimeError('Consumer VMA changed after producer observation')
  no_exec(candidate,[c_after,p_after]);observation['producerFDDiagnosticAfter']={}
  observation['producerFDAfter']=metadata(producer['pid'],number,candidate,pm_after,observation['producerFDDiagnosticAfter'])
  after_inventory=list((Path('/proc')/str(producer['pid'])/'fd').iterdir())
  if len(after_inventory)>MAX_FDS:raise RuntimeError('Producer FD inventory exceeds bound after observation')
  after_matches=[]
  for path in after_inventory:
   st=path.stat()
   if (st.st_dev,st.st_ino)==(candidate['device'],candidate['inode']):after_matches.append(int(path.name))
  observation['matchingProducerFDsAfter']=after_matches
  if after_matches!=[number]:raise RuntimeError('Producer FD matching inventory changed')
  if observation['producerFDBefore']!=observation['producerFDAfter']:raise RuntimeError('Producer FD metadata changed between snapshots')
  observation['accepted']=True;proof['mappings'][candidate['line']]=observation
 guard();proof['accepted']=True;return proof

def confirm(proof,batch,consumer,producer,frozen,guard,peer):
 if not proof.get('mappings'):return
 followup={};proof['afterDiskValidation']=followup
 try:
  observe(followup,batch,consumer,producer,frozen,guard,peer)
  if not followup['accepted'] or any(proof.get(k)!=followup.get(k) for k in ('mappings','consumerBefore','producerBefore','privatePeerBefore','mountBefore')):raise RuntimeError('Shared-data witness changed during disk validation')
 except Exception:
  proof['accepted']=False;raise
 proof['confirmedAfterDiskValidation']=True
