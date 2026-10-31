import {placeInZone} from '../input/pointer.js';
import {watchEffectCompletion} from '../../assets/shared/effect-completion.js';

/** Project immutable host observations and send requests back to the host. */
export function mountStage({root, host}) {
  if (!globalThis.Elm?.DesktopStage) throw new Error('The compiled Elm desktop stage is unavailable.');
  const mount = document.createElement('div');
  root.replaceChildren(mount);
  const app = globalThis.Elm.DesktopStage.init({node: mount});
  let cancel = null, last = null, disposed = false, watchGeneration = 0;
  const cancelWatch = () => { watchGeneration++; cancel?.(); cancel = null; };
  const forced = matchMedia('(forced-colors: active)');
  // Motion is enabled only after the host publishes Elm's applied profile.
  const tier = snapshot => {
    const appearance = snapshot.appearance?.values || snapshot.appearance;
    const applied = snapshot.motion?.applied;
    const profile = typeof applied === 'string' ? applied : applied?.profile;
    if (document.hidden || forced.matches || !appearance || appearance.effectsOff !== false || appearance.theme === 'high-contrast') return 'off';
    return snapshot.effectsTier === 'reduced' ? 'reduced' : 'full';
  };
  const render = snapshot => {
    if (disposed) return;
    const nextTier = tier(snapshot);
    const appliedMotion = snapshot.motion?.applied;
    const motion = typeof appliedMotion === 'string' ? appliedMotion : appliedMotion?.profile;
    const portalTier = motion === 'full' ? nextTier : 'off';
    if (last && (last.epoch !== snapshot.epoch || last._tier !== portalTier || last.activeWorkspace !== snapshot.activeWorkspace)) cancelWatch();
    if (last && root.querySelector('[data-portal-phase="open"]')) {
      const prior = root.querySelector('[data-portal-phase="open"]');
      const key = prior?.dataset.effectCycle;
      // Elm removes stale decorations on the next observation; cancel the watcher now.
      if (key && last.windows?.some(w => !snapshot.windows?.some(n => n.id === w.id && n.incarnation === w.incarnation))) cancelWatch();
    }
    root.style.setProperty('--stage-width', `${Math.max(1, snapshot.output?.width || 1280)}px`);
    root.style.setProperty('--stage-height', `${Math.max(1, snapshot.workArea?.height || 664)}px`);
    root.dataset.effectsTier = nextTier;
    const appearance = snapshot.appearance?.values || snapshot.appearance || {};
    const applied = snapshot.motion?.applied;
    const profile = typeof applied === 'string' ? applied : applied?.profile;
    root.dataset.theme = appearance.theme || 'night';
    root.dataset.motion = profile === 'full' ? 'full' : 'reduced';
    // Shared portal CSS consults the document attribute for the OS fallback.
    // Only an acknowledged full profile overrides that fallback.
    document.documentElement.dataset.motion = root.dataset.motion;
    // History is observed most-recent-first; focused observation takes precedence.
    const history = snapshot.activationHistory || [];
    const windows = (snapshot.windows || []).map((window, index) => {
      const rank = history.findIndex(id => id === window.incarnation || id === window.id);
      const mode = window.placementMode ?? window.placement ?? window.mode;
      // A compositor can report a floating client while it is snapped or maximized.
      // Its current placement takes precedence over that underlying capability.
      const placement = window.maximized === true || mode === 'maximized' ? 'maximized'
        : mode === 'snapped' ? 'snapped'
        : mode === 'tiled' ? 'tiled'
        : mode === 'floating' || window.floating === true ? 'floating'
        : window.floating === false ? 'tiled' : 'unknown';
      return {...window, _stack: 1 + (window.pinned ? 20000 : 0) + (window.focused ? 10000 : (rank < 0 ? index : 1000 - rank)), _placement: placement};
    });
    last = {...snapshot, windows, _now: Math.round(performance.now()), _tier: portalTier};
    app.ports.observe.send(last);
  };
  app.ports.input.subscribe(value => {
    const snapshot = host.getSnapshot();
    const target = snapshot.windows?.find(w => w.id === value.windowId && w.incarnation === value.incarnation && !w.minimized && (w.workspace === snapshot.activeWorkspace || w.pinned));
    if (!target) return;
    const captured = {kind:'window', windowId:target.id, incarnation:target.incarnation, epoch:snapshot.epoch};
    const focus = () => {
      if (!target.focused) host.dispatchInput({...captured, action:'focus'});
      const current = host.getSnapshot();
      return current.epoch === snapshot.epoch && current.windows?.some(w => w.id === target.id && w.incarnation === target.incarnation && w.focused);
    };
    if (value.action === 'snap-hover') {
      if (target.focused) void host.invoke('snap');
    } else if (value.action === 'window-menu') {
      if (focus()) {
        // Keyboard invocation follows the rendered titlebar, including stage scrolling.
        const titlebar = [...root.querySelectorAll('.stage-window')]
          .find(element => element.dataset.windowId === target.id)?.querySelector('.stage-titlebar');
        const rect = titlebar?.getBoundingClientRect();
        const anchor = value.trigger === 'pointer' && value.anchor
          ? value.anchor
          : rect ? {x: rect.left, y: rect.bottom} : {x: target.geometry.x, y: target.geometry.y + 24};
        void host.invoke('window-menu', {anchor, trigger: value.trigger || 'keyboard', windowId: target.id, incarnation: target.incarnation});
      }
    } else if (value.action === 'maximize-toggle') {
      if (!focus()) return;
      const current = host.getSnapshot().windows.find(w => w.id === target.id && w.incarnation === target.incarnation);
      if (current?.maximized || current?.placementMode === 'maximized') host.dispatchInput({...captured, action:'restore-geometry'});
      else placeInZone(host, target.id, target.incarnation, 'maximize');
    } else {
      if (value.action !== 'minimize' || focus()) host.dispatchInput({...captured, action:value.action});
    }
  });
  app.ports.watch.subscribe(({cycle, phase, tier: effectTier}) => {
    cancelWatch();
    const generation = watchGeneration;
    requestAnimationFrame(() => {
      if (disposed || generation !== watchGeneration) return;
      const target = root.querySelector(`[data-effect-cycle="${cycle}"]`);
      if (!target) { app.ports.completed.send(cycle); return; }
      const duration = effectTier === 'reduced' ? (phase === 'open' ? 120 : 90) : (phase === 'open' ? 520 : 360);
      cancel = watchEffectCompletion({target, cycle, duration, animationName: effectTier === 'reduced' ? 'wl-portal-fade' : `wl-portal-${phase}`, onComplete: () => { cancel = null; if (!disposed) app.ports.completed.send(cycle); }});
    });
  });
  const preference = () => { cancelWatch(); if (last) render(last); };
  forced.addEventListener('change', preference);
  document.addEventListener('visibilitychange', preference);
  return {render, getAnchors() { return {root, desktop: root, bar: document.getElementById('bar'), popup: document.getElementById('popup')}; }, destroy() { disposed = true; cancelWatch(); forced.removeEventListener('change', preference); document.removeEventListener('visibilitychange', preference); root.replaceChildren(); }};
}
