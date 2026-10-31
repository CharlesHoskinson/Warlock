import { effectiveShortcut } from './keyboard.js';
import { placeInZone, focusedWindowAction } from './pointer.js';

const rows = [
  ['Alt + Tab', 'Next window', 'next', 'The operating system may intercept this chord.'],
  ['Alt + Shift + Tab', 'Previous window', 'previous', 'The operating system may intercept this chord.'],
  ['Release Alt', 'Activate candidate', 'activate', 'Use Activate if release is intercepted.'],
  ['Escape', 'Cancel switching', 'cancel', 'Returns to the previous window.']
];
export function mountLegend(root, host) {
  root.replaceChildren();
  const heading = document.createElement('h2'); heading.textContent = 'Shortcuts';
  const label = document.createElement('label'); label.textContent = 'Filter shortcuts';
  const filter = document.createElement('input'); filter.type = 'search'; label.append(filter);
  const list = document.createElement('ul');
  for (const [chord, title, action, note] of rows) {
    const li = document.createElement('li'); const text = document.createElement('span'); text.textContent = `${chord}: ${title}. ${note} `;
    const button = document.createElement('button'); button.type = 'button'; button.textContent = title; button.addEventListener('click', () => host.dispatchInput({ kind: 'switcher', action }));
    li.append(text, button); list.append(li);
  }
  for (const [chord, title, action] of [
    ['Super + Left', 'Snap focused window left', 'left'],
    ['Super + Right', 'Snap focused window right', 'right'],
    ['Super + Up', 'Maximize focused window', 'maximize'],
    ['Super + Down', 'Restore or minimize focused window', 'restore-or-minimize']
  ]) {
    const li = document.createElement('li');
    const text = document.createElement('span');
    text.textContent = `${chord}: ${title}. The operating system may intercept this chord. ${action === 'restore-or-minimize' ? 'Restores a snapped or maximized window; minimizes a normal window. ' : ''}`;
    const button = document.createElement('button'); button.type = 'button'; button.textContent = title;
    button.addEventListener('click', () => focusedWindowAction(host, action));
    li.append(text, button); list.append(li);
  }
  const dynamic = new Map();
  for (const [chord, title, input] of [
    ['Super + Tab','Task View',{kind:'utility',action:'task-view'}], ['Super + Z','Snap layouts',{kind:'utility',action:'snap'}], ['Alt + Space','Window actions',{kind:'utility',action:'window-menu'}],
    ['Super + Alt + Space','Applications',{kind:'shortcut',route:'applications'}], ['Super + Escape','System',{kind:'shortcut',route:'system'}], ['Super + Shift + Alt + comma','Notifications',{kind:'shortcut',route:'notifications'}]
  ]) {
    const li = document.createElement('li'); const text = document.createElement('span'); text.textContent = `${chord}: ${title}. The browser or operating system may intercept this chord. `;
    const button = document.createElement('button'); button.type = 'button'; button.textContent = title; button.addEventListener('click', () => host.dispatchInput(input)); li.append(text, button); list.append(li);
    if (input.kind === 'shortcut') dynamic.set(input.route, {text, title, button});
  }
  const update = snapshot => {
    for (const [route, item] of dynamic) {
      const chord = effectiveShortcut(snapshot, route);
      item.text.textContent = `${chord || 'No Warlock chord active'}: ${item.title}. ${chord ? 'The browser or operating system may intercept this chord. ' : 'Use the button to open it. '}`;
    }
  };
  update(host.getSnapshot?.());
  const unsubscribe = host.subscribe?.(update);
  for (let index = 1; index <= 9; index++) {
    for (const [modifier, action] of [['Super', 'activate'], ['Super + Shift', 'launch'], ['Super + Alt', 'menu']]) {
      const li = document.createElement('li');
      const button = document.createElement('button'); button.type = 'button';
      button.textContent = `${action} taskbar app ${index}`;
      button.addEventListener('click', () => host.dispatchInput({ kind: 'taskbar-number', index, action }));
      li.append(document.createTextNode(`${modifier} + ${index}: The operating system may intercept this chord. `), button); list.append(li);
    }
  }
  const geometry = document.createElement('li');
  const description = document.createElement('p');
  description.textContent = 'Move or resize the focused window in 32 pixel steps. Drag a titlebar or use Alt + drag to move. Alt + right-drag resizes; these buttons provide a keyboard alternative.';
  geometry.append(description);
  for (const [mode, label, dx, dy] of [
    ['move','Move left',-32,0], ['move','Move right',32,0], ['move','Move up',0,-32], ['move','Move down',0,32],
    ['resize','Make narrower',-32,0], ['resize','Make wider',32,0], ['resize','Make shorter',0,-32], ['resize','Make taller',0,32]
  ]) {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = label;
    button.addEventListener('click', () => {
      const snapshot = host.getSnapshot?.();
      const window = snapshot?.windows?.find(item => item.focused && !item.minimized);
      if (!window) return;
      const gesture = {kind:'pointer', epoch:snapshot.epoch, windowId:window.id, incarnation:window.incarnation, mode, x:0, y:0, pointerId:-1};
      if (host.dispatchInput({...gesture, action:'start'})) host.dispatchInput({...gesture, action:'end', currentX:dx, currentY:dy});
    });
    geometry.append(button);
  }
  const snapHelp = document.createElement('p'); snapHelp.textContent = 'Drag a window to an output edge for a half, to a corner for a quarter, or to the top for the full work area. These buttons place the focused window without dragging.'; geometry.append(snapHelp);
  for (const [zone, title] of [['left','Left half'],['right','Right half'],['top-left','Top left'],['top-right','Top right'],['bottom-left','Bottom left'],['bottom-right','Bottom right'],['maximize','Full work area']]) {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = title;
    button.addEventListener('click', () => { const w = host.getSnapshot()?.windows?.find(item => item.focused && !item.minimized); if (w) placeInZone(host,w.id,w.incarnation,zone); }); geometry.append(button);
  }
  list.append(geometry);
  filter.addEventListener('input', () => { const query = filter.value.toLowerCase(); for (const li of list.children) li.hidden = !li.textContent.toLowerCase().includes(query); });
  root.append(heading, label, list);
  return () => { unsubscribe?.(); root.replaceChildren(); };
}
