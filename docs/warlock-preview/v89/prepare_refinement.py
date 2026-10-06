"""Prepare owned asynchronous-retirement model and actual compiled Elm oracle."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root=r/'implementation/warlock-preview-provider-v89'
assert not (root/'component-manifest.json').exists()
files={
'spec/retirement_async.qnt':r'''module retirement_async {
 type State={first:bool,pendingFirst:bool,knownFirst:bool,readyFirst:bool,
  second:bool,pendingSecond:bool,readySecond:bool,fresh:bool,cutoff:int,
  commands:List[str],history:List[str]}
 type Event=ObserveFirst|ObserveSecond|TerminalFirst|FinalFirst|FinalSecond|
  OldSeedFirst|OldSeedSecond|MidSeedFresh|FreshSeed|ForeignFinal|PrematureFinal|
  DuplicateTerminal|OldObservation
 var s:State
 pure def label(e:Event):str=match e{
  |ObserveFirst=>"ObserveFirst"|ObserveSecond=>"ObserveSecond"|TerminalFirst=>"TerminalFirst"
  |FinalFirst=>"FinalFirst"|FinalSecond=>"FinalSecond"|OldSeedFirst=>"OldSeedFirst"
  |OldSeedSecond=>"OldSeedSecond"|MidSeedFresh=>"MidSeedFresh"|FreshSeed=>"FreshSeed"
  |ForeignFinal=>"ForeignFinal"|PrematureFinal=>"PrematureFinal"
  |DuplicateTerminal=>"DuplicateTerminal"|OldObservation=>"OldObservation"}
 pure def reduce(st:State,e:Event):State={
  val base={...st,commands:[]}
  match e{
   |ObserveFirst=>if(st.first and not(st.pendingFirst))
      {...base,pendingFirst:true,commands:["first:cancel"]} else base
   |ObserveSecond=>if(st.second and not(st.pendingSecond))
      {...base,pendingSecond:true,readySecond:true,commands:["second:retire-ready"]} else base
   |TerminalFirst=>{...base,knownFirst:false,readyFirst:true,commands:["first:acknowledge","first:retire-ready"]}
   |FinalFirst=>if(st.first and st.readyFirst)
      {...base,first:false,pendingFirst:false,readyFirst:false,cutoff:if(st.cutoff>102)st.cutoff else 102} else base
   |FinalSecond=>if(st.second and st.readySecond)
      {...base,second:false,pendingSecond:false,readySecond:false,cutoff:104} else base
   |MidSeedFresh=>if(st.cutoff<103){...base,fresh:true} else base
   |FreshSeed=>{...base,fresh:true}
   |_=>base
  }
 }
 action init=s'={first:true,pendingFirst:false,knownFirst:true,readyFirst:false,
  second:true,pendingSecond:false,readySecond:false,fresh:false,cutoff:0,commands:[],history:[]}
 action fire(e:Event):bool=all{
  match e{
   |TerminalFirst=>s.first and s.pendingFirst and s.knownFirst
   |OldSeedFirst=>not(s.first)
   |OldSeedSecond=>not(s.second)
   |MidSeedFresh=>not(s.fresh) and s.cutoff>0
   |FreshSeed=>not(s.fresh) and s.cutoff>0
   |PrematureFinal=>not(s.readyFirst)
   |DuplicateTerminal=>s.readyFirst or not(s.first)
   |_=>true
  },
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(ObserveFirst,ObserveSecond,TerminalFirst,FinalFirst,FinalSecond,
  OldSeedFirst,OldSeedSecond,MidSeedFresh,FreshSeed,ForeignFinal,PrematureFinal,DuplicateTerminal,OldObservation).oneOf();fire(e)}
 val safety=all{s.readyFirst implies (s.first and s.pendingFirst and not(s.knownFirst)),
  s.readySecond implies (s.second and s.pendingSecond),not(s.first) implies not(s.knownFirst),
  s.cutoff==0 or s.cutoff==102 or s.cutoff==104}
}
''',
'spec/retirement_async_tests.qnt':r'''module retirement_async_tests {
 import retirement_async.* from "./retirement_async"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run completionBehindSiblingObservation=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(FinalFirst)).then(check(not(s.first) and s.second))
 run completionBehindSiblingCompletion=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(FinalSecond)).then(fire(FinalFirst)).then(check(not(s.first) and not(s.second)))
 run pendingJobCannotForget=init.then(fire(ObserveFirst)).then(fire(PrematureFinal)).then(check(s.first and s.knownFirst and not(s.readyFirst)))
 run foreignCompletionNoAuthority=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ForeignFinal)).then(check(s.first and s.readyFirst))
 run ackBeforeReady=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(check(s.commands==["first:acknowledge","first:retire-ready"]))
 run replayedCompletionInert=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(FinalFirst)).then(fire(FinalFirst)).then(fire(DuplicateTerminal)).then(check(not(s.first) and s.commands==[]))
 run olderCompletionCannotRewindCutoff=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(FinalSecond)).then(fire(FinalFirst)).then(fire(MidSeedFresh)).then(check(not(s.fresh) and s.cutoff==104))
 run freshActorAfterReorderedCompletion=init.then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(ObserveSecond)).then(fire(FinalSecond)).then(fire(FinalFirst)).then(fire(OldSeedFirst)).then(fire(OldSeedSecond)).then(fire(FreshSeed)).then(check(not(s.first) and not(s.second) and s.fresh))
 run olderObservationAfterSiblingCompletion=init.then(fire(ObserveSecond)).then(fire(FinalSecond)).then(fire(ObserveFirst)).then(fire(TerminalFirst)).then(fire(FinalFirst)).then(check(not(s.first) and not(s.second)))
 run observationBeforeOwnClockCannotClose=init.then(fire(OldObservation)).then(check(s.first and not(s.pendingFirst) and s.knownFirst))
}
''',
'qa/retirement-refinement-replay.js':r''' 'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Elm}=require(path.resolve(process.argv[2]));
const fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),source=fixture.clientScope,job=fixture.terminalReceipts[0].event.event.frame.job;
const ids={first:'family:'+source.scope.context.incarnation,second:'family:3',fresh:'family:4'};
const label=Object.fromEntries(Object.entries(ids).map(([k,v])=>[v,k]));
function decode(v){if(Array.isArray(v))return v.map(decode);if(v&&typeof v==='object')return '#bigint' in v?Number(v['#bigint']):Object.fromEntries(Object.entries(v).map(([k,x])=>[k,decode(x)]));return v;}
function worker(){const app=Elm.PreviewPresenterReplay.init();let pending;
 app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});
 return (kind,value)=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(new Error('Compiled async refinement timeout')),3000);
  assert(!pending);pending=result=>{clearTimeout(timer);resolve(result);};app.ports.incoming.send({kind,value});});}
const presentation={surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:Object.values(ids).map(id=>({id,domId:'window-'+id,label:'Window',ariaLabel:'Window',detail:'',enabled:true}))};
function seed(who,time){const native=structuredClone(source);if(who!=='first'){native.scope.context.incarnation=ids[who].slice(7);native.requestId=who==='fresh'?'15':'9';native.scope.observation=who==='fresh'?'77':String(BigInt(native.scope.observation)+1n);native.scope.now=String(BigInt(source.scope.now)+BigInt(time??1));}
 return {kind:'source-seed',publication:'1',lease:'1',identity:ids[who],source:native,title:'Native source',application:'fixture'};}
const observation=(subject,request,sequence,time)=>({kind:'native-incarnation-retirement',binding:source.binding,subject,request,sequence,clock:source.scope.clock,now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100',state:'Retired'});
const final=(subject,entry,request,sequence,time)=>({kind:'native-actor-retired',identity:'family:'+subject,binding:source.binding,subject,entry,entryIssuedThrough:'2',requestFloor:entry==='1'?'1':'0',request,sequence,clock:source.scope.clock,now:String(BigInt(source.scope.now)+BigInt(time)),issuedThrough:'100'});
const firstFinal=final(source.scope.context.incarnation,'1','12','3',102),secondFinal=final('3','2','14','5',104);
const terminal={kind:'event',identity:ids.first,event:{kind:'receipt',sequence:'4',event:{kind:'cancelled',job}}};
const events={ObserveFirst:observation(source.scope.context.incarnation,'10','1',100),ObserveSecond:observation('3','13','4',103),
 TerminalFirst:terminal,DuplicateTerminal:terminal,FinalFirst:firstFinal,FinalSecond:secondFinal,PrematureFinal:firstFinal,
 ForeignFinal:{...firstFinal,binding:{...firstFinal.binding,session:'999'}},OldObservation:observation(source.scope.context.incarnation,'10','1',-1),
 OldSeedFirst:seed('first'),OldSeedSecond:seed('second'),MidSeedFresh:seed('fresh',103),FreshSeed:seed('fresh',105)};
function projection(result){const rows=Object.fromEntries(result.models.map(row=>[label[row.identity],row]));assert(Object.keys(rows).every(k=>k!=='undefined'));
 const ready=row=>Boolean(row&&!row.active&&!row.model.demand&&row.model.accepted===null&&row.model.known.length===0&&row.model.cancelling.length===0&&row.model.retiring.length===0);
 return {first:Boolean(rows.first),pendingFirst:Boolean(rows.first&&!rows.first.active),knownFirst:Boolean(rows.first&&rows.first.model.known.length),readyFirst:ready(rows.first),
  second:Boolean(rows.second),pendingSecond:Boolean(rows.second&&!rows.second.active),readySecond:ready(rows.second),fresh:Boolean(rows.fresh),
  commands:result.commands.flatMap(row=>row.commands.map(command=>label[row.identity]+':'+command.kind))};}
(async()=>{const traces=[];let compared=0;
 for(const file of process.argv.slice(4)){const states=decode(JSON.parse(fs.readFileSync(file,'utf8'))).states.map(v=>v.s),send=worker();
  await send('presentation',presentation);await send('native',seed('first'));await send('native',seed('second'));
  const trigger={...job};delete trigger.request;let result=await send('native',{kind:'event',identity:ids.first,event:{kind:'request',trigger}});
  let length=0,count=0;
  for(const state of states){if(state.history.length===0){assert.deepEqual(projection({...result,commands:[]}),Object.fromEntries(Object.entries(state).filter(([k])=>!['history','cutoff'].includes(k))));continue;}
   if(state.history.length===length)continue;assert.equal(state.history.length,length+1);length=state.history.length;
   const event=state.history.at(-1);assert(events[event],event);result=await send('native',events[event]);
   const wanted=Object.fromEntries(Object.entries(state).filter(([k])=>!['history','cutoff'].includes(k)));
   assert.deepEqual(projection(result),wanted,path.basename(file)+' step '+length+' '+event);count++;compared++;}
  traces.push({trace:path.basename(file),statesCompared:count});}
 console.log(JSON.stringify({passed:true,statesCompared:compared,coupledTraces:traces,nativeAcceptance:false,fullReleaseAccepted:false,
  scope:'Actual optimized immutable Elm observable actor/lifecycle state and ordered command projection; cutoff tested through source admission, not observed as an internal field. Synthetic native facts do not establish transport or physical cleanup.'}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
''',
'qa/retirement-refinement-check.py':r'''"""Explicit asynchronous Quint scenarios coupled to actual full-build Elm."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-refinement-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
names=['spec/retirement_async.qnt','spec/retirement_async_tests.qnt','qa/retirement-refinement-replay.js','qa/native-source-fixture.json','qa/retirement-refinement-check.py']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Two independently delivered actor-retirement channels coupled to actual full-build immutable Elm and ordered commands. Synthetic native facts; physical/native transport and continuing >256-window turnover remain open.'}
def run(name,args,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
try:
 build=next(root.glob('qa/build-*/report.json'));proof=json.loads(build.read_text());assert proof['passed'] and len(proof['commands'])==95
 for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
 report['fullBuild']={'path':str(build),'sha256':sha(build)}
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 compiled=out/'preview-replay.js';shutil.copy2(build.parent/'inputs/assets/preview-replay.js',compiled);report['compiledElmSHA256']=sha(compiled)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'retirement_async_tests.qnt').read_text());assert len(selected)==10
 run('typecheck',[str(tool),'typecheck','retirement_async_tests.qnt'],folder)
 run('selected',[str(tool),'test','retirement_async_tests.qnt','--main=retirement_async_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=890051','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
 assert len(list(out.glob('named-*.itf.json')))==10
 run('samples',[str(tool),'run','retirement_async.qnt','--main=retirement_async','--backend=typescript','--invariant=safety','--seed=890052','--max-samples=300','--max-steps=30','--n-traces=20','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
 traces=sorted(out.glob('*.itf.json'))
 evidence=json.loads(run('compiled-replay',['node',str(out/'inputs/qa/retirement-refinement-replay.js'),str(compiled),str(out/'inputs/qa/native-source-fixture.json'),*[str(p) for p in traces]]))
 assert evidence['passed'] and len(evidence['coupledTraces'])==30
 mutants=[]
 for name,old,new,witness in [
  ('global-sibling-gate','if(st.first and st.readyFirst)','if(st.first and st.readyFirst and not(st.pendingSecond))','completionBehindSiblingObservation'),
  ('rewind-shared-clock','cutoff:if(st.cutoff>102)st.cutoff else 102','cutoff:102','olderCompletionCannotRewindCutoff'),
  ('premature-removal','if(st.first and st.readyFirst)','if(st.first)','pendingJobCannotForget')]:
  changed=out/name;shutil.copytree(folder,changed);p=changed/'retirement_async.qnt';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  run(name+'-typecheck',[str(tool),'typecheck','retirement_async_tests.qnt'],changed)
  p=subprocess.run([str(tool),'test','retirement_async_tests.qnt','--main=retirement_async_tests','--backend=typescript','--match=^'+witness+'$','--seed=890053','--max-samples=1'],cwd=changed,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  assert p.returncode!=0 and 'QNT508' in p.stdout+p.stderr and 'Assertion failed' in p.stdout+p.stderr,(name,p.stdout,p.stderr)
  mutants.append({'name':name,'witness':witness,'namedAssertionFailure':True})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,selectedNames=selected,namedScenarios=10,invariantSamples=300,evidence=evidence,unsafeModelMutantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:900]}),flush=True);sys.exit(not report['passed'])
'''}
for name,body in files.items():
 p=root/name;assert not p.exists(),name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-preview-provider-v89',
 ['PROGRESS public62 delivery verified and receipt committed; own fresh GUI89 asynchronous refinement: independently delivered observations/completions, per-actor readiness, ordered ACK/Ready, delayed completion and shared-cutoff seed witnesses. Explicit10 selected scenarios and actual compiled state/command oracle next; native observation/readiness/completion transport, retained completion delivery, actual >256 native/Elm turnover and all original release gates remain.'],
 'progress',['docs/warlock-repository/v62/publication/branch.json','implementation/warlock-preview-provider-v89/qa/retirement-async-check-1791323160645595846/report.json']))
