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
 const packet=JSON.parse(fs.readFileSync(path.join(out,'snap.json'),'utf8'));
 await evaluate('receivePresentation('+JSON.stringify(packet.frame)+')');
 await until(`document.querySelector('.surface-popup[data-mode="snap"]')?.dataset.publication==="1"`);
 await until(`document.querySelectorAll('[data-surface-control^="snap:region:"]').length===6`);
 check('Actual production snap frame renders all six previews',await evaluate(`document.querySelector("h1").textContent==="Snap window"`));
 check('Selected preview is accessible',await evaluate(`document.querySelector('[data-surface-control="snap:region:left-half"]').getAttribute("aria-current")==="true"`));
 check('Preview uses selected glow and shading',await evaluate(`getComputedStyle(document.querySelector('[data-surface-control="snap:region:left-half"]')).boxShadow!=="none"`));
 async function key(key){await call('Input.dispatchKeyEvent',{type:'keyDown',key,code:key});await call('Input.dispatchKeyEvent',{type:'keyUp',key,code:key});await sleep(60);}
 await evaluate(`document.querySelector('[data-surface-control="snap:region:left-half"]').focus()`);
 await key('End');check('End reaches last enabled quarter and skips unavailable apply',await evaluate(`document.activeElement.dataset.surfaceControl==="snap:region:bottom-right"`));
 await key('ArrowUp');check('Arrow traversal reaches adjacent enabled region',await evaluate(`document.activeElement.dataset.surfaceControl==="snap:region:bottom-left"`));
 await key('Home');check('Home reaches Close',await evaluate(`document.activeElement.dataset.surfaceControl==="control:close"`));
 await key('ArrowDown');await key('Enter');
 check('Enter emits the exact region action once',await evaluate(`nativePackets.filter(p=>p.kind==="surface-action"&&p.id==="snap:region:left-half").length===1`));
 const before=await evaluate(`nativePackets.filter(p=>p.kind==="surface-action").length`);await click('[data-surface-control="snap:apply"]');
 check('Unavailable placement cannot dispatch an action',await evaluate(`document.querySelector('[data-surface-control="snap:apply"]').disabled && nativePackets.filter(p=>p.kind==="surface-action").length===`+before));
 await capture('snap-chooser');
 // Renderer/adapter fixture for the existing menu's new utility route. This
 // checks real keyboard adapters, not native operation admission or Elm policy.
 const menu={...packet.frame,publication:'2',lease:'2',mode:'menu',popup:[
  {id:'control:menu-close',domId:'menu-close',label:'Close',ariaLabel:'Close window actions',detail:'',enabled:true},
  {id:'menu:1:0',domId:'menu-op',label:'Minimize',ariaLabel:'Minimize',detail:'Selected',enabled:true},
  {id:'control:snap-open',domId:'menu-snap',label:'Snap window',ariaLabel:'Open snapping',detail:'',enabled:true}]};
 await evaluate('receivePresentation('+JSON.stringify(menu)+')');await until(`document.querySelector('.surface-popup[data-mode="menu"]')?.dataset.publication==="2"`);await sleep(80);
 await evaluate(`document.getElementById('menu-op').focus()`);await key('Tab');
 check('Menu Tab reaches the snap utility',await evaluate(`document.activeElement.dataset.surfaceControl==="control:snap-open"`));
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',modifiers:8});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab'});await sleep(60);
 check('Menu Shift Tab returns to selected native operation',await evaluate(`document.activeElement.dataset.surfaceControl==="menu:1:0"`));
 await key('Tab');menu.publication='3';await evaluate('receivePresentation('+JSON.stringify(menu)+')');await sleep(80);
 check('Unrelated publication retains focused utility',await evaluate(`document.activeElement.dataset.surfaceControl==="control:snap-open"`));
 await key('Enter');
 check('Menu Enter activates its exact current utility once',await evaluate(`nativePackets.filter(p=>p.kind==="surface-action"&&p.id==="control:snap-open"&&p.publication==="3"&&p.lease==="2").length===1`));
 check('Utility Enter cannot invoke selected window operation',await evaluate(`nativePackets.filter(p=>p.kind==="surface-menu-navigation"&&p.key==="Enter").length===0`));
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'snap-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
