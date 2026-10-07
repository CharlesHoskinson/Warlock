"""Retain exact native128 inputs; add held Core19 pair and reviewed resource phase."""
import hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];repo=root.parents[1];parent=repo/'implementation/warlock-client-provider-native-v128';plugin=repo/'implementation/warlock-family-style-crop-capture-v19'
out=root/'qa'/('prepare-resource-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Exact retained GUI92/native128 source/runtime/probes and current core16/plugin19 pair; additive actual resource registry/capture/lock/FD phase. Does not relabel held106 CPU reports as native/current runtime acceptance.'}
try:
 prior_path=parent/'qa/preflight.json';pre=json.loads(prior_path.read_text());assert pre['passed'] and not pre['nativeLaunched'];inputs=dict(pre['inputs'])
 for path,digest in inputs.items():assert sha(path)==digest,path
 inputs[str(prior_path)]=sha(prior_path)
 manifest=parent/'component-manifest.json';held=json.loads(manifest.read_text());assert held['sourceHeld'] and held['passed'] and held['nativeChecks']==2466 and held['normalOwnedExits']==277
 for rel,row in held['files'].items():assert sha(parent/rel)==row['sha256'],rel
 baseline=pathlib.Path(held['nativeReport']);proof=json.loads(baseline.read_text());assert sha(baseline)==held['nativeReportSHA256'] and proof['passed'] and proof['cleanupPassed'] and len(proof['checks'])==2466 and all(c['passed'] for c in proof['checks']) and len(proof['ownedExitCodes'])==277 and all(p['exitCode']==0 for p in proof['ownedExitCodes'])
 inputs[str(manifest)]=sha(manifest);inputs[str(baseline)]=sha(baseline);pre['retainedNative128Report']=str(baseline)
 pm=plugin/'component-manifest.json';p=json.loads(pm.read_text());assert p['sourceHeld'] and p['passed'] and p['resourceControls']==21 and p['actualExportDescriptorsClosed']==2 and p['resourceCompiledVariants']==3
 for rel,row in p['files'].items():assert sha(plugin/rel)==row['sha256'],rel;inputs[str(plugin/rel)]=row['sha256']
 for rel,alias in p['directoryAliases'].items():assert (plugin/rel).is_symlink() and str((plugin/rel).resolve())==alias
 inputs[str(pm)]=sha(pm)
 descriptor=plugin/'native-build-report.json';pair=json.loads(descriptor.read_text());assert pair['result']=='pass' and sha(root/'native-build-report.json')==sha(descriptor) and sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256']
 assert pre['pair']['core']=={'path':pair['binary'],'sha256':pair['sha256']}
 for field,digest in [('pluginBuildReport','pluginBuildReportSHA256'),('coreComponentManifest','coreComponentManifestSHA256'),('linkClosureReport','linkClosureReportSHA256'),('buildReport','buildReportSHA256')]:assert sha(pair[field])==pair[digest];inputs[pair[field]]=pair[digest]
 plugin_build=json.loads(pathlib.Path(pair['pluginBuildReport']).read_text());assert plugin_build['passed'] and not plugin_build['missingSymbols']
 for key in ['dependencies','linkDependencies','linkedLibraries','tools']:
  for path,digest in plugin_build.get(key,{}).items():assert sha(path)==digest,path;inputs[path]=digest
 for base in [root,root/'qa']:
  for path in base.iterdir():
   if path.is_file():inputs[str(path)]=sha(path)
 inputs[str(descriptor)]=sha(descriptor);pre['pair']['plugin']=pair['plugin']
 pre['resourceModuleManifest']=str(pm);pre['legacyProviderRuntime']='Held GUI92 full host/probes retained exactly from native128; no current106 native acceptance.'
 pre['scope']=report['scope'];pre['inputs']=inputs
 assert not (root/'qa/preflight.json').exists() and all(sha(path)==digest for path,digest in inputs.items())
 (root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n');report.update(passed=True,inputs=inputs,pair=pre['pair'],originalNativeChecksRetained=2466,originalNormalExitsRetained=277)
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1600]}),flush=True);sys.exit(not report['passed'])
