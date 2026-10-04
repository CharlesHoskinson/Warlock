import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
log=REPO/'implementation/elm-surface-publication-trace-native-v533/qa/native-1791139524997273985/native-evidence/elm-webview.log'
frames=[json.loads(line.removeprefix('backend-frame: ')) for line in log.read_text().splitlines() if line.startswith('backend-frame: ')][:6]
assert [f['kind'] for f in frames]==['attached','host-recovery-watermarks','host-geometry-negotiate','action-projection','geometry-attached','geometry-facts']
(OUT/'captured-frames.json').write_text(json.dumps(frames,indent=2)+'\n')
(OUT/'probe.cjs').write_text("const app=require(process.argv[2]).Elm.Probe.init({flags:null});app.ports.outgoing.subscribe(x=>{console.log(JSON.stringify(x));process.exit(0)});app.ports.incoming.send(JSON.parse(require('fs').readFileSync(process.argv[3],'utf8')));setTimeout(()=>process.exit(2),3000);")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'pointerRaceCausallyResolved':False,'capturedLog':str(log),'capturedLogSHA256':sha(log),'scope':'Actual compiled opaque Elm controllers, identical captured backend observations, synthetic public owner transition; no live input acceptance','checks':[]}
try:
 for number,expected in [(507,1),(521,0)]:
  source=next((REPO/'implementation').glob('*v'+str(number)));inputs=OUT/str(number)/'inputs';shutil.copytree(source/'src',inputs/'src');shutil.copy2(source/'elm.json',inputs/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',inputs/'src/Probe.elm')
  worker=inputs.parent/'worker.js';p=subprocess.run(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--output='+str(worker)],cwd=inputs,capture_output=True,timeout=180);(inputs.parent/'compile.stdout').write_bytes(p.stdout);(inputs.parent/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-2000:]
  p=subprocess.run(['node',str(OUT/'probe.cjs'),str(worker),str(OUT/'captured-frames.json')],capture_output=True,text=True,timeout=10);(inputs.parent/'result.stdout').write_text(p.stdout);(inputs.parent/'result.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
  witness=json.loads(p.stdout);(inputs.parent/'witness.json').write_text(json.dumps(witness,indent=2)+'\n');assert witness['sameSurface'] and witness['stateChanged'] and witness['ownerCorrect'] and witness['publishes']==expected and witness['otherEffects']==0,witness
  controls=witness['before']['bar'];assert any(c['id'].startswith('bar:group:') and c['enabled'] for c in controls),controls
  report['checks'].append({'source':str(source.relative_to(REPO)),'passed':True,'expectedPublishes':expected,'witness':witness})
 report['passed']=True
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
