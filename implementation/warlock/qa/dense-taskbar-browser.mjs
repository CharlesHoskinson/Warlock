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

 await call('Page.enable');await call('Runtime.enable');await viewport(480,96);await call('Page.navigate',{url:base+'/qa/dense.html'});await until('!!window.receivePresentation');
 let pub=0;
 async function show(disabled=-1){const frame={surfaceProtocol:2,publication:String(++pub),lease:'0',mode:'closed',status:'Ready',popup:[],bar:Array.from({length:100},(_,i)=>({id:'bar:pin:app-'+i,domId:'pin:'+pub+':'+i,label:'Application '+i,ariaLabel:'Activate Application '+i,detail:'Pinned; Open',enabled:i!==disabled}))};await evaluate('receivePresentation('+JSON.stringify(frame)+')');await until('document.querySelector(".surface-bar")?.dataset.publication==='+JSON.stringify(frame.publication));await sleep(60);}
 async function key(value){await call('Input.dispatchKeyEvent',{type:'keyDown',key:value,code:value});await call('Input.dispatchKeyEvent',{type:'keyUp',key:value,code:value});await sleep(40);}
 const state=()=>evaluate(`(()=>{const a=document.querySelector('.surface-actions'),f=document.activeElement,r=f.getBoundingClientRect(),v=a.getBoundingClientRect();return {id:f.dataset.surfaceControl,domId:f.id,x:r.x,right:r.right,top:r.top,bottom:r.bottom,left:v.left,viewRight:v.right,viewBottom:v.bottom,scroll:a.scrollLeft,scrollWidth:a.scrollWidth,width:a.clientWidth,font:getComputedStyle(document.body).fontSize,shadow:getComputedStyle(f).boxShadow,order:[...a.children].map(b=>b.dataset.surfaceControl)};})()`);
 const visible=s=>s.x>=s.left-.5&&s.right<=s.viewRight+.5&&s.top>=0&&s.bottom<=s.viewBottom+.5;
 await show();await evaluate(`document.querySelector('[data-surface-control="bar:pin:app-0"]').focus()`);const first=await state();check('Enlarged first item visible with bounded overflow',first.font==='24px'&&visible(first)&&first.scrollWidth>first.width,first);
 await key('End');const last=await state();check('End reveals last item',last.id==='bar:pin:app-99'&&visible(last),last);await capture('dense-last');
 await show(98);await key('ArrowLeft');const skipped=await state();check('Arrow traversal skips disabled controls without changing order',skipped.id==='bar:pin:app-97'&&visible(skipped)&&JSON.stringify(skipped.order)===JSON.stringify(first.order),skipped);
 await key('Home');check('Home reveals first item',(await state()).id==='bar:pin:app-0'&&visible(await state()));
 await key('End');await show();const changed=await state();check('Publication changes keep the logical selected identity',changed.id==='bar:pin:app-99'&&changed.domId==='pin:3:99'&&visible(changed),changed);
 for(const width of [960,320,640]){await viewport(width,96);const current=await state();check('Resize '+width+' preserves order and visible selection',current.id==='bar:pin:app-99'&&visible(current)&&JSON.stringify(current.order)===JSON.stringify(first.order),current);}
 await call('Input.dispatchMouseEvent',{type:'mouseWheel',x:600,y:30,deltaX:0,deltaY:-30000});await sleep(70);check('Vertical wheel reaches the beginning',(await state()).scroll===0,await state());
 await show();check('Observation publications do not undo manual scrolling',(await state()).scroll===0,await state());
 await key('End');check('Keyboard navigation reveals selection after manual scrolling',visible(await state()));
 await show(99);await show();check('A transiently disabled selection returns by current identity',(await state()).id==='bar:pin:app-99'&&visible(await state()));
 await call('Emulation.setEmulatedMedia',{features:[{name:'forced-colors',value:'active'}]});await key('Home');check('Forced colors retain a visible focus outline',await evaluate(`getComputedStyle(document.activeElement).outlineStyle!=='none'`));
 check('Scrolling and navigation never emit activation',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action').length===0`));await call('Emulation.setEmulatedMedia',{features:[]});await viewport(480,420);await call('Page.navigate',{url:base+'/qa/dense-picker.html'});await until('!!window.receivePresentation');
 let pickerPub=0;
 async function showPicker(disabled=-1,lease='1',reverse=false){
  const members=Array.from({length:20},(_,i)=>({id:'family:'+i,domId:'picker:'+String(pickerPub+1)+':'+i,label:'Document '+i,ariaLabel:'Activate Document '+i,detail:'Open',enabled:i!==disabled}));
  if(reverse)members.reverse();
  const frame={surfaceProtocol:2,publication:String(++pickerPub),lease,mode:'picker',status:'Choose a window',bar:[],popup:[{id:'control:close',domId:'picker-close:'+pickerPub,label:'Close',ariaLabel:'Close picker',detail:'',enabled:true},...members]};
  await evaluate('receivePresentation('+JSON.stringify(frame)+')');await until('document.querySelector(".surface-popup")?.dataset.publication==='+JSON.stringify(frame.publication));await sleep(70);
 }
 const pickerState=()=>evaluate(`(()=>{const n=document.querySelector('.surface-popup'),f=document.activeElement,r=f.getBoundingClientRect();return {id:f.dataset.surfaceControl,domId:f.id,top:r.top,bottom:r.bottom,height:innerHeight,font:getComputedStyle(document.body).fontSize,scroll:n.scrollTop,scrollHeight:n.scrollHeight,clientHeight:n.clientHeight,order:[...n.querySelectorAll('[data-surface-control]')].map(b=>b.dataset.surfaceControl)};})()`);
 const pickerVisible=s=>s.top>=-.5&&s.bottom<=s.height+.5;
 await showPicker();await evaluate(`document.querySelector('[data-surface-control="family:0"]').focus()`);
 const pickerFirst=await pickerState();check('Picker uses enlarged text and bounded overflow',pickerFirst.font==='24px'&&pickerVisible(pickerFirst)&&pickerFirst.scrollHeight>pickerFirst.clientHeight,pickerFirst);
 await key('End');const pickerLast=await pickerState();check('Picker End reveals final member',pickerLast.id==='family:19'&&pickerVisible(pickerLast),pickerLast);await capture('picker-last');
 await showPicker(18);await key('ArrowUp');const pickerSkip=await pickerState();check('Picker arrows skip disabled member without changing order',pickerSkip.id==='family:17'&&pickerVisible(pickerSkip)&&JSON.stringify(pickerSkip.order)===JSON.stringify(pickerFirst.order),pickerSkip);
 await key('Home');check('Picker Home reaches close action',(await pickerState()).id==='control:close'&&pickerVisible(await pickerState()));
 await key('ArrowDown');check('Picker Down reaches first member',(await pickerState()).id==='family:0'&&pickerVisible(await pickerState()));
 await key('End');await showPicker();const pickerUpdated=await pickerState();check('Picker publication keeps selected logical identity',pickerUpdated.id==='family:19'&&pickerUpdated.domId==='picker:3:19'&&pickerVisible(pickerUpdated),pickerUpdated);
 for(const [width,height] of [[320,260],[700,600],[480,420]]){await viewport(width,height);const v=await pickerState();check('Picker resize '+width+'x'+height+' reveals current member',v.id==='family:19'&&pickerVisible(v)&&JSON.stringify(v.order)===JSON.stringify(pickerFirst.order),v);}
 await evaluate(`document.querySelectorAll('.surface-controls button').forEach(button=>button.style.minHeight='160px')`);await sleep(100);const grown=await pickerState();check('Late picker content growth keeps final selection visible',grown.id==='family:19'&&pickerVisible(grown),grown);
 await evaluate(`document.querySelectorAll('.surface-controls button').forEach(button=>button.style.minHeight='')`);await sleep(100);
 await showPicker(-1,'1',true);check('Picker reordered publication preserves chosen identity',(await pickerState()).id==='family:19'&&pickerVisible(await pickerState()));
 await evaluate(`document.body.tabIndex=-1;document.body.focus()`);await showPicker(-1,'2');check('Picker old lease cannot restore a selected member',await evaluate('document.activeElement===document.body'));
 await evaluate(`document.querySelector('[data-surface-control="family:0"]').focus()`);await key('ArrowUp');await key('ArrowUp');check('Picker arrows clamp at first action',(await pickerState()).id==='control:close');
 await key('End');await key('ArrowDown');check('Picker arrows clamp at final member',(await pickerState()).id==='family:19'&&pickerVisible(await pickerState()));
 check('Picker navigation emits no window action',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action').length===0`));
 await viewport(480,260);let menuPub=100;
 async function showMenu(selected=19,allDisabled=false){
  const frame={surfaceProtocol:2,publication:String(++menuPub),lease:'3',mode:'menu',status:'Window actions',bar:[],popup:[{id:'control:menu-close',domId:'menu-close',label:'Close',ariaLabel:'Close window actions',detail:'',enabled:true},...Array.from({length:20},(_,i)=>({id:'menu:1:'+i,domId:'menu:1:'+i,label:'Operation '+i,ariaLabel:'Operation '+i,detail:i===selected?'Selected':'',enabled:!allDisabled&&i!==18}))]};
  await evaluate('receivePresentation('+JSON.stringify(frame)+')');await until('document.querySelector(".surface-popup")?.dataset.publication==='+JSON.stringify(frame.publication));await sleep(70);
 }
 const menuState=()=>evaluate(`(()=>{const f=document.activeElement,r=f.getBoundingClientRect(),n=document.querySelector('.surface-popup');return {id:f.dataset.surfaceControl,top:r.top,bottom:r.bottom,height:innerHeight,font:getComputedStyle(document.body).fontSize,scroll:n.scrollTop,order:[...n.querySelectorAll('[data-surface-control]')].map(b=>b.dataset.surfaceControl)};})()`);
 await showMenu();const menuLast=await menuState();check('Overflowing menu projection focuses selected last operation',menuLast.id==='menu:1:19'&&pickerVisible(menuLast),menuLast);
 await key('Home');check('Menu navigation uses typed native policy request',await evaluate(`nativePackets.at(-1).kind==='surface-menu-navigation'&&nativePackets.at(-1).key==='Home'`));await showMenu(0);check('Projected Home selection reveals first enabled operation',(await menuState()).id==='menu:1:0'&&pickerVisible(await menuState()));
 await key('End');await showMenu(19);check('Projected End selection reveals final operation',(await menuState()).id==='menu:1:19'&&pickerVisible(await menuState()));
 await evaluate(`document.querySelector('[data-surface-control="menu:1:19"]').style.minHeight='180px'`);await sleep(100);const grownMenu=await menuState();check('Same focused menu row growth remains fully revealed',grownMenu.id==='menu:1:19'&&pickerVisible(grownMenu),grownMenu);
 await evaluate(`document.querySelector('[data-surface-control="menu:1:19"]').style.minHeight=''`);await sleep(80);await viewport(320,180);check('Shrinking menu viewport reveals selected operation',pickerVisible(await menuState()),await menuState());
 await key('Tab');check('Menu Tab reaches visible dismissal control',(await menuState()).id==='control:menu-close'&&pickerVisible(await menuState()),await menuState());
 await showMenu(19);check('Menu ordinary publication preserves Tab focus on dismissal',(await menuState()).id==='control:menu-close'&&pickerVisible(await menuState()));
 await key('Tab');check('Menu Tab returns to visible current operation',(await menuState()).id==='menu:1:19'&&pickerVisible(await menuState()));
 await call('Input.dispatchMouseEvent',{type:'mouseWheel',x:120,y:90,deltaX:0,deltaY:-30000});await sleep(80);await showMenu(19);check('Menu ordinary publication preserves deliberate wheel scrolling',(await menuState()).scroll===0,await menuState());await key('End');check('Menu keyboard navigation reveals existing selection after manual scrolling',pickerVisible(await menuState()));
 await showMenu(-1,true);await evaluate(`document.querySelector('[data-surface-control="control:menu-close"]').focus()`);await key('Escape');check('All-disabled menu keeps typed dismissal reachable',await evaluate(`nativePackets.at(-1).kind==='surface-menu-navigation'&&nativePackets.at(-1).key==='Escape'`));
 check('Menu browsing never emits activation',await evaluate(`nativePackets.filter(p=>p.kind==='surface-action').length===0`));
 await evaluate(`window.originalMenuHasFocus=document.hasFocus.bind(document);document.hasFocus=()=>false;document.body.tabIndex=-1;document.body.focus()`);await showMenu(19);check('Inactive menu document does not restore operation focus',await evaluate('document.activeElement===document.body'));await evaluate(`document.hasFocus=window.originalMenuHasFocus`);
 check('No uncaught browser exceptions',report.errors.length===0,report.errors);report.passed=true;
}catch(error){report.error=String(error.stack||error);}
finally{
 if(ws?.readyState===1){try{await call('Browser.close',{},null);}catch(_){}ws.close();}
 for(let i=0;i<100&&browser.exitCode===null;i++)await sleep(20);if(browser.exitCode===null)browser.kill('SIGTERM');
 await new Promise(resolve=>{if(browser.exitCode!==null)resolve();else browser.once('exit',resolve);});report.browserExitCode=browser.exitCode;
 fs.writeFileSync(path.join(out,'browser.stderr'),stderr);fs.writeFileSync(path.join(out,'browser.stdout'),stdout);fs.writeFileSync(path.join(out,'dense-browser.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,captures:report.captures,error:report.error}));process.exitCode=report.passed?0:1;
}
