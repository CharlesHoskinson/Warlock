import assert from 'node:assert/strict';
import { installOutsideDismissal } from './index.js';
class Target extends EventTarget {}
const doc = new Target(); doc.defaultView = new Target();
const root = {contains: () => true};
let snapshot = {epoch: 1, viewScope:{id:'1', generation:'1'}, presentation: {mode:'launcher', lease:'5', publication:'9', applied:{popup:true}}};
const inputs = [];
const host = {getSnapshot: () => snapshot, dispatchInput: input => {
  if (input.epoch === snapshot.epoch && input.scope.id === snapshot.viewScope.id && input.scope.generation === snapshot.viewScope.generation && input.lease === snapshot.presentation.lease && snapshot.presentation.mode !== 'closed') inputs.push(input);
}};
const stop = installOutsideDismissal({doc, root, isDesktop:false, host});
const control = {closest: () => ({})};
const blank = {closest: () => null};
const send = (type, target, id=1) => { const e = new Event(type); Object.defineProperties(e, {target:{value:target}, button:{value:0}, pointerId:{value:id}}); doc.dispatchEvent(e); };
const tick = () => new Promise(resolve => setTimeout(resolve, 5));
// Ordinary and held Bar presses leave the original stamp available for the renderer.
for (const delay of [0, 10]) { send('pointerdown', control); await new Promise(resolve => setTimeout(resolve, delay)); assert.equal(inputs.length, 0); send('pointerup', control); await tick(); assert.equal(inputs.length, 0); }
// Cancellation, mismatched releases and blur never dismiss.
send('pointerdown', blank); send('pointercancel', blank); send('pointerup', blank); await tick();
send('pointerdown', blank); send('pointerup', blank, 2); await tick();
send('pointerdown', blank); doc.defaultView.dispatchEvent(new Event('blur')); send('pointerup', blank); await tick(); assert.equal(inputs.length, 0);
// Focusing an unfocused client advances the publication during the click.
// The same popup lease still receives the completed outside dismissal.
send('pointerdown', blank); send('pointerup', blank);
snapshot = {...snapshot, presentation:{...snapshot.presentation, publication:'10'}};
await tick();
assert.deepEqual(inputs, [{kind:'popup-dismiss', epoch:1, scope:{id:'1', generation:'1'}, lease:'5'}]);
inputs.length = 0;
// A replacement popup, a retired epoch or a changed scope survives the old gesture.
for (const change of [
  s => ({...s, presentation:{...s.presentation, lease:'6'}}),
  s => ({...s, epoch:2}),
  s => ({...s, viewScope:{id:'1', generation:'2'}})
]) {
  const original = snapshot;
  send('pointerdown', blank); send('pointerup', blank);
  snapshot = change(snapshot); await tick(); assert.equal(inputs.length, 0);
  snapshot = original;
}
// Genuine outside clicks dismiss only after completion.
send('pointerdown', blank); await tick(); assert.equal(inputs.length, 0);
send('pointerup', blank); await tick(); assert.equal(inputs.length, 1);
stop(); console.log('Outside gesture, focus publication, replacement and cancellation checks passed');
