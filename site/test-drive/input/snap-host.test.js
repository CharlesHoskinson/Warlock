// Pass a host module with patches/host-snap-shortcuts.patch applied.
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {focusedWindowAction, zoneGeometry} from './pointer.js';
const {createHost} = await import(pathToFileURL(process.argv[2]));
globalThis.location = {origin:'https://example.test'};
globalThis.addEventListener = () => {}; globalThis.removeEventListener = () => {};
const frames = Object.fromEntries(['controller','bar','popup'].map(id => [id,{postMessage(){}}]));
const host = createHost({frames}); host.start();
const original = host.getSnapshot().windows.find(w => w.focused);
for (const [action, mode] of [['left','snapped'],['right','snapped'],['maximize','maximized']]) {
  assert(focusedWindowAction(host, action));
  const current = host.getSnapshot().windows.find(w => w.id === original.id);
  assert.equal(current.placementMode, mode); assert(current.focused);
  assert.deepEqual(current.geometry, zoneGeometry(action, host.getSnapshot().workArea));
  assert.deepEqual(current.restoreGeometry, original.geometry);
}
assert(focusedWindowAction(host,'restore-or-minimize'));
let current = host.getSnapshot().windows.find(w => w.id === original.id);
assert.deepEqual(current.geometry,original.geometry); assert(current.focused);
assert(focusedWindowAction(host,'restore-or-minimize'));
current = host.getSnapshot().windows.find(w => w.id === original.id);
assert(current.minimized); assert(!current.focused);
assert(host.getSnapshot().windows.some(w => w.focused && w.id !== original.id));
// A pinned window remains visible and actionable after changing workspaces.
const seed = host.getSnapshot();
host.reset({...seed, activeWorkspace:'2', windows:seed.windows.map(w => ({...w, focused:false,
  ...(w.id === original.id ? {pinned:true, minimized:false, placementMode:'floating', geometry:original.geometry} : {})}))});
assert(host.dispatchInput({kind:'window', action:'focus', epoch:host.getSnapshot().epoch, windowId:original.id, incarnation:original.incarnation}));
const pinned = host.getSnapshot().windows.find(w => w.id === original.id);
for (const action of ['left','right','maximize']) {
  assert(focusedWindowAction(host, action));
  assert.deepEqual(host.getSnapshot().windows.find(w => w.id === original.id).geometry, zoneGeometry(action, host.getSnapshot().workArea));
}
assert(focusedWindowAction(host, 'restore-or-minimize'));
assert.deepEqual(host.getSnapshot().windows.find(w => w.id === original.id).geometry, original.geometry);
assert(focusedWindowAction(host, 'restore-or-minimize'));
assert(host.getSnapshot().windows.find(w => w.id === original.id).minimized);
assert.equal(host.dispatchInput({kind:'window', action:'minimize', epoch:seed.epoch, windowId:pinned.id, incarnation:pinned.incarnation}), false);
assert.equal(host.dispatchInput({kind:'window', action:'minimize', epoch:host.getSnapshot().epoch, windowId:pinned.id, incarnation:'stale'}), false);
host.destroy(); console.log('Snap shortcut geometry and focus checks passed');
