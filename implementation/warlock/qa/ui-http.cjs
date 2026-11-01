'use strict';
// Generated Elm + its real HTTP kernel. DOM/XHR are controlled test doubles;
// this is transport/component evidence, never a WebKit/CSP/native certificate.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const {isDeepStrictEqual:equal}=require('node:util');
const [mainFile,barFile,popupFile,replayFile,reportFile]=process.argv.slice(2);
if(process.argv.length!==7) throw Error('Expected HTTP_MAIN.js HTTP_BAR.js HTTP_POPUP.js REPLAY.js REPORT.json');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const report={schema:1,passed:false,nativeAcceptance:false,guiAcceptance:false,cspExecutionAcceptance:false,releaseAccepted:false,seed:20261101,seedCount:32,checks:[],failures:[],trace:[],artifactHashes:{}};
for(const [name,file] of Object.entries({main:mainFile,bar:barFile,popup:popupFile,replay:replayFile,harness:__filename}))report.artifactHashes[name]=hash(fs.readFileSync(file));
function check(name,ok,witness){const row={name,passed:Boolean(ok)};if(!ok)row.witness=witness??null;report.checks.push(row);if(!ok)report.failures.push(row);}
function need(name,ok,witness){check(name,ok,witness);if(!ok)throw Error(name);}
function save(){fs.writeFileSync(reportFile,JSON.stringify(report,null,2)+'\n');}
const environments=[];

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
  focus(){this.focused=true;this.focusCount=(this.focusCount??0)+1;}
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
  vm.createContext(sandbox);vm.runInContext(fs.readFileSync(file,'utf8'),sandbox,{timeout:2000});
  const app=sandbox.Elm[name].init({node:mount,flags});
  if(app.ports?.outgoing)app.ports.outgoing.subscribe(value=>messages.push(JSON.parse(JSON.stringify(value))));
  const env={requests,messages,container,app,
    async flush(){for(let round=0;round<12;round++){for(const [id,row]of [...timers])if(row.delay<=0){timers.delete(id);row.fn();}await new Promise(resolve=>setImmediate(resolve));}},
    async tick(milliseconds){for(const [id,row]of [...timers])if(row.delay<=milliseconds){timers.delete(id);row.fn();}await this.flush();},
    gets(){return requests.filter(r=>r.method==='GET');},posts(){return requests.filter(r=>r.method==='POST');},
    get(){return requests.find(r=>r.method==='GET'&&!r.done&&!r.aborted);},
    latest(){return messages.at(-1);},
    async send(value){app.ports.incoming.send(value);await this.flush();},
    async event(value){const request=this.get();need(name+' actual pending GET before controlled event',Boolean(request));request.respond(200,JSON.stringify(value));await this.flush();},
    close(){timers.clear();for(const request of requests)if(!request.done&&!request.aborted)request.abort();}
  };
  environments.push(env);return env;
}
const gateway=(kind,payload)=>({bridgeProtocol:1,kind,payload});
const binding={lifetime:'9007199254741001',session:'9007199254741103',frontend:'9007199254741207'};
const topology={viewProtocol:2,kind:'view-topology',revision:'1',views:[{id:'1',generation:'1'}],locations:[{scope:{id:'1',generation:'1'},box:[0,0,800,600]}]};
const initialGateway=gateway('native-event',{protocolVersion:3,kind:'attached',binding});
async function worker(renderer){const env=harness(replayFile,'UiHttpReplay',{renderer});await env.flush();need('worker actual GET reachable',env.gets().length===1);return env;}
function headerCheck(label,request){check(label+' required nonsimple header',request?.headers['X-Warlock-Api']==='1',request?.headers);check(label+' fixed original HTTP timeout',request?.timeout===5000,request?.timeout);check(label+' local relative route',request?.url==='/events'||request?.url==='/commit'||request?.url==='/actions',request?.url);}
async function enqueue(env,value){await env.send({kind:'enqueue',value});}

