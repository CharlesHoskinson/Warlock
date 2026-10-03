const fs = require('node:fs');
const assert = require('node:assert/strict');
const { Elm } = require(process.env.ELM_REPLAY);
const app = Elm.Replay.init({ flags: null });
let pending;
app.ports.outgoing.subscribe(value => { assert(pending); const resolve = pending; pending = null; resolve(value); });
function send(value) { return new Promise(resolve => { pending = resolve; app.ports.incoming.send(value); }); }
function window(id, patch = {}) { return { id: String(id), owner: null, mapped: true, minimized: false, member: true, modal: false, inputAtProbe: true, ...patch }; }
function scene(patch = {}) { return { revision: '9007199254740993', locked: false, windows: [window(1), window(2, { owner: '1', modal: true }), window(3)], order: ['1','2','3'], focused: '2', ...patch }; }
const receipts = [];
async function check(name, candidate, expected) {
  const result = await send(candidate);
  if (expected.accepted) assert.deepEqual(result, expected, name);
  else { assert.equal(result.accepted, false, name); assert.equal(Object.keys(result).sort().join(','), 'accepted,error', name); }
  receipts.push({ name, candidate, expected, result });
}
async function main() {
  // Independent fixed-family oracle: no implementation traversal or order solver.
  for (let minimized=0; minimized<8; minimized++) for (let member=0; member<8; member++)
  for (let mapped=0; mapped<8; mapped++) for (let input=0; input<8; input++) {
    const windows = scene().windows.map((w,i) => ({ ...w, minimized: !!(minimized & (1<<i)), member: !!(member & (1<<i)), mapped: !!(mapped & (1<<i)), inputAtProbe: !!(input & (1<<i)) }));
    const owner = !!(mapped&1) && !!(member&1) && !(minimized&1);
    const child = owner && !!(mapped&2) && !!(member&2) && !(minimized&2);
    const peer = !!(mapped&4) && !!(member&4) && !(minimized&4);
    const order = [owner?'1':null, child?'2':null, peer?'3':null].filter(Boolean);
    const focus = child?'2':owner?'1':peer?'3':null;
    const hit = peer && (input&4)?'3':child && (input&2)?'2':owner && (input&1)?'1':null;
    await check(`flags-${minimized}-${member}-${mapped}-${input}`, scene({windows, order, focused: focus}), {accepted:true, paint:order, focus, hit});
  }
  const base = scene();
  const negatives = [
    ['child-before-owner', scene({order:['2','1','3']})],
    ['modal-blocked-parent', scene({focused:'1'})],
    ['unknown-focus', scene({focused:'4'})],
    ['missing-order-entry', scene({order:['1','2']})],
    ['duplicate-order-entry', scene({order:['1','2','2','3']})],
    ['duplicate-incarnation', scene({windows:[...base.windows,window(1)]})],
    ['unknown-owner', scene({windows:[window(1),window(2,{owner:'4'}),window(3)]})],
    ['self-cycle', scene({windows:[window(1,{owner:'1'}),window(2),window(3)]})],
    ['family-cycle', scene({windows:[window(1,{owner:'2'}),window(2,{owner:'1'}),window(3)]})],
    ['unknown-minimized', scene({windows:[window(1,{minimized:null}),window(2),window(3)]})],
    ['revision-number', scene({revision:9007199254740992})],
    ['revision-overflow', scene({revision:'18446744073709551616'})],
    ['incarnation-zero', scene({windows:[window(0),window(2),window(3)]})],
    ['unexpected-scene-field', {...scene(),pinBypass:true}],
    ['locked-order', scene({locked:true})],
    ['inactive-owner-with-live-child', scene({windows:[window(1,{member:false}),window(2,{owner:'1'}),window(3)],order:['2','3'],focused:'2'})],
    ['scene-bound', scene({windows:Array.from({length:257},(_,i)=>window(i+1)),order:[],focused:null})],
    ['family-depth-bound', scene({windows:Array.from({length:35},(_,i)=>window(i+1,{owner:i?String(i):null})),order:[],focused:null})]
  ];
  for(const [name,candidate] of negatives) await check(name,candidate,{accepted:false});
  await check('lock-clears-all',scene({locked:true,order:[],focused:null}),{accepted:true,paint:[],focus:null,hit:null});
  await check('transparent-modal-keyboard-focus',scene({windows:[window(1),window(2,{owner:'1',modal:true,inputAtProbe:false}),window(3,{inputAtProbe:false})]}),{accepted:true,paint:['1','2','3'],focus:'2',hit:'1'});
  await check('lossless-large-incarnation',scene({windows:[window('18446744073709551615')],order:['18446744073709551615'],focused:'18446744073709551615'}),{accepted:true,paint:['18446744073709551615'],focus:'18446744073709551615',hit:'18446744073709551615'});
  let traceCount=0, traceStates=0;
  if(process.env.QUINT_TRACES) {
    const files=fs.readdirSync(process.env.QUINT_TRACES).filter(name=>name.endsWith('.itf.json'));
    assert.equal(files.filter(name=>name.startsWith('named-')).length,6);
    assert(files.some(name=>name.startsWith('sample-')));
    for(const file of files) {
      const trace=JSON.parse(fs.readFileSync(process.env.QUINT_TRACES+'/'+file));
      assert(trace.states.length>0);
      traceCount++;
      for(const [index,{s}] of trace.states.entries()) {
        const ints=set=>set['#set'].map(n=>n['#bigint']);
        const minimized=ints(s.minimized), inactive=ints(s.inactive);
        const order=s.order.map(n=>n['#bigint']);
        const focus=s.focus['#bigint']==='0'?null:s.focus['#bigint'];
        const candidate=scene({locked:s.locked,windows:scene().windows.map(w=>({...w,minimized:minimized.includes(w.id),member:!inactive.includes(w.id)})),order,focused:focus});
        await check(`quint-${file}-${index}`,candidate,{accepted:true,paint:order,focus,hit:order.at(-1)||null});
        traceStates++;
      }
    }
  }
  fs.writeFileSync(process.env.ELM_REPORT,JSON.stringify({passed:true,cases:receipts.length,traceCount,traceStates,receipts},null,2)+'\n');
  console.log(JSON.stringify({passed:true,cases:receipts.length,traceCount,traceStates}));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
