import hashlib,json,os,tarfile
from pathlib import Path
base=Path(__file__).resolve().parent
os.umask(0o077)
def digest(p):
 with Path(p).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
assert base.stat().st_uid==os.getuid() and not base.is_symlink()
assert digest(base/'qa-source.tar')=='44fcfa1419b7f705668fc1afe53e68fd4f1870e0a828f6560b3a8113f2f7f86a'
with tarfile.open(base/'qa-source.tar') as archive:
 for item in archive.getmembers():
  p=Path(item.name);assert item.isfile() and not p.is_absolute() and '..' not in p.parts
 archive.extractall(base,filter='data')
assert digest(base/'qa-manifest.json')=='c73504f1804bb48204d0e9b906abc5d67ac6c9a460f7c12fbbdcf430e991b4b3'
m=json.loads((base/'qa-manifest.json').read_text())
for name,sha in m['qaInputs'].items():assert digest(base/name)==sha
pin=json.loads((base/'model-toolchain.json').read_text())
assert digest(base/'model-toolchain.tar.gz')==pin['archiveSHA256']
toolchain=base/'model-toolchain';toolchain.mkdir(mode=0o700)
with tarfile.open(base/'model-toolchain.tar.gz') as archive:
 for item in archive.getmembers():
  p=Path(item.name);assert not p.is_absolute() and '..' not in p.parts and p.parts[0] in ['node','quint']
 archive.extractall(toolchain,filter='data')
root=toolchain/'quint';rows={}
for p in sorted(root.rglob('*')):
 name=str(p.relative_to(root))
 if p.is_symlink():
  assert p.resolve().is_relative_to(root.resolve());rows[name]={'symlink':p.readlink().as_posix(),'sha256':digest(p) if p.is_file() else None}
 elif p.is_file():rows[name]={'sha256':digest(p)}
assert len(rows)==pin['files'] and hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()==pin['treeSHA256']
assert digest(toolchain/'node')==pin['nodeSHA256']
receipt=dict(qaInputs=len(m['qaInputs']),quintFiles=len(rows),quintTreeSHA256=pin['treeSHA256'],nodeSHA256=pin['nodeSHA256'],networkDownloads=False,nativeAccepted=False)
(base/'stage-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
