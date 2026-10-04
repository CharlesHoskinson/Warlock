import hashlib,json,os,resource,stat,time,traceback
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'fullReleaseAccepted':False}
try:
 gui=REPO/'implementation/elm-focus-recovery-integrated-gui-v333';refs={}
 def report(p):
  m=json.loads(p.read_text());assert m['passed'],p;refs[str(p.relative_to(REPO))]=sha(p);return m
 audit=report(REPO/'implementation/elm-focus-recovery-integration-audit-v334/qa/review-1791154650502982303/report.json')
 for name,d in audit['candidateProductionPins'].items():assert sha(gui/name)==d,name
 for p,d in audit['primaryProductionPins'].items():assert sha(p)==d,p
 build_path=gui/'qa/build-1791154674626733228/report.json';b=report(build_path);assert len(b['commands'])==21 and all(c['exitCode']==0 for c in b['commands'])
 assert json.loads((gui/'qa/current-build.json').read_text())['report']==str(build_path)
 for name,d in b['inputs'].items():assert sha(gui/name)==d,name
 for name,d in b['artifacts'].items():assert sha(build_path.parent/name)==d,name
 assert sha(build_path.parent/'elm-host')==b['binarySHA256']
 for section in ['compilerDependencies','tools','linkedLibraries']:
  for p,d in b[section].items():assert sha(p)==d['sha256'],p
 public=report(gui/'qa/tests-1791154674631575841/report.json');assert len(public['checks'])==51 and all(c['passed'] for c in public['checks'])
 for name,d in public['sourceSHA256'].items():assert sha(gui/'src'/name)==d,name
 drain=report(gui/'qa/drain-1791154726900489297/report.json');assert len(drain['checks'])==21 and all(c['passed'] for c in drain['checks'])
 for name,d in drain['frontendSourceHashes'].items():assert sha(gui/'src'/name)==d,name
 for p,d in drain['sourceHashes'].items():assert sha(p)==d,p
 assert "sys.path.insert(0,str(ROOT/'adapter'))" in (gui/'qa/drain.py').read_text()
 controls=report(gui/'qa/controls-1791154745873534661/report.json');assert len(controls['checks'])==20 and len(controls['compiledControls'])==6 and all(c['passed'] for c in controls['checks']) and all(c['detected'] for c in controls['compiledControls'])
 context=report(REPO/'implementation/elm-focus-recovery-integrated-context-qa-v335/qa/checks-1791154675866002943/report.json');assert len(context['current']['checks'])==20 and all(c['passed'] for c in context['current']['checks']) and context['counterexamples']
 for p,d in context['inputs'].items():assert sha(p)==d,p
 pair=json.loads((REPO/'implementation/elm-grant-retirement-runtime-v595/qa/build-pair-manifest.json').read_text())['nativePair'];native=[]
 for name,packet,count in [('elm-focus-recovery-integrated-native-v337','native-1791154784041096502',135),('elm-focus-recovery-integrated-menu-v338','native-1791155048206265273',89)]:
  p=REPO/'implementation'/name/'qa'/packet/'report.json';m=report(p)
  assert len(m['checks'])==count and all(c['passed'] for c in m['checks']) and m['cleanupPassed'] and m['pair']==pair
  assert m['buildReport']==str(build_path) and m['buildReportSHA256']==sha(build_path)
  assert not m['mainDesktopActions'] and not m['privateHost']['mainDisplayUsed']
  cleanup=m['privateHost'];assert all(k in cleanup for k in ['runtimeGone','cleanupErrors','remainingDescendants','unexpectedInnerDescendants']) and cleanup['runtimeGone'] and not any(cleanup.get(k) for k in ['cleanupErrors','remainingDescendants','unexpectedInnerDescendants'])
  for path,d in m['inputs'].items():assert sha(path)==d,path
  for path,d in m['artifacts'].items():assert sha(p.parent/path)==d,path
  native.append({'report':str(p.relative_to(REPO)),'sha256':sha(p),'checks':count,'passed':True,'normalCleanupPassed':True})
 roots=['implementation/elm-focus-recovery-integration-audit-v332','implementation/elm-focus-recovery-integrated-gui-v333','implementation/elm-focus-recovery-integration-audit-v334','implementation/elm-focus-recovery-integrated-context-qa-v335','implementation/elm-focus-recovery-integrated-menu-v336','implementation/elm-focus-recovery-integrated-native-v337','implementation/elm-focus-recovery-integrated-menu-v338','implementation/elm-focus-recovery-integrated-held-v339',str(ROOT.relative_to(REPO))]
 inventory=[]
 for name in roots:
  for p in sorted((REPO/name).rglob('*')):
   if p in [ROOT/'acceptance-manifest.json',OUT/'report.json']:continue
   st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
   if p.is_symlink():row['symlink']=os.readlink(p)
   elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
   elif p.is_dir():continue
   else:raise RuntimeError('Owned special file: '+str(p))
   inventory.append(row)
 m={'passed':True,'component':ROOT.name,'selectedProduction':str(gui.relative_to(REPO)),'currentNativeScopedChecks':224,'nativeCampaigns':native,'sameCompiledGUIAndPair':True,'pair':pair,'buildCommands':21,'compiledPublicControllerChecks':51,'ownAdapterDrainChecks':21,'compiledRecoveryControls':20,'compiledMutantsDetected':6,'inertContextControls':20,'fullGUI473Accepted':False,'lostReleaseRepeatNativeAccepted':False,'physicalOutputsGPUATIMEAccepted':False,'fullReleaseAccepted':False,'references':refs,'ownedRoots':roots,'files':inventory,'scope':'Current333 original135 recovery journey and original89 menu native qualification only; preserved source/glyph/focus ancestry327 and newer640 recovery source; no transferred broad acceptance','openGates':['actual captured333 broker/receipt fixture plus originalcap83/focus83/geometry161/reconnect57','current333 actual lost-release/repeated restart campaign','current responsive893 and renderercohort40','fullGTK/Qt','capture/restore/motion','outputs/GPU/high-refresh','AT/IME','budgets/soak','representative user journeys','reversible packaging/deployment/rollback']}
 (ROOT/'acceptance-manifest.json').write_text(json.dumps(m,indent=2)+'\n');r.update(passed=True,nativeChecks=224,manifestSHA256=sha(ROOT/'acceptance-manifest.json'),files=len(inventory))
except Exception as e:r.update(error=repr(e),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'report':str(OUT/'report.json'),**r}));raise SystemExit(not r['passed'])
