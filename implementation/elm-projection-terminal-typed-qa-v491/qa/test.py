import hashlib,importlib.util,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-projection-correlated-terminal-v490';OUT=ROOT/'qa'/('checks-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
log=REPO/'implementation/elm-xdg-origin-menu-regression-v478/qa/native-1791134835598728098/native-evidence/elm-webview.log';requests=[json.loads(l.split(': ',1)[1]) for l in log.read_text().splitlines() if l.startswith('frontend-request: ')];request=next(r for r in requests if r.get('kind')=='projection-request' and r.get('requestId')=='58');sys.path.insert(0,str(SOURCE/'adapter'));spec=importlib.util.spec_from_file_location('actual_fixed_daemon',SOURCE/'adapter/daemon.py');daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon);frames=[];daemon.send=frames.append
class Client:
 bound=request['binding'];calls=[]
 def scene_facts(self,req):self.calls.append(('facts',req));return {'revision':'18' if len(self.calls)==1 else '19','outputGeneration':'1'}
 def snapshot(self,req):self.calls.append(('snapshot',req));return {'windows':[]}
client=Client();daemon.handle_request(client,None,request,None);terminal={'protocolVersion':3,'kind':'projection-unavailable','binding':request['binding'],'requestId':'58','reason':'scene-changed'};assert frames==[terminal]
inputs=OUT/'inputs';shutil.copytree(SOURCE/'src',inputs/'src');shutil.copy2(SOURCE/'elm.json',inputs/'elm.json');worker='''port module TerminalProbe exposing (main)
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
 let decoded=D.decodeValue (D.map2 Tuple.pair (D.at ["request","binding"] Binding.decoder) (D.at ["request","requestId"] UInt64.decoder)) raw
 in case decoded of
  Err _ -> ((),outgoing E.null)
  Ok (binding,request) ->
   let base=Shell.initial
       current=UInt64.next request |> Maybe.withDefault request
       bool name=D.decodeValue (D.field name D.bool) raw |> Result.withDefault False
       pending={base|binding=Just binding,request=current,expected=Just request,geometryExpected=Just current,phase=Shell.Reconciling,reconnecting=False,transportRefused=bool "transport",deferNotifications=bool "defer"}
       notice=D.decodeValue (D.field "frame" D.value) raw |> Result.withDefault E.null
       apply _ (model,count)=let (next,stepCommands)=Shell.update (Shell.Incoming notice) model in (next,count+List.length stepCommands)
       (final,commands)=List.foldl apply (pending,0) (List.range 1 100)
   in ((),outgoing (E.object [("model",Shell.encode final),("expected",Maybe.map (UInt64.string >> E.string) final.expected |> Maybe.withDefault E.null),("geometryExpected",Maybe.map (UInt64.string >> E.string) final.geometryExpected |> Maybe.withDefault E.null),("retry",E.bool final.projectionRetryQueued),("effectsPreserved",E.bool (final.effects==pending.effects)),("commands",E.int commands)]))}
''';(inputs/'src/TerminalProbe.elm').write_text(worker)
p=subprocess.run(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/TerminalProbe.elm','--output='+str(OUT/'worker.js')],cwd=inputs,capture_output=True,timeout=180);(OUT/'compile.stdout').write_bytes(p.stdout);(OUT/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-1500:]
script="const fs=require('fs');const app=require(process.argv[2]).Elm.TerminalProbe.init({flags:null});app.ports.outgoing.subscribe(x=>{console.log(JSON.stringify(x));process.exit(0)});app.ports.incoming.send(JSON.parse(fs.readFileSync(process.argv[3],'utf8')));setTimeout(()=>process.exit(2),3000);";(OUT/'probe.cjs').write_text(script)
cases=[('matching',terminal,{},'60',1,False),('foreign',dict(terminal,binding=dict(request['binding'],frontend='2')),{},'58',0,False),('stale',dict(terminal,requestId='57'),{},'58',0,False),('noncanonical',dict(terminal,requestId='058'),{},'58',0,False),('unknownReason',dict(terminal,reason='guess'),{},'58',0,False),('extra',dict(terminal,extra=True),{},'58',0,False),('protocol',dict(terminal,protocolVersion=4),{},'58',0,False),('transport',terminal,{'transport':True},None,0,True),('deferred',terminal,{'defer':True},None,0,True)]
checks=[]
for name,frame,options,expected,count,retry in cases:
 arg=OUT/(name+'.json');arg.write_text(json.dumps({'request':request,'frame':frame,**options})+'\n');p=subprocess.run(['node',str(OUT/'probe.cjs'),str(OUT/'worker.js'),str(arg)],capture_output=True,text=True,timeout=10);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);assert p.returncode==0;actual=json.loads(p.stdout);assert actual['expected']==expected and actual['commands']==count and actual['retry']==retry and actual['geometryExpected']=='59' and actual['effectsPreserved'];checks.append({'name':name,'passed':True,'actual':actual})
report={'passed':True,'scope':'Actual candidate backend with synthetic changing facts and compiled actual typed Shell decoder/retry state; no native repair acceptance','checks':checks,'backendFrames':frames,'inputs':{str(p):sha(p) for p in [Path(__file__),log,SOURCE/'adapter/daemon.py',SOURCE/'src/Shell.elm']},'artifacts':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts},'nativeAcceptance':False};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'typedCases':len(checks),'report':str(OUT/'report.json')}))
