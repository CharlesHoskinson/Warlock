#!/usr/bin/env python3
import hashlib,json,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parents[1]
SOURCE=ROOT
LOG=REPO/'implementation/elm-pending-observation-recovery-trace-v573/qa/native-1791143276230101221/native-evidence/elm-webview.log'
OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lines=LOG.read_text().splitlines();backend=[(i,json.loads(l.split(': ',1)[1])) for i,l in enumerate(lines) if l.startswith('backend-frame: ')]
start=[i for i,x in backend if x.get('kind')=='attached'][-1]
captured=[{'line':i+1,'rawLine':lines[i],'frame':x} for i,x in backend if i>=start]
assert [x['frame']['kind'] for x in captured]==['attached','host-recovery-watermarks','host-uncertain','host-geometry-negotiate','action-projection','geometry-attached','geometry-facts']
(OUT/'captured-frames.json').write_text(json.dumps(captured,indent=2)+'\n')
shutil.copy2(LOG,OUT/'captured573.log')
# Only public observation inputs align request91. Captured native frames are never rewritten.
events=[{'kind':'native','frame':x['frame']} for x in captured[:3]]
events += [{'kind':'refresh','provenance':'harness public observation request, not captured native frame'} for _ in range(90)]
events += [{'kind':'native','frame':x['frame']} for x in captured[3:]]
events += [{'kind':'checkpoint'},{'kind':'activate-current'},{'kind':'retry-observation'},{'kind':'recovery-control'},{'kind':'activate-current'},{'kind':'applications'}]
(OUT/'events.json').write_text(json.dumps(events,indent=2)+'\n')
inputs=OUT/'inputs';shutil.copytree(SOURCE/'src',inputs/'src');shutil.copy2(SOURCE/'elm.json',inputs/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',inputs/'src/Probe.elm')
commands=[]
for name,command,cwd in [('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--output='+str(OUT/'worker.js')],inputs),('probe',['node',str(ROOT/'qa/probe.cjs'),str(OUT/'worker.js'),str(OUT/'events.json'),str(OUT/'rows-raw.json')],ROOT)]:
 p=subprocess.run(command,cwd=cwd,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);commands.append({'command':command,'cwd':str(cwd),'exitCode':p.returncode});assert p.returncode==0,p.stderr.decode()[-2000:]
rows=json.loads((OUT/'rows-raw.json').read_text());(OUT/'rows.json').write_text(json.dumps(rows,indent=2)+'\n')
before,first,guarded,refresh,second,apps=rows[-6:]
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
check('capturedFrameBytesPreserved',all(x['rawLine']==lines[x['line']-1] for x in captured))
check('capturedProjectionAdmitted',before['phase']=='Ready' and before['blocked'] and before['unresolved']==1)
control=next(c for c in before['frame']['bar'] if c['id']=='bar:group:application:GTK Application')
check('unknownTargetMutationDisabled',not control['enabled'] and 'awaiting native confirmation' in control['ariaLabel'])
check('explicitVisibleRecoveryReason','does not retry' in before['frame']['status'])
check('publishedRecoveryControlEnabled',next(c for c in before['frame']['bar'] if c['id']=='bar:recovery-refresh')['enabled'])
check('disabledRendererActionNotAdmitted',first['frame']==before['frame'] and not first['wires'])
check('noReplayCounterConsumption',all(r['effectRequest']=='12' and r['effectGeneration']=='12' for r in [before,first,refresh,second,apps]))
check('noMutationWiresInEntireHarness',all(w.get('kind')!='window-effect' for r in rows for w in r['wires']))
check('existingRetryWindowsDoesNotExposeRecovery',guarded['blocked'] and not guarded['wires'])
check('observationRefreshKeepsReservation',refresh['blocked'] and refresh['unresolved']==1 and any(w.get('kind')=='projection-request' for w in refresh['wires']))
check('repeatActionStillCannotMutate',second['blocked'] and not second['wires'])
check('independentApplicationsControlEnabled',next(c for c in before['frame']['bar'] if c['id']=='bar:applications')['enabled'])
check('publicApplicationsActionReachable',apps['frame']['mode']=='applications' and apps['blocked'] and any(w.get('kind')=='catalog-request' for w in apps['wires']))
report={'passed':True,'nativeAcceptance':False,'scope':'Changed Surface pure recovery presentation on public GUI567 reducers: affected mutation disabled, observation refresh admitted, Unknown preserved. No authority semantics changed.','checks':checks,'commands':commands,'capturedLogSHA256':sha(LOG),'sourceFiles':{str(p.relative_to(SOURCE)):sha(p) for p in (SOURCE/'src').glob('*.elm')},'limitations':['No native launches or actual keyboard/AT/IME acceptance.','Not a full native timeline replay:90 public observation-only Refresh inputs align captured projection request91.','Compiled publication numbers differ from native123/124; exact native published frames retained separately.','Captured final scene has one target family; no fabricated second-family independent-target claim.','No reservation-release implementation or native authority revocation certificate is produced.'],'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'checks':len(checks)}))
