"""Source-only private AQ/bootstrap host closure; root reviews before freeze."""
from pathlib import Path
import argparse,hashlib,json,os,re,shlex,subprocess
B=Path(__file__).resolve().parent;Q=B.parent
HOSTS=(Q/'private-weston-aq-bootstrap-host-v5',Q/'private-weston-x11-bootstrap-host-v3')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,row):
 fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
def verify(row):
 for p,h in row['inputs'].items():
  path=Path(p)
  if path.is_symlink() or sha(path)!=h or path.stat().st_mode&0o7777!=row['inputModes'][p]:raise RuntimeError('Exact bootstrap input changed: '+p)
 for p,t in row['symlinks'].items():
  if not Path(p).is_symlink() or os.readlink(p)!=t:raise RuntimeError('Exact bootstrap link changed: '+p)
 return row

def collect():
 files={};modes={};links={};manifests=[]
 def add(p,expected=None,mode=None):
  p=Path(p);name=str(p)
  if p.is_symlink():
   target=os.readlink(p)
   if name in links and links[name]!=target:raise RuntimeError('Conflicting loader link')
   links[name]=target;add(p.resolve());return
  actual=sha(p);actualmode=p.stat().st_mode&0o7777
  if expected is not None and actual!=expected:raise RuntimeError('Frozen ancestor bytes changed: '+name)
  if mode is not None and mode!=actualmode:raise RuntimeError('Frozen ancestor mode changed: '+name)
  if name in files and files[name]!=actual:raise RuntimeError('Conflicting input')
  files[name]=actual;modes[name]=actualmode
 def packet(p):
  row=json.loads(p.read_text())
  for n,h in row['inputs'].items():add(n,h,row.get('inputModes',{}).get(n))
  for n,t in row.get('symlinks',{}).items():
   if os.readlink(n)!=t:raise RuntimeError('Frozen ancestor link changed')
   add(n)
  add(p);manifests.append(dict(path=str(p),sha256=sha(p)))
 for prior in ('aquamarine-nested-lifecycle-v1','private-weston-aq-host-v4','private-weston-x11-host-v2'):packet(Q/prior/'frozen-inputs.json')
 for directory in (B,*HOSTS,Q/'held-host-bootstrap-causal-review-v1'):
  for p in sorted(directory.rglob('*')):
   if '__pycache__' in p.parts or p.name in ('source-ready.json','frozen-inputs.json'):continue
   if p.is_file() or p.is_symlink():add(p)
 # Compiler-generated prerequisites identify actual headers/build sources, no projection.
 for p in (B/'build').rglob('*.o.d'):
  text=p.read_text().replace('\\\n',' ');body=text.split(':',1)[1]
  for name in shlex.split(body):
   path=Path(name)
   if not path.is_absolute():path=B/'build'/path
   add(path)
 # Static ELF dependency inspection; never executes or dlopens the SO.
 seen=set();needed=[]
 def elf(p):
  p=Path(p);add(p);real=p.resolve()
  if str(real) in seen:return
  seen.add(str(real))
  data=subprocess.check_output(['/usr/bin/readelf','-d',str(real)],text=True,stderr=subprocess.PIPE)
  for soname in re.findall(r'\(NEEDED\).*?\[(.*?)\]',data):
   paths=[B/'prefix/lib'/soname,Path('/usr/lib')/soname]
   path=next((x for x in paths if x.exists()),None)
   if path is None:raise RuntimeError('Unresolved static loader dependency: '+soname)
   needed.append(dict(consumer=str(real),soname=soname,path=str(path)));elf(path)
 for p in (B/'prefix/lib/libaquamarine.so.0.15.0',Path('/usr/bin/cmake'),Path('/usr/bin/c++'),Path('/usr/bin/as'),Path('/usr/bin/ld'),Path('/usr/bin/readelf'),Path('/usr/bin/nm'),Path('/usr/bin/wayland-scanner'),Path('/usr/lib/gcc/x86_64-pc-linux-gnu/16/cc1plus'),Path('/usr/lib/gcc/x86_64-pc-linux-gnu/16/collect2')):elf(p)
 for p in ('/usr/lib/ld-linux-x86-64.so.2','/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml','/usr/share/hwdata/pnp.ids'):add(p)
 result=dict(inputs=files,inputModes=modes,symlinks=links,retainedManifests=manifests,staticELFDependencies=needed,scope='Private AQ post-initial-commit flush plus exact selector-only hosts; live configure/backend/full52 proof pending',nativeLoaded=False,nativeLaunch=False,mainChanges=False,actualFailedWireCauseProved=False)
 return verify(result)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-ready',action='store_true');p.add_argument('--freeze',action='store_true');p.add_argument('--verify',action='store_true');a=p.parse_args()
 if a.verify:
  row=verify(json.loads((B/'frozen-inputs.json').read_text()))
  for host in HOSTS:
   if (host/'frozen-inputs.json').read_bytes()!=(B/'frozen-inputs.json').read_bytes():raise RuntimeError('Private host closure differs')
 else:
  row=collect()
  if a.source_ready:save(B/'source-ready.json',dict(result='source-ready',rootReviewPending=True,nativeLaunch=False,closure=row))
  elif a.freeze:
   ready=json.loads((B/'source-ready.json').read_text())['closure']
   if row!=ready:raise RuntimeError('Reviewed source-ready closure changed')
   for path in (B/'frozen-inputs.json',*(host/'frozen-inputs.json' for host in HOSTS)):
    if path.exists():raise RuntimeError('Fresh freeze refuses existing packet')
   for path in (B/'frozen-inputs.json',*(host/'frozen-inputs.json' for host in HOSTS)):save(path,row)
  else:raise RuntimeError('Explicit review operation required')
 print(json.dumps(dict(result='pass',inputs=len(row['inputs']),modes=len(row['inputModes']),links=len(row['symlinks']),nativeLaunch=False)))
if __name__=='__main__':main()
