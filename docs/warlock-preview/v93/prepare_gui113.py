"""Own distinct live-window preview realm detachment without window retirement."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v112';root=repo/'implementation/warlock-preview-provider-v113'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeRecoveryChecks']==129 and d['recoveryStates']==498 and d['fullBuildCommands']==98 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Typed Elm preview realm and distinct scoped detachment integration in the existing single PreviewPresenter policy. Native assigns all realm/job/entry/control identities. Exact incoming/outgoing realm wrappers reject old domains before reducer mutation. Scoped seed/readiness/completion/final-processing must retain lifecycle settlement and request-floor guards without fabricating permanent retirement or resetting the Native grant. Preserve existing permanent retirement and all resource/Unknown/deadline barriers. Actual controlled host/WebKit/Core activation separate.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS own freshGUI113 from held112. Implement typed native realm and distinct scoped detachment in single existing Elm preview policy; exact C seed/delivery shapes and settlement/request-floor matching before readiness, final processing or membership removal. Preserve permanent native retirement unchanged and original lifecycle Unknown/resource/ACK/deadline barriers. All realm/control IDs native-owned; no grant reset. GUI112 C129/model24/36/498/nineJS+threeNative/full98/fourresource+fourscoped held and PUBLIC81. Native130 current110 legacy2518/278/full cleanup bounded baseline. Actual host/WebKit/Core and full release gates remain open; no installed changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
