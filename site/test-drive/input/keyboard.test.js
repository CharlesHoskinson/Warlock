import assert from 'node:assert/strict';
import { installKeyboard } from './keyboard.js';
class Events {
  constructor() { this.events = new Map(); }
  addEventListener(type, fn) { this.events.set(type, fn); }
  removeEventListener(type) { this.events.delete(type); }
  fire(type, data = {}) { const event = { currentTarget: this, target: desktop, key: '', code: '', repeat: false, altKey: false, ctrlKey: false, metaKey: false, shiftKey: false, isComposing: false, defaultPrevented: false, getModifierState: () => true, preventDefault() { this.defaultPrevented = true; }, ...data }; this.events.get(type)?.(event); return event; }
}
const document = new Events(); document.defaultView = new Events();
let focused = true; document.hasFocus = () => focused;
const desktop = { ownerDocument: document, contains: target => target === desktop, closest: () => null };
const inputs = []; const dispose = installKeyboard({ documents: [document], host: { dispatchInput: input => inputs.push(input) }, root: desktop });
document.fire('keydown', { key: 'Tab', altKey: true });
document.fire('keydown', { key: 'Tab', altKey: true, shiftKey: true });
document.fire('keyup', { key: 'Alt', code: 'AltLeft' });
assert.deepEqual(inputs.map(x => x.action), ['next', 'previous', 'activate']);
document.fire('keydown', { key: 'Tab', altKey: true });
focused = false; document.defaultView.fire('blur');
document.fire('keyup', { key: 'Alt', code: 'AltLeft' });
assert.deepEqual(inputs.slice(-2).map(x => x.action), ['next', 'cancel']);
focused = true;
const frameDocument = new Events(); frameDocument.defaultView = new Events();
dispose.addDocument(frameDocument);
document.fire('keydown', {key:'Tab', altKey:true});
document.defaultView.fire('blur');
frameDocument.fire('keyup', {key:'Alt', code:'AltLeft'});
assert.deepEqual(inputs.slice(-2).map(x => x.action), ['next', 'activate']);
const before = inputs.length;
document.fire('keydown', { key: 'z', metaKey: true, isComposing: true });
document.fire('keydown', { key: 'z', metaKey: true, target: { closest: () => ({}) } });
document.fire('keydown', { key: 'z', metaKey: true, repeat: true });
assert.equal(inputs.length, before);
document.fire('keydown', { key: '!', code: 'Digit1', metaKey: true, shiftKey: true });
assert.deepEqual(inputs.at(-1), { kind: 'taskbar-number', index: 1, action: 'launch' });
dispose();
console.log('Keyboard translation checks passed');
const alternateInputs = [];
const alternateHost = {dispatchInput: input => alternateInputs.push(input), getSnapshot: () => ({epoch:1, services: {shortcutInventory: {applications:{active:'alternate',alternateAvailable:true,defaultAvailable:true,alternateChord:'SUPER + CTRL + ALT + SPACE',defaultChord:'SUPER + ALT + SPACE'}}, shortcutPreferences: {choices:{applications:'alternate'}}}})};
const stopAlternate = installKeyboard({documents:[document],host:alternateHost,root:desktop});
document.fire('keydown', {key:' ',metaKey:true,altKey:true});
assert.equal(alternateInputs.length, 0);
document.fire('keydown', {key:' ',metaKey:true,altKey:true,ctrlKey:true});
assert.deepEqual(alternateInputs[0], {kind:'shortcut',route:'applications'});
stopAlternate();

const operations = [];
const snapHost = {getSnapshot: () => ({epoch: 4, activeWorkspace:'1', workArea:{x:0,y:56,width:1280,height:664}, windows:[{id:'1',incarnation:'7',workspace:'1',focused:true,minimized:false,placementMode:'tiled'}]}), dispatchInput: value => {operations.push(value); return true;}};
const stopSnap = installKeyboard({documents:[document],host:snapHost,root:desktop});
for (const key of ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown']) document.fire('keydown',{key,metaKey:true});
assert.deepEqual(operations.map(value => value.zone || value.action), ['left','right','maximize','minimize']);
const count = operations.length;
for (const options of [{isComposing:true}, {target:{closest:()=>({})}}, {repeat:true}, {shiftKey:true}]) document.fire('keydown',{key:'ArrowLeft',metaKey:true,...options});
assert.equal(operations.length,count);
stopSnap();

// The real popup adapter listens in document capture and skips prevented
// events. Window capture must record the chord first, with no second step.
const popupDoc = new Events(); popupDoc.defaultView = new Events();
const chordInputs = [];
const stopChord = installKeyboard({ documents: [popupDoc], host: {dispatchInput: value => chordInputs.push(value)}, root: desktop });
const captured = popupDoc.defaultView.fire('keydown', {key:'Tab', altKey:true, target:desktop});
assert.equal(captured.defaultPrevented, true);
popupDoc.fire('keydown', {...captured, currentTarget:popupDoc});
popupDoc.fire('keyup', {key:'Alt', code:'AltLeft'});
assert.deepEqual(chordInputs.map(value => value.action), ['next', 'activate']);
stopChord();

// Only the observed active binding controls interception, even when saved
// preferences differ or are still being applied.
const observed = {active:'default',defaultAvailable:true,alternateAvailable:true,defaultChord:'SUPER + ALT + SPACE',alternateChord:'SUPER + CTRL + ALT + SPACE'};
const transitionInputs = [];
const transitionHost = {getSnapshot:()=>({services:{shortcutInventory:{applications:observed},shortcutPreferences:{choices:{applications:'alternate'}}}}),dispatchInput: input=>transitionInputs.push(input)};
const stopTransition = installKeyboard({documents:[document],host:transitionHost,root:desktop});
const press = ctrlKey => document.fire('keydown',{key:' ',metaKey:true,altKey:true,ctrlKey});
assert.equal(press(false).defaultPrevented,true);
assert.equal(press(true).defaultPrevented,false);
observed.active='alternate';
assert.equal(press(false).defaultPrevented,false);
assert.equal(press(true).defaultPrevented,true);
observed.active='keep';
assert.equal(press(false).defaultPrevented,false);
assert.equal(press(true).defaultPrevented,false);
assert.equal(transitionInputs.length,2);
stopTransition();
console.log('Observed Default, Alternate and Keep transitions passed');