async function roots(){
  const main=harness(mainFile,'HttpMain');await main.flush();
  need('HttpMain has no authored port transport',!main.app.ports,Object.keys(main.app.ports??{}));
  need('HttpMain initial exact GET route',main.gets().length===1&&main.get().url==='/events');headerCheck('HttpMain GET',main.get());
  await main.event(gateway('view-topology',topology));
  need('HttpMain produces actual whole commit',main.posts().length===1,main.requests.map(x=>x.url));
  const first=JSON.parse(main.posts()[0].body);
  check('HttpMain preserves complete five-field view commit',equal(Object.keys(first).sort(),['focus','kind','projection','requests','viewProtocol'])&&first.viewProtocol===1&&first.kind==='view-commit',first);
  check('HttpMain does not extract requests into RPC',typeof first.projection==='object'&&Array.isArray(first.requests)&&Array.isArray(first.focus));
  headerCheck('HttpMain POST',main.posts()[0]);check('HttpMain uses only commit endpoint',main.posts()[0].url==='/commit');
  main.posts()[0].respond(204);await main.flush();check('HttpMain HTTP204 invents no new policy message',main.posts().length===1);
  main.close();
  const control=(id,domId,label)=>({id,domId,label,ariaLabel:label,detail:'',enabled:true});
  const frame={surfaceProtocol:2,publication:'1',lease:'1',mode:'applications',status:'Ready',bar:[control('bar:applications','open-applications','Applications')],popup:[control('control:refresh','refresh-applications','Refresh')]};
  for(const [file,name,popup]of [[barFile,'HttpBar',false],[popupFile,'HttpPopup',true]]){
    const env=harness(file,name);await env.flush();need(name+' no authored port transport',!env.app.ports);headerCheck(name+' GET',env.get());
    await env.event(gateway('presentation',frame));
    const identity=popup?'control:refresh':'bar:applications';
    const button=walk(env.container,node=>node.attributes['data-surface-control']===identity);
    need(name+' actual Elm enabled control painted in DOM test double',button&&typeof button.listeners.click==='function',{text:env.container.textContent,matchedControl:button?domWitness(button):null,tree:domWitness(env.container)});
    button.listeners.click({type:'click',target:button,currentTarget:button,stopPropagation(){},preventDefault(){}});await env.flush();
    need(name+' actual Elm DOM callback reaches one HTTP POST',env.posts().length===1,env.requests.map(x=>x.url));
    const action=JSON.parse(env.posts()[0].body);
    check(name+' exact typed action provenance',equal(action,{surfaceProtocol:2,kind:'surface-action',surface:popup?'popup':'bar',publication:'1',lease:'1',id:identity}),action);
    check(name+' only actions endpoint',env.posts()[0].url==='/actions');headerCheck(name+' POST',env.posts()[0]);
    env.posts()[0].respond(204);await env.flush();check(name+' delivery completion does not replay action',env.posts().length===1);
    await env.event(initialGateway);check(name+' native source rejected visibly',env.container.textContent.includes('source is not allowed'));check(name+' rejected role cannot emit privileged POST',env.posts().length===1);env.close();
  }
}

async function fifo(){
  let state=20261101;
  for(let seed=0;seed<32;seed++){
    state=(Math.imul(state,1664525)+1013904223)>>>0;
    const count=2+state%13;
    for(const renderer of [false,true]){
      const env=await worker(renderer),label=`seed${seed}/${renderer?'renderer':'controller'}`;
      const expected=Array.from({length:count},(_,sequence)=>({seed,sequence,text:'λ🙂-'+state}));
      for(const value of expected)await enqueue(env,value);
      need(label+' one active POST with queued successors',env.posts().length===1&&env.latest().problem===null);
      for(let index=0;index<count;index++){
        need(label+' next request reachable '+index,env.posts().length===index+1);
        const request=env.posts()[index];
        check(label+' FIFO exact payload '+index,equal(JSON.parse(request.body),expected[index]));
        check(label+' static route '+index,request.url===(renderer?'/actions':'/commit'));
        headerCheck(label+' POST'+index,request);
        request.respond(204);await env.flush();
      }
      check(label+' no duplicate after drained queue',env.posts().length===count&&env.latest().problem===null);
      check(label+' positive delivery never Incoming/Lost',env.messages.every(x=>x.event===null));
      env.close();
    }
  }
}

