"""Project observed204 stages into the combined requirements model, not policy."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];repo=root.parents[1];sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
native=repo/'implementation/warlock-client-provider-native-v204';path=native/'qa/native-1791405433168520892/report.json';n=json.loads(path.read_text());pre=json.loads((native/'qa/preflight.json').read_text())
assert n['passed'] and n['cleanupPassed'] and n['combinedControlledPreviewRestartQualified'] and n['combinedKnownPreviewBeforeRestartQualified'] and n['historicalUnknownBeforeNewAction']['record']['status']=='Unknown'
for p,h in pre['inputs'].items():assert sha(p)==h,p
for p,h in n['artifacts'].items():assert sha(path.parent/p)==h,p
checks={c['name']:c for c in n['checks']};assert all(c['passed'] for c in n['checks'])
original=n['originalControlledPreview']['model'];pending=checks['combinedWindowPendingAndOriginalPreviewUnretiredAtFailure']['state']
retiring=pending['privatePolicy']['models'][0]['model']['retiring']
assert original['accepted']['job'] in [r['job'] for r in retiring]
assert pending['privatePolicy']['realm']['closing'] and not pending['privatePolicy']['realm']['closed']
closed=n['originalControlledPreviewStrictClose'];assert closed['privatePolicy']['realm']['closed'] and not closed['privatePolicy']['models'] and closed['nativeEffectError']==''
assert n['operation']=='minimize' and n['faultBoundary']=='lost' and n['operationFaultMarker']['outcome']['status']=='Committed'
first=path.parent/'native-evidence/generation-1.log';second=path.parent/'native-evidence/generation-2.log';text=first.read_text()
markers=['controlled-native-reader-held:','controlled-native-reader-probed:','Web process terminated:','controlled-native-reader-released:','controlled-native-realm-retired:','native-recovery-ready:','recovery-restart-requested']
positions=[text.index(m) for m in markers];assert positions==sorted(positions)
assert n['recovery']['freshBinding']!=n['recovery']['oldBinding'] and n['recovery']['freshBinding']['lifetime']==n['recovery']['oldBinding']['lifetime']
assert n['freshControlledPreview']['model']['scope']['binding']!=original['scope']['binding'] and n['freshControlledPreview']['model']['scope']['clock']==original['scope']['clock']
inputs={str(p):sha(p) for p in [path,native/'qa/preflight.json',first,second,root/'spec/combined_recovery.qnt',pathlib.Path(__file__)]}
model=next(root.glob('qa/model-*/report.json'));m=json.loads(model.read_text());assert m['passed'] and m['namedScenarios']==14 and m['invariantSamples']==200;inputs[str(model)]=sha(model)
out=root/'qa'/('coupled-'+str(time.time_ns()));out.mkdir(mode=0o700);(out/'inputs').mkdir(mode=0o700);shutil.copy2(root/'spec/combined_recovery.qnt',out/'inputs/combined_recovery.qnt')
closing=['ClosePreview'];pending_events=closing+['AdmitWindow','NativeWindowCommit'];unknown=pending_events+['LoseReceipt'];failed=unknown+['RendererFailure'];reader=failed+['CloseReader'];strict=reader+['NativeStrictClose'];recovered=strict+['Recovery'];restarted=recovered+['Restart'];scene=restarted+['Scene'];history=scene+['WindowBindingRetired','ReleaseReservation'];explicit=history+['ExplicitNewCommand'];fresh=explicit+['FreshCapture'];final=fresh+['CloseFreshReader','FreshStrictClose']
cases=[
 ('actualCapturedReader',[],'s.reader and not(s.admitted)','combinedPreviewKnownActualNativeCustody-1'),
 ('actualClosingReader',closing,'s.reader and s.closing and not(s.closed)','combinedActualReaderBlocksRetirementBeforeCommand-1'),
 ('actualPendingNativeCommit',pending_events,'s.admitted and s.nativeWindowCommitted and not(s.oldUnknown)','actualNativeCommitPrecedesLostMinimizeOrRestoreReceipt'),
 ('actualWindowUnknown',unknown,'s.oldUnknown and s.historyUnknown and s.reader','lostBrokerReceiptShowsUnknownInExistingUI'),
 ('actualRendererFailureBlockedRecovery',failed,'s.rendererFailed and s.reader and not(s.recovery)','combinedRendererDeathCannotSettleHeldNativeReader'),
 ('actualReaderClose',reader,'not(s.reader or s.closed)','combinedNativeReaderAndStrictClosePrecedeGTKRecovery'),
 ('actualStrictNativeClose',strict,'s.closed and s.oldUnknown and not(s.recovery)','combinedOriginalStrictNativeAndHostCustodyClose-1'),
 ('actualGTKRecovery',recovered,'s.recovery and s.closed and s.oldUnknown','combinedNativeReaderAndStrictClosePrecedeGTKRecovery'),
 ('actualExplicitRestart',restarted,'s.host==2 and s.lifetime==1 and s.oldUnknown','nativeRestartButtonEmitsExplicitRestartExit'),
 ('actualFreshCoherentUnknown',scene,'s.scene and s.oldUnknown and s.replays==0','freshCoherentSnapshotPrecedesNewEffects'),
 ('actualHistoricalUnknownAfterRetirement',history,'s.reservationReleased and s.historyUnknown and s.oldUnknown','durableReservationReleasePreservesExactHistoricalUnknown'),
 ('actualExplicitAdvancedCommand',explicit,'s.newCommand and s.request==2 and s.generation==2 and s.historyUnknown','freshExplicitActionUsesCurrentStateAndAdvancedIdentity'),
 ('actualFreshOwnNativeCapture',fresh,'s.freshPreview and s.freshOwner==2 and s.lifetime==1 and s.historyUnknown','combinedFreshHostPreviewUsesNewNativeOwnerSameCompositor'),
 ('actualFreshNativeClosePreservesHistory',final,'s.freshClosed and not(s.freshReader) and s.historyUnknown','combinedFreshPreviewNativeClosePreservesHistoricalWindowUnknown')]
for _,_,_,name in cases:assert checks[name]['passed'],name
runs=[' run '+name+'=init'+''.join('.then(fire('+event+'))' for event in events)+'.then(check('+condition+'))' for name,events,condition,_ in cases]
(out/'inputs/concrete_combined.qnt').write_text('module concrete_combined {\n import combined_recovery.* from "./combined_recovery"\n action check(ok:bool):bool=all{assert(ok and safety),s\'=s}\n'+'\n'.join(runs)+'\n}\n')
tool=pathlib.Path(m['quint']['path']);assert sha(tool)==m['quint']['sha256']
report={'passed':False,'inputs':inputs,'quint':m['quint'],'commands':[],'observations':[{'name':name,'events':events,'condition':condition,'nativeCheck':origin} for name,events,condition,origin in cases],'originalRetiringJobUnchanged':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewUncertaintyNativeQualified':False,'scope':'Fourteen abstract stages projected from actual qualified204 known-preview/uncertain-window-command combined scenario. Original immutable job/deadline persists in actual retiring custody; native strict close is an independently checked Bootstrap/driver/physical/journal/ticket/confirmation proof, not inferred from renderer death or reader close. GIO close before strict close before GTK recovery; actual native Restart/fresh binding/same lifetime, original normalized Unknown/no replay/retirement history/advanced explicit command, fresh own-native capture and strict close. This is bounded stage projection, not full callback/step refinement, actual preview-effect uncertainty, hardware/physical reveal or full native13/release qualification.'}
try:
 for name,args in [('typecheck',[str(tool),'typecheck','concrete_combined.qnt']),('selected',[str(tool),'test','concrete_combined.qnt','--main=concrete_combined','--backend=typescript','--match=^('+'|'.join(c[0] for c in cases)+')$','--seed=2040049','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stdout+p.stderr
 assert len(list(out.glob('coupled-*.itf.json')))==14 and all(sha(p)==h for p,h in inputs.items());report.update(passed=True,coupledStages=14)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
