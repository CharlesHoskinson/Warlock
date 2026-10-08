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


 await call('Page.enable');await call('Runtime.enable');await viewport(640,620);
 await call('Page.addScriptToEvaluateOnNewDocument',{source:'window.nativePackets=[];window.webkit={messageHandlers:{native:{postMessage:text=>nativePackets.push(JSON.parse(text))}}};'});
 const packet=JSON.parse(fs.readFileSync(path.join(out,'switcher.json'),'utf8'));
 await call('Page.navigate',{url:base+'/qa/dense.html'});await until('typeof receivePresentation==="function"');
 await evaluate('receivePresentation('+JSON.stringify(packet.taskbarFrame)+')');await until('!!document.querySelector(".surface-bar")');
 check('Taskbar is a named native toolbar',await evaluate(`document.querySelector('[role="toolbar"]').getAttribute('aria-label')==='Warlock taskbar'`));
 check('Only active taskbar button is pressed',await evaluate(`(()=>{const b=[...document.querySelectorAll('.control-group')];return b.length===3&&b.filter(n=>n.getAttribute('aria-pressed')==='true').length===1&&b.every(n=>n.getAttribute('role')==='button'&&n.getAttribute('aria-label'));})()`));
 await call('Page.navigate',{url:base+'/qa/dense-picker.html'});await until('typeof receivePresentation==="function"');
 await evaluate('receivePresentation('+JSON.stringify(packet.frame)+')');await until('!!document.querySelector("[role=listbox]")');
 async function selected(){return evaluate(`(()=>{const list=document.querySelector('[role="listbox"]');return {name:list?.getAttribute('aria-label'),rows:[...document.querySelectorAll('[role="option"]')].map(b=>({name:b.getAttribute('aria-label'),selected:b.getAttribute('aria-selected'),id:b.id,identity:b.dataset.surfaceControl,disabled:b.disabled}))};})()`);}
 const first=await selected();check('Named switcher list has three actual window options',first.name==='Switch windows'&&first.rows.length===3,first);
 check('Exactly one selected state matches typed current choice',first.rows.filter(b=>b.selected==='true').length===1&&first.rows.every(b=>(b.selected==='true')===b.name.endsWith('; selected')),first);
 check('Switcher actions retain button semantics outside listbox',await evaluate(`document.querySelectorAll('[aria-label="Window switcher actions"] [role="button"]').length===4&&!document.querySelector('[role="listbox"] [role="button"]')`));
 const firstId=first.rows.find(b=>b.selected==='true').id;await evaluate('document.getElementById('+JSON.stringify(firstId)+').focus()');
 check('Chosen option has actual DOM focus',await evaluate('document.activeElement.id==='+JSON.stringify(firstId)));
 await capture('switcher-accessible-selection');
 await evaluate('receivePresentation('+JSON.stringify(packet.cycledFrame)+')');await until('document.querySelector(".surface-popup")?.dataset.publication==="2"');
 const next=await selected();check('Typed cycle changes exactly one native selection',next.rows.filter(b=>b.selected==='true').length===1&&next.rows.find(b=>b.selected==='true').id!==firstId,next);
 check('Observation preserves control identity and does not submit window effects',next.rows.every((b,i)=>b.identity===first.rows[i].identity)&&await evaluate(`!nativePackets.some(p=>p.kind==='window-effect'||p.kind==='application-launch')`));
 await evaluate('receivePresentation('+JSON.stringify(packet.closedFrame)+')');await until('document.querySelector(".surface-popup")?.dataset.publication==="3"');
 check('Retired switcher exports no stale selected options',await evaluate('document.querySelectorAll("[role=option]").length===0'));
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'accessibility-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
