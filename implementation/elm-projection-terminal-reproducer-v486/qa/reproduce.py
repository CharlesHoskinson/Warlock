import hashlib,importlib.util,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-shared-geometry-carrier-v422';OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
held=REPO/'implementation/elm-xdg-origin-combined-qualification-v484/qa/slice-manifest.json';assert sha(held)=='1860680083a19d1db101ed30f066a2b25b8442e63071663953124f368a5fbbc4'
for e in json.loads(held.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
log=REPO/'implementation/elm-xdg-origin-menu-regression-v478/qa/native-1791134835598728098/native-evidence/elm-webview.log';lines=log.read_text().splitlines();requests=[json.loads(l.split(': ',1)[1]) for l in lines if l.startswith('frontend-request: ')];request=next(r for r in requests if r.get('kind')=='projection-request' and r.get('requestId')=='58')
sys.path.insert(0,str(SOURCE/'adapter'));spec=importlib.util.spec_from_file_location('actual_frozen_daemon',SOURCE/'adapter/daemon.py');daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon);emitted=[];daemon.send=emitted.append
class Client:
 bound=request['binding'];calls=[]
 def scene_facts(self,req):
  self.calls.append(('facts',req));return {'revision':'18' if len(self.calls)==1 else '19','outputGeneration':'1'}
 def snapshot(self,req):self.calls.append(('snapshot',req));return {'windows':[]}
client=Client();daemon.handle_request(client,None,request,None);assert emitted==[{'protocolVersion':3,'kind':'host-refresh'}];assert client.calls==[('facts','58'),('snapshot','58'),('facts','58')]
assert not any(x.get('requestId')=='58' for x in emitted)
inputs=OUT/'inputs';shutil.copytree(SOURCE/'src',inputs/'src');shutil.copy2(SOURCE/'elm.json',inputs/'elm.json');worker='''port module ProjectionWitness exposing (main)
import Binding
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker {init=\\_ -> ((),Cmd.none),subscriptions=\\_ -> incoming Run,update=\\(Run raw) _ ->
 let decoded=D.decodeValue (D.map2 Tuple.pair (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder)) raw
 in case decoded of
  Err _ -> ((),outgoing E.null)
  Ok (binding,request) ->
   let base=Shell.initial
       pending={base|binding=Just binding,request=request,expected=Just request,phase=Shell.Reconciling,reconnecting=False}
       notice=E.object [("protocolVersion",E.int 3),("kind",E.string "host-refresh")]
       apply _ (model,count)=let (next,stepCommands)=Shell.update (Shell.Incoming notice) model in (next,count+List.length stepCommands)
       (final,commands)=List.foldl apply (pending,0) (List.range 1 100)
   in ((),outgoing (E.object [("model",Shell.encode final),("expected",Maybe.map (UInt64.string >> E.string) final.expected |> Maybe.withDefault E.null),("commands",E.int commands)]))}
''';(inputs/'src/ProjectionWitness.elm').write_text(worker)
cmd=['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/ProjectionWitness.elm','--output='+str(OUT/'worker.js')];p=subprocess.run(cmd,cwd=inputs,capture_output=True,timeout=180);(OUT/'compile.stdout').write_bytes(p.stdout);(OUT/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-1500:]
script="const fs=require('fs');const Elm=require(process.argv[2]).Elm;const app=Elm.ProjectionWitness.init({flags:null});app.ports.outgoing.subscribe(x=>{console.log(JSON.stringify(x));process.exit(0)});app.ports.incoming.send(JSON.parse(fs.readFileSync(process.argv[3],'utf8')));setTimeout(()=>process.exit(2),3000);";(OUT/'replay.cjs').write_text(script);(OUT/'request.json').write_text(json.dumps(request)+'\n');p=subprocess.run(['node',str(OUT/'replay.cjs'),str(OUT/'worker.js'),str(OUT/'request.json')],capture_output=True,text=True,timeout=10);(OUT/'replay.stdout').write_text(p.stdout);(OUT/'replay.stderr').write_text(p.stderr);assert p.returncode==0;model=json.loads(p.stdout);assert model['expected']=='58' and model['commands']==0 and model['model']['phase']=='Reconciling' and model['model']['notificationQueued'] is True
report={'passed':True,'scope':'Actual frozen backend handler with synthetic disagreeing native fact revisions18/19 and actual compiled Shell422 pending-read state from capturedrequest58; no new native or repair acceptance','backendCalls':client.calls,'actualBackendFrames':emitted,'compiledShellWitness':model,'inputs':{str(p):sha(p) for p in [Path(__file__),held,log,SOURCE/'adapter/daemon.py',SOURCE/'src/Shell.elm']},'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts},'nativeAcceptance':False};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'handlerCorrelatedReplies':0,'compiledShellQueuedNotices':100,'compiledShellCommands':0,'report':str(OUT/'report.json')}))
