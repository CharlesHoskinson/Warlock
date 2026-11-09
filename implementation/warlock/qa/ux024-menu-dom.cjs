"use strict";
// Uninstrumented compiled HttpPopup; controlled DOM/XHR component only.
// No simulated default Tab movement: only the production event handler can focus.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const [image,output]=process.argv.slice(2);
if(process.argv.length!==4)throw Error('Expected explicit compiled HttpPopup.js-or-html and NEW report.json');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const report={schema:1,passed:false,scope:'UX024 live menu popup DOM component',nativeAcceptance:false,originalAccepted:false,checks:[],failures:[],trace:[],cases:[],artifactHashes:{image:hash(fs.readFileSync(image)),harness:hash(fs.readFileSync(__filename))}};
function check(name,ok,witness){const row={name,passed:!!ok};if(!ok)row.witness=witness??null;report.checks.push(row);if(!ok)report.failures.push(row);}
function need(name,ok,witness){check(name,ok,witness);if(!ok)throw Error(name);}
function compiledSource(file){const raw=fs.readFileSync(file,'utf8');if(!raw.trimStart().startsWith('<'))return raw;
 const scripts=[...raw.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m=>m[1]);
 const selected=scripts.filter(s=>s.includes('_Platform_export')&&s.includes('HttpPopup'));
 if(selected.length!==1)throw Error('Expected exactly one uninstrumented Elm HttpPopup script');
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

const gateway=(kind,payload)=>({bridgeProtocol:1,kind,payload});
const row=(id,enabled=true,domId=id)=>({id,domId,label:id,ariaLabel:id,detail:'',enabled});
const rows=()=>[row('control:menu-close'),row('menu:disabled',false),row('menu:first'),row('menu:last')];
const frame=(items=rows(),publication='7',lease='1',mode='menu')=>({surfaceProtocol:2,publication,lease,mode,status:'Ready',bar:[],popup:items});
function control(env,id){return walk(env.container,n=>n.attributes['data-surface-control']===id||n.attributes['data-surface-field']===id);}
function popup(env){return walk(env.container,n=>(n.className??n.attributes.class??'').split(' ').includes('surface-popup'));}
function activate(node){if(!node)throw Error('Expected rendered control');node.focus();focusLog.length=0;}
function dispatch(target,options={}){
 const event={type:'keydown',key:'Tab',code:'Tab',keyCode:9,which:9,shiftKey:false,ctrlKey:false,altKey:false,metaKey:false,isComposing:false,repeat:false,target,currentTarget:target,defaultPrevented:false,cancelBubble:false,
  preventDefault(){this.defaultPrevented=true;},stopPropagation(){this.cancelBubble=true;},...options};
 for(let node=target;node;node=node.parentNode){event.currentTarget=node;const callback=node.listeners.keydown;if(callback)callback(event);if(event.cancelBubble)break;}
 return event;
}
async function setup(shown=frame()){activeNode=null;focusLog.length=0;const env=harness(image,'HttpPopup');await env.flush();await env.event(gateway('presentation',shown));need('real menu root rendered',!!popup(env),domWitness(env.container));return env;}
async function run(name,body){const before=report.failures.length;try{await body();report.cases.push({name,passed:report.failures.length===before});}catch(error){check(name+' completed',false,String(error.stack??error));report.cases.push({name,passed:false});}finally{for(const e of environments)e.close();}}
function noRequests(env,name){check(name+' sends no HTTP mutation',env.posts().length===0,env.posts().map(x=>({url:x.url,body:x.body})));}
async function traverse(name,from,to,shift=false,items=rows()){
 await run(name,async()=>{const env=await setup(frame(items)),start=control(env,from),expected=control(env,to);activate(start);const event=dispatch(start,{shiftKey:shift});await env.flush();
 check(name+' prevents browser escape',event.defaultPrevented);check(name+' actual DOM focus target',activeNode===expected&&focusLog.length===1,{focusLog,active:activeNode?.id,expected:expected?.id});noRequests(env,name);});
}
(async()=>{
 await traverse('Tab follows menu DOM order and skips disabled','control:menu-close','menu:first');
 await traverse('Tab moves to next menu control','menu:first','menu:last');
 await traverse('Tab wraps last to first','menu:last','control:menu-close');
 await traverse('Shift Tab wraps first to last','control:menu-close','menu:last',true);
 await traverse('Shift Tab skips disabled','menu:first','control:menu-close',true);
 await traverse('One enabled control contains Tab','control:menu-close','control:menu-close',false,[row('control:menu-close')]);
 await traverse('One enabled control contains Shift Tab','control:menu-close','control:menu-close',true,[row('control:menu-close')]);
 await traverse('Escaped DOM identity uses existing mapping','menu:first','menu:last',false,[row('menu:first'),row('menu:last',true,'surface-control-tail')]);
 for(const [name,patch] of [['composition',{isComposing:true}],['IME229',{keyCode:229,which:229}],['Control Tab',{ctrlKey:true}],['Alt Tab',{altKey:true}],['Meta Tab',{metaKey:true}],['Escape native route',{key:'Escape',code:'Escape',keyCode:27,which:27}]]){
  await run(name+' preserved',async()=>{const env=await setup(),start=control(env,'menu:last');activate(start);const event=dispatch(start,patch);await env.flush();check(name+' is not consumed',!event.defaultPrevented);check(name+' has no local focus change',activeNode===start&&focusLog.length===0,focusLog);noRequests(env,name);});
 }
 await run('Empty menu invents no focus target',async()=>{const env=await setup(frame([]));focusLog.length=0;dispatch(popup(env));await env.flush();check('empty focus remains absent',focusLog.length===0,focusLog);noRequests(env,'empty');});
 await run('All-disabled menu invents no focus target',async()=>{const env=await setup(frame([row('menu:disabled',false)]));focusLog.length=0;dispatch(popup(env));await env.flush();check('disabled focus remains absent',focusLog.length===0,focusLog);noRequests(env,'disabled');});
 for(const [name,next] of [['stale publication',frame(rows(),'8','1')],['retired lease',frame(rows(),'8','2')]]){
  await run(name+' old DOM callback refused',async()=>{const env=await setup(),start=control(env,'menu:last');activate(start);
   // Deliver current model BEFORE the scheduled DOM animation frame. This keeps
   // the actual old generated callback, without fabricating Elm model values.
   env.get().respond(200,JSON.stringify(gateway('presentation',next)));await new Promise(resolve=>setImmediate(resolve));
   dispatch(start);await env.flush();check(name+' cannot move focus from old callback',focusLog.length===0,focusLog);noRequests(env,name);});
 }
 report.passed=report.cases.length===18&&report.cases.every(x=>x.passed)&&report.failures.length===0;
 report.limits=['Controlled DOM/XHR and synthetic keyboard events, not actual WebKit or native input.','No browser-default Tab policy is implemented by the harness.','Only live menu order is the proposed behavior; no generic popup traversal assertion.','Escape is passed through only; actual eligible opener return is not established.','No service, backend effect, original scenario or release acceptance.'];
})().catch(error=>{report.failures.push({name:'harness terminal',witness:String(error.stack??error)});}).finally(()=>{for(const env of environments)env.close();fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});process.exitCode=report.passed?0:1;});
