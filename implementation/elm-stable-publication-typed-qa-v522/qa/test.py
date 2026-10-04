import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-stable-surface-publication-v521';OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
inputs=OUT/'inputs';shutil.copytree(SOURCE/'src',inputs/'src');shutil.copy2(SOURCE/'elm.json',inputs/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',inputs/'src/Probe.elm')
p=subprocess.run(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--output='+str(OUT/'worker.js')],cwd=inputs,capture_output=True,timeout=180);(OUT/'compile.stdout').write_bytes(p.stdout);(OUT/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-2000:]
s="const app=require(process.argv[2]).Elm.Probe.init({flags:null});app.ports.outgoing.subscribe(x=>{console.log(JSON.stringify(x));process.exit(0)});app.ports.incoming.send(process.argv[3]);setTimeout(()=>process.exit(2),3000);";(OUT/'probe.cjs').write_text(s)
cases=[('startup',1,0,True,True),('stable',0,0,True,True),('owner2',0,0,True,True),('duplicate',0,0,True,False),('disconnect',1,0,False,True),('reconnect',1,1,False,True),('invalid',0,0,True,False),('relocateClosed',0,0,True,False),('many',0,0,True,False)]
checks=[]
for name,publishes,others,same,changed in cases:
 p=subprocess.run(['node',str(OUT/'probe.cjs'),str(OUT/'worker.js'),name],capture_output=True,text=True,timeout=10);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);assert p.returncode==0
 witness=json.loads(p.stdout);assert witness['publishes']==publishes and witness['otherEffects']==others and witness['sameSurface']==same and witness['stateChanged']==changed and witness['ownerCorrect'],(name,witness)
 checks.append({'name':name,'passed':True,'witness':witness})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'passed':True,'scope':'Actual compiled public SurfaceController transitions preserve established full surface on empty effects; startup, visible changes and reconnect remain published; no causal504/native proof','checks':checks,'nativeAcceptance':False,'inputs':{str(p):sha(p) for p in [Path(__file__),ROOT/'qa/Probe.elm',SOURCE/'src/SurfaceController.elm']},'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'cases':len(checks)}))
