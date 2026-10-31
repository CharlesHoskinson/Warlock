/** Ordinary Popup legacy preview endpoint. Only the four bundled, local fixture
 * handles can cross the resource boundary. */
export function createPreviewProvider({host, frames, localImagesReady}) {
  let epoch, sequence = 0n, catalogSequence = 0n, currentFrame = null, appliedStamp = null;
  let diagnostic = 'live';
  const scopes = new Map();
  if (typeof document !== 'undefined') {
    const panel = document.getElementById('shortcuts');
    if (panel) {
      const box = document.createElement('section');
      const heading = document.createElement('h3'); heading.textContent = 'Preview diagnostics';
      const label = document.createElement('label'); label.textContent = 'Preview state for the next opened window picker ';
      const select = document.createElement('select');
      for (const state of ['live','historical','loading','unavailable','capacity','waiting','expired','conflict','exhausted']) {
        const option = document.createElement('option'); option.value = state; option.textContent = state[0].toUpperCase() + state.slice(1); select.append(option);
      }
      select.addEventListener('change', () => { diagnostic = select.value; });
      const help = document.createElement('p'); help.textContent = 'Choose a state, close this panel, then open a window picker. Close and reopen the picker to apply a different state.';
      label.append(select); box.append(heading, label, help); panel.append(box);
    }
  }
  const handles = ['1','2','3','4'].map(n => n.repeat(64));
  // Decode the exact local files before offering them. The shipped popup-local
  // bundle resolves these handles to the same relative paths.
  let ready = localImagesReady === true;
  const verify = localImagesReady === undefined && typeof Image !== 'undefined'
    ? Promise.all(handles.map(handle => new Promise(resolve => {
        const image = new Image();
        image.onload = () => resolve(image.naturalWidth > 0 && image.naturalHeight > 0);
        image.onerror = () => resolve(false);
        image.src = new URL(`./assets/${handle}.svg`, import.meta.url).href;
      }))).then(results => { ready = results.every(Boolean); enroll(); })
    : Promise.resolve();
  void verify;
  const jobs = new Map(), receipts = new Map(), owners = new Map();
  const key = value => JSON.stringify(value);
  const retire = () => { for (const job of jobs.values()) clearTimeout(job.timer); jobs.clear(); receipts.clear(); owners.clear(); scopes.clear(); sequence = 0n; catalogSequence = 0n; currentFrame = null; appliedStamp = null; };
  // Retire leases immediately on a host reset, even if no further preview
  // command arrives from the old renderer.
  host.subscribe?.(snapshot => {
    if (epoch !== snapshot.epoch) { retire(); epoch = snapshot.epoch; }
  });
  const send = (identity, event, context) => {
    if (context.signal.aborted || host.getSnapshot().epoch !== epoch) return;
    frames.popup?.contentWindow?.postMessage({bridgeVersion:1, epoch, frameId:'popup', kind:'deliver', payload:{method:'receiveNativePreview',value:{kind:'event',identity,event}}}, location.origin);
  };
  const deliver = value => frames.popup?.contentWindow?.postMessage({bridgeVersion:1, epoch, frameId:'popup', kind:'deliver', payload:{method:'receiveNativePreview',value}}, location.origin);
  // The renderer itself acknowledges application of the same publication and
  // lease. Enrollment follows that acknowledgement, never a speculative DOM.
  function enroll() {
    const snapshot = host.getSnapshot();
    if (!ready || !currentFrame || !appliedStamp || snapshot.epoch !== epoch || !snapshot.binding || currentFrame.publication !== appliedStamp.publication || currentFrame.lease !== appliedStamp.lease) return;
    const {publication, lease} = appliedStamp;
    if (snapshot.presentation?.publication !== publication || snapshot.presentation?.lease !== lease) return;
    const rows = snapshot.windows.filter(w => currentFrame.popup?.some(control => control.id === `family:${w.incarnation}` && control.enabled));
    const serial = String(++catalogSequence);
    const now = String(Math.max(1, Math.floor(performance.now()) + 1));
    const deadline = String(Number(now) + 60000);
    deliver({protocolVersion:3,kind:'catalog',publication,lease,binding:snapshot.binding,requestId:serial,sequence:serial,revision:serial,windows:rows.map(w=>({incarnation:w.incarnation,application:w.application,label:w.label,minimized:w.minimized}))});
    for (const window of rows) {
      const identity = `family:${window.incarnation}`;
      const context = {lifetime:snapshot.binding.lifetime,incarnation:window.incarnation,output:'1',privacy:'1',rendering:'1',scene:'1',content:'1'};
      const scope = {binding:snapshot.binding,context,observation:serial,clock:'1',now,present:true,sourceLive:diagnostic === 'live' ? !window.minimized : true,locked:false,gpuReady:true};
      scopes.set(identity, scope);
      deliver({kind:'seed',publication,lease,identity,scope,title:window.label,application:window.application});
      if (['capacity','waiting','expired','conflict','exhausted'].includes(diagnostic)) {
        deliver({kind:'demand-feedback',identity,binding:snapshot.binding,subject:window.incarnation,clock:'1',publication,lease,sequence:serial,deadline,outcome:diagnostic});
      } else {
        deliver({kind:'event',identity,event:{kind:'request',trigger:{binding:snapshot.binding,context,origin:serial,clock:'1',deadline}}});
      }
    }
  }
  if (typeof addEventListener === 'function') addEventListener('message', event => {
    const envelope = event.data, snapshot = host.getSnapshot();
    if (event.origin !== location.origin || !envelope || envelope.bridgeVersion !== 1 || envelope.epoch !== snapshot.epoch || envelope.kind !== 'native' || event.source !== frames[envelope.frameId]?.contentWindow || typeof envelope.payload !== 'string') return;
    let packet; try { packet = JSON.parse(envelope.payload); } catch { return; }
    if (envelope.frameId === 'controller' && packet.kind === 'view-commit') currentFrame = packet.projection?.frame || null;
    if (envelope.frameId === 'popup' && packet.kind === 'presentation-applied' && packet.surfaceProtocol === 2) { appliedStamp = {publication:packet.publication,lease:packet.lease}; enroll(); }
  });
  const receipt = (identity, event, context) => {
    const id = key([event.kind, event.job || event.frame.job]);
    let stored = receipts.get(id);
    if (!stored) { stored = {kind:'receipt',sequence:String(++sequence),event}; receipts.set(id, stored); }
    send(identity, stored, context);
  };
  return (packet, context) => {
    if (context.signal.aborted || packet.previewProtocol !== 2 || packet.kind !== 'preview-commands' || !Array.isArray(packet.entries)) return;
    const snapshot = host.getSnapshot();
    if (epoch !== snapshot.epoch) { retire(); epoch = snapshot.epoch; }
    for (const entry of packet.entries) {
      if (typeof entry.identity !== 'string' || !Array.isArray(entry.commands)) continue;
      for (const command of entry.commands) {
        const job = command.job || command.frame?.job;
        if (job && key(job.binding) !== key(snapshot.binding)) continue;
        const id = job && key(job);
        if (command.kind === 'acquire' && job) {
          if (jobs.has(id)) continue;
          const window = snapshot.windows.find(w => w.incarnation === job.context?.incarnation);
          const n = Number(window?.incarnation);
          const handle = Number.isInteger(n) && n >= 1 && n <= 4 ? String(n).repeat(64) : null;
          if (diagnostic === 'loading') { jobs.set(id, {identity:entry.identity,job}); continue; }
          if (diagnostic === 'unavailable' || !ready || !handle || owners.has(handle)) {
            jobs.set(id, {identity:entry.identity,job});
            send(entry.identity, {kind:'source-denied',job,reason:'source-unavailable'}, context);
            continue;
          }
          const frame = {job,handle,owned:true,signaled:false,fidelity:'client',coverage:['client'],expires:job.deadline};
          jobs.set(id,{identity:entry.identity,job,frame}); owners.set(handle,id);
          send(entry.identity,{kind:'offer',frame},context);
          const signaled = {...frame,signaled:true};
          jobs.get(id).frame = signaled;
          send(entry.identity,{kind:'fence',frame:signaled},context);
          if (diagnostic === 'historical' && scopes.has(entry.identity)) {
            const previous = scopes.get(entry.identity);
            const scope = {...previous, context:{...previous.context, scene:String(BigInt(previous.context.scene) + 1n)}, observation:String(++catalogSequence), sourceLive:false};
            scopes.set(entry.identity, scope);
            send(entry.identity,{kind:'observe',scope},context);
          }
          // Expiry is an observed clock transition; Elm owns retirement and
          // requests release after its paint gate has cleared.
          jobs.get(id).timer = setTimeout(() => {
            if (!jobs.has(id) || context.signal.aborted || host.getSnapshot().epoch !== epoch) return;
            send(entry.identity,{kind:'clock',binding:job.binding,clock:job.clock,now:job.deadline},context);
          },60000);
        } else if (command.kind === 'cancel' && jobs.has(id)) {
          receipt(entry.identity,{kind:'cancelled',job},context);
        } else if (command.kind === 'release' && jobs.get(id)?.frame && command.frame.handle === jobs.get(id).frame.handle) {
          clearTimeout(jobs.get(id).timer); owners.delete(command.frame.handle);
          receipt(entry.identity,{kind:'released',frame:command.frame},context);
        } else if (command.kind === 'acknowledge') {
          const terminal = [...receipts].find(([, value]) => value.sequence === command.sequence && key(value.event.job || value.event.frame?.job) === id);
          if (terminal) { receipts.delete(terminal[0]); if (terminal[1].event.kind !== 'cancelled' || !jobs.get(id)?.frame) jobs.delete(id); }
        } else if (command.kind === 'reconcile' && key(command.binding) === key(snapshot.binding)) {
          for (const [jobId, state] of jobs) {
            if (state.frame) { owners.delete(state.frame.handle); receipt(state.identity,{kind:'released',frame:state.frame},context); }
            else receipt(state.identity,{kind:'cancelled',job:state.job},context);
          }
        }
      }
    }
  };
}
