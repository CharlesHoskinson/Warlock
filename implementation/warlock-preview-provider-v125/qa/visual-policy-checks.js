'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),readline=require('node:readline'),{spawn}=require('node:child_process');
const {Elm}=require(process.argv[4]),codec=Elm.NativePreviewVisualReplay.init();let decoderPending,checks=0;
codec.ports.outgoing.subscribe(v=>{assert(decoderPending);const resolve=decoderPending;decoderPending=null;resolve(v);});
const fixture=JSON.parse(fs.readFileSync(process.argv[5],'utf8')),source=fixture.clientScope,baseFrame=fixture.terminalReceipts[0].event.event.frame;
function same(a,b,label){assert.deepEqual(a,b,label);checks++;}function check(value,label){assert(value,label);checks++;}
function decoded(value){return new Promise((resolve,reject)=>{assert(!decoderPending);const timer=setTimeout(()=>reject(Error('Original three-second visual decoder timeout')),3000);decoderPending=v=>{clearTimeout(timer);resolve(v);};codec.ports.incoming.send({kind:'projection',domain:{binding:value.binding,receiverEpoch:value.receiverEpoch},value});});}
(async()=>{
 for(const fidelity of ['client','family']){
  const child=spawn(process.argv[3],[process.argv[2]],{stdio:['pipe','pipe','pipe']});let waiting,stderr='';const buffered=[];
  child.stderr.on('data',data=>stderr+=data);const terminal=new Promise(resolve=>child.on('close',(code,signal)=>{resolve({code,signal});if(waiting){clearTimeout(waiting.timer);waiting.reject(Error('Owned worker exit: '+stderr));waiting=null;}}));
  readline.createInterface({input:child.stdout}).on('line',line=>{const value=JSON.parse(line);if(waiting){const resolve=waiting.resolve;clearTimeout(waiting.timer);waiting=null;resolve(value);}else buffered.push(value);});
  function call(value){child.stdin.write(JSON.stringify(value)+'\n');if(buffered.length)return Promise.resolve(buffered.shift());return new Promise((resolve,reject)=>{assert(!waiting);const timer=setTimeout(()=>reject(Error('Original three-second native policy timeout')),3000);waiting={resolve,reject,timer};});}
  const domain={binding:source.binding,receiverEpoch:'1'},identity='family:'+source.scope.context.incarnation;let ordinal=0;
  const wrap=event=>({previewProtocol:3,kind:'native-preview-realm-event',...domain,event});
  async function send(kind,value=null){const row=await call({op:'invoke',input:JSON.stringify({kind,value})});check(row.ok && row.code===0,'Original C/JSC invocation');const projection=row.projection;if(projection.visuals!==null){const valid=await decoded(projection.visuals);check(valid.accepted,'Authoritative policy emits valid visual DTO');same(valid.value,projection.visuals,'Pure renderer decoder retains exact projection');}return projection;}
  async function flush(r){while(r.realm.ingress.pending){const row=r.realm.ingress.intents[0];ordinal++;const packet={previewProtocol:3,kind:'preview-commands',...domain,controlOrdinal:String(ordinal),entries:[row]};r=await send('issued',{previewProtocol:3,kind:'preview-control-ticket',...domain,controlOrdinal:String(ordinal),alreadyDelivered:false,wire:JSON.stringify(packet)});}return r;}
  try{
   const initial=await send('status');same(initial.visuals,null,'Uncontrolled worker projects no realm authority');
   await send('grant',{...domain,capacity:1065});
   await send('presentation',{surfaceProtocol:2,publication:'1',lease:'1',mode:'picker',status:'',bar:[],popup:[{id:identity,domId:'window',label:'Window',ariaLabel:'Window',detail:'',enabled:true}]});
   await send('native',wrap({kind:'source-seed',publication:'1',lease:'1',identity,source,title:'Private window',application:'fixture'}));
   const frame=structuredClone(baseFrame);frame.fidelity=fidelity;if(fidelity==='family')frame.coverage=['client','decoration','modal','popup'];
   const trigger={...frame.job};delete trigger.request;
   let r=await send('native',wrap({kind:'event',identity,event:{kind:'request',trigger}}));same(r.visuals.previews[0].visual.state,'loading');check(r.models[0].model.known.length===1,'Original Unknown job retained');await flush(r);
   r=await send('native',wrap({kind:'event',identity,event:{kind:'offer',frame}}));same(r.visuals.previews[0].visual,{kind:'lifecycle',state:'live',title:null,icon:null,frame:frame.handle,fidelity});same(r.models[0].model.image,'elm-shell://preview/'+frame.handle);check(r.models[0].model.known.length===1,'Projection does not settle original resource');
   const scope=structuredClone(source.scope);scope.observation=String(BigInt(scope.observation)+1n);scope.now=String(BigInt(scope.now)+1n);scope.context.content=String(BigInt(scope.context.content)+1n);
   r=await send('native',wrap({kind:'event',identity,event:{kind:'observe',scope}}));same(r.visuals.previews[0].visual,{kind:'lifecycle',state:'historical',title:null,icon:null,frame:frame.handle,fidelity});same(r.models[0].model.state,'historical','Historical display uses original policy authorization');
   scope.locked=true;scope.observation=String(BigInt(scope.observation)+1n);scope.now=String(BigInt(scope.now)+1n);scope.context.privacy=String(BigInt(scope.context.privacy)+1n);
   r=await send('native',wrap({kind:'event',identity,event:{kind:'observe',scope}}));same(r.visuals.previews[0].visual,{kind:'lifecycle',state:'unavailable',title:'Preview unavailable',icon:null,frame:null,fidelity:null});check(r.models[0].model.known.length===1 && r.models[0].model.retiring.length===1,'Concealment retains Unknown and physical retirement');check(!JSON.stringify(r.visuals).includes('Private window') && !JSON.stringify(r.visuals).includes(frame.handle),'Visual DTO excludes concealed preview metadata/resource');await flush(r);
   r=await send('native',wrap({kind:'event',identity,event:{kind:'receipt',sequence:'4',event:{kind:'released',frame}}}));same(r.models[0].model.known,[],'Explicitly synthetic exact terminal receipt settles original job');await flush(r);
   r=await send('quarantine',domain);same(r.visuals.previews[0].visual,{kind:'hidden'},'Quarantine revokes the same original presentation stamp');await flush(r);
   const seed={detachProtocol:1,kind:'native-preview-detach-seed',identity,...domain,subject:source.scope.context.incarnation,entry:'1',entryIssuedThrough:'1',requestFloor:'1'};
   r=await send('native',wrap(seed));check(r.commands.entries.some(row=>row.commands[0].kind==='detach-ready'),'Readiness follows exact settlement');await flush(r);
   r=await send('native',wrap({detachProtocol:1,kind:'native-preview-binding-detach-delivery',...domain,deliveryOrdinal:'1',event:{kind:'native-preview-actor-detached',identity,subject:seed.subject,entry:'1',entryIssuedThrough:'1',requestFloor:'1'}}));same(r.models,[]);same(r.visuals.previews[0].visual,{kind:'hidden'},'Detached membership produces no preview');await flush(r);
   r=await send('closed',domain);check(r.realm.closed,'Explicit synthetic native close after empty ingress');same(await call({op:'close'}),{ok:true,code:0,held:false});child.stdin.end();same(await terminal,{code:0,signal:null});same(stderr,'');
  }catch(error){child.stdin.destroy();child.kill('SIGTERM');await terminal;throw error;}
 }
 console.log(JSON.stringify({passed:true,checks,actualNativeOwnedJSC:true,singleWindowPolicyPerFixture:true,pureRendererDecoder:true,syntheticNativeFacts:true,cohorts:['client','family'],states:['loading','live','historical','locked-unavailable','quarantine-hidden','detached-hidden'],normalOwnedExits:2,actualDOM:false,actualCapturedFD:false,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
