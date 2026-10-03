"""Complete owned map snapshots before strict validation; no process launch/input."""
import base64,hashlib,time

def error_record(error):
 return {'type':type(error).__name__,'errno':getattr(error,'errno',None),'error':str(error)}

def capture(identities,same,read_maps,label):
 batch={'phase':label,'monotonicNs':time.monotonic_ns(),'validationStarted':False,'processes':[]}
 for identity in identities:
  row={'identity':dict(identity),'lifetimeBefore':same(identity)};batch['processes'].append(row)
  if not row['lifetimeBefore']:
   row.update(lifetimeAfter=False,exitedBeforeObservation=True);continue
  try:
   raw=read_maps(identity['pid'])
   row.update(rawMapsBase64=base64.b64encode(raw).decode(),rawMapsBytes=len(raw),rawMapsSHA256=hashlib.sha256(raw).hexdigest())
   row['maps']=raw.decode('utf-8')
  except (OSError,UnicodeError) as error:row['readError']=error_record(error)
  row['lifetimeAfter']=same(identity)
  if row.get('readError',{}).get('type')=='FileNotFoundError' and not row['lifetimeAfter']:row['exitedDuringObservation']=True
 return batch

def validate(batch,same,authority):
 # Caller must durably persist the entire captured batch first. Validation never
 # obtains additional maps or discards an earlier raw snapshot or failure.
 batch['validationStarted']=True;errors=[]
 for row in batch['processes']:
  if row.get('exitedBeforeObservation') or row.get('exitedDuringObservation'):continue
  try:
   if row.get('readError'):raise RuntimeError('Owned maps unreadable:'+str(row['identity']['pid'])+':'+str(row['readError']))
   if not row['lifetimeBefore'] or not row['lifetimeAfter']:raise RuntimeError('Owned mapping process lifetime changed during capture')
   row.update(authority(row['maps']))
   if not same(row['identity']):raise RuntimeError('Owned mapping process lifetime changed during validation')
   row['accepted']=True
  except Exception as error:
   row.update(accepted=False,validationError=error_record(error));errors.append(error)
 batch['accepted']=not errors
 if errors:raise errors[0]
 return batch