async function focusRoutes(){
  const control=(id,domId,label,enabled=true)=>({id,domId,label,ariaLabel:label||'Search applications',detail:'',enabled});
  for(const [file,name,popup]of [[barFile,'HttpBar',false],[popupFile,'HttpPopup',true]]){
    const env=harness(file,name);await env.flush();
    let frame={surfaceProtocol:2,publication:'1',lease:'1',mode:'applications',status:'Ready',bar:[control('bar:applications','bar-focus','Applications')],popup:[control('control:search','query-focus',''),control('control:refresh','popup-focus','Refresh')]};
    await env.event(gateway('presentation',frame));
    const domId=popup?'popup-focus':'bar-focus';
    const instruction={focusProtocol:1,kind:'focus',surface:popup?'popup':'bar',publication:'1',lease:'1',domId};
    const target=walk(env.container,node=>(node.id??node.attributes.id)===domId);
    need(name+' focus positive actual DOM target exists',Boolean(target));
    await env.event(gateway('focus',instruction));
    check(name+' accepted exact current focus executes actual Browser.Dom command',target.focusCount===1,target.focusCount);
    check(name+' focus completion does not POST acknowledgement',env.posts().length===0);
    for(const [label,patch]of [['publication',{publication:'2'}],['lease',{lease:'2'}],['surface',{surface:popup?'bar':'popup'}],['foreign target',{domId:'outside-current-frame'}],['version',{focusProtocol:2}],['kind',{kind:'native-focus'}],['extra',{unexpected:true}],['noncanonical counter',{publication:'01'}],['target bound',{domId:'x'.repeat(1025)}]]){
      await env.event(gateway('focus',{...instruction,...patch}));
      check(name+' rejects focus '+label,target.focusCount===1&&env.posts().length===0,{count:target.focusCount,posts:env.posts().length});
    }
    if(popup){
      const input=walk(env.container,node=>(node.id??node.attributes.id)==='query-focus');
      need(name+' real composition callback present',typeof input?.listeners.compositionstart==='function');
      input.value='';input.listeners.compositionstart({target:input,currentTarget:input,isComposing:true});await env.flush();
      await env.event(gateway('focus',instruction));
      check(name+' active IME preedit not interrupted by remote focus',target.focusCount===1&&env.posts().length===0);
      input.listeners.compositionend({target:input,currentTarget:input,isComposing:false});await env.flush();
      await env.event(gateway('focus',instruction));
      check(name+' completed unchanged composition permits fresh focus',target.focusCount===2&&env.posts().length===0);
    }
    frame={...frame,publication:'2',bar:frame.bar.map(row=>({...row,enabled:false})),popup:frame.popup.map(row=>({...row,enabled:false}))};
    await env.event(gateway('presentation',frame));
    const disabledTarget=walk(env.container,node=>(node.id??node.attributes.id)===domId),before=disabledTarget.focusCount??0;
    await env.event(gateway('focus',{...instruction,publication:'2'}));
    check(name+' disabled current target refused',(disabledTarget.focusCount??0)===before);
    if(popup){
      frame={...frame,publication:'3',mode:'notifications',popup:[{...control('notifications:item','focus-only','Notification',false),focusOnly:true}]};
      await env.event(gateway('presentation',frame));
      const focusOnly=walk(env.container,node=>(node.id??node.attributes.id)==='focus-only');
      need(name+' focusOnly current target actually painted',Boolean(focusOnly));
      await env.event(gateway('focus',{...instruction,publication:'3',domId:'focus-only'}));
      check(name+' focusOnly current target admitted',focusOnly.focusCount===1);
    }
    check(name+' all focus routes invent no delivery or native ACK',env.posts().length===0);env.close();
  }
}

