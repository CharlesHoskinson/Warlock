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
 await call('Page.navigate',{url:base+'/assets/bar.html'});await until('!!window.receivePresentation');
 const packet=JSON.parse(fs.readFileSync(path.join(out,'attention.json'),'utf8'));
 await viewport(800,160);packet.frame.status='Connected';await evaluate('receivePresentation('+JSON.stringify(packet.frame)+')');await until(`document.querySelector('.surface-bar')?.dataset.publication==="1"`);
 const observed=await evaluate(`(()=>{const rows=[...document.querySelectorAll('.control-group')];return rows.map(b=>({name:b.getAttribute('aria-label'),state:b.dataset.windowState,detail:b.querySelector('.control-detail').textContent,border:getComputedStyle(b).borderTopColor,shadow:getComputedStyle(b).boxShadow,background:getComputedStyle(b).backgroundColor}));})()`);
 const active=observed.find(row=>row.state==='active'),attention=observed.find(row=>row.state==='attention');
 check('Original active and attention have distinct visible color and shape',active&&attention&&active.border!==attention.border&&active.shadow!==attention.shadow&&active.background!==attention.background,observed);
 check('Original accessible state distinguishes attention from active',attention.name.includes('Attention; Open')&&active.name.includes('Active'),observed);
 check('Active is the current application and attention remains inactive',await evaluate(`document.querySelector('[data-window-state="active"]').getAttribute('aria-current')==='true' && document.querySelector('[data-window-state="attention"]').getAttribute('aria-current')==='false'`));
 check('Application indicators remain visible before utilities with status present',await evaluate(`(()=>{const area=document.querySelector('.surface-actions').getBoundingClientRect();return [...document.querySelectorAll('.control-group')].every(b=>{const r=b.getBoundingClientRect();return r.left>=area.left&&r.right<=area.right;})&&document.querySelector('.surface-actions').firstElementChild.matches('.control-group');})()`));
 await capture('attention-active-native-view');
 check('State has no animated attention flashing',await evaluate(`[...document.querySelectorAll('.control-group')].every(b=>getComputedStyle(b).animationName==='none')`));
 await evaluate('receivePresentation('+JSON.stringify(packet.clearFrame)+')');await until(`document.querySelector('.surface-bar')?.dataset.publication==="2"`);
 check('New observation removes attention highlight and label',await evaluate(`!document.querySelector('[data-window-state="attention"]')&&!document.querySelector('[aria-label*="Attention; Open"]')`));
 await evaluate('receivePresentation('+JSON.stringify(packet.activeFrame)+')');await until(`document.querySelector('.surface-bar')?.dataset.publication==="3"`);
 check('Native active state takes priority over remaining urgency',await evaluate(`!document.querySelector('[data-window-state="attention"]')&&document.querySelector('[data-window-state="active"]').textContent.includes('Attention Window')`));
 const dusk=structuredClone(packet.frame);dusk.publication='4';dusk.appearance={...dusk.appearance,theme:'dawn'};
 await evaluate('receivePresentation('+JSON.stringify(dusk)+')');await until(`document.querySelector('.surface-bar')?.dataset.publication==="4"`);
 check('Dawn attention has its documented darker amber border',await evaluate(`getComputedStyle(document.querySelector('[data-window-state="attention"]')).borderTopColor==='rgb(140, 78, 0)'`));
 await call('Emulation.setEmulatedMedia',{features:[{name:'forced-colors',value:'active'}]});
 check('Forced colors preserves different edge shapes',await evaluate(`getComputedStyle(document.querySelector('[data-window-state="attention"]')).borderTopWidth==='4px'&&getComputedStyle(document.querySelector('[data-window-state="active"]')).borderBottomWidth==='4px'`));
 check('Observing attention never submits an application or window effect',await evaluate(`!nativePackets.some(p=>p.kind==='window-effect'||p.kind==='application-launch')`));
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'attention-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
