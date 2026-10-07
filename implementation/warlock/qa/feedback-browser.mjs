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
 await call('Page.enable');await call('Runtime.enable');await viewport(1440,80);await call('Page.navigate',{url:base+'/qa/feedback.html'});await until('!!window.testApp');
 const rows=await fetch(base+'/qa/feedback.json').then(r=>r.json());let pub=0;
 async function show(state){const frame=structuredClone(rows.find(r=>r.status===state).frame);frame.publication=String(++pub);frame.bar.push(...Array.from({length:14},(_,i)=>({id:'bar:group:fixture-'+i,domId:'fixture-'+i,label:'Window '+i,ariaLabel:'Activate Window '+i,detail:'1',enabled:true})));await evaluate('testApp.ports.presentation.send('+JSON.stringify(frame)+')');await until('document.querySelector(".surface-bar")?.dataset.publication==='+JSON.stringify(frame.publication));await sleep(70);return frame;}
 function seen(){return evaluate(`(()=>{const n=document.querySelector('[role=status]'),r=n.getBoundingClientRect(),c=getComputedStyle(n),a=document.querySelector('.surface-actions').getBoundingClientRect();return {text:n.textContent,label:n.getAttribute('aria-label'),atomic:n.getAttribute('aria-atomic'),live:n.getAttribute('aria-live'),width:r.width,height:r.height,x:r.x,y:r.y,clip:c.clipPath,display:c.display,controlsRight:a.right};})()`);}
 for(const state of ['Pending','Refused','Unknown']){await show(state);const o=await seen();check(state+' actual compiled view visibly exposes typed feedback',o.width>=180&&o.height===48&&o.clip==='none'&&o.display!=='none'&&o.x>=0&&o.x+o.width<=1440,o);check(state+' full message available to accessibility',o.text===o.label&&o.atomic==='true'&&o.live==='polite',o);}
 await capture('feedback-wide-unknown');
 // Regression control: the old stylesheet hides the status on the same actual view.
 await evaluate(`document.querySelector('link').disabled=true;fetch('/qa/baseline.css').then(r=>r.text()).then(t=>{const s=document.createElement('style');s.id='baseline';s.textContent=t;document.head.append(s);})`);await until('!!document.getElementById("baseline")');const before=await seen();check('Inherited stylesheet reproduces visually hidden status',before.width===1&&before.height===1&&before.clip!=='none',before);
 await evaluate(`document.getElementById('baseline').remove();document.querySelector('link').disabled=false`);await sleep(50);
 await viewport(320,80);await show('Unknown');let narrow=await seen();check('320px feedback fits and does not cover controls',narrow.x>=0&&narrow.x+narrow.width<=320&&narrow.controlsRight<=narrow.x&&narrow.height===48,narrow);
 await evaluate(`document.getElementById('fixture-13').focus()`);await sleep(50);check('Last control remains reachable and is revealed in bounded overflow',await evaluate(`(()=>{const n=document.getElementById('fixture-13'),r=n.getBoundingClientRect(),a=document.querySelector('.surface-actions').getBoundingClientRect();return document.activeElement===n&&r.x>=a.x&&r.right<=a.right+1;})()`));
 await evaluate('window.heldFocus=document.activeElement');await show('Refused');check('Feedback update preserves keyed control and focus',await evaluate('document.activeElement===heldFocus&&heldFocus.isConnected'));
 await capture('feedback-narrow-refused');check('Status changes never dispatch an action',await evaluate('actions.length===0'));
 await show('Unknown');await evaluate(`document.querySelector('[data-surface-control="bar:recovery-refresh"]').focus()`);await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter'});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter'});await sleep(40);check('Recovery keyboard activation emits one observation-control action',await evaluate('actions.length===1&&actions[0].kind==="surface-action"&&actions[0].id==="bar:recovery-refresh"'));
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:' ',code:'Space'});await show('Unknown');await call('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space'});await sleep(40);check('Old pressed input is cancelled across a new publication',await evaluate('actions.length===1'));
 await sleep(80);check('Unknown remains visibly unconfirmed without auto-retry',await evaluate(`document.querySelector('[role=status]').textContent.includes('not confirmed')&&actions.length===1`));
 await show('Committed');const ready=await seen();check('Ready status does not consume taskbar width',ready.display==='none',ready);
 check('No uncaught browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
