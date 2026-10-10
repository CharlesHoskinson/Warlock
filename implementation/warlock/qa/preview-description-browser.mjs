import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const [base,out,binary]=process.argv.slice(2), report={passed:false,checks:[],captures:[],states:[],errors:[],externalRequests:[],nativeAcceptance:false,fullReleaseAccepted:false};
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



 await call('Page.enable');await call('Runtime.enable');await call('Accessibility.enable');await viewport(640,620);
 const fixture=JSON.parse(fs.readFileSync(path.join(out,'preview-states.json'),'utf8'));
 const frame=fixture.frame, chosenControl=frame.popup.find(row=>row.id==='family:1');
 check('Original identity-bound state fixture is admitted',!!chosenControl&&fixture.checks.foreignIncarnationCannotBorrowPixels&&fixture.checks.newLeaseHidesOldFrame);
 await call('Page.navigate',{url:base+'/qa/preview-description.html'});await until('typeof receiveVisual==="function"');
 const binding={lifetime:'1',session:'1',frontend:'1'};let sequence=0;
 function packet(visual,surface=frame){return {channelProtocol:1,kind:'native-preview-projection',binding,receiverEpoch:'1',rendererLease:'1',visualSequence:String(++sequence),visual:{visualProtocol:1,kind:'native-preview-visual',binding,receiverEpoch:'1',surface,previews:surface.popup.map(row=>({identity:row.id,visual:row.id===chosenControl.id?visual:{kind:'hidden'}}))}};}
 async function send(value){await evaluate('receiveVisual('+JSON.stringify(value)+')');await until('previewReceipts.at(-1)?.visualSequence==='+JSON.stringify(value.visualSequence));await sleep(40);}
 async function describe(){const {nodes}=await call('Accessibility.getFullAXTree');return nodes.filter(node=>!node.ignored&&node.name?.value===chosenControl.ariaLabel&&node.role?.value==='button').map(node=>({name:node.name.value,role:node.role.value,description:node.description?.value||'',focused:node.properties?.find(p=>p.name==='focused')?.value.value||false}));}
 await send(packet(fixture.states[0]));
 await call('Page.bringToFront');
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
 await until('document.activeElement?.dataset.surfaceControl==="control:close"');
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
 await until('document.activeElement?.dataset.surfaceControl==="family:1"');
 const initial=await evaluate(`(()=>{window.initialButton=document.querySelector('[data-surface-control="family:1"]');const r=initialButton.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};})()`);
 const cases=[
  ['loading',fixture.states[0],'Preview loading'],
  ['live',fixture.states[1],'Live preview; Window family'],
  ['historical',fixture.states[2],'Historical preview; Window family'],
  ['unavailable',fixture.states[3],'Preview unavailable'],
  ['fallback',{kind:'fallback'},'Preview unavailable'],
  ...[['capacity','Waiting for preview capacity'],['waiting','Waiting for preview'],['expired','Preview request expired'],['conflict','Preview request changed'],['exhausted','Preview unavailable']].map(([state,label])=>[state,{kind:'local',state,title:state==='exhausted'?label:'Document 1'},label]),
  ['hidden',{kind:'hidden'},'']
 ];
 for(const [state,visual,description] of cases){
  await send(packet(visual));const ax=await describe();
  check(state+': named focused control carries exact passive description',ax.length===1&&ax[0].description===description&&ax[0].focused,ax);
  const observed=await evaluate(`(()=>{const b=document.querySelector('[data-surface-control="family:1"]'),r=b.getBoundingClientRect(),ref=b.getAttribute('aria-describedby');return {same:b===initialButton,focused:document.activeElement===b,rect:{x:r.x,y:r.y,width:r.width,height:r.height},live:b.querySelectorAll('[aria-live],[role="status"]').length,description:ref?document.getElementById(ref)?.textContent:'',visibleState:b.querySelector('.preview-state')?.textContent||'',title:b.querySelector('.preview-title')?.textContent||'',hiddenDescription:ref?getComputedStyle(document.getElementById(ref)).display==='none':true,images:[...b.querySelectorAll('img')].every(n=>n.alt==='')};})()`);
  check(state+': focus and reserved chosenControl geometry are stable',observed.same&&observed.focused&&JSON.stringify(observed.rect)===JSON.stringify(initial),observed);
  check(state+': no preview live region and description is outside layout',observed.live===0&&observed.hiddenDescription&&observed.description===description&&observed.images,observed);
  if(state!=='hidden')check(state+': visible state matches accessible state',description.startsWith(observed.visibleState)&&observed.visibleState.length>0,observed);
  if(state==='fallback'||state==='exhausted')check(state+': unavailable is rendered once',observed.visibleState==='Preview unavailable'&&observed.title==='');
  if(state==='waiting')check('Real window title remains visible',observed.title==='Document 1');
  report.states.push({state,accessible:ax,observed});
  if(state==='loading'||state==='unavailable')await capture(state);
 }
 // IDs are externally supplied render data; a control may use the normal
 // description prefix. Relationships must still point to only its description.
 const collision=structuredClone(frame);collision.popup.at(-1).domId='preview-description-'+chosenControl.domId;
 await send(packet({kind:'fallback'},collision));
 check('Description IDs cannot alias a supplied control ID',await evaluate(`(()=>{const b=document.querySelector('[data-surface-control="family:1"]'),ref=b.getAttribute('aria-describedby');return ref!==${JSON.stringify(collision.popup.at(-1).domId)}&&[...document.querySelectorAll('[id]')].filter(n=>n.id===ref).length===1&&document.getElementById(ref).textContent==='Preview unavailable';})()`));
 const before=await describe(), foreign=packet({kind:'hidden'},collision);foreign.binding={...binding,frontend:'2'};
 await evaluate('receiveVisual('+JSON.stringify(foreign)+')');await sleep(40);
 check('Foreign renderer binding cannot erase focused preview description',JSON.stringify(await describe())===JSON.stringify(before));
 const accepted=packet({kind:'fallback'},collision);await send(accepted);const receiptCount=await evaluate('previewReceipts.length');
 await evaluate('receiveVisual('+JSON.stringify(accepted)+')');await until('previewReceipts.length==='+String(receiptCount+1));
 check('Repeated exact projection keeps the same focused description',JSON.stringify(await describe())===JSON.stringify(before));
 const closed={...frame,publication:'999',mode:'closed',popup:[]};await send(packet({kind:'hidden'},closed));
 check('Retired picker exports no stale descriptions or controls',await evaluate('document.querySelectorAll(".preview-description,[data-surface-control]").length===0'));
 check('Component inspection submits no window effects',await evaluate('nativePackets.length===0'));
 check('No browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'preview-description-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
