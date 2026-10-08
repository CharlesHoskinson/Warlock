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
 await call('Page.navigate',{url:base+'/assets/popup.html'});await until('!!window.receivePresentation');
 const packet=JSON.parse(fs.readFileSync(path.join(out,'notifications.json'),'utf8'));
 await evaluate('receivePresentation('+JSON.stringify(packet.frame)+')');
 await until(`document.querySelector('.surface-popup[data-mode="notifications"]')?.dataset.publication==="1"`);
 check('Center shows notification text and named current action',await evaluate(`document.querySelector('h1').textContent==='Notifications' && document.body.textContent.includes('Calendar: Meeting soon') && document.body.textContent.includes('Bring your notes') && document.querySelector('[data-surface-control$=":invoke:open"]').getAttribute('aria-label')==='Open meeting'`));
 check('Notification content cannot issue actions',await evaluate(`document.querySelectorAll('[data-notification-content]').length===2 && !document.querySelector('[data-surface-control$=":summary"],[data-surface-control$=":body"]')`));
 async function key(key){await call('Input.dispatchKeyEvent',{type:'keyDown',key,code:key});await call('Input.dispatchKeyEvent',{type:'keyUp',key,code:key});await sleep(60);}
 await viewport(320,220);await evaluate(`document.querySelector('[data-surface-control="control:close"]').focus()`);await key('End');
 check('End reveals last live operation on small output',await evaluate(`document.activeElement.dataset.surfaceControl.endsWith(':dismiss:') && document.activeElement.getBoundingClientRect().bottom<=innerHeight+1`));
 await key('Home');check('Home returns to Close',await evaluate(`document.activeElement.dataset.surfaceControl==='control:close' && document.activeElement.getBoundingClientRect().top>=0`));
 await evaluate(`document.querySelector('[data-surface-control$=":invoke:open"]').focus()`);await key('Enter');
 check('Production keyboard emits one current surface action',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action' && p.id.endsWith(':invoke:open') && p.publication==='1').length===1`));
 await evaluate('receivePresentation('+JSON.stringify(packet.expiredFrame)+')');
 await until(`document.querySelector('.surface-popup').dataset.publication==='2'`);
 check('Expired action disappears while center stays open',await evaluate(`document.activeElement.dataset.surfaceControl==='control:close' && !document.querySelector('[data-surface-control$=":invoke:open"]') && !document.querySelector('[data-surface-control$=":dismiss:"]') && document.body.textContent.includes('History · expired')`));
 check('Expired content remains readable',await evaluate(`document.body.textContent.includes('Calendar: Meeting soon') && document.body.textContent.includes('Bring your notes')`));
 await evaluate(`document.querySelector('[data-surface-control="control:close"]').focus()`);await key('Escape');
 check('Escape dismisses via matching physical release',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action' && p.id==='control:close' && p.publication==='2').length===1`));
 await capture('notification-expired-history');
 const invalid=structuredClone(packet.frame);invalid.publication='3';invalid.popup.push(invalid.popup.at(-1));await evaluate('receivePresentation('+JSON.stringify(invalid)+')');await sleep(80);
 check('Duplicate presentation identity fails closed',await evaluate(`document.querySelector('.surface-popup')===null`));
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'notifications-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
