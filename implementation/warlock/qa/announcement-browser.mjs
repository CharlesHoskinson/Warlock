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
 await call('Page.navigate',{url:base+'/qa/announcement-host.html'});await until('["bar1","bar2","popup"].every(id=>typeof document.getElementById(id).contentWindow.receiveAnnouncement==="function")');
 const windows=['bar1','bar2','popup'];
 async function frame(value){await evaluate(`for(const id of ${JSON.stringify(windows)})document.getElementById(id).contentWindow.receivePresentation(${JSON.stringify(value.frame)});`);await sleep(80);}
 function scope(id){return {id:String(id),generation:'1'};}
 async function metadata(value,deliver=false){for(const id of windows){const recipient={scope:scope(id==='bar2'?2:1),surface:id==='popup'?'popup':'bar'};
  const active=JSON.stringify(recipient)===JSON.stringify(value.announcer);
  const packet={announcementProtocol:1,kind:'announcement-projection',recipient,announcer:value.announcer,publication:value.frame.publication,lease:value.frame.lease,message:value.announcement,deliver:deliver&&active};
  await evaluate(`document.getElementById(${JSON.stringify(id)}).contentWindow.receiveAnnouncement(${JSON.stringify(packet)})`);
 }await sleep(80);}
 async function observe(){return evaluate(`(()=>{return ${JSON.stringify(windows)}.map(id=>{const w=document.getElementById(id).contentWindow,d=w.document;return {id,live:[...d.querySelectorAll('[aria-live="polite"]')].map(n=>({text:n.textContent,sequence:n.querySelector('[data-announcement-sequence]')?.dataset.announcementSequence||null,correlation:n.querySelector('[data-announcement-correlation]')?.dataset.announcementCorrelation||null})),visual:[...d.querySelectorAll('.surface-status,.surface-popup>p[role="status"]')].map(n=>({text:n.textContent,live:n.getAttribute('aria-live')})),focus:d.activeElement?.dataset.surfaceControl||null,packets:w.nativePackets||[]};});})()`);}
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
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'announcement-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
