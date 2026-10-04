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
# Separate typed observation fixture for per-family independence; NOT a captured native trajectory.
first=[x for _,x in backend][:6]
assert [x['kind'] for x in first]==['attached','host-recovery-watermarks','host-geometry-negotiate','action-projection','geometry-attached','geometry-facts']
def additional(name,inputs):
 path=OUT/(name+'-events.json');path.write_text(json.dumps(inputs,indent=2)+'\n')
 command=['node',str(ROOT/'qa/probe.cjs'),str(OUT/'worker.js'),str(path),str(OUT/(name+'-rows.json'))]
 p=subprocess.run(command,capture_output=True,timeout=30);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);commands.append({'command':command,'exitCode':p.returncode});assert p.returncode==0
 return json.loads((OUT/(name+'-rows.json')).read_text())
ordinary=additional('ordinary',[{'kind':'native','frame':f} for f in first])[-1]
check('ordinaryNoRecoveryControls',not ordinary['blocked'] and ordinary['unresolved']==0 and not any('recovery-refresh' in c['id'] for c in ordinary['frame']['bar']+ordinary['frame']['popup']))
check('ordinaryApplicationAndGroupPreserved',len(ordinary['frame']['bar'])==2 and all(c['enabled'] for c in ordinary['frame']['bar']))
# Clone an actual observed window record into a DECLARED pure observation fixture.
# Exact captured frames remain unmodified in captured-frames.json and core witness.
fixture=json.loads(json.dumps(events[:-6]))
window=next(w for w in first[3]['scene']['windows'] if w['incarnation']=='1')
projection=next(e['frame'] for e in fixture if e.get('kind')=='native' and e['frame']['kind']=='action-projection')
projection['scene']['windows'].append(window)
fixture += [{'kind':'activate-current'},{'kind':'family-one'}]
independent=additional('declared-independent-observation-fixture',fixture)
picker=independent[-2];member1=next(c for c in picker['frame']['popup'] if c['id']=='family:1');member2=next(c for c in picker['frame']['popup'] if c['id']=='family:2')
check('perTargetPickerIndependence',member1['enabled'] and not member2['enabled'] and picker['blocked'])
check('independentSelectionRequestsCurrentObservations',independent[-1]['choiceRoot']=='1' and independent[-1]['blocked'] and independent[-1]['effectRequest']=='12' and {w.get('kind') for w in independent[-1]['wires']}=={'projection-request','geometry-facts-request'})
# Align actual native admitted control publication with compiled SurfaceRenderer output.
packet=before['frame'];(OUT/'publication.json').write_text(json.dumps(packet)+'\n')
flags=subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True).split()
command=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(ROOT/'native/recovery-presentation-test.c'),'-o',str(OUT/'native-recovery-test'),*flags]
p=subprocess.run(command,capture_output=True,timeout=60);commands.append({'command':command,'exitCode':p.returncode});(OUT/'recovery-build.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()
command=[str(OUT/'native-recovery-test'),str(OUT/'publication.json')];p=subprocess.run(command,capture_output=True,timeout=30);commands.append({'command':command,'exitCode':p.returncode});(OUT/'native-recovery.stdout').write_bytes(p.stdout);assert p.returncode==0,p.stdout.decode()
native=json.loads(p.stdout);check('nativeAdmissionAgrees',all(native.values()))
for size in [259,260,261]:
 bounded=json.loads(json.dumps(packet));bounded['bar']=[{'id':'fixture-'+str(i),'domId':'fixture-'+str(i),'label':'Fixture','ariaLabel':'Fixture','detail':'','enabled':True} for i in range(size)]
 decoded=additional('elm-bar-capacity-'+str(size),[{'kind':'validate','frame':bounded}])[-1]
 check('elmBarCapacity'+str(size),decoded['rendererValid']==(size==259))
report={'passed':True,'nativeAcceptance':False,'scope':'Changed Surface pure recovery presentation on public GUI567 reducers: affected mutation disabled, observation refresh admitted, Unknown preserved. No authority semantics changed.','checks':checks,'commands':commands,'capturedLogSHA256':sha(LOG),'sourceFiles':{str(p.relative_to(SOURCE)):sha(p) for p in (SOURCE/'src').glob('*.elm')},'limitations':['No native launches or actual keyboard/AT/IME acceptance.','Independent-family test is an explicitly declared typed observation fixture, not captured native facts.','Bar-control bound is explicitly amended from257 to259 in both decoders; original257 evidence remains historical.','Not a full native timeline replay:90 public observation-only Refresh inputs align captured projection request91.','Compiled publication numbers differ from native123/124; exact native published frames retained separately.','Captured final scene has one target family; no fabricated second-family independent-target claim.','No reservation-release implementation or native authority revocation certificate is produced.'],'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'checks':len(checks)}))
