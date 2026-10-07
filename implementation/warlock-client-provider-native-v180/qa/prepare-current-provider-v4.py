"""Exact prior campaign closure plus current held GUI110 legacy host identity."""
import hashlib,json,pathlib,resource,sys,time,traceback
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];repo=root.parents[1];parent=repo/'implementation/warlock-client-provider-native-v130';provider=repo/'implementation/warlock-preview-provider-v119';out=root/'qa'/('prepare-current-provider-v4-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Current held GUI119 compiled legacy host/assets/backend on exact retained core16/plugin19. Original130/129/128/126 ordered fixed controls, actual allocator/expiry/deadline/pixel/resource/receipt/teardown preserved; historical standalone probes remain original source. New native persistent policy/visual channel/pure renderer and controlled/scoped detachment URI protocol remain inactive; this legacy campaign qualifies none of their new routes.'}
try:
 path=parent/'qa/preflight.json';pre=json.loads(path.read_text());assert pre['passed'] and not pre['nativeLaunched'];inputs=dict(pre['inputs'])
 for path,value in inputs.items():assert sha(path)==value,path
 m=parent/'component-manifest.json';prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['nativeChecks']==2518 and prior['normalOwnedExits']==278
 for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
 baseline=pathlib.Path(prior['nativeReport']);proof=json.loads(baseline.read_text());assert sha(baseline)==prior['nativeReportSHA256'] and proof['passed'] and proof['cleanupPassed'] and len(proof['checks'])==2518 and len(proof['ownedExitCodes'])==278 and all(c['passed'] for c in proof['checks']) and all(c['exitCode']==0 for c in proof['ownedExitCodes'])
 inputs[str(m)]=sha(m);inputs[str(baseline)]=sha(baseline);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');pre['retainedNative130Report']=str(baseline)
 m=provider/'component-manifest.json';held=json.loads(m.read_text());assert held['sourceHeld'] and held['passed'] and held['fullBuildCommands']==115 and held['originalBuildCommands']==112 and held['orderedVisualCustodyCPUQualified'] and not held['realHostPolicyActivated'] and not held['actualRendererProjectionActivated'] and not held['webKitActivated'] and not held['nativeAcceptance']
 inputs[str(m)]=sha(m)
 for rel,row in held['files'].items():assert sha(provider/rel)==row['sha256'],rel;inputs[str(provider/rel)]=row['sha256']
 build=pathlib.Path(held['reports']['build']['path']);d=json.loads(build.read_text());assert sha(build)==held['reports']['build']['sha256'] and d['passed'] and len(d['commands'])==115 and all(row['exitCode']==0 for row in d['commands'])
 for rel,value in d['inputs'].items():assert sha(provider/rel)==value,rel
 for rel,value in d['artifacts'].items():assert sha(build.parent/rel)==value,rel
 for key in ['compilerDependencies','linkedLibraries','tools']:
  for path,row in d[key].items():
   assert isinstance(row,dict) and sha(path)==row['sha256'] and pathlib.Path(path).stat().st_size==row['size'] and str(pathlib.Path(path).resolve())==row['resolved'],path
   inputs[path]=row['sha256']
 binary=build.parent/'elm-host';assert sha(binary)==d['binarySHA256'];inputs[str(binary)]=sha(binary);inputs[str(build)]=sha(build)
 pre['fullHostBinary']=str(binary);pre['fullHostAssets']=str(build.parent/'inputs/assets');pre['fullHostBackend']=str(build.parent/'inputs/adapter/daemon.py');pre['familyProviderBuild']=str(build)
 pre['currentProviderManifest']=str(m);pre['currentProviderBuild']=str(build);pre['legacyProviderRuntime']=report['scope'];pre['newURIRouterActivated']=False;pre['newControlledFactoryActivated']=False
 pair=json.loads((root/'native-build-report.json').read_text());assert set(pre['pair'])=={'core','plugin','aquamarine'} and pre['pair']['core']=={'path':pair['binary'],'sha256':pair['sha256']} and pre['pair']['plugin']==pair['plugin']
 assert sha(pre['pair']['aquamarine']['path'])==pre['pair']['aquamarine']['sha256']
 assert sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256']
 for base in [root,root/'qa']:
  for p in base.iterdir():
   if p.is_file():inputs[str(p)]=sha(p)
 pre['scope']=report['scope'];pre['inputs']=inputs;assert not (root/'qa/preflight.json').exists() and all(sha(path)==value for path,value in inputs.items())
 (root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n');report.update(passed=True,inputs=inputs,pair=pre['pair'],originalNativeChecksRetained=2518,originalNormalExitsRetained=278,currentProviderManifest=str(m),currentProviderBuild=str(build))
except Exception as error:report['error']=repr(error);report['traceback']=traceback.format_exc()
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1800]}),flush=True);sys.exit(not report['passed'])
