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
 const packet=JSON.parse(fs.readFileSync(path.join(out,'settings.json'),'utf8'));
 await evaluate('receivePresentation('+JSON.stringify(packet.frame)+')');
 await until(`document.querySelector('.surface-popup[data-mode="settings"]')?.dataset.publication==="1"`);
 check('Actual settings popup renders named controls',await evaluate(`document.querySelector("h1").textContent==="Settings" && JSON.stringify([...document.querySelectorAll('[data-surface-control]')].map(b=>b.dataset.surfaceControl))===${JSON.stringify(JSON.stringify(packet.frame.popup.filter(row=>!row.id.startsWith('settings:help:text:')).map(row=>row.id)))}`));
 check('Loaded appearance is current, not an unsaved draft',await evaluate(`document.documentElement.dataset.theme==="night" && document.documentElement.dataset.textScale==="100"`));
 check('Save disabled without changes',await evaluate(`document.querySelector('[data-surface-control="settings:save"]').disabled`));
 check('Current theme and scale exposed semantically',await evaluate(`document.querySelector('[data-surface-control="settings:theme:night"]').getAttribute('aria-current')==='true' && document.querySelector('[data-surface-control="settings:scale:100"]').getAttribute('aria-current')==='true'`));
 async function key(key){await call('Input.dispatchKeyEvent',{type:'keyDown',key,code:key});await call('Input.dispatchKeyEvent',{type:'keyUp',key,code:key});await sleep(60);}
 await evaluate(`document.querySelector('[data-surface-control="settings:theme:night"]').focus()`);
 await key('End');check('End reaches refresh and skips disabled Save',await evaluate(`document.activeElement.dataset.surfaceControl==='settings:refresh'`));
 await key('Home');check('Home reveals Close',await evaluate(`document.activeElement.dataset.surfaceControl==='control:close' && document.activeElement.getBoundingClientRect().top>=0`));
 await key('ArrowDown');check('Arrow reaches dismissible help',await evaluate(`document.activeElement.dataset.surfaceControl==='settings:help' && document.activeElement.getAttribute('aria-expanded')==='true'`));
 check('Guidance is readable text rather than disabled controls',await evaluate(`document.querySelectorAll('[data-settings-help]').length===3 && [...document.querySelectorAll('[data-settings-help]')].every(row=>row.tagName==='P' && !row.hasAttribute('disabled') && !row.hasAttribute('data-surface-control'))`));
 await evaluate(`document.querySelector('[data-surface-control="settings:theme:night"]').focus()`);
 await key('ArrowDown');await key('Enter');check('Keyboard theme dispatch uses exact current identity once',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action' && p.id==='settings:theme:dawn' && p.publication==='1' && p.lease==='1').length===1`));
 check('Dispatch alone cannot optimistically apply theme',await evaluate(`document.documentElement.dataset.theme==='night'`));
 await evaluate('receivePresentation('+JSON.stringify(packet.savedFrame)+')');
 await until(`document.documentElement.dataset.theme==='dawn' && document.documentElement.dataset.textScale==='150'`);
 check('Committed text size applies to real rendering',await evaluate(`getComputedStyle(document.body).fontSize==='24px'`));
 check('Dawn colors apply to actual document',await evaluate(`getComputedStyle(document.body).backgroundColor==='rgb(237, 242, 247)' && getComputedStyle(document.body).color==='rgb(23, 37, 54)'`));
 check('Committed selected state follows receipt',await evaluate(`document.querySelector('[data-surface-control="settings:theme:dawn"]').getAttribute('aria-current')==='true' && document.querySelector('[data-surface-control="settings:scale:150"]').getAttribute('aria-current')==='true'`));
 await viewport(320,220);await evaluate(`document.querySelector('[data-surface-control="settings:theme:dawn"]').focus()`);await key('End');
 check('Enlarged small viewport reveals last control',await evaluate(`document.activeElement.dataset.surfaceControl==='settings:refresh' && document.activeElement.getBoundingClientRect().bottom<=innerHeight+1`));
 await key('Home');const count=await evaluate(`nativePackets.filter(p=>p.kind==='surface-action' && p.id==='control:close').length`);await key('Escape');
 check('Escape submits dismissal after real key release',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action' && p.id==='control:close' && p.publication==='2').length`)==count+1);
 await capture('settings-dawn-enlarged');
 const luminance=rgb=>{const values=rgb.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return .2126*values[0]+.7152*values[1]+.0722*values[2];};
 const contrast=(a,b)=>{const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
 report.appearanceFixtures=[];
 for(const frame of packet.appearanceFrames){
  await call('Emulation.setEmulatedMedia',{features:[{name:'forced-colors',value:'none'}]});
  await viewport(480,360);await evaluate('receivePresentation('+JSON.stringify(frame)+')');
  await until(`document.querySelector('.surface-popup')?.dataset.publication===${JSON.stringify(frame.publication)} && document.documentElement.dataset.theme===${JSON.stringify(frame.appearance.theme)} && document.documentElement.dataset.textScale===${JSON.stringify(String(frame.appearance.textScale))}`);
  await evaluate(`document.querySelector('[data-surface-control="control:close"]').focus()`);await key('End');
  const observed=await evaluate(`(()=>{const a=document.activeElement,s=getComputedStyle(a),b=getComputedStyle(document.body),r=a.getBoundingClientRect();return {theme:document.documentElement.dataset.theme,scale:document.documentElement.dataset.textScale,foreground:s.color,background:s.backgroundColor,bodyForeground:b.color,bodyBackground:b.backgroundColor,outlineColor:s.outlineColor,outlineWidth:s.outlineWidth,outlineOffset:s.outlineOffset,fontSize:b.fontSize,identity:a.dataset.surfaceControl,visible:r.x>=0&&r.y>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1,hasName:!!a.getAttribute('aria-label')};})()`);
  const ratio=contrast(observed.foreground,observed.background);report.appearanceFixtures.push({...observed,contrast:ratio});
  check('Readable enlarged named target '+observed.theme+'/'+observed.scale,ratio>=4.5 && observed.visible && observed.hasName && observed.identity==='settings:refresh' && Number.parseFloat(observed.fontSize)===16*frame.appearance.textScale/100,observed);
  if(observed.theme==='high-contrast')check('Inset high contrast focus '+observed.scale,observed.outlineColor==='rgb(255, 255, 0)' && observed.outlineWidth==='3px' && observed.outlineOffset==='-4px' && contrast(observed.outlineColor,observed.background)>=3,observed);
 }
 await capture('settings-high-contrast-enlarged');
 await call('Emulation.setEmulatedMedia',{features:[{name:'forced-colors',value:'active'}]});
 await evaluate(`document.querySelector('[data-surface-control="control:close"]').focus()`);await key('End');
 const forced=await evaluate(`(()=>{const s=getComputedStyle(document.activeElement);return {foreground:s.color,background:s.backgroundColor,outlineColor:s.outlineColor,outlineWidth:s.outlineWidth};})()`);
 check('Forced color content and focus remain readable',contrast(forced.foreground,forced.background)>=4.5 && contrast(forced.outlineColor,forced.background)>=3 && Number.parseFloat(forced.outlineWidth)>=2,forced);
 report.forcedColors=forced;await capture('settings-high-contrast-forced-colors');
 await call('Emulation.setEmulatedMedia',{features:[{name:'forced-colors',value:'none'}]});
 await evaluate('receivePresentation('+JSON.stringify({...packet.savedFrame,publication:'15'})+')');await until(`document.documentElement.dataset.theme==='dawn'`);
 const invalid=structuredClone(packet.savedFrame);invalid.publication='16';invalid.appearance.textScale=77;await evaluate('receivePresentation('+JSON.stringify(invalid)+')');await sleep(80);
 check('Invalid presentation scale cannot change appearance',await evaluate(`document.querySelector('.surface-popup')===null && document.documentElement.dataset.textScale==='150'`));
 await evaluate('receivePresentation('+JSON.stringify(packet.helpDismissedFrame)+')');await until(`document.querySelector('.surface-popup')?.dataset.publication==='20'`);
 await evaluate(`document.querySelector('[data-surface-control="settings:help"]').focus()`);
 check('Dismissed help keeps a keyboard reachable reopening control',await evaluate(`document.querySelectorAll('[data-settings-help]').length===0 && document.activeElement.getAttribute('aria-expanded')==='false' && document.activeElement.textContent.includes('Show help')`));
 await key('Enter');check('Help Enter emits one current scoped action',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action' && p.id==='settings:help' && p.publication==='20' && p.lease==='1').length===1`));
 await evaluate('receivePresentation('+JSON.stringify(packet.helpReopenedFrame)+')');await until(`document.querySelector('.surface-popup')?.dataset.publication==='21'`);
 check('Reopening help retains the same focused identity and reveals it',await evaluate(`document.activeElement.dataset.surfaceControl==='settings:help' && document.activeElement.getAttribute('aria-expanded')==='true' && document.querySelectorAll('[data-settings-help]').length===3 && document.activeElement.getBoundingClientRect().top>=0 && document.activeElement.getBoundingClientRect().bottom<=innerHeight+1`));
 await key('End');check('Help does not trap preference navigation',await evaluate(`document.activeElement.dataset.surfaceControl==='settings:refresh'`));
 await capture('settings-keyboard-help');
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'settings-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
