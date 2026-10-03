"""Mechanical external inventory union. Never launches or writes native config."""
from pathlib import Path
import hashlib,os,stat

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def union(packet,ancestors,extra=()):
 """Ancestors are declared input/mode/link dictionaries, validated before union.
 Exclude only this packet's own root descriptor; nested descriptors are inputs.
 """
 packet=Path(packet).resolve();own=packet/'frozen-inputs.json';inputs={};modes={};links={};directories={}
 def include(p,sha=None,mode=None):
  p=Path(p);key=str(p)
  if p==own:return
  if p.is_symlink():
   target=os.readlink(p)
   if key in inputs and (links.get(key)!=target or digest(p)!=inputs[key] or stat.S_IMODE(p.stat().st_mode)!=modes[key]):raise RuntimeError('Conflicting file/link role: '+key)
   if key in links and links[key]!=target:raise RuntimeError('Conflicting link: '+key)
   links[key]=target;return
  actual=digest(p);actualmode=stat.S_IMODE(p.stat().st_mode)
  if sha is not None and actual!=sha:raise RuntimeError('Ancestral bytes changed: '+key)
  if mode is not None and (type(mode)is not int or actualmode!=mode):raise RuntimeError('Ancestral mode changed: '+key)
  if key in links:raise RuntimeError('Conflicting file/link role: '+key)
  if key in inputs and (inputs[key]!=actual or modes[key]!=actualmode):raise RuntimeError('Conflicting inherited input: '+key)
  inputs[key]=actual;modes[key]=actualmode
 for row in ancestors:
  if set(row['inputs'])!=set(row['inputModes']):raise RuntimeError('Complete ancestral declared modes required')
  for name,sha in row['inputs'].items():
   # Byte+link aliases are permitted only if the declared manifest records both.
   p=Path(name)
   if p.is_symlink():
    if row.get('symlinks',{}).get(name)!=os.readlink(p):raise RuntimeError('Ancestral link role changed')
    if type(row['inputModes'][name])is not int or digest(p)!=sha or stat.S_IMODE(p.stat().st_mode)!=row['inputModes'][name]:raise RuntimeError('Ancestral alias bytes/mode changed')
    if name in inputs and (inputs[name]!=sha or modes[name]!=row['inputModes'][name]):raise RuntimeError('Conflicting ancestral alias bytes/mode: '+name)
    if name in links and links[name]!=os.readlink(p):raise RuntimeError('Conflicting ancestral alias target: '+name)
    inputs[name]=sha;modes[name]=row['inputModes'][name];links[name]=os.readlink(p)
   else:include(p,sha,row['inputModes'][name])
  for name,target in row.get('symlinks',{}).items():
   p=Path(name)
   if not p.is_symlink()or os.readlink(p)!=target:raise RuntimeError('Ancestral exact link changed')
   if name in links and links[name]!=target:raise RuntimeError('Conflicting ancestral literal target: '+name)
   links[name]=target
  for name,mode in row.get('directoryModes',{}).items():
   p=Path(name)
   if type(mode)is not int or p.is_symlink()or not p.is_dir()or stat.S_IMODE(p.stat().st_mode)!=mode:raise RuntimeError('Ancestral directory changed: '+name)
   if name in directories and directories[name]!=mode:raise RuntimeError('Conflicting ancestral directory mode: '+name)
   directories[name]=mode
 for root,ds,fs in os.walk(packet,followlinks=False):
  root=Path(root)
  if str(root)in directories and directories[str(root)]!=stat.S_IMODE(root.stat().st_mode):raise RuntimeError('Conflicting current directory mode')
  directories[str(root)]=stat.S_IMODE(root.stat().st_mode)
  ds[:]=sorted(d for d in ds if d not in {'.git','__pycache__'}and not d.startswith('attempt-'))
  for name in ds[:]:
   p=root/name
   if p.is_symlink():include(p);ds.remove(name)
  for name in sorted(fs):include(root/name)
 for p in extra:include(Path(p))
 # Recheck the complete captured union after assembly; no stale partial row survives.
 for name,sha in inputs.items():
  p=Path(name)
  if digest(p)!=sha or stat.S_IMODE(p.stat().st_mode)!=modes[name]:raise RuntimeError('Union input changed before return: '+name)
 for name,target in links.items():
  p=Path(name)
  if not p.is_symlink()or os.readlink(p)!=target:raise RuntimeError('Union link changed before return: '+name)
 for name,mode in directories.items():
  p=Path(name)
  if p.is_symlink()or not p.is_dir()or stat.S_IMODE(p.stat().st_mode)!=mode:raise RuntimeError('Union directory changed before return: '+name)
 return dict(inputs=inputs,inputModes=modes,symlinks=links,directoryModes=directories,nativeAuthorized=False,exclusions=['only own root frozen-inputs.json','git and Python cache directories','attempt directories'])
