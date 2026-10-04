"""Independent scoped473 archival review, after all root-native terminal notices."""
import argparse,ast,hashlib,json,os,resource,stat,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
CACHE={}
def sha(p):
 p=Path(p);s=p.stat();key=(str(p.resolve()),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
 if key not in CACHE:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  CACHE[key]=h.hexdigest()
 return CACHE[key]
def load(p):return json.loads(Path(p).read_text())
FILES={};LINKS={};PINS={};ERRORS=[]
def check(p,v,label,allow_link=False):
 p=Path(p)
 try:
  assert p.is_file(),'not regular file'
  assert allow_link or not p.is_symlink(),'unexpected link'
  digest=v if isinstance(v,str) else v['sha256'];assert sha(p)==digest,'hash mismatch'
  if isinstance(v,dict) and 'size' in v:assert p.stat().st_size==v['size'],'size mismatch'
  PINS[str(p)]=digest
  if p.is_relative_to(REPO) and not p.is_symlink():FILES[str(p.relative_to(REPO))]={'sha256':digest,'size':p.stat().st_size}
 except Exception as ex:ERRORS.append({'label':label,'path':str(p),'error':str(ex)})
def inventory(directory):
 for base,dirs,names in os.walk(directory,followlinks=False):
  for name in list(dirs):
   p=Path(base)/name
   if name in ('elm-stuff','__pycache__') or p.is_symlink():
    dirs.remove(name);LINKS[str(p.relative_to(REPO))]={'kind':'excluded-cache' if not p.is_symlink() else 'symlink','target':os.readlink(p) if p.is_symlink() else None}
  for name in names:
   p=Path(base)/name;s=p.lstat();rel=str(p.relative_to(REPO))
   if stat.S_ISREG(s.st_mode):FILES[rel]={'sha256':sha(p),'size':s.st_size}
   else:LINKS[rel]={'kind':'symlink' if p.is_symlink() else 'runtime-special','target':os.readlink(p) if p.is_symlink() else None}
def frozen(directory,digest):
 p=directory/'component-manifest.json';check(p,digest,'component manifest');d=load(p);rows=d['files']
 rows=rows if isinstance(rows,list) else [{'path':k,**({'sha256':v} if isinstance(v,str) else v)} for k,v in rows.items()]
 for v in rows:
  rel=v['path'];q=(REPO if rel.startswith('implementation/') else directory)/rel
  if 'symlink' in v:
   if not q.is_symlink() or os.readlink(q)!=v['symlink']:ERRORS.append({'label':'manifest link mismatch','path':str(q)})
  else:check(q,v,'manifest file')
 for field in ('symlinks','intentionalUnsafeFixtureSymlinks','intentionalUnsafeGuardFixtureSymlinks','excludedOrSpecial','symlinksAndExclusions'):
  for rel,v in d.get(field,{}).items():
   if isinstance(v,dict) and v.get('kind')!='symlink':continue
   target=v if isinstance(v,str) else v['target'];q=(REPO if rel.startswith('implementation/') else directory)/rel
   if not q.is_symlink() or os.readlink(q)!=target:ERRORS.append({'label':'manifest recorded link mismatch','path':str(q)})
   LINKS[str(q.relative_to(REPO))]={'kind':'symlink','target':target}
 if d.get('parent') and d.get('parentSHA256'):check(REPO/d['parent'],d['parentSHA256'],'parent pin')
 return {'path':str(p.relative_to(REPO)),'sha256':digest,'files':len(rows)}
def dump(x):return ast.dump(x,include_attributes=False)
def calls(t,name):return [dump(n) for n in sorted(ast.walk(t),key=lambda n:(getattr(n,'lineno',0),getattr(n,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
def oracle(current,old,helpers):
 a=ast.parse(old.read_text());b=ast.parse(current.read_text())
 for name in ('check','wait'):assert calls(a,name)==calls(b,name),str(current)+' '+name+' calls'
 for name in helpers:
  x=next(n for n in ast.walk(a) if isinstance(n,ast.FunctionDef) and n.name==name);y=next(n for n in ast.walk(b) if isinstance(n,ast.FunctionDef) and n.name==name);assert dump(x)==dump(y),str(current)+' '+name+' helper'
 return {'ancestor':str(old.relative_to(REPO)),'ancestorSHA256':sha(old),'current':str(current.relative_to(REPO)),'currentSHA256':sha(current),'checkCalls':len(calls(a,'check')),'helpers':helpers}

