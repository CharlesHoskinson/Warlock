import hashlib,json,os,resource,stat,time,traceback
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('review-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'fullReleaseAccepted':False}
try:
 refs={}
 def pinned(path,digest):assert sha(path)==digest,path;refs[str(path.relative_to(REPO))]=digest;return json.loads(path.read_text())
 def owned_inventory(m):
  names=[v['path'] for v in m['files']];assert len(names)==len(set(names))
  for v in m['files']:
   p=REPO/v['path']
   if 'symlink' in v:assert p.is_symlink() and os.readlink(p)==v['symlink']
   else:assert not p.is_symlink() and sha(p)==v['sha256'] and p.stat().st_size==v['size'],p
 a=pinned(REPO/'implementation/elm-focus-recovery-integrated-held-v340/acceptance-manifest.json','86d318a1e44007f3d8ac581cd2f0f364c981f1740fe0a93bdd6fc3d27b367912');owned_inventory(a)
 b=pinned(REPO/'implementation/elm-focus-recovery-current-fixture-held-v345/acceptance-manifest.json','85f37f8d8a71f2ab3820dfb00f603e2d10433c95d7e2e8a8848cf0b9c26a1bc4');owned_inventory(b)
 assert a['currentNativeScopedChecks']==224 and b['nativeCurrentTotalScopedChecksWith340']==390 and a['pair']==b['pair'];pair=a['pair']
 producer=REPO/'implementation/elm-focus-recovery-pinned-toolchain-v349';pm=pinned(producer/'component-manifest.json','be3e9e56f9ea55054af8d410942aa38d769b001fa35e9830251699bdfe5d2139')
 assert pm['passed'] and pm['sameProgramAs333'] and pm['publicAssertions']==51 and pm['provenanceGuardFixtures']==8
 for v in pm['files']:
  p=producer/v['path'];assert sha(p)==v['sha256'] and p.stat().st_size==v['size'],p
 for name,target in pm['intentionalUnsafeGuardFixtureSymlinks'].items():assert (producer/name).is_symlink() and os.readlink(producer/name)==target
 provenance=json.loads((producer/'qa/provenance-report.json').read_text());assert provenance['passed'] and all(v['byteIdentical'] for v in provenance['sameProgramComparisons'].values()) and provenance['heldCompilerPackageCacheFiles']==111 and provenance['dependencyPackages']==7
 gui=REPO/'implementation/elm-focus-recovery-integrated-gui-v333';build=gui/'qa/build-1791154674626733228/report.json';original=json.loads(build.read_text());fresh_path=Path(provenance['buildReport']);fresh=json.loads(fresh_path.read_text())
 for name in ['inputs/assets/elm.js','inputs/assets/bar.js','inputs/assets/popup.js']:assert sha(build.parent/name)==sha(fresh_path.parent/name)==original['artifacts'][name]==fresh['artifacts'][name]
 assert sha(build.parent/'elm-host')==sha(fresh_path.parent/'elm-host')==original['binarySHA256']==fresh['binarySHA256']
 native=[]
 paths=[('elm-focus-recovery-integrated-native-v337','native-1791154784041096502',135),('elm-focus-recovery-integrated-menu-v338','native-1791155048206265273',89),('elm-focus-recovery-integrated-capability-v343','native-1791155736788534260',83),('elm-focus-recovery-integrated-focus-v344','native-1791155783734329032',83),('elm-focus-recovery-integrated-geometry-v346','native-1791156230352763195',161),('elm-focus-recovery-integrated-reconnect-v347','native-1791156362831582750',57),('elm-focus-recovery-integrated-lost-release-v348','native-final',18)]
 for name,packet,count in paths:
  p=REPO/'implementation'/name/'qa'/packet/'report.json';m=json.loads(p.read_text());assert m['passed'] and len(m['checks'])==count and all(v['passed'] for v in m['checks']) and m['cleanupPassed'] and m['pair']==pair
  assert m['buildReport']==str(build);h=m['privateHost'];assert not h['mainDisplayUsed'] and h['runtimeGone'] and not any(h[k] for k in ['cleanupErrors','remainingDescendants','unexpectedInnerDescendants'])
  for path,digest in m.get('inputs',{}).items():assert sha(path)==digest,path
  for path,digest in m['artifacts'].items():assert sha(p.parent/path)==digest,path
  refs[str(p.relative_to(REPO))]=sha(p);native.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':count,'passed':True,'normalCleanupPassed':True,'legacyNativeAcceptance':m.get('nativeAcceptance'),'legacyAllContractScenariosPassed':m.get('allContractScenariosPassed')})
  if count==161:assert m['nativeAcceptance'] is False and m['allContractScenariosPassed'] is False
 lost=REPO/'implementation/elm-focus-recovery-integrated-lost-release-v348';pf=json.loads((lost/'qa/preflight.json').read_text());assert pf['passed'] and pf['gui']==str(gui) and pf['outputDirectory']==str(lost/'qa/native-final')
 assert json.loads((lost/'qa/native-final/report.json').read_text())['preflightSHA256']==sha(lost/'qa/preflight.json')
 for p,d in pf['inputs'].items():assert sha(p)==d,p
 controls=json.loads((lost/'qa/controls-1791156433725511265/report.json').read_text());assert controls['passed'] and len(controls['checks'])==25 and all(c['passed'] for c in controls['checks'])
 roots=['implementation/elm-focus-recovery-integrated-geometry-v346','implementation/elm-focus-recovery-integrated-reconnect-v347','implementation/elm-focus-recovery-integrated-lost-release-v348','implementation/elm-focus-recovery-pinned-toolchain-v349',str(ROOT.relative_to(REPO))];files=[]
 for name in roots:
  for p in sorted((REPO/name).rglob('*')):
   if p in [ROOT/'acceptance-manifest.json',OUT/'report.json']:continue
   st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
   if p.is_symlink():row['symlink']=os.readlink(p)
   elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
   elif p.is_dir():continue
   else:raise RuntimeError('Owned special file: '+str(p))
   files.append(row)
 m={'passed':True,'component':ROOT.name,'selectedNativeProduction':str(gui.relative_to(REPO)),'freshSameProgramProducer':str(producer.relative_to(REPO)),'nativeOriginalRecovery135Passed':True,'nativeScopedGeneral473Passed':True,'nativeLostRelease18Passed':True,'currentNativeScopedChecks':626,'nativeCampaigns':native,'sameCompiledProgramPayloads':True,'pair':pair,'compilerSHA256':provenance['compilerSHA256'],'heldCompilerPackageCacheFiles':111,'dependencyPackages':7,'freshBuildCommands':21,'freshPublicAssertions':51,'freshProvenanceGuardControls':8,'cpuLostReleaseFaultControls':25,'references':refs,'ownedRoots':roots,'files':files,'allGeometryContractScenariosAccepted':False,'nativeMixedMultiOriginLossAccepted':False,'nativeArchiveScalingAccepted':False,'nativeATIMEHardwareBudgetsAccepted':False,'fullUIUXAccepted':False,'fullReleaseAccepted':False,'scope':'Original135 plus allfive scoped473 and single-origin same-view actual durable lost-release18, same333 production and byte-identical fresh349 payloads; all broader release gates remain open','next':['current same-program responsive22bounds893/cohort40','mixed multi-origin native recovery','scalable archive migration/C/frontend integration','fullGTK/Qt own-popup integration','preview/restore/continuous motion/window workflow','physical outputs/GPU/high-refresh','AT/IME and usability','measured budgets/soak','representative user acceptance','reversible packaging/deployment/rollback']}
 (ROOT/'acceptance-manifest.json').write_text(json.dumps(m,indent=2)+chr(10));r.update(passed=True,files=len(files),nativeScopedChecks=626,manifestSHA256=sha(ROOT/'acceptance-manifest.json'))
except Exception as e:r.update(error=repr(e),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(r,indent=2)+chr(10));print(json.dumps({'report':str(OUT/'report.json'),**r}));raise SystemExit(not r['passed'])
