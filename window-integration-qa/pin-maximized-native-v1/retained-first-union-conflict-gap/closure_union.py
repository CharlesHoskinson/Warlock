"""Mechanical external inventory union. Never launches or writes native config."""
from pathlib import Path
import hashlib,os,stat

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def union(packet,ancestors,extra=()):
 """Ancestors are declared input/mode/link dictionaries, validated before union.
 Exclude only this packet's own root descriptor; nested descriptors are inputs.
 """
 packet=Path(packet).resolve();own=packet/'frozen-inputs.json';inputs={};modes={};links={}
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
    inputs[name]=sha;modes[name]=row['inputModes'][name];links[name]=os.readlink(p)
   else:include(p,sha,row['inputModes'][name])
  for name,target in row.get('symlinks',{}).items():
   p=Path(name)
   if not p.is_symlink()or os.readlink(p)!=target:raise RuntimeError('Ancestral exact link changed')
   links[name]=target
 for root,ds,fs in os.walk(packet,followlinks=False):
  root=Path(root);ds[:]=sorted(d for d in ds if d not in {'.git','__pycache__'}and not d.startswith('attempt-'))
  for name in ds[:]:
   p=root/name
   if p.is_symlink():include(p);ds.remove(name)
  for name in sorted(fs):include(root/name)
 for p in extra:include(Path(p))
 return dict(inputs=inputs,inputModes=modes,symlinks=links,nativeAuthorized=False,exclusions=['only own root frozen-inputs.json','git and Python cache directories','attempt directories'])
