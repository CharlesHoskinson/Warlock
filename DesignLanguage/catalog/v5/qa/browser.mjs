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
async function click(selector){await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);await sleep(60);}
async function route(name){await evaluate('location.hash='+JSON.stringify(name));await until('!!document.querySelector("main h1") && location.hash === '+JSON.stringify('#'+name));await sleep(100);}
async function viewport(width,height=980){await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await sleep(80);}
async function capture(name){await evaluate('document.fonts.ready');const r=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.data,'base64'));report.captures.push(name+'.png');}
async function observation(){return evaluate('window.fixtureObservation');}
try{
 let match;for(let i=0;i<100;i++){match=stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);if(match)break;if(browser.exitCode!==null)throw Error('Browser exited '+browser.exitCode+' '+stderr);await sleep(30);}if(!match)throw Error('No DevTools endpoint '+stderr);
 const endpoint=match[1],info=await fetch(endpoint.replace('ws:','http:').replace(/\/devtools\/.*/, '/json/version')).then(r=>r.json());report.browser=info;report.binary=binary;
 ws=new WebSocket(endpoint);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 ws.onmessage=event=>{const m=JSON.parse(event.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}}
  else if(m.method==='Runtime.exceptionThrown')report.errors.push(m.params.exceptionDetails);
  else if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')report.errors.push(m.params.entry);
  else if(m.method==='Network.requestWillBeSent'){const url=m.params.request.url;if(!url.startsWith(base)&&!url.startsWith('elm-shell://preview/'+'1'.repeat(64))&&!url.startsWith('data:'))report.externalRequests.push(url);}
 };
 const target=await call('Target.createTarget',{url:'about:blank'},null);session=(await call('Target.attachToTarget',{targetId:target.targetId,flatten:true},null)).sessionId;
 await call('Page.enable');await call('Runtime.enable');await call('Log.enable');await call('Network.enable');await viewport(1440);await call('Page.navigate',{url:base+'/index.html'});await until('!!document.querySelector("main article")');await sleep(200);
 check('No external asset request at initial load',report.externalRequests.length===0);
 check('49 source modules, 14 current component families',await evaluate('WARLOCK_CATALOG.registry.modules.length===49 && WARLOCK_CATALOG.registry.components.length===14'));
 await capture('desktop-overview');
 const routes=await evaluate('[...document.querySelectorAll("#nav a")].map(a=>a.hash.slice(1))');
 for(const r of routes){await route(r);check(r+' has readable heading',await evaluate('document.querySelector("main h1").textContent.trim().length>0'));if(r.startsWith('component/'))check(r+' six sections',await evaluate('document.querySelectorAll("main section>h2").length===6'));check(r+' no desktop overflow',await evaluate('document.documentElement.scrollWidth<=innerWidth'));}
 await route('component/menu');await until('window.fixtureObservation?.menuStatus==="Ready"');
 check('Real source publishes disabled Size',await evaluate(`document.querySelector('[data-surface-control="demo-menu:3"]').disabled`));
 await click('[data-surface-control="demo-menu:0"]');await until('window.fixtureObservation?.outstanding===1');check('Activation dispatches one intent',await evaluate('fixtureObservation.effects.dispatches===1'));
 check('Pending disables all operation rows',await evaluate('[...document.querySelectorAll("[data-surface-control]")].every(b=>b.disabled)'));
 await click('[data-outcome="unknown"]');await until('fixtureObservation.menuStatus.includes("unconfirmed")');await capture('desktop-menu-unknown');
 await click('[data-surface-control="demo-menu:0"]');check('Unknown cannot repeat an intent',(await observation()).outstanding===1);
 await click('[data-dismiss]');await until('fixtureObservation.menuStatus.startsWith("Menu closed")');check('Dismissal retains unresolved intent',(await observation()).outstanding===1);
 await click('[data-outcome="committed"]');await until('fixtureObservation.outstanding===0');check('Correlated receipt settles dismissed intent',true);
 await click('#fixture-reset');await until('fixtureObservation.menuStatus==="Ready"');
 await evaluate(`document.querySelector('[data-surface-control="demo-menu:0"]').focus()`);
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'End',code:'End'});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'End',code:'End'});await sleep(80);
 check('End routes through real Menu.Navigate',await evaluate('document.querySelector("[aria-current=true]").dataset.surfaceControl==="demo-menu:11"'));
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter'});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter'});await until('fixtureObservation.outstanding===1');check('Enter activates source-selected item once',true);
 await route('component/window-group');await until('fixtureObservation?.topic==="bar"');
 for(const [profile,expected] of [['active','Request minimize'],['minimized','Request restore'],['inactive','Request activate'],['multiple','Open window picker'],['unavailable','Unavailable'],['empty','Unavailable']]){
  await evaluate(`document.querySelector('#profile').value=${JSON.stringify(profile)};document.querySelector('#profile').dispatchEvent(new Event('change'))`);await until('fixtureObservation.decision==='+JSON.stringify(expected));check('Taskbar.primary False '+profile,true);
 }
 await route('component/preview');await until('fixtureObservation?.preview?.state==="unavailable"');await click('[data-preview=load]');await until('fixtureObservation.preview.state==="loading"');check('Request creates typed acquire',await evaluate('fixtureObservation.effects.some(e=>e.kind==="acquire")'));
 await click('[data-preview=frame]');await until('fixtureObservation.preview.state==="live"');check('Explicit offered fixture produces live source state',await evaluate('!!fixtureObservation.preview.accepted'));
 await click('[data-preview=historical]');await until('fixtureObservation.preview.state==="historical"');check('Historical preserves authorized accepted packet',await evaluate('!!fixtureObservation.preview.accepted'));await sleep(100);await capture('desktop-preview-historical');
 check('Fixture image mapping is explicit',await evaluate('document.querySelector(".preview-image").dataset.fixtureOriginalUri.startsWith("elm-shell://preview/")'));
 await click('[data-preview=lock]');await until('fixtureObservation.preview.state==="unavailable"');check('Lock revokes pixels and requests release',await evaluate('!document.querySelector(".preview-image") && fixtureObservation.effects.some(e=>e.kind==="release")'));
 await click('#fixture-reset');await click('[data-preview=load]');await click('[data-preview=frame]');await click('[data-preview=expire]');await until('fixtureObservation.preview.state==="unavailable"');check('Explicit fixture clock expires accepted pixels',await evaluate('fixtureObservation.effects.some(e=>e.kind==="release")'));
 await route('tokens');await evaluate('document.querySelector("#theme").value="light";document.querySelector("#theme").dispatchEvent(new Event("change"))');check('Appearance changes without route change',await evaluate('document.documentElement.dataset.theme==="light" && location.hash==="#tokens"'));await capture('desktop-tokens-light');
 await evaluate('document.querySelector("#search").value="unknown";document.querySelector("#search").dispatchEvent(new Event("input"))');check('Search finds relevant component states',await evaluate(`document.querySelector('#nav a[href="#component/menu"]')!==null`));
 await evaluate('document.querySelector("#search").value="no-such-widget-xyz";document.querySelector("#search").dispatchEvent(new Event("input"))');check('Search explains empty results',await evaluate('document.querySelector("#nav .empty").textContent.includes("No matching")'));
 await evaluate('document.querySelector("#search").value="";document.querySelector("#search").dispatchEvent(new Event("input"))');
 await viewport(390,844);await route('overview');check('Mobile navigation is a closed disclosure',await evaluate('!document.querySelector("#navigation").open'));await capture('mobile-overview');
 await viewport(320,760);await route('component/menu');check('320px text and controls do not overflow',await evaluate('document.documentElement.scrollWidth<=innerWidth'));await capture('narrow-menu');
 await viewport(1440);await call('Emulation.setEmulatedMedia',{features:[{name:'forced-colors',value:'active'},{name:'prefers-reduced-motion',value:'reduce'}]});await evaluate('document.querySelector("#fixture-reset").focus()');
 check('Forced colors and reduced motion active',await evaluate('matchMedia("(forced-colors:active)").matches && matchMedia("(prefers-reduced-motion:reduce)").matches'));await capture('forced-colors-focus');
 await call('Emulation.setEmulatedMedia',{features:[]});await route('library');await click('#library-inspect');check('Proposed specimen action gives local feedback',await evaluate('document.querySelector("#library-result").textContent.includes("No desktop action")'));
 // Browser coverage is deliberately scoped; product renderer findings are not repaired by tests.
 check('No off-origin network requests',report.externalRequests.length===0,report.externalRequests);
 check('No uncaught script exceptions',report.errors.filter(e=>e.exception||e.exceptionId).length===0,report.errors);
 report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
