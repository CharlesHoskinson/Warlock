import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-stable-surface-publication-v521';OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'scope':'Actual compiled current521 controller with verbatim225 native observations and public primary/choice events; no new native stimulus acceptance','checks':[]}
try:
 witness=REPO/'implementation/elm-picker-joint-observation-v226/witness.json';w=json.loads(witness.read_text());log=Path(w['nativeLog']);assert sha(log)==w['nativeLogSHA256']
 frames=[json.loads(line.removeprefix('backend-frame: ')) for line in log.read_text().splitlines() if line.startswith('backend-frame: ')]
 assert [f['kind'] for f in frames[:6]]==['attached','host-recovery-watermarks','host-geometry-negotiate','action-projection','geometry-attached','geometry-facts']
 events=[{'kind':'native','frame':f} for f in frames[:6]]+[{'kind':'primary'},{'kind':'choose','root':'2'}]+[{'kind':'native','frame':f} for f in frames[6:]]+[{'kind':'deadline'}]
 path=OUT/'captured-events.json';path.write_text(json.dumps(events,indent=2)+'\n')
 inputs=OUT/'inputs';shutil.copytree(SOURCE/'src',inputs/'src');shutil.copy2(SOURCE/'elm.json',inputs/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',inputs/'src/Probe.elm')
 worker=OUT/'worker.js';p=subprocess.run(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--output='+str(worker)],cwd=inputs,capture_output=True,timeout=180);(OUT/'compile.stdout').write_bytes(p.stdout);(OUT/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-2500:]
 runner=OUT/'probe.cjs';runner.write_text("const app=require(process.argv[2]).Elm.Probe.init({flags:null});app.ports.outgoing.subscribe(x=>{console.log(JSON.stringify(x));process.exit(0)});app.ports.incoming.send(JSON.parse(require('fs').readFileSync(process.argv[3],'utf8')));setTimeout(()=>process.exit(2),3000);")
 p=subprocess.run(['node',str(runner),str(worker),str(path)],capture_output=True,text=True,timeout=10);(OUT/'replay.stdout').write_text(p.stdout);(OUT/'replay.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
 rows=json.loads(p.stdout);(OUT/'rows.json').write_text(json.dumps(rows,indent=2)+'\n');assert len(rows)==len(events)
 def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
 check('capturedBootstrapAvailable',rows[5]['available'])
 check('confirmedNativePrimaryRepresentedByActualPublicEvent',rows[6]['picker'])
 check('confirmedNativeChoiceCreatesOriginalRequestPair',rows[7]['pendingChoice'] and [r['kind'] for r in rows[7]['requests']]==['projection-request','geometry-facts-request'] and [r['requestId'] for r in rows[7]['requests']]==['4','5'])
 check('originalRequestPairAndSupersedingPairSeen',[(r['frame']['kind'],r['frame'].get('requestId')) for r in events if r['kind']=='native' and r['frame']['kind'] in ['action-projection','geometry-facts']]==[('action-projection','1'),('geometry-facts','3'),('action-projection','4'),('geometry-facts','5'),('action-projection','6'),('geometry-facts','7')])
 check('geometryLastLeavesAvailablePendingChoice',rows[-2]['available'] and rows[-2]['pendingChoice'] and rows[-2]['geometryRequest']=='7')
 check('capturedOrderNeverIssuesActivation',not any(w['kind']=='window-effect' for r in rows for w in r['requests']))
 check('originalTimerRetiresUnconsumedChoice',not rows[-1]['pendingChoice'] and 'took too long' in rows[-1]['choiceNotice'])
 report.update(passed=True,capturedLog=str(log),capturedLogSHA256=sha(log),inputs={str(p):sha(p) for p in [Path(__file__),ROOT/'qa/Probe.elm',witness,*sorted((SOURCE/'src').glob('*.elm')),SOURCE/'elm.json']})
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
