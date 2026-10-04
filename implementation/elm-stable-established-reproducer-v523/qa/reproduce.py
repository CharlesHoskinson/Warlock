import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-projection-native-escape-combined-v507';OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
inputs=OUT/'inputs';shutil.copytree(SOURCE/'src',inputs/'src');shutil.copy2(SOURCE/'elm.json',inputs/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',inputs/'src/Probe.elm')
p=subprocess.run(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--output='+str(OUT/'worker.js')],cwd=inputs,capture_output=True,timeout=180);(OUT/'compile.stdout').write_bytes(p.stdout);(OUT/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-2000:]
s="const app=require(process.argv[2]).Elm.Probe.init({flags:null});app.ports.outgoing.subscribe(x=>{console.log(JSON.stringify(x));process.exit(0)});app.ports.incoming.send(null);setTimeout(()=>process.exit(2),3000);";(OUT/'probe.cjs').write_text(s)
p=subprocess.run(['node',str(OUT/'probe.cjs'),str(OUT/'worker.js')],capture_output=True,text=True,timeout=10);assert p.returncode==0;witness=json.loads(p.stdout);assert witness['stateChanged'] and witness['sameSurface'] and witness['publishCount']==1 and witness['before']['publication']!=witness['after']['publication']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'passed':True,'scope':'Actual compiled SurfaceController internal owner change republishes identical closed surface; synthetic initial state, not causal504/native repair proof','witness':witness,'nativeAcceptance':False,'inputs':{str(p):sha(p) for p in [Path(__file__),ROOT/'qa/Probe.elm',SOURCE/'src/SurfaceController.elm']},'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'witness':witness}))
