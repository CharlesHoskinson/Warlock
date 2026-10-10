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




 await call('Page.enable');await call('Runtime.enable');await viewport(640,700);
 const fixture=JSON.parse(fs.readFileSync(path.join(out,'pin-max.json'),'utf8'));
 await call('Page.addScriptToEvaluateOnNewDocument',{source:'window.nativePackets=[];window.webkit={messageHandlers:{native:{postMessage:s=>nativePackets.push(JSON.parse(s))}}};'});
 await call('Page.navigate',{url:base+'/assets/popup.html'});await until('typeof window.receivePresentation==="function"');
 const show=async value=>{await evaluate(`window.receivePresentation(${JSON.stringify(value)})`);await sleep(100);};
 const observed=()=>evaluate(`(()=>{const b=document.querySelector('[role="menuitemcheckbox"]');return b?{label:b.getAttribute('aria-label'),checked:b.getAttribute('aria-checked'),identity:b.dataset.surfaceControl,disabled:b.disabled,rect:b.getBoundingClientRect().toJSON(),publication:document.querySelector('.surface-popup').dataset.publication}:null})()`);
 await show(fixture.uncheckedFrame);await until('document.querySelector("[role=menuitemcheckbox]")?.getAttribute("aria-checked")==="false"');
 const unchecked=await observed();check('Observed unpinned window has one unchecked stable Always on top menu control',unchecked.label==='Always on top'&&!unchecked.disabled&&await evaluate('document.querySelectorAll("[role=menuitemcheckbox]").length===1'),unchecked);
 await evaluate('window.pinNode=document.querySelector("[role=menuitemcheckbox]");pinNode.focus();window.nativePackets=[]');
 await show(fixture.checkedFrame);const checked=await observed();
 check('Observed pin keeps label identity actual DOM node and keyboard focus',checked.label===unchecked.label&&checked.identity===unchecked.identity&&checked.checked==='true'&&await evaluate('pinNode===document.querySelector("[role=menuitemcheckbox]")&&document.activeElement===pinNode'),checked);
 const ax=await call('Accessibility.getFullAXTree');check('Browser accessibility tree exposes checked menu item',ax.nodes.some(n=>n.role?.value==='menuitemcheckbox'&&n.name?.value==='Always on top'&&n.properties?.some(p=>p.name==='checked'&&p.value.value==='true')));
 check('Selected MAX checkbox exposes current selection and actual keyboard focus',await evaluate('document.querySelector("[role=menuitemcheckbox]").getAttribute("aria-current")=="true"&&document.activeElement===document.querySelector("[role=menuitemcheckbox]")'),await evaluate('(()=>{const b=document.querySelector("[role=menuitemcheckbox]");return {current:b?.getAttribute("aria-current"),detail:b?.textContent,focus:document.activeElement?.dataset.surfaceControl,checkedIdentity:b?.dataset.surfaceControl}})()'));
 check('Observation alone submits no actions',await evaluate('nativePackets.every(p=>p.kind!=="surface-action")'));
 await capture('AlwaysOnTopChecked');
 const rowIndex=fixture.checkedFrame.popup.findIndex(r=>r.checked!==undefined);
 let restoredPublication=12;
 for(const [name,mutate] of [
  ['Wrong boolean',f=>f.popup[rowIndex].checked='true'],
  ['Wrong mode',f=>f.mode='settings'],
  ['Wrong identity',f=>f.popup[rowIndex].id='control:close-forged'],
  ['Duplicate checked control',f=>{f.popup[0].checked=false;f.popup[0].id='menu:1:other'}],
  ['Missing current shape',f=>delete f.popup[rowIndex].focusOnly]
 ]){const f=structuredClone(fixture.checkedFrame);f.publication='20';mutate(f);await show(f);check(name+' fails closed without retaining an actionable checkbox',(await observed())===null&&await evaluate('nativePackets.every(p=>p.kind!=="surface-action")'));const restore=structuredClone(fixture.checkedFrame);restore.publication=String(restoredPublication++);await show(restore);check(name+' recovers only through a fresh valid observation',(await observed())?.checked==='true');}
 await evaluate('document.querySelector("[role=menuitemcheckbox]").focus()');
 const actionPublication=(await observed()).publication;
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await sleep(80);
 const keys=await evaluate('nativePackets.filter(p=>p.kind==="surface-menu-navigation")');check('Keyboard invocation uses original scoped native menu navigation without checked authority',keys.length===1&&keys[0].key==='Enter'&&keys[0].publication===actionPublication&&!Object.hasOwn(keys[0],'checked'),keys);await click('[role=menuitemcheckbox]');const actions=await evaluate('nativePackets.filter(p=>p.kind==="surface-action")');check('Pointer invocation sends exactly one existing identity scoped action without checked authority',actions.length===1&&actions[0].id===checked.identity&&actions[0].publication===actionPublication&&!Object.hasOwn(actions[0],'checked'),actions);
 const pendingFrame=structuredClone(fixture.pendingFrame);pendingFrame.publication=String(restoredPublication++);await show(pendingFrame);const pendingObservation=await observed();check('Pending observes prior unchecked native state and cannot dispatch',pendingObservation?.checked==='false'&&pendingObservation.disabled,pendingObservation);
 await evaluate('document.querySelector("[role=menuitemcheckbox]").click()');await sleep(50);check('Disabled checkbox does not replay an action',await evaluate('nativePackets.filter(p=>p.kind==="surface-action").length===1'));
 const high=structuredClone(fixture.checkedFrame);high.publication='30';high.appearance.theme='high-contrast';high.appearance.textScale=200;await show(high);await capture('AlwaysOnTopHighContrast');
 const shape=await evaluate('getComputedStyle(document.querySelector("[role=menuitemcheckbox]"),"::before").borderTopStyle');check('High contrast retains a checkbox shape with actual shipped palette and text scaling',shape==='solid'&&await evaluate('document.documentElement.dataset.theme==="high-contrast"&&getComputedStyle(document.documentElement).fontSize==="32px"&&getComputedStyle(document.querySelector("[role=menuitemcheckbox]")).backgroundColor==="rgb(0, 0, 0)"'));
 report.observations={unchecked,checked,pending:pendingObservation};check('No browser runtime exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error);report.passed=false;}finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');await new Promise(r=>{if(browser.exitCode!==null)r();else browser.once('exit',r)});report.browserExitCode=browser.exitCode;report.browserSignal=browser.signalCode;fs.writeFileSync(path.join(out,'pin-check-browser.json'),JSON.stringify(report,null,2)+'\n');
}
console.log(JSON.stringify({passed:report.passed,error:report.error,checks:report.checks.length}));process.exitCode=report.passed?0:1;
