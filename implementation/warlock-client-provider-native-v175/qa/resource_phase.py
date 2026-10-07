"""Additive actual Core19 capture/registry/export/producer/local-FD phase."""
import errno,fcntl,hashlib,json,mmap,os,pathlib,re,time,zlib
from lock_control import publish

def exercise(s,private,pre,env,source_scope,request,exchange,check,host,attached):
 evidence={'snapshots':[],'applicationDroppedReplies':[],'captures':[],'localDescriptorsClosed':0,'nativeAcceptance':False,'fullReleaseAccepted':False}
 binding=attached['binding'];subject=source_scope()['context']['incarnation'];last_sequence=0;last_now=0
 held=[];locker=None;lock_control=s.host.runtime/'resource-phase-lock-control'
 def resource(operation,capture,transfer='0',target_subject=None,**extra):
  nonlocal last_sequence,last_now
  value=request('preview-client-resource-'+operation+'-request',captureRequest=str(capture),subjectIncarnation=target_subject or subject,transfer=str(transfer),**extra)
  if value.get('kind')=='refused':return value
  fields={'protocolVersion','kind','resourceProtocol','operation','binding','requestId','captureRequest','subjectIncarnation','sequence','clock','now','status','producerState','producerBytes','exportState','exportTransfer','exportBytes','locked'}
  check('resourceNativeExactEnvelope-'+str(len(evidence['snapshots'])),set(value)==fields and value['protocolVersion']==3 and value['kind']=='preview-client-resources' and value['resourceProtocol']==1 and value['binding']==binding and value['captureRequest']==str(capture) and value['subjectIncarnation']==(target_subject or subject) and value['clock']==binding['lifetime'] and value['operation']=={'state':'observe','release':'release-export','retire':'retire-producer'}[operation],reply=value)
  for field in ['requestId','captureRequest','subjectIncarnation','sequence','clock','now','producerBytes','exportTransfer','exportBytes']:
   assert isinstance(value[field],str) and re.fullmatch(r'0|[1-9][0-9]*',value[field]) and int(value[field])<=2**64-1
  check('resourceNativeOriginalClockAndSequence-'+str(len(evidence['snapshots'])),int(value['requestId'])>int(capture) and int(value['sequence'])>last_sequence and int(value['now'])>=last_now and isinstance(value['locked'],bool),reply=value)
  last_sequence=int(value['sequence']);last_now=int(value['now']);evidence['snapshots'].append(value);return value
 def owned_capture(tag):
  scope=source_scope();deadline=int(scope['now'])+2000000000
  captured=request('preview-client-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
  check('resource'+tag+'ActualScopedCapture',captured.get('kind')=='preview-client-owned' and captured['previewEligible'] is False,reply=captured)
  header,rights=exchange(1,captured['captureRequest']);assert len(rights)==1;descriptor=rights[0];held.append(descriptor)
  check('resource'+tag+'OriginalSCMRightsContext',header[22]==11 and header[23]==deadline and header[10]<deadline and header[11]>=header[10] and header[18:22]==tuple(int(scope['context'][k]) for k in ['privacy','rendering','scene','content']),header=list(header))
  seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
  check('resource'+tag+'ActualSealedCloexecDescriptor',fcntl.fcntl(descriptor,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(descriptor,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(descriptor).st_size==header[14])
  with mmap.mmap(descriptor,header[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ) as memory:
   encoded=memory[:];check('resource'+tag+'OriginalSealedPNGChecksum',encoded[:8]==b'\x89PNG\r\n\x1a\n' and zlib.crc32(encoded)==header[17])
  evidence['captures'].append({'scope':scope,'reply':captured,'header':list(header),'encodedSHA256':hashlib.sha256(encoded).hexdigest()})
  return captured['captureRequest'],header,descriptor,encoded
 def local_alive(tag,descriptor,encoded):
  check('resource'+tag+'LocalFDIndependent',fcntl.fcntl(descriptor,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.pread(descriptor,len(encoded),0)==encoded)
 def local_close(tag,descriptor):
  os.close(descriptor);held.remove(descriptor)
  try:fcntl.fcntl(descriptor,fcntl.F_GETFD);closed=False
  except OSError as error:closed=error.errno==errno.EBADF
  check('resource'+tag+'ActualLocalFDClose',closed);evidence['localDescriptorsClosed']+=1
 try:
  original,h,descriptor,encoded=owned_capture('Original')
  observed=resource('state',original)
  check('resourceOriginalActualProducerAndExportOwned',observed['status']=='Observed' and observed['producerState']=='Owned' and int(observed['producerBytes'])>0 and observed['exportState']=='Live' and observed['exportTransfer']==str(h[16]) and int(observed['exportBytes'])>0,reply=observed)
  pending=resource('retire',original)
  check('resourceLiveExportBlocksScopedProducerRetirement',pending['status']=='PendingExport' and pending['producerBytes']==observed['producerBytes'] and pending['exportTransfer']==observed['exportTransfer'])
  publish(lock_control,'hold');display=pathlib.Path(env['WAYLAND_DISPLAY']);display=display if display.is_absolute() else s.host.runtime/display
  socket_stat=display.stat();child=next(row for _,row in s.host.processes if row['name']=='hyprland')
  lock_env=dict(env,WARLOCK_PRIVATE_LOCK_FIXTURE='1',WARLOCK_LOCK_CONTROL_PATH=str(lock_control),WAYLAND_DISPLAY=display.name,WARLOCK_LOCK_SOCKET_DEV=str(socket_stat.st_dev),WARLOCK_LOCK_SOCKET_INO=str(socket_stat.st_ino),WARLOCK_LOCK_SERVER_PID=str(child['pid']))
  locker=s.host.launch('resource-private-lock',[pre['lockFixture']],env=lock_env)
  until=time.monotonic()+6
  while time.monotonic()<until:
   s.guard();path=private/'resource-private-lock.log';rows=[json.loads(line) for line in path.read_text().splitlines() if line.startswith('{')] if path.exists() else []
   if any(row.get('event')=='locked' for row in rows):break
   time.sleep(.04)
  else:raise RuntimeError('Original six-second fixture observation deadline')
  locked=resource('state',original)
  check('resourceRealSessionLockKeepsOriginalMetadata',locked['locked'] and locked['producerBytes']==observed['producerBytes'] and locked['exportTransfer']==observed['exportTransfer'])
  # Deliberately drop a complete response at the application boundary. Only
  # the subsequent original-target observation supplies cleanup authority.
  dropped=request('preview-client-resource-release-request',captureRequest=original,subjectIncarnation=subject,transfer=str(h[16]));evidence['applicationDroppedReplies'].append(dropped)
  refreshed=resource('state',original)
  check('resourceFreshObserveRepairsApplicationLostReleaseACK',refreshed['locked'] and refreshed['exportState']=='Released' and refreshed['exportTransfer']=='0' and refreshed['exportBytes']=='0' and refreshed['producerBytes']==observed['producerBytes'])
  pending=resource('retire',original)
  check('resourceActualLockedProducerRemainsPending',pending['status']=='PendingLock' and pending['locked'] and pending['producerBytes']==observed['producerBytes'] and pending['exportTransfer']=='0')
  local_alive('Locked',descriptor,encoded)
  publish(lock_control,'unlock');locker.wait(timeout=5)
  rows=[json.loads(line) for line in (private/'resource-private-lock.log').read_text().splitlines() if line.startswith('{')]
  check('resourcePrivateLockNormalUnlockExit',locker.returncode==0 and any(row.get('event')=='unlock-synced' for row in rows));locker=None
  dropped=request('preview-client-resource-retire-request',captureRequest=original,subjectIncarnation=subject,transfer='0');evidence['applicationDroppedReplies'].append(dropped)
  refreshed=resource('state',original)
  check('resourceFreshObserveRepairsApplicationLostProducerACK',not refreshed['locked'] and refreshed['producerState']=='Retired' and refreshed['producerBytes']=='0' and refreshed['exportState']=='Released' and refreshed['exportBytes']=='0')
  local_alive('BackendZero',descriptor,encoded)
  other,other_h,other_descriptor,other_encoded=owned_capture('Other')
  absent=resource('retire',original)
  check('resourceOldTargetCannotRetireCurrentCapture',absent['status']=='Settled' and absent['producerBytes']=='0' and absent['exportTransfer']=='0')
  current=resource('state',other)
  check('resourceOtherCurrentCaptureStillOwned',current['producerState']=='Owned' and current['exportTransfer']==str(other_h[16]))
  wrong={**binding,'frontend':str(int(binding['frontend'])+1)}
  rejected=resource('state',other,binding=wrong)
  check('resourceActualRegistryRejectsForeignBinding',rejected.get('kind')=='refused',reply=rejected)
  rejected=resource('retire',other,target_subject=str(int(subject)+1))
  check('resourceExactCaptureRejectsForeignSubject',rejected.get('kind')=='refused',reply=rejected)
  rejected=resource('release',other,other_h[16]+1)
  check('resourceExactExportRejectsForeignTransfer',rejected.get('kind')=='refused',reply=rejected)
  after=resource('state',other)
  check('resourceRejectedTargetsPreserveOriginalResourcesAndSequence',int(after['sequence'])==int(current['sequence'])+1 and after['producerBytes']==current['producerBytes'] and after['exportTransfer']==current['exportTransfer'])
  resource('release',other,other_h[16]);settled=resource('retire',other)
  check('resourceActualOtherCaptureScopedBackendDrain',settled['status']=='Settled' and settled['producerBytes']=='0' and settled['exportBytes']=='0')
  local_alive('OtherBackendZero',other_descriptor,other_encoded);local_close('Other',other_descriptor);local_close('Original',descriptor)
  evidence.update(passed=True,applicationBoundaryACKLossOnly=True,actualCoreRegistryAndResources=True,actualSessionLock=True,retainedImportedFDIndependent=True,scope='Actual core16/plugin19 kernel-authenticated registry, original scoped client captures and binary SCM_RIGHTS sealed imports, scoped export/producer metadata and cleanup under actual private session lock, lost application ACK repair, old-target/foreign-binding/subject/transfer refusal and independent local FD closure. Legacy GUI92/native128 campaign remains separate from inactive GUI106 controlled factory and WebKit integration.')
  return evidence
 finally:
  if locker and locker.poll() is None:
   publish(lock_control,'unlock');locker.wait(timeout=5)
   assert locker.returncode==0,'Resource private lock cleanup normal exit'
  for descriptor in held:os.close(descriptor)
