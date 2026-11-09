"use strict";
// Uninstrumented compiled HttpBar; controlled DOM/XHR component only.
// Synthetic DOM key delivery to uninstrumented compiled production; no native input claim.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const [image,output]=process.argv.slice(2);
if(process.argv.length!==4)throw Error('Expected explicit compiled HttpBar.js-or-html and NEW report.json');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const report={schema:1,passed:false,scope:'UX024 rendered taskbar context-key component',nativeAcceptance:false,originalAccepted:false,checks:[],failures:[],trace:[],cases:[],artifactHashes:{image:hash(fs.readFileSync(image)),harness:hash(fs.readFileSync(__filename))}};
function check(name,ok,witness){const row={name,passed:!!ok};if(!ok)row.witness=witness??null;report.checks.push(row);if(!ok)report.failures.push(row);}
function need(name,ok,witness){check(name,ok,witness);if(!ok){report.setupFailures=(report.setupFailures??0)+1;throw Error(name);}}
function compiledSource(file){const raw=fs.readFileSync(file,'utf8');if(!raw.trimStart().startsWith('<'))return raw;
 const scripts=[...raw.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m=>m[1]);
 const selected=scripts.filter(s=>s.includes('_Platform_export')&&s.includes('HttpBar'));
 if(selected.length!==1)throw Error('Expected exactly one uninstrumented Elm HttpBar script');
 const start='(function(scope){',end='}(this));',body=selected[0],a=body.indexOf(start),z=body.indexOf(end);
 if(a<0||z<a||body.indexOf(start,a+1)>=0||body.indexOf(end,z+1)>=0)throw Error('Unexpected Elm HTML wrapper');
 return body.slice(a,z+end.length);}

