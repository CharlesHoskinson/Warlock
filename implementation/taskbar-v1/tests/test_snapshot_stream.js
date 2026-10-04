const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../widget_v66/SnapshotStream.js'), 'utf8').replace(/^\.pragma library\s*/, ''), context);
const snapshot = (epoch='one', sequence=1) => ({protocolVersion:1,epoch,sequence,groups:[],snapGroups:[],monitors:[],settings:{},focusedAddress:'',reducedMotion:false});
const decode = (value, state=context.initial()) => context.decode(JSON.stringify(value), state);
let first = decode(snapshot());
assert(first);
assert(decode(snapshot('one',2), first.state));
assert.equal(decode(snapshot('one',1), first.state), null);
assert.equal(decode(snapshot('two',2), first.state), null);
assert(decode(snapshot('two',1), context.initial()));
for (const mutate of [v=>v.protocolVersion=2,v=>v.sequence=0,v=>v.sequence=1.5,v=>v.sequence=Number.MAX_SAFE_INTEGER+1,v=>v.epoch='',v=>v.epoch='x'.repeat(129),v=>v.groups={},v=>v.monitors=null,v=>v.settings=[],v=>v.reducedMotion=1]) {
  let value=snapshot(); mutate(value); assert.equal(decode(value), null);
}
assert.equal(context.decode('{', context.initial()), null);
assert.equal(context.decode('x'.repeat(4*1024*1024+1), context.initial()), null);
let group={key:'app',desktopId:'app',name:'App',icon:'app',pinned:false,actions:[],recent:[],windows:[{address:'0x123',workspace:{name:'1'}}]};
let value=snapshot(); value.groups=[group]; assert(decode(value));
group.windows[0].workspace=null; assert.equal(decode(value),null);
group.windows[0].workspace={name:'1'}; group.windows[0].address='not-an-address'; assert.equal(decode(value),null);
console.log('Snapshot stream: 21 acceptance, epoch, ordering, bound and malformed-shape checks passed');
