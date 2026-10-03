"""Fail-closed disk mapping authority; no imports execute processes or input."""
from pathlib import Path
import hashlib,os,stat
import re

def mapping_authority(raw,expected,runtime,cache_roots,shared_data=None):
 runtime=Path(runtime).resolve();cache_roots=[Path(p).resolve() for p in cache_roots]
 if any(not p.is_relative_to(runtime) for p in cache_roots):raise RuntimeError('Cache allowance outside private runtime')
 frozen={};mutable=[];anonymous=[]
 for line in raw.splitlines():
  parts=line.split(maxsplit=5)
  if len(parts)!=6:continue
  name=parts[5]
  if not name.startswith('/'):continue
  if name.startswith('/memfd:'):
   anonymous.append({'path':name,'permissions':parts[1],'classification':'Anonymous runtime mapping, not a disk input; executable JIT is not frozen disk code'})
   continue
  deleted=name.endswith(' (deleted)');path=Path(name.removesuffix(' (deleted)'));resolved=path.resolve()
  if deleted:
   proof=shared_data or {};observation=proof.get('mappings',{}).get(line)
   if parts[1]=='r--p' and re.fullmatch(r'/dev/shm/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} \(deleted\)',name) and proof.get('accepted') is True and proof.get('consumerRawMapsSHA256')==hashlib.sha256(raw.encode()).hexdigest() and observation and observation.get('accepted') is True and observation.get('mapping',{}).get('line')==line:
    mutable.append({'path':name,'permissions':parts[1],'inode':int(parts[4]),'classification':'Exact producer-owned read-only unlinked tmpfs protocol data; observed bounded snapshots, not frozen disk code','producerProof':observation});continue
   raise RuntimeError('Deleted mapped disk input:'+str(path))
  st=path.stat()
  if not stat.S_ISREG(st.st_mode):raise RuntimeError('Mapped disk input is not a regular file:'+str(path))
  if int(parts[4])!=st.st_ino:raise RuntimeError('Mapped disk inode differs from current input:'+str(path))
  mode=stat.S_IMODE(st.st_mode)
  if resolved.is_relative_to(runtime):
   if 'x' in parts[1] or not any(resolved.is_relative_to(root) for root in cache_roots):raise RuntimeError('Unapproved runtime disk mapping:'+str(path))
   if st.st_uid!=os.getuid():raise RuntimeError('Private mapped cache must have owned UID')
   mutable.append({'path':str(path),'permissions':parts[1],'inode':st.st_ino,'classification':'Non-executable owned profile/cache data only'});continue
  row=expected.get(str(resolved))
  if not row:raise RuntimeError('Actual disk mapping absent from frozen closure:'+str(path))
  actual=hashlib.sha256(path.read_bytes()).hexdigest()
  if actual!=row['sha256'] or mode!=row['mode']:raise RuntimeError('Actual mapped input bytes/mode changed:'+str(path))
  if resolved==Path('/opt/brave-bin/libqt5_shim.so'):raise RuntimeError('Unused missing Qt5 shim actually loaded')
  frozen[str(path)]={'sha256':actual,'mode':mode,'inode':st.st_ino,'permissions':parts[1]}
 return {'frozenFiles':frozen,'ownedMutableMaps':mutable,'anonymousMaps':anonymous}

def exact_files_instance(rows,pid,app):
 exact=[r for r in rows if r.get('pid')==pid and Path(r.get('config_path','')).resolve()==(Path(app)/'shell.qml').resolve()]
 if len(exact)!=1 or not exact[0].get('id'):raise RuntimeError('One exact captured Files instance required')
 return exact[0]
