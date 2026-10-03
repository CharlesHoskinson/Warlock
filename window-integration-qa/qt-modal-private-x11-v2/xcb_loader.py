"""Read-only static closure and actual loaded XCB module checks."""
from pathlib import Path
import hashlib,json,re,subprocess
B=Path(__file__).resolve().parent
QXCB=Path('/usr/lib/qt6/plugins/platforms/libqxcb.so')
QPA=Path('/usr/lib/libQt6XcbQpa.so.6').resolve()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def mapped(pid):
 result={}
 for line in Path(f'/proc/{pid}/maps').read_text().splitlines():
  pieces=line.split(maxsplit=5)
  if len(pieces)==6 and pieces[5].startswith('/') and not pieces[5].endswith(' (deleted)'):
   p=Path(pieces[5])
   if p.is_file():result[str(p.resolve())]=sha(p)
 return result

def native_loader_gate(pid):
 closure=json.loads((B/'xcb-loader-closure.json').read_text());actual=mapped(pid)
 required={str(QXCB.resolve()):sha(QXCB),str(QPA):sha(QPA)}
 if not all(actual.get(p)==value and closure['files'].get(p)==value for p,value in required.items()):raise RuntimeError('actual Qt XCB platform/Qt6XcbQpa mapping missing or changed')
 matched={p:actual[p] for p in actual if p in closure['files']}
 if any(value!=closure['files'][p] for p,value in matched.items()):raise RuntimeError('actual XCB loader dependency changed')
 return {'passed':True,'requiredModules':required,'actualMatchedLoaderFiles':matched,'closureSHA256':sha(B/'xcb-loader-closure.json'),'actualQtPID':pid}

def collect():
 roots=[QXCB,QPA,Path('/usr/bin/Xwayland'),Path('/usr/bin/python3').resolve(),Path('/bin/sh').resolve()]
 roots+=list(Path('/usr/lib/qt6/plugins/xcbglintegrations').glob('*.so'))
 files={};links={};logs={}
 def add(p):
  p=Path(p)
  while p.is_symlink():links[str(p)]=str(p.readlink());p=p.resolve()
  files[str(p)]=sha(p)
 for root in roots:
  add(root);r=subprocess.run(['/usr/bin/ldd',str(root)],capture_output=True,text=True,timeout=10)
  if r.returncode or 'not found' in r.stdout+r.stderr:raise RuntimeError('loader dependency unresolved: '+str(root))
  logs[str(root)]=r.stdout+r.stderr
  for line in r.stdout.splitlines():
   candidates=re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',line)
   for path in candidates:add(path)
 report={'files':files,'symlinks':links,'ldd':logs,'roots':list(map(str,roots)),'nativeLoaderProved':False,'actualMapsRequired':True}
 p=B/'xcb-loader-closure.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'files':len(files),'symlinks':len(links),'sha256':sha(p)}))
if __name__=='__main__':collect()