async function rendererSeedRoutes(){
  for(let seed=0;seed<32;seed++)for(const [file,name,popup]of [[barFile,'HttpBar',false],[popupFile,'HttpPopup',true]]){
    const env=harness(file,name);await env.flush();
    const publication=String(9007199254742001n+BigInt(seed)),lease=String(9007199254743007n+BigInt(seed));
    const ids=[0,1].map(n=>(popup?'entry:':'bar:pin:')+seed+'-'+n);
    const rows=ids.map((id,n)=>({id,domId:'seed-'+seed+'-'+n,label:'λ🙂 '+seed+' '+n,ariaLabel:'Seed '+seed+' '+n,detail:'',enabled:true}));
    const frame={surfaceProtocol:2,publication,lease,mode:'applications',status:'Ready',bar:popup?[]:rows,popup:popup?rows:[]};
    await env.event(gateway('presentation',frame));
    for(const id of ids){
      const button=walk(env.container,n=>n.attributes['data-surface-control']===id);
      need(name+' seeded actual DOM control reachable '+seed+'/'+id,button&&typeof button.listeners.click==='function');
      button.listeners.click({type:'click',target:button,currentTarget:button,stopPropagation(){},preventDefault(){}});await env.flush();
    }
    need(name+' seeded actions keep one inflight POST '+seed,env.posts().length===1);
    for(let index=0;index<2;index++){
      need(name+' seeded FIFO action reachable '+seed+'/'+index,env.posts().length===index+1);
      const request=env.posts()[index],action=JSON.parse(request.body);
      check(name+' seeded exact scoped action '+seed+'/'+index,equal(action,{surfaceProtocol:2,kind:'surface-action',surface:popup?'popup':'bar',publication,lease,id:ids[index]}),action);
      check(name+' seeded static actions route '+seed+'/'+index,request.url==='/actions');headerCheck(name+' seeded POST '+seed+'/'+index,request);
      request.respond(204);await env.flush();
    }
    check(name+' seeded no completion replay '+seed,env.posts().length===2);env.close();
  }
}

async function capacities(){
  for(const renderer of [false,true]){
    const env=await worker(renderer);
    for(let n=0;n<16;n++)await enqueue(env,{n});
    check('capacity16 admits '+renderer,env.posts().length===1&&env.latest().problem===null);
    await enqueue(env,{n:16});
    check('capacity17 rejects '+renderer,typeof env.latest().problem==='string'&&env.latest().event?.kind==='lost',env.latest());
    check('capacity rejection cancels active GET/POST '+renderer,env.gets()[0].aborted&&env.posts()[0].aborted);
    const before=env.requests.length;await enqueue(env,{n:17});await env.tick(10000);
    check('capacity sticky failure never retries '+renderer,env.requests.length===before&&env.latest().event===null);
    env.posts()[0].respond(204,'',true);await env.flush();check('late204 cannot drain refused queue '+renderer,env.posts().length===1);env.close();
    const maximum=renderer?8192:131072;
    for(const [mode,offset,unicode,accepted]of [['exact',0,false,true],['over',1,false,false],['utf8-over',1,true,false]]){
      const boundary=await worker(renderer),overhead=Buffer.byteLength(JSON.stringify({padding:''}));
      const padding=unicode?'λ'.repeat(Math.floor((maximum-overhead)/2)+1):'x'.repeat(maximum-overhead+offset);
      const value={padding};await enqueue(boundary,value);
      check('actual request '+renderer+'/'+mode+' bytes precondition',unicode?JSON.stringify(value).length<maximum&&Buffer.byteLength(JSON.stringify(value))>maximum:Buffer.byteLength(JSON.stringify(value))===maximum+offset);
      check('actual request boundary '+renderer+'/'+mode,accepted?boundary.posts().length===1&&boundary.latest().problem===null:boundary.posts().length===0&&boundary.latest().event?.kind==='lost',boundary.latest());boundary.close();
    }
  }
}

