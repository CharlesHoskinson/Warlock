"""Actual fixed read-only IPC histories; original query/maintenance absolute1s budgets."""
from pathlib import Path
import hashlib,json,statistics,time,stat
import test_readonly_ipc as fixture

P=Path(__file__).resolve().parent
sources={str(f):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mode':stat.S_IMODE(f.stat().st_mode)} for f in P.iterdir() if f.is_file() and f.suffix=='.py'}
f=fixture.ReadonlyKernelTests();f.setUp();samples=[];rotations=[];failure=None;queries=0;fd_initial=len(__import__('os').listdir('/proc/self/fd'))
try:
 for requested in (0,64,128,256,512,768,1024):
  while f.reader.serial<requested:
   begin=time.monotonic_ns()
   try:
    if f.query(timeout=1)!=b'[]':raise AssertionError('fresh reply differs')
    queries+=1;f.records.clear()
    if len(f.reader.rows)>=64:
     start=time.monotonic_ns();deadline=time.monotonic()+1
     def remaining():
      left=deadline-time.monotonic()
      if left<=0:raise TimeoutError('actual maintenance absolute deadline')
      return left
     f.reader.rotate_closed(remaining)
     rotations.append({'serial':f.reader.serial,'epoch':f.reader.epoch,'elapsedNs':time.monotonic_ns()-start})
     f.records.clear()
   except BaseException as e:
    failure={'phase':'fill','requested':requested,'type':type(e).__name__,'message':str(e),'serial':f.reader.serial};break
  if failure:break
  values=[]
  for _ in range(7):
   begin=time.monotonic_ns()
   try:
    if f.query(timeout=1)!=b'[]':raise AssertionError('fresh reply differs')
    values.append(time.monotonic_ns()-begin);queries+=1;f.records.clear()
   except BaseException as e:
    failure={'phase':'sample','requested':requested,'type':type(e).__name__,'message':str(e),'serial':f.reader.serial};break
  samples.append({'archivedRows':f.reader.serial-len(f.reader.rows),'segments':f.reader.epoch,'activeRows':len(f.reader.rows),
      'genuineRows':f.reader.serial,'elapsedNs':values,'medianNs':statistics.median(values) if values else None,
      'maxNs':max(values) if values else None,'ownedTipGenerations':len(f.reader.current.tips),
      'borrowersAfterQuery':f.reader.current.borrowers,'processFDs':len(__import__('os').listdir('/proc/self/fd'))})
  (P/'v22-history-measurement-progress.json').write_text(json.dumps({'samples':samples,'rotations':rotations,'failure':failure},indent=2)+'\n')
  print(json.dumps(samples[-1]),flush=True)
  if failure:break
 if failure is None:
  begin=time.monotonic_ns();f.reader.assert_closed();audit_close_ns=time.monotonic_ns()-begin
 else:audit_close_ns=None
 source_unchanged=all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==v['sha256'] and stat.S_IMODE(Path(n).stat().st_mode)==v['mode'] for n,v in sources.items())
 result={'version':1,'samples':samples,'rotations':rotations,'failure':failure,'genuineQueries':queries,'actualPeerDataRequests':f.control.requests.count(b'j/clients'),
   'originalQueryTimeoutSeconds':1,'actualMaintenanceTimeoutSeconds':1,'noSyntheticRows':True,'noRuntimeOverrides':True,'sourceUnchanged':source_unchanged,
   'sourceSHA256':sources,'initialProcessFDs':fd_initial,'normalFullAuditCloseNs':audit_close_ns,'normalCurrentFDsClosed':f.reader.current.closed,
   'nativeLaunch':False,'unlimitedHistoryAccepted':False}
 (P/'v22-history-measurement-final.json').write_text(json.dumps(result,indent=2)+'\n')
 assert failure is None and source_unchanged and queries==1031 and result['actualPeerDataRequests']==queries
finally:
 f.reader.current.close(force=True);f.tearDown()
