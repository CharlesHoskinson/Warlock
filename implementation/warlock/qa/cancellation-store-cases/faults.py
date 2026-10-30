from fixture import *
from unittest.mock import patch
import stat
cases=['write-zero','file-sync','close','replace','directory-sync','retire-unlink','retire-directory-sync','retire-write-sync','ack-pending-sync']
for case in cases:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-fault-') as temporary:
  root=pathlib.Path(temporary);store=open_store(root,'faultqa','1')
  key,rec,native,wire=prepared(store,intent())
  store.cancellation_attempt(key,'cancel');outcome=native.cancel_effect(wire)
  proof=_native_cancellation_evidence(rec,DEADLINE,wire['preparedId'],outcome,phase='established')
  if case.startswith('retire-') or case=='ack-pending-sync':store.cancellation_observe(key,proof)
  if case=='ack-pending-sync':store.cancellation_finish(key)
  old=(store.path/'ledger-v6.json').read_bytes();live=(store.path/'admissions-v1'/(storage_key(rec)+'.json'))
  directory_inode=(store.path/'admissions-v1').stat().st_ino
  real_write,real_sync,real_close,real_replace,real_unlink=os.write,os.fsync,os.close,os.replace,os.unlink
  original_writer=store.ledger._write_file_locked
  armed=[False];triggered=[0]
  def fail():
   triggered[0]+=1
   raise OSError('injected '+case)
  def writer(name,body,limit):
   armed[0]=name=='ledger-v7.json'
   try:return original_writer(name,body,limit)
   finally:armed[0]=False
  def write(fd,body):
   if armed[0] and case=='write-zero':triggered[0]+=1;return 0
   return real_write(fd,body)
  def sync(fd):
   mode=os.fstat(fd)
   if armed[0] and ((case=='file-sync' and stat.S_ISREG(mode.st_mode)) or (case in ['directory-sync','retire-write-sync','ack-pending-sync'] and stat.S_ISDIR(mode.st_mode))):fail()
   if case=='retire-directory-sync' and stat.S_ISDIR(mode.st_mode) and mode.st_ino==directory_inode:fail()
   return real_sync(fd)
  def close(fd):
   if armed[0] and case=='close' and stat.S_ISREG(os.fstat(fd).st_mode):
    real_close(fd);fail()
   return real_close(fd)
  def replace(src,dst,**kw):
   if armed[0] and case=='replace' and dst=='ledger-v7.json':fail()
   return real_replace(src,dst,**kw)
  def unlink(name,**kw):
   if case=='retire-unlink' and name==storage_key(rec)+'.json':fail()
   return real_unlink(name,**kw)
  with patch.object(store.ledger,'_write_file_locked',writer),patch('cancellation_ledger.os.write',write),patch('cancellation_ledger.os.fsync',sync),patch('cancellation_ledger.os.close',close),patch('cancellation_ledger.os.replace',replace),patch('cancellation_ledger.os.unlink',unlink):
   if case=='ack-pending-sync':refused(lambda:store.cancellation_ack_pending(key),case+' refuses ACK permission')
   elif case.startswith('retire-'):refused(lambda:store.cancellation_finish(key),case+' refuses retirement completion')
   else:refused(lambda:store.cancellation_observe(key,proof),case+' refuses certificate completion')
  check(triggered[0]>=1 and store.ledger.poisoned,case+' actual syscall cut poisons lane')
  refused(lambda:store.cancellation_snapshot(BOUND),case+' poisoned lane does not silently continue')
  check(not any(x['kind']=='effect-decision-ack' for x in native.calls),case+' never ACKs failed local durability')
  check((store.path/'ledger-v6.json').read_bytes()==old,case+' frozen predecessor unchanged')
  store.close()
  with RecoveryStore(root,'faultqa','1',cancellation=True) as reopened:
   record=reopened.cancellation_snapshot(BOUND)[0]
   if case in ['write-zero','file-sync','close','replace']:
    check(record['certificate'] is None and live.exists(),case+' reopens unresolved with exact admission retained')
   else:
    check(record['certificate']['response']==outcome and record['stage']=='AdmissionRetired' and not live.exists(),case+' reopens stored certificate and repairs exact retirement')
   check(record['ackState']!='Acknowledged',case+' restart never manufactures native ACK')
   refused(lambda:reopened.cancellation_ack_pending(key),case+' restart has no old native authority')
   check((reopened.path/'ledger-v6.json').read_bytes()==old,case+' recovery leaves predecessor unchanged')
print(json.dumps({'passed':True,'checks':len(checks),'faultCases':cases,'nativeAcceptance':False,'powerLossProved':False,'scope':'Actual private store syscall failures/poison/reopen with strict native response double; no transport/native/power-loss proof.'}))