async function failures(){
  for(const renderer of [false,true]){
    for(const failure of ['error','timeout']){
      const env=await worker(renderer);await enqueue(env,{a:1});await enqueue(env,{a:2});env.posts()[0].fail(failure);await env.flush();
      check('POST '+failure+' delivery remains unconfirmed '+renderer,env.latest().event?.kind==='lost'&&env.latest().problem.includes('unconfirmed'),env.latest());
      check('POST '+failure+' cancels GET '+renderer,env.gets()[0].aborted);
      await enqueue(env,{a:3});await env.tick(10000);check('POST '+failure+' never repeats '+renderer,env.posts().length===1);env.close();
    }
    for(const [status,body]of [[200,''],[201,''],[202,''],[204,'unexpected'],[205,''],[400,'']]){
      const env=await worker(renderer);await enqueue(env,{a:1});await enqueue(env,{a:2});env.posts()[0].respond(status,body);await env.flush();
      check('POST exact204 requirement '+renderer+'/'+status+'/'+body,Boolean(env.latest().problem)&&env.posts().length===1&&env.latest().event?.kind==='lost',env.latest());env.close();
    }
    for(const [status,body]of [[200,''],[201,JSON.stringify(gateway('presentation',{}))],[202,''],[204,'unexpected'],[205,''],[206,'{}'],[404,''],[500,'']]){
      const env=await worker(renderer);env.get().respond(status,body);await env.flush();
      check('GET exact200/204 requirement '+renderer+'/'+status+'/'+body.slice(0,8),Boolean(env.latest().problem)&&env.gets().length===1,env.latest());env.close();
    }
    const idle=await worker(renderer);idle.get().respond(204);await idle.flush();check('idle204 is not incoming '+renderer,idle.latest().problem===null&&idle.latest().event===null);check('idle has no immediate busy poll '+renderer,idle.gets().length===1);await idle.tick(99);check('idle respects spacing '+renderer,idle.gets().length===1);await idle.tick(100);check('idle starts one fresh GET '+renderer,idle.gets().length===2);headerCheck('idle next GET',idle.get());idle.close();
    for(const bad of ['not-json',JSON.stringify(null),JSON.stringify({bridgeProtocol:2,kind:'presentation',payload:{}}),JSON.stringify({bridgeProtocol:1,kind:'presentation',payload:{},extra:true}),JSON.stringify({bridgeProtocol:1,kind:'presentation'}),JSON.stringify(gateway(renderer?'native-event':'presentation',{})),JSON.stringify(gateway('unapproved',{}))]){
      const env=await worker(renderer);env.get().respond(200,bad);await env.flush();check('invalid or foreign-role gateway fails closed '+renderer+'/'+hash(bad).slice(0,8),Boolean(env.latest().problem)&&env.latest().event?.kind==='lost'&&env.gets().length===1,env.latest());env.close();
    }
    const valid=await worker(renderer),wire=gateway(renderer?'presentation':'native-event',{controlled:true});await valid.event(wire);check('matching role gateway positive '+renderer,valid.latest().event?.kind==='incoming'&&equal(valid.latest().event.value,wire)&&valid.gets().length===2&&valid.latest().problem===null,valid.latest());valid.close();
    const stopped=await worker(renderer);await enqueue(stopped,{n:1});await stopped.send({kind:'stop'});check('explicit stop cancels both active requests '+renderer,stopped.gets()[0].aborted&&stopped.posts()[0].aborted&&stopped.latest().event?.kind==='lost');const before=stopped.requests.length;await stopped.send({kind:'stop'});await enqueue(stopped,{n:2});await stopped.tick(10000);check('stop remains inert '+renderer,stopped.requests.length===before&&stopped.latest().event===null);stopped.close();
  }
  const limit=1048704;
  for(const [label,extra,utf8,accepted]of [['exact',0,false,true],['over',1,false,false],['utf8-over',1,true,false]]){
    const env=await worker(false),empty=gateway('native-event',{padding:''}),overhead=Buffer.byteLength(JSON.stringify(empty));
    empty.payload.padding=utf8?'λ'.repeat(Math.floor((limit-overhead)/2)+1):'x'.repeat(limit-overhead+extra);
    const wire=JSON.stringify(empty);need('event boundary '+label+' input',utf8?wire.length<limit&&Buffer.byteLength(wire)>limit:Buffer.byteLength(wire)===limit+extra);
    env.get().respond(200,wire);await env.flush();check('event byte bound '+label,accepted?env.latest().event?.kind==='incoming'&&env.latest().problem===null:env.latest().event?.kind==='lost'&&Boolean(env.latest().problem),env.latest()?.problem);env.close();
  }
}

