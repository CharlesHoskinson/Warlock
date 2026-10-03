"""Offline stable loader seeds from a fixed retained owned batch; no launches."""
from pathlib import Path
import base64,hashlib,json,stat

def enumerate_inputs(raw_batches,expected,runtime):
 runtime=Path(runtime);missing={};stable={};deleted=[];runtime_rows=[];anonymous=[]
 for batch in raw_batches:
  for row in batch['processes']:
   if row.get('readError') or not row.get('lifetimeBefore') or not row.get('lifetimeAfter'):raise RuntimeError('Incomplete retained owned map observation')
   raw=base64.b64decode(row['rawMapsBase64'],validate=True)
   if len(raw)!=row['rawMapsBytes'] or hashlib.sha256(raw).hexdigest()!=row['rawMapsSHA256'] or raw.decode()!=row['maps']:raise RuntimeError('Retained raw mapping bytes/hash/decode differ')
   for line in row['maps'].splitlines():
    parts=line.split(maxsplit=5)
    if len(parts)!=6 or not parts[5].startswith('/'):continue
    name=parts[5];entry={'identity':row['identity'],'line':line,'path':name,'permissions':parts[1],'device':parts[3],'inode':int(parts[4])}
    if name.startswith('/memfd:'):anonymous.append(entry);continue
    if name.endswith(' (deleted)'):deleted.append(entry);continue
    path=Path(name);resolved=str(path.resolve())
    if path.is_relative_to(runtime):runtime_rows.append(entry);continue
    st=path.stat()
    # Preserve V6's stable disk inode/bytes/mode property. Record both devices;
    # do not invent superblock-device equality for ordinary subvolume files.
    if not stat.S_ISREG(st.st_mode) or st.st_ino!=entry['inode']:raise RuntimeError('Retained stable mapped inode/type changed:'+name)
    if resolved not in stable:
     value={'path':name,'resolved':resolved,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':stat.S_IMODE(st.st_mode),'inode':st.st_ino,'device':st.st_dev,'elf':path.read_bytes()[:4]==b'\x7fELF','aliases':[]}
     old=expected.get(resolved)
     if old and (value['sha256']!=old['sha256'] or value['mode']!=old['mode']):raise RuntimeError('Retained already-frozen mapped input changed:'+name)
     if not old:
      if not path.is_relative_to('/usr'):raise RuntimeError('Unknown missing non-system path requires separate review:'+name)
      missing[resolved]=value
     stable[resolved]=value
    stable[resolved]['aliases'].append(entry)
 return {'stableInputs':list(stable.values()),'missingStableInputs':list(missing.values()),'deletedMappings':deleted,'privateRuntimeMappings':runtime_rows,'anonymousMappings':anonymous,'priorMappingAccepted':False,'newDataAuthorityGranted':False}

def from_packet(b):
 b=Path(b);ret=b/'retained-v6-failure';packet=json.loads((ret/'frozen-inputs.json').read_text());expected={str(Path(r['path']).resolve()):r for r in packet['files']}
 launch=json.loads((ret/'browser-exec.json').read_text());runtime=Path(launch['profile']).parent
 return enumerate_inputs(json.loads((ret/'owned-mapping-evidence.json').read_text()),expected,runtime)
