"""Retain native128 freezer assertions and add exact actual Core19 scope."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');out=pathlib.Path(__file__).parent/'freeze_native129.py';assert not out.exists()
s=(repo/'docs/warlock-preview/v91/freeze_native128.py').read_text().replace('warlock-client-provider-native-v128','warlock-client-provider-native-v129')
old="assert len(proof['checks'])==2466+comparison126['current']['actualAttemptChecks']-2 and len(proof['ownedExitCodes'])==277+comparison126['current']['attempts']-1"
assert s.count(old)==1;s=s.replace(old,"assert len(proof['checks'])==2517+comparison126['current']['actualAttemptChecks']-2 and len(proof['ownedExitCodes'])==278+comparison126['current']['attempts']-1")
addition='''
prior128=json.loads(pathlib.Path(preflight['retainedNative128Report']).read_text());comparison128=audit.compare(prior128,proof,stable)
assert comparison128==proof['priorNative128Retention'] and comparison128['fixedOrderedControls']==2459
assert any(row['name']=='allPriorNative128FixedOrderedAndActualRetryAssertionsRetained' and row['passed'] for row in proof['checks'])
resources=proof['actualCaptureResourceEvidence'];assert resources['passed'] and resources['actualCoreRegistryAndResources'] and resources['actualSessionLock'] and resources['retainedImportedFDIndependent'] and resources['applicationBoundaryACKLossOnly']
assert len(resources['captures'])==2 and len(resources['snapshots'])==11 and len(resources['applicationDroppedReplies'])==2 and resources['localDescriptorsClosed']==2
assert len([row for row in proof['checks'] if row['name'].startswith('resource')])==49
for sample in resources['captures']:
 scope=sample['scope'];header=sample['header'];assert header[23]==int(scope['now'])+2000000000 and header[10]<header[23] and header[22]==11
assert all(row['binding']==resources['snapshots'][0]['binding'] and row['clock']==row['binding']['lifetime'] for row in resources['snapshots'])
assert all(int(b['sequence'])>int(a['sequence']) and int(b['now'])>=int(a['now']) for a,b in zip(resources['snapshots'],resources['snapshots'][1:]))
nativeManifest=pathlib.Path(preflight['resourceModuleManifest']);current=json.loads(nativeManifest.read_text());assert current['sourceHeld'] and current['passed']
for rel,row in current['files'].items():assert sha(nativeManifest.parent/rel)==row['sha256'],rel
for rel,alias in current['directoryAliases'].items():assert (nativeManifest.parent/rel).is_symlink() and str((nativeManifest.parent/rel).resolve())==alias
descriptor=json.loads((root/'native-build-report.json').read_text());assert preflight['pair']==proof['pair'] and preflight['pair']['plugin']==descriptor['plugin'] and sha(pathlib.Path(descriptor['plugin']['path']))==descriptor['plugin']['sha256']
'''
old='\nfiles={}';assert s.count(old)==1;s=s.replace(old,'\n'+addition+old)
old="'typedNativeRetirementEvidence':typed,'nativeAcceptance':False";assert s.count(old)==1
s=s.replace(old,"'typedNativeRetirementEvidence':typed,'prior128FixedOrderedControls':comparison128['fixedOrderedControls'],'captureResourceControls':49,'captureResourceSnapshots':11,'actualImportedDescriptorsClosed':2,'captureResourceEvidence':resources,'scope':preflight['scope'],'legacyProviderRuntime':preflight['legacyProviderRuntime'],'nativeAcceptance':False")
a=s.index('report.update(');b=s.index("\n(repo/'docs/warlock-preview/v91/report.json')",a)
s=s[:a]+"report.update(prior126FixedOrderedControls=comparison126['fixedOrderedControls'],prior128FixedOrderedControls=comparison128['fixedOrderedControls'],captureResourceControls=49,captureResourceSnapshots=11,actualImportedDescriptorsClosed=2,captureResourceEvidence=resources,scope=preflight['scope'],legacyProviderRuntime=preflight['legacyProviderRuntime'],next='Qualified bounded GUI92/native129/core16/plugin19 retains all original128/126 fixed controls, actual allocator/expiry oracles and normal exits. Actual Core resource registry/capture/FD/lock metadata witnesses now pass. Held106 control/reader/adoption/Elm changes remain inactive CPU component evidence. Next native106 integration, distinct live-window binding detachment and renderer native outbox/WebKit; all original full release gates remain open.')"+s[b:]
s=s.replace("(repo/'docs/warlock-preview/v91/report.json')","(repo/'docs/warlock-preview/v93/native-report129.json')")
a=s.index(" ['PROGRESS currentGUI92/native128");b=s.index("\n 'progress'",a)
s=s[:a]+" ['PROGRESS heldNative129 exactcore16/plugin19 and retainedGUI92 legacy runtime. Native2517 checks/278 normal exits/full cleanup; actual49 Core registry/resource/SCM_RIGHTS/lock controls,11 scoped snapshots,two imported local descriptors independently closed. Retain2459 original128 and2458 original126 fixed controls plus actual allocator attempts within original expiry. Held106 local FD/GIO/allocator/Elm/current-host CPU and public73 remain separate; controlled factory/new protocol not activated in WebKit. Next owned publication74, distinct live-window preview-binding detachment and native receiver freshness, then renderer native outbox/current integration. All full release gates remain open; no installed changes.'],"+s[b:]
s=s.replace("'docs/warlock-preview/v91/report.json'","'docs/warlock-preview/v93/native-report129.json'")
ast.parse(s);out.write_text(s);print(out)
