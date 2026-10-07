"""Hold intentional unsafe source/failure and qualify only the bounded detector."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=repo/'implementation/warlock-preview-provider-v128';native=repo/'implementation/warlock-client-provider-native-v139';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
reports=list(native.glob('qa/native-controlled-*/report.json'));assert len(reports)==1;report=reports[0];d=json.loads(report.read_text())
assert not d['passed'] and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
bad=[x for x in d['checks'] if not x['passed']];assert len(bad)==1 and bad[0]['name']=='controlledNativeClosedCurtainRegionExcludesCurrentPreview'
assert bad[0]['pixels']['red']==19200 and bad[0]['observation']['opacity']==1 and d['actualClosedCurtainRegionPixels']['red']==19200
assert any(x['name']=='controlled-host' and x['exitCode']==1 for x in d['ownedExitCodes']) and all(x['exitCode']==0 for x in d['ownedExitCodes'] if x['name']!='controlled-host')
assert not any(x['name']=='controlledFullHostNormalExit' for x in d['checks'])
positive=repo/'implementation/warlock-preview-provider-v127';positive_native=repo/'implementation/warlock-client-provider-native-v138';manifests=[]
for root in [positive,positive_native]:
 m=root/'component-manifest.json';held=json.loads(m.read_text());assert held['passed'] and held['sourceHeld']
 for rel,row in held['files'].items():assert sha(root/rel)==row['sha256'],rel
 manifests.append({'path':str(m),'sha256':sha(m)})
good=json.loads(pathlib.Path(held['reports']['controlledNative']['path']).read_text());assert good['passed'] and len(good['checks'])==29 and len(good['ownedExitCodes'])==13 and good['actualClosedCurtainRegionPixels']['red']==0 and good['actualNativeGTKPaintObservation']['opacity']==0 and d['pair']==good['pair']
assert sha(native/'qa/native-controlled-host.py')==sha(positive_native/'qa/native-controlled-host.py')
changes=[]
for base in ['src','native','assets','adapter']:
 for p in (positive/base).glob('*'):
  if p.is_file() and sha(p)!=sha(gui/base/p.name):changes.append(str(p.relative_to(positive)))
assert changes==['native/controlled-preview-host.h']
old=(positive/'native/controlled-preview-host.h').read_text();new=(gui/'native/controlled-preview-host.h').read_text();a=old.index('static void controlled_curtain(void)');b=old.index('static void controlled_fault',a);c=new.index('static void controlled_curtain(void)');e=new.index('static void controlled_fault',c);assert old[:a]==new[:c] and old[b:]==new[e:] and 'gtk_widget_set_opacity(GTK_WIDGET(popup_view),1.0)' in new[c:e]
pre=json.loads((native/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in d['artifacts'].items():assert sha(report.parent/rel)==h,rel
build=pathlib.Path(pre['controlledHostBuild']);b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==119 and all(x['exitCode']==0 for x in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
scope='Intentional unsafe QA-only variant changes only the controlled native curtain setter0to1. Unchanged actual Native138 oracle detects19200 exposed preview pixels and native opacity1 in the original current popup region, after original pure-renderer image/output/context checks. Original scenario deadline6/core16/plugin19/AQ155 unchanged. The original assertion fails; no normal host close is claimed. Host exits1 with original strict close refusal, all other owned exits normal/private cleanup. Full119 passes. This source is never an accepted production/default/installed candidate. Detector evidence qualifies only the corresponding held positive GUI127/Native138 bounded closed-curtain region; no ongoing transition concealment, physical reveal, hardware, stale callback/recovery or full release acceptance.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'intentionalUnsafeNegativeControl':True,'boundedCurtainDetectorQualified':True,'cpuBuildPassed':True,'fullBuildCommands':119,'failedNativeReport':str(report),'failedNativeReportSHA256':sha(report),'privateSessionCleanupPassed':True,'normalControlledHostClosureQualified':False,'normalCloseClaimed':False,'actualExposedPreviewPixels':19200,'actualOpacity':1,'originalNativeOracleUnchanged':True,'originalNativePolicyIssuerPhysicalProductUnchanged':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'positiveManifests':manifests}
for root in [gui,native]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 out=root/'component-manifest.json';assert not out.exists();out.write_text(json.dumps(dict(common,files=files),indent=2)+'\n');print(root.name,len(files))
qualification=dict(common,passed=True,boundedClosedCurtainRegionQualified=True,unsafeVariantAccepted=False,positiveNativeChecks=29,positiveNormalOwnedExits=13,positiveSamples=248976,negativeExposedPixels=19200,physicalConcealmentQualified=False,physicalRevealQualified=False,hardwarePresentationQualified=False,actualStalePaintCallbackQualified=False)
out=pathlib.Path(__file__).with_name('component-curtain-control-report.json');assert not out.exists();out.write_text(json.dumps(qualification,indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';s=task.read_text();s+='\n- [x] Freeze bounded CONTROL-038 native popup/GTK paint/current geometry observation\n  and actual output-region concealment detector: GUI127/Native138 positive29/13\n  plus actual unsafe GUI128/Native139 rejected by the unchanged native oracle.\n  Stale callbacks, ongoing transitions, physical reveal/hardware and recovery/full\n  release remain open; the unsafe variant is retained failure evidence only.\n';task.write_text(s)
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,common['owner'],str(positive.relative_to(repo)),['PROGRESS bounded actual closed-curtain region detector qualified: held positiveGUI127/Native13829checks13normalexits, original source reference19200red/current native URI and private output248976opaque region samples zero previewcolors; intentional unsafeGUI128/Native139 opacity1 yields19200 real previewpixels and unchanged original native oracle rejects. Expected failure/host1/strict close refusal/privatecleanup/other normal exits retained; full119/originaldeadline6/core16/plugin19/AQ155 unchanged. Only native curtain helper changed, original runner byte-identical; no policy/issuer/physical/journal/confirmation changes or grant reset. GTK after-paint is not compositor/hardware proof; bounded region does not qualify ongoing transitions/reveal/stale callbacks/recovery/full release. Next PUBLIC94 then safe positive lineage actual async stale callback/physical frame/reveal and pressure/workload qualification. Unsafe variant never installed/default accepted; installed/drafts/foreign preserved.'],'progress',[str((gui/'component-manifest.json').relative_to(repo)),str((native/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
