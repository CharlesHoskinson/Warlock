"""Root-reviewed mechanical freeze only. This script never launches a desktop."""
import argparse,hashlib,json,os,re,stat
from pathlib import Path
from capture_packet import inventory
B=Path(__file__).resolve().parent.parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_snapshot(ready,expected):
 if ready.parent!=B or not re.fullmatch('[0-9a-f]{64}',expected)or digest(ready)!=expected:raise RuntimeError('Exact reviewed source-ready required')
 row=json.loads(ready.read_bytes());p=B/row['sourceClosure']
 if digest(p)!=row['sourceClosureSHA256']:raise RuntimeError('Reviewed source closure changed')
 captured=json.loads(p.read_bytes())
 for name,sha in captured['inputs'].items():
  f=Path(name)
  if f.is_symlink()or not f.is_file()or digest(f)!=sha or stat.S_IMODE(f.stat().st_mode)!=captured['inputModes'][name]:raise RuntimeError('Reviewed bytes/modes changed: '+name)
 for name,target in captured['symlinks'].items():
  if not Path(name).is_symlink()or os.readlink(name)!=target:raise RuntimeError('Reviewed link changed')
 for name,mode in captured['directoryModes'].items():
  p=Path(name)
  if p.is_symlink()or not p.is_dir()or stat.S_IMODE(p.stat().st_mode)!=mode:raise RuntimeError('Reviewed directory mode changed')
 return row

def emit(path,row):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(B,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-ready',type=Path,required=True);parser.add_argument('--source-ready-sha256',required=True);a=parser.parse_args()
 for p in [B/'frozen-inputs.json',B/'frozen-checkpoint.json']:
  if p.exists()or p.is_symlink():raise RuntimeError('Fresh frozen descriptor/checkpoint required')
 verify_snapshot(a.source_ready,a.source_ready_sha256)
 # This includes all local source-ready descriptors, inherited nested manifests,
 # exact source/mode/link/directory and approved root review/verifier extras.
 row=inventory();row['reviewedSourceReadySHA256']=a.source_ready_sha256;row['nativeAuthorized']=False
 emit(B/'frozen-inputs.json',row)
 checkpoint=dict(manifestSHA256=digest(B/'frozen-inputs.json'),sourceReadySHA256=a.source_ready_sha256,inputs=len(row['inputs']),links=len(row['symlinks']),directories=len(row['directoryModes']),nativeLaunch=False,mainWrites=False)
 emit(B/'frozen-checkpoint.json',checkpoint);print(json.dumps(checkpoint))