const environments=[];let activeNode=null;const focusLog=[];
async function bounded(_label,promise){return promise;}
class Node {
  constructor(type,name,text=''){this.nodeType=type;this.tagName=name;this.nodeName=name;this.data=text;this.nodeValue=text;this.parentNode=null;this.childNodes=[];this.attributes={};this.style={setProperty(k,v){this[k]=v;},removeProperty(k){delete this[k];}};this.listeners={};}
  get textContent(){return this.nodeType===3?this.data:this.childNodes.map(x=>x.textContent).join('');}
  set textContent(value){if(this.nodeType===3){this.data=String(value);this.nodeValue=this.data;}else{this.childNodes=[];if(value)this.appendChild(new Node(3,'#text',String(value)));}}
  appendChild(child){return this.insertBefore(child,null);}
  insertBefore(child,before){if(child.nodeType===11){for(const item of [...child.childNodes])this.insertBefore(item,before);return child;}if(child.parentNode)child.parentNode.removeChild(child);let i=before?this.childNodes.indexOf(before):-1;if(i<0)i=this.childNodes.length;this.childNodes.splice(i,0,child);child.parentNode=this;return child;}
  removeChild(child){const i=this.childNodes.indexOf(child);if(i<0)throw Error('Missing DOM child');this.childNodes.splice(i,1);child.parentNode=null;return child;}
  replaceChild(child,old){this.insertBefore(child,old);this.removeChild(old);return old;}
  replaceData(_offset,_count,value){this.data=String(value);this.nodeValue=this.data;}
  setAttribute(k,v){this.attributes[k]=String(v);}
  setAttributeNS(_ns,k,v){this.setAttribute(k,v);}
  getAttribute(k){return this.attributes[k]??null;}
  removeAttribute(k){delete this.attributes[k];}
  removeAttributeNS(_ns,k){this.removeAttribute(k);}
  addEventListener(k,fn){this.listeners[k]=fn;}
  removeEventListener(k,fn){if(this.listeners[k]===fn)delete this.listeners[k];}
  focus(){activeNode=this;focusLog.push(this.id??this.attributes.id??null);this.focused=true;this.focusCount=(this.focusCount??0)+1;}
}
function walk(node,predicate){if(predicate(node))return node;for(const child of node.childNodes){const found=walk(child,predicate);if(found)return found;}return null;}
function domWitness(node){return {tag:node.tagName,id:node.id??node.attributes.id??null,attributes:node.attributes,disabled:node.disabled??false,listeners:Object.keys(node.listeners),children:node.childNodes.map(domWitness)};}
function harness(file,name,flags=null){
  const requests=[],messages=[],timers=new Map();let sequence=0;
  class XHR {
    constructor(){this.handlers={};this.upload={handlers:{},addEventListener(kind,handler){this.handlers[kind]=handler;}};this.headers={};this.aborted=false;this.done=false;this.abortCount=0;}
    addEventListener(kind,handler){this.handlers[kind]=handler;}
    open(method,url,async){this.method=method;this.url=url;this.async=async;}
    setRequestHeader(key,value){this.headers[key]=value;}
    getAllResponseHeaders(){return 'Content-Type: application/json\r\n';}
    send(body){this.body=body??'';requests.push(this);report.trace.push({root:name,method:this.method,url:this.url,headers:this.headers,bytes:Buffer.byteLength(this.body),sha256:hash(this.body)});}
    abort(){this.aborted=true;this.abortCount++;}
    respond(status,body='',late=false){if(!late&&(this.done||this.aborted))throw Error('Response to inactive XHR');this.done=true;this.status=status;this.statusText=String(status);this.response=body;this.responseURL='http://127.0.0.1:41001'+this.url;this.handlers.load();}
    fail(kind){if(this.done||this.aborted)throw Error('Failure to inactive XHR');this.done=true;this.handlers[kind]();}
  }
  const later=(fn,delay=0)=>{const id=++sequence;timers.set(id,{fn,delay});return id;};
  const cancel=id=>timers.delete(id);
  const container=new Node(1,'DIV'),mount=new Node(3,'#text','');container.appendChild(mount);
  const document={body:container,documentElement:container,createTextNode:text=>new Node(3,'#text',String(text)),createElement:tag=>new Node(1,tag.toUpperCase()),createElementNS:(_ns,tag)=>new Node(1,tag.toUpperCase()),createDocumentFragment:()=>new Node(11,'#document-fragment'),addEventListener(){},removeEventListener(){},getElementById:id=>walk(container,n=>(n.id??n.attributes.id)===id)};
  const window={document,addEventListener(){},removeEventListener(){},requestAnimationFrame:fn=>later(fn,0),cancelAnimationFrame:cancel};
  const sandbox={console,document,window,XMLHttpRequest:XHR,setTimeout:later,clearTimeout:cancel,requestAnimationFrame:window.requestAnimationFrame,cancelAnimationFrame:cancel};
  vm.createContext(sandbox);vm.runInContext(compiledSource(file),sandbox,{timeout:2000});
  const app=sandbox.Elm[name].init({node:mount,flags});
  if(app.ports?.outgoing)app.ports.outgoing.subscribe(value=>messages.push(JSON.parse(JSON.stringify(value))));
  const env={requests,messages,container,app,
    async flush(){for(let round=0;round<12;round++){for(const [id,row]of [...timers])if(row.delay<=0){timers.delete(id);row.fn();}await new Promise(resolve=>setImmediate(resolve));}},
    async tick(milliseconds){for(const [id,row]of [...timers])if(row.delay<=milliseconds){timers.delete(id);row.fn();}await this.flush();},
    gets(){return requests.filter(r=>r.method==='GET');},posts(){return requests.filter(r=>r.method==='POST');},
    get(){return requests.find(r=>r.method==='GET'&&!r.done&&!r.aborted);},
    latest(){return messages.at(-1);},
    async send(value){app.ports.incoming.send(value);await bounded('worker reply',this.flush());},
    async event(value){const request=this.get();need(name+' actual pending GET before controlled event',Boolean(request),request?undefined:{alert:walk(container,node=>node.attributes?.role==='alert')?.textContent??null,requests:requests.map(row=>({method:row.method,url:row.url,done:row.done,aborted:row.aborted}))});request.respond(200,JSON.stringify(value));await this.flush();},
    close(){timers.clear();for(const request of requests)if(!request.done&&!request.aborted)request.abort();}
  };
  environments.push(env);return env;
}


