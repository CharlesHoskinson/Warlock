const fs=require('fs'),assert=require('assert'),{Elm}=require(process.argv[2]);
const app=Elm.SurfaceReplay.init({flags:null}),timer=setTimeout(()=>{throw Error('Surface replay deadline');},5000);
const binding={lifetime:'1',session:'2',frontend:'3'},snapshot={catalogProtocol:1,lifetime:'9007199254740993',generation:'1',entries:[{id:'close',name:'Close app',iconHint:'',wmclass:''}]};
const native=frame=>({kind:'native',frame}),attached=native({protocolVersion:3,kind:'attached',binding}),catalog=(requestId='1')=>native({protocolVersion:3,kind:'application-catalog',binding,requestId,snapshot});
const open=[attached,{kind:'open'},catalog()];
function replay(events){return new Promise(resolve=>{const cb=value=>{app.ports.outgoing.unsubscribe(cb);resolve(value);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events);});}
const action=(frame,id)=>({surfaceProtocol:1,kind:'surface-action',publication:frame.publication,lease:frame.lease,id});
(async()=>{const cases=[];async function check(name,events,verify){const rows=await replay(events);verify(rows,rows.at(-1));cases.push({name,rows});}
const current=(await replay(open)).at(-1).frame;
await check('current projection admitted by presentation decoder',open,(_,last)=>{assert(last.rendererAdmitted);assert.equal(last.frame.mode,'applications');assert.equal(last.frame.lease,'1');});
await check('namespaced app identity remains distinct from close',open,(_,last)=>assert.deepEqual(last.frame.popup.map(c=>c.id),['control:close','control:refresh','entry:close']));
await check('renderer current choice reaches native ID intent',[...open,{kind:'action',action:action(current,'entry:close')}],(_,last)=>{assert.equal(last.frame.mode,'closed');assert.equal(last.requests[0].kind,'application-launch');assert.deepEqual(last.requests[0].intent,{request:'1',lifetime:snapshot.lifetime,generation:'1',entry:'close'});});
await check('closing for launch emits no automatic opener focus',[...open,{kind:'action',action:action(current,'entry:close')}],(_,last)=>assert.equal(last.frame.popup.length,0));
await check('stale native dismissal cannot retire new lease',[...open,{kind:'dismiss',lease:'1'},{kind:'open'},{kind:'dismiss',lease:'1'}],(_,last)=>{assert.equal(last.frame.mode,'applications');assert.equal(last.frame.lease,'2');});
await check('native dismissal retires current popup',[...open,{kind:'dismiss',lease:'1'}],(_,last)=>assert.equal(last.frame.mode,'closed'));
await check('refresh keeps same logical native popup lease',[...open,{kind:'action',action:action(current,'control:refresh')},catalog('2')],(_,last)=>{assert.equal(last.frame.mode,'applications');assert.equal(last.frame.lease,'1');});
await check('stale publication cannot launch after refresh',[...open,{kind:'open'},catalog('2'),{kind:'action',action:action(current,'entry:close')}],(_,last)=>assert.equal(last.requests.length,0));
await check('duplicate callback cannot resubmit',[...open,{kind:'action',action:action(current,'entry:close')},{kind:'action',action:action(current,'entry:close')}],(_,last)=>assert.equal(last.requests.length,0));
for(const [name,mutation] of [['old lease',{lease:'0'}],['numeric publication',{publication:3}],['wrong protocol',{surfaceProtocol:2}],['arbitrary entry',{id:'/bin/sh'}],['extra Exec',{exec:'/bin/sh'}],['wrong kind',{kind:'execute'}]])await check('invalid renderer action '+name,[...open,{kind:'action',action:{...action(current,'entry:close'),...mutation}}],(_,last)=>{assert.equal(last.requests.length,0);assert.equal(last.frame.publication,current.publication);});
await check('disconnected renderer action cannot submit',[...open,native({protocolVersion:3,kind:'host-disconnected'}),{kind:'action',action:action(current,'entry:close')}],(_,last)=>assert.equal(last.requests.length,0));
await check('frame contains presentation only',open,(_,last)=>{const raw=JSON.stringify(last.frame);assert(!raw.includes('Exec')&&!raw.includes('iconHint')&&!raw.includes('context'));assert(last.frame.popup.every(c=>Object.keys(c).sort().join()==='detail,domId,enabled,id,label'));});
fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks:cases.length,scope:'Compiled single interaction controller/presentation DTO/action/lease component; native dual-view integration not qualified',cases},null,2)+'\n');clearTimeout(timer);})();
