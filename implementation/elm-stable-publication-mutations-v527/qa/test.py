import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-stable-surface-publication-v521';OUT=ROOT/'qa'/('controls-'+str(time.time_ns()));OUT.mkdir()
source=(SOURCE/'src/SurfaceController.elm').read_text();controls=[('force-publish','stableSurface || stableApplications','False || stableApplications','stable'),('lose-state','(Model {model|desktop=next},List.map DesktopEffect effects)','(current,List.map DesktopEffect effects)','owner2'),('suppress-startup','model.publication/=UInt64.zero && ','','startup'),('suppress-visible-change','&& E.encode 0 (Surface.packet model.publication model.lease next)==E.encode 0 (frame current)','&& True','disconnect')]
# The full packet comparison appears twice: this control changes only the first
# new stableSurface guard, retaining the historical applications-only path.
rows=[]
script="const app=require(process.argv[2]).Elm.Probe.init({flags:null});app.ports.outgoing.subscribe(x=>{console.log(JSON.stringify(x));process.exit(0)});app.ports.incoming.send(process.argv[3]);setTimeout(()=>process.exit(2),3000);";(OUT/'probe.cjs').write_text(script)
for name,before,after,case in controls:
 count=source.count(before);assert count==(2 if name=='suppress-visible-change' else 1)
 target=OUT/name;shutil.copytree(SOURCE/'src',target/'src');shutil.copy2(SOURCE/'elm.json',target/'elm.json');shutil.copy2(REPO/'implementation/elm-stable-publication-typed-qa-v522/qa/Probe.elm',target/'src/Probe.elm');(target/'src/SurfaceController.elm').write_text(source.replace(before,after,1))
 binary=target/'worker.js';p=subprocess.run(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--output='+str(binary)],cwd=target,capture_output=True,timeout=180);(target/'compile.stdout').write_bytes(p.stdout);(target/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-1500:]
 p=subprocess.run(['node',str(OUT/'probe.cjs'),str(binary),case],capture_output=True,text=True,timeout=10);(target/'case.stdout').write_text(p.stdout);(target/'case.stderr').write_text(p.stderr);assert p.returncode==0;w=json.loads(p.stdout)
 rejected= w['publishes']!=0 if name=='force-publish' else not w['ownerCorrect'] if name=='lose-state' else w['publishes']!=1
 assert rejected,(name,w);rows.append({'name':name,'case':case,'rejected':True,'witness':w});print(name,'rejected',flush=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={'passed':True,'scope':'Actual compiled Elm incorrect guard mutations rejected by public state transitions; no native proof','nativeAcceptance':False,'controls':rows,'sourceSHA256':sha(SOURCE/'src/SurfaceController.elm'),'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'mutantsRejected':len(rows),'report':str(OUT/'report.json')}))
