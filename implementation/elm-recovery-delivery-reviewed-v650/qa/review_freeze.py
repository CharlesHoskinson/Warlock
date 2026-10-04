"""Own650 review/freeze, terminal native646 only; no GUI execution."""
import argparse,ast,json,os,sys,time
from pathlib import Path
from inventory import ROOT,REPO,sha,load,check,frozen,inventory,FILES,LINKS,PINS,ERRORS,dump

def main():
 a=argparse.ArgumentParser();a.add_argument('--terminal-attestation',required=True);args=a.parse_args();assert args.terminal_attestation=='root646-terminal-18-pass-cleanup-true';assert not (ROOT/'component-manifest.json').exists()
 gui=REPO/'implementation/elm-recovery-delivery-integrated-gui-v640';p630=REPO/'implementation/elm-recovery-delivery-integration-v630';p642=REPO/'implementation/elm-informational-history-drain-v642';p626=REPO/'implementation/elm-reconciliation-startup-order-v626';p641=REPO/'implementation/elm-native-lost-release-preparation-v641';p649=REPO/'implementation/elm-pre-native-source-review-v649';p646=REPO/'implementation/elm-recovery-delivery-native-v646';core=REPO/'implementation/elm-grant-retirement-runtime-v595'
 specs=[('elm-reconciliation-progress-reviewed-v645','209fc5f8dee5e3542472d6fb942a60b52a887d00f8ae9ff0bbe68afce2e47fa6'),('elm-reconciliation-scoped-general-reviewed-v648','bcd53d5abc424cae817372b715084837b8eaa2d37a69d27adad95c24ee7e1b99'),('elm-recovery-delivery-integration-v630','de086f609ef1f04c3a02cef438e4ab9b1629d3bad1ae011ccd5bec279142aac5'),('elm-informational-history-drain-v642','60612a16384282d72c96e3cd2820ef8b8805f23a53b5e418d93f8f36392f8018'),('elm-pre-native-source-review-v649','5b4052d50b771aebcf8fb97d131efec0e680e4b1ab0b5e9bb57854bc3201f713'),('elm-native-lost-release-preparation-v641','50d7c29be57298492e69110d9298acce82fe8b6cacb86fb73d2446e1a292e3ed')]
 parents=[frozen(REPO/'implementation'/n,h) for n,h in specs]
 production=[]
 for directory in ('adapter','native'):
  expected={str(p.relative_to(p630)) for p in (p630/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts};actual={str(p.relative_to(gui)) for p in (gui/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts};assert expected==actual,directory+' exact inventory'
  for rel in sorted(expected):check(gui/rel,sha(p630/rel),'640 production equals630');production.append(rel)
 names={p.name for p in (p626/'src').glob('*.elm')};assert names=={p.name for p in (gui/'src').glob('*.elm')};frontend={}
 for name in sorted(names):
  source=p642 if name in ('ReconciliationTracking.elm','SurfaceController.elm') else p626;check(gui/'src'/name,sha(source/'src'/name),'640 frontend selected parent');frontend[name]=str(source.relative_to(REPO))
 check(gui/'src/Desktop.elm','b7add5eaef405b1b0a75431711f983fcbfa9e17262211e276434e731115d9fdc','Desktop231 guard provenance');check(gui/'assets/shell.css','cd294a6ec59ca0873ff04e68df86b4df471cb4eeed4013fa908a5f11bb790d30','CSS278 provenance')
 for p in (p626/'assets').glob('*'):
  if p.is_file():check(gui/'assets'/p.name,sha(p),'asset626 unchanged')
 for rel,h in load(gui/'qa/parents.json').items():check(REPO/rel,h,'640 parent pin')
 pointer=gui/'qa/current-build.json';bp=Path(load(pointer)['report']);assert bp==gui/'qa/build-1791153819143987946/report.json';b=load(bp);assert b['passed'];check(bp,sha(bp),'actual640 build report');check(pointer,sha(pointer),'actual640 build pointer')
 for rel,h in b['inputs'].items():
  check(gui/rel,h,'640 current build source')
  check(bp.parent/'inputs'/rel,b['artifacts'].get('inputs/'+rel,h),'640 captured build input/output')
 for rel,h in b['artifacts'].items():check(bp.parent/rel,h,'640 compiled artifacts')
 check(bp.parent/'elm-host',b['binarySHA256'],'640 actual native host')
 for group in ('compilerDependencies','tools','linkedLibraries'):
  for rel,v in b[group].items():check(rel,v,'640 '+group,True);assert str(Path(rel).resolve())==v['resolved']
 assert all(x['exitCode']==0 for x in b['commands'])
 for name in ('Main','Bar','Popup'):assert any('--optimize' in x['command'] and 'src/'+name+'.elm' in x['command'] for x in b['commands']),name+' actual optimized compilation'
 cpu=[]
 for directory,count in [('tests-1791153820316433749',51),('drain-1791153891368556594',21),('controls-1791153924910941912',20)]:
  rp=gui/'qa'/directory/'report.json';d=load(rp);assert d['passed'] and len(d['checks'])==count and all(x['passed'] for x in d['checks']);assert d.get('nativeAcceptance') is False
  if 'sourceSHA256' in d:
   for rel,h in d['sourceSHA256'].items():check(gui/'src'/rel,h,'CPU sourceSHA256')
  for rel,h in d.get('sourceHashes',{}).items():check(rel,h,'CPU actual source hashes')
  for rel,h in d.get('frontendSourceHashes',{}).items():check(gui/'src'/rel,h,'CPU actual frontend source hashes')
  if directory.startswith('controls'):assert len(d['compiledControls'])==6 and all(x['detected'] for x in d['compiledControls'])
  cpu.append({'path':str(rp.relative_to(REPO)),'sha256':sha(rp),'checks':count,'mutants':6 if directory.startswith('controls') else 0,'scope':d.get('scope','Actual public compiled reducer controls')})
 review=load(p649/'qa/report.json');assert review['passed'] and review['verdict']=='ready-for-reviewed-native-preflight' and review['checks']==8425 and len(review['pins'])==6499
 for rel,v in review['pins'].items():check(rel,v,'649 reviewed exact pin',True)
 pair=load(core/'qa/build-pair-manifest.json');assert pair['passed']
 for rel,h in pair['files'].items():check(core/rel,h,'595 owning source')
 for key,v in pair['nativePair'].items():check(v['path'],v['sha256'],'595 native '+key,True)
 for key in ('owningAcceptance','producerEvidence','keyboardAcceptance','owningCoreComponent'):check(pair[key],pair[key+'SHA256'],'595 owner '+key)
 native_descriptor=load(core/'native-build-report.json');check(native_descriptor['pluginBuildReport'],native_descriptor['pluginBuildReportSHA256'],'native compiler report');nb=load(native_descriptor['pluginBuildReport']);assert nb['passed'] and nb['core']['sha256']==pair['nativePair']['core']['sha256']
 for group in ('dependencies','linkedLibraries'):
  for rel,h in nb[group].items():check(rel,h,'native '+group,True)
 pre=p646/'qa/preflight.json';pf=load(pre);assert pf['passed'] and pf['gui']==str(gui) and pf['buildReport']==str(bp)
 for rel,h in pf['inputs'].items():check(rel,h,'646 preflight pin',True)
 rp=p646/'qa/native-evidence/report.json';n=load(rp);assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==18 and all(x['passed'] for x in n['checks']);assert n['pair']==pair['nativePair'] and n['buildReport']==str(bp) and n['mainDesktopActions'] is False;check(pre,n['preflightSHA256'],'646 preflight consumed')
 for rel,h in n['artifacts'].items():check(rp.parent/rel,h,'646 native artifact')
 host=n['privateHost'];assert host['runtimeGone'] and not host['remainingDescendants'] and not host['cleanupErrors'] and not host['unexpectedInnerDescendants'] and not host['mainDisplayUsed']
 assert any(x['name']=='webviewAndBackendNormalExit' and x['exitCode']==0 for x in n['checks'])
 original=ast.parse((REPO/'implementation/elm-reconciliation-native-journey-v627/qa/regression.py').read_text());runner=ast.parse((p641/'qa/runner.py').read_text())
 for name in ('click','wait'):
  a=next(x for x in ast.walk(original) if isinstance(x,ast.FunctionDef) and x.name==name);c=next(x for x in ast.walk(runner) if isinstance(x,ast.FunctionDef) and x.name==name);assert dump(a)==dump(c),name+' unchanged native helper'
 fault=n['fault'];fresh=n['freshCertificate'];unknown=fault['record'];effect=n['originalInterruptedIntent'];assert fault['kind']=='qa-release-output-lost' and unknown['status']=='Unknown' and unknown['binding']==effect['binding'] and unknown['intent']==effect['intent'];assert fresh['record']==unknown and fresh['anchorId']==fault['originalRelease']['id'] and fresh['id']!=fault['certificate']['id'];assert fresh['proof']['binding']==n['finalBinding'] and fresh['proof']['queriedBinding']==n['oldBinding'] and fresh['proof']['grantState']=='Retired';assert n['firstRecoveryBinding']!=n['finalBinding']
 for rel in n['artifacts']:
  if rel.endswith('/ledger-v6.json'):
   ledger=load(rp.parent/rel);assert any(x['record']==unknown and x['id']==fault['originalRelease']['id'] for x in ledger['releases'])
  if rel.endswith('/release-deliveries-v1.json'):assert fresh in load(rp.parent/rel)['certificates']
 p652=REPO/'implementation/elm-recovery-delivery-core-journey-v652';r652=p652/'qa/native-1791154509493145109/report.json';d652=load(r652)
 assert d652['passed'] and d652['cleanupPassed'] and len(d652['checks'])==135 and all(x['passed'] for x in d652['checks']);assert d652['pair']==pair['nativePair'] and d652['buildReport']==str(bp);check(bp,d652['buildReportSHA256'],'652 current build');check(p652/'qa/preflight.json',d652['preflightSHA256'],'652 consumed preflight')
 for rel,h in d652['inputs'].items():check(rel,h,'652 native input',True)
 for rel,h in d652['artifacts'].items():check(r652.parent/rel,h,'652 native artifact')
 h652=d652['privateHost'];assert h652['runtimeGone'] and not h652['remainingDescendants'] and not h652['cleanupErrors'] and not h652['unexpectedInnerDescendants'] and not h652['mainDisplayUsed'];assert any(x['name']=='webviewAndBackendNormalExit' and x.get('exitCode')==0 for x in d652['checks'])
 t652=ast.parse((p652/'qa/regression.py').read_text());t135=ast.parse((REPO/'implementation/elm-output-shared-qa-v151/qa/regression.py').read_text())
 def calls(t,name):return [dump(x) for x in sorted(ast.walk(t),key=lambda x:(getattr(x,'lineno',0),getattr(x,'col_offset',0))) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id==name]
 for name in ('check','wait'):assert calls(t652,name)==calls(t135,name)
 for name in ('wait','click','check','choose','press_key'):
  x=next(x for x in ast.walk(t135) if isinstance(x,ast.FunctionDef) and x.name==name);y=next(x for x in ast.walk(t652) if isinstance(x,ast.FunctionDef) and x.name==name);assert dump(x)==dump(y)
 for directory in (gui,p642,p649,p646,p652):inventory(directory)

 provenance={'exactElmCompilerBinarySeparatelyHeld':False,'ElmPackageSourceHashesSeparatelyHeld':False,'recorded':'npm elm@0.19.2-0 version command, node/npm/C tool/header/library bytes and actual optimized artifact hashes','scope':'Already built hash-pinned tuple qualification; no complete compiler reproducibility claim'}
 result={'schema':1,'passed':not ERRORS,'errors':ERRORS,'selectedProduction':str(gui.relative_to(REPO)),'production630InventoryCount':len(production),'production630Files':production,'frontendSelection':frontend,'parents':parents,'actualBuildReport':str(bp.relative_to(REPO)),'actualBuildReportSHA256':sha(bp),'compilerClosureCounts':{k:len(b[k]) for k in ('compilerDependencies','tools','linkedLibraries','artifacts')},'actualCPUReports':cpu,'642HistoricalMutants':{'inherited':13,'targeted':6,'total':19,'scope':'Frozen642 historical compiled mutants; separate from six newly rerun actual640 mutants'},'649ExactReviewedPins':len(review['pins']),'native652':{'path':str(r652.relative_to(REPO)),'sha256':sha(r652),'checks':135,'passed':True,'cleanupPassed':True,'scope':d652['scope']},'native646':{'path':str(rp.relative_to(REPO)),'sha256':sha(rp),'checks':18,'passed':True,'cleanupPassed':True,'scope':n['scope']},'toolchainProvenance':provenance,'pins':dict(sorted(PINS.items())),'terminalAttestation':args.terminal_attestation,'limitations':{'original135On640':True,'full473On640':False,'boundsOn640':False,'mixedMultiOriginNativeDeliveryAcceptance':False,'scalableHistoryAccepted':False,'performanceAccepted':False,'fullUIUXAccepted':False,'fullReleaseAccepted':False}}
 out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir();report=out/'report.json';report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'report':str(report),'passed':result['passed'],'errors':ERRORS}))
 if ERRORS:raise SystemExit(1)
 inventory(ROOT)
 m={'schema':1,'component':ROOT.name,'sourceHeld':True,'evidenceIntegrityPassed':True,'selectedProduction':str(gui.relative_to(REPO)),'productionWired':True,'lostReleaseSameViewExplicitReconnectNativeAccepted':True,'lostReleaseNativeChecks':18,'lostReleaseScope':'One real durable certificate output lost before wire; same retained Elm view, explicit second reconnect, fresh native proof/read certificate anchored to immutable original Unknown, no old replay, next effect from new explicit intent only','actual640PublicCompiledChecks':51,'actual640CoordinatorFilesystemCompiledDrainChecks':21,'actual640TargetedCompiledChecks':20,'actual640CompiledMutantsDetected':6,'frozen642HistoricalCompiledMutants':19,'original135On640Accepted':True,'original473On640Accepted':False,'boundsOn640Accepted':False,'mixedMultiOriginNativeDeliveryAccepted':False,'scalableHistoryAccepted':False,'performanceAccepted':False,'fullUIUXAccepted':False,'fullReleaseAccepted':False,'mainDesktopActivated':False,'completedRequirementIds':[],'toolchainProvenance':provenance,'review':str(report.relative_to(REPO)),'reviewSHA256':sha(report),'parentPins':parents,'files':dict(sorted(FILES.items())),'symlinksAndExclusions':dict(sorted(LINKS.items())),'selfExcluded':str((ROOT/'component-manifest.json').relative_to(REPO))}
 p=ROOT/'component-manifest.json';p.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':sha(p),'files':len(FILES)}))
if __name__=='__main__':main()
