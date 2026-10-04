import hashlib,json,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1]
for path,row in json.loads((root/'reviewed-inputs.json').read_text()).items():
 p=Path(path);assert p.is_file() and not p.is_symlink();data=p.read_bytes()
 assert hashlib.sha256(data).hexdigest()==row['sha256'] and len(data)==row['size'],str(p)
files={}
for p in sorted(root.rglob('*')):
 if p.is_file() and p.name!='component-manifest.json':
  assert not p.is_symlink();data=p.read_bytes();files[str(p.relative_to(root))]={'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'mode':stat.S_IMODE(p.stat().st_mode)}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'reviewDisposition':'No remaining read-only observer source blocker; native mapping/focus/delivery unqualified','files':files}
p=root/'component-manifest.json';p.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':hashlib.sha256(p.read_bytes()).hexdigest()}))
