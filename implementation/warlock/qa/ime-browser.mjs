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
 const packet=JSON.parse(fs.readFileSync(path.join(out,'ime.json'),'utf8'));
 await call('Page.navigate',{url:base+'/qa/dense-picker.html'});await until('typeof receivePresentation==="function"');
 await evaluate('receivePresentation('+JSON.stringify(packet.frame)+')');await until('!!document.querySelector("[data-surface-field]")');
 await evaluate(`window.imeField=document.querySelector('[data-surface-field]');imeField.focus();window.nativePackets=[];`);
 const escape=type=>call('Input.dispatchKeyEvent',{type,key:'Escape',code:'Escape',windowsVirtualKeyCode:27});
 await escape('keyDown');await sleep(60);
 check('Apps Escape keydown retains popup and emits no close',await evaluate(`nativePackets.every(p=>p.kind!=='surface-action')&&document.activeElement===imeField`));
 await escape('keyUp');await sleep(60);
 check('Apps Escape release emits one exact current close',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action').length===1&&nativePackets.find(p=>p.kind==='surface-action').id==='control:close'&&nativePackets.find(p=>p.kind==='surface-action').lease==='1'`));
 await escape('keyUp');await sleep(40);
 check('Repeated release cannot emit another close',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action').length===1`));
 await evaluate('window.nativePackets=[]');
 async function composing(type,value,data=''){await evaluate(`(()=>{imeField.value=${JSON.stringify(value)};imeField.setSelectionRange(imeField.value.length,imeField.value.length);imeField.dispatchEvent(new CompositionEvent(${JSON.stringify(type)},{bubbles:true,data:${JSON.stringify(data)}}));})()`);await sleep(40);}
 async function input(value,isComposing){await evaluate(`(()=>{imeField.value=${JSON.stringify(value)};imeField.dispatchEvent(new InputEvent('input',{bubbles:true,data:${JSON.stringify(value)},isComposing:${isComposing},inputType:'insertCompositionText'}));})()`);await sleep(40);}
 const count=()=>evaluate(`nativePackets.filter(p=>p.kind==='surface-query').length`);
 await composing('compositionstart','');await input('é',true);
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
 await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await sleep(40);
 check('Compiled preedit prevents Enter launch and keeps search focus',await evaluate(`!nativePackets.some(p=>p.kind==='surface-action')&&document.activeElement===imeField&&document.querySelector('[data-input-composing]').dataset.inputComposing==='true'`));
 await escape('keyDown');await escape('keyUp');await sleep(40);
 check('Actual compiled preedit prevents Escape dismissal',await evaluate(`!nativePackets.some(p=>p.kind==='surface-action')&&document.querySelector('[data-input-composing]').dataset.inputComposing==='true'`));
 // Escape may edit/cancel the browser's input value. Start the original IME
 // commit/cancel oracle on a fresh document, retaining its original text.
 await call('Page.navigate',{url:base+'/qa/dense-picker.html'});await until('typeof receivePresentation==="function"');
 await evaluate('receivePresentation('+JSON.stringify(packet.frame)+')');await until('!!document.querySelector("[data-surface-field]")');
 await evaluate(`window.imeField=document.querySelector('[data-surface-field]');imeField.focus();window.nativePackets=[];`);
 await composing('compositionstart','');await input('é',true);
 check('Preedit stays in real field without query dispatch',await evaluate(`imeField.value==='é'&&document.querySelector('[data-input-composing]').dataset.inputComposing==='true'`)&&await count()===0);
 await evaluate('receivePresentation('+JSON.stringify(packet.refreshFrame)+')');await until('document.querySelector(".surface-popup").dataset.publication==="2"');
 check('Same-field observation keeps native input node and preedit',await evaluate(`imeField===document.querySelector('[data-surface-field]')&&imeField.value==='é'&&document.activeElement===imeField`)&&await count()===0);
 await evaluate('receivePresentation('+JSON.stringify(packet.equalFrame)+')');await until('document.querySelector(".surface-popup").dataset.publication==="3"');
 await evaluate('receivePresentation('+JSON.stringify(packet.nextFrame)+')');await until('document.querySelector(".surface-popup").dataset.publication==="4"');
 check('Matching observation cannot clear uncommitted preedit',await evaluate(`imeField.value==='é'&&document.querySelector('[data-input-composing]').dataset.inputComposing==='true'`));
 await input('é',false);check('Final input preceding end does not dispatch preedit',await count()===0);
 await composing('compositionend','é','é');await input('é',false);
 check('Composition end and final input dispatch exactly one committed query',await count()===1&&await evaluate(`nativePackets.find(p=>p.kind==='surface-query').query==='é'`));
 check('Commit retains correct caret and focus',await evaluate(`imeField.selectionStart===1&&imeField.selectionEnd===1&&document.activeElement===imeField`));
 await capture('ime-committed-query');
 await evaluate('receivePresentation('+JSON.stringify(packet.ackFrame)+')');await until('document.querySelector(".surface-popup").dataset.publication==="5"');
 await composing('compositionstart','é');await input('é candidate',true);
 await composing('compositionend','é','');await input('é',false);
 check('Cancellation clears preedit and retains only prior committed text',await evaluate(`imeField.value==='é'&&document.querySelector('[data-input-composing]').dataset.inputComposing==='false'`)&&await count()===1);
 await composing('compositionstart','é');await input('é held',true);
 await evaluate('receivePresentation('+JSON.stringify(packet.filesFrame)+')');await until('document.querySelector(".surface-popup").dataset.mode==="files"');
 check('Other field cannot inherit launcher preedit',await evaluate(`document.querySelector('[data-input-composing]').dataset.inputComposing==='false'&&document.querySelector('[data-surface-field]').value===''`));
 check('No application/window effect is caused by composition',await evaluate(`!nativePackets.some(p=>p.kind==='application-launch'||p.kind==='window-effect'||p.kind==='surface-action')`));
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'ime-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
