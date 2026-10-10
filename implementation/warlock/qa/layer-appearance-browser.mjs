import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const [base,rootOut,binary]=process.argv.slice(2), out=path.join(rootOut,'layer-browser'), report={passed:false,checks:[],captures:[],errors:[],externalRequests:[],nativeAcceptance:false,fullReleaseAccepted:false};
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
 const packet=JSON.parse(fs.readFileSync(path.join(rootOut,'layer-appearance.json'),'utf8'));
 const key=async value=>{await call('Input.dispatchKeyEvent',{type:'keyDown',key:value,code:value,windowsVirtualKeyCode:9});await call('Input.dispatchKeyEvent',{type:'keyUp',key:value,code:value,windowsVirtualKeyCode:9});await sleep(35);};
 await evaluate('receivePresentation('+JSON.stringify(packet.draftFrame)+')');
 await until(`document.querySelector('.surface-popup')?.dataset.publication==='20'`);
 check('Unsaved flags do not project',await evaluate(`document.documentElement.dataset.effects==='on' && document.documentElement.dataset.reducedTransparency==='false'`));
 await call('Page.reload');await until('!!window.receivePresentation');
 for(const frame of packet.frames){
  await evaluate('receivePresentation('+JSON.stringify(frame)+')');
  await until(`document.querySelector('.surface-popup')?.dataset.publication===${JSON.stringify(frame.publication)} && document.documentElement.dataset.effects===${JSON.stringify(frame.appearance.effectsOff?'off':'on')} && document.documentElement.dataset.reducedTransparency===${JSON.stringify(String(frame.appearance.reducedTransparency))}`);
  for(let n=0;n<50 && !(await evaluate(`document.activeElement?.dataset.surfaceControl==='settings:effects-off'`));n++)await key('Tab');
  check('Keyboard reaches effects control '+frame.publication,await evaluate(`document.activeElement?.dataset.surfaceControl==='settings:effects-off'`));
  const observed=await evaluate(`(()=>{const node=document.activeElement,s=getComputedStyle(node),popup=document.querySelector('.surface-popup'),p=getComputedStyle(popup),r=node.getBoundingClientRect();return {identity:node.dataset.surfaceControl,outline:s.outlineStyle,outlineWidth:parseFloat(s.outlineWidth),boxShadow:s.boxShadow,visible:r.x>=0&&r.y>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1,background:p.backgroundColor,alpha:p.backgroundColor.startsWith('rgba')?parseFloat(p.backgroundColor.split(',').at(-1)):1,backdrop:p.backdropFilter,opacity:p.opacity,theme:document.documentElement.dataset.theme,effects:document.documentElement.dataset.effects,transparency:document.documentElement.dataset.reducedTransparency,name:node.getAttribute('aria-label')};})()`);
  check('Equivalent named visible focus '+frame.publication,observed.outline!=='none' && observed.outlineWidth>=2 && observed.visible && observed.name==='Disable soft effects',observed);
  if(frame.appearance.effectsOff){const shadows=await evaluate(`[...document.querySelectorAll('.surface-popup,.surface-popup button')].filter(node=>getComputedStyle(node).boxShadow!=='none').map(node=>({identity:node.dataset.surfaceControl,shadow:getComputedStyle(node).boxShadow}))`);check('Soft shadows suppressed '+frame.publication,shadows.length===0,shadows);}
  if(frame.appearance.reducedTransparency)check('Opaque backing without backdrop effect '+frame.publication,observed.opacity==='1' && observed.backdrop==='none' && observed.alpha===1,observed);
  check('Typed toggle states expose aria-pressed '+frame.publication,await evaluate(`document.querySelector('[data-surface-control="settings:effects-off"]').getAttribute('aria-pressed')===${JSON.stringify(String(frame.appearance.effectsOff))} && document.querySelector('[data-surface-control="settings:reduced-transparency"]').getAttribute('aria-pressed')===${JSON.stringify(String(frame.appearance.reducedTransparency))}`));
  check('Both current flag controls remain present '+frame.publication,await evaluate(`!!document.querySelector('[data-surface-control="settings:reduced-transparency"]')`));
  if(frame.appearance.effectsOff && frame.appearance.reducedTransparency)await capture('layer-appearance-'+frame.appearance.theme);
 }
 check('No window effect authority from decoration',await evaluate(`!nativePackets.some(row=>row.kind==='window-effect')`));
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
