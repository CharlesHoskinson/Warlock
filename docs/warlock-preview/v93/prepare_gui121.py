"""Own bounded native returned-output custody before actual controlled GUI use."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v120';root=repo/'implementation/warlock-preview-provider-v121';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativePolicyDriverCPUQualified'] and d['fullBuildCommands']==116 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
native=pathlib.Path(d['nativeBaselineManifest']);assert sha(native)==d['nativeBaselineManifestSHA256'];n=json.loads(native.read_text());assert n['sourceHeld'] and n['passed'] and n['nativeChecks']==2518 and n['normalOwnedExits']==278
for rel,row in n['files'].items():assert sha(native.parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [name for name in names if name in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [name for name in names if (pathlib.Path(path)/name).is_dir() and name!='toolchain']
 return [name for name in names if name in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'nativeBaselineManifest':str(native),'nativeBaselineManifestSHA256':sha(native),'purpose':'Qualify bounded original native returned-output custody and paused producer scheduling before actual controlled host/pure renderer activation. Audit original dispatch output paths, reserve output storage before native effects, preserve original returned events/tickets/receipts, drain admitted native outputs before accepting more ordinary policy work where backpressure permits. Keep original single Elm policy/native issuance/effects/physical/deadline authorities and all host/WebKit/frame/concealment/URI/recovery gates.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
(root/'OUTPUT-CUSTODY-NEXT.md').write_text('''# Returned native output custody

GUI120 is held/public CPU driver evidence. This derivative owns the next code
change: a bound and progress qualification for retained original native dispatch
results, plus paused producer scheduling before actual controlled GUI use.

Source audit found that original dispatch emits at most two frame events for
Acquire; reconcile, physical Cancel/Release and terminal acknowledgment emit no
events. Native retire/detach and final-delivery acknowledgment return at most one
original completion. Both journals return only their next completion. They do
not return their whole actor inventory. Preserve those original sources.

Next verify closed output field/byte bounds on original serializers and maximum
UInt64/token shapes, reserve capacity before dispatch, retain every returned byte
before acknowledging transport, and prioritize processing admitted results where
the original deferred-input gate permits. Model pressure with original ingress
1065 plus deferred ordinary/quarantine bounds, and couple it to actual C/JSC.
Do not infer progress or resource acceptance from the prior single-subject trace.

Actual controlled host/pure renderer WebKit context, one-time native initialization,
original GTK admission, async DOM/frame, physical concealment and URI remain next.
Live uncertain/process-loss recovery and original delayed never-issued proposal
expiry/revocation outcomes remain separate. Native131 legacy2518/278 remains the
actual current Core16/plugin19/AQ155 baseline; full GUI release is open.
''')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,d['owner'],str(root.relative_to(repo)),['PROGRESS ownGUI121 after held/publicGUI1202250+constructor9/Quint14/200/six concrete witnesses/four guards/full116. Next bound original native returned-output custody and paused producer schedule before actual controlled host/pure renderer. Original C dispatch audit: Acquire returns two frame events; cancel/release/reconcile/terminal ACK return none; original native retire/detach/final ACK return at most next one completion, not whole inventory. Verify byte/field bounds, reserve capacity before effects, retain exact outcomes before outbox receipt, prioritize admitted outputs under original deferred policy gate; qualify pressure/progress without changing original authorities/deadlines. Native131 current actual legacy2518/278 stays. Actual WebKit context/GTK admission/async frame/physical concealment/URI, uncertain live/process recovery, delayed proposal outcomes and full release remain open; no installed/foreign changes.'],'progress',[str(m.relative_to(repo)),str(native.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo)),str((root/'OUTPUT-CUSTODY-NEXT.md').relative_to(repo))]))
