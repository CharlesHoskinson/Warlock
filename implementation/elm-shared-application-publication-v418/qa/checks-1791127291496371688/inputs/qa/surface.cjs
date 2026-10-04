const fs=require('fs'),assert=require('assert'),{Elm}=require(process.argv[2]);
const app=Elm.SurfaceReplay.init({flags:null}),timer=setTimeout(()=>{throw Error('Surface replay deadline');},5000);
const binding={lifetime:'1',session:'2',frontend:'3'},snapshot={catalogProtocol:1,lifetime:'9007199254740993',generation:'1',entries:[{id:'close',name:'Close app',iconHint:'',wmclass:''}]};
const native=frame=>({kind:'native',frame}),attached=native({protocolVersion:3,kind:'attached',binding}),catalog=(requestId='1')=>native({protocolVersion:3,kind:'application-catalog',binding,requestId,snapshot});
const open=[attached,{kind:'open'},catalog()];
function replay(events){return new Promise(resolve=>{const cb=value=>{app.ports.outgoing.unsubscribe(cb);resolve(value);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events);});}
const action=(frame,id)=>({surfaceProtocol:2,surface:'popup',kind:'surface-action',publication:frame.publication,lease:frame.lease,id});
(async()=>{const cases=[];async function check(name,events,verify){const rows=await replay(events);verify(rows,rows.at(-1));cases.push({name,rows});}
const current=(await replay(open)).at(-1).frame;
await check('current projection admitted by presentation decoder',open,(_,last)=>{assert(last.rendererAdmitted);assert.equal(last.frame.mode,'applications');assert.equal(last.frame.lease,'1');});
await check('namespaced app identity remains distinct from close',open,(_,last)=>assert.deepEqual(last.frame.popup.map(c=>c.id),['control:close','control:refresh','entry:close']));
await check('renderer current choice reaches native ID intent',[...open,{kind:'action',action:action(current,'entry:close')}],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.requests[0].kind,'application-launch');assert.deepEqual(last.requests[0].intent,{request:'1',lifetime:snapshot.lifetime,generation:'1',entry:'close'});});
await check('closing for launch emits no automatic opener focus',[...open,{kind:'action',action:action(current,'entry:close')}],(_,last)=>{assert.equal(last.frame.popup.length,0);assert.equal(last.order[0],'publish');assert(last.order.indexOf('send')>0);});
await check('stale native dismissal cannot retire new lease',[...open,{kind:'dismiss',lease:'1'},{kind:'open'},{kind:'dismiss',lease:'1'}],(_,last)=>{assert.equal(last.frame.mode,'applications');assert.equal(last.frame.lease,'2');});
await check('native dismissal retires current popup',[...open,{kind:'dismiss',lease:'1'}],(_,last)=>assert.equal(last.frame.mode,'closed'));
await check('refresh keeps same logical native popup lease',[...open,{kind:'action',action:action(current,'control:refresh')},catalog('2')],(_,last)=>{assert.equal(last.frame.mode,'applications');assert.equal(last.frame.lease,'1');});
await check('stale publication cannot launch after refresh',[...open,{kind:'open'},catalog('2'),{kind:'action',action:action(current,'entry:close')}],(_,last)=>assert.equal(last.requests.length,0));
await check('duplicate callback cannot resubmit',[...open,{kind:'action',action:action(current,'entry:close')},{kind:'action',action:action(current,'entry:close')}],(_,last)=>assert.equal(last.requests.length,0));
for(const [name,mutation] of [['old lease',{lease:'0'}],['numeric publication',{publication:3}],['wrong protocol',{surfaceProtocol:3}],['arbitrary entry',{id:'/bin/sh'}],['extra Exec',{exec:'/bin/sh'}],['wrong kind',{kind:'execute'}]])await check('invalid renderer action '+name,[...open,{kind:'action',action:{...action(current,'entry:close'),...mutation}}],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.frame.publication,current.publication);});
await check('disconnected renderer action cannot submit',[...open,native({protocolVersion:3,kind:'host-disconnected'}),{kind:'action',action:action(current,'entry:close')}],(_,last)=>assert.equal(last.requests.length,0));
await check('frame contains presentation only',open,(_,last)=>{const raw=JSON.stringify(last.frame);assert(!raw.includes('Exec')&&!raw.includes('iconHint')&&!raw.includes('context'));assert(last.frame.popup.every(c=>Object.keys(c).sort().join()==='ariaLabel,detail,domId,enabled,id,label'));});
await check('popup origin cannot act on bar control',[...open,{kind:'action',action:action(current,'bar:applications')}],(_,last)=>assert.equal(last.requests.length,0));
await check('bar origin cannot act on popup control',[...open,{kind:'action',action:{...action(current,'entry:close'),surface:'bar'}}],(_,last)=>assert.equal(last.requests.length,0));
for(const [name,change] of [
 ['zero publication',{publication:'0'}],['numeric publication',{publication:1}],['zero open lease',{lease:'0'}],['unknown mode',{mode:'overlay'}],['unknown version',{surfaceProtocol:3}],['extra command',{exec:'/bin/sh'}],['duplicate action identity',{popup:[current.popup[0],current.popup[0]]}],['duplicate DOM identity',{popup:[current.popup[0],{...current.popup[1],domId:current.popup[0].domId}]}],['oversized text',{status:'x'.repeat(1025)}],['boolean publication',{publication:true}],['closed with controls',{mode:'closed'}],['hidden command on control',{popup:[{...current.popup[0],exec:'/bin/sh'}]}]
]) await check('presentation decoder rejects '+name,[{kind:'validate',frame:{...current,...change}}],(_,last)=>assert.equal(last.rendererAdmitted,false));
const lostEvents=[...open,native({protocolVersion:3,kind:'host-disconnected'})];
const lost=(await replay(lostEvents)).at(-1).frame;
const reconnect={...action(lost,'bar:reconnect'),surface:'bar'};
await check('detached bar exposes enabled explicit recovery',lostEvents,(_,last)=>{const c=last.frame.bar.find(c=>c.id==='bar:reconnect');assert(c.enabled);assert.equal(c.ariaLabel,'Reconnect to the window system');});
await check('current recovery callback reaches native restart',[...lostEvents,{kind:'action',action:reconnect}],(_,last)=>{assert.deepEqual(last.requests,[{protocolVersion:3,kind:'host-reconnect'}]);assert(!last.frame.bar.find(c=>c.id==='bar:reconnect').enabled);});
await check('duplicate recovery callback cannot repeat restart',[...lostEvents,{kind:'action',action:reconnect},{kind:'action',action:reconnect}],(_,last)=>assert.equal(last.requests.length,0));
await check('retired recovery callback cannot restart fresh binding',[...lostEvents,{kind:'action',action:reconnect},native({protocolVersion:3,kind:'attached',binding:{...binding,session:'4'}}),{kind:'action',action:reconnect}],(_,last)=>assert.equal(last.requests.length,0));
for(const [operation,minimized,focused] of [['Minimize',false,'7'],['Restore',true,null],['Activate',false,null]]){
 const windows=native({protocolVersion:3,kind:'action-projection',binding,requestId:'1',context:{lifetime:'1',epoch:'3',output:'1',revision:'1'},scene:{revision:'1',focused,windows:[{owner:null,application:'owned.app',available:true,incarnation:'7',label:'Owned window',minimized}]}});
 await check('accessible primary intent '+operation,[attached,windows],(_,last)=>{const c=last.frame.bar.find(c=>c.id.startsWith('bar:group:'));assert.equal(c.ariaLabel,operation+' Owned window');assert.equal(c.label,'Owned window');assert(c.enabled);});
}
await check('legacy surface callback cannot use new controls',[...open,{kind:'action',action:{...action(current,'entry:close'),surfaceProtocol:1}}],(_,last)=>assert.equal(last.requests.length,0));
await check('legacy surface frame is rejected',[{kind:'validate',frame:{...current,surfaceProtocol:1}}],(_,last)=>assert.equal(last.rendererAdmitted,false));
await check('missing accessible label is rejected',[{kind:'validate',frame:{...current,popup:current.popup.map(({ariaLabel,...control})=>control)}}],(_,last)=>assert.equal(last.rendererAdmitted,false));
const scene=(requestId,revision,options={})=>native({protocolVersion:3,kind:'action-projection',binding,requestId,context:{lifetime:'1',epoch:'3',output:options.output||'1',revision},scene:{revision,focused:'7',windows:[{owner:null,application:'owned.app',available:true,incarnation:'7',label:'First',minimized:false},...(options.gone?[]:[{owner:null,application:'owned.app',available:!options.blocked,incarnation:'8',label:'Second',minimized:false}])]}});
const baseline=[attached,scene('1','1')];const barFrame=(await replay(baseline)).at(-1).frame;
const openPicker=[...baseline,{kind:'action',action:{...action(barFrame,'bar:group:application:owned.app'),surface:'bar'}}];
const pickerFrame=(await replay(openPicker)).at(-1).frame;
const choose=[...openPicker,{kind:'action',action:action(pickerFrame,'family:8')}];
await check('picker choice closes before authoritative reread',choose,(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.requests.length,1);assert.equal(last.requests[0].kind,'projection-request');assert.equal(last.requests[0].requestId,'2');});
await check('deferred choice uses post-close revision',[...choose,scene('2','2')],(_,last)=>{assert.equal(last.requests.length,1);assert.equal(last.requests[0].kind,'window-effect');assert.equal(last.requests[0].intent.context.revision,'2');assert.equal(last.requests[0].intent.incarnation,'8');});
await check('duplicate post-close snapshot cannot repeat intent',[...choose,scene('2','2'),scene('2','2')],(_,last)=>assert.equal(last.requests.length,0));
await check('stale pre-close snapshot cannot issue choice',[...choose,scene('1','1')],(_,last)=>assert.equal(last.requests.length,0));
await check('retired target cannot issue choice',[...choose,scene('2','2',{gone:true})],(_,last)=>assert.equal(last.requests.length,0));
await check('blocked target cannot issue choice',[...choose,scene('2','2',{blocked:true})],(_,last)=>assert.equal(last.requests.length,0));
await check('changed output cannot carry deferred choice',[...choose,scene('2','2',{output:'2'})],(_,last)=>assert.equal(last.requests.length,0));
await check('disconnect cancels choice before native submission',[...choose,native({kind:'host-disconnected'}),scene('2','2')],(_,last)=>assert.equal(last.requests.length,0));
await check('choice wait announces refresh',choose,(_,last)=>assert.equal(last.frame.status,'Updating your window choice…'));
const expired=[...choose,{kind:'choice-deadline'}];
const expiredFrame=(await replay(expired)).at(-1).frame;
await check('expired choice offers explicit refresh without effect',expired,(_,last)=>{assert.equal(last.requests.length,0);assert(last.frame.status.includes('took too long'));assert(last.frame.bar.find(c=>c.id==='bar:refresh-windows').enabled);});
await check('late projection after expiry cannot apply choice',[...expired,scene('2','2')],(_,last)=>{assert.equal(last.requests.length,0);assert(last.frame.status.includes('took too long'));});
await check('refresh after expiry requests facts only',[...expired,{kind:'action',action:{...action(expiredFrame,'bar:refresh-windows'),surface:'bar'}}],(_,last)=>{assert.equal(last.requests.length,1);assert.equal(last.requests[0].kind,'projection-request');assert.equal(last.requests[0].requestId,'3');});
await check('duplicate expiry has no new publication',[...expired,{kind:'choice-deadline'}],(_,last)=>assert.equal(last.frame.publication,expiredFrame.publication));
await check('completion retires deadline token',[...choose,scene('2','2'),{kind:'choice-deadline'}],(_,last)=>{assert.equal(last.requests.length,0);assert(!last.frame.status.includes('took too long'));});
await check('native geometry reflow creates a fresh logical lease',[...open,{kind:'reflow',lease:'1'}],(_,last)=>{assert.equal(last.frame.mode,'applications');assert.equal(last.frame.lease,'2');assert.equal(last.requests[0].kind,'projection-request');});
await check('retired geometry reflow cannot replace newer lease',[...open,{kind:'reflow',lease:'1'},{kind:'reflow',lease:'1'}],(_,last)=>{assert.equal(last.frame.lease,'2');assert.equal(last.requests.length,0);});
await check('closed surface ignores geometry reflow',[...open,{kind:'dismiss',lease:'1'},{kind:'reflow',lease:'1'}],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.requests.length,0);});
fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks:cases.length,scope:'Compiled single interaction controller/presentation DTO/action/lease component; native dual-view integration not qualified',cases},null,2)+'\n');clearTimeout(timer);})();
