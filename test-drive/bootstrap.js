const status = document.getElementById('startup');
const frames = Object.fromEntries(['controller', 'bar', 'popup'].map(id => [id, document.getElementById(id)]));
const desktop = document.getElementById('desktop');
const tools = document.querySelector('.desktop-tools');
let lastViewport = null;
function resizeDesktop() {
  document.documentElement.style.setProperty('--desktop-tools-height', `${tools.getBoundingClientRect().height}px`);
  const width = desktop.clientWidth, height = desktop.clientHeight;
  if (host && width > 0 && height > 0) host.dispatchInput({kind:'viewport', width, height});
}
const panel = (buttonId, panelId) => {
  const button = document.getElementById(buttonId), target = document.getElementById(panelId);
  button.addEventListener('click', () => { target.hidden = !target.hidden; button.setAttribute('aria-expanded', String(!target.hidden)); });
};
panel('help-button', 'help');
panel('shortcuts-button', 'shortcuts');
let host, stage, stopInput, tour, readinessTimer;
let readyResolve, readyEpoch = -1, controllerReady = false, rendererReady = new Set(), appliedBar = null;
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
function sendMotionPreference() { host?.dispatchInput({kind:'system-motion-preference', profile: motionPreference.matches ? 'reduced' : 'full'}); }
function checkReady() {
  const snapshot = host?.getSnapshot();
  if (snapshot?.binding && controllerReady && rendererReady.has('bar') && rendererReady.has('popup') && appliedBar && snapshot.presentation?.publication === appliedBar.publication && snapshot.presentation?.lease === appliedBar.lease) {
    clearTimeout(readinessTimer); status.hidden = true; readyResolve?.();
  }
}
addEventListener('message', event => {
  const envelope = event.data;
  if (event.origin !== location.origin || !envelope || envelope.bridgeVersion !== 1 || envelope.epoch !== readyEpoch || !frames[envelope.frameId] || event.source !== frames[envelope.frameId].contentWindow || envelope.kind !== 'native' || typeof envelope.payload !== 'string') return;
  let packet; try { packet = JSON.parse(envelope.payload); } catch { return; }
  if (envelope.frameId === 'controller' && packet.kind === 'host-ready') controllerReady = true;
  if (['bar','popup'].includes(envelope.frameId) && packet.kind === 'presentation-ready') rendererReady.add(envelope.frameId);
  if (envelope.frameId === 'bar' && packet.kind === 'presentation-applied') appliedBar = packet;
  checkReady();
});
function armReadiness() {
  clearTimeout(readinessTimer);
  readinessTimer = setTimeout(() => fail(new Error('the host did not admit an actionable presentation')), 12000);
}
function reconcile(snapshot) {
  const appearance = snapshot.appearance?.values || snapshot.appearance || {};
  const theme = appearance.theme || appearance.appearance;
  if (['night', 'dawn', 'high-contrast'].includes(theme)) document.documentElement.dataset.theme = theme;
  const scale = Number(appearance.textScale || appearance.scale);
  if ([100, 125, 150, 200].includes(scale)) document.documentElement.style.fontSize = `${scale}%`;
  const top = snapshot.workArea?.y - (snapshot.output?.y || 0);
  if (Number.isFinite(top) && top > 0) document.getElementById('desktop').style.setProperty('--desktop-bar-height', `${top}px`);
}

