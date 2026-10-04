const fs=require('fs'),assert=require('assert'),{Elm}=require(process.argv[2]);
const app=Elm.OutputReplay.init({flags:null}),deadline=setTimeout(()=>{throw Error('Output replay deadline');},5000);
const scope=(id,generation='1')=>({id:String(id),generation});const one=scope(1),two=scope(2);
const topology=(revision,views)=>({kind:'topology',frame:{viewProtocol:1,kind:'view-topology',revision:String(revision),views}});
const binding={lifetime:'1',session:'2',frontend:'3'},native=frame=>({kind:'native',frame});
const attached=native({protocolVersion:3,kind:'attached',binding});
const catalog=(requestId='1')=>native({protocolVersion:3,kind:'application-catalog',binding,requestId,snapshot:{catalogProtocol:1,lifetime:'9007199254740993',generation:'1',entries:[{id:'test',name:'Test app',iconHint:'',wmclass:''}]}});
const scoped=(s,frame,id,surface='bar')=>({kind:'action',frame:{viewProtocol:1,kind:'view-action',scope:s,action:{surfaceProtocol:2,kind:'surface-action',publication:frame.publication,lease:frame.lease,id,surface}}});
function replay(events){return new Promise(resolve=>{const cb=rows=>{app.ports.outgoing.unsubscribe(cb);resolve(rows);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events);});}
(async()=>{const cases=[];async function check(name,events,verify){const rows=await replay(events);try{verify(rows.at(-1),rows)}catch(error){fs.writeFileSync(process.argv[3],JSON.stringify({passed:false,name,error:String(error),rows,cases},null,2));throw error};cases.push({name,rows});}
const base=[topology(1,[one,two]),attached];const closed=(await replay(base)).at(-1).projection.frame;
const opened=[...base,scoped(one,closed,'bar:applications'),catalog()];const open=(await replay(opened)).at(-1).projection.frame;
await check('one authority attaches once for two presentation views',base,(last,rows)=>{assert.equal(rows.at(-1).requests.length,1);assert.deepEqual(last.projection.views,[one,two]);});
await check('selected bar owns application popup',opened,last=>{assert.deepEqual(last.projection.popupOwner,one);assert.equal(last.projection.frame.mode,'applications');});
await check('second bar relocates same controller using fresh lease',[...opened,scoped(two,open,'bar:applications'),catalog('2')],last=>{assert.deepEqual(last.projection.popupOwner,two);assert.equal(last.projection.frame.lease,'2');assert.equal(last.projection.frame.mode,'applications');});
await check('wrong view cannot use valid popup control',[...opened,scoped(two,open,'entry:test','popup')],last=>{assert.deepEqual(last.requests,[]);assert.equal(last.projection.frame.publication,open.publication);assert.deepEqual(last.projection.popupOwner,one);});
await check('owning view submits launch once',[...opened,scoped(one,open,'entry:test','popup')],last=>{assert.equal(last.requests.length,1);assert.equal(last.requests[0].kind,'application-launch');assert.equal(last.projection.popupOwner,null);});
await check('duplicate launch callback cannot resubmit',[...opened,scoped(one,open,'entry:test','popup'),scoped(one,open,'entry:test','popup')],last=>assert.deepEqual(last.requests,[]));
await check('owner removal closes popup and retains other view',[...opened,topology(2,[two])],last=>{assert.equal(last.projection.popupOwner,null);assert.equal(last.projection.frame.mode,'closed');assert.deepEqual(last.projection.views,[two]);});
await check('nonowner removal preserves popup',[...opened,topology(2,[one])],last=>{assert.deepEqual(last.projection.popupOwner,one);assert.equal(last.projection.frame.publication,open.publication);});
await check('replacement generation closes old owner',[...opened,topology(2,[scope(1,'2'),two])],last=>{assert.equal(last.projection.popupOwner,null);assert.equal(last.projection.frame.mode,'closed');});
await check('retired generation cannot trigger bar',[...opened,topology(2,[scope(1,'2'),two]),scoped(one,open,'bar:applications')],last=>assert.deepEqual(last.requests,[]));
await check('empty output set suspends popup without retiring authority',[...opened,topology(2,[])],last=>{assert.deepEqual(last.projection.views,[]);assert.equal(last.projection.frame.mode,'closed');assert.equal(last.projection.popupOwner,null);});
await check('retired output id cannot be reused',[...base,topology(2,[]),topology(3,[one])],last=>{assert.deepEqual(last.projection.views,[]);assert.equal(last.projection.revision,'2');});
await check('new id permits replug after zero outputs',[...base,topology(2,[]),topology(3,[scope(3)])],last=>{assert.deepEqual(last.projection.views,[scope(3)]);assert.equal(last.projection.revision,'3');});
await check('old topology cannot resurrect retired view',[...base,topology(2,[two]),topology(1,[one,two])],last=>assert.deepEqual(last.projection.views,[two]));
await check('generation rollback is rejected',[...base,topology(2,[scope(1,'2'),two]),topology(3,[one,two])],last=>assert.deepEqual(last.projection.views,[scope(1,'2'),two]));
for(const [name,change] of [['unknown scope',{scope:scope(3)}],['zero generation',{scope:scope(1,'0')}],['numeric id',{scope:{id:1,generation:'1'}}],['extra scope field',{scope:{...one,output:'other'}}],['extra dispatcher',{execute:'shell'}],['wrong protocol',{viewProtocol:2}],['wrong kind',{kind:'execute'}]]){
 const event=scoped(one,open,'entry:test','popup');event.frame={...event.frame,...change};await check('reject '+name,[...opened,event],last=>{assert.deepEqual(last.requests,[]);assert.equal(last.projection.frame.publication,open.publication);});
}
for(const [name,change] of [['duplicate identities',{views:[one,scope(1,'2')]}],['numeric revision',{revision:2}],['zero scope',{views:[scope(0)]}],['excessive views',{views:Array.from({length:65},(_,n)=>scope(n+3))}],['unlisted fields',{command:'run'}]]){
 const event=topology(2,[one,two]);event.frame={...event.frame,...change};await check('reject topology '+name,[...base,event],last=>assert.equal(last.projection.revision,'1'));
}
for(const kind of ['dismiss','reflow']){
 await check(kind+' refuses nonowner',[...opened,{kind,frame:{scope:two,lease:open.lease}}],last=>{assert.equal(last.projection.frame.publication,open.publication);assert.deepEqual(last.requests,[]);});
 await check(kind+' refuses stale lease',[...opened,{kind,frame:{scope:one,lease:'0'}}],last=>assert.equal(last.projection.frame.publication,open.publication));
 await check(kind+' refuses retired scope',[...opened,topology(2,[two]),{kind,frame:{scope:one,lease:open.lease}}],last=>assert.equal(last.projection.frame.mode,'closed'));
}
await check('scoped reflow retains owner and advances lease',[...opened,{kind:'reflow',frame:{scope:one,lease:open.lease}}],last=>{assert.equal(last.projection.frame.lease,'2');assert.deepEqual(last.projection.popupOwner,one);});
await check('scoped dismissal closes current popup',[...opened,{kind:'dismiss',frame:{scope:one,lease:open.lease}}],last=>assert.equal(last.projection.popupOwner,null));
await check('closed popup retains scoped bar focus destination',[...opened,{kind:'dismiss',frame:{scope:one,lease:open.lease}}],last=>{assert.deepEqual(last.projection.focusOwner,one);assert.equal(last.projection.popupOwner,null);});
await check('owner removal selects live focus fallback',[...opened,topology(2,[two])],last=>{assert.deepEqual(last.projection.focusOwner,two);assert.equal(last.projection.popupOwner,null);});
fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks:cases.length,cases},null,2));clearTimeout(deadline);console.log(cases.length+' shared output controller checks passed');
})().catch(e=>{console.error(e);process.exitCode=1;clearTimeout(deadline);});
