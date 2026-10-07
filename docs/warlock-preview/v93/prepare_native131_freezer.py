"""Retain all original native freezer checks and add current source130 comparison."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
base=pathlib.Path('/home/hoskinson/omarchy-windows-parity/docs/warlock-preview/v93');s=(base/'freeze_native130.py').read_text().replace("root=repo/'implementation/warlock-client-provider-native-v130'","root=repo/'implementation/warlock-client-provider-native-v131'").replace("len(proof['checks'])==2518+","len(proof['checks'])==2519+")
needle="assert proof['currentGUI110LegacyRuntimeQualified'] and not proof['newURIRouterActivated'] and not proof['newControlledFactoryActivated']";assert s.count(needle)==1
insert="""prior130=json.loads(pathlib.Path(preflight['retainedNative130Report']).read_text());comparison130=audit.compare(prior130,proof,stable)
assert comparison130==proof['priorNative130Retention'] and comparison130['fixedOrderedControls']==2510
assert any(row['name']=='allPriorNative130FixedOrderedAndActualRetryAssertionsRetained' and row['passed'] and row['evidence']==comparison130 for row in proof['checks'])
assert proof['currentGUI119LegacyRuntimeQualified'] and not proof['nativePersistentPolicyActivated'] and not proof['nativeVisualChannelActivated'] and not proof['pureRendererActivated']
"""
s=s.replace(needle,insert+needle)
s=s.replace("'currentGUI110LegacyRuntimeQualified':True,","'currentGUI110LegacyRuntimeQualified':True,'currentGUI119LegacyRuntimeQualified':True,'nativePersistentPolicyActivated':False,'nativeVisualChannelActivated':False,'pureRendererActivated':False,'prior130FixedOrderedControls':comparison130['fixedOrderedControls'],")
needle="(repo/'docs/warlock-preview/v93/native-report130.json')";assert s.count(needle)==1
s=s.replace(needle,"report.update(currentGUI119LegacyRuntimeQualified=True,nativePersistentPolicyActivated=False,nativeVisualChannelActivated=False,pureRendererActivated=False,prior130FixedOrderedControls=comparison130['fixedOrderedControls'],next='Publish Native131 current GUI119 legacy coherence qualification; then actual controlled persistent policy/renderer host with durable input/native-ticket custody/retry and WebKit callback/frame/concealment/URI barriers. Original full release gates remain open.')\n(repo/'docs/warlock-preview/v93/native-report131.json')")
a=s.index(" ['PROGRESS heldNative130");b=s.index('\n ',a+2)
s=s[:a]+" ['PROGRESS heldNative131 current GUI119 compiled legacy runtime/core16/plugin19/AQ155. Native original130 fixed controls plus actual allocator attempts/original expiry/deadlines/pixels/normal teardown retained, current shared visual helpers qualify actual legacy host/DOM only. All original49 Core resource/FD/lock witnesses/11 scoped snapshots/two independent FD closures remain. GUI92 standalone probes remain original identity. New persistent JSC policy/channel/pure renderer/controlled factory/URI routes inactive and not qualified. Next publication and actual controlled host input/native ticket custody/retry, WebKit actual context/async frame/physical concealment/URI barriers. Uncertain worker/revoked delayed proposal and all original full release gates remain; no installed changes.'],"+s[b:]
s=s.replace("'docs/warlock-preview/v93/native-report130.json'","'docs/warlock-preview/v93/native-report131.json'")
ast.parse(s);p=base/'freeze_native131.py';assert not p.exists();p.write_text(s);print(p)
