"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const {Elm}=require(path.resolve(process.argv[2])),fixture=JSON.parse(fs.readFileSync(process.argv[3],"utf8"));
assert.equal(crypto.createHash("sha256").update(fs.readFileSync(fixture.sourceReport)).digest("hex"),fixture.sourceReportSHA256);
const source=fixture.clientScope,frame=fixture.terminalReceipts[0].event.event.frame,job=frame.job,owner=job.binding,identity="family:"+job.context.incarnation;
let checks=0;const check=(a,b,msg)=>{assert.deepEqual(a,b,msg);checks++;};
const commands=r=>r.commands.flatMap(row=>row.commands),model=r=>r.models.find(row=>row.identity===identity)?.model;
const wrapped=event=>({kind:"event",identity,event});
const seed={kind:"source-seed",publication:"1",lease:"1",identity,source,title:"Scoped title",application:"own.app"};
const control=(subject,enabled=true)=>({id:"family:"+subject,domId:"client"+subject,label:"Client",ariaLabel:"Client",detail:"",enabled});
const presentation={surfaceProtocol:2,publication:"1",lease:"1",mode:"picker",status:"",bar:[],popup:[control(job.context.incarnation),control("9007199254740993"),control("8",false)]};
const row=(subject=job.context.incarnation,minimized=false)=>({incarnation:subject,label:"Actual λ 🌙 title",application:"own.app",minimized});
const catalog=(request="1",rows=[row()])=>({protocolVersion:3,kind:"catalog",publication:"1",lease:"1",binding:structuredClone(owner),requestId:request,sequence:request,revision:"1",windows:rows});
function worker(){const app=Elm.PreviewCatalogReplay.init();let pending=null;app.ports.outgoing.subscribe(value=>{assert(pending);const done=pending;pending=null;done(value);});return (kind,value)=>new Promise((resolve,reject)=>{assert.equal(pending,null);const timer=setTimeout(()=>{pending=null;reject(Error("Original three-second Elm enrollment replay deadline"));},3000);pending=v=>{clearTimeout(timer);resolve(v);};app.ports.incoming.send({kind,value});});}
async function prepared(){const send=worker();await send("presentation",presentation);return send;}
async function start(send){await send("native",seed);const trigger=structuredClone(job);delete trigger.request;return send("native",wrapped({kind:"request",trigger}));}
async function controls(){
 let send=await prepared(),result=await send("native",catalog("9007199254740993",[row(),row("9007199254740993",true),row("8"),row("99")]));
 check(result.models.map(r=>[r.identity,r.model]),[[identity,null],["family:9007199254740993",null]],"Only enabled exact picker/native incarnations enroll without scopes");
 check(result.enrollment,[{identity,nativeScoped:false,minimized:false},{identity:"family:9007199254740993",nativeScoped:false,minimized:true}],"Native minimized fact retained losslessly");
 check(commands(result),[],"Inventory cannot acquire or settle");check(result.metadata.map(r=>r.visible),[false,false],"Inventory alone supplies no native privacy authority");
 const unchanged=structuredClone(result);
 const mutations=[c=>c.extra=true,c=>c.protocolVersion=2,c=>c.publication="2",c=>c.lease="2",c=>c.binding.session="999",c=>c.binding.extra=true,c=>c.requestId="9007199254740993",c=>c.requestId="9007199254740992",c=>c.sequence="9007199254740993",c=>c.revision="0",c=>c.revision=1,c=>c.requestId="01",c=>c.requestId="18446744073709551616",c=>c.windows.push(row()),c=>c.windows[0].incarnation="0",c=>c.windows[0].incarnation=2,c=>c.windows[0].extra=true,c=>c.windows[0].minimized="false",c=>c.windows[0].label="λ".repeat(513),c=>c.windows[0].application="bad\nlabel",c=>c.windows.push({...row("99"),minimized:0}),c=>c.windows=Array.from({length:257},(_,i)=>row(String(i+1)))];
 for(const mutate of mutations){const value=catalog("9007199254740994",[row(),row("9007199254740993",true)]);mutate(value);result=await send("native",value);check(result,unchanged,"Whole malformed/stale/foreign catalog is atomic refusal");}
 result=await send("native",wrapped({kind:"request",trigger:(()=>{const t=structuredClone(job);delete t.request;return t;})()}));check(result,unchanged,"Metadata-only entries cannot accept capture triggers");
 result=await send("native",catalog("18446744073709551615",[row(job.context.incarnation,true)]));check(result.enrollment,[{identity,nativeScoped:false,minimized:true}],"Latest metadata-only catalog removes missing inventory without physical authority");
 result=await send("presentation",{...presentation,publication:"2",lease:"2"});check(result.models,[],"Closing stale metadata-only enrollment needs no fabricated lifecycle cleanup");
 send=await prepared();result=await start(send);const beforeFirst=structuredClone(result);result=await send("native",{...catalog("1",[]),binding:{...owner,session:"999"}});check(result,{...beforeFirst,commands:[]},"Foreign first empty catalog cannot cancel an already scoped owner");
 send=await prepared();await send("native",catalog());result=await start(send);check(commands(result),[{kind:"acquire",job}],"Only exact native source plus original request emits Acquire");check(model(result).scope,source.scope,"Catalog promotion retains actual scope and native clock");check(result.enrollment,[{identity,nativeScoped:true,minimized:false}],"Promotion remains one entry in one Elm state");
 const active=structuredClone(model(result));result=await send("native",catalog("2",[row(job.context.incarnation,true)]));check(model(result),active,"Metadata inventory cannot mutate existing capture policy");check(commands(result),[],"Catalog does not issue another capture");
 result=await send("native",catalog("3",[]));check(commands(result),[{kind:"cancel",job}],"Removed inventory emits original exact Cancel");check(model(result).known,[job],"Removal retains original native job until receipt");check(model(result).scope,source.scope,"Removal never fabricates clock or deadline");check(result.models[0].active,false,"Removed capture entry stops presentation demand");
 result=await send("native",catalog("4",[]));check(commands(result),[],"Repeated removal cannot replay cancellation");check(model(result).cancelling,[job],"Unknown cleanup remains owned");
 result=await send("native",catalog("5"));check(commands(result),[],"Reappearance cannot reopen or replay retained capture");check(model(result).cancelling,[job],"Reappearance does not retire old job");check(result.models[0].active,false,"Only a new native seed may reopen demand");
 result=await send("native",wrapped({kind:"receipt",sequence:"1",event:{kind:"cancelled",job}}));check(commands(result),[{kind:"acknowledge",job,sequence:"1"}],"Exact terminal receipt acknowledgement remains routed to retained owner");check(model(result).known,[],"Only exact receipt clears known original job");
 for(const stage of ["candidate","accepted"]){
  send=await prepared();await send("native",catalog());await start(send);await send("native",wrapped({kind:"offer",frame:{...frame,signaled:false}}));if(stage==="accepted")await send("native",wrapped({kind:"fence",frame}));
  result=await send("native",catalog("2",[]));
  if(stage==="accepted"){
   check(commands(result),[],"Inventory removal cannot revoke accepted historical native cache");check(model(result).accepted,frame,"Accepted original resource remains owned after demand closes");check(model(result).known,[job],"Closed accepted cache retains exact original job");
   result=await send("native",wrapped({kind:"source-denied",job,reason:"source-unavailable"}));
  }
  check(commands(result),[{kind:"release",frame:stage==="candidate"?{...frame,signaled:false}:frame}],"Original native denial or candidate close releases exact frame");check(model(result).retiring.length,1,"Catalog cannot prove physical retirement");check(model(result).known,[job],"Frame native ownership retained");
  result=await send("native",fixture.terminalReceipts[0]);check(commands(result),[{kind:"acknowledge",job,sequence:"3"}],"Original frame receipt still routed after inventory removal");check(model(result).retiring,[],"Exact receipt retires original frame");
 }
 send=await prepared();result=await send("native",catalog("1",Array.from({length:256},(_,i)=>row(String(i+1)))));check(result.models.length,1,"256-record native catalog accepted and intersected");
 console.log(JSON.stringify({passed:true,checks,nativeAcceptance:false,fullReleaseAccepted:false,scope:"Actual optimized Elm strict catalog, metadata-only/native promotion, original Cancel/Release/ACK and scope/job/deadline retention; controlled fixture deliveries do not prove physical/native product enrollment"}));
}
async function replay(trace){const send=await prepared();let request=0,result=await send("native",{kind:"invalid"}),cancels=0;const actual=[];
 for(const name of trace){
  switch(name){
   case "Catalog":result=await send("native",catalog(String(++request)));break;
   case "Minimized":result=await send("native",catalog(String(++request),[row(job.context.incarnation,true)]));break;
   case "Remove":result=await send("native",catalog(String(++request),[]));break;
   case "Stale":result=await send("native",catalog(String(request)));break;
   case "Foreign":result=await send("native",{...catalog(String(request+1)),binding:{...owner,session:"999"}});break;
   case "Start":result=await start(send);break;
   case "Receipt":result=await send("native",wrapped({kind:"receipt",sequence:"1",event:{kind:"cancelled",job}}));break;
   default:throw Error("Unknown Quint action "+name);
  }
  const emitted=commands(result);for(const c of emitted){if(c.kind==="cancel")cancels++;assert(["acquire","cancel","acknowledge"].includes(c.kind));assert.deepEqual(c.job,job);}
  const current=model(result),inventory=result.enrollment.find(r=>r.identity===identity);
  actual.push({present:!!inventory,scoped:!!current,demand:!!current?.demand,pending:!!current?.cancelling.length,known:current?.known.length||0,minimized:!!inventory?.minimized,request,cancels,history:[]});
 }
 process.stdout.write(JSON.stringify(actual)+"\n");
}
(async()=>{if(process.argv[4]==="--replay"){let raw="";for await(const chunk of process.stdin)raw+=chunk;await replay(JSON.parse(raw));}else await controls();})().catch(error=>{process.stderr.write(error.stack+"\n");process.exitCode=1;});
