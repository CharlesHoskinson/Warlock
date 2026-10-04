const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const context={};vm.createContext(context);
const source=path.join(__dirname,'../SwitcherState.js');
vm.runInContext(fs.readFileSync(source,'utf8').replace(/^\.pragma library\s*/,''),context);
const R=context;
const request={mode:'switcher',candidates:[0,1,2].map(i=>({address:'0x'+(i+1),pid:10+i,stableId:'stable-'+i}))};
let checks=0;
function test(name,run){run();checks++;console.log('PASS '+name)}
function fresh(){return R.create('session','epoch')}
function step(s,n,d=1,g=1){return R.step(s,'session',g,n,d)}
function ready(s){return R.ready(s,s.epoch,s.generation,s.token,request)}
function permutations(items){return !items.length?[[]]:items.flatMap((value,i)=>permutations(items.filter((_,j)=>j!==i)).map(rest=>[value,...rest]))}
for(const order of permutations(['step1','step2','release']))test('reordered '+order.join(','),()=>{
 let s=fresh(),effects=0,builders=0;
 for(const event of order){let t=event==='release'?R.release(s,'session',1,2):step(s,event==='step1'?1:2);s=t.state;effects+=!!t.effect;
  if(t.builder){builders++;t=ready(s);s=t.state;effects+=!!t.effect;}}
 assert.equal(builders,1);assert.equal(effects,1);assert.equal(s.phase,'committed');assert.equal(s.effect.candidate.address,'0x3');
 let claim=R.claim(s,'epoch',1,s.token);assert.equal(claim.candidate.address,'0x3');assert.equal(R.claim(claim.state,'epoch',1,s.token).candidate,null);
});
test('release while query pending never opens overlay',()=>{let s=step(fresh(),1).state;s=R.release(s,'session',1,1).state;assert.equal(s.phase,'pending');s=ready(s).state;assert.equal(s.phase,'committed')});
test('query ready before release opens then commits',()=>{let s=ready(step(fresh(),1).state).state;assert.equal(s.phase,'open');assert.equal(R.release(s,'session',1,1).state.phase,'committed')});
test('release-before-begin latches only this generation',()=>{let s=R.release(fresh(),'session',1,1).state;assert.equal(s.phase,'pending');s=step(s,1).state;assert.equal(ready(s).state.effect.candidate.address,'0x2')});
test('duplicates have no repeated builder or effect',()=>{let s=step(fresh(),1).state;assert.equal(step(s,1).builder,false);s=ready(s).state;let t=R.release(s,'session',1,1);assert.ok(t.effect);assert.equal(R.release(t.state,'session',1,1).effect,null)});
test('conflicting duplicate cancels',()=>{let s=step(fresh(),1).state;assert.equal(step(s,1,-1).state.phase,'cancelled')});
test('missing late ordinal prevents early selection',()=>{let s=step(fresh(),1).state;s=R.release(s,'session',1,2).state;s=ready(s).state;assert.equal(s.phase,'pending');assert.equal(s.effect,null);assert.equal(step(s,2).state.effect.candidate.address,'0x3')});
test('reverse and mixed repeats',()=>{let s=step(fresh(),1,-1).state;s=step(s,2,-1).state;s=step(s,3,1).state;s=ready(s).state;assert.equal(s.selected,2)});
test('cancelled query ready cannot reopen',()=>{let s=step(fresh(),1).state;s=R.cancel(s).state;assert.equal(ready(s).accepted,false);assert.equal(step(s,2).accepted,false)});
test('older generation cannot release newer chooser',()=>{let s=step(fresh(),1,1,2).state;assert.equal(R.release(s,'session',1,1).accepted,false);assert.equal(step(s,1,1,1).accepted,false)});
test('new generation revokes previous effect before claim',()=>{let s=ready(step(fresh(),1).state).state;s=R.release(s,'session',1,1).state;const old=s.token;s=step(s,1,1,2).state;assert.equal(R.claim(s,'epoch',1,old).candidate,null)});
test('cancel after commit revokes unclaimed effect',()=>{let s=ready(step(fresh(),1).state).state;s=R.release(s,'session',1,1).state;s=R.cancel(s).state;assert.equal(R.claim(s,'epoch',1,s.token).candidate,null)});
test('foreign epoch and session cannot authorize',()=>{let s=step(fresh(),1).state;assert.equal(R.ready(s,'foreign',1,s.token,request).accepted,false);assert.equal(R.step(s,'foreign',2,1,1).accepted,false)});
test('invalid candidates cancel',()=>{let s=step(fresh(),1).state;assert.equal(R.ready(s,s.epoch,1,s.token,{mode:'switcher',candidates:[{address:'0x1',pid:1,stableId:''}]}).state.phase,'cancelled')});
test('empty candidates cancel',()=>{let s=step(fresh(),1).state;assert.equal(R.ready(s,s.epoch,1,s.token,{mode:'switcher',candidates:[]}).state.phase,'cancelled')});
test('stale builder token does not cancel live generation',()=>{let s=step(fresh(),1,1,2).state;assert.equal(R.cancel(s,1,'old').accepted,false)});
test('ordinal and direction bounds',()=>{for(const n of [0,-1,4097,1.5])assert.equal(step(fresh(),n).accepted,false);assert.equal(step(fresh(),1,0).accepted,false)});
test('manual selection is claimed once',()=>{let s=ready(step(fresh(),1).state).state;s=R.choose(s,0).state;s=R.release(s,'session',1,1).state;assert.equal(s.effect.candidate.address,'0x1')});
test('candidate payload is copied against mutation',()=>{let s=ready(step(fresh(),1).state).state;const original=s.request.candidates[1].address;request.candidates[1].address='0x99';assert.equal(s.request.candidates[1].address,original);request.candidates[1].address=original});
test('explicit selection survives missing reordered press',()=>{let s=ready(step(fresh(),2).state).state;s=R.choose(s,0).state;s=R.release(s,'session',1,2).state;assert.equal(s.phase,'pending');s=step(s,1).state;assert.equal(s.effect.candidate.address,'0x1')});
test('repeat cycles from manual arrow selection',()=>{let s=ready(step(fresh(),1).state).state;s=R.choose(s,0).state;s=step(s,2).state;assert.equal(s.selected,1)});
test('reload barrier cancels old pending build',()=>{let s=step(fresh(),1).state;s=R.barrier(s,'session',2).state;assert.equal(s.phase,'cancelled');assert.equal(ready(s).accepted,false);assert.equal(R.release(s,'session',1,1).accepted,false);assert.equal(step(s,1,1,3).accepted,true)});
test('late reload barrier cannot cancel newer chord',()=>{let s=step(fresh(),1,1,3).state;assert.equal(R.barrier(s,'session',2).accepted,false)});
console.log('SWITCHER_REDUCER_PASS '+checks);
