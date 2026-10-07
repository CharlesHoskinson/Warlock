"""Own actual captured local FD/readers reconciliation without changing held105."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v105';target=repo/'implementation/warlock-preview-provider-v106'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=root/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and not target.exists()
for rel,row in d['files'].items():assert sha(root/rel)==row['sha256'],rel
plugin=repo/'implementation/warlock-family-style-crop-capture-v19/component-manifest.json';p=json.loads(plugin.read_text());assert p['sourceHeld'] and p['passed'] and not p['nativeAcceptance']
for rel,row in p['files'].items():assert sha(plugin.parent/rel)==row['sha256'],rel
for rel,alias in p['directoryAliases'].items():assert (plugin.parent/rel).is_symlink() and str((plugin.parent/rel).resolve())==alias
def ignore(path,names):
 base=pathlib.Path(path)
 if base==root:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if base==root/'qa':return [n for n in names if (base/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'elm-stuff','__pycache__'}]
shutil.copytree(root,target,ignore=ignore)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(m),'owningPluginComponentManifest':str(plugin),'owningPluginComponentManifestSHA256':sha(plugin),'purpose':'Actual authenticated capture FD transport into ImportedClients, sealed mapping/Broker adoption and scoped native resource reconciliation. Qualify real local FD/readers and post-transfer result allocation failure custody; backend zero alone cannot grant final physical proof. Preserve original request/clock/context/deadline, single acquisition and actual native control/receipt/incarnation barriers. Core16/plugin19 sources held and inactive; no installed changes.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS ownGUI106 actual scoped capture FD/mapping/readers/post-transfer exception recovery. Held105/plugin19 component477 C+35decoder/four variants;resource14/22/349/three;engine21/two export descriptors/three;original capture14/66/816/three;C10190/260/1041;full95 and exactcore16/plugin19 compile. Source commit1387ee79b973310c060e68e20b6e2ec2ac0d9aa8/public72 delivery currently in progress, verify before claiming. QualifiedGUI92/native128/core16/plugin18 and all original capture/native/full-release gates unchanged. No installed/main desktop/draft changes.'],'progress',[str(m.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo)),str(plugin.relative_to(repo))]))
