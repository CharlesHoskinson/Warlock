"""Own fresh native128 campaign derivative for actual Core19 resource metadata."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v129';root=repo/'implementation/warlock-client-provider-native-v130'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeChecks']==2517 and d['normalOwnedExits']==278 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['warlock-preview-provider-v110','warlock-family-style-crop-capture-v19']:
 base=repo/'implementation'/name;held=json.loads((base/'component-manifest.json').read_text());assert held['sourceHeld'] and held['passed']
 for rel,row in held['files'].items():assert sha(base/rel)==row['sha256'],rel
 for rel,alias in held.get('directoryAliases',{}).items():assert (base/rel).is_symlink() and str((base/rel).resolve())==alias
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() or n=='preflight.json']
 return [n for n in names if n=='__pycache__']
shutil.copytree(parent,root,ignore=ignore)
shutil.copy2(repo/'implementation/warlock-family-style-crop-capture-v19/native-build-report.json',root/'native-build-report.json')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Requalify current held GUI110 compiled legacy runtime on exact core16/plugin19 while retaining every original native129/128/126 fixed ordered control, actual allocator attempts/original expiry/deadlines/physical/resource/receipt/normal cleanup. Historical probes remain exact held inputs. New URI router/controlled factory/scoped-detachment activation remains inactive and unqualified by this legacy campaign. No installed changes.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
p=root/'qa/native.py';text=p.read_text();text=text.replace('Retain original GUI92/native128 campaign and fixed126 identities/deadlines/pixel/teardown oracles on exact core16/plugin19. Add real Core registry/scoped client capture/resource/SCM_RIGHTS/actual private lock and independent local FD metadata witnesses. GUI106 controlled factory/ownership fixes remain CPU-qualified and inactive; this campaign does not establish GUI106/WebKit protocol integration, ordinary capture eligibility or full release.', 'Current held GUI110 legacy runtime requalification on exact core16/plugin19 with unchanged original129/128/126 fixed ordered controls, actual allocator/expiry/pixel/deadline/cleanup and Core scoped resource/FD/lock witnesses. Historical probes remain exact prior source. New GUI110 URI router/controlled factory/scoped-detachment protocol remain inactive; no actual new callback registration/controlled Core/ordinary capture eligibility or full release acceptance.')
needle=" r['priorNative128Retention']=comparison128";assert text.count(needle)==1
text=text.replace(needle,needle+"\n prior129=json.loads(pathlib.Path(pre['retainedNative129Report']).read_text());comparison129=compare(prior129,r,stableNames)\n check('allPriorNative129FixedOrderedAndActualRetryAssertionsRetained',len(prior129['checks'])==2517 and comparison129['passed'],evidence=comparison129)\n r['priorNative129Retention']=comparison129\n r['currentGUI110LegacyRuntimeQualified']=True\n r['newURIRouterActivated']=False\n r['newControlledFactoryActivated']=False")
p.write_text(text)
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS ownNative130 current heldGUI110 legacy runtime on exact core16/plugin19; every original129/128/126 fixed control, actual allocator/expiry/deadline/resource/receipt/teardown remains. New URI router/controlled factory/scoped-detachment activation remains inactive; historical standalone probes retain original sources. Prepare exact preflight before serialized native launch; no installed/main desktop/draft changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
