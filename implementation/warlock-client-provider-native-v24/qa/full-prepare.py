"""Bind full current shared host to the preserved native768 owning tuple."""
import hashlib,json,pathlib,resource,shutil,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('prepare-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 old=REPO/'implementation/warlock-client-provider-native-v1/qa/preflight.json';pre=json.loads(old.read_text());assert pre['passed']
 for p,h in pre['inputs'].items():assert sha(p)==h,p
 provider=REPO/'implementation/warlock-preview-provider-v29';reports=sorted(provider.glob('qa/build-*/report.json'));assert len(reports)==1;build=reports[0];built=json.loads(build.read_text());assert built['passed']
 inputs=dict(pre['inputs']);inputs[str(old)]=sha(old);inputs[str(build)]=sha(build)
 for rel,h in built['inputs'].items():assert sha(provider/rel)==h;inputs[str(provider/rel)]=h
 for path in [*ROOT.glob('*.py'),*ROOT.glob('*.json'),*ROOT.glob('*.md'),*ROOT.joinpath('qa').glob('*.py')]:
  if path.is_file():inputs[str(path)]=sha(path)
 assets=pathlib.Path(built['compiledAssetPackage']['path'])
 for name,h in built['compiledAssetPackage']['files'].items():assert sha(assets/name)==h;inputs[str(assets/name)]=h
 binary=build.parent/'elm-host';assert sha(binary)==built['binarySHA256'];inputs[str(binary)]=built['binarySHA256']
 pointer=pathlib.Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer');assert pointer.is_file();inputs[str(pointer)]=sha(pointer)
 for directory,key,buildprefix in [('warlock-session-lock-fixture-v1','lockFixture','lock-build-'),('warlock-native-denial-witness-v4','denialWitness','build-')]:
  component=REPO/'implementation'/directory;reports=list(component.glob('qa/'+buildprefix+'*/report.json'));assert len(reports)==1
  report=reports[0];compiled=json.loads(report.read_text());assert compiled['passed'];inputs[str(report)]=sha(report)
  for p,h in compiled['inputs'].items():assert sha(p)==h;inputs[p]=h
  for rel,h in compiled['artifacts'].items():p=report.parent/rel;assert sha(p)==h;inputs[str(p)]=h
  binaryKey='client' if key=='lockFixture' else 'binary';pre[key]=compiled[binaryKey];pre[key+'Report']=str(report)
 retained=REPO/'implementation/warlock-client-provider-native-v9/qa/native-1791244709653558848/report.json';baseline=json.loads(retained.read_text());assert baseline['passed'] and len(baseline['checks'])==828;inputs[str(retained)]=sha(retained);pre['retainedNativeReport']=str(retained)
 freshRetained=REPO/'implementation/warlock-client-provider-native-v11/qa/native-1791246651449352688/report.json';freshBaseline=json.loads(freshRetained.read_text());assert freshBaseline['passed'] and len(freshBaseline['checks'])==857;inputs[str(freshRetained)]=sha(freshRetained);pre['retainedFreshDemandReport']=str(freshRetained)
 imported=REPO/'implementation/warlock-imported-client-witness-v2';reports=list(imported.glob('qa/build-*/report.json'));assert len(reports)==1
 report=reports[0];compiled=json.loads(report.read_text());assert compiled['passed'];inputs[str(report)]=sha(report)
 for path,h in compiled['inputs'].items():assert sha(path)==h;inputs[path]=h
 for rel,h in compiled['artifacts'].items():path=report.parent/rel;assert sha(path)==h;inputs[str(path)]=h
 pre['importedWitness']=compiled['binary'];pre['importedWitnessReport']=str(report)
 importedBaseline=REPO/'implementation/warlock-client-provider-native-v14/qa/native-1791247665571383988/report.json';baseline=json.loads(importedBaseline.read_text());assert baseline['passed'] and len(baseline['checks'])==883;inputs[str(importedBaseline)]=sha(importedBaseline);pre['retainedHistoricalReport']=str(importedBaseline)
 cBridgeBaseline=REPO/'implementation/warlock-client-provider-native-v17/qa/native-1791249357395983423/report.json';baseline=json.loads(cBridgeBaseline.read_text());assert baseline['passed'] and len(baseline['checks'])==904;inputs[str(cBridgeBaseline)]=sha(cBridgeBaseline);pre['retainedImportedReport']=str(cBridgeBaseline)
 guiBaseline=REPO/'implementation/warlock-client-provider-native-v18/qa/native-1791250150656075469/report.json';baseline=json.loads(guiBaseline.read_text());assert baseline['passed'] and len(baseline['checks'])==905;inputs[str(guiBaseline)]=sha(guiBaseline);pre['retainedCBridgeReport']=str(guiBaseline)
 retainedGUI=REPO/'implementation/warlock-client-provider-native-v21/qa/native-1791251678795868798/report.json';baseline=json.loads(retainedGUI.read_text());assert baseline['passed'] and len(baseline['checks'])==918;inputs[str(retainedGUI)]=sha(retainedGUI);pre['retainedFullGUIReport']=str(retainedGUI)
 asymmetric=REPO/'implementation/warlock-imported-client-witness-v4';reports=list(asymmetric.glob('qa/build-*/report.json'));assert len(reports)==1
 report=reports[0];compiled=json.loads(report.read_text());assert compiled['passed'];inputs[str(report)]=sha(report)
 for path,h in compiled['inputs'].items():assert sha(path)==h;inputs[path]=h
 for rel,h in compiled['artifacts'].items():path=report.parent/rel;assert sha(path)==h;inputs[str(path)]=h
 pre['asymmetricWitness']=compiled['binary'];pre['asymmetricWitnessReport']=str(report)
 retainedResume=REPO/'implementation/warlock-client-provider-native-v23/qa/native-1791252749472257123/report.json';baseline=json.loads(retainedResume.read_text());assert baseline['passed'] and len(baseline['checks'])==933;inputs[str(retainedResume)]=sha(retainedResume);pre['retainedResumeReport']=str(retainedResume)
 pre.update(inputs=inputs,fullHostBinary=str(binary),fullHostAssets=str(assets),fullHostBackend=str(build.parent/'inputs/adapter/daemon.py'),fullHostBuildReport=str(build),pointer=str(pointer))
 for p in (build.parent/'inputs/adapter').glob('*.py'):inputs[str(p)]=sha(p)
 assert all(sha(p)==h for p,h in inputs.items())
 (ROOT/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n');r.update(passed=True,inputs=inputs,pair=pre['pair'])
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
