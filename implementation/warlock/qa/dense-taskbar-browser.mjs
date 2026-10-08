import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const [base,out,binary]=process.argv.slice(2), report={passed:false,checks:[],captures:[],errors:[],externalRequests:[],nativeAcceptance:false,fullReleaseAccepted:false};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const browser=spawn(binary,['--remote-debugging-address=127.0.0.1','--remote-debugging-port=0','--user-data-dir='+path.join(out,'profile'),'--disable-gpu','--disable-breakpad','--disable-crash-reporter','--no-first-run','about:blank'],{stdio:['ignore','pipe','pipe']});
let stderr='',stdout='',ws,session,sequence=0,pending=new Map();
browser.stderr.on('data',v=>stderr+=v);browser.stdout.on('data',v=>stdout+=v);
function call(method,params={},sessionId=session){return new Promise((resolve,reject)=>{const id=++sequence;const timer=setTimeout(()=>{pending.delete(id);reject(new Error('CDP timeout '+method));},15000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));});}
function check(name,condition,detail){if(!condition)throw Error(name+' '+JSON.stringify(detail));report.checks.push({name,detail});}
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function until(expression){for(let i=0;i<100;i++){if(await evaluate(expression))return;await sleep(30);}throw Error('Condition timeout '+expression);}
async function click(selector){const rect=await evaluate(`(()=>{const b=document.querySelector(${JSON.stringify(selector)});b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()`);await call('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...rect});await call('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...rect});await sleep(60);}
async function route(name){await evaluate('location.hash='+JSON.stringify(name));await until('!!document.querySelector("main h1") && location.hash === '+JSON.stringify('#'+name));await sleep(100);}
async function viewport(width,height=980){await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await sleep(80);}
async function capture(name){await evaluate('document.fonts.ready');const r=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.data,'base64'));report.captures.push(name+'.png');}
async function observation(){return evaluate('window.fixtureObservation');}
try{
 let match;for(let i=0;i<100;i++){match=stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);if(match)break;if(browser.exitCode!==null)throw Error('Browser exited '+browser.exitCode+' '+stderr);await sleep(30);}if(!match)throw Error('No DevTools endpoint '+stderr);
 ws=new WebSocket(match[1]);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 ws.onmessage=event=>{const m=JSON.parse(event.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}}else if(m.method==='Runtime.exceptionThrown')report.errors.push(m.params.exceptionDetails);};
 const target=await call('Target.createTarget',{url:'about:blank'},null);session=(await call('Target.attachToTarget',{targetId:target.targetId,flatten:true},null)).sessionId;

 await call('Page.enable');await call('Runtime.enable');await viewport(480,96);await call('Page.navigate',{url:base+'/qa/dense.html'});await until('!!window.receivePresentation');
 let pub=0;
 async function show(disabled=-1){const frame={surfaceProtocol:2,publication:String(++pub),lease:'0',mode:'closed',status:'Ready',popup:[],bar:Array.from({length:100},(_,i)=>({id:'bar:pin:app-'+i,domId:'pin:'+pub+':'+i,label:'Application '+i,ariaLabel:'Activate Application '+i,detail:'Pinned; Open',enabled:i!==disabled}))};await evaluate('receivePresentation('+JSON.stringify(frame)+')');await until('document.querySelector(".surface-bar")?.dataset.publication==='+JSON.stringify(frame.publication));await sleep(60);}
 async function key(value){await call('Input.dispatchKeyEvent',{type:'keyDown',key:value,code:value});await call('Input.dispatchKeyEvent',{type:'keyUp',key:value,code:value});await sleep(40);}
 const state=()=>evaluate(`(()=>{const a=document.querySelector('.surface-actions'),f=document.activeElement,r=f.getBoundingClientRect(),v=a.getBoundingClientRect();return {id:f.dataset.surfaceControl,domId:f.id,x:r.x,right:r.right,top:r.top,bottom:r.bottom,left:v.left,viewRight:v.right,viewBottom:v.bottom,scroll:a.scrollLeft,scrollWidth:a.scrollWidth,width:a.clientWidth,font:getComputedStyle(document.body).fontSize,shadow:getComputedStyle(f).boxShadow,order:[...a.children].map(b=>b.dataset.surfaceControl)};})()`);
 const visible=s=>s.x>=s.left-.5&&s.right<=s.viewRight+.5&&s.top>=0&&s.bottom<=s.viewBottom+.5;
 await show();await evaluate(`document.querySelector('[data-surface-control="bar:pin:app-0"]').focus()`);const first=await state();check('Enlarged first item visible with bounded overflow',first.font==='24px'&&visible(first)&&first.scrollWidth>first.width,first);
 await key('End');const last=await state();check('End reveals last item',last.id==='bar:pin:app-99'&&visible(last),last);await capture('dense-last');
 await show(98);await key('ArrowLeft');const skipped=await state();check('Arrow traversal skips disabled controls without changing order',skipped.id==='bar:pin:app-97'&&visible(skipped)&&JSON.stringify(skipped.order)===JSON.stringify(first.order),skipped);
 await key('Home');check('Home reveals first item',(await state()).id==='bar:pin:app-0'&&visible(await state()));
 await key('End');await show();const changed=await state();check('Publication changes keep the logical selected identity',changed.id==='bar:pin:app-99'&&changed.domId==='pin:3:99'&&visible(changed),changed);
 for(const width of [960,320,640]){await viewport(width,96);const current=await state();check('Resize '+width+' preserves order and visible selection',current.id==='bar:pin:app-99'&&visible(current)&&JSON.stringify(current.order)===JSON.stringify(first.order),current);}
 await call('Input.dispatchMouseEvent',{type:'mouseWheel',x:600,y:30,deltaX:0,deltaY:-30000});await sleep(70);check('Vertical wheel reaches the beginning',(await state()).scroll===0,await state());
 await show();check('Observation publications do not undo manual scrolling',(await state()).scroll===0,await state());
 await key('End');check('Keyboard navigation reveals selection after manual scrolling',visible(await state()));
 await show(99);await show();check('A transiently disabled selection returns by current identity',(await state()).id==='bar:pin:app-99'&&visible(await state()));
 await call('Emulation.setEmulatedMedia',{features:[{name:'forced-colors',value:'active'}]});await key('Home');check('Forced colors retain a visible focus outline',await evaluate(`getComputedStyle(document.activeElement).outlineStyle!=='none'`));
 check('Scrolling and navigation never emit activation',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action').length===0`));check('No uncaught browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'dense-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
