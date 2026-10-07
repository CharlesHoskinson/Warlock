"""Hold actual output observation; no physical concealment/reveal claim."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-client-provider-native-v137';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
reports=list(root.glob('qa/native-controlled-*/report.json'));assert len(reports)==1;report=reports[0];d=json.loads(report.read_text())
assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==26 and len(d['ownedExitCodes'])==12 and all(x['passed'] for x in d['checks']) and all(x['exitCode']==0 for x in d['ownedExitCodes'])
assert d['actualPrivateWaylandOutputObserved'] and d['actualCapturedPixelsQualified'] and not d['physicalConcealmentQualified'] and not d['physicalRevealQualified'] and not d['hardwarePresentationQualified'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
parent=repo/'implementation/warlock-client-provider-native-v136';m=parent/'component-manifest.json';held=json.loads(m.read_text());assert held['passed'] and held['sourceHeld']
for rel,row in held['files'].items():assert sha(parent/rel)==row['sha256'],rel
original=json.loads(pathlib.Path(held['reports']['controlledNative']['path']).read_text());assert {x['name'] for x in original['checks']}<={x['name'] for x in d['checks']}
pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in d['artifacts'].items():assert sha(report.parent/rel)==h,rel
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root);assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
scope='Actual unchanged GUI126 controlled pure-renderer pixels plus real private Wayland output observed while original native image/accepted resource/context stayed current before and after capture. All original21 image/admission/drain checks retained;26 checks/12 owned normal exits/private cleanup/original deadline6/core16/plugin19/AQ155. Original grim capture and independent PNG oracle produce800x600 output; actual snapshot shows the closed opacity curtain as a blank native popup. No reliable original popup-geometry/frame concealment oracle or negative control has yet been qualified. This observation does not establish physical concealment/reveal or hardware presentation. Original policy/native physical/journal/confirmation/strict close unchanged; all pressure/workload/RSS/recovery/full preview/release gates remain open.'
out=root/'component-manifest.json';assert not out.exists();result=dict(held);result.update(files=files,scope=scope,nativeChecks=26,normalOwnedExits=12,actualPrivateWaylandOutputObserved=True,actualPrivateWaylandOutputPixels=d['actualPrivateWaylandOutputPixels'],physicalConcealmentQualified=False,physicalRevealQualified=False,hardwarePresentationQualified=False,sourceHeld=True,passed=True,privateSessionCleanupPassed=True,reports={'build':held['reports']['build'],'controlledNative':{'path':str(report),'sha256':sha(report)}},parentManifest=str(m),parentManifestSHA256=sha(m));out.write_text(json.dumps(result,indent=2)+'\n')
summary=pathlib.Path(__file__).with_name('component-report137.json');assert not summary.exists();summary.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldNative137 unchangedGUI126 actual pure-renderer pixels plus original grim private Wayland output800x600 while original native image/accepted resource/context remains current before and after capture. Original21 checks retained;26checks12normalexits/privatecleanup/deadline6/core16/plugin19/AQ155. Actual output shows closed native opacity curtain blank popup, but popup geometry/frame oracle and negative control remain unqualified; no physical concealment/reveal/hardware claim. Next GUI127 original native popup geometry/GTK frame observation and independent bounded concealment oracle with original current pure image reference; prepare actual negative control before qualifying concealment. Policy/native physical/journal/confirmation/strict close unchanged; release/pressure/workload/RSS/recovery/full preview remain open. Installed/drafts/foreign preserved.'],'progress',[str(out.relative_to(repo)),str(summary.relative_to(repo)),str(report.relative_to(repo))]))
print('Held native output observation',len(files))
