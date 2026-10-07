"""Own current GUI119 legacy native source while retaining every original130 oracle."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v130';provider=repo/'implementation/warlock-preview-provider-v119';root=repo/'implementation/warlock-client-provider-native-v131';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['nativeChecks']==2518 and prior['normalOwnedExits']==278 and not root.exists()
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
pm=provider/'component-manifest.json';held=json.loads(pm.read_text());assert held['sourceHeld'] and held['passed'] and held['fullBuildCommands']==115 and not held['realHostPolicyActivated'] and not held['actualRendererProjectionActivated']
for rel,row in held['files'].items():assert sha(provider/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() or n=='preflight.json']
 return [n for n in names if n=='__pycache__']
shutil.copytree(parent,root,ignore=ignore)
scope='Current held GUI119 legacy host/assets/backend requalification on exact core16/plugin19/AQ155. Retain all original130/129/128/126 fixed ordered controls, actual allocator/expiry/deadlines/pixels/resource/receipt/normal teardown. Historical standalone probes retain original sources. New native persistent policy/visual channel/pure renderer/controlled factory/scoped URI route remain inactive and are not qualified by this legacy campaign. No installed/main desktop changes.'
(root/'ANCESTRY.json').write_text(json.dumps({'owner':prior['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'providerManifest':str(pm),'providerManifestSHA256':sha(pm),'purpose':scope,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
p=root/'qa/native.py';s=p.read_text();a=s.index("'scope':");b=s.index(",'checks'",a);s=s[:a]+"'scope':"+repr(scope)+s[b:]
old=" r['priorNative129Retention']=comparison129";assert s.count(old)==1
s=s.replace(old,old+"\n prior130=json.loads(pathlib.Path(pre['retainedNative130Report']).read_text());comparison130=compare(prior130,r,stableNames)\n check('allPriorNative130FixedOrderedAndActualRetryAssertionsRetained',len(prior130['checks'])==2518 and comparison130['passed'],evidence=comparison130)\n r['priorNative130Retention']=comparison130\n r['currentGUI119LegacyRuntimeQualified']=True\n r['nativePersistentPolicyActivated']=False\n r['nativeVisualChannelActivated']=False\n r['pureRendererActivated']=False")
ast.parse(s);p.write_text(s)
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,prior['owner'],str(root.relative_to(repo)),['PROGRESS ownNative131 current heldGUI119 legacy host/assets/backend requalification on exact core16/plugin19/AQ155. Original130/129/128/126 fixed controls, actual allocator/expiry/deadline/pixel/resource/receipt/normal teardown unchanged. Historical probes remain original, new JSC policy/channel/pure renderer/controlled URI route inactive. Next exact preflight then serialized protected native campaign; no installed/main desktop changes. Actual controlled host/renderer barriers, native ticket/input custody and full release gates remain.'],'progress',[str(m.relative_to(repo)),str(pm.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
