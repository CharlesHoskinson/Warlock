'use strict';
const assert=require('node:assert/strict');
const {Elm}=require(process.argv[2]),app=Elm.NativePreviewVisualReplay.init();
let pending,checks=0;
app.ports.outgoing.subscribe(v=>{assert(pending);const resolve=pending;pending=null;resolve(v);});
function send(kind,value,domain){return new Promise((resolve,reject)=>{assert(!pending);const timer=setTimeout(()=>reject(Error('Original three-second decoder timeout')),3000);pending=v=>{clearTimeout(timer);resolve(v);};app.ports.incoming.send({kind,value,domain:domain??null});});}
async function accept(kind,value,domain){const r=await send(kind,value,domain);assert(r.accepted,'Original valid '+kind);assert.deepEqual(r.value,value);checks+=2;}
async function refuse(kind,value,domain){const r=await send(kind,value,domain);assert.deepEqual(r,{accepted:false,value:null},'Refuse changed original '+kind);checks++;}
const clone=v=>structuredClone(v),frame='1'.repeat(64),icon='2'.repeat(64);
const domain={binding:{lifetime:'18446744073709551615',session:'2',frontend:'1'},receiverEpoch:'18446744073709551615'};
const surface={surfaceProtocol:2,publication:'18446744073709551615',lease:'18446744073709551615',mode:'picker',status:'',bar:[],popup:[{id:'family:1',domId:'window-1',label:'Window',ariaLabel:'Window',detail:'',enabled:true}]};
const projection={visualProtocol:1,kind:'native-preview-visual',...domain,surface,previews:[{identity:'family:1',visual:{kind:'hidden'}}]};
(async()=>{
 for(const value of [{kind:'hidden'},{kind:'fallback'},...['capacity','waiting','expired','conflict','exhausted'].map(state=>({kind:'local',state,title:'Window'})),...['live','historical'].flatMap(state=>['client','family'].map(fidelity=>({kind:'lifecycle',state,title:null,icon:null,frame,fidelity}))),...['loading','unavailable'].flatMap(state=>[null,icon].map(token=>({kind:'lifecycle',state,title:'Window',icon:token,frame:null,fidelity:null})))])await accept('visual',value);
 for(const value of [null,{},[],{kind:'foreign'},{kind:1},{kind:'hidden',extra:true},{kind:'fallback',title:'hidden metadata'},{kind:'local',state:'foreign',title:'Window'},{kind:'local',state:'waiting',title:null},{kind:'local',state:'waiting',title:'x'.repeat(1025)},{kind:'local',state:'waiting',title:'😀'.repeat(257)},{kind:'local',state:'waiting',title:'bad\x7f'},{kind:'local',state:'waiting',title:'bad\n'},{kind:'local',state:'waiting',title:'Window',job:{}},{kind:'lifecycle',state:'live',title:null,icon:null,frame,fidelity:'foreign'}])await refuse('visual',value);
 await accept('visual',{kind:'local',state:'waiting',title:'x'.repeat(1024)});
 await accept('visual',{kind:'local',state:'waiting',title:'😀'.repeat(256)});
 const live={kind:'lifecycle',state:'live',title:null,icon:null,frame,fidelity:'client'};
 for(const change of [v=>v.extra=true,v=>v.state='unknown',v=>v.frame=null,v=>v.fidelity=null,v=>v.title='leaked metadata',v=>v.icon=icon,v=>v.frame='0'.repeat(64),v=>v.frame='A'.repeat(64),v=>v.frame='1'.repeat(63),v=>v.frame='elm-shell://preview/'+frame,v=>v.frame='https://foreign.example/pixel',v=>v.frame={},v=>v.state='loading',v=>v.known=[]]){const bad=clone(live);change(bad);await refuse('visual',bad);}
 const fallback={kind:'lifecycle',state:'unavailable',title:'Preview unavailable',icon:null,frame:null,fidelity:null};
 for(const change of [v=>v.title=null,v=>v.frame=frame,v=>v.fidelity='client',v=>v.icon='0'.repeat(64),v=>v.icon='javascript:foreign',v=>v.icon={},v=>v.title='bad\r']){const bad=clone(fallback);change(bad);await refuse('visual',bad);}
 await accept('projection',projection,domain);
 for(const change of [v=>v.visualProtocol=2,v=>v.kind='foreign',v=>v.extra=true,v=>v.binding.frontend='2',v=>v.receiverEpoch='1',v=>v.receiverEpoch=1,v=>v.receiverEpoch='18446744073709551616',v=>v.previews=[],v=>v.previews.push(v.previews[0]),v=>v.previews[0].identity='family:foreign',v=>v.previews[0].extra=true,v=>v.previews[0].visual.extra=true,v=>v.surface=null,v=>v.surface.extra=true,v=>v.surface.publication='0',v=>v.surface.mode='foreign',v=>v.surface.popup[0].extra=true,v=>v.surface.bar=clone(v.surface.popup)]){const bad=clone(projection);change(bad);await refuse('projection',bad,domain);}
 await accept('projection',{...projection,surface:null,previews:[]},domain);
 const twin=clone(projection);twin.surface.popup.push({...twin.surface.popup[0],id:'family:2',domId:'window-2'});twin.previews.push({identity:'family:2',visual:clone(live)});await accept('projection',twin,domain);
 const reordered=clone(twin);reordered.previews.reverse();await refuse('projection',reordered,domain);
 const full=clone(projection);full.surface.popup=Array.from({length:2051},(_,i)=>({...surface.popup[0],id:'family:'+i,domId:'window-'+i}));full.previews=full.surface.popup.map(row=>({identity:row.id,visual:{kind:'hidden'}}));await accept('projection',full,domain);
 const exceeded=clone(full);exceeded.surface.popup.push({...surface.popup[0],id:'family:2051',domId:'window-2051'});exceeded.previews.push({identity:'family:2051',visual:{kind:'hidden'}});await refuse('projection',exceeded,domain);
 const bar=clone(projection);bar.surface.bar=Array.from({length:259},(_,i)=>({...surface.popup[0],id:'bar:'+i,domId:'bar-'+i}));await accept('projection',bar,domain);bar.surface.bar.push({...surface.popup[0],id:'bar:259',domId:'bar-259'});await refuse('projection',bar,domain);
 console.log(JSON.stringify({passed:true,checks,pureRendererDecoder:true,windowPolicyInstances:0,originalPopupCapacity:2051,originalBarCapacity:259,losslessUInt64:true,nativeAcceptance:false,fullReleaseAccepted:false}));
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