document.getElementById('reset-button').addEventListener('click', () => {
  if (host) { status.hidden = false; status.textContent = 'Desktop reset. Waiting for an admitted interface.'; controllerReady = false; rendererReady.clear(); appliedBar = null; readyEpoch = host.getSnapshot().epoch + 1; host.reset(); lastViewport = null; resizeDesktop(); sendMotionPreference(); armReadiness(); }
  else location.reload();
});
document.getElementById('tour-button').addEventListener('click', () => {
  if (tour) Promise.resolve(tour.start()).catch(fail);
  else { status.hidden = false; status.textContent = 'The tour is unavailable until the desktop is ready.'; }
});
function fail(error) {
  status.hidden = false;
  status.replaceChildren(document.createTextNode(`Desktop unavailable: ${error.message}. `));
  const retry = document.createElement('button'); retry.type = 'button'; retry.textContent = 'Retry'; retry.addEventListener('click', () => location.reload()); status.append(retry);
}
function loadStageBundle() {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script'); script.src = 'stage/desktop-stage.js';
    script.onload = resolve; script.onerror = () => reject(new Error('the compiled Elm desktop stage could not be loaded'));
    document.head.append(script);
  });
}
async function start() {
  try {
    const [hostModule, stageModule, inputModule, previewModule, serviceModule, scenarioModule, tourModule] = await Promise.all([
      import('./host/index.js'), import('./stage/index.js'), import('./input/index.js'), import('./previews/index.js'), import('./services/index.js'), import('./scenarios/index.js'), import('./tour/index.js'), loadStageBundle()
    ]);
    const ready = new Promise(resolve => { readyResolve = resolve; });
    host = hostModule.createHost({frames, onSnapshot(snapshot) {
      reconcile(snapshot);
      stage?.render(snapshot);
      checkReady();
      const placement = snapshot.popupPlacement;
      const popup = frames.popup;
      popup.hidden = !placement || placement.open === false;
      if (placement && Number.isFinite(placement.x) && Number.isFinite(placement.y)) {
        Object.assign(popup.style, {left:`${placement.x}px`, top:`${placement.y}px`, width:`${placement.width}px`, height:`${placement.height}px`});
      }
    }, onDiagnostic(event) {
      if (event.kind === 'service-error') fail(new Error(`service ${event.detail?.kind}: ${event.detail?.message}`));
    }});
    // The tour and bootstrap can both observe the allocation. Admit each size once.
    const dispatchInput = host.dispatchInput.bind(host);
    host.dispatchInput = input => {
      if (input?.kind === 'viewport') {
        const {width, height} = input;
        if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) return false;
        if (lastViewport?.width === width && lastViewport?.height === height) return false;
        lastViewport = {width, height};
      }
      return dispatchInput(input);
    };
    stage = stageModule.mountStage({root:document.getElementById('stage'), host});
    serviceModule.registerServices(host);
    host.registerPreview(previewModule.createPreviewProvider({host, frames}));
    stopInput = inputModule.installInput({host, stage, frames, legendRoot:document.getElementById('legend')});
    tour = tourModule.mountTour({host, stage, root:document.getElementById('tour')});
    readyEpoch = host.getSnapshot().epoch;
    host.start();
    resizeDesktop();
    sendMotionPreference();
    motionPreference.addEventListener('change', sendMotionPreference);
    armReadiness();
    const resizeObserver = new ResizeObserver(resizeDesktop);
    resizeObserver.observe(tools);
    resizeObserver.observe(desktop);
    addEventListener('pagehide', () => resizeObserver.disconnect(), {once:true});
    addEventListener('resize', resizeDesktop);
    await Promise.race([ready, new Promise((_, reject) => setTimeout(() => reject(new Error('the host did not admit an actionable presentation')), 12000))]);
    stage.render(host.getSnapshot());
    status.hidden = true;
    const query = new URLSearchParams(location.search), scenario = query.get('scenario');
    if (scenario) {
      try { const result = await scenarioModule.loadScenario(scenario, host); if (result?.ok === false) { status.hidden = false; status.textContent = result.reason; } }
      catch (error) { status.hidden = false; status.textContent = `Scenario “${scenario}” is unavailable. The default desktop is shown. ${error.message}`; }
    }
    if (query.get('tour') === 'first-run') await tour.start();
    else if (query.has('tour')) { status.hidden = false; status.textContent = 'That tour is unavailable. The default desktop is shown.'; }
  } catch (error) { fail(error); }
}
start();
addEventListener('pagehide', () => { motionPreference.removeEventListener('change', sendMotionPreference); stopInput?.(); tour?.destroy(); stage?.destroy(); host?.destroy(); }, {once:true});
