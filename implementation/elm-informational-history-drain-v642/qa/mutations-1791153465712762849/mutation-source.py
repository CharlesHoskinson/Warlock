import hashlib,json,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir()
PRIMARY=max((ROOT/'qa').glob('tests-*/report.json'),key=lambda p:p.parent.name).parent
mutants=[
 ('release-keeps-live','Effects.elm','{model | unresolved=List.filter (\\t -> not (t.status==Unknown && t.effectProtocol==protocolId && t.intent==intent)) model.unresolved}','model','valid'),
 ('invented-committed','Effects.elm','{model | unresolved=List.filter','{model | transaction=Maybe.map (\\t -> {t|status=Committed}) model.transaction,unresolved=List.filter','valid'),
 ('announced-proof-changed','ReconciliationTracking.elm','accepted.proof/=proof','False','changed-proof-sequence'),
 ('geometry-own-context-unchecked','ReconciliationFrame.elm','observation.geometryContext==expected.geometryContext','True','stale-own-geometry-revision'),
 ('legacy-origin-released','ReconciliationTracking.elm','List.any (\\entry -> entry.intent==record.intent && entry.protocol==record.effectProtocol) model.legacy','False','legacy-origin'),
 ('menu-reservation-left-live','MenuBridge.elm','if accepted then Model {state|menu=menu,router=ReceiptRouter.forgetReservation local state.router} else model','model','menu-release'),
 ('ack-after-reads','SurfaceController.elm','readyEffects++effects','effects++readyEffects','valid'),
 ('shared-origin-unblocked','Shell.elm','if preserveShared then model.effects else Effects.releaseUnknown protocolId intent model.effects','Effects.releaseUnknown protocolId intent model.effects','full-origin-collision'),
 ('cross-domain-equality','ReconciliationTracking.elm','if accepted.proof/=proof then','if accepted.proof/=proof || proof.sequence/=action.context.revision then','valid')]
mutants += [
 ('requested-erases-accepted','ReconciliationTracking.elm','then {slot|actionRequest=Just request}','then {slot|actionRequest=Just request,action=Nothing}','dirty-final-geometry'),
 ('ui-phase-hides-accepted','ReconciliationTracking.elm','after.expected/=Just request && actionContext','after.expected/=Just request && after.phase==Shell.Ready && actionContext','dirty-final-action'),
 ('new-request-invalidates-release','ReconciliationTracking.elm','R.decodeReleased {currentBinding=current','if slot.actionRequest/=Just action.request || slot.geometryRequest/=Just geometry.request then Err "Superseded observation" else R.decodeReleased {currentBinding=current','dirty-final-geometry'),
 ('accepted-new-action-ignored','ReconciliationTracking.elm','if actionAccepted && slot.actionRequest==Just request then','if actionAccepted && slot.actionRequest==Just request && slot.action==Nothing then','actual-new-action-obsoletes-pair')]
reports=[]
for name,filename,old,new,scenario in mutants:
 dest=OUT/name;shutil.copytree(ROOT/'src',dest/'src');shutil.copy2(ROOT/'elm.json',dest/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',dest/'src/Probe.elm')
 p=dest/'src'/filename;text=p.read_text();assert text.count(old)==1,(name,text.count(old));p.write_text(text.replace(old,new))
 events=PRIMARY/(scenario+'-events.json');shutil.copy2(events,dest/'events.json');commands=[]
 for label,cmd in [('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--optimize','--output='+str(dest/'worker.js')]),('probe',['node',str(ROOT/'qa/probe.cjs'),str(dest/'worker.js'),str(dest/'events.json'),str(dest/'rows.json')])]:
  result=subprocess.run(cmd,cwd=dest,capture_output=True,timeout=180);(dest/(label+'.stdout')).write_bytes(result.stdout);(dest/(label+'.stderr')).write_bytes(result.stderr);commands.append({'command':cmd,'cwd':str(dest),'exitCode':result.returncode});assert result.returncode==0,result.stderr.decode()
 rows=json.loads((dest/'rows.json').read_text())
 if scenario=='valid':
  after=rows[-3];detected=after['blocked'] or after['transaction']['transaction']['status']!='Unknown' or [w['kind'] for w in rows[6]['wires']]!=['reconciliation-ready','projection-request','geometry-facts-request']
 elif scenario in ['dirty-final-geometry','dirty-final-action']:detected=rows[-1]['blocked'] or rows[-1]['transaction']['transaction']['status']!='Unknown'
 elif scenario=='menu-release':detected=rows[-2]['outstanding']!=0 or rows[-2]['registry']!=0 or rows[-2]['historicalUnknownMenus']!=1
 else:detected=not rows[-1]['blocked']
 report={'name':name,'detected':detected,'scenario':scenario,'commands':commands,'mutatedSourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'counterexample':{'events':'events.json','rows':'rows.json','expected':'valid release keeps historical Unknown, clears exact live/menu only, ready ack precedes requested reads; rejected release remains blocked'}}
 (dest/'report.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(report);print(name,detected,flush=True)
report={'passed':all(r['detected'] for r in reports),'controls':reports,'nativeAcceptance':False,'primaryReport':str(PRIMARY/'report.json')}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(ROOT/'qa/mutations.py',OUT/'mutation-source.py');print(json.dumps({'passed':report['passed'],'controls':len(reports),'report':str(OUT/'report.json')}));raise SystemExit(not report['passed'])