// Controlled XHR interleavings: same compiled UiHttp and DesktopPolicy entry.
// Seeds determine literal wire IDs only; they do not model native provenance.
async function eventDuringDelivery(){
  const seedBase=20261101;
  for(let seed=0;seed<8;seed++)for(const renderer of [false,true]){
    const id=seedBase+seed,label=`event-during-delivery/${renderer?'renderer':'controller'}/${id}`;
    const first={seed:id,sequence:0},second={seed:id,sequence:1};
    // A role-valid unmatched disposition reaches the real policy without
    // creating a domain publication. A malformed native envelope legitimately
    // publishes refusal feedback; that is not an HTTP replay.
    const allowed=renderer ? gateway('presentation',{controlled:true,seed:id})
      : gateway('view-disposition',{viewProtocol:1,kind:'batch-disposition',disposition:'admitted',scope:{id:'1',generation:'1'},revision:'1',publication:'1',lease:'1',binding,batch:'{}'});
    const hostile=[
      ['malformed','{'],
      ['foreign-role',JSON.stringify(gateway(renderer?'native-event':'presentation',{seed:id}))],
      ['extra-field',JSON.stringify({...allowed,extra:true})],
      ['wrong-version',JSON.stringify({...allowed,bridgeProtocol:2})]
    ];
    for(const [kind,wire] of hostile){
      const env=await worker(renderer);
      await enqueue(env,first);await enqueue(env,second);
      need(label+'/'+kind+' one exact active POST',env.posts().length===1&&equal(JSON.parse(env.posts()[0].body),first));
      env.get().respond(200,wire);await env.flush();
      check(label+'/'+kind+' rejects and poisons',env.latest().event?.kind==='lost'&&typeof env.latest().problem==='string',env.latest());
      check(label+'/'+kind+' cancels active POST',env.posts()[0].aborted);
      const before=env.requests.length;
      env.posts()[0].respond(204,'',true);await env.flush();
      await enqueue(env,{seed:id,sequence:2});await env.tick(10000);
      check(label+'/'+kind+' late completion never sends queued or new action',env.requests.length===before&&env.posts().length===1,env.requests.map(x=>x.url));
      env.close();
    }
    const good=await worker(renderer);
    await enqueue(good,first);await enqueue(good,second);
    need(label+'/valid one active POST',good.posts().length===1&&equal(JSON.parse(good.posts()[0].body),first));
    need(label+'/valid unmatched disposition precondition',good.latest().pendingBatches===0);
    await good.event(allowed);
    check(label+'/valid matching role delivered during active POST',good.latest().event?.kind==='incoming'&&equal(good.latest().event.value,allowed)&&good.latest().problem===null&&good.posts().length===1,good.latest());
    check(label+'/valid preserves no pending domain batch',good.latest().pendingBatches===0,good.latest());
    good.posts()[0].respond(204);await good.flush();
    need(label+'/valid queued successor actually sent',good.posts().length===2);
    check(label+'/valid FIFO retains exact successor',equal(JSON.parse(good.posts()[1].body),second));
    good.posts()[1].respond(204);await good.flush();
    check(label+'/valid delivery drains without replay',good.posts().length===2&&good.latest().problem===null&&good.latest().event===null,good.latest());
    good.close();
  }
}

async function receiptNotAck(){
  const env=await worker(false);
  await env.event(gateway('view-topology',topology));
  need('controlled topology causes actual commit before attach',env.posts().length===1);
  env.posts()[0].respond(204);await env.flush();
  await env.event(initialGateway);
  const pending=env.latest().pendingBatches;
  need('controlled authenticated binding registers actual pending batch',pending>0&&env.posts().length===2,{pending,posts:env.posts().length,messages:env.messages});
  const request=env.posts()[1],whole=JSON.parse(request.body);
  need('receipt-negative control actual batch has requests',whole.requests.length>0&&whole.projection.frame);
  request.respond(204);await env.flush();
  check('HTTP204 does not settle owning pending batch',env.latest().pendingBatches===pending,env.latest());
  check('HTTP204 has no policy/native event',env.latest().event===null);
  const certificate={viewProtocol:1,kind:'batch-disposition',disposition:'admitted',scope:{id:'1',generation:'1'},revision:whole.projection.revision,publication:whole.projection.frame.publication,lease:whole.projection.frame.lease,binding,batch:request.body};
  await env.event(gateway('view-disposition',certificate));
  check('explicit matching bridge disposition positive settles batch',env.latest().pendingBatches===pending-1,env.latest());
  report.trace.push({label:'explicit controlled host preconditions; no native issuer',topology,attached:initialGateway,wholeCommit:whole,matchingDisposition:certificate});env.close();
}

(async()=>{try{await roots();await focusRoutes();await rendererSeedRoutes();await fifo();await capacities();await failures();await eventDuringDelivery();await receiptNotAck();report.passed=report.failures.length===0;}catch(error){report.error=String(error.stack??error);check('harness completed all campaigns',false,String(error));}finally{for(const env of environments)env.close();save();process.exitCode=report.passed?0:1;}})();
