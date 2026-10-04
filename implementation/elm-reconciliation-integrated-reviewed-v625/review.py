#!/usr/bin/python3
"""Read-only independent inventory review; writes only an owned timestamped report."""
import argparse, ast, hashlib, json, os, stat, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parent.parent
EXCLUDE={'__pycache__','elm-stuff'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
def inventory(root):
 files={}; special={}
 for base,dirs,names in os.walk(root,followlinks=False):
  for name in list(dirs):
   p=Path(base)/name
   if name in EXCLUDE or p.is_symlink():
    dirs.remove(name);special[str(p.relative_to(root))]={'kind':'excluded-cache' if name in EXCLUDE else 'symlink','target':os.readlink(p) if p.is_symlink() else None}
  for name in names:
   p=Path(base)/name;r=str(p.relative_to(root));s=p.lstat()
   if stat.S_ISREG(s.st_mode):files[r]={'sha256':sha(p),'size':s.st_size}
   else:special[r]={'kind':'symlink' if stat.S_ISLNK(s.st_mode) else 'runtime-special','target':os.readlink(p) if p.is_symlink() else None}
 return {'files':files,'special':special}
def review(config):
 errors=[];checks=[];inventories={};manifests={};builds={}
 def check(p,v,label,follow=False):
  try:
   if p.is_symlink() and not follow:raise ValueError('unexpected symlink')
   if not p.is_file():raise ValueError('not regular file')
   expected=v if isinstance(v,str) else v['sha256']
   if sha(p)!=expected:raise ValueError('hash mismatch')
   if isinstance(v,dict) and 'size' in v and p.stat().st_size!=v['size']:raise ValueError('size mismatch')
   if isinstance(v,dict) and 'resolved' in v and str(p.resolve())!=v['resolved']:raise ValueError('resolved path mismatch')
  except Exception as e:errors.append({'label':label,'path':str(p),'error':str(e)})
 for item in config['components']:
  root=REPO/item['path']; key=item['path'];p=root/'component-manifest.json'
  if 'manifestSHA256' in item:
   check(p,item['manifestSHA256'],key+' manifest');d=load(p);manifests[key]={'sha256':sha(p),'claims':{k:v for k,v in d.items() if k!='files'}}
   rows=d['files'];rows=rows if isinstance(rows,list) else [{'path':k,**({'sha256':v} if isinstance(v,str) else v)} for k,v in rows.items()]
   for row in rows:check(root/row['path'],row,key+' inventory')
   for rel,value in d.get('intentionalUnsafeFixtureSymlinks',{}).items():
    q=root/rel
    if not q.is_symlink() or os.readlink(q)!=value['target']:errors.append({'label':key+' fixture symlink','path':str(q)})
   for field in ('parentProductionFiles','unchangedParentProductionFiles','unchangedProductionFiles'):
    values=d.get(field,{})
    if isinstance(values,dict):
     for rel,v in values.items():
      check(root/rel,v,key+' copied parent')
      if d.get('parent'):check(Path(d['parent'])/rel,v,key+' actual parent')
   checks.append({'component':key,'manifestEntries':len(rows),'sourceHeldFlag':d.get('sourceHeld'),'intentionalSymlinks':len(d.get('intentionalUnsafeFixtureSymlinks',{}))})
  inventories[key]=inventory(root)
  pointer=root/'qa/current-build.json'
  bp=Path(item['buildReport']) if item.get('buildReport') else Path(load(pointer)['report']) if pointer.exists() else None
  if bp:
   b=load(bp);builds[key]={'report':str(bp),'sha256':sha(bp),'passed':b['passed'],'counts':{k:len(b.get(k,{})) for k in ('inputs','compilerDependencies','tools','linkedLibraries','artifacts')}}
   if not b['passed']:errors.append({'label':key+' build did not pass'})
   for group in ('compilerDependencies','tools','linkedLibraries'):
    for rel,v in b.get(group,{}).items():check(Path(rel),v,key+' '+group,True)
   for rel,v in b.get('artifacts',{}).items():check(bp.parent/rel,v,key+' artifact')
   for rel,v in b.get('inputs',{}).items():
    check(root/rel,v,key+' current source input')
    # Compilers overwrite generated assets; the preserved input preimage and final artifacts are distinct contracts.
    if rel in ('assets/elm.js','assets/bar.js','assets/popup.js'):continue
    check(bp.parent/'inputs'/rel,v,key+' build input')
   if b.get('binarySHA256'):check(bp.parent/'elm-host',b['binarySHA256'],key+' native binary')
  pp=root/'qa/parents.json'
  if pp.exists():
   for rel,v in load(pp).items():check(REPO/rel,v,key+' parent pin')
 native=[]
 for item in config.get('nativeReports',[]):
  p=REPO/item['path'];d=load(p)
  if item.get('expectedPassed') is not None and d.get('passed') is not item['expectedPassed']:errors.append({'label':'native disposition','path':str(p)})
  check(Path(d['buildReport']),d['buildReportSHA256'],'native build pin')
  pre=p.parent.parent/'preflight.json';check(pre,d['preflightSHA256'],'native preflight pin');pf=load(pre)
  if not pf.get('passed'):errors.append({'label':'native preflight not passed'})
  for rel,v in pf['inputs'].items():check(Path(rel),v,'native preflight input',True)
  for rel,v in d['inputs'].items():check(Path(rel),v,'native input',True)
  for rel,v in d.get('artifacts',{}).items():check(p.parent/rel,v,'native artifact')
  for name,v in d['pair'].items():check(Path(v['path']),v,'native ABI '+name,True)
  if d.get('passed'):
   if len(d['checks'])!=135 or not all(x.get('passed') is True for x in d['checks']):errors.append({'label':'original135 incomplete'})
   host=d['privateHost']
   if not d.get('cleanupPassed') or not host.get('runtimeGone') or host.get('remainingDescendants') or host.get('cleanupErrors') or host.get('unexpectedInnerDescendants'):errors.append({'label':'native normal cleanup not proven'})
   if not any(x['name']=='webviewAndBackendNormalExit' and x.get('exitCode')==0 for x in d['checks']):errors.append({'label':'native frontend/backend normal exit missing'})
   original=ast.parse((REPO/'implementation/elm-output-shared-qa-v151/qa/regression.py').read_text());actual=ast.parse((p.parent.parent/'regression.py').read_text())
   def calls(tree,name):
    return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(tree),key=lambda n:(getattr(n,'lineno',0),getattr(n,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
   for name in ('check','wait'):
    if calls(original,name)!=calls(actual,name):errors.append({'label':'original AST call mismatch '+name})
   for name in ('wait','click','check','choose','press_key'):
    a=next(n for n in ast.walk(original) if isinstance(n,ast.FunctionDef) and n.name==name);b=next(n for n in ast.walk(actual) if isinstance(n,ast.FunctionDef) and n.name==name)
    if ast.dump(a,include_attributes=False)!=ast.dump(b,include_attributes=False):errors.append({'label':'original AST helper mismatch '+name})
   for rel in ('inspection.py','grab_guard.py'):
    if ast.dump(ast.parse((p.parent.parent/rel).read_text()),include_attributes=False)!=ast.dump(ast.parse((REPO/'implementation/elm-reconciliation-native-journey-v618/qa'/rel).read_text()),include_attributes=False):errors.append({'label':'unchanged native helper '+rel})
  native.append({'report':str(p),'sha256':sha(p),'passed':d.get('passed'),'cleanupPassed':d.get('cleanupPassed'),'checks':d.get('checks'),'error':d.get('error')})
 return {'schema':1,'reviewPassed':not errors,'errors':errors,'checks':checks,'manifests':manifests,'builds':builds,'native':native,'inventories':inventories,'claims':{'nativeAcceptance':False,'mainDesktopActivation':False,'deliveryLossAcceptance':False,'scope':'Independent byte/pin/closure verification only; test results are preserved producer evidence, not rerun acceptance'}}
def main():
 a=argparse.ArgumentParser();a.add_argument('--config',default=str(HERE/'candidate.json'));args=a.parse_args();c=Path(args.config);d=review(load(c));d['configSHA256']=sha(c);d['command']=['review.py','--config',str(c)];out=HERE/'qa'/('review-'+str(time.time_ns()));out.mkdir(parents=True);(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'reviewPassed':d['reviewPassed'],'errors':d['errors'],'components':len(d['inventories'])}));return 0 if d['reviewPassed'] else 1
if __name__=='__main__':raise SystemExit(main())
