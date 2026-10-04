"""Independent current640 scoped473 follow-up; root native659 terminal required."""
import argparse,ast,json,os,time
from pathlib import Path
from inventory import ROOT,REPO,sha,load,check,frozen,inventory,FILES,LINKS,PINS,ERRORS,oracle

def main():
 a=argparse.ArgumentParser();a.add_argument('--terminal-attestation',required=True);args=a.parse_args();assert args.terminal_attestation=='root659-terminal-57-pass-cleanup-true';assert not (ROOT/'component-manifest.json').exists()
 specs=[('elm-recovery-delivery-reviewed-v650','6e2adfe16cbd3edee5d28d350a49842d1ea6039dfe84ff116450e0fcb0ec2536'),('elm-recovery-delivery-integrated-gui-v640','f09652e1b61b5850d9efead5ac624c4d3097a69d68470b986fd94655d52765df'),('elm-recovery-delivery-pinned-toolchain-v651','b7375326417b1a42c76a1c7e73eafadcf9061dda656341075c0a82f301e63c59'),('elm-recovery-delivery-current-fixture-v654','be2f7b794c7149109256be31e960f0a146867611b7dd4e19a6d2f38b7335649e'),('elm-recovery-delivery-current-fixture-v660','67a337ab1f629f82f445aaa2da948c85db44e0c7a959afba57590943f4e7869b'),('elm-paged-history-storage-v647','30eaeeada4ff5fcd60c67378d682a74e162eb57721e01d7269909cc3bfa560ac'),('elm-paged-ledger-integration-review-v661','90f7843684bb07f28f6a6bb70616297eeda61d06590ec0c138bf564cc1524bcc'),('elm-uncertainty-layout-review-v662','d0ed87ec3df20fe40a265942595b97db5408309ebbee4931acefce6b8925eea3'),('elm-recovery-delivery-geometry-v658','2e54ccd1349a4447fc00a840fdb136b99026853e39e7d276dd59656c12db67c2'),('elm-recovery-delivery-reconnect-v659','27a2446f1b6d050a965bf0998235e5ab050497322cae84bb1090bf456efc1205')]
 parents=[frozen(REPO/'implementation'/n,h) for n,h in specs]
 gui=REPO/'implementation/elm-recovery-delivery-integrated-gui-v640';build=gui/'qa/build-1791153819143987946/report.json';b=load(build);assert b['passed'];check(build,'66c4a615937fc475712594f59ea8b17969837a26ea3f3eaa0de07fa38e2aab63','selected640 actual build')
 for rel,h in b['inputs'].items():check(gui/rel,h,'640 current source');check(build.parent/'inputs'/rel,b['artifacts'].get('inputs/'+rel,h),'640 captured source/output')
 for rel,h in b['artifacts'].items():check(build.parent/rel,h,'640 actual artifact')
 for group in ('compilerDependencies','tools','linkedLibraries'):
  for rel,v in b[group].items():check(rel,v,'640 compiler closure',True);assert str(Path(rel).resolve())==v['resolved']
 core=REPO/'implementation/elm-grant-retirement-runtime-v595';pair=load(core/'qa/build-pair-manifest.json');assert pair['passed']
 for rel,h in pair['files'].items():check(core/rel,h,'595 pair source')
 for name,v in pair['nativePair'].items():check(v['path'],v['sha256'],'native owning ABI '+name,True)
 suites=[('elm-recovery-delivery-full-menu-v653','1791154566655788530',89,'elm-responsive-full-menu-v281',['wait','click','check']),('elm-recovery-delivery-capability-v655','1791155403706458771',83,'elm-responsive-capability-v283',['wait','click','check']),('elm-recovery-delivery-focus-v657','1791155571310711670',83,'elm-responsive-focus-v284',['wait','click','check']),('elm-recovery-delivery-geometry-v658','1791155859745149870',161,'elm-responsive-geometry-v288',['wait','parent_pointer','open_menu','settle_menu','geometry_row']),('elm-recovery-delivery-reconnect-v659','1791156344029340594',57,'elm-responsive-reconnect-v293',['wait','check','click','keys','right'])]
 native=[];oracles=[]
 for name,stamp,count,ancestor,helpers in suites:
  root=REPO/'implementation'/name;rp=root/'qa'/('native-'+stamp)/'report.json';d=load(rp);assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==count and all(x['passed'] for x in d['checks']);assert d['pair']==pair['nativePair'] and d['buildReport']==str(build);check(build,d['buildReportSHA256'],'native640 consumed build')
  for rel,h in d['inputs'].items():check(rel,h,'native consumed input',True)
  for rel,h in d['artifacts'].items():check(rp.parent/rel,h,'native output evidence')
  if 'preflightSHA256' in d:check(root/'qa/preflight.json',d['preflightSHA256'],'native consumed preflight')
  host=d['privateHost'];assert host['runtimeGone'] and not host['remainingDescendants'] and not host['cleanupErrors'] and not host['unexpectedInnerDescendants'] and not host['mainDisplayUsed'] and d['mainDesktopActions'] is False
  if name.endswith('v658'):
   assert any(x['name']=='normalWebviewAndBackendExit' and x['passed'] for x in d['checks']);assert d['nativeAcceptance'] is False and d['allContractScenariosPassed'] is False
  else:assert any(x['name']=='webviewAndBackendNormalExit' and x.get('exitCode')==0 for x in d['checks'])
  runner=root/'qa/native.py';text=runner.read_text();assert 'xwayland={enabled=false}' in text
  if name.endswith('v653'):assert "str(build_path.parent/'inputs/adapter/daemon.py')" in text
  else:assert 'elm-recovery-delivery-current-fixture-v660' in text
  oracles.append(oracle(runner,REPO/'implementation'/ancestor/'qa/native.py',helpers));inventory(root)
  native.append({'path':str(rp.relative_to(REPO)),'sha256':sha(rp),'passed':True,'cleanupPassed':True,'checks':count,'scope':d['scope'],'legacyNativeAcceptance':d.get('nativeAcceptance'),'legacyAllContractScenariosPassed':d.get('allContractScenariosPassed')})
 # New651 receipt reproduces the same program; never reconstruct old640 producer.
 tc=REPO/'implementation/elm-recovery-delivery-pinned-toolchain-v651';m=load(tc/'component-manifest.json');p=load(tc/'qa/provenance-report.json');assert m['passed'] and m['sameProgramAs640'] and p['passed'] and p['old640CompilerProvenanceReconstructed'] is False;assert p['heldCompilerPackageCacheFiles']==111 and p['dependencyPackages']==7
 check(tc/p['compiler'],p['compilerSHA256'],'new651 held exact Elm compiler');assert p['compilerSHA256']=='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'
 rb=Path(p['buildReport']);pb=load(rb);rp=Path(p['publicReport']);pp=load(rp);assert pb['passed'] and pp['passed'] and len(pp['checks'])==51 and all(x['passed'] for x in pp['checks']);assert len(pb['elmToolchainBeforeAfterChecks'])==21 and all(x['beforeAfterVerified'] for x in pb['elmToolchainBeforeAfterChecks']);assert len(pp['elmToolchainBeforeAfterChecks'])==39 and all(x['beforeAfterVerified'] for x in pp['elmToolchainBeforeAfterChecks'])
 for rel,h in p['productionSourceHashes'].items():check(tc/rel,h,'651 source producer');check(gui/rel,h,'651 source equals640')
 for rel,row in p['sameProgramComparisons'].items():assert row['byteIdentical'] and row['new']==row['parent640'];check(rb.parent/rel,row['new'],'651 reproduced program');check(build.parent/rel,row['parent640'],'640 same program')
 for group in ('compilerDependencies','tools','linkedLibraries'):
  for rel,v in pb[group].items():check(rel,v,'651 native toolchain',True);assert str(Path(rel).resolve())==v['resolved']
 failed=REPO/'implementation/elm-recovery-delivery-current-fixture-v654';fm=load(failed/'component-manifest.json');assert fm['passed'] is False and fm['readyForNative'] is False;fr=load(failed/fm['failedReport']);assert fr['passed'] is False and 'malformed interleaved refresh' in fr['error']
 fixture=REPO/'implementation/elm-recovery-delivery-current-fixture-v660';f=load(fixture/'component-manifest.json');assert f['passed'] and f['finalChecks']==161 and f['originalChecks']==159 and f['additionalStale626Checks']==2 and f['profiles']==['broker','receipt'] and f['backendComponentManifestSHA256']=='f09652e1b61b5850d9efead5ac624c4d3097a69d68470b986fd94655d52765df'
 for x in f['reports']:
  q=load(fixture/x['path']);assert q['passed'] and len(q['checks'])==x['checks'] and all(y['passed'] for y in q['checks'])
 proto=REPO/'implementation/elm-paged-history-storage-v647';pm=load(proto/'component-manifest.json');q=load(proto/pm['report']);assert q['passed'] and q['assertions']==362 and pm['retainedRecords']==1026 and pm['ledgerIntegrated'] is False and pm['S15Accepted'] is False and pm['powerLossQualified'] is False
 rv=REPO/'implementation/elm-paged-ledger-integration-review-v661';rm=load(rv/'component-manifest.json');assert rm['newAssertions']==62 and rm['ledgerIntegrated'] is False and rm['S15Accepted'] is False and rm['historical362NotRerun'] is True
 for rel,v in rm['reviewedInputs'].items():check(REPO/'implementation'/rel,v,'661 independent input review')
 ux=REPO/'implementation/elm-uncertainty-layout-review-v662';u=load(ux/'component-manifest.json');assert u['nativeExecuted'] is False and u['layoutAcceptance'] is False and u['ATCompliance'] is False and u['compiledPreparationChecks']==152 and u['sourceReviewChecks']==129
 for rel in (u['preparationReport'],u['reviewReport']):assert load(ux/rel)['passed']
 for name,_ in specs:inventory(REPO/'implementation'/name)
 # Root664 failed before native on missing PIL. Hold terminal failure if present;
 # live corrected667/665 and future663 are never inventoried.
 failure664=[]
 for root664 in (REPO/'implementation').glob('*v664'):
  if (root664/'qa/failure.json').exists():
   fp=root664/'qa/failure.json';failure664.append({'path':str(fp.relative_to(REPO)),'sha256':sha(fp),'scope':'Terminal pre-native dependency failure, no layout acceptance'});inventory(root664)
 result={'schema':1,'passed':not ERRORS,'errors':ERRORS,'selectedProduction':str(gui.relative_to(REPO)),'currentScopedGeneral473Passed':True,'native':native,'originalOracleReview':oracles,'parents':parents,'651SameProgramReceipt':{'compilerSHA256':p['compilerSHA256'],'heldFiles':111,'packages':7,'publicChecks':51,'guardFixtures':8,'buildBeforeAfterCommands':21,'publicBeforeAfterCommands':39,'sameProgramArtifacts':p['sameProgramComparisons'],'old640CompilerProvenanceReconstructed':False},'654FailedPreparationHeld':True,'660CorrectedFixtureChecks':161,'boundedStorage647':{'filesystemAssertions':362,'retainedRecords':1026,'ledgerIntegrated':False,'S15Accepted':False,'powerLossQualified':False},'independentStorageReview661':{'newAssertions':62,'historical362Rerun':False,'ledgerIntegrated':False,'S15Accepted':False},'uncertaintyPreparation662':{'compiledChecks':152,'sourceReviewChecks':129,'nativeExecuted':False,'layoutAcceptance':False,'ATCompliance':False},'664TerminalFailures':failure664,'pins':dict(sorted(PINS.items())),'terminalAttestation':args.terminal_attestation}
 out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir();report=out/'report.json';report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'report':str(report),'passed':result['passed'],'errors':ERRORS}))
 if ERRORS:raise SystemExit(1)
 inventory(ROOT)
 m={'schema':1,'component':ROOT.name,'sourceHeld':True,'evidenceIntegrityPassed':True,'selectedProduction':str(gui.relative_to(REPO)),'currentScopedGeneral473Passed':True,'currentScopedGeneralChecks':473,'currentScopedGeneralCampaigns':native,'scope':'Five original scoped current640 general campaigns89+83+83+161+57 only; original135 and additive18 separately650held','original135On640SeparatelyQualified':True,'singleOriginNativeLostReleaseAdditive18SeparatelyQualified':True,'newExplicitCompilerSameProgramReceipt651':True,'old640CompilerProvenanceReconstructed':False,'bounds22On640Accepted':False,'allGeometryContractAccepted':False,'uncertaintyLayoutNativeAccepted':False,'nativeATCompliance':False,'mixedMultiOriginNativeDeliveryAccepted':False,'scalableHistoryAccepted':False,'performanceAccepted':False,'fullUIUXAccepted':False,'fullReleaseAccepted':False,'mainDesktopActivated':False,'completedRequirementIds':[],'boundedStorage647FilesystemAssertions':362,'boundedStorage647Records':1026,'independentStorage661NewAssertions':62,'pagedLedgerIntegrated':False,'S15Accepted':False,'powerLossQualified':False,'uncertainty662PreparationOnly':True,'parentPins':parents,'review':str(report.relative_to(REPO)),'reviewSHA256':sha(report),'files':dict(sorted(FILES.items())),'symlinksAndExclusions':dict(sorted(LINKS.items())),'selfExcluded':str((ROOT/'component-manifest.json').relative_to(REPO))}
 manifest=ROOT/'component-manifest.json';manifest.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'manifest':str(manifest),'sha256':sha(manifest),'regularFiles':len(FILES),'specialOrExcluded':len(LINKS)}))
if __name__=='__main__':main()
