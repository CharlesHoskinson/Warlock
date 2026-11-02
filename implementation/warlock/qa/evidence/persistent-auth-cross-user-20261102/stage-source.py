import hashlib,json,os,tarfile,tempfile
from pathlib import Path
base=Path(__file__).resolve().parent
stage=Path('/home/charl/warlock-mvp-20261101T1058Z')
source=stage/'source'
m=json.loads((base/'source-manifest.json').read_text())
archive=base/'source-delta.tar'
def digest(p):
 with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
assert base.stat().st_uid==os.getuid() and source.is_dir() and not source.is_symlink()
assert digest(archive)==m['archiveSha256']
expected=m['sources'];before={}
with tarfile.open(archive) as incoming,tarfile.open(base/'source-preimages.tar','x') as saved:
 members=incoming.getmembers()
 assert len(members)==len(expected) and len({p.name for p in members})==len(members)
 for item in members:
  assert item.isfile() and item.name in expected and item.name.startswith('implementation/warlock/haskell/')
  relative=Path(item.name);assert not relative.is_absolute() and '..' not in relative.parts
  target=source/relative
  for ancestor in [target,*target.parents]:
   if ancestor==source.parent:break
   assert not ancestor.is_symlink(),str(ancestor)
  if target.exists():
   assert target.is_file() and target.stat().st_uid==os.getuid()
   before[item.name]=digest(target);saved.add(target,arcname=item.name,recursive=False)
  else:before[item.name]=None
  raw=incoming.extractfile(item).read()
  assert len(raw)==expected[item.name]['bytes'] and hashlib.sha256(raw).hexdigest()==expected[item.name]['sha256']
 for item in members:
  target=source/item.name;target.parent.mkdir(parents=True,exist_ok=True)
  raw=incoming.extractfile(item).read()
  fd,temporary=tempfile.mkstemp(prefix='.engine-stage-',dir=target.parent)
  with os.fdopen(fd,'wb') as stream:stream.write(raw)
  os.replace(temporary,target)
problems=[]
for name,sha in m['completeHaskellSources'].items():
 p=source/name
 if p.is_symlink() or not p.is_file() or digest(p)!=sha:problems.append(name)
receipt=dict(sourceArchiveSha256=digest(archive),preimages=before,preimageArchiveSha256=digest(base/'source-preimages.tar'),completeHaskellInputs=len(m['completeHaskellSources']),sourceMatches=not problems,mismatchedInputs=problems,nativeAccepted=False,releaseAccepted=False)
(base/'source-stage-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='preimages'}))
assert not problems,problems
