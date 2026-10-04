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
 for field in ('symlinks','intentionalUnsafeFixtureSymlinks','excludedOrSpecial'):
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

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--terminal-attestation',required=True);args=parser.parse_args();assert args.terminal_attestation=='root644-terminal-57-pass-cleanup-true';assert not (ROOT/'component-manifest.json').exists()
 parent_specs=[('elm-reconciliation-integrated-reviewed-v625','c3ae21924ca40b0539458c0ec0b51a58229b1dcf11faae5e838cc9bf39fb0266'),('elm-reconciliation-regression-reviewed-v638','2bb21110d05bb2c4d4e9faefd6f5b36c71b888c32d07052d7c85c4ac41bd6427'),('elm-reconciliation-progress-reviewed-v645','209fc5f8dee5e3542472d6fb942a60b52a887d00f8ae9ff0bbe68afce2e47fa6'),('elm-native-lost-release-preparation-v641','50d7c29be57298492e69110d9298acce82fe8b6cacb86fb73d2446e1a292e3ed'),('elm-reconciliation-geometry-v643','a334f078a34384b8f598c4814c8388bd43e4d511a8a0687c9045306bad95c064'),('elm-reconciliation-reconnect-v644','d61c8f3fb21d0f20556e95fe4c51bddbddc9eafd7de0909f3561b898b429d1a9')]
 components=[frozen(REPO/'implementation'/n,v) for n,v in parent_specs]
 specs=[('elm-reconciliation-full-menu-v631','1791152528506709531',89,'elm-responsive-full-menu-v281',['wait','click','check']),('elm-reconciliation-capability-v635','1791153068380503866',83,'elm-responsive-capability-v283',['wait','click','check']),('elm-reconciliation-focus-v636','1791153142086839486',83,'elm-responsive-focus-v284',['wait','click','check']),('elm-reconciliation-geometry-v643','1791153565172306638',161,'elm-responsive-geometry-v288',['wait','parent_pointer','open_menu','settle_menu','geometry_row']),('elm-reconciliation-reconnect-v644','1791153663684362914',57,'elm-responsive-reconnect-v293',['check','wait','click','keys','right'])]
 native=[];oracles=[];pair=load(REPO/'implementation/elm-grant-retirement-runtime-v595/qa/build-pair-manifest.json')['nativePair'];build_sha='b42a34f1661f68a4fb51b44d293ef4b5c70cc34b837867c22147f1a65a70483e'
 for name,stamp,count,ancestor,helpers in specs:
  r=REPO/'implementation'/name;p=r/'qa'/('native-'+stamp)/'report.json';d=load(p);assert d['passed'] is True and d['cleanupPassed'] is True and len(d['checks'])==count and all(x.get('passed') is True for x in d['checks']),name
  assert d['pair']==pair and d['buildReportSHA256']==build_sha,name+' selected tuple'
  check(Path(d['buildReport']),build_sha,'native build report')
  for key,v in pair.items():check(v['path'],v['sha256'],'native ABI '+key,True)
  for rel,v in d['inputs'].items():check(rel,v,'native input',True)
  for rel,v in d.get('artifacts',{}).items():check(p.parent/rel,v,'native artifact')
  if 'preflightSHA256' in d:check(r/'qa/preflight.json',d['preflightSHA256'],'native preflight')
  host=d['privateHost'];assert host.get('runtimeGone') is True and not host.get('remainingDescendants') and not host.get('cleanupErrors') and not host.get('unexpectedInnerDescendants'),name+' cleanup'
  assert d.get('mainDesktopActions') is False and host.get('mainDisplayUsed') is False,name+' private display'
  assert any((x['name']=='webviewAndBackendNormalExit' and x.get('exitCode')==0) or (name.endswith('v643') and x['name']=='normalWebviewAndBackendExit' and x['passed'] is True) for x in d['checks']),name+' frontend/backend normal exit'
  current=r/'qa/native.py';text=current.read_text();assert 'xwayland={enabled=false}' in text
  if name.endswith('v643'):
   assert "Whole-transition absolute six-second deadline" in text
   assert d.get('nativeAcceptance') is False and d.get('allContractScenariosPassed') is False,'preserve legacy geometry dispositions'
  else:assert 'Unchanged observation deadline' in text
  if not name.endswith('v631'):assert 'elm-reconciliation-current-fixture-v634' in text,name+' current fixture'
  else:assert "str(build_path.parent/'inputs/adapter/daemon.py')" in text,'631 actual captured daemon'
  oracles.append(oracle(current,REPO/'implementation'/ancestor/'qa/native.py',helpers))
  if name.endswith('v644'):
   for rel in ('fixture.py','qa/inspection.py','qa/grab_guard.py','qa/sampling.py'):assert sha(r/rel)==sha(REPO/'implementation'/ancestor/rel),rel
  inventory(r)
  native.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':True,'cleanupPassed':True,'checks':count,'source':d['buildReport'],'legacyNativeAcceptance':d.get('nativeAcceptance'),'legacyAllContractScenariosPassed':d.get('allContractScenariosPassed'),'scope':d['scope']})
 prep=REPO/'implementation/elm-native-lost-release-preparation-v641';pd=load(prep/'component-manifest.json');pr=Path(pd['report']);q=load(pr);assert pd['nativeLaunched'] is False and pd['targetPreflightPending'] is True and q['passed'] and len(q['checks'])==25 and all(x['passed'] for x in q['checks']);inventory(prep)
 # Inventory previously held packets includes preserved failures and repeat-history
 # defect639; unresolved historical dispositions are never rewritten by this review.
 report={'schema':1,'independentReviewPassed':not ERRORS,'errors':ERRORS,'terminalAttestation':args.terminal_attestation,'components':components,'native':native,'originalOracleReview':oracles,'currentScopedGeneralCount':sum(x['checks'] for x in native),'currentScopedGeneral473Passed':not ERRORS and sum(x['checks'] for x in native)==473,'selectedProduction':'implementation/elm-reconciliation-startup-order-v626','nativeLostReleasePreparation':{'checks':25,'report':str(pr),'sha256':sha(pr),'nativeLaunched':False,'targetPreflightPending':True},'externalAndSourcePins':dict(sorted(PINS.items())),'limitations':{'allGeometryContractAccepted':False,'fullUIUXAccepted':False,'fullReleaseAccepted':False,'releaseDeliveryLossNativeAccepted':False,'scalableHistoryAccepted':False,'repeatHistoryDefectOpen':'RECOVERY-639-001','completedRequirementIds':[]}}
 out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir();rp=out/'report.json';rp.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'review':str(rp),'passed':report['independentReviewPassed'],'errors':ERRORS}))
 if ERRORS:raise SystemExit(1)
 inventory(ROOT)
 manifest={'schema':1,'component':ROOT.name,'sourceHeld':True,'evidenceIntegrityPassed':True,'independentReviewPassed':True,'selectedProduction':report['selectedProduction'],'currentScopedGeneral473Passed':True,'currentScopedGeneralChecks':473,'currentScopedGeneralCampaigns':native,'scope':'Five original scoped general GUI campaigns89+83+83+161+57 on626/205/594/AQ155 only; original135 separately held625','originalNative135SeparatelyHeld':True,'allGeometryContractAccepted':False,'fullUIUXAccepted':False,'fullReleaseAccepted':False,'releaseDeliveryLossNativeAccepted':False,'scalableHistoryAccepted':False,'repeatHistoryDefectOpen':'RECOVERY-639-001','nativeLostReleasePreparedCPUChecks':25,'nativeLostReleasePreparedNativeLaunched':False,'nativeLostReleaseTargetPreflightPending':True,'completedRequirementIds':[],'parentPins':components,'review':str(rp.relative_to(REPO)),'reviewSHA256':sha(rp),'files':dict(sorted(FILES.items())),'symlinksAndExclusions':dict(sorted(LINKS.items())),'selfExcluded':str((ROOT/'component-manifest.json').relative_to(REPO))}
 p=ROOT/'component-manifest.json';p.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':sha(p),'regularFiles':len(FILES),'specialOrExcluded':len(LINKS)}))
if __name__=='__main__':main()
