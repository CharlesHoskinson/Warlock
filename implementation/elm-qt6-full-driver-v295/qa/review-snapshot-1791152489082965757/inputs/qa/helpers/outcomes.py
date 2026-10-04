"""Closed cleanup classifications. Nonzero never means normal service operation."""
import hashlib,os,signal,json
from pathlib import Path
class Refused(ValueError):pass
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def classify(record,rows):
 terminal=rows[-1]
 if terminal['kind']!='terminal' or terminal['error'] is not None or terminal['fallback'] is not False or terminal['liveDescendants']:raise Refused('actual terminal error/fallback/live child')
 descriptor=Path(record['descriptorCapture'])
 if digest(descriptor)!=record['descriptorSHA256']:raise Refused('current exact descriptor hash')
 d=json.loads(descriptor.read_text())
 if d!={'argv':record['argv'],'binarySHA256':record['binarySHA256']}:raise Refused('closed actual descriptor fields')
 header=rows[0]
 if header['argv']!=record['argv'] or header['descriptor']!=record['descriptor'] or header['descriptorSHA256']!=record['descriptorSHA256']:raise Refused('exact original descriptor')
 owned={};exits={};signals={};classes={}
 for index,row in enumerate(rows):
  if row['kind']=='owned-child':
   r=row['identity'];k=(r['pid'],r['start'])
   if k in owned:raise Refused('duplicate owned identity')
   owned[k]=r
  elif row['kind']=='signal':
   r=row['identity'];k=(r['pid'],r['start'])
   if owned.get(k)!=r or k in exits:raise Refused('signal exact owned identity before exit')
   observed=row['observedIdentity']
   if any(observed[k]!=r[k] for k in ('pid','start','uid')) or any(observed[k]!=os.getuid() or r[k]!=os.getuid() for k in ('realUid','effectiveUid','savedUid','filesystemUid')):raise Refused('exact unprivileged signal-time credentials')
   signals.setdefault(k,[]).append((index,row['signal']))
  elif row['kind']=='child-exit':
   r=row['identity'];k=(r['pid'],r['start'])
   if owned.get(k)!=r or k in exits or os.waitstatus_to_exitcode(row['waitStatus'])!=row['exitCode']:raise Refused('unique actual owned exit')
   exits[k]=(index,row)
 declared={}
 for item in terminal['allWaitStatuses']:
  r=item['identity'];k=(r['pid'],r['start'])
  if owned.get(k)!=r or k in declared:raise Refused('exact terminal identity ledger')
  declared[k]=item['exitCode']
 if not owned or set(owned)!=set(exits) or declared!={k:v[1]['exitCode'] for k,v in exits.items()}:raise Refused('full actual conserved wait ledger')
 primary=next(iter(owned))
 if terminal['childExitCode']!=exits[primary][1]['exitCode']:raise Refused('primary actual status')
 unavailable=record['name']=='org.freedesktop.systemd1' and record['argv']==['/bin/false']
 if unavailable:
  if record['source']!='/usr/share/dbus-1/services/org.freedesktop.systemd1.service' or digest(record['source'])!=record['sourceSHA256'] or digest('/bin/false')!=record['binarySHA256']:raise Refused('captured unavailable service and binary')
  if len(owned)!=1 or signals or terminal['cancelled'] is not False or exits[primary][1]['waitStatus']!=256 or terminal['childExitCode']!=1:raise Refused('exact unavailable primary-only exit1')
  return {'serviceOutcome':'expected-unavailable','exitClasses':{str(primary[0])+':'+primary[1]:'expected-unavailable'},'normalServiceOperation':False}
 for k,(index,row) in exits.items():
  code=row['exitCode'];sent=signals.get(k,[])
  if code==0:kind='normal'
  elif code==-signal.SIGTERM and terminal['cancelled'] is True and any(sig==signal.SIGTERM for _,sig in sent):kind='SIGTERM-cancellation'
  elif code==15 and row['waitStatus']==3840 and terminal['cancelled'] is True and record['name']=='org.gtk.vfs.Daemon' and record['argv']==['/usr/lib/gvfsd'] and any(sig==signal.SIGTERM for _,sig in sent):
   if record['source']!='/usr/share/dbus-1/services/org.gtk.vfs.Daemon.service' or digest(record['source'])!=record['sourceSHA256'] or digest(record['argv'][0])!=record['binarySHA256']:raise Refused('captured exact GVfs descriptor')
   kind='SIGTERM-handler-exit15'
  else:raise Refused('unexpected or unsignalled nonzero exit')
  if any(sig==signal.SIGKILL for _,sig in sent):raise Refused('fallback kill never positive cleanup')
  classes[str(k[0])+':'+k[1]]=kind
 return {'serviceOutcome':'cancelled' if any(v!='normal' for v in classes.values()) else 'normal','exitClasses':classes,'normalServiceOperation':all(v=='normal' for v in classes.values())}
