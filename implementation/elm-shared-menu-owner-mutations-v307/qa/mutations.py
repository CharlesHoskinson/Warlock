"""Independent behavioral regression sensitivity on actual shared Elm modules."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT.parent/'elm-shared-staged-menu-carrier-complete-v305'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir()
paths=[SOURCE/'elm.json',*sorted((SOURCE/'src').glob('*.elm')),*[SOURCE/'qa'/n for n in ['shared-menu.cjs','shared-fixtures.json','shared-geometry-fixtures.json']]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':'Actual compiled shared owner cancellation and popup scope tests with three deliberately unsafe mutants; no native GUI qualification','sourceInputs':{str(p.relative_to(SOURCE)):sha(p) for p in paths},'commands':[],'mutants':[]}
shutil.copy2(Path(__file__),OUT/'mutations.py')
def run(label,args,cwd):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180);(OUT/(label+'.stdout')).write_text(p.stdout);(OUT/(label+'.stderr')).write_text(p.stderr);report['commands'].append({'name':label,'exitCode':p.returncode,'argv':args});print(label,p.returncode,flush=True);return p.returncode
try:
 edits=[('baseline',None,None,None),('omit-prepared-owner-cancellation','Desktop.elm','Just provider -> windowBase (TaskbarShell.MenuEvent (Menu.Invalidate (Provider.getBinding provider))) model','Just provider -> (model,[])'),('foreign-popup-scope','OutputController.elm','(popup && owner current/=Just callback.scope) || not canMove','not canMove'),('retain-owner-at-zero-outputs','OutputController.elm','in Controller.update (Controller.Interaction (Desktop.PresentationOwner registered)) controllerModel','in if scope==Nothing then (controllerModel,[]) else Controller.update (Controller.Interaction (Desktop.PresentationOwner registered)) controllerModel')]
 for name,module,old,new in edits:
  target=OUT/name;target.mkdir();
  for p in paths:
   q=target/'inputs'/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  if module:
   p=target/'inputs/src'/module;s=p.read_text()
   if name=='omit-prepared-owner-cancellation':
    start=s.index('        PresentationOwner scope ->');end=s.index('        OwnerScope raw ->',start);region=s[start:end];assert region.count(old)==1;region=region.replace(old,new);s=s[:start]+region+s[end:]
   else:assert s.count(old)==1;s=s.replace(old,new)
   p.write_text(s)
  cwd=target/'inputs';assert run(name+'-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/SharedRecoveryReplay.elm','--output='+str(target/'replay.js')],cwd)==0
  code=run(name+'-checks',['node','qa/shared-menu.cjs',str(target/'replay.js'),'qa/shared-fixtures.json','qa/shared-geometry-fixtures.json',str(target/'checks.json')],cwd);d=json.loads((target/'checks.json').read_text())
  if module:
   failures=[x['name'] for x in d['cases'] if not x['passed']];assert code!=0 and failures;report['mutants'].append({'name':name,'detected':True,'failedCases':failures,'mutatedSHA256':sha(cwd/'src'/module)})
  else:assert code==0 and d['passed'] and d['checks']==13
 for name,digest in report['sourceInputs'].items():assert sha(SOURCE/name)==digest
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
