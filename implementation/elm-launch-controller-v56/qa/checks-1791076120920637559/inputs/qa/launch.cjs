const fs=require('fs'),assert=require('assert'),{Elm}=require(process.argv[2]);
const app=Elm.LaunchReplay.init({flags:null}),deadline=setTimeout(()=>{throw Error('Launch replay deadline');},6000);
const snapshot={catalogProtocol:1,lifetime:'9007199254740993',generation:'18446744073709551615',entries:[{id:'fixture',name:'Fixture',iconHint:'fixture',wmclass:'Fixture'}]};
const intent={request:'1',lifetime:snapshot.lifetime,generation:snapshot.generation,entry:'fixture'};
const receipt=(status='Submitted',reason='native-submission-accepted',change={})=>({catalogProtocol:1,kind:'launch-outcome',intent,status,reason,...change});
const bind={kind:'bind',host:'host-A'},cat={kind:'catalog',snapshot},select={kind:'select',entry:'fixture'},start={kind:'start',index:0};
const initial=[bind,cat,select,start];
const got=(r=receipt(),host='host-A')=>({kind:'receipt',host,receipt:r});
function replay(events){return new Promise(resolve=>{const cb=value=>{app.ports.outgoing.unsubscribe(cb);resolve(value);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events);});}
(async()=>{const cases=[];
async function check(name,events,verify){const rows=await replay(events);verify(rows,rows.at(-1));cases.push({name,rows});}
await check('lossless scoped request enters Pending',initial,(rows,last)=>{assert.equal(last.status,'Pending');assert.deepEqual(last.intent,intent);});
await check('duplicate selection callback cannot launch again',[...initial,start],(_,last)=>{assert.equal(last.intent,null);assert.equal(last.status,'Pending');});
await check('submitted receipt accepted without readiness claim',[...initial,got()],(_,last)=>assert.equal(last.status,'Submitted'));
await check('refusal clears Pending',[...initial,got(receipt('Refused','stale-catalog'))],(_,last)=>assert.equal(last.status,'Refused'));
await check('unknown requires explicit acknowledgement',[...initial,got(receipt('Unknown','submission-not-confirmed')),select,{kind:'start',index:1}],(_,last)=>{assert.equal(last.status,'Unknown');assert.equal(last.intent,null);});
await check('explicit new user action after unknown acknowledgement',[...initial,{kind:'timeout'},{kind:'acknowledge'},select,{kind:'start',index:1}],(_,last)=>{assert.equal(last.status,'Pending');assert.equal(last.intent.request,'2');});
await check('old selection remains retired after acknowledgement',[...initial,{kind:'timeout'},{kind:'acknowledge'},start],(_,last)=>{assert.equal(last.status,'Idle');assert.equal(last.intent,null);});
await check('disconnect preserves uncertainty and retires catalog',[...initial,{kind:'disconnect'},bind,select,start],(_,last)=>{assert.equal(last.status,'Unknown');assert.equal(last.selections,1);assert.equal(last.intent,null);});
await check('new host cannot settle old pending launch',[...initial,{kind:'bind',host:'host-B'},got(receipt(),'host-B')],(_,last)=>assert.equal(last.status,'Unknown'));
await check('wrong host receipt ignored',[...initial,got(receipt(),'host-B')],(_,last)=>assert.equal(last.status,'Pending'));
for(const [name,changed] of [['request','2'],['lifetime','2'],['generation','2'],['entry','other']]) await check('receipt correlation '+name,[...initial,got(receipt('Submitted','native-submission-accepted',{intent:{...intent,[name]:changed}}))],(_,last)=>assert.equal(last.status,'Pending'));
for(const [name,bad] of [
 ['extra root',receipt('Submitted','native-submission-accepted',{exec:'unsafe'})],['extra intent',receipt('Submitted','native-submission-accepted',{intent:{...intent,extra:true}})],['unknown status',receipt('Ready')],['invalid reason',receipt('Submitted','application-ready')],['numeric counter',receipt('Submitted','native-submission-accepted',{intent:{...intent,request:1}})],['zero counter',receipt('Submitted','native-submission-accepted',{intent:{...intent,request:'0'}})],['version',receipt('Submitted','native-submission-accepted',{catalogProtocol:2})],['kind',receipt('Submitted','native-submission-accepted',{kind:'window-outcome'})]]) await check('malformed receipt ignored '+name,[...initial,got(bad)],(_,last)=>assert.equal(last.status,'Pending'));
await check('catalog refresh retires even same-generation callbacks',[bind,cat,select,cat,start],(_,last)=>{assert.equal(last.status,'Idle');assert.equal(last.intent,null);});
await check('catalog change retires stale selection',[bind,cat,select,{kind:'catalog',snapshot:{...snapshot,generation:'1'}},start],(_,last)=>assert.equal(last.intent,null));
await check('malformed refresh retires selection',[bind,cat,select,{kind:'catalog',snapshot:{}},start],(_,last)=>assert.equal(last.intent,null));
await check('removed entry never selected',[bind,{kind:'catalog',snapshot:{...snapshot,entries:[]}},select,start],(_,last)=>{assert.equal(last.selections,0);assert.equal(last.intent,null);});
await check('receipt still correlates after catalog changed during flight',[...initial,{kind:'catalog',snapshot:{...snapshot,generation:'1'}},got()],(_,last)=>assert.equal(last.status,'Submitted'));
await check('duplicate receipt cannot override settled state',[...initial,got(),got(receipt('Unknown','submission-not-confirmed'))],(_,last)=>assert.equal(last.status,'Submitted'));
await check('timeout does not resubmit on late receipt',[...initial,{kind:'timeout'},got()],(_,last)=>{assert.equal(last.status,'Unknown');assert.equal(last.intent,null);});
await check('submitted permits fresh intentional launch',[...initial,got(),select,{kind:'start',index:1}],(_,last)=>{assert.equal(last.intent.request,'2');assert.equal(last.status,'Pending');});
const native=JSON.parse(fs.readFileSync(process.argv[3])),nativeReceipt=native.checks.find(c=>c.name==='native GIO submission accepted').outcome;
const nativeSnap=JSON.parse(fs.readFileSync(process.argv[4]));
await check('actual native GIO receipt settles matching compiled controller',[bind,{kind:'catalog',snapshot:nativeSnap},select,start,got(nativeReceipt)],(_,last)=>assert.equal(last.status,'Submitted'));
fs.writeFileSync(process.argv[5],JSON.stringify({passed:true,checks:cases.length,scope:'Compiled pure controller and actual native receipt replay; authenticated transport/GUI not qualified',cases},null,2)+'\n');clearTimeout(deadline);
})();
