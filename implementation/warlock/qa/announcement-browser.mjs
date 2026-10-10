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



 await call('Page.enable');await call('Runtime.enable');await viewport(1360,1000);
 const fixture=JSON.parse(fs.readFileSync(path.join(out,'announcements.json'),'utf8'));
 await call('Page.navigate',{url:base+'/qa/announcement-host.html'});await until('["bar1","bar2","popup"].every(id=>typeof document.getElementById(id)?.contentWindow?.receiveAnnouncement==="function")');
 const windows=['bar1','bar2','popup'];
 async function frame(value){await evaluate(`for(const id of ${JSON.stringify(windows)})document.getElementById(id).contentWindow.receivePresentation(${JSON.stringify(value.frame)});`);await sleep(80);}
 function scope(id){return {id:String(id),generation:'1'};}
 async function metadata(value,deliver=false){for(const id of windows){const recipient={scope:scope(id==='bar2'?2:1),surface:id==='popup'?'popup':'bar'};
  const active=JSON.stringify(recipient)===JSON.stringify(value.announcer);
  const packet={announcementProtocol:1,kind:'announcement-projection',recipient,announcer:value.announcer,publication:value.frame.publication,lease:value.frame.lease,message:value.announcement,deliver:deliver&&active};
  await evaluate(`document.getElementById(${JSON.stringify(id)}).contentWindow.receiveAnnouncement(${JSON.stringify(packet)})`);
 }await sleep(80);}
 async function observe(){return evaluate(`(()=>{return ${JSON.stringify(windows)}.map(id=>{const w=document.getElementById(id).contentWindow,d=w.document;return {id,live:[...d.querySelectorAll('[aria-live="polite"],[aria-live="assertive"]')].map(n=>({live:n.getAttribute('aria-live'),text:n.textContent,sequence:n.querySelector('[data-announcement-sequence]')?.dataset.announcementSequence||null,correlation:n.querySelector('[data-announcement-correlation]')?.dataset.announcementCorrelation||null})),visual:[...d.querySelectorAll('.surface-status,.surface-popup>p[role="status"]')].map(n=>({text:n.textContent,live:n.getAttribute('aria-live')})),focus:d.activeElement?.dataset.surfaceControl||null,packets:w.nativePackets||[]};});})()`);}
 const first=fixture.settingsFrame;
 await frame(first);await metadata({...first,announcement:null});
 check('Only the designated popup owns a live region before refusal', (await observe()).every(row=>row.live.length===(row.id==='popup'?1:0)));
 await evaluate(`(()=>{const d=document.getElementById('popup').contentWindow.document;const b=d.querySelector('[data-surface-control="settings:save"]');window.originalFocus=b;b.focus();})()`);
 await until('document.getElementById("popup").contentWindow.document.activeElement===originalFocus');
 await evaluate(`window.spokenMutations=[];for(const id of ${JSON.stringify(windows)}){const d=document.getElementById(id).contentWindow.document;let last='';new MutationObserver(()=>{const n=d.querySelector('.shell-announcement [data-announcement-sequence]');if(n&&n.dataset.announcementSequence!==last){last=n.dataset.announcementSequence;spokenMutations.push({id,sequence:last,text:n.textContent});}}).observe(d.body,{subtree:true,childList:true,characterData:true,attributes:true});}`);
 await metadata(first,true);const delivered=await observe();
 check('Refusal text and identity are delivered on one route',delivered.every(row=>row.live.length===(row.id==='popup'?1:0))&&delivered.find(row=>row.id==='popup').live[0].text===first.announcement.text&&delivered.find(row=>row.id==='popup').live[0].correlation===first.announcement.correlation,delivered);
 check('Persistent status remains readable and passive on mirrors',delivered.every(row=>row.visual.length>0&&row.visual.every(n=>n.live==='off')),delivered);
 check('Refusal does not relocate focused control',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===originalFocus'));
 const mutationCount=await evaluate('spokenMutations.length');await metadata(first,true);await metadata(first,false);
 check('Repeated exact delivery and publication do not repeat the live mutation',await evaluate('spokenMutations.length')===mutationCount&&mutationCount===1);
 await frame(fixture.secondFrame);await metadata(fixture.secondFrame,true);
 check('New refusal with the same words has its own identity and mutation',await evaluate('spokenMutations.length===2&&spokenMutations[0].text===spokenMutations[1].text&&spokenMutations[0].sequence!==spokenMutations[1].sequence'));
 check('New receipt keeps the same keyed focused control',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===originalFocus'));
 await frame(fixture.retiredFrame);await metadata(fixture.retiredFrame,false);const relocated=await observe();
 check('Owner retirement moves eligibility without replaying the prior refusal',relocated.every(row=>row.live.length===(row.id==='bar2'?1:0))&&relocated.find(row=>row.id==='bar2').live[0].text===''&&await evaluate('spokenMutations.length===2'),relocated);
 const stale={announcementProtocol:1,kind:'announcement-projection',recipient:{scope:scope(2),surface:'bar'},announcer:fixture.retiredFrame.announcer,publication:'1',lease:fixture.retiredFrame.frame.lease,message:{...fixture.secondFrame.announcement,sequence:'99'},deliver:true};
 await evaluate(`document.getElementById('bar2').contentWindow.receiveAnnouncement(${JSON.stringify(stale)})`);await sleep(50);
 check('Stale publication cannot announce in a newly selected host',await evaluate('spokenMutations.length===2'));
 const mirror={...stale,publication:fixture.retiredFrame.frame.publication,recipient:{scope:scope(1),surface:'bar'}};
 await evaluate(`document.getElementById('bar1').contentWindow.receiveAnnouncement(${JSON.stringify(mirror)})`);await sleep(50);
 check('Nonowner recipient cannot announce even with a forged delivery flag',await evaluate('spokenMutations.length===2&&document.getElementById("bar1").contentWindow.document.querySelectorAll("[aria-live=polite]").length===0'));
 check('Announcement projection submits no actions or focus effects', (await observe()).every(row=>row.packets.every(p=>!['surface-action','surface-query','window-effect','application-launch','surface-focus'].includes(p.kind))));
 report.observations={first:delivered,relocated,mutations:await evaluate('spokenMutations')};
 if(fs.existsSync(path.join(out,'notification-announcements.json'))){
  const notifications=JSON.parse(fs.readFileSync(path.join(out,'notification-announcements.json'),'utf8'));
  await call('Page.navigate',{url:base+'/qa/announcement-host.html?notifications'});
  await until('["bar1","bar2","popup"].every(id=>typeof document.getElementById(id)?.contentWindow?.receiveAnnouncement==="function")');
  await frame(notifications.notificationFrame);await metadata(notifications.notificationFrame,false);
  const button=identity=>`document.getElementById("popup").contentWindow.document.querySelector('[data-surface-control="${identity}"]')`;
  check('Session permission controls have readable names and unpressed state',await evaluate(`${button('notifications:dnd')}?.getAttribute('aria-pressed')==='false'&&${button('notifications:critical-interrupt')}?.getAttribute('aria-pressed')==='false'`));
  await evaluate(`${button('notifications:dnd')}.focus()`);
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter'});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter'});await sleep(50);
  check('Actual keyboard submits one current policy control',await evaluate('document.getElementById("popup").contentWindow.nativePackets.filter(p=>p.kind==="surface-action"&&p.id==="notifications:dnd").length===1'));
  await frame(notifications.dndFrame);await metadata(notifications.dndFrame,false);
  check('DND updates visual history without replaying a message or moving control focus',await evaluate(`${button('notifications:dnd')}.getAttribute('aria-pressed')==='true'&&document.getElementById("popup").contentWindow.document.activeElement===${button('notifications:dnd')}&&document.getElementById("popup").contentWindow.document.body.textContent.includes('Meeting 2')`) && (await observe()).every(row=>row.live.every(live=>!live.sequence)));
  await frame(notifications.politeFrame);await metadata(notifications.politeFrame,true);
  let observed=await observe();check('Unopted critical arrival has one polite owner',observed.every(row=>row.live.length===(row.id==='popup'?1:0))&&observed.find(row=>row.id==='popup').live[0].live==='polite');
  await frame(notifications.urgentFrame);await metadata(notifications.urgentFrame,true);
  observed=await observe();check('Opted critical arrival has one assertive owner',observed.every(row=>row.live.length===(row.id==='popup'?1:0))&&observed.find(row=>row.id==='popup').live[0].live==='assertive'&&observed.find(row=>row.id==='popup').live[0].correlation===notifications.urgentFrame.announcement.correlation);
  await metadata(notifications.urgentFrame,true);check('Repeated urgent delivery retains one serial',await evaluate('document.getElementById("popup").contentWindow.document.querySelectorAll("[data-announcement-sequence]").length===1'));
  await frame(notifications.ordinaryWithConsentFrame);await metadata(notifications.ordinaryWithConsentFrame,true);
  observed=await observe();check('Ordinary arrival remains polite with critical consent enabled',observed.find(row=>row.id==='popup').live[0].live==='polite');
  check('Arrival projections retain the focused policy control',await evaluate(`document.getElementById("popup").contentWindow.document.activeElement===${button('notifications:dnd')}`));
  report.notificationObservations=observed;
 }
 if(fs.existsSync(path.join(out,'adapter-announcements.json'))){
  const adapters=JSON.parse(fs.readFileSync(path.join(out,'adapter-announcements.json'),'utf8'));
  await call('Page.navigate',{url:base+'/qa/announcement-host.html?adapters'});
  await until('["bar1","bar2","popup"].every(id=>typeof document.getElementById(id)?.contentWindow?.receiveAnnouncement==="function")');
  await frame(adapters.openedFrame);await metadata(adapters.openedFrame,false);
  const button=`document.getElementById("popup").contentWindow.document.querySelector('[data-surface-control="notifications:refresh"]')`;
  await evaluate(`window.adapterFocus=${button};adapterFocus.focus()`);
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter'});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter'});await sleep(50);
  check('Keyboard refresh submits exactly one current read control',await evaluate('document.getElementById("popup").contentWindow.nativePackets.filter(p=>p.kind==="surface-action"&&p.id==="notifications:refresh").length===1'));
  await frame(adapters.failedFrame);await metadata(adapters.failedFrame,true);
  let observed=await observe();
  check('Unavailable adapter uses exactly one polite owner with real correlation',observed.every(row=>row.live.length===(row.id==='popup'?1:0))&&observed.find(row=>row.id==='popup').live[0].live==='polite'&&observed.find(row=>row.id==='popup').live[0].correlation===adapters.failedFrame.announcement.correlation);
  check('Failed receipt retains actual keyed refresh node',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===adapterFocus&&adapterFocus.isConnected&&!adapterFocus.disabled'));
  const firstSerial=adapters.failedFrame.announcement.sequence;
  await metadata(adapters.failedFrame,true);await metadata(adapters.failedFrame,false);
  check('Repeated adapter delivery retains one message identity',await evaluate(`document.getElementById("popup").contentWindow.document.querySelectorAll('[data-announcement-sequence="${firstSerial}"]').length===1`));
  await frame(adapters.retryPendingFrame);await metadata(adapters.retryPendingFrame,false);
  check('Pending read retains focused refresh control and visible progress',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===adapterFocus&&!adapterFocus.disabled&&adapterFocus.textContent.includes("Reading current targets")'));
  await frame(adapters.retryFrame);await metadata(adapters.retryFrame,true);
  check('Explicit retry has fresh polite message without focus movement',await evaluate(`document.getElementById("popup").contentWindow.document.activeElement===adapterFocus&&document.getElementById("popup").contentWindow.document.querySelector('[data-announcement-sequence="${adapters.retryFrame.announcement.sequence}"]')!==null`)&&adapters.retryFrame.announcement.sequence!==firstSerial);
  await frame(adapters.recoveredFrame);await metadata(adapters.recoveredFrame,false);
  check('Successful recovery updates current state without replay or focus movement',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===adapterFocus&&adapterFocus.isConnected&&!adapterFocus.disabled')&&adapters.recoveredFrame.announcement.sequence===adapters.retryFrame.announcement.sequence);
  report.adapterObservations=await observe();
 }
 if(fs.existsSync(path.join(out,'notification-relevance.json'))){
  const relevance=JSON.parse(fs.readFileSync(path.join(out,'notification-relevance.json'),'utf8'));
  await call('Page.navigate',{url:base+'/qa/announcement-host.html?relevance'});
  await until('["bar1","bar2","popup"].every(id=>typeof document.getElementById(id)?.contentWindow?.receiveAnnouncement==="function")');
  await frame(relevance.readyFrame);await metadata(relevance.readyFrame,false);
  const button=`document.getElementById("popup").contentWindow.document.querySelector('[data-surface-control="notification:9:1:invoke:open"]')`;
  await evaluate(`window.expiryFocus=${button};expiryFocus.focus()`);await sleep(80);
  check('Actual focused notification submits scoped passive fact',await evaluate('document.getElementById("popup").contentWindow.nativePackets.some(p=>p.kind==="surface-notification-focus"&&p.id==="notification:9:1:invoke:open"&&p.surface==="popup")'));
  await frame(relevance.focusedFrame);await metadata(relevance.focusedFrame,false);
  check('Focus observation keeps keyed node without message',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===expiryFocus')&&relevance.focusedFrame.announcement===null);
  await frame(relevance.pendingFrame);await metadata(relevance.pendingFrame,false);
  check('Pending action keeps focus with honest unavailable semantics',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===expiryFocus&&!expiryFocus.disabled&&expiryFocus.getAttribute("aria-disabled")==="true"'));
  await frame(relevance.pendingExpiredFrame);await metadata(relevance.pendingExpiredFrame,true);
  const observed=await observe();
  check('Focused expiry uses one polite owner and exact identity',observed.every(row=>row.live.length===(row.id==='popup'?1:0))&&observed.find(row=>row.id==='popup').live[0].live==='polite'&&observed.find(row=>row.id==='popup').live[0].correlation===relevance.expiredFrame.announcement.correlation);
  check('Expired action remains the same focused unavailable node',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===expiryFocus&&expiryFocus.isConnected&&!expiryFocus.disabled&&expiryFocus.getAttribute("aria-disabled")==="true"&&expiryFocus.dataset.focusOnly==="true"&&expiryFocus.textContent.includes("expired")'),await evaluate('({same:document.getElementById("popup").contentWindow.document.activeElement===expiryFocus,connected:expiryFocus.isConnected,disabled:expiryFocus.disabled,aria:expiryFocus.getAttribute("aria-disabled"),focusOnly:expiryFocus.dataset.focusOnly,text:expiryFocus.textContent,active:document.getElementById("popup").contentWindow.document.activeElement?.outerHTML})'));
  const before=await evaluate('document.getElementById("popup").contentWindow.nativePackets.filter(p=>p.kind==="surface-action").length');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter'});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter'});await sleep(80);
  check('Retained unavailable control cannot submit an action',await evaluate('document.getElementById("popup").contentWindow.nativePackets.filter(p=>p.kind==="surface-action").length')===before);
  await frame(relevance.refusedFrame);await metadata(relevance.refusedFrame,true);
  check('Expired-action refusal retains keyed focus and polite message',await evaluate('document.getElementById("popup").contentWindow.document.activeElement===expiryFocus')&&(await observe()).find(row=>row.id==='popup').live[0].correlation===relevance.refusedFrame.announcement.correlation);
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab'});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab'});await sleep(80);
  check('User can navigate away from unavailable control',await evaluate('document.getElementById("popup").contentWindow.document.activeElement!==expiryFocus'));
  await frame(relevance.clearedFrame);await metadata(relevance.clearedFrame,false);
  check('Leaving unavailable control retires it',await evaluate('!expiryFocus.isConnected'));
  report.notificationRelevanceObservations=observed;
 }
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'announcement-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
