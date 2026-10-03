"""Publish source metadata with output captured outside inventoried packet."""
import datetime,hashlib,json,os,stat
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def meta(p):
 s=p.stat();return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=stat.S_IMODE(s.st_mode),size=s.st_size)
def write(p,row):
 with p.open('x')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
old=json.loads((B/'retained-first-handoff-output-race/SOURCE_READY.json').read_text())
previous=json.loads((B/'retained-first-handoff-output-race/SOURCE_READY_INPUTS.json').read_text())
# Runtime sources/mtime and all compilation outputs remain exactly as reviewed.
fixed=json.loads((B/'final-build-source-fixed-v3-before.json').read_text())
for rel,m in fixed['sources'].items():
 p=B/rel;actual=meta(p)
 assert actual['sha256']==m['sha256']and actual['mode']==m['mode']and p.stat().st_mtime_ns==m['mtimeNs'],rel
for rel,target in fixed['links'].items():assert (B/rel).is_symlink()and os.readlink(B/rel)==target
for ancestor in previous['ancestors']:
 root=Path(ancestor['stage'])
 assert meta(root/'SOURCE_READY.json')==ancestor['sourceReady']and meta(root/'SOURCE_READY_INPUTS.json')==ancestor['sourceReadyInputs']
 for rel,m in ancestor['files'].items():assert meta(root/rel)==m,rel
 for rel,m in ancestor['links'].items():assert (root/rel).is_symlink()and os.readlink(root/rel)==m['target']and stat.S_IMODE((root/rel).lstat().st_mode)==m['mode']
 for rel,mode in ancestor['directories'].items():assert stat.S_IMODE((root/rel).stat().st_mode)==mode
symbols=json.loads((B/'final-review/dynamic-symbol-availability-v3.json').read_text())
assert len(symbols['objects'])==2 and all(not r['missing']for r in symbols['objects'])
files={};links={};directories={}
for root,ds,fs in os.walk(B,followlinks=False):
 root=Path(root);ds[:]=sorted(d for d in ds if d not in {'.git','__pycache__'})
 for name in ds[:]:
  p=root/name;rel=str(p.relative_to(B))
  if p.is_symlink():links[rel]=dict(target=os.readlink(p),mode=stat.S_IMODE(p.lstat().st_mode));ds.remove(name)
  else:directories[rel]=stat.S_IMODE(p.stat().st_mode)
 for name in sorted(fs):
  p=root/name;rel=str(p.relative_to(B))
  if rel in {'SOURCE_READY.json','SOURCE_READY_INPUTS.json'}:continue
  if p.is_symlink():links[rel]=dict(target=os.readlink(p),mode=stat.S_IMODE(p.lstat().st_mode))
  else:files[rel]=meta(p)
write(B/'SOURCE_READY_INPUTS.json',dict(schema=1,files=files,links=links,directories=directories,ancestors=previous['ancestors'],exclusions=previous['exclusions'],nativeAuthorized=False))
old.update(created=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceClosureSHA256=meta(B/'SOURCE_READY_INPUTS.json')['sha256'],files=len(files),links=len(links),directories=len(directories),outputCaptureOutsidePacket=True,strongSymbolAvailability='final-review/dynamic-symbol-availability-v3.json',firstDescriptorOutputRaceRetained='retained-first-handoff-output-race',correctedOwningBodiesProof='final-review/approved-hit-and-root-lineage.json')
write(B/'SOURCE_READY.json',old)
# Validate every claimed byte after publisher has finished its writes.
for rel,m in files.items():assert meta(B/rel)==m,rel
print(json.dumps(dict(readySHA256=meta(B/'SOURCE_READY.json')['sha256'],closureSHA256=meta(B/'SOURCE_READY_INPUTS.json')['sha256'],files=len(files),directories=len(directories),links=len(links),parentFiles=sum(len(a['files'])for a in previous['ancestors']),nativeAuthorized=False),indent=2))
