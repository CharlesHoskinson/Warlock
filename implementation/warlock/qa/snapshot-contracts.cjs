// Execute only under root's protected QA; stdout is the retained result.
const { Elm } = require(process.argv[2]);
const seed = 0x5eed1234; let rng = seed >>> 0;
function random() { rng ^= rng << 13; rng ^= rng >>> 17; rng ^= rng << 5; return rng >>> 0; }
const row = (id, dom) => ({ id, domId: dom, label: id, ariaLabel: id, detail: '', enabled: true });
const app = (publication='1', lease='1') => ({ surfaceProtocol:2, publication, lease, mode:'applications', status:'', bar:[row('bar:apps','b')], popup:[row('control:search','q'),row('entry:1','e1')] });
const frames = [], expected = [], names = [];
function add(name, frame, valid) { names.push(name); frames.push(frame); expected.push(valid); }
for (let i=0;i<200;i++) {
  let f = app(String(1+random()%999999), String(1+random()%999999));
  f.status = 'sample-'+(random()%100000); f.popup[1].label = 'application-'+(random()%100000);
  add('valid-'+i,f,true);
}
add('uint64-max',app('18446744073709551615','18446744073709551615'),true);
add('valid-legacy-shape',app(),true);
let f=app(); f.surfaceProtocol=3; add('version',f,false);
f=app(); f.publication='0'; add('publication-zero',f,false);
f=app(); f.publication='18446744073709551616'; add('publication-overflow',f,false);
f=app(); f.publication='01'; add('publication-noncanonical',f,false);
f=app(); f.lease='0'; add('open-zero-lease',f,false);
f=app(); f.popup[1].id='control:search'; add('duplicate-identity',f,false);
f=app(); f.popup[1].domId='q'; add('duplicate-dom-id',f,false);
f=app(); f.popup[1].id=''; add('empty-identity',f,false);
f=app(); f.popup[1].id='a'.repeat(513); add('identity-too-long',f,false);
f=app(); f.popup[1].id='a'.repeat(512); add('identity-boundary',f,true);
f=app(); f.popup[1].focusOnly=true; add('enabled-focus-only',f,false);
f=app(); f.popup[1].checked=true; add('checked-without-focusOnly',f,false);
f=app(); f.bar=Array.from({length:301},(_,i)=>row('b'+i,'d'+i)); add('bar-capacity',f,false);
f=app(); f.mode='closed'; add('closed-has-popup',f,false);
f=app(); f.popup[1].extra=true; add('unexpected-field',f,false);
f=app(); f.popup[1].enabled=false; add('disabled-entry-action',f,true);
f=app(); f.publication=1; add('numeric-publication-refused',f,false);
add('above-js-safe-integer-a',app('9007199254740992','1'),true);
add('above-js-safe-integer-b',app('9007199254740993','1'),true);
const edit = (pub,lease,id='control:search') => ({surfaceProtocol:2,kind:'surface-query',surface:'popup',publication:pub,lease,id,query:'typed'});
const flags={frames,first:app('1','1'),next:app('2','1'),stale:app('1','1'),duplicate:app('2','1'),edit:edit('1','1'),future:edit('3','1'),wrongLease:edit('1','2'),wrongId:edit('1','1','entry:1'),invalid:{surfaceProtocol:99},third:app('3','1')};
flags.currentAction={surfaceProtocol:2,kind:'surface-action',surface:'popup',publication:'2',lease:'1',id:'entry:1'};
flags.retiredFrame=app('3','2');
flags.retiredLeaseAction={...flags.currentAction,publication:'3'};
const worker=Elm.SurfaceSnapshotContracts.init({flags});
worker.ports.outgoing.subscribe(result => {
  const failures=[];
  if (result.cases.length !== names.length) failures.push({name:'case-count',actual:result.cases.length,expected:names.length});
  result.cases.forEach((actual,i) => {
    if (actual.accepted!==expected[i] || !actual.equivalent || !actual.idempotent || !actual.pendingEquivalent || !actual.pendingSuppressesEntry || !actual.actionsEquivalent)
      failures.push({name:names[i],input:frames[i],expectedAccepted:expected[i],actual});
  });
  for (const [name,ok] of Object.entries(result.sequence)) if (!ok) failures.push({name,actual:ok,sequence:flags});
  process.stdout.write(JSON.stringify({seed:'0x5eed1234',budget:200,caseCount:names.length,sequenceChecks:result.sequence,failures},null,2)+'\n');
  process.exitCode=failures.length ? 1 : 0;
});