const CASE_NAMES=["group-context-menu","group-shift-f10","pin-context-menu","pin-shift-f10","nested-label-bubbles-to-group","current-publication-wire","current-lease-wire","closed-bar-zero-lease","full-width-counter-wire","ordinary-click-preserved","disabled-group-refused","disabled-pin-refused","utility-control-refused","plain-f10-preserved","shift-context-menu-preserved","ctrl-context-menu-preserved","alt-context-menu-preserved","meta-context-menu-preserved","ctrl-shift-f10-preserved","alt-shift-f10-preserved","meta-shift-f10-preserved","composition-preserved","ime229-preserved","repeat-refused","return-preserved","stale-publication-refused","stale-lease-refused","removed-group-old-callback-refused","disabled-successor-old-callback-refused","foreign-role-stopped-old-callback-refused","transport-error-stopped-old-callback-refused","post-failure-never-replays-context","popup-only-group-not-a-bar-target","seeded-keyboard-admission-property"];
const gateway=(kind,payload)=>({bridgeProtocol:1,kind,payload});
const group='bar:group:application:documents',pin='bar:pin:org.example.Editor';
const row=(id,enabled=true,domId=id)=>({id,domId,label:id,ariaLabel:id,detail:'',enabled});
const rows=()=>[row(group),row(pin),row('bar:applications')];
const frame=(items=rows(),publication='7',lease='1')=>({surfaceProtocol:2,publication,lease,mode:'closed',status:'Ready',bar:items,popup:[]});
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const canonical=value=>Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])):value;
const exact=(a,b)=>equal(canonical(a),canonical(b));
function control(env,id){return walk(env.container,n=>n.attributes['data-surface-control']===id);}
function bar(env){return walk(env.container,n=>(n.className??n.attributes.class??'').split(' ').includes('surface-bar'));}
function activate(node){need('rendered control exists',!!node);node.focus();focusLog.length=0;}
function dispatch(target,options={}){
 const event={type:'keydown',key:'ContextMenu',code:'ContextMenu',keyCode:93,which:93,shiftKey:false,ctrlKey:false,altKey:false,metaKey:false,isComposing:false,repeat:false,target,currentTarget:target,defaultPrevented:false,cancelBubble:false,
  preventDefault(){this.defaultPrevented=true;},stopPropagation(){this.cancelBubble=true;},...options};
 for(let node=target;node;node=node.parentNode){event.currentTarget=node;const callback=node.listeners.keydown;if(callback)callback(event);if(event.cancelBubble)break;}
 return event;
}
const shiftF10={key:'F10',code:'F10',keyCode:121,which:121,shiftKey:true};
async function setup(shown=frame()){
 activeNode=null;focusLog.length=0;const env=harness(image,'HttpBar');await env.flush();
 need('HttpBar has no authored action port',!env.app.ports);await env.event(gateway('presentation',shown));
 need('actual bar root rendered',!!bar(env),domWitness(env.container));return env;
}
async function run(name,body){const before=report.failures.length;try{await body();report.cases.push({name,passed:report.failures.length===before});}catch(error){check(name+' completed',false,String(error.stack??error));report.cases.push({name,passed:false});}finally{for(const e of environments)e.close();}}
function witness(env){return env.posts().map(x=>({url:x.url,body:x.body,aborted:x.aborted}));}
function expected(id,publication='7',lease='1'){return {surfaceProtocol:2,kind:'surface-context',surface:'bar',publication,lease,id,trigger:'keyboard',x:0,y:0};}
function noMutation(env,label){check(label+' emits no POST',env.posts().length===0,witness(env));check(label+' does not change local focus',focusLog.length===0,focusLog);}
async function positive(name,id,options={},shown=frame(),nested=false){
 await run(name,async()=>{
  const env=await setup(shown),button=control(env,id);activate(button);
  const target=nested?walk(button,n=>(n.className??n.attributes.class??'').split(' ').includes('control-label')):button;
  need('actual event target exists',!!target);const event=dispatch(target,options);await env.flush();
  check(name+' handles native context-menu default',event.defaultPrevented);
  check(name+' emits exactly one context POST',env.posts().length===1,witness(env));
  const post=env.posts()[0];
  check(name+' exact current keyboard wire',!!post&&post.url==='/actions'&&exact(JSON.parse(post.body),expected(id,shown.publication,shown.lease)),witness(env));
  check(name+' emits no click action or commit',env.posts().every(p=>p.url==='/actions'&&JSON.parse(p.body).kind==='surface-context'),witness(env));
  check(name+' does not move local focus',focusLog.length===0,focusLog);
  if(post){post.respond(204);await env.flush();check(name+' completion never replays',env.posts().length===1,witness(env));}
 });
}
async function negative(name,id,options={},shown=frame()){
 await run(name,async()=>{const env=await setup(shown),button=control(env,id);activate(button);const event=dispatch(button,options);await env.flush();check(name+' preserves default',!event.defaultPrevented);noMutation(env,name);});
}
(async()=>{
 await positive('group-context-menu',group);
 await positive('group-shift-f10',group,shiftF10);
 await positive('pin-context-menu',pin);
 await positive('pin-shift-f10',pin,shiftF10);
 await positive('nested-label-bubbles-to-group',group,{},frame(),true);
 await positive('current-publication-wire',group,{},frame(rows(),'19','1'));
 await positive('current-lease-wire',pin,shiftF10,frame(rows(),'19','4'));
 await positive('closed-bar-zero-lease',group,{},frame(rows(),'7','0'));
 await positive('full-width-counter-wire',pin,shiftF10,frame(rows(),'18446744073709551615','18446744073709551615'));
 await run('ordinary-click-preserved',async()=>{
  const env=await setup(),button=control(env,group);activate(button);need('ordinary click handler exists',typeof button.listeners.click==='function');
  button.listeners.click({type:'click',target:button,currentTarget:button,stopPropagation(){},preventDefault(){}});await env.flush();
  check('ordinary click remains exact surface-action',env.posts().length===1&&env.posts()[0].url==='/actions'&&exact(JSON.parse(env.posts()[0].body),{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:'7',lease:'1',id:group}),witness(env));
 });
 await negative('disabled-group-refused',group,{},frame([row(group,false),row(pin)]));
 await negative('disabled-pin-refused',pin,shiftF10,frame([row(group),row(pin,false)]));
 await negative('utility-control-refused','bar:applications');
 for(const [name,options] of [
  ['plain-f10-preserved',{...shiftF10,shiftKey:false}],['shift-context-menu-preserved',{shiftKey:true}],
  ['ctrl-context-menu-preserved',{ctrlKey:true}],['alt-context-menu-preserved',{altKey:true}],['meta-context-menu-preserved',{metaKey:true}],
  ['ctrl-shift-f10-preserved',{...shiftF10,ctrlKey:true}],['alt-shift-f10-preserved',{...shiftF10,altKey:true}],['meta-shift-f10-preserved',{...shiftF10,metaKey:true}],
  ['composition-preserved',{isComposing:true}],['ime229-preserved',{keyCode:229,which:229}],['repeat-refused',{repeat:true}],
  ['return-preserved',{key:'Enter',code:'Enter',keyCode:13,which:13}]
 ])await negative(name,group,options);
 for(const [name,next]of [
  ['stale-publication-refused',frame(rows(),'9','1')],['stale-lease-refused',frame(rows(),'9','2')],
  ['removed-group-old-callback-refused',null],['disabled-successor-old-callback-refused',frame([row(group,false),row(pin)],'9','1')]
 ])await run(name,async()=>{
  const env=await setup(),button=control(env,group);activate(button);
  // Retire the old keyed node through the real GET/update/render route first.
  // Reusing a keyed node can update its listener; this detached node is not reused.
  await env.event(gateway('presentation',frame([row(pin)],'8',next?.lease??'1')));
  need('old keyed group is actually detached',button.parentNode===null&&!control(env,group),domWitness(env.container));
  if(next){await env.event(gateway('presentation',next));need('successor node is distinct from retained old node',control(env,group)!==button&&!!control(env,group));}
  dispatch(button);await env.flush();noMutation(env,name);
 });
 for(const how of ['foreign-role','transport-error'])await run(how+'-stopped-old-callback-refused',async()=>{
  const env=await setup(),button=control(env,group);activate(button);const get=env.get();need('pending actual GET exists',!!get);
  if(how==='foreign-role')get.respond(200,JSON.stringify(gateway('native-event',{})));else get.fail('error');
  await env.flush();need('actual HttpBar transport alert rendered',!!walk(env.container,n=>n.attributes.role==='alert'),domWitness(env.container));
  dispatch(button);await env.flush();await env.tick(10000);noMutation(env,how);
 });
 await run('post-failure-never-replays-context',async()=>{
  const env=await setup(),button=control(env,group);activate(button);dispatch(button);await env.flush();
  const first=env.posts()[0];check('one first context POST before transport failure',env.posts().length===1,witness(env));
  if(!first)return;
  check('first body is exact keyboard context',exact(JSON.parse(first.body),expected(group)),first.body);
  first.fail('error');await env.flush();need('POST failure stopped HttpBar',!!walk(env.container,n=>n.attributes.role==='alert'),domWitness(env.container));
  dispatch(button);await env.flush();await env.tick(10000);
  check('failed POST and stale callback never replay',env.posts().length===1,witness(env));
 });
 await run('popup-only-group-not-a-bar-target',async()=>{
  const shown={...frame([]),'mode':'menu','popup':[row(group)]};const env=await setup(shown);
  need('popup-only control is not rendered by HttpBar',!control(env,group));dispatch(bar(env));await env.flush();noMutation(env,'popup-only');
 });
 await run('seeded-keyboard-admission-property',async()=>{
  const seeds=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31];
  report.seededKeyboard={algorithm:'xorshift32',seeds,sampleCount:0,samples:[]};
  for(const seed of seeds){
   let state=(seed+1)>>>0;
   const next=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;};
   const kind=next()%4,id=next()%2===0?group:pin;
   const publication=String(1+next()%65535),lease=String(next()%65536);
   const key=['ContextMenu','F10','Enter','Tab'][kind];
   const eventFields={key,code:key,keyCode:next()%4===0?229:({ContextMenu:93,F10:121,Enter:13,Tab:9}[key]),shiftKey:(next()&1)===1,ctrlKey:next()%4===0,altKey:next()%4===0,metaKey:next()%4===0,isComposing:next()%4===0,repeat:next()%4===0};
   // Four stratified positive witnesses prevent an all-refusal seed campaign.
   // All remaining samples retain generated fields; no production predicate is called.
   if(seed%8===0)Object.assign(eventFields,{key:seed%16===0?'ContextMenu':'F10',code:seed%16===0?'ContextMenu':'F10',keyCode:seed%16===0?93:121,shiftKey:seed%16!==0,ctrlKey:false,altKey:false,metaKey:false,isComposing:false,repeat:false});
   eventFields.which=eventFields.keyCode;
   const allowed=!eventFields.ctrlKey&&!eventFields.altKey&&!eventFields.metaKey&&!eventFields.isComposing&&eventFields.keyCode!==229&&!eventFields.repeat&&((eventFields.key==='ContextMenu'&&!eventFields.shiftKey)||(eventFields.key==='F10'&&eventFields.shiftKey));
   const env=await setup(frame(rows(),publication,lease)),button=control(env,id);activate(button);
   const event=dispatch(button,eventFields);await env.flush();
   const actual=witness(env),wanted=expected(id,publication,lease);
   check('seed '+seed+' exact admission',allowed?env.posts().length===1&&env.posts()[0].url==='/actions'&&exact(JSON.parse(env.posts()[0].body),wanted):env.posts().length===0,{eventFields,allowed,actual});
   check('seed '+seed+' default handling matches admission',event.defaultPrevented===allowed,{eventFields,allowed,defaultPrevented:event.defaultPrevented});
   check('seed '+seed+' never activates or moves focus',focusLog.length===0&&env.posts().every(post=>post.url==='/actions'&&JSON.parse(post.body).kind==='surface-context'),{focusLog,actual});
   report.seededKeyboard.samples.push({seed,event:eventFields,id,publication,lease,allowed,defaultPrevented:event.defaultPrevented,posts:actual});report.seededKeyboard.sampleCount++;
   env.close();
  }
  check('exact32 reproducible keyboard samples',report.seededKeyboard.sampleCount===32);
 });
 report.inventoryMatches=exact(report.cases.map(x=>x.name),CASE_NAMES);
 report.passed=report.inventoryMatches&&report.cases.every(x=>x.passed)&&report.failures.length===0;
 report.classification=report.setupFailures?'fixture-setup-failed':!report.inventoryMatches?'fixture-inventory-failed':report.passed?'component-pass':'semantic-red';
 report.limits=['Synthetic DOM keyboard events delivered to actual compiled HttpBar callbacks; not native WebKit input.','Controlled GET presentations establish component GIVEN state; they do not authenticate a taskbar provider.','Actual POST requests are observed only; no backend/window effect is executed.','Keyboard coordinates are fixed0/0 and confer no pointer-position claim.','FocusOnly Bar controls are forbidden by existing snapshot decoder; disabled rows are not made focusOnly here.','Old callbacks after HTTP failure remain stopped; no model state is injected.','No service, native readiness, original scenario or release acceptance.'];
})().catch(error=>{report.classification='fixture-execution-failed';report.failures.push({name:'harness terminal',witness:String(error.stack??error)});}).finally(()=>{for(const env of environments)env.close();fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.exitCode=report.passed?0:1;});
